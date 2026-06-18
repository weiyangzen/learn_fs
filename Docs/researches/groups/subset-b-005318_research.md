# subset-b-005318 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrb.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/myrb.h

## Purpose

`myrb.h` is the private hardware and firmware ABI header for the block-command-era Mylex DAC960/AcceleRAID/eXtremeRAID PCI RAID controller driver. It describes the older DAC960 V1 firmware interface: command opcodes, status codes, packed controller reply buffers, physical and logical device records, mailbox layouts, DMA helper records, controller-private host state, and register definitions for LA, PG, and PD controller families.

The file is not an implementation unit; it is the contract consumed by the matching V1 driver code. Most definitions are byte-annotated and `__packed`, so this header is part of the firmware-visible ABI rather than ordinary in-kernel data modeling.

## Important APIs, Types, and Functions

Key constants size the driver's view of the hardware: `MYRB_MAX_LDEVS`, `MYRB_MAX_CHANNELS`, `MYRB_MAX_TARGETS`, `MYRB_SCATTER_GATHER_LIMIT`, `MYRB_CMD_MBOX_COUNT`, `MYRB_STAT_MBOX_COUNT`, `MYRB_MAILBOX_TIMEOUT`, `MYRB_DCMD_TAG`, and `MYRB_MCMD_TAG`. Monitor intervals are split into primary and secondary polling periods.

`enum myrb_cmd_opcode` enumerates V1 firmware commands for extended and legacy reads/writes, DCDB passthrough, flush, enquiry, logical/physical device state, event log reads, rebuild, consistency check, background initialization, configuration, firmware image, diagnostic, and subsystem operations. The many `MYRB_STATUS_*` constants define command completion meanings, but several status values are reused across command families, so callers must interpret them in opcode context.

Firmware reply and request structures include `struct myrb_enquiry`, `struct myrb_enquiry2`, `struct myrb_ldev_info`, `struct myrb_pdev_state`, `struct myrb_log_entry`, `struct myrb_rbld_progress`, `struct myrb_bgi_status`, `struct myrb_error_entry`, `struct myrb_config2`, and `struct myrb_dcdb`. These model controller state, logical drive state, physical drive state, event log payloads, rebuild/background initialization progress, error counters, configuration flags, and direct SCSI command descriptor blocks.

`union myrb_cmd_mbox` is the core V1 submission ABI. It overlays the 16-byte command mailbox with opcode-specific views such as `common`, `type3`, `type3B`, `type3C`, `type3D`, `type3E`, `type3R`, `type4`, `type5`, and `typeX`. `struct myrb_stat_mbox` is the corresponding status mailbox record with command id, valid bit, and 16-bit status.

Driver-owned runtime types are `struct myrb_cmdblk`, which wraps a mailbox, completion status, optional DCDB, and optional S/G list, and `struct myrb_hba`, which stores controller geometry, feature flags, PCI/SCSI objects, workqueue and monitor state, DMA pools, mailbox rings, direct/monitor command blocks, enquiry/error/logical-device buffers, and hardware callback pointers. `struct myrb_privdata` selects a controller-family hardware initializer, IRQ handler, and MMIO size.

The bottom half of the header defines register offsets and bit masks for LA, PG, and PD controller interfaces, plus callback typedefs `myrb_hw_init_t` and `mbox_mmio_init_t`. These register constants are consumed by low-level code that polls doorbells, acknowledges status, masks interrupts, and resets controllers.

## Control Flow

The intended runtime flow is mailbox based. The driver allocates command and status mailbox rings, fills a `union myrb_cmd_mbox` variant for the operation it wants, uses controller-family register callbacks to notify the adapter, and later consumes a `struct myrb_stat_mbox` completion. Direct commands use reserved tag `MYRB_DCMD_TAG`; monitor commands use `MYRB_MCMD_TAG`; normal SCSI commands use other ids.

Controller discovery starts with enquiry commands. `MYRB_CMD_ENQUIRY` fills `struct myrb_enquiry` with drive counts, logical drive sizes, rebuild/check state, event sequence, battery presence, and dead drive locations. `MYRB_CMD_ENQUIRY2` fills `struct myrb_enquiry2` with controller model, firmware version, channel limits, memory/cache sizes, command limits, block sizes, SCSI bus capabilities, and firmware feature bits. Logical and physical discovery then use `MYRB_CMD_GET_LDEV_INFO` and `MYRB_CMD_GET_DEVICE_STATE`.

