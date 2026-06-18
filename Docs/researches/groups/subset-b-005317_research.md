# Research: subset-b-005317

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.c

## Purpose

`mv_sas.c` is the core libsas low-level driver implementation for Marvell 88SE64xx/88SE94xx SAS/SATA HBAs. It translates libsas `sas_task` work into hardware command slots, manages PHY and port notifications, owns device-private allocation and teardown, handles task management and error recovery, and drains RX completion/attention events from the controller. It is intentionally chip-family-neutral: hardware differences are routed through the `mvs_dispatch` table defined in `mv_sas.h` and implemented by the 64xx/94xx backend files.

## Important APIs, Types, and Functions

- `mvs_queue_command()` is the libsas queue entry. It locates the per-controller `struct mvs_info`, prepares a hardware slot with `mvs_task_prep()`, and starts delivery through `MVS_CHIP_DISP->start_delivery()`.
- `mvs_task_prep()`, `mvs_task_prep_smp()`, `mvs_task_prep_ssp()`, and `mvs_task_prep_ata()` build command headers, open address frames, PRD tables, DMA mappings, response buffers, and TX ring descriptors for SMP, SSP, SATA, and STP tasks.
- `mvs_slot_complete()` is the main completion path. It interprets RX descriptors, fills libsas task status, copies SMP responses, handles ATA D2H FIS responses, frees DMA/slot state, drops device running counts, and invokes `task_done`.
- `mvs_int_rx()` drains the RX ring and dispatches completions, errors, slot resets, and attention interrupts.
- `mvs_int_port()`, `mvs_update_phyinfo()`, `mvs_bytes_dmaed()`, `mvs_work_queue()`, and `mvs_sig_time_out()` implement hotplug, OOB completion, SATA signature waits, broadcast-change notifications, and PHY loss/recovery.
- `mvs_dev_found()`, `mvs_dev_gone()`, `mvs_port_formed()`, and `mvs_port_deformed()` are the libsas discovery callbacks that bind/unbind `domain_device` and `asd_sas_port` objects to driver-private `mvs_device` and `mvs_port` records.
- `mvs_abort_task()`, `mvs_query_task()`, `mvs_lu_reset()`, and `mvs_I_T_nexus_reset()` provide SAM task management and error-handler reset behavior.
- Tag helpers `mvs_tag_alloc()`, `mvs_tag_free()`, `mvs_find_tag()`, and slot helpers `mvs_slot_task_free()` coordinate reserved internal tags, blk-mq request tags, DMA pool buffers, and `task->lldd_task`.

## Control Flow

Normal I/O starts in libsas, enters `mvs_queue_command()`, and runs under `mvi->lock`. `mvs_task_prep()` validates port/device presence, maps SGLs for non-ATA tasks, chooses either a request tag plus `MVS_RSVD_SLOTS` or a reserved bitmap tag, allocates a DMA slot buffer, then calls the protocol-specific builder. The builders write one TX ring entry and one command header; the shared caller links the slot onto the port list, attaches `task->lldd_task`, increments `mvi_dev->running_req`, advances `tx_prod`, and the queue entry kicks the hardware.

Completion runs from interrupt context through `mvs_int_rx()`. The first RX dword mirrors the hardware producer; if it does not change the driver falls back to `rx_update()`. Each descriptor triggers `mvs_slot_complete()` for DONE or ERR cases. Completion marks the task done under `task_state_lock`, handles aborted tasks specially, maps RX flags/protocol-specific status into libsas status, decrements `running_req`, frees SATA register sets when the last ATA request drains, releases DMA resources, drops the HBA lock around the upper-layer callback, and then reacquires it.

Hotplug enters through per-PHY interrupts in `mvs_int_port()`. POOF/loss events release outstanding tasks, clear SRS interrupts, and schedule delayed work. COMWAKE starts a SATA signature timer. SIG_FIS or ID_DONE causes port type detection, PHY info repair, optional SAS PHY tuning, byte-DMA notification to libsas, and port-formed notification if the event followed a plug-out. Broadcast changes are converted to libsas port events through delayed work.

