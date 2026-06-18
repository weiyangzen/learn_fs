# Research: sources/distributed-fs/ceph-client/drivers/scsi/hpsa.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005265`: lines 1-9315, `Docs/researches/chunks/subset-b-005265_research.md`
- `subset-b-005266`: lines 9316-10006, `Docs/researches/chunks/subset-b-005266_research.md`

## Chunk Research

### subset-b-005265: lines 1-9315

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

### subset-b-005266: lines 9316-10006

# sources/distributed-fs/ceph-client/drivers/scsi/hpsa.c lines 9316-10006

## Scope

This chunk covers the final part of the `hpsa` Smart Array SCSI driver. It begins inside the I/O accelerator mode 2 setup tail of `hpsa_enter_performant_mode()`, then defines performant-mode allocation/free helpers, drains outstanding accelerated commands, builds the driver's SAS transport objects, registers SAS transport callbacks, registers/unregisters the PCI driver at module load/unload, and ends with compile-time layout checks for firmware-visible RAID map and ioaccel command structures.

The chunk is not a complete driver by itself. It depends on earlier probe, interrupt, queuecommand, completion, command-pool, SG-chain, controller-configuration, and SCSI discovery code in `hpsa.c`, plus structure definitions in `hpsa.h` and `hpsa_cmd.h`.

## Purpose

The code has three main jobs:

- Finish transitioning a controller into high-throughput "performant" transport, optionally with ioaccel mode 1 or mode 2 direct I/O acceleration.
- Publish controller and physical HBA devices through the Linux SAS transport class so non-RAID physical devices have `sas_port`, `sas_phy`, and `sas_rphy` objects visible to the SCSI/SAS infrastructure.
- Attach the driver to kernel module lifecycle and protect firmware-visible structure layouts with `BUILD_BUG_ON()` offset checks.

The performant-mode section allocates host memory that the controller DMA engine directly consumes: reply queues, block-fetch tables, ioaccel command pools, and ioaccel2 SG chain blocks. The SAS section creates Linux device-model wrappers around controller/device SAS addresses rather than issuing real PHY control commands; most transport operations are stubs or informational.

## Important APIs, Types, and Functions

### Performant and ioaccel resources

- `hpsa_free_ioaccel1_cmd_and_bft()` releases the mode 1 coherent `io_accel1_cmd` pool and its heap block-fetch table, then nulls `h->ioaccel_cmd_pool`, `h->ioaccel_cmd_pool_dhandle`, and `h->ioaccel1_blockFetchTable`.
- `hpsa_alloc_ioaccel1_cmd_and_bft()` reads `cfgtable->io_accel_max_embedded_sg_count`, caps it to `IOACCEL1_MAXSGENTRIES`, asserts `struct io_accel1_cmd` alignment, allocates one coherent command frame per controller command slot, allocates the mode 1 BFT, zeros the command pool, and unwinds through the matching free helper on failure.
- `hpsa_free_ioaccel2_cmd_and_bft()` first releases ioaccel2 SG chain blocks through `hpsa_free_ioaccel2_sg_chain_blocks()`, then releases the coherent `io_accel2_cmd` pool and heap BFT.
- `hpsa_alloc_ioaccel2_cmd_and_bft()` mirrors the mode 1 path with `IOACCEL2_MAXSGENTRIES`, `struct io_accel2_cmd`, and an additional `hpsa_allocate_ioaccel2_sg_chain_blocks()` call for chained S/G support.
- `hpsa_free_performant_mode()` is the aggregate cleanup routine for allocations owned by `hpsa_put_ctlr_into_performant_mode()`: regular performant BFT, reply queues, ioaccel1 resources, and ioaccel2 resources.
- `hpsa_put_ctlr_into_performant_mode()` checks the `hpsa_simple_mode` module parameter and controller `TransportSupport`, allocates ioaccel resources if supported, sizes reply queues from MSI-X vector count and `h->max_commands`, allocates each coherent reply queue, allocates the regular BFT, and calls `hpsa_enter_performant_mode()`.
- `is_accelerated_cmd()` tests `CommandList::cmd_type` for `CMD_IOACCEL1` or `CMD_IOACCEL2`.
- `hpsa_drain_accel_commands()` scans all command slots, temporarily increments each command refcount to test allocation state, counts allocated accelerated commands, frees the temporary reference with `cmd_free()`, and sleeps in 100 ms intervals until no ioaccel commands remain outstanding.

