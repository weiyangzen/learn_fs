# sources/distributed-fs/ceph-client/drivers/scsi/hpsa.c lines 1-9315

## Purpose

This chunk is the main Linux SCSI low-level driver for HP/Microchip Smart Array SAS RAID and HBA controllers. It registers the `hpsa` PCI driver, exposes Smart Array logical volumes and HBA-mode physical disks to the SCSI midlayer, supports legacy `cciss`-style passthrough ioctls, manages controller reset and kdump recovery, and implements both normal CISS command submission and HP SSD Smart Path I/O accelerator paths.

The code is hardware-facing and stateful. It maps PCI BARs and controller configuration tables, negotiates simple versus performant transport modes, allocates DMA command/error/reply pools, submits SCSI commands through controller doorbell/register queues, processes interrupt completions, discovers and reconciles devices, and runs periodic work to detect controller lockups and configuration changes.

## Important APIs, Types, and Entry Points

- Module and PCI integration: `hpsa_pci_device_id`, `products`, `hpsa_pci_driver`, `hpsa_init_one()`, `hpsa_remove_one()`, `hpsa_shutdown()`, `hpsa_suspend()`, `hpsa_resume()`. The driver aliases `cciss` and supports a `hpsa_simple_mode` module parameter.
- SCSI host integration: `hpsa_driver_template` wires `.queuecommand`, `.scan_start`, `.scan_finished`, `.change_queue_depth`, `.eh_device_reset_handler`, `.ioctl`, `.compat_ioctl`, `.sdev_init`, `.sdev_configure`, and `.sdev_destroy`.
- Controller state: `struct ctlr_info` from `hpsa.h` stores PCI device, mapped BAR/config tables, access method callbacks, command pools, reply queues, locks, workqueues, per-controller device table `h->dev[]`, transport mode bits, firmware support, lockup state, passthrough throttling, and discovery state.
- Device state: `struct hpsa_scsi_dev_t` stores OS bus/target/lun, firmware `scsi3addr`, inquiry identity, SAS/enclosure/path data, logical volume status, queue depth, `commands_outstanding`, reset/removal flags, RAID map/offload flags, HBA ioaccel handle, and logical-to-physical disk pointers.
- Command state: `struct CommandList` and `struct ErrorInfo` from `hpsa_cmd.h` represent CISS commands, DMA error descriptors, SCSI command ownership, command type, refcount, waiting completion, logical device pointer, and physical disk used for ioaccel.
- Sysfs attributes: per-device `raid_level`, `lunid`, `unique_id`, `hp_ssd_smart_path_enabled`, `path_info`, `sas_address`; per-host `rescan`, `firmware_revision`, `commands_outstanding`, `transport_mode`, `resettable`, `hp_ssd_smart_path_status`, `raid_offload_debug`, `lockup_detected`, `ctlr_num`, `legacy_board`.
- Command submission paths: `hpsa_scsi_queue_command()`, `cmd_tagged_alloc()`, `hpsa_ioaccel_submit()`, `hpsa_scsi_ioaccel_raid_map()`, `hpsa_scsi_ioaccel_direct_map()`, `hpsa_ciss_submit()`, `enqueue_cmd_and_start_io()`.
- Completion and error paths: `do_hpsa_intr_intx()`, `do_hpsa_intr_msi()`, `next_command()`, `process_indexed_cmd()`, `finish_cmd()`, `complete_scsi_command()`, `process_ioaccel2_completion()`, `handle_ioaccel_mode2_error()`, `hpsa_command_resubmit_worker()`.
- Discovery and reconciliation: `hpsa_update_scsi_devices()`, `hpsa_gather_lun_info()`, `hpsa_update_device_info()`, `adjust_hpsa_scsi_table()`, `hpsa_add_device()`, `hpsa_remove_device()`, `hpsa_add_sas_host()`, `hpsa_add_sas_device()` declarations are present here, with SAS bodies after the requested chunk.
- Reset and health: `hpsa_eh_device_reset_handler()`, `hpsa_do_reset()`, `wait_for_device_to_become_ready()`, `hpsa_init_reset_devices()`, `hpsa_kdump_hard_reset_controller()`, `hpsa_kdump_soft_reset()`, `detect_controller_lockup()`, `controller_lockup_detected()`, `fail_all_outstanding_cmds()`.
- Passthrough ioctl support: `hpsa_ioctl()`, `hpsa_passthru_ioctl()`, `hpsa_big_passthru_ioctl()`, 32-bit compat wrappers, and `fill_cmd()` for constructing internal CISS/BMIC/reset commands.

## Control Flow

Probe starts in `hpsa_init_one()`. It looks up the board ID, optionally performs a kdump/reset-devices hard reset, allocates `ctlr_info`, initializes locks, allocates per-CPU lockup flags, initializes PCI resources via `hpsa_pci_init()`, allocates a SCSI host, configures DMA masks, disables interrupts, requests IRQs, allocates command pools and SG chain blocks, enters performant mode, creates ordered workqueues, handles an optional soft reset retry path, enables interrupts, runs HBA inquiry, adds the SCSI host, and schedules monitor/rescan/event work.