Error handling combines hardware slot errors and libsas TMFs. `mvs_slot_err()` inspects the error dwords in the slot response buffer, issues stop/active commands through dispatch hooks, fabricates SSP sense for no-destination cases, and maps SATA/STP failures to protocol responses. Abort/query/LU/I_T reset paths invoke libsas helpers with driver tags and then release local slot state.

## State and Persistence Behavior

Runtime state is in `struct mvs_info`: TX/RX rings, RX FIS area, command headers, slot array, reserved-tag bitmap, per-PHY/port/device tables, workqueue list, and chip dispatch pointer. This file does not persist configuration to disk or firmware; it only reads/writes device MMIO through dispatch hooks and consumes HBA info that other code initializes. Device state persists for the lifetime of libsas discovery objects via `dev->lldd_dev`, `sas_port->lldd_port`, `sas_phy->lldd_phy`, and `task->lldd_task`.

SATA register-set assignment is persistent per attached `mvs_device` while ATA requests are outstanding. `mvs_assign_reg_set()` lazily assigns taskfile sets; `mvs_slot_complete()` frees them only after `running_req` reaches zero, and device removal frees them unconditionally. Timers and delayed work hold transient PHY-event state and must be canceled or made harmless by state checks.

## Dependencies and Integration Points

The file depends heavily on libsas (`sas_task`, `domain_device`, `sas_notify_*`, `sas_abort_task`, `sas_lu_reset`, `sas_phy_reset`, `sas_drain_work`), libata for NCQ tags, the SCSI midlayer through libsas, PCI/DMA APIs, kernel timers/workqueues, and Marvell register definitions from `mv_defs.h`. Hardware-specific operations are abstracted through `MVS_CHIP_DISP`, including PRD layout, register-set allocation, interrupt clearing, PHY operations, RX producer reads, DMA workarounds, and GPIO writes.

Chip backends, probe code, and headers must initialize `mvi->chip`, DMA pools, rings, PHY tables, locks, and libsas callback registration correctly before these paths run. `mvs_scan_start()` and `mvs_scan_finished()` integrate with the SCSI scan lifecycle by synthesizing byte-DMA events on all PHYs and draining libsas work before reporting completion.

## Risks and Edge Cases

- Locking is subtle: `mvs_slot_complete()` intentionally drops `mvi->lock` around `task_done()`. Any caller must tolerate slot/task state changing around that callback.
- `task->lldd_task`, port lists, and device removal can race with abort/completion/hotplug paths. The code uses locks and task state flags, but stale slot pointers remain a high-risk area.
- `mvs_find_dev_mvi()` and related PHY lookup loops assume libsas arrays are populated and terminated as expected; invalid topology state could lead to wrong HBA selection.
- SMP response copying uses `kmap_atomic()` and copies `sg_dma_len()` bytes from the slot response; response length mismatches or malformed hardware data are important test cases.
- ATA/STP NCQ handling mutates the FIS sector count and uses libata `ata_queued_cmd` tags. Incorrect tag mapping can corrupt NCQ completion association.
- Delayed hotplug work allocates with `GFP_ATOMIC`; allocation failure silently drops event handling except for returning `-ENOMEM`.
- Timer function presence is used as an active flag for SATA signature timeout. That pattern is fragile if timer lifecycle rules change.

## Test Signals

Useful validation signals include successful SAS and SATA discovery, wide-port formation/deformation, SMP expander management, SSP read/write, SATA NCQ read/write, ATAPI command paths, broadcast-change rescans, link flap while I/O is outstanding, abort and LU/I_T reset recovery, RX descriptor error injection, DMA mapping failure handling, and controller removal while delayed PHY work or signature timers are pending. Kernel logs should show expected PHY attach/remove messages without leaked tasks, repeated "reuse same slot" reports, DMA API warnings, or libsas task timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.h

## Purpose

`mv_sas.h` is the shared interface and state definition header for the Marvell mvsas driver. It defines the chip dispatch ABI, controller/PHY/port/device/slot data structures, DMA layout helpers, flash-backed HBA info page format, and function prototypes used by the main libsas implementation and chip-specific 64xx/94xx backends.