Read/write I/O uses `type4` or `type5` mailbox views depending on whether the command is direct or scatter/gather. `type5` carries the compact logical-drive transfer fields, LBA, DMA address, S/G count, and S/G type. DCDB commands use `struct myrb_dcdb` to tunnel SCSI CDBs to physical devices with DMA direction, timeout, autosense, CDB length, sense buffer, and device status.

Monitoring and management flows are represented by event, rebuild, consistency, background initialization, and error-table structures. The driver tracks `new_ev_seq` and `old_ev_seq` in `struct myrb_hba`, reads event log entries, reports rebuild/background initialization progress, and keeps flags such as `need_ldev_info`, `need_err_info`, `need_rbld`, `need_cc_status`, and `need_bgi_status` to decide which firmware queries should run in the monitor work item.

## State and Persistence Behavior

This header defines in-memory kernel state and controller firmware state, not file-backed persistence. Persistent side effects happen on the RAID controller through firmware commands: configuration writes, rebuild/control operations, background initialization, bad-data table operations, capacity expansion, firmware image updates, and device state changes.

`struct myrb_hba` owns long-lived kernel state for one adapter. It caches geometry (`ldev_block_size`, heads/sectors, stripe/segment size), feature flags (`dual_mode_interface`, `bgi_status_supported`, `safte_enabled`), mailbox ring positions, DMA allocations, command blocks, enquiry data, error tables, logical device information, and progress state. The monitor work fields and event sequence fields make controller state updates incremental across polling periods.

The packed firmware structures persist only as snapshots. For example, `struct myrb_enquiry` and `struct myrb_enquiry2` report current controller state; `struct myrb_config2` mirrors firmware configuration bytes and checksum; `struct myrb_error_entry` records counters; `struct myrb_log_entry` carries a single event. Callers must refresh these buffers from firmware when they need current state.

## Dependencies and Integration Points

`myrb.h` depends on Linux kernel types and subsystems made available by its including C file: PCI, SCSI host integration, DMA pools, completions, workqueues, delayed work, mutexes, spinlocks, MMIO accessors, and `irq_handler_t`. It integrates with the Mylex DAC960 V1 firmware via byte-exact packed command and reply structures.

Hardware integration is split by controller family. LA, PG, and PD register definitions describe doorbells, command mailbox byte registers, status registers, interrupt masks, and error status registers. The `myrb_privdata` table in implementation code can bind a PCI id to the proper register layout and initialization sequence.

SCSI integration is indirect through command blocks and logical/physical device structures. Logical drives are exposed using `struct myrb_ldev_info` and controller geometry, while physical devices and SCSI passthrough use `struct myrb_pdev_state` and `struct myrb_dcdb`.

## Risks and Edge Cases

The file relies heavily on C bitfields in `__packed` hardware ABI structures. Bitfield layout is compiler and endian sensitive, so this code assumes the kernel/compiler conventions used by the target architecture match the firmware layout. The byte comments are useful for review but are not compile-time guarantees.

Status values are reused for different command families. A generic status decoder can easily mislabel failures unless it considers the opcode or operation class. `MYRB_STATUS_CHECK_CONDITION` also overlaps with logical-drive offline status in some contexts.

Several firmware buffers contain fixed-size arrays tied to old controller limits, such as 32 logical devices, 45 physical devices, 21 dead drives, 6 channel parameters, and 32 S/G entries. Any caller must clamp firmware-reported values to these constants before indexing.

Mailbox and DMA address fields are mostly 32-bit (`u32`) in the V1 ABI. Systems with high DMA addresses require implementation-side DMA mask handling or bounce behavior that keeps firmware-visible addresses representable.

Progress reporting structures use controller block counts and fields such as `blocks_left`, `blocks_done`, and logical device size. Callers must avoid division by zero and must handle in-progress status codes that can mean valid data, failure, success, or termination depending on the query.

## Test Signals