The line-range entry starts after mode 2 BFT programming has computed `bft2_offset`, asserted `CfgTable::io_accel_request_size_offset` at `0xb8`, mapped the controller BFT register window with `remap_pci_mem()`, written all `bft2` entries with `writel()`, rang `SA5_DOORBELL`, and waited for `hpsa_wait_for_mode_change_ack()`.

### SAS transport objects

- `struct hpsa_sas_node`, `struct hpsa_sas_port`, and `struct hpsa_sas_phy` are driver-private wrappers defined in `hpsa.h`. A node owns a list of ports, a port owns a SAS address, optional `sas_rphy`, and a list of phys, and a phy tracks whether it has been added to the SAS port list.
- `hpsa_alloc_sas_node()` allocates a node, stores the parent device, and initializes `port_list_head`.
- `hpsa_free_sas_node()` walks all ports on the node with `list_for_each_entry_safe()` and frees them before freeing the node.
- `hpsa_alloc_sas_port()` allocates a driver port, creates a kernel `sas_port` with `sas_port_alloc_num()`, adds it with `sas_port_add()`, stores the SAS address, initializes the phy list, and links the port into the parent node.
- `hpsa_free_sas_port()` frees every child phy, deletes the kernel `sas_port`, removes the driver port from the node list, and frees it.
- `hpsa_alloc_sas_phy()` allocates a driver phy, creates a kernel `sas_phy` with the port's next phy index, increments `next_phy_index`, and links the driver phy to its parent port.
- `hpsa_free_sas_phy()` removes the phy from the `sas_port`, optionally removes it from the driver's list if it had been added, deletes the kernel `sas_phy`, and frees the wrapper.
- `hpsa_sas_port_add_phy()` initializes `sas_phy::identify` using the parent port SAS address, marks both initiator and target protocols as `SAS_PROTOCOL_STP`, sets link rates to unknown, calls `sas_phy_add()`, attaches the phy to the port with `sas_port_add_phy()`, links the driver wrapper into `phy_list_head`, and marks it added.
- `hpsa_sas_port_add_rphy()` fills `sas_rphy::identify` with the port SAS address and STP protocol flags, then registers it with `sas_rphy_add()`.
- `hpsa_add_sas_host()` builds the controller's root SAS node under `h->scsi_host->shost_dev`, adds one port for `h->sas_address`, adds one phy to that port, and stores the node in `h->sas_host`.
- `hpsa_delete_sas_host()` frees `h->sas_host`.
- `hpsa_add_sas_device()` creates a SAS port for a physical device's `device->sas_address`, allocates a SAS end device rphy with `sas_end_device_alloc()`, stores bidirectional links between `device` and port, and registers the rphy.
- `hpsa_remove_sas_device()` frees `device->sas_port` and clears the device pointer.
- `hpsa_find_device_by_sas_rphy()` linearly searches `h->dev[0..h->ndevices)` for a device whose `sas_port->rphy` matches a SAS transport query.

### SAS transport callbacks and module registration

- `hpsa_sas_get_enclosure_identifier()` maps from `sas_rphy` to `Scsi_Host` using `phy_to_shost()`, maps the host to `ctlr_info` with `shost_to_hba()`, finds the matching `hpsa_scsi_dev_t`, and returns `sd->eli`.
- `hpsa_sas_get_linkerrors()`, `hpsa_sas_phy_reset()`, `hpsa_sas_phy_enable()`, and `hpsa_sas_phy_setup()` are success stubs.
- `hpsa_sas_get_bay_identifier()` and `hpsa_sas_phy_speed()` return unsupported errors (`-ENXIO` and `-EINVAL`).
- `hpsa_sas_phy_release()` is an empty release callback.
- `hpsa_sas_transport_functions` is the `sas_function_template` used by `sas_attach_transport()`.
- `hpsa_init()` attaches the SAS transport template first and then registers `hpsa_pci_driver`. If PCI registration fails, it releases the SAS transport template.
- `hpsa_cleanup()` unregisters the PCI driver and releases the SAS transport template.
- `module_init(hpsa_init)` and `module_exit(hpsa_cleanup)` are the driver's module lifecycle hooks.

### Compile-time hardware ABI checks