## Important APIs, Types, and Definitions

- `DRV_NAME`, `DRV_VERSION`, `MVS_ID_NOT_MAPPED`, `WIDE_PORT_MAX_PHY`, `MVS_MAX_SG`, `MVS_CHIP_SLOT_SZ`, `MVS_RX_FISL_SZ`, and FIS address macros describe global driver constants and per-chip sizing.
- `struct mvs_dispatch` is the central hardware abstraction table. It contains chip init/remap, ISR, interrupt mask, PHY register, port config, command issue, RX update, register-set allocation, PRD generation, PHY discovery, SPI/flash, DMA workaround, interrupt tuning, NCQ error, and GPIO hooks.
- `struct mvs_chip_info` provides per-family dimensions and selects the dispatch table.
- `struct mvs_cmd_hdr` matches the hardware command header written for each slot.
- `struct mvs_port`, `struct mvs_phy`, `struct mvs_device`, `struct mvs_slot_info`, and `struct mvs_info` hold all live driver state.
- `struct hba_info_page`, `struct phy_tuning`, and `struct ffe_control` describe the 256-byte flash/NVRAM HBA information page and PHY tuning data.
- Prototypes export the main functions from `mv_sas.c` to probe/interrupt/chip files: queueing, scan, PHY control, device notifications, resets, RX handling, task release, and GPIO.

## Control Flow and Contracts

The header’s most important control-flow contract is `struct mvs_dispatch`: generic code calls `MVS_CHIP_DISP->...` instead of touching chip-specific registers directly. Backends must provide coherent implementations for ring advancement, interrupt status/ack, PRD sizing, register-set allocation, port type detection, and PHY reset. The main file assumes these hooks are callable under `mvi->lock` and often from interrupt context.

The DMA layout macros define how generic code interprets memory allocated elsewhere: RX FIS areas are indexed by register set or unassociated PHY ID, slot buffers are split into command table/open-address-frame/PRD/status areas, and command headers contain physical addresses for those regions. Any backend change in PRD size/count must remain compatible with the slot buffer sizing constants from `mv_defs.h`.

## State and Persistence Behavior

`struct mvs_info` is the in-memory controller instance. It stores PCI/device handles, MMIO regions, libsas host pointers, TX/RX rings and DMA addresses, RX FIS DMA memory, slot headers, chip identity, reserved-tag bitmap, per-PHY and per-port arrays, device table, flash fields, bulk DMA buffers, and a flexible array of slot info. None of this is persistent except `hba_info_param`, `flashid`, `flashsize`, and `flashsectSize`, which mirror data read from controller flash/NVRAM by other driver code.

`struct hba_info_page` documents persistent firmware/flash contents, including signature, per-port SAS addresses, FFE controls, PHY rates, and tuning parameters. Fields filled with `0xff` are considered invalid. The main `mv_sas.c` code uses the runtime state derived from these values but does not itself write the page.

## Dependencies and Integration Points

The header includes Linux kernel core headers, DMA/PCI/interrupt APIs, libsas, SCSI command/tag helpers, SAS ATA integration, and Marvell hardware definitions from `mv_defs.h`. It exposes external dispatch tables `mvs_64xx_dispatch` and `mvs_94xx_dispatch`, target-mode globals, and the optional `interrupt_coalescing` tunable.

Every source file in the mvsas driver depends on this header for common type identity. The header also defines the low-level driver data pointers that libsas stores in `sas_ha_struct`, `asd_sas_phy`, `asd_sas_port`, `domain_device`, and `sas_task`.

## Risks and Edge Cases

- The dispatch table is large and mostly unchecked at call sites. Missing or incompatible backend hooks can crash generic paths.
- Several structures map hardware DMA or firmware ABI layouts; packing/alignment and endian conversions are critical.
- Macros such as `MVS_PHY_ID` depend on a local variable named `sas_phy`, which makes call-site context significant and easy to misuse.
- `struct mvs_info` uses a flexible array for slots; allocation must account for chip slot count and alignment.
- The HBA info page uses bitfields and mixed-width fields for persistent hardware data; portability and endian assumptions should be treated carefully.

