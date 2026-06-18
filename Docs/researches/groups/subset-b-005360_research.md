# subset-b-005360 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/stex.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/stex.c

## Purpose
`stex.c` implements the PCI SCSI host driver for Promise SuperTrak EX and related Promise/SymplyStor RAID controllers. It exposes logical arrays through the Linux SCSI mid-layer, owns controller handshake/reset/power-management paths, and translates SCSI commands into Promise request/status queue messages.

## Important APIs, Types, And Functions
The core state is `struct st_hba`, which holds MMIO mappings, coherent request/status memory, queue indices, card type, CCB table, reset workqueue, waitqueue, and Promise-specific callbacks. `struct st_ccb` binds a SCSI command to a firmware request, sense buffer, SG count, and returned SRB/SCSI status. `struct req_msg`, `struct status_msg`, `struct st_msg_header`, and `struct handshake_frame` are the firmware wire formats.

The SCSI-facing entry points are `stex_queuecommand()`, `stex_sdev_configure()`, `stex_abort()`, `stex_reset()`, and `stex_biosparam()` in `driver_template`. PCI lifecycle is handled by `stex_probe()`, `stex_remove()`, `stex_shutdown()`, `stex_suspend()`, and `stex_resume()`. Interrupt paths split between legacy/common controllers (`stex_intr()`, `stex_mu_intr()`) and SS/Yel/P3-style controllers (`stex_ss_intr()`, `stex_ss_mu_intr()`). Firmware setup/reset flows are `stex_common_handshake()`, `stex_ss_handshake()`, `stex_handshake()`, `stex_do_reset()`, `stex_yos_reset()`, `stex_hard_reset()`, `stex_ss_reset()`, and `stex_p3_reset()`.

## Control Flow
Module init registers `stex_pci_driver`. Probe enables PCI, maps BAR0, sets a 64-bit or 32-bit DMA mask, chooses `st_card_info`, allocates one coherent DMA region containing request slots, optional scratch space, status slots, and copy buffers, allocates CCBs, requests IRQ/MSI, performs the firmware handshake, then registers and scans a SCSI host.

`stex_queuecommand_lck()` rejects commands while disconnected or reset, locally emulates some management-visible commands (`MODE_SENSE_10` caching page, console-device `INQUIRY`/`TEST_UNIT_READY`, driver-version passthrough), allocates the next request ring slot, maps SG entries, stores the SCSI command in the tag-indexed CCB, and rings the appropriate controller doorbell. Interrupt handlers drain status entries, validate tags/payload sizes, copy sense or data payloads, unmap DMA, translate SRB/SCSI status through `stex_scsi_done()`, and complete the SCSI command. Reset work may be queued from firmware reset-request bits or SCSI EH; it serializes through `mu_status` and `reset_waitq`, fails outstanding commands with `DID_RESET`, re-handshakes, and wakes waiters.

## State And Persistence Behavior
Runtime state is volatile driver/controller state: coherent request/status queues, queue head/tail indices, `out_req_cnt`, CCB slots, `mu_status`, MSI state, PM support, and `S6flag` from the reboot notifier. No disk persistence is maintained by the driver; durable storage state is owned by the RAID firmware. Suspend/shutdown paths send management CDBs (`CTLR_SHUTDOWN`, `PMIC_SHUTDOWN`, or power-state commands) and set `MU_STATE_STOP`.

## Dependencies And Integration Points
The driver integrates with PCI, DMA mapping, the SCSI host template, block queue timeouts, SCSI EH, MSI/IRQ APIs, reboot notifiers, and Promise firmware MMIO doorbells. It depends on card-specific register layouts and request formats selected by `st_card_info`. It also exposes a synthetic Promise RAID console target at `host->max_id - 1`.

## Risks
Important risks include tag/ring corruption, invalid firmware status heads, completion for stale CCBs, reset races while interrupts return pending commands, coherent DMA sizing for large controller families, and different semantics between legacy and SS/P3 doorbells. `scsi_dma_map()` failures are guarded with `BUG_ON(nseg < 0)`, so unexpected DMA map failures are fatal. Abort tries to poll pending interrupts before failing, which can race with normal interrupt completion. Reboot notifier registration is global while the driver can bind multiple devices.

## Test Signals
Useful signals include probe failure injection at each allocation/mapping/IRQ/handshake step, 32-bit and 64-bit DMA mask coverage, MSI and shared IRQ paths, command completion with valid and invalid tags, passthrough driver-version and adapter-info commands, console target behavior, lost-interrupt abort handling, firmware-requested reset, SCSI EH host reset, remove with outstanding I/O, suspend/resume/shutdown PM commands for PM-capable and non-PM cards, and queue-depth/tag boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/stex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/storvsc_drv.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/storvsc_drv.c

## Purpose
`storvsc_drv.c` implements the Microsoft Hyper-V virtual storage SCSI driver. It negotiates the VM storage protocol over VMBus, exposes synthetic SCSI, IDE, and Fibre Channel devices to the Linux SCSI mid-layer, maps SCSI SG lists into Hyper-V multipage buffers, handles completions and unsolicited LUN-change notifications, and manages multichannel I/O distribution.