- `verify_offsets()` is marked unused but contains `BUILD_BUG_ON(offsetof(...))` checks. Because `BUILD_BUG_ON()` is compile-time, the function protects structure layout without needing runtime calls.
- Checked structures are `struct raid_map_data`, `struct io_accel2_cmd`, and `struct io_accel1_cmd`.
- The verified offsets correspond to controller/firmware-visible DMA layouts used by RAID offload and ioaccel command submission paths. For example, `io_accel2_cmd::sg` must start at byte 64, and `io_accel1_cmd::SG` must start at `0x78 + 8`.

## Control Flow

During PCI probe, earlier `hpsa_init_one()` allocates base controller state, maps PCI/config tables, creates a `Scsi_Host`, requests interrupts, allocates the regular command pool and SG chain blocks, then calls `hpsa_put_ctlr_into_performant_mode()`.

`hpsa_put_ctlr_into_performant_mode()` exits without action when the `hpsa_simple_mode` parameter is set or the controller does not advertise `PERFORMANT_MODE`. If the controller advertises ioaccel mode 1, it allocates the mode 1 command pool and BFT; otherwise, if it advertises ioaccel mode 2, it allocates the mode 2 command pool, BFT, and ioaccel2 chain blocks. The code prefers mode 1 when both flags appear because the mode 1 branch is tested first.

After ioaccel-specific allocation, it sets `h->nreply_queues` from MSI-X vector count, defaulting to one queue without MSI-X. It calls `hpsa_get_max_perf_mode_cmds()` to refresh command limits, sets `h->reply_queue_size = h->max_commands * sizeof(u64)`, and allocates one coherent ring per reply queue. Each ring is initialized with `size = h->max_commands`, `wraparound = 1`, and `current_entry = 0`. It then allocates a regular performant block-fetch table sized for `SG_ENTRIES_IN_CMD + 1` entries and calls `hpsa_enter_performant_mode()`, whose earlier body writes controller config-table state, reply queue addresses, BFT contents, access method changes, and ioaccel setup.

Error handling is staged. Failure before the regular BFT goes to `clean1`, freeing reply queues and both ioaccel resource families. Failure after BFT allocation goes to `clean2`, additionally freeing `h->blockFetchTable`. On success, long-lived cleanup is delegated to `hpsa_free_performant_mode()`, which is called by probe error paths, kdump soft-reset unwind, and driver remove.

Accelerated command drain is independent of allocation. `hpsa_drain_accel_commands()` loops over the command pool until no allocated command has an ioaccel command type. The refcount bump lets the routine safely distinguish free versus allocated command slots using the same command-lifetime primitive as normal command allocation. Each loop iteration releases the artificial reference with `cmd_free()` and sleeps before retrying if any accelerated command was seen.

SAS host creation is triggered by the discovery/update path. Earlier `hpsa_update_scsi_devices()` creates the controller-level SAS host when `h->sas_host == NULL` by calling `hpsa_add_sas_host()`. Physical HBA devices are added through `hpsa_add_device()`, which calls `hpsa_add_sas_device(h->sas_host, device)` for non-logical devices. Logical RAID devices instead go through `scsi_add_device()`.

SAS removal mirrors discovery. Physical device removal calls `hpsa_remove_sas_device()`. Controller removal calls `hpsa_delete_sas_host()` before `scsi_remove_host()`, then later frees device info and performant-mode resources. The node/port/phy linked lists make the controller-level delete recursively delete all known ports and phys.

Module load first attaches the SAS transport class. The SCSI host allocation path later assigns `sh->transportt = hpsa_sas_transport_template`, so host allocation depends on `hpsa_init()` having completed SAS transport attachment. Only after that does `hpsa_init()` register the PCI driver. Module unload unregisters PCI first, allowing all controllers to remove before the shared SAS transport template is released.

## State and Persistence Behavior

Most state in this chunk is host lifetime state under `struct ctlr_info`:

- `ioaccel_cmd_pool`, `ioaccel_cmd_pool_dhandle`, and `ioaccel1_blockFetchTable` for mode 1.
- `ioaccel2_cmd_pool`, `ioaccel2_cmd_pool_dhandle`, `ioaccel2_blockFetchTable`, `ioaccel2_bft2_regs`, and ioaccel2 SG chain blocks for mode 2.
- `reply_queue[]`, `reply_queue_size`, `nreply_queues`, and `blockFetchTable` for performant-mode completions and command fetch sizing.
- `ioaccel_maxsg`, derived from controller configuration and capped to the driver's supported ioaccel mode.
- `sas_host`, a root `hpsa_sas_node` that owns driver-private SAS ports and phys.

