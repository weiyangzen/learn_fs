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