## Important APIs, Types, And Functions
Protocol structures include `struct vstor_packet`, `struct vmscsi_request`, `struct vmstorage_protocol_version`, `struct vmstorage_channel_properties`, and `struct hv_fc_wwn_packet`. Driver state is held in `struct storvsc_device` for per-VMBus-channel storage state and `struct hv_host_device` for SCSI host-private state. Each SCSI command uses `struct storvsc_cmd_request` as `cmd_size` private storage.

Key functions are `storvsc_probe()`, `storvsc_remove()`, `storvsc_suspend()`, `storvsc_resume()`, `storvsc_connect_to_vsp()`, `storvsc_channel_init()`, `storvsc_execute_vstor_op()`, `handle_multichannel_storage()`, `handle_sc_creation()`, `storvsc_queuecommand()`, `storvsc_do_io()`, `storvsc_on_channel_callback()`, `storvsc_on_receive()`, `storvsc_on_io_completion()`, `storvsc_command_completion()`, `storvsc_handle_error()`, and `storvsc_host_reset_handler()`.

## Control Flow
Module init computes the aligned VMBus ring size and maximum outstanding requests per channel, optionally attaches the FC transport, and registers `storvsc_drv`. Probe sizes `scsi_driver.can_queue` from ring capacity and subchannel count, allocates a SCSI host and `storvsc_device`, opens the primary VMBus channel, negotiates protocol versions from newest supported downward, queries channel properties, optionally fetches FC WWNs, ends initialization, creates subchannels when supported, sets SCSI host limits by device class, creates the ordered error workqueue, registers the host, and scans or adds the IDE boot device.

`storvsc_queuecommand()` filters known-bad legacy commands on older hosts, fills the VMSC SCSI request, maps the SCSI SG list, builds an inline or heap multipage-buffer payload, and calls `storvsc_do_io()` with the current CPU. `storvsc_do_io()` picks a VMBus channel by CPU affinity, NUMA locality, and ring free-space percentage, sends an in-band or MPB descriptor packet, and increments `num_outstanding_req`. The callback drains packets with a small time budget, validates packet length and transaction IDs, maps nonzero transaction IDs back to SCSI tags, unmaps DMA, copies status/sense/transfer length, runs error-specific work scheduling, completes the SCSI command, frees heap payloads, and wakes drain waiters when outstanding I/O reaches zero.

## State And Persistence Behavior
State is volatile guest-driver state: negotiated `vmstor_proto_version`, ring-buffer sizing module parameters, `stor_chns` CPU-to-channel cache, `alloced_cpus`, FC `node_name`/`port_name`, `destroy` and drain flags, and outstanding request count. No persistent storage metadata is written by this driver. Suspend drains requests, drains the error workqueue, closes the channel, frees channel mappings, and clears CPU masks; resume reconnects and renegotiates.

## Dependencies And Integration Points
The file integrates the Hyper-V VMBus API, Linux SCSI host/device/EH APIs, blk-mq tags, DMA mapping, CPU masks and NUMA topology, FC transport attributes when configured, and SCSI device scanning/removal workqueues. It depends on Hyper-V packet IDs: `VMBUS_RQST_INIT`, `VMBUS_RQST_RESET`, and command transaction IDs derived from SCSI tags plus one.

## Risks
High-risk areas are transaction-ID validation, unsolicited packet rejection, heap payload lifetime for large SG lists, races between removal and inbound completions, channel selection while target CPUs move, global `vmstor_proto_version` across devices, and trusting host-reported transfer lengths. The code clamps transfer length to the payload length and rejects bogus ID-zero completion/FC data packets, but correctness still depends on strict VMBus/SCSI tag pairing. Reset handling waits for all in-flight packets after bus reset because host responses may still be arriving.