Build coverage should catch syntax and type drift, but ABI drift needs stronger checks: inspect `sizeof()` and `offsetof()` for firmware-visible structures if this header changes. Probe tests should include LA, PG, and PD family devices or emulation paths, command/status mailbox wraparound, interrupt acknowledge paths, and reset/init timeout handling.

Functional validation should exercise enquiry/enquiry2 discovery, logical-device info refresh, physical-device state reads, event-log sequence handling, DCDB passthrough with and without autosense, S/G read/write I/O at the 32-entry limit, cache flush, rebuild and consistency-check monitoring, and error-table updates. Fault injection should cover DMA allocation failures, invalid firmware status values, mailbox timeout, and firmware-reported counts larger than the driver constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/myrs.c

## Purpose

`myrs.c` is the Linux SCSI low-level driver implementation for Mylex DAC960/AcceleRAID/eXtremeRAID controllers that use the newer DAC960 V2 SCSI-based firmware interface. It registers a PCI driver named `myrs`, initializes supported controller families, enables the firmware memory-mailbox interface, exposes RAID logical drives through the SCSI midlayer and RAID class, exposes physical devices as non-ULD-attached SCSI devices, and provides sysfs controls for RAID state, rebuild, consistency check, discovery, cache flush, and enclosure-message filtering.

The implementation is organized around firmware IOCTL mailboxes, a ring of coherent command mailboxes, a ring of coherent status mailboxes, interrupt-driven completion, and a delayed monitor worker that polls health status and controller events.

## Important APIs, Types, and Functions

Name helpers `myrs_devstate_name()` and `myrs_raid_level_name()` translate firmware enums into user-visible strings. `myrs_reset_cmd()`, `myrs_qcmd()`, and `myrs_exec_cmd()` are the core command helpers: reset a command block, copy it into the next memory mailbox, ring the controller, and optionally wait for completion.

Firmware query helpers include `myrs_get_ctlr_info()`, `myrs_get_ldev_info()`, `myrs_get_pdev_info()`, `myrs_translate_pdev()`, `myrs_get_event()`, and `myrs_get_fwstatus()`. Management helpers include `myrs_dev_op()` for controller/device operations, `myrs_enable_mmio_mbox()` for coherent mailbox setup, `myrs_get_config()` for initial controller sizing, and `myrs_log_event()` for event decoding and state update hints.

SCSI and sysfs integration is provided by `myrs_queuecommand()`, `myrs_host_reset()`, `myrs_mode_sense()`, `myrs_sdev_init()`, `myrs_sdev_configure()`, `myrs_sdev_destroy()`, and the `myrs_template` `scsi_host_template`. Per-device sysfs attributes are `raid_state`, `raid_level`, `rebuild`, and `consistency_check`. Per-host attributes are `serial`, `ctlr_num`, `processor`, `model`, `ctlr_type`, `cache_size`, `firmware`, `discovery`, `flush_cache`, and `disable_enclosure_messages`.

RAID class integration uses `myrs_is_raid()`, `myrs_get_resync()`, `myrs_get_state()`, and `myrs_raid_functions`. PCI lifecycle functions are `myrs_alloc_host()`, `myrs_detect()`, `myrs_probe()`, `myrs_remove()`, `myrs_cleanup()`, `myrs_init_module()`, and `myrs_cleanup_module()`.

Completion and monitoring functions are `myrs_handle_scsi()`, `myrs_handle_cmdblk()`, and `myrs_monitor()`. Memory/resource functions are `myrs_create_mempools()`, `myrs_destroy_mempools()`, and `myrs_unmap()`.

Hardware-specific code is split into GEM, BA, and LP blocks. Each block supplies register access helpers, mailbox initialization, hardware init, interrupt handling, and `struct myrs_privdata` records. Supported PCI ids are DAC960 GEM, BA, and LP variants.

## Control Flow

Module load attaches a RAID class template and registers the PCI driver. Probe calls `myrs_detect()`, which allocates a `Scsi_Host`, enables the PCI device, maps BAR 0 into MMIO space, selects the PCI-id-specific hardware initializer, waits for controller initialization to finish, enables the memory mailbox interface, requests the IRQ, and stores the host-private controller state.