PCI initialization maps the controller BAR and CISS config/transfer tables, writes the driver version into firmware-visible config space, reads controller limits, verifies the CISS signature, sets driver support bits, applies P600 prefetch quirks, and first enters simple mode. Later `hpsa_put_ctlr_into_performant_mode()` and the beginning of `hpsa_enter_performant_mode()` set up reply queues and block-fetch tables, program transport request bits, and switch access-method callbacks for performant/ioaccel modes.

SCSI queueing begins at `hpsa_scsi_queue_command()`. It rejects missing, removed, locked-up, or resetting devices, allocates a command by block-layer tag, and prefers ioaccel for non-passthrough first attempts when Smart Path is enabled. Logical-volume ioaccel uses `hpsa_scsi_ioaccel_raid_map()` to map eligible single-stripe reads, RAID0 writes, and selected RAID1/ADM/5/6 reads to a physical disk command. HBA-mode ioaccel uses the device handle directly. Ineligible or retry commands fall back to `hpsa_ciss_submit()`, which fills the normal CISS command, maps SGs, and posts it.

Completion is interrupt-driven. INTx and MSI/MSI-X handlers retrieve raw tags, convert direct-lookup tags into `CommandList` indexes, and call `finish_cmd()`. SCSI commands flow to `complete_scsi_command()`, which unmaps DMA, handles device removal and lockup sentinel status, decodes CISS or ioaccel errors, copies sense data, sets SCSI results, retries ioaccel failures through `hpsa_command_resubmit_worker()` when appropriate, and finally frees command references and calls `scsi_done()`. Internal commands and ioaccel TMFs complete a stack `completion`.

Discovery is triggered by SCSI scanning, sysfs `rescan`, ioctls that register/deregister disks, event monitor work, discovery polling, and offline-device polling. `hpsa_update_scsi_devices()` performs REPORT PHYSICAL LUNS and REPORT LOGICAL LUNS, identifies local logical counts, checks external controllers, allocates candidate device records, gathers inquiry/VPD/BMIC/SAS/path/RAID-map data, filters masked spares, and calls `adjust_hpsa_scsi_table()`. That function compares the new candidate list with `h->dev[]`, updates minor attributes in place, replaces changed entries, removes missing entries, adds new entries, rebuilds logical-volume physical-disk pointers, then notifies the SCSI/SAS layers outside the device-table lock.

Reset and lockup paths deliberately block or fail I/O. `hpsa_eh_device_reset_handler()` marks controller reset in progress, blocks new I/O to the target device with `dev->in_reset`, sends either logical LUN reset or physical target reset, waits for outstanding device commands to drain, then waits for TUR readiness. `detect_controller_lockup()` samples interrupt and heartbeat timestamps; on failure `controller_lockup_detected()` masks interrupts, records the scratchpad lockup code per CPU, may request a firmware checkpoint, disables PCI, and completes all outstanding commands with `CMD_CTLR_LOCKUP`.

## State and Persistence Behavior

Persistent driver state is in memory plus firmware-visible controller tables, not on disk. `h->cfgtable` and `h->transtable` are MMIO mappings into controller state; writes to transport request, block-fetch registers, reply queue addresses, event-clear registers, driver support bits, and diagnostic options change controller behavior until reset or driver teardown.

The authoritative runtime device table is `h->dev[]` protected by `h->devlock`. Candidate device lists are rebuilt on each scan, then reconciled into this table. `sdev->hostdata` points back to entries in `h->dev[]`; removal sets `removed`/`was_removed` and waits for outstanding commands before notifying SCSI or SAS transport.

Command allocation has two domains. Tagged SCSI commands use block request tags offset above `HPSA_NRESERVED_CMDS`. Driver-internal commands use a reserved bitmap region and busy-wait until a reserved command becomes available. Both use `CommandList.refcount` to guard lifetime, with `SCSI_CMD_IDLE` and `SCSI_CMD_BUSY` sentinel pointers marking ownership state.

I/O accelerator state is intentionally conservative. Logical-volume offload is only enabled after a scan has refreshed the RAID map and rebuilt `phys_disk[]`. Event handling may immediately turn off offload, block SCSI requests, drain accelerated commands, acknowledge firmware events, and rely on a later rescan to re-enable offload with fresh mapping data.

Controller health is stored in per-CPU `h->lockup_detected`, heartbeat timestamps, and outstanding-command counters. Firmware flash commands temporarily lengthen the heartbeat sample interval to avoid false lockup detection.

## Dependencies and Integration Points