## Test Signals
Test probe against SCSI, IDE, and synthetic FC GUIDs; protocol negotiation fallback; obsolete host rejection; multichannel creation and CPU retargeting; ring low-water channel fallback; large SG lists requiring heap MPB payloads; `PAGE_SIZE != HV_HYP_PAGE_SIZE` PFN construction; invalid transaction IDs and short packets; LUN add/remove notifications; capacity/granularity sense-triggered rescan; invalid-LUN removal; host reset drain; suspend/resume reconnect; FC WWN updates; queue-depth clamping; and legacy command filtering for `WRITE_SAME`/`SET_WINDOW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/storvsc_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi.c

## Purpose
`sun3_scsi.c` is the Sun3 NCR5380 SCSI controller front-end. It wires the generic `NCR5380.c` core to Sun3 on-board or VME DMA hardware, provides platform probe/remove glue, and implements Sun3-specific DVMA setup, FIFO handling, interrupt dispatch, and residual reporting.

## Important APIs, Types, And Functions
The file defines `NCR5380_read()`, `NCR5380_write()`, and NCR5380 callback aliases before including `NCR5380.h` and later `NCR5380.c`. Hardware layouts are `struct sun3_dma_regs` and, for non-VME on-board controllers, `struct sun3_udc_regs`. Important functions are `scsi_sun3_intr()`, `sun3scsi_dma_setup()`, `sun3scsi_dma_count()`, `sun3scsi_dma_residual()`, `sun3scsi_dma_xfer_len()`, `sun3scsi_dma_start()`, `sun3scsi_dma_finish()`, `sun3_scsi_probe()`, and `sun3_scsi_remove()`.

## Control Flow
At build time, the file becomes either `sun3_scsi` or a VME variant depending on `SUN3_SCSI_VME`. Probe applies module-parameter overrides for queue depth, commands per LUN, SG table size, and host ID. Non-VME probe maps one memory resource and allocates DVMA memory for UDC descriptors. VME probe scans up to two IRQ/MMIO resource pairs, maps VME16 space, and tests whether the DMA CSR looks like a present board. Probe then allocates a SCSI host with `NCR5380_hostdata`, initializes the generic NCR5380 core, requests the IRQ, initializes the Sun3 DMA registers, optionally resets the SCSI bus, registers the host, and scans.

For data transfer, `sun3scsi_dma_xfer_len()` requests DMA only for non-passthrough transfers of at least `DMA_MIN_SIZE`. `sun3scsi_dma_setup()` maps the buffer into DVMA space, resets FIFO/UDC state, programs direction and count/address registers, and returns the accepted byte count. The generic NCR5380 core calls `sun3scsi_dma_start()` to launch the UDC or VME DMA count and later `sun3scsi_dma_finish()` to disable DMA, drain/read FIFO leftovers, compute `last_residual`, copy residual packed bytes back into memory for reads, unmap DVMA, and reset controller state. The IRQ handler checks DMA error bits and forwards SCSI/DMA interrupts to `NCR5380_intr()`.

## State And Persistence Behavior
The driver uses file-static state for the single supported controller: `dregs`, `udc_regs`, `sun3_dma_orig_addr`, `sun3_dma_orig_count`, `sun3_dma_active`, `sun3_dma_setup_done`, and `last_residual`. There is no persistent state; all state is MMIO, DVMA mappings, and NCR5380 host state. The TODO notes lack of support for multiple Sun3 SCSI VME boards, and the globals enforce that limitation.

## Dependencies And Integration Points
It depends on m68k Sun3 IO/DVMA helpers, the platform bus, SCSI host APIs, the generic NCR5380 core, and platform-provided IRQ/MMIO resources. VME builds additionally use `sun3_ioremap()`, VME page types, `dvma_map_vme()`, and `sun3_map_test()`.

## Risks
The main risks are single-controller global state, FIFO residual edge cases on odd read/write counts, UDC timeout paths, VME board detection false positives, DVMA mapping lifetime, and error unwinding across partially initialized NCR5380/DVMA resources. The code returns DMA length zero for small/passthrough commands, so performance and correctness depend on the NCR5380 PIO fallback.

## Test Signals
Test non-VME and VME builds, module-parameter overrides, missing resources, IRQ request failure, DVMA allocation failure, DMA transfers below and above `DMA_MIN_SIZE`, odd-length reads/writes, FIFO empty timeout, DMA bus error/conflict IRQ reporting, VME board probing, residual reporting through the NCR5380 core, remove cleanup, and `NCR5380_maybe_reset_bus()` behavior during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi_vme.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi_vme.c

## Purpose
`sun3_scsi_vme.c` is a tiny wrapper that builds the Sun3 NCR5380 front-end in VME mode. It defines `SUN3_SCSI_VME` and includes `sun3_scsi.c`, causing that implementation to compile with VME-specific register programming, probing, naming, and DVMA helpers.

## Important APIs, Types, And Functions
The file declares no standalone functions or data structures. Its only API effect is the `SUN3_SCSI_VME` preprocessor symbol, which changes `sun3_scsi.c` behavior: the driver name becomes `sun3_scsi_vme`, the SCSI host name becomes "Sun3 NCR5380 VME SCSI", VME resources are probed, VME DVMA mapping is used, and VME-specific DMA address/count/fifo/interrupt-vector registers are programmed.

## Control Flow
There is no runtime control flow in this file itself. Compilation flows into `sun3_scsi.c` with the VME branch enabled. The resulting platform driver is registered through `module_platform_driver_probe()` from the included file and probes VME MMIO/IRQ resource pairs.

## State And Persistence Behavior
No independent state is stored here. All runtime state is the file-static Sun3 NCR5380 state from `sun3_scsi.c`, including the single-controller DMA globals and NCR5380 host data. The wrapper creates no persistent state.

## Dependencies And Integration Points
This file depends entirely on `sun3_scsi.c`. It integrates through Kbuild/compilation rather than a C-call boundary, so source-level changes to `sun3_scsi.c` directly affect the VME variant.

## Risks
The primary risk is that the wrapper hides a second compiled personality of `sun3_scsi.c`; changes tested only in the on-board build may break the VME build. VME-specific risks inherited from the included file include resource scanning, board detection through CSR behavior, VME interrupt-vector setup, and packed FIFO residual handling.

## Test Signals
Test signals are compile coverage for the VME object, platform alias/name matching for `sun3_scsi_vme`, VME resource probing, IRQ vector programming, VME DVMA map/unmap, and the full Sun3 NCR5380 DMA/interrupt test set under `SUN3_SCSI_VME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi_vme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3x_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun3x_esp.c