`myrs_enable_mmio_mbox()` sets a 64-bit DMA mask with 32-bit fallback, allocates a temporary coherent mailbox, allocates coherent command and status mailbox rings, allocates the firmware health buffer, allocates host-side controller info and event buffers, fills a `MYRS_IOCTL_SET_MEM_MBOX` command, and submits it through the controller-family hardware mailbox initialization callback. The command/status rings are circular; `myrs_qcmd()` advances `next_cmd_mbox` and rings the controller when the previous mailbox slots indicate the controller needs notification.

After low-level detection, `myrs_get_config()` reads controller info, validates that old firmware 6.00-00 is rejected, fills host limits from controller data, caps queue depth to controller `max_tcq - 3` and mailbox capacity, sets `max_sectors` and `sg_tablesize`, and logs model, firmware, channel, memory, queue, and device counts. `myrs_create_mempools()` then creates DMA pools for large S/G lists, sense buffers, long CDB buffers, creates an ordered monitor workqueue, and schedules `myrs_monitor()`. Probe finally calls `scsi_add_host()` and `scsi_scan_host()`.

SCSI discovery uses `myrs_sdev_init()`. Channels below `ctlr_info->physchan_present` are physical devices; the driver allocates `struct myrs_pdev_info`, queries firmware, stores it in `sdev->hostdata`, and later prevents upper-layer driver attachment except for skipping the HBA device. Channels at or above `physchan_present` are logical drives; the driver translates channel/id to logical-drive number, queries `struct myrs_ldev_info`, stores it in `hostdata`, maps firmware RAID levels to RAID class levels, and logs non-online states. `myrs_sdev_configure()` marks logical devices as tagged-capable and sets write-cache default when firmware reports write cache enabled.

Normal I/O enters `myrs_queuecommand()`. The function rejects devices without `hostdata`, synthesizes an illegal-request response for `REPORT_LUNS`, and handles `MODE_SENSE` locally for logical drives by building caching and block-descriptor data. Other commands allocate a DMA sense buffer and, for CDBs longer than 10 bytes, a DMA DCDB buffer. Logical drives use `MYRS_CMD_OP_SCSI_10` or `MYRS_CMD_OP_SCSI_256` addressed to the firmware-provided logical backing pdev fields; physical devices use passthrough opcodes. Request tags are offset by 3 because ids 1 and 2 are reserved for direct and monitor commands. Data buffers are mapped with `scsi_dma_map()`. Up to two S/G entries fit in the mailbox; larger lists allocate an S/G DMA-pool block and set `add_sge_mem`. The command is submitted under `queue_lock`.

Interrupt handlers for GEM, BA, and LP are structurally identical after register-specific acknowledge. They walk status mailboxes while `id > 0`, map ids 1 and 2 to the direct and monitor command blocks, map other ids back to SCSI commands with `scsi_host_find_tag(host, id - 3)`, copy status, sense length, and residual into the command block, clear the status mailbox, advance the status ring, and dispatch either `myrs_handle_cmdblk()` for synchronous firmware commands or `myrs_handle_scsi()` for SCSI I/O. SCSI completion unmaps DMA, copies sense data on `MYRS_STATUS_FAILED`, frees sense/DCDB/SGL pool objects, sets residual, maps nonresponsive statuses to `DID_BAD_TARGET`, otherwise returns `DID_OK | firmware_status`, and calls `scsi_done()`.

The monitor worker first issues `GET_HEALTH_STATUS`. If `needs_update` is set, it refreshes controller info under `cinfo_mutex`. If firmware's next event sequence is ahead of `cs->next_evseq`, it fetches one event, logs it, increments the sequence, and reschedules quickly. It also refreshes every logical device when controller info reports long-running operations such as background initialization, logical/physical init, consistency check, rebuild, or expansion. If there is no new epoch, event, or urgent update, it falls back to the secondary interval.

Sysfs write paths are firmware command frontends. `raid_state_store()` accepts `offline`, `kill`, `online`, or `standby`, translates physical devices to logical devices when needed, and sends `MYRS_IOCTL_SET_DEVICE_STATE`. `rebuild_store()` starts or stops rebuild with `MYRS_IOCTL_RBLD_DEVICE_START/STOP` after checking current logical-device state. `consistency_check_store()` starts or stops consistency check with `MYRS_IOCTL_CC_START/STOP`. `discovery_store()` sends `START_DISCOVERY`, resets event sequence tracking, forces monitor work, and waits for it. `flush_cache_store()` sends `FLUSH_DEVICE_DATA`.