The coherent DMA allocations persist until controller teardown or probe unwind. Their DMA handles are programmed into the controller by the performant-mode transition and are subsequently used by interrupt/completion and ioaccel queueing paths. The heap BFT arrays are host-side source tables used while programming transport mode. The ioaccel2 BFT register mapping is established during `hpsa_enter_performant_mode()` and stored in `h->ioaccel2_bft2_regs`; this chunk writes the register entries but does not unmap that mapping in the visible cleanup helper.

The SAS transport objects persist in the Linux device model while the controller and physical devices are present. `hpsa_scsi_dev_t::sas_port` is the durable link from the driver's device table to the SAS transport rphy. `hpsa_sas_get_enclosure_identifier()` uses that link later to report the cached enclosure logical identifier `hpsa_scsi_dev_t::eli`, which was populated by earlier inquiry/report-diagnostic discovery code.

There is no file-backed persistence in this chunk. Persistent side effects are hardware/device-model state: controller transport mode is changed through config-table doorbells and SAS class objects become visible to user space under the kernel device hierarchy. Compile-time offset checks prevent accidental persistent ABI drift in firmware-visible command structures.

## Dependencies and Integration Points

- PCI and DMA APIs: `pci_resource_start()`, `dma_alloc_coherent()`, `dma_free_coherent()`, `remap_pci_mem()`, `readl()`, `writel()`, and PCI driver registration.
- HPSA controller config and transport helpers from earlier in `hpsa.c`: `hpsa_enter_performant_mode()`, `hpsa_wait_for_mode_change_ack()`, `hpsa_get_max_perf_mode_cmds()`, `hpsa_free_reply_queues()`, `hpsa_allocate_ioaccel2_sg_chain_blocks()`, `hpsa_free_ioaccel2_sg_chain_blocks()`, `calc_bucket_map()`, and `hpsa_find_cfg_addrs()`.
- Command lifetime code: `struct CommandList`, `cmd_free()`, command refcounts, and `CMD_IOACCEL1`/`CMD_IOACCEL2` command types.
- SCSI/SAS transport core: `sas_attach_transport()`, `sas_release_transport()`, `sas_port_alloc_num()`, `sas_port_add()`, `sas_port_delete()`, `sas_phy_alloc()`, `sas_phy_add()`, `sas_phy_delete()`, `sas_port_add_phy()`, `sas_port_delete_phy()`, `sas_end_device_alloc()`, `sas_rphy_add()`, and `sas_rphy_free()`.
- SCSI host integration: `hpsa_scsi_host_alloc()` assigns `hpsa_sas_transport_template` to `Scsi_Host::transportt`; `shost_to_hba()` and `phy_to_shost()` bridge SAS callbacks back to `struct ctlr_info`.
- Device discovery/removal code: physical device add/remove paths call `hpsa_add_sas_device()` and `hpsa_remove_sas_device()`, while controller discovery creates `h->sas_host` through `hpsa_add_sas_host()`.
- Firmware-visible structures in `hpsa_cmd.h`: `raid_map_data`, `io_accel1_cmd`, and `io_accel2_cmd`. Offset checks in this chunk are tied directly to queueing, RAID map, and encryption/ioaccel setup code earlier in the driver.

## Risks and Edge Cases