## Purpose
`sun3x_esp.c` is the Sun3x platform front-end for the generic ESP SCSI core. It maps Sun3x ESP and DMA registers, implements `esp_driver_ops` for big-endian m68k DMA register access, and registers a platform SCSI host named `sun3x_esp`.

## Important APIs, Types, And Functions
The key integration object is `sun3x_esp_ops`, which supplies `esp_write8`, `esp_read8`, `irq_pending`, `reset_dma`, `dma_drain`, `dma_invalidate`, `send_dma_cmd`, and `dma_error` to `esp_scsi.c`. Probe/remove are `esp_sun3x_probe()` and `esp_sun3x_remove()`. DMA helper functions are `sun3x_esp_reset_dma()`, `sun3x_esp_dma_drain()`, `sun3x_esp_dma_invalidate()`, `sun3x_esp_send_dma_cmd()`, and `sun3x_esp_dma_error()`.

## Control Flow
Probe allocates a SCSI host with `scsi_esp_template`, sets `host->max_id`, initializes the embedded `struct esp`, maps ESP registers from memory resource 0 and DMA registers from resource 1, allocates a coherent 16-byte command block, requests the platform IRQ with `scsi_esp_intr`, sets initiator ID 7, configures the ESP clock to 20 MHz, stores driver data, and calls `scsi_esp_register()`. Remove unregisters the ESP core, disables DMA interrupts, frees IRQ and command-block DMA memory, and releases the SCSI host.

During I/O, the ESP core calls the ops. Register accesses use `reg * 4` spacing. DMA reset toggles `DMA_RST_SCSI` and enables interrupts. Drain waits for `DMA_FIFO_ISDRAIN` to clear after requesting standard drain. Invalidate waits for `DMA_PEND_READ`, disables DMA/write/count, toggles `DMA_FIFO_INV`, and clears it. `send_dma_cmd()` loads ESP transfer count bytes, enables DMA, sets write direction, writes the DMA address, and starts the ESP command.

## State And Persistence Behavior
State is the generic `struct esp` plus mapped MMIO pointers, command-block DMA address, IRQ number, configured SCSI ID/mask, and clock frequency. No persistent state is stored. DMA controller state is reset or invalidated around transfers.

## Dependencies And Integration Points
The driver depends on Sun3x platform resources, m68k DMA/DVMA headers, coherent DMA allocation, platform IRQs, and the generic `esp_scsi` core. It intentionally bypasses normal `readl()`/`writel()` in favor of volatile 32-bit accesses because the m68k helpers assume little-endian MMIO semantics that are wrong for Sun3x.

## Risks
Risks include endian-sensitive DMA register access, missing cleanup of mapped MMIO in remove, drain/invalidate timeouts that only log, IRQ sharing interactions, and hard-coded SCSI ID/clock assumptions. Probe error unwinding unmaps resources, but normal remove frees only IRQ/command block/host and disables interrupts.