Remove flushes controller cache, cancels and destroys monitor/mempool resources, frees coherent mailbox and firmware buffers, disables interrupts, unmaps MMIO, frees IRQ, disables the PCI device, and drops the SCSI host. Module unload unregisters PCI and releases the RAID class template.

## State and Persistence Behavior

Persistent kernel state lives in `struct myrs_hba`, defined in `myrs.h` and filled here. It includes MMIO pointers, PCI/SCSI objects, model and firmware strings, event epoch/sequence tracking, monitor flags, workqueue, DMA pools, command/status mailbox rings, direct and monitor command blocks, firmware health buffer, controller info cache, event buffer, and mutexes.

Per-SCSI-device state is stored in `sdev->hostdata`: physical devices own a dynamically allocated `struct myrs_pdev_info`, logical drives own a dynamically allocated `struct myrs_ldev_info`. These caches are refreshed by discovery, sysfs show/store operations, event handling, and monitor updates. They are freed by `myrs_sdev_destroy()`.

The driver itself has no file-backed persistence. However, sysfs writes can change controller-persistent or disk-visible RAID state: setting devices online/offline/standby, starting or canceling rebuild, starting or canceling consistency checks, triggering discovery, and flushing controller cache. Firmware configuration and rebuild/check progress survive in the controller and arrays according to firmware behavior, not in driver-owned storage.

The coherent command/status mailbox rings and firmware health buffer persist for the life of the controller. Their DMA addresses are programmed into firmware by `SET_MEM_MBOX`; losing or freeing them before disabling the controller interface would break completion delivery.

## Dependencies and Integration Points

The file depends on Linux PCI, coherent and streaming DMA, DMA pools, interrupts, SCSI midlayer, block request tags and timeouts, RAID class, workqueues, completions, spinlocks, mutexes, sysfs attributes, unaligned access helpers, and sense-data helpers.

Firmware integration is through the DAC960 V2 mailbox ABI from `myrs.h`: IOCTL opcodes, SCSI 10/256 and passthrough opcodes, 64-byte command mailboxes, 8-byte status mailboxes, controller info, logical/physical device info, health status, and event records.

Hardware integration is controller-family-specific. GEM uses shifted 32-bit register accesses, BA and LP use byte doorbell/mask registers, and all families provide operations for hardware mailbox submission, memory-mailbox notification, interrupt masking, reset, initialization polling, error-status reading, and command-status reading.

User-space integration is mostly sysfs through SCSI host and device attributes, plus standard SCSI block devices for logical drives and RAID class state/resync reporting. Physical devices are discovered but `no_uld_attach` prevents normal upper-layer storage attachment.

## Risks and Edge Cases

`myrs_translate_pdev()` does not call `myrs_reset_cmd()` before filling the shared direct command block, unlike most other direct-command helpers. If previous direct-command mailbox fields survive and are relevant to the reused union view, this can submit stale bits. The call is protected by `dcmd_mutex`, but not by a reset.

`myrs_get_event()` uses the monitor command block without a visible `myrs_reset_cmd()` before filling the get-event mailbox. It overwrites many fields, but stale control bits or DMA fields could be a risk if previous monitor commands used a different union view.

`myrs_get_fwstatus()` sets `sgl->sge[0].sge_count = mbox->ctlr_info.dma_size` even though it filled the `common` union view. The overlapping layout likely makes this the same low 24-bit DMA size field, but it is fragile and confusing.

`myrs_cleanup()` calls `cs->disable_intr(cs)` even though the callback type expects `void __iomem *base`; the hardware helpers expect an MMIO base, not `struct myrs_hba *`. This is a strong bug signal in the visible code path.

`disable_enclosure_messages_store()` uses `to_scsi_device(dev)` even though the attribute is installed as a SCSI host attribute, while the show path uses `class_to_shost(dev)`. That mismatch is a likely sysfs store crash or invalid cast risk.

Interrupt handlers hold `queue_lock` while completing SCSI commands through `scsi_done()`. If any completion path re-enters driver locking in an unexpected way, lock-order problems are possible. Existing code may rely on SCSI midlayer expectations for low-level driver completion context.