## Test Signals

Header-level validation comes from successful builds across all mvsas chip backends, sparse/endian checks on MMIO and DMA structures, boot/probe on 64xx and 94xx adapters, stress of maximum slot/SG counts, and exercising optional hooks such as GPIO, SPI, interrupt coalescing, STP reset, and DMA workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvumi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvumi.c

## Purpose

`mvumi.c` is the Marvell UMI PCI SCSI host driver for MV9143 and MV9580 storage controllers. It performs PCI setup, firmware handshake, DMA communication-list allocation, SCSI command framing, interrupt-driven completion, hotplug/event processing, timeout/reset handling, suspend/resume, shutdown cache flushes, and SCSI host attachment.

## Important APIs, Types, and Functions

- PCI/module entry points are `mvumi_probe_one()`, `mvumi_detach_one()`, `mvumi_shutdown()`, `mvumi_suspend()`, `mvumi_resume()`, and `module_pci_driver(mvumi_pci_driver)`.
- SCSI host operations are declared in `mvumi_template`: `mvumi_queue_command()`, `mvumi_timed_out()`, `mvumi_host_reset()`, `mvumi_sdev_configure()`, and `mvumi_bios_param()`.
- Firmware setup flows through `mvumi_init_fw()`, `mvumi_cfg_hw_reg()`, `mvumi_start()`, `mvumi_check_handshake()`, `mvumi_handshake_event()`, `mvumi_handshake()`, `mvumi_hs_process_page()`, `mvumi_hs_build_page()`, and `mvumi_init_data()`.
- Command allocation and tag handling are in `mvumi_alloc_cmds()`, `mvumi_free_cmds()`, `mvumi_get_cmd()`, `mvumi_return_cmd()`, `tag_init()`, `tag_get_one()`, and `tag_release_one()`.
- I/O preparation and issue are in `mvumi_build_frame()`, `mvumi_make_sgl()`, `mvumi_fire_cmd()`, `mvumi_send_command()`, and per-chip inbound-list availability hooks.
- Completion runs through `mvumi_isr_handler()`, `mvumi_clear_intr()`, `mvumi_receive_ob_list_entry()`, `mvumi_handle_clob()`, `mvumi_complete_cmd()`, and `mvumi_complete_internal_cmd()`.
- Internal synchronous commands use `mvumi_create_internal_cmd()`, `mvumi_issue_blocked_cmd()`, `mvumi_delete_internal_cmd()`, with users such as inquiry, event fetch, and cache flush.
- Hotplug and discovery are handled by `mvumi_probe_devices()`, `mvumi_inquiry()`, `mvumi_rescan_bus()`, `mvumi_handle_hotplug()`, `mvumi_launch_events()`, `mvumi_get_event()`, and notification parsers.

## Control Flow

Probe enables the PCI device, sets DMA mask, allocates a `Scsi_Host`, initializes lists/mutexes/wait queues, maps BARs, selects a device template for MV9143 or MV9580, configures MMIO register pointers, allocates a handshake page, and drives the firmware handshake. During handshake, firmware capability page 1 is queried, host/list pages are sent, communication-list memory is allocated, and inbound/outbound ring parameters are committed to MMIO registers. After command objects are allocated, the driver requests IRQs, enables interrupts, attaches to the SCSI midlayer, optionally adds a MV9580 virtual device, and starts a kernel thread for rescan work.

Normal SCSI I/O enters `mvumi_queue_command()` under `host_lock`, obtains a command from `cmd_pool`, builds a message frame from the CDB and DMA-mapped SGL, stores it in `scsi_cmd_priv`, and calls `fire_cmd`. `mvumi_fire_cmd()` queues the command, checks firmware inbound capacity, assigns a tag and request ID, either writes a dynamic-list entry pointing to a host frame or copies the frame into the inbound list, and rings the inbound write pointer.