## Test Signals
Test probe/remove on Sun3x platform resources, endian-correct DMA CSR reads/writes, DMA interrupt pending and error bits, FIFO drain timeout, pending-read invalidate timeout, read/write DMA command setup, command-block allocation failure, IRQ request failure, `scsi_esp_register()` failure unwinding, and generic ESP command completion through `scsi_esp_intr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3x_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun_esp.c

## Purpose
`sun_esp.c` is the SPARC SBUS/Open Firmware front-end for the generic ESP SCSI core. It supports classic ESP/FAS and HME-style FAS366 arrangements, maps DMA and ESP registers from OF platform devices, derives initiator/clock/burst/differential properties, and supplies SBUS-specific DMA operations to `esp_scsi.c`.

## Important APIs, Types, And Functions
`enum dvma_rev` classifies DMA revisions. The `sbus_esp_ops` table implements ESP register access, IRQ pending checks, DMA reset/drain/invalidate/send/error callbacks. Setup helpers include `esp_sbus_setup_dma()`, `esp_sbus_map_regs()`, `esp_sbus_map_command_block()`, `esp_sbus_register_irq()`, `esp_get_scsi_id()`, `esp_get_differential()`, `esp_get_clock_params()`, `esp_get_bursts()`, and `esp_sbus_get_props()`. Platform lifecycle is `esp_sbus_probe()`, `esp_sbus_probe_one()`, and `esp_sbus_remove()`.

## Control Flow
OF matching binds names `SUNW,esp`, `SUNW,fas`, and `esp`. Probe finds the DMA platform device from the parent `espdma`/`dma` node or treats `SUNW,fas` as HME with combined resources. `esp_sbus_probe_one()` allocates a SCSI host, sets max target ID by HME capability, records wide capability for HME, maps DMA and ESP registers, allocates the command block, requests IRQ, reads OF properties, clears ESC1 reset state if necessary, stores driver data, and registers with the ESP core.

DMA reset first normalizes the DMA engine based on revision. HME reset programs parity/timing/interrupt/burst/SBUS64 bits in `prev_hme_dmacsr`, waits for pending reads to clear, and resets address/count state. Other revisions set 2-clock/3-clock, burst, add-enable, or FIFO behavior as needed. `sbus_esp_send_dma_cmd()` handles FASHME specially by programming 24-bit ESP transfer count, issuing the ESP command before DMA CSR/address/count enable, and preserving HME CSR state; other revisions enable DMA, optionally set ESC1 byte count, write DMA address, then issue the ESP command. Remove unregisters ESP, disables interrupts, frees IRQ/DMA memory, unmaps both register resources, drops the SCSI host, clears driver data, and releases the DMA device reference.

## State And Persistence Behavior
State is volatile `struct esp` state plus DMA revision, burst mask, HME previous CSR image, OF-derived SCSI ID/clock/differential flags, mapped register pointers, IRQ, and command-block DMA memory. There is no persistent state.

## Dependencies And Integration Points
The driver integrates OF platform discovery, SBUS IO helpers, SPARC DMA capability helpers (`sbus_can_dma_64bit()`, `sbus_can_burst64()`, `sbus_set_sbus64()`), Linux IRQ/DMA APIs, and the generic ESP SCSI core. It also interacts with FC/SCSI-style SCSI target behavior indirectly through `esp_scsi`.

## Risks
Risks are revision-specific DMA programming differences, HME CSR shadow corruption, OF property fallback mistakes, DMA node lifetime/reference handling, FIFO drain/invalidate timeouts, resource-index differences between HME and non-HME devices, and SBUS64/burst negotiation mismatches. The probe path must unwind mapped resources and command-block memory precisely.

## Test Signals
Test OF matches for `SUNW,esp`, `SUNW,fas`, and `esp`; parent-DMA versus HME resource topology; DMA revisions `DMA_VERS0`, `DMA_ESCV1`, `DMA_VERS1`, `DMA_VERS2`, `DMA_VERHME`, and `DMA_VERSPLUS`; burst property intersections; SCSI ID property fallback; differential flag handling; HME and non-HME DMA send paths; drain/invalidate timeouts; remove cleanup; and `scsi_esp_register()`/IRQ/command-block failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/Makefile

## Purpose
This Kbuild file defines how the second-generation Symbios/LSI 53C8XX PCI SCSI controller driver is linked when `CONFIG_SCSI_SYM53C8XX_2` is enabled.

## Important APIs, Types, And Functions
There are no runtime APIs. The important Kbuild variables are `sym53c8xx-objs`, which lists `sym_fw.o`, `sym_glue.o`, `sym_hipd.o`, `sym_malloc.o`, and `sym_nvram.o`, and `obj-$(CONFIG_SCSI_SYM53C8XX_2)`, which selects the composite `sym53c8xx.o`.

## Control Flow
At build time, Kbuild links the listed component objects into `sym53c8xx.o` when the config symbol is built-in or modular. Runtime control flow begins in the linked C objects, not in this file.

## State And Persistence Behavior
No runtime state or persistence exists. The file only controls build composition.

## Dependencies And Integration Points
It integrates with the kernel Kbuild system and the SCSI Kconfig symbol `CONFIG_SCSI_SYM53C8XX_2`. Link completeness depends on symbols supplied across the five component translation units.

## Risks
Risks are stale object names, omitted objects causing unresolved symbols, and accidental build exclusion if the config symbol changes. Because firmware tables and glue/hipd logic are separate objects, object ordering and inclusion are required for a complete driver.

## Test Signals
Build with `CONFIG_SCSI_SYM53C8XX_2=y` and `m`, run modpost, verify `sym53c8xx.o` contains firmware, glue, HIPD, allocator, and NVRAM objects, and check clean builds after any file rename or source split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym53c8xx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym53c8xx.h

## Purpose
`sym53c8xx.h` is the Linux configuration header for the Symbios/LSI 53C8XX/53C1010 driver. It translates Kconfig choices into driver constants, declares the boot/module setup structure, and sets global limits for tags, scatter-gather, targets, LUNs, NVRAM, generic-chip support, immediate arbitration, and residual reporting.

## Important APIs, Types, And Functions
The central type is `struct sym_driver_setup`, containing max tags, burst order, LED/differential/IRQ/bus-check/host-ID settings, verbosity, settle delay, NVRAM usage, and excluded devices. `SYM_LINUX_DRIVER_SETUP` provides defaults derived from Kconfig. Macros such as `SYM_CONF_DMA_ADDRESSING_MODE`, `SYM_CONF_NVRAM_SUPPORT`, `SYM_CONF_GENERIC_SUPPORT`, `SYM_CONF_MAX_TAG`, `SYM_CONF_MAX_TAG_ORDER`, `SYM_CONF_MAX_SG`, `SYM_CONF_MAX_TARGET`, `SYM_CONF_MAX_LUN`, `SYM_SETUP_*`, and `SYM_SETUP_RESIDUAL_SUPPORT` are consumed throughout the driver. The header declares `sym_driver_setup` and `sym_debug_flags`.

## Control Flow
There is no executable control flow. Compile-time conditionals clamp tag limits to 2..256 and select a tag-order power based on that maximum. Runtime setup flows through objects that instantiate `sym_driver_setup`, parse boot/module overrides, and use these macros in allocation, negotiation, queue-depth, and firmware selection.

## State And Persistence Behavior
The header defines shape and defaults for runtime setup state but stores no state itself. `sym_driver_setup` is externally defined and mutable at boot/module parameter parsing time. No persistent state is maintained.

## Dependencies And Integration Points
It depends on SCSI Symbios Kconfig symbols and is included by driver implementation files. It directly influences firmware selection (`SYM_CONF_GENERIC_SUPPORT`), firmware relocation/runtime data sizes (`SYM_CONF_MAX_SG`, tag order), PCI DMA addressing behavior, proc/debug/user-command support, and NVRAM behavior.

## Risks
Risks include compile-time limits that must match firmware table sizes and C data structures, tag-order mismatches, enabling unsupported DMA addressing modes, and global defaults that affect all adapters. Increasing `SYM_CONF_MAX_SG` or max tags without matching memory/script assumptions could corrupt firmware scripts or queues.

## Test Signals
Test builds across DMA addressing modes 0/1/2, max tags below 2, normal, and above 256, default tag overrides, NVRAM enabled behavior, generic-chip fallback, residual reporting, and driver parameter parsing that updates `sym_driver_setup`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym53c8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_defs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_defs.h

## Purpose
`sym_defs.h` defines the hardware vocabulary for the Symbios/LSI SCSI processor driver: chip feature flags, the memory-mapped register layout, SCRIPTS instruction encodings, table formats, SCSI phase constants, message constants, PPR options, and SCSI status aliases.

## Important APIs, Types, And Functions
Important data types are `struct sym_chip`, which describes a supported chip ID/revision/name/features and timing capabilities; `struct sym_reg`, a packed-by-layout representation of the chip register file; `struct sym_tblmove`, used by indirect move SCRIPTS entries; and `struct sym_tblsel`, used by table-driven selection. Feature flags include `FE_WIDE`, `FE_ULTRA*`, `FE_LDSTR`, `FE_RAM`, `FE_64BIT`, `FE_NOPM`, `FE_CRC`, `FE_C10`, `FE_DAC`, and others. Instruction macros include `SCR_MOVE_*`, `SCR_SEL_*`, `SCR_WAIT_*`, `SCR_SET`, `SCR_CLR`, `SCR_COPY`, register operation macros, load/store macros, `SCR_JUMP`/`SCR_CALL`/`SCR_INT`, condition macros, and phase/message/status aliases.

## Control Flow
The header has no runtime control flow, but the constants directly generate the firmware SCRIPTS arrays in `sym_fw1.h`/`sym_fw2.h`. The C code also uses `REG()` offsets and feature bits to program registers, patch scripts, and choose firmware. Runtime SCRIPTS control flow is encoded as 32-bit opcodes built by these macros.

## State And Persistence Behavior
No state is stored here. It defines register offsets and bit meanings for live chip state and shared script structures. Persistent hardware/NVRAM data is handled elsewhere.

## Dependencies And Integration Points
The header depends on SCSI protocol constants from the kernel and on structure offsets matching the chip manuals. It is consumed by firmware definitions, relocation code, and the high-level driver implementation. `sym_fw_bind_script()` depends on the top nibble and relocation forms generated from these macros.

## Risks
Risks are especially high because a wrong register offset or opcode bit can produce invalid DMA, SCSI bus hangs, or incorrect script relocation. `struct sym_reg` must match real MMIO layout. Feature flags must match silicon quirks, and SCRIPTS macros must preserve exact instruction lengths expected by firmware struct arrays.

## Test Signals
Test signals include compile-time firmware generation, script relocation, supported chip probing by feature flags, register programming on multiple revisions, wide/sync/PPR negotiation, phase mismatch handling, SCSI reset/interrupt status decoding, load/store firmware on `FE_LDSTR` chips, generic firmware on older chips, and hardware or emulator validation of SCRIPTS opcode streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.c

## Purpose
`sym_fw.c` instantiates, selects, patches, sets up, and relocates the Symbios SCRIPTS firmware templates. It includes firmware template headers under different symbol names, builds offset tables, fills runtime-generated scatter-gather script slots, computes bus-address tables, chooses firmware by chip features, and binds script operands to physical/MMIO addresses.

## Important APIs, Types, And Functions
Externally important functions are `sym_find_firmware()` and `sym_fw_bind_script()`. Internal setup/patch functions include `sym_fw1_patch()`, `sym_fw2_patch()`, `sym_fw_fill_data()`, `sym_fw_setup_bus_addresses()`, `sym_fw1_setup()`, and `sym_fw2_setup()`. Static firmware descriptors `sym_fw1` and `sym_fw2` are built with `SYM_FW_ENTRY()`, with firmware #1 present when `SYM_CONF_GENERIC_SUPPORT` is enabled and firmware #2 always present.

## Control Flow
At compile time the file includes `sym_fw1.h` and `sym_fw2.h` with macro-renamed script objects, then initializes offset tables through `SYM_GEN_FW_A/B/Z`. At runtime, `sym_find_firmware()` returns the load/store firmware for chips with `FE_LDSTR`, otherwise the generic firmware for older chips that do not require prefetch, phase-mismatch, or DAC features.

Firmware setup fills `data_in` and `data_out` script arrays for `SYM_CONF_MAX_SG` entries using `SCR_CHMOV_TBL` and offsets into `struct sym_dsb`, then builds host-side script label bus-address tables from base DMA addresses and offset tables. Patch functions remove LED instructions when unsupported, optionally remove IARB hints, patch queue and target-table bus addresses, remove 64-bit DMA dirty-map logic when DAC is unavailable, remove C1010-only reselection or workaround paths when not applicable, and patch phase-mismatch mini-script addresses.

`sym_fw_bind_script()` walks a script dword stream, converts opcodes to script endian, checks illegal zero opcodes, turns `SCR_DATA_ZERO` placeholders into zero, determines how many operands require relocation based on opcode class, removes `SCR_NO_FLUSH` when prefetch is unsupported, adjusts MOVE/CHMOV forms for non-wide chips, and relocates register, script A/B label, and host-control-block references to actual bus/MMIO addresses.

## State And Persistence Behavior
The file mutates per-adapter in-memory script copies through setup, patch, and bind. Persistent device state is not stored. Script templates are static; runtime state is derived from `struct sym_hcb` DMA/MMIO base addresses, feature flags, queue bus addresses, target table address, PCI device ID/revision, and clock.

## Dependencies And Integration Points
It depends on `sym_glue.h`, `sym_fw.h`, `sym_fw1.h`, `sym_fw2.h`, `sym_defs.h` opcodes, `struct sym_hcb`, `struct sym_data`, PCI IDs, feature flags, endian conversion via `cpu_to_scr()`, and debug/panic helpers. It is the bridge between C host data structures and the SCRIPTS processor code executed by the controller.

## Risks
Risks include mismatched script struct lengths versus initializer contents, incorrect relocation classification, stale patch offsets, feature detection mistakes causing unsupported script instructions, and panic on unexpected relocation tags. Firmware patching writes directly into script copies, so label offsets and struct fields must stay synchronized across headers and generated tables.

## Test Signals
Test firmware selection for `FE_LDSTR`, generic fallback, and unsupported combinations; bind scripts with and without `FE_PFEN`, `FE_WIDE`, `FE_DAC`, `FE_C10`, and C1010 revision workarounds; validate generated bus-address tables; enable `DEBUG_SCRIPT`; run hardware I/O with wide and narrow devices; exercise reselection, phase mismatch, negotiation, abort, and data-overrun paths; and build after any firmware template length change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.h

## Purpose
`sym_fw.h` defines the C interface between the Symbios driver and its SCRIPTS firmware templates. It standardizes label lists, offset-table and bus-address structures, firmware descriptors, firmware declaration macros, script bus-address accessors, and relocation marker encodings used inside the template headers.

## Important APIs, Types, And Functions
Important macros are `SYM_GEN_FW_A`, `SYM_GEN_FW_B`, and `SYM_GEN_FW_Z`, which enumerate externally useful labels in script areas A, B, and Z. Types include `struct sym_fwa_ofs`, `struct sym_fwb_ofs`, `struct sym_fwz_ofs`, their bus-address counterparts `struct sym_fwa_ba`, `struct sym_fwb_ba`, `struct sym_fwz_ba`, and `struct sym_fw`. `SYM_FW_ENTRY()` builds a firmware descriptor from template objects and setup/patch functions. `SCRIPTA_BA()`, `SCRIPTB_BA()`, and `SCRIPTZ_BA()` access computed label bus addresses. Relocation macros include `HADDR_1/2`, `RADDR_1/2`, `SYM_GEN_PADDR_A/B`, and marker constants `RELOC_SOFTC`, `RELOC_LABEL_A`, `RELOC_REGISTER`, `RELOC_LABEL_B`, plus `SCR_DATA_ZERO`.

## Control Flow
There is no runtime control flow. Compile-time macro expansion generates offset structures in `sym_fw.c` and relocation-coded operands in firmware template headers. Runtime code consumes the resulting descriptor and relocation markers in setup/patch/bind functions.

## State And Persistence Behavior
The header defines descriptor shapes and relocation encodings but stores no state. Per-adapter state lives in `struct sym_hcb` fields such as `fwa_bas`, `fwb_bas`, and `fwz_bas`, which match the bus-address structures defined here.

## Dependencies And Integration Points
It depends on `struct sym_hcb`, `struct Scsi_Host`, register offset macro `REG()`, and script struct definitions from firmware headers. It integrates script labels with C code that jumps into script fragments or patches script operands.

## Risks
The key risk is interface drift: adding/removing labels in script templates without updating `SYM_GEN_FW_A/B/Z` or firmware offset structs can break C references or relocation. Relocation marker values must remain consistent with `sym_fw_bind_script()`'s `RELOC_MASK` decoding. `SCR_DATA_ZERO` must not collide with valid script data needing preservation.

## Test Signals
Compile all firmware templates, verify offset-table initialization, run script binding on all firmware areas, inspect `SCRIPTA_BA`/`SCRIPTB_BA` users for valid labels, and test after adding any script label or relocation form.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw1.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw1.h

## Purpose
`sym_fw1.h` is the generic Symbios SCRIPTS firmware template used for older/non-load-store chips when `SYM_CONF_GENERIC_SUPPORT` is enabled. It defines the layout and initializer contents for script area A, script area B, and initialization script Z, encoding SCSI selection, command dispatch, data movement, message handling, reselection, completion, abort, negotiation, and snoop-test behavior.

## Important APIs, Types, And Functions
The main types are `struct SYM_FWA_SCR`, `struct SYM_FWB_SCR`, and `struct SYM_FWZ_SCR`. They are not normal callable APIs; their array fields are named script labels consumed by `sym_fw.h` and `sym_fw.c`. Script A contains hot-path labels such as `start`, `getjob_begin`, `select`, `wf_sel_done`, `send_ident`, `command`, `dispatch`, `init`, `clrack`, `datai_done`, `datao_done`, `msg_in`, `status`, `complete`, `done`, `save_dp`, `restore_dp`, `disconnect`, `idle`, `ungetjob`, `reselect`, `reselected`, `resel_tag`, `resel_dsa`, `resel_no_tag`, `data_in`, `data_out`, `pm0_data`, and `pm1_data`. Script B contains out-of-line paths such as `no_data`, `sel_for_abort`, `msg_bad`, `msg_weird`, `wdtr_resp`, `send_wdtr`, `sdtr_resp`, `send_sdtr`, `ppr_resp`, `send_ppr`, `data_ovrun`, `abort_resel`, `resel_bad_lun`, `bad_i_t_l`, `bad_i_t_l_q`, and data slots like `done_pos`, `startpos`, and `targtbl`. Script Z provides `snooptest` and `snoopend`.

## Control Flow
The SCRIPTS processor starts at `start`, checks whether the host requested manual recovery, reads the next job from the start queue, loads DSA, selects the target with ATN, sends identify/tag/negotiation messages, sends the command, and dispatches by SCSI phase. Data phases jump through generated SG move tables; status and command-complete message paths save status, copy the CCB header back, flush posted writes with dummy reads, enqueue the DSA in the done queue, and raise `SCR_INT_FLY`. Disconnect paths save host status and return to the scheduler. Reselection waits in `reselect`, decodes target/LUN/tag, reloads transfer registers and CCB headers, and jumps back to the saved restart point. Script B handles extended/messages, negotiation replies, overrun byte counting, abort/reset message sending, bad status, bad reselections, and WSR residual-byte handling. Script Z performs a read/write/read memory snoop test then interrupts.

## State And Persistence Behavior
The template contains static script opcodes and `SCR_DATA_ZERO` placeholders. Runtime setup fills `data_in`/`data_out`, zeroes data placeholders, patches queue/target addresses, and relocates `HADDR`, `RADDR`, and `PADDR` operands into per-adapter bus/MMIO addresses. It persists no state beyond the controller-executed script copy in DMA memory.

## Dependencies And Integration Points
It depends on script opcode macros from `sym_defs.h`, relocation macros from `sym_fw.h`, host data structures such as `struct sym_hcb`, `struct sym_ccb`, `struct sym_dsb`, `struct sym_ccbh`, `struct sym_tcbh`, and `struct sym_lcbh`, and interrupt/status constants handled by the C driver (`SIR_*`, `HS_*`, `HF_*`, `SS_REG`, `HS_REG`, `HF_REG`). It is included by `sym_fw.c` under macro-renamed symbol names.

## Risks
This is high-risk firmware data: array lengths in the structs must match initializer instruction counts, self-modifying script slots must remain aligned with comments and offset tables, and host C structures must keep the offsets assumed by `offsetof()` operands. Bugs can lose completions, corrupt queues, mishandle reselection tags, hang the SCSI bus, or misreport residuals. Conditional blocks for IARB and target-role support change lengths and must stay synchronized.

## Test Signals
Test compile-time structure initializers, firmware offset generation, script relocation, generic firmware selection on non-`FE_LDSTR` chips, normal command completion, disconnect/reselect with tagged and untagged commands, SAVE/RESTORE DATA POINTER, wide residual handling, data overrun/underrun, negotiation messages (WDTR/SDTR/PPR), abort/reset recovery, bad LUN/tag reselection, snoop test interrupt, and completion queue integrity under heavy tagged I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw1.h -->