`myrs_queuecommand()` handles `scsi_dma_map()` returning zero by falling through the multi-SG path with `nsge == 0`, leaving no S/G entries but still submitting a command with nonzero `dma_size` if `scsi_bufflen()` was nonzero. Negative mapping errors also fall into the same path because only `nsge == 1` and `nsge > 2` are special-cased. This needs careful review against SCSI DMA API semantics.

Timeout conversion stores `rq->timeout` directly in firmware seconds/minutes fields, but Linux request timeouts are normally in jiffies. If this code expects seconds, command timeout programming may be wrong unless the surrounding API changed or normalizes the field.

The driver caps queue depth by reserving ids 1 and 2, then uses `rq->tag + 3`. Correctness depends on all SCSI requests having valid tags below the configured queue depth and on no firmware completion returning id 0 for a real command.

Probe error handling is staged but split across `myrs_detect()`, `myrs_get_config()`, `myrs_create_mempools()`, and `scsi_add_host()`. Fault-injection testing should confirm every partial allocation path releases coherent memory, IRQ, MMIO, workqueue, and DMA pools exactly once.

## Test Signals

Build tests should include this driver and `myrs.h` with warnings enabled. Static analysis should flag the callback argument mismatch in `myrs_cleanup()`, the host/sysfs cast mismatch in `disable_enclosure_messages_store()`, direct-command mailbox reset inconsistencies, and DMA-map return handling in `myrs_queuecommand()`.

Probe validation should cover GEM, BA, and LP hardware paths; DMA mask fallback from 64-bit to 32-bit; mailbox enable failure; firmware initialization timeout; firmware 6.00-00 rejection; and IRQ request failure. Runtime I/O tests should cover logical-drive reads/writes with no data, one S/G entry, two inline S/G entries, and more-than-two S/G entries requiring `sg_pool`.

SCSI behavior tests should cover local `REPORT_LUNS` rejection, logical-drive `MODE_SENSE` with and without block descriptors, write-cache reporting, FUA propagation, long CDB allocation via `dcdb_pool`, residual reporting, sense copying on firmware failure, nonresponsive-device status mapping, and host reset.

Management tests should exercise all sysfs attributes: state changes for physical and logical devices, rebuild start/stop, consistency check start/stop, discovery, cache flush, enclosure-message filtering, RAID class state/resync, and show paths after device removal. Monitor tests should inject health status changes, event sequence increments, logical-drive state transitions, enclosure events, sense events, and long-running operation progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/myrs.h

## Purpose

`myrs.h` is the private ABI and controller-state header for the Mylex DAC960 V2 SCSI-interface driver implemented by `myrs.c`. It defines firmware opcodes, IOCTL opcodes, status codes, packed controller reply/request structures, 64-byte command mailbox overlays, status mailbox format, per-command and per-controller driver state, callback typedefs, and register definitions for GEM, BA, and LP controller families.

Like `myrb.h`, this header is firmware-facing. Most structures include byte comments and `__packed` annotations because they are copied to or from controller DMA buffers and MMIO mailboxes.

## Important APIs, Types, and Functions

Top-level constants include `MYRS_MAILBOX_TIMEOUT`, reserved command ids `MYRS_DCMD_TAG` and `MYRS_MCMD_TAG`, line buffer size, monitor intervals, `MYRS_SG_LIMIT`, memory mailbox counts, `MYRS_DCDB_SIZE`, and `MYRS_SENSE_SIZE`. `MYRS_MAX_CMD_MBOX` and `MYRS_MAX_STAT_MBOX` size the coherent command and status rings used by the implementation.

`enum myrs_cmd_opcode` defines firmware command classes: memory copy, SCSI 10-byte passthrough, SCSI 255/256-byte passthrough, logical SCSI 10, logical SCSI 256, and IOCTL. `enum myrs_ioctl_opcode` defines controller management operations such as get controller/logical/physical info, get health status, get event, discovery, set device state, initialization control, rebuild control, consistency check, memory mailbox setup, reset, flush, pause, locate, configuration changes, physical-to-logical translation, and clear configuration. `MYRS_STATUS_*` constants are one-byte completion statuses.