Interrupt handling first clears and classifies interrupt sources. Doorbell events may schedule event work or continue handshaking. Communication-list output interrupts copy outbound frames into a driver-owned pool, and `mvumi_handle_clob()` returns the outbound buffers, releases tags, decrements firmware outstanding count, completes either SCSI or internal waiters, and tries to send queued commands. SCSI completion maps firmware request status to host result, copies sense payloads when present, unmaps DMA, calls `scsi_done()`, and returns the command to the pool.

Hotplug is split between firmware events and a rescan thread. Bus-change interrupts increment `pnp_count` and wake `mvumi_rescan_bus()`, which probes target IDs with internal INQUIRY commands, compares WWIDs, removes missing devices, and calls `scsi_add_device()` for new devices. Event notifications are fetched by scheduled work and logged or converted to add/remove operations.

## State and Persistence Behavior

`struct mvumi_hba` stores all runtime state: BAR mappings, register table, SCSI host, firmware state, communication-list addresses, list slots, tag stack, tag-to-command table, target bitmap, outstanding count, waiting request list, device lists, hotplug thread, and event/discovery synchronization. State is not persisted by this driver. The only durable interaction is sending firmware SCSI commands such as cache flush/shutdown and controller reset/handshake commands through MMIO doorbells.

Internal commands allocate coherent frame/data buffers on demand and wait on `int_cmd_wait_q`. Normal I/O command frames are preallocated either dynamically in a coherent inbound-frame area or as per-command cached allocations depending on firmware capability. The target map is updated during `sdev_configure()` and later drives shutdown cache flushing.

## Dependencies and Integration Points

The driver integrates with the PCI core, SCSI midlayer, DMA API, kthreads, workqueues, wait queues, interrupt handling, and MMIO accessors. It uses constants and ABI structures from `mvumi.h`, including handshake pages, SGL formats, command/response frames, and register templates. Device behavior depends on firmware protocol support flags such as compact SGL, PRD host mode, dynamic source mode, and new IO depth encoding.

MV9143 and MV9580 differ in BAR selection, register offsets, inbound/outbound ring accounting, request ID checking, reset behavior, and virtual-device handling. Those differences are captured by `mvumi_instance_template` and `mvumi_cfg_hw_reg()`.

## Risks and Edge Cases

- Tag and outbound-frame validation is critical. A bad tag or stale request ID can miscomplete commands; the code logs and skips suspect frames.
- Timeout handling manually removes `tag_cmd`, releases tags, unmaps DMA, and returns the command while firmware may still complete later; late completions must be safely rejected.
- `mvumi_issue_blocked_cmd()` can time out and manipulate queues under `host_lock`; internal command lifecycle bugs can leak coherent buffers or corrupt the tag stack.
- Handshake and reset paths reuse existing HBA state. Failure during resume or reset may leave firmware and host rings out of sync.
- Hotplug WWID matching can reject duplicate WWIDs or ID changes; MV9143 uses a synthetic WWID of `id + 1`, which is weaker than firmware UUIDs.
- `mvumi_resume()` maps BARs and calls `pci_release_regions()` on some failure paths even though resume did not request regions, so PM error unwinding deserves scrutiny.
- Several allocations use `GFP_ATOMIC` outside hard IRQ paths; memory pressure can cause command/event drops.

## Test Signals

Important tests include probe/remove on both PCI IDs, firmware handshake page negotiation, compact and non-compact SGLs, dynamic-source and copied inbound frame modes, SCSI read/write with many SG entries, CHECK CONDITION sense propagation, command timeout followed by late completion, host reset, shutdown/suspend cache flush, hotplug add/remove/rescan, event notification logging, MV9580 virtual-device attach, and DMA API/debug checks for map/unmap balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvumi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvumi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvumi.h

## Purpose

`mvumi.h` defines the firmware ABI, register abstraction, command frame formats, SGL formats, handshake pages, event structures, runtime HBA state, and per-chip operation template for the Marvell UMI SCSI driver. It is the contract between `mvumi.c` and the MV9143/MV9580 firmware message-unit protocol.

## Important APIs, Types, and Definitions