- The ioaccel allocation selection uses `if (io_accel1) ... else if (io_accel2) ...`; controllers advertising both modes will allocate mode 1 resources. Any hardware expecting mode 2 preference would need a deliberate policy change across allocation, setup, and queueing paths.
- `hpsa_free_performant_mode()` frees both ioaccel1 and ioaccel2 families unconditionally. The helpers are null-safe, which makes this robust for partial allocation and capability-dependent allocation.
- `hpsa_put_ctlr_into_performant_mode()` returns success without allocating performant resources when simple mode is forced or performant mode is unsupported. Callers and cleanup paths must tolerate null reply queues and BFT pointers; this chunk's free helpers do.
- Reply queue sizing relies on `hpsa_get_max_perf_mode_cmds()` and `h->max_commands`. If controller-reported limits are wrong, coherent queue allocation size and completion processing can diverge from hardware behavior.
- `hpsa_drain_accel_commands()` has no explicit timeout. If an accelerated command never completes or never changes type/refcount, the loop can sleep forever. This may be acceptable for teardown/reset contexts that require strict draining, but it is a hang risk on broken hardware or lost completions.
- The refcount probing in `hpsa_drain_accel_commands()` assumes `atomic_inc_return()` followed by `cmd_free()` is a safe way to sample command allocation state for every slot. Any future command lifetime changes must preserve that invariant.
- SAS transport protocol fields are hardcoded to `SAS_PROTOCOL_STP` and link rates are unknown. This exposes enough topology for devices but does not model rich PHY properties or real reset/enable/speed control.
- Several SAS callbacks are stubs returning success even though they do not alter hardware (`phy_reset`, `phy_enable`, `phy_setup`). User-space or SAS-core callers may interpret success as an actual action.
- `hpsa_free_sas_phy()` calls `sas_port_delete_phy()` before testing `added_to_port`. If a future caller passes a phy that was allocated but never successfully added, the current helper may ask the SAS core to remove a non-attached phy. The current error path avoids this by directly calling `sas_phy_free()`/`kfree()` for an unadded phy in `hpsa_add_sas_host()`.
- `hpsa_add_sas_device()` sets `device->sas_port` before `sas_rphy_add()` succeeds, but clears it in the failure path. That temporary state must not be observed concurrently by code that assumes a fully registered rphy.
- `hpsa_delete_sas_host()` does not clear `h->sas_host` after freeing it. In current remove flow the controller is being torn down, but reuse after delete would be unsafe unless the caller nulls it.
- The ioaccel2 BFT register mapping stored in `h->ioaccel2_bft2_regs` is written here; no corresponding unmap is visible in this chunk's cleanup routines. Review should confirm `remap_pci_mem()` semantics or cleanup elsewhere.
- `verify_offsets()` protects several critical layouts, but it only covers listed members. Unchecked firmware-visible fields can still drift if structure definitions are edited without matching offset assertions.
- `hpsa_init()` correctly releases the SAS transport template if PCI driver registration fails. If later initialization paths assume `hpsa_sas_transport_template` is non-null, module load order must remain SAS-transport first.

## Test and Validation Signals

- Build the driver after any changes to `hpsa_cmd.h`; `BUILD_BUG_ON()` in this chunk should fail compilation if `raid_map_data`, `io_accel1_cmd`, or `io_accel2_cmd` offsets drift from firmware-visible ABI.
- Probe controllers with `hpsa_simple_mode` enabled and disabled. In simple mode, `hpsa_put_ctlr_into_performant_mode()` should no-op successfully and cleanup should not warn on null performant resources.
- Probe controllers advertising no performant support, performant-only support, ioaccel1 support, and ioaccel2 support. Expected signals include correct allocation family, reply queue count equal to MSI-X vectors or one, and successful mode-change acknowledgment.
- Use fault injection for `dma_alloc_coherent()`, `kmalloc()`, and `hpsa_allocate_ioaccel2_sg_chain_blocks()` to verify staged unwind frees ioaccel pools, reply queues, and BFTs without double-free.
- Exercise remove and probe-error paths after successful performant setup. Validate `hpsa_free_performant_mode()` clears command pool pointers, reply queue heads, and BFT pointers.
- Run high-concurrency ioaccel I/O followed by reset/remove paths that call `hpsa_drain_accel_commands()`. The visible signal is that the drain exits only after `CMD_IOACCEL1`/`CMD_IOACCEL2` commands leave the allocated state.
- Discover physical HBA devices and confirm `/sys/class/sas_port`, `/sys/class/sas_phy`, and rphy/end-device entries appear with the expected SAS addresses.
- Remove physical devices or rescan topology changes and confirm `hpsa_remove_sas_device()` deletes the SAS port/rphy and clears `hpsa_scsi_dev_t::sas_port`.
- Query SAS enclosure identifiers through the transport class. Devices with matching `sas_rphy` should return `hpsa_scsi_dev_t::eli`; unknown rphys or missing host/controller mappings should return `-ENXIO`.
- Exercise SAS transport operations from user space where available. Link error queries should return zero, bay identifier should fail with `-ENXIO`, and speed setting should fail with `-EINVAL`.
- Test module load failure by forcing `pci_register_driver()` failure after `sas_attach_transport()` succeeds; the SAS transport template should be released. Module unload should unregister PCI devices before releasing the shared SAS transport.