Controller/device information structures are `struct myrs_ctlr_info`, `struct myrs_ldev_info`, `struct myrs_pdev_info`, `struct myrs_fwstat`, and `struct myrs_event`. They provide controller model/firmware/hardware/cache/memory/CPU/error/long-operation counts, logical-drive state and progress LBAs, physical-device state and counters, health/event sequence information, and individual event records.

Firmware identity and addressing types include `enum myrs_devstate`, `enum myrs_raid_level`, `enum myrs_stripe_size`, `enum myrs_cacheline_size`, `struct myrs_pdev`, `struct myrs_ldev`, `enum myrs_opdev`, and `struct myrs_devmap`. Transfer types include `struct myrs_cmd_ctrl`, `struct myrs_cmd_tmo`, `struct myrs_sge`, and `union myrs_sgl`.

`union myrs_cmd_mbox` is the central 64-byte firmware command layout. It has views for `common`, `SCSI_10`, `SCSI_255`, `ctlr_info`, `ldev_info`, `pdev_info`, `get_event`, `set_devstate`, `cc`, `set_mbox`, and `dev_op`. `struct myrs_stat_mbox` is the completion record carrying id, firmware status, sense length, and residual.

Driver runtime types are `struct myrs_cmdblk` and `struct myrs_hba`. `myrs_cmdblk` stores a mailbox plus completion status, autosense metadata, residual, completion pointer, optional S/G pool block, optional long CDB buffer, and sense buffer. `myrs_hba` stores MMIO/PCI/SCSI state, model/firmware strings, health/event tracking, monitor flags, workqueue, locks, DMA pools, hardware callbacks, mailbox rings, command blocks, firmware health/controller/event buffers, and mutexes.

The inline helper `dma_addr_writeql()` writes a `dma_addr_t` to two adjacent 32-bit MMIO registers for controllers that accept 64-bit DMA addresses as two dwords.

## Control Flow

The structures in this header support the `myrs.c` probe and I/O flow. During probe, implementation code allocates `struct myrs_hba`, maps controller registers, chooses a `struct myrs_privdata` entry, allocates command/status mailboxes sized by this header, fills a `set_mbox` mailbox with the ring DMA addresses and health buffer DMA address, and submits it through a family-specific hardware mailbox init function.

Direct and monitor commands use `struct myrs_cmdblk` instances embedded in `myrs_hba`. The implementation fills one of the IOCTL mailbox views, points `union myrs_sgl` at a DMA buffer for firmware output, submits it, and waits for a `struct myrs_stat_mbox` completion. Normal SCSI I/O uses per-request `struct myrs_cmdblk` storage from `scsi_cmd_priv()`, fills `SCSI_10` or `SCSI_255`, maps data S/Gs into `union myrs_sgl`, and receives status through the same status ring.

Controller state queries fill `struct myrs_ctlr_info`, which then drives SCSI host limits: physical/virtual channel counts, target counts, queue depth, maximum transfer size, and S/G table size. Logical and physical discovery fill `struct myrs_ldev_info` and `struct myrs_pdev_info` and store those records as per-device hostdata.

Monitoring uses `struct myrs_fwstat` to detect epoch and event sequence changes. `struct myrs_event` records are fetched by event number and decoded by implementation code. Long-running operation fields in `myrs_ctlr_info`, `myrs_ldev_info`, and `myrs_pdev_info` drive progress reporting for rebuild, background initialization, foreground initialization, migration, patrol, and consistency check.

The GEM, BA, and LP register sections provide the constants used by the family-specific init and interrupt handlers. Each family defines inbound doorbell bits, outbound doorbell/status bits, interrupt mask bits, error status bits, and register offsets. `struct myrs_privdata` binds those offsets and helper functions to a PCI id.

## State and Persistence Behavior

This header defines volatile kernel state and firmware DMA layouts. `struct myrs_hba` fields persist for the life of a probed controller: coherent mailbox rings, firmware health buffer, cached controller information, event buffer, monitor scheduling state, and DMA pools. `struct myrs_cmdblk` state persists only for an active command, except the embedded direct and monitor command blocks that are reused serially.