- Driver and PCI constants include `MV_DRIVER_NAME`, version fields, `PCI_DEVICE_ID_MARVELL_MV9143`, `PCI_DEVICE_ID_MARVELL_MV9580`, internal command wait time, inquiry UUID offsets, and `MVUMI_MAX_SG_ENTRY`.
- `struct mvumi_hw_regs` stores mapped MMIO register pointers and bit masks for doorbells, interrupts, resets, and inbound/outbound communication-list control.
- Doorbell and command flag enums define handshake, reset, bus-change, event, data direction, DMA/PIO, and PRDT-in-host bits.
- Event structures include `mvumi_hotplug_event`, `mvumi_driver_event`, `mvumi_event_req`, and `mvumi_events_wq`.
- SGL ABI types are `mvumi_sgl` and `mvumi_compact_sgl`, with macros `sgd_getsz`, `sgd_setsz`, and `sgd_inc` adapting to compact SGL firmware capability.
- `mvumi_cmd`, `mvumi_msg_frame`, and `mvumi_rsp_frame` define command tracking and inbound/outbound wire frames.
- Handshake definitions include firmware states, signatures, status/state encoders, `mvumi_hs_header`, and pages 1 through 4 for firmware capability, host info, firmware control, and communication-list info.
- `struct mvumi_hba` is the central runtime controller state; `struct mvumi_instance_template` provides function pointers for chip-specific command issue, interrupt control, ring checks, status reads, and reset.

## Control Flow and Contracts

The header encodes a strict startup contract. Firmware starts in a handshake state, page 1 reports capabilities and dimensions, the driver allocates communication-list memory sized from those fields, and pages 2 through 4 send host identity and DMA addresses back to firmware. The frame and SGL structures must remain layout-compatible with firmware, including compact SGL stride selection and endian handling by the C file.

Normal command flow uses `mvumi_msg_frame` as the host-to-firmware CDB container and `mvumi_rsp_frame` as the firmware-to-host completion container. Tags are indexes into `hba->tag_cmd`; request IDs optionally protect against stale completions. `mvumi_instance_template` isolates the few hardware differences that cannot be represented just by register offsets.

## State and Persistence Behavior

`struct mvumi_hba` persists for the bound PCI device lifetime. It stores mapped BARs, DMA communication lists, shadow pointers, handshake page, firmware capability results, host limits, ring positions, firmware state, command/tag pools, target bitmap, event lists, and hotplug thread state. The header defines no disk persistence. It does define firmware-visible persistent-like protocol fields such as controller firmware version and target WWID inquiry offsets, but actual persistence is handled by firmware.

## Dependencies and Integration Points

The header assumes Linux kernel list, atomic, mutex, wait queue, PCI, DMA, SCSI, and workqueue types are already available through the C file includes or kernel build context. It directly supports the SCSI midlayer through `mvumi_cmd_priv`, which stores a pointer in each `scsi_cmnd` private area. Firmware event IDs and Marvell-specific SCSI CDB constants integrate the driver with controller management functions such as shutdown cache flush and event retrieval.

## Risks and Edge Cases

- Several structures are firmware ABI layouts but are not all explicitly marked packed; compiler layout assumptions must match the platform ABI expected by firmware.
- `IS_DMA64` is a compile-time `sizeof(dma_addr_t)` check, not a runtime device capability check; the C code still falls back if 64-bit DMA mask setup fails.
- Compact SGL macros cast between normal and compact descriptors and increment a typed pointer through byte arithmetic; misuse can corrupt frame payloads.
- `HSP_MAX_SIZE` uses a GCC statement expression, tying this header to kernel/GNU C expectations.
- `mvumi_hba` mixes fields protected by `host_lock`, device mutexes, atomics, and wait queues; the header does not document lock ownership, so callers must follow `mvumi.c` conventions.

## Test Signals