- Linux PCI core: device matching, BAR/resource management, IRQ vector allocation, DMA masks, power-state resets, `pci_set_drvdata()`, and shutdown/remove callbacks.
- Linux SCSI midlayer: `Scsi_Host`, queuecommand, device configuration/destruction, error handling, scanning, queue depth, request tags, SG mapping, result/sense handling, and block request timeouts.
- SAS transport: the host template attaches `hpsa_sas_transport_template`, and physical devices are exposed through SAS host/device helpers rather than plain `scsi_add_device()`.
- CISS/Smart Array firmware ABI: CISS command lists, BMIC commands, REPORT LUNS formats, VPD pages, config table fields, doorbell bits, reply queues, transport mode bits, and ioaccel command formats.
- Userspace ABI: legacy `cciss` ioctl numbers, 32-bit compat passthrough structs, sysfs host/device attributes, and kernel logs that identify device discovery/removal/reset/offload state.
- Workqueues and timing: ordered controller-specific workqueues handle rescan, resubmit, and monitoring; delayed work uses heartbeat and event intervals.

## Risks and Edge Cases

- Hardware ABI correctness is critical. `BUILD_BUG_ON()` layout checks and exact DMA/block-fetch programming indicate that structure size, alignment, endian conversion, and tag encoding mistakes can corrupt controller communication.
- `cmd_alloc()` spins indefinitely while searching reserved internal commands. It assumes reserved commands will eventually be freed; a leak or stuck internal command can hang the caller.
- Locking is subtle. `h->lock`, `h->devlock`, `scan_lock`, `reset_lock`, `offline_device_lock`, per-command refcounts, and waitqueues coordinate interrupt completions, scans, resets, remove paths, and sysfs reads. Several comments call out assumptions and FIXME lock questions in ioaccel command/device matching.
- Device reconciliation must not enable ioaccel against stale RAID maps or stale physical disk pointers. The code updates offload flags in a staged order and uses memory barriers around `ioaccel_handle` before `hba_ioaccel_enabled`.
- Discovery can be expensive or disruptive. Spare disks may be skipped to avoid spinning them up, external controllers disable report-lun-data caching and may enable polling, and offline logical volumes are withheld from the SCSI midlayer until ready.
- Reset and removal can race with I/O. The driver uses `dev->in_reset`, `reset_in_progress`, `remove_in_progress`, SCSI request blocking, and outstanding-command waits, but teardown ordering is constrained because `scsi_remove_host()` may issue cache flushes.
- Lockup detection intentionally fails all outstanding commands and disables PCI, so false positives are severe. Firmware flashing lengthens heartbeat sampling as mitigation.
- Passthrough ioctls accept user-provided CDBs and buffers behind `CAP_SYS_RAWIO`, throttle concurrency, and use bidirectional DMA. Size checks prevent obvious over-allocation, but these paths remain high-risk compatibility ABI.
- The requested chunk ends inside `hpsa_enter_performant_mode()`. The follow-on lines after 9315 finish ioaccel2 block-fetch register setup, allocation/free helpers, drain logic, and SAS transport bodies; this document summarizes only behavior visible through line 9315 while noting continuations where relevant.

## Test Signals

- Build signals: compile with common SCSI, PCI, SAS transport, compat ioctl, and DMA APIs enabled; `BUILD_BUG_ON()` assertions catch command layout drift.
- Probe/init logs: driver banner, board ID/product selection, legacy-board warning, CISS signature validation, transport mode transition, IRQ allocation names, and SCSI host scan success.
- Sysfs signals: host `transport_mode`, `commands_outstanding`, `lockup_detected`, `resettable`, `firmware_revision`, `hp_ssd_smart_path_status`; device `raid_level`, `lunid`, `unique_id`, `path_info`, `sas_address`, and `hp_ssd_smart_path_enabled`.
- I/O signals: normal CISS read/write completion, ioaccel eligible and ineligible paths, ioaccel retry fallback to CISS on disabled/busy/error statuses, correct residual and sense propagation, and queue-depth enforcement for physical disks.
- Discovery signals: REPORT LUNS changes add/remove/replace devices, masked/spare devices are skipped, offline logical volumes stay hidden and later rescan when ready, external controller detection enables discovery polling and disables RLD caching.
- Error-handling signals: logical and physical reset success/failure, TUR wait behavior, SCSI midlayer reset return values, device removal while commands are outstanding, and no new I/O accepted during reset.
- Health signals: periodic heartbeat monitoring does not fire under normal interrupt activity; simulated stalled heartbeat sets `lockup_detected`, masks interrupts, disables PCI, and completes outstanding commands as `DID_NO_CONNECT`.
- Userspace ABI signals: `CCISS_GETPCIINFO`, `CCISS_GETDRIVVER`, `CCISS_PASSTHRU`, `CCISS_BIG_PASSTHRU`, and 32-bit compat variants enforce permissions, copy error info back, throttle passthrough concurrency, and trigger rescans for legacy register/deregister commands.