`struct myrs_ctlr_info` is a cached snapshot of controller firmware state. It includes many counters and long-duration activity fields, but those values are authoritative only when freshly read from firmware. `struct myrs_ldev_info` and `struct myrs_pdev_info` snapshots are similarly used as cached per-device state and refreshed by monitor/sysfs paths.

The header exposes firmware operations that can affect persistent controller or array state, including configuration create/delete/clear/add, device state changes, rebuild, initialization, consistency check, device reset, flush, pause, locate, and physical-to-logical translation. The persistence is owned by the controller firmware and disks, not by files in the host filesystem.

The command/status mailbox rings and health buffer are coherent DMA objects whose addresses are stored by firmware after `MYRS_IOCTL_SET_MEM_MBOX`. Their lifetime and alignment are critical: firmware can DMA completions and health data into them asynchronously while the driver is active.

## Dependencies and Integration Points

The header depends on kernel integer types, DMA address types, SCSI host types, PCI types, workqueue types, locks, completions, MMIO accessors, and `irq_handler_t` through its inclusion context. It is tightly integrated with Linux SCSI midlayer request-private command storage and with the RAID class through fields consumed by `myrs.c`.

Firmware integration is the DAC960 V2 SCSI-interface command ABI. `union myrs_cmd_mbox`, `union myrs_sgl`, `struct myrs_stat_mbox`, and the controller/device/event structures are shared with the controller via DMA or hardware mailbox submission.

Hardware integration is defined by the GEM, BA, and LP register constants. The implementation writes doorbells, command mailbox addresses, interrupt masks, status acknowledgments, and reset bits using these offsets. `dma_addr_writeql()` bridges Linux `dma_addr_t` values to the controller's two-register 64-bit address programming model.

## Risks and Edge Cases

The many packed bitfield structures are ABI-sensitive. Bitfield order, enum size, packing, and endianness must remain compatible with the controller firmware. Any compiler or architecture change that alters these assumptions can corrupt mailbox or reply interpretation.

`union myrs_cmd_mbox` overlays fields with different declared widths, including 24-bit bitfields for DMA size in IOCTL views and full 32-bit `dma_size` in SCSI views. Implementation code must fill the union view matching the opcode; reading a field through another view is fragile even when the current layout overlaps.

`MYRS_SENSE_SIZE` is 14 bytes, smaller than the generic SCSI sense buffer. The driver copies only firmware-reported sense length up to `SCSI_SENSE_BUFFERSIZE`, but the allocated firmware autosense area is fixed by this header. Commands needing larger autosense data may lose detail.

The firmware mailbox counts and S/G limits are fixed constants. The implementation caps host limits against these values, but any new hardware reporting higher queue depth or S/G capacity cannot use it without changing the ABI handling and pool sizing.

`struct myrs_pdev_info` reserves a large trailing area, and `myrs.c` reuses part of `rsvd13` as a `struct myrs_devmap` scratch area in one path. That is space-efficient but fragile because it treats reserved firmware output bytes as host-owned temporary storage.

Register definitions differ subtly between GEM, BA, and LP. For example, "mailbox full" and "initialization in progress" bits have inverted meanings in some families. Family-specific helper code must use the matching constants exactly.

## Test Signals

Compile-time validation should include `sizeof()` and `offsetof()` checks for firmware-visible structures if this header is edited, especially `struct myrs_ctlr_info`, `struct myrs_ldev_info`, `struct myrs_pdev_info`, `union myrs_cmd_mbox`, and `struct myrs_stat_mbox`. Sparse or static-analysis runs should inspect packed bitfields and union aliasing.

Runtime validation should confirm that `SET_MEM_MBOX` programs command/status rings correctly, status mailbox completion ids map to direct, monitor, and SCSI request command blocks, and health/event buffers update through DMA. Discovery tests should verify controller info sizing, physical and logical device info parsing, RAID level mapping, and physical-to-logical translation.

Hardware-family tests should exercise GEM, BA, and LP register paths for init polling, error-status reads, mailbox submission, interrupt masking/unmasking, status acknowledgment, and reset. Fault-injection tests should cover DMA allocation failures, mailbox timeout, invalid status ids, and firmware-reported limits exceeding `MYRS_MAX_CMD_MBOX`, `MYRS_MAX_STAT_MBOX`, or `MYRS_SG_LIMIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/myrs.h -->