Header correctness is signaled by successful builds with both supported PCI device IDs, sparse and endian checks around frame/SGL fields, firmware handshake negotiation with and without compact/dynamic-source capabilities, high queue-depth tag-stack tests, event payload parsing, and command-private storage validation through `cmd_size = sizeof(struct mvumi_cmd_priv)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvumi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/myrb.c

## Purpose

`myrb.c` is the SCSI block-interface driver for Mylex DAC960/AcceleRAID/eXtremeRAID PCI RAID controllers using DAC960 V1 firmware. It probes several hardware mailbox variants, exposes RAID logical drives as SCSI devices, provides pass-through access for physical devices, integrates with the Linux RAID class, implements sysfs controls for rebuild/consistency/device state/cache flush, monitors controller events, and translates firmware completions into SCSI results.

## Important APIs, Types, and Functions

- Module lifecycle is `myrb_init_module()`/`myrb_cleanup_module()`, which attach/release a RAID class template and register/unregister a PCI driver.
- PCI lifecycle is `myrb_probe()`, `myrb_detect()`, `myrb_remove()`, `myrb_cleanup()`, and `myrb_unmap()`.
- SCSI host operations are in `myrb_template`: `myrb_queuecommand()`, `myrb_host_reset()`, `myrb_sdev_init()`, `myrb_sdev_configure()`, `myrb_sdev_destroy()`, and `myrb_biosparam()`.
- Command execution helpers include `myrb_reset_cmd()`, `myrb_qcmd()`, `myrb_exec_cmd()`, `myrb_exec_type3()`, `myrb_exec_type3D()`, `myrb_pthru_queuecommand()`, and `myrb_ldev_queuecommand()`.
- Controller discovery and monitoring are handled by `myrb_get_hba_config()`, `myrb_hba_enquiry()`, `myrb_get_ldev_info()`, `myrb_get_errtable()`, `myrb_get_event()`, `myrb_update_rbld_progress()`, `myrb_get_cc_progress()`, `myrb_bgi_control()`, and `myrb_monitor()`.
- Completion paths are `myrb_handle_scsi()` for SCSI commands and `myrb_handle_cmdblk()` for synchronous driver/controller commands.
- Sysfs/RAID class integration includes `raid_state`, `raid_level`, `rebuild`, `consistency_check`, `ctlr_num`, `firmware`, `model`, `flush_cache`, plus `myrb_is_raid()`, `myrb_get_resync()`, and `myrb_get_state()`.
- Hardware backends cover DAC960 LA, PG, PD, and older P controllers with specific mailbox register helpers, init functions, interrupt handlers, and `myrb_privdata` records.

## Control Flow

Probe selects hardware-private data from the PCI ID, allocates a SCSI host, enables the PCI device, maps the controller register window, runs the backend-specific hardware init, requests the IRQ, queries firmware/controller configuration, creates DMA pools and a monitor workqueue, adds the host, and scans it. Backend init waits for controller initialization, reports BIOS/error-status messages, enables memory mailbox mode where supported, allocates common DMA enquiry/error/logical-drive buffers, and installs queue/interrupt/reset function pointers.

Logical drive I/O uses a synthetic SCSI target channel: `myrb_logical_channel()` returns the last channel, and logical drives appear as targets on that channel. `myrb_ldev_queuecommand()` handles simple commands like INQUIRY, MODE SENSE, REQUEST SENSE, READ CAPACITY, TEST UNIT READY, and SYNCHRONIZE CACHE in software. Read/write/verify commands are translated into type 5 firmware mailbox commands with either a direct data address or a DMA-pooled scatter-gather table, then queued under `queue_lock`.

Physical-device commands on non-logical channels use `myrb_pthru_queuecommand()`, which builds a DCDB command, maps at most one SGL entry, copies the SCSI CDB, chooses firmware timeout class, and submits the DCDB mailbox. Physical devices are configured as no-ULD-attach so they are visible for management/pass-through but not normal block use.

Interrupt handlers are backend-specific but share the same pattern: acknowledge interrupt/status, identify command ID, map driver command IDs 1/2 to `dcmd_blk`/`mcmd_blk` or SCSI IDs `tag + 3` back through `scsi_host_find_tag()`, store firmware status, clear the status entry, and call either `myrb_handle_cmdblk()` or `myrb_handle_scsi()`. The older P backend translates old opcodes and command layouts before/after hardware submission.

Monitoring is a delayed ordered workqueue. `myrb_monitor()` prioritizes pending event log entries, error table updates, rebuild progress, logical-drive changes, consistency-check progress, background initialization, then periodic enquiry. Enquiry updates flags that drive subsequent monitor work and logs state changes such as deferred write errors, logical drive count/state changes, dead physical devices, and rebuild/check transitions.

Sysfs store methods issue synchronous firmware commands to start/cancel rebuilds, start/cancel consistency checks, change physical drive state, or flush cache. Show methods fetch current device state, RAID level, rebuild progress, controller number, firmware version, and model.

## State and Persistence Behavior

Controller state lives in `struct myrb_hba` from `myrb.h`, accessed through `shost_priv()`. This file manages firmware enquiry buffers, logical-drive info, error tables, command/status memory mailboxes, DMA pools for SGL/DCDB objects, command blocks for synchronous commands, monitor flags, geometry/cache/model/firmware metadata, and backend function pointers. Logical and physical device per-SCSI-device state is stored in `sdev->hostdata` and freed in `myrb_sdev_destroy()`.

The driver does not store persistent data in the filesystem. It sends persistent or controller-affecting firmware commands, including starting/stopping rebuilds, consistency checks with auto-restore, physical device state changes, cache flushes, and possible controller reset. Firmware/controller state is authoritative and is periodically re-queried into host memory.

## Dependencies and Integration Points

The file integrates with PCI, MMIO/PIO register accessors, DMA pools/coherent memory, the SCSI host/midlayer, blk-mq request tags, SCSI sense helpers, Linux RAID class, sysfs device attributes, delayed workqueues, and firmware ABI structures/macros from `myrb.h`. It also depends on legacy DAC960 hardware register definitions from the header. `myrb.h` is essential context for mailbox unions, status codes, HBA fields, controller constants, and backend register offsets.

## Risks and Edge Cases

- Removal order in `myrb_remove()` calls `myrb_cleanup()` before `myrb_destroy_mempools()`. Since cleanup releases the SCSI host reference and mempool destroy accesses `cb`, this order should be reviewed against current object lifetime guarantees.
- `myrb_pthru_queuecommand()` only supports `nsge <= 1`; if `scsi_dma_map()` returns 0, it still dereferences the first SG entry. DMA_NONE or zero-length physical pass-through commands need careful validation.
- `REQUEST_SENSE` in logical-drive command handling copies sense data and returns without calling `scsi_done()`, unlike adjacent software-completed commands; this is a likely bug or at least a high-priority behavior check.
- `consistency_check_store()` initializes `ldev_num` to `0xFFFF` and never updates it from `rbld_buf`, so cancel likely always reports "not in progress" for the selected logical drive.
- Several error paths in backend init request I/O regions or allocate coherent memory before later failure; unwind depends on `myrb_cleanup()` seeing partially initialized fields.
- Command IDs reserve 1 and 2 for driver/monitor commands and use `tag + 3` for SCSI. Queue depth and tag allocation must never exceed firmware mailbox assumptions.
- Hardware mailbox handlers hold `queue_lock` while calling `myrb_handle_scsi()` and `scsi_done()`, which may have latency or lock-order implications.
- Older P-controller command translation mutates mailbox fields before submission and restores them on completion; missed restoration could confuse shared completion/error paths.

## Test Signals

Useful tests include probe/remove for LA, PG, PD, and P PCI IDs; firmware version gating; logical drive scan and state updates; software-emulated INQUIRY/MODE SENSE/READ CAPACITY paths; read/write with direct and SG DMA; physical pass-through with DMA_NONE, one SG, and multiple SG cases; IRQ completion for synchronous and SCSI commands; monitor work under event/rebuild/logical-drive changes; sysfs rebuild/consistency/raid_state/cache controls; RAID class resync/state reads; host reset; and teardown with in-flight monitor work and commands. Static analysis should specifically flag missing `scsi_done()` paths and partial-probe cleanup leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrb.c -->
