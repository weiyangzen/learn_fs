# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_os.c

## Purpose

`mpi3mr_os.c` is the Linux OS/SCSI integration layer for the Broadcom MPI3 storage controller driver. It binds the firmware-facing MPI3 controller core to the kernel PCI, SCSI mid-layer, blk-mq, SAS transport, power-management, and PCI error-recovery frameworks.

The file owns the driver module entry/exit path, PCI probe/remove/shutdown/suspend/resume callbacks, the `scsi_host_template`, SCSI command submission, SCSI completion mapping, SCSI error handling, firmware event top-half/bottom-half routing, target-device exposure/removal, and per-controller OS-visible state. Firmware transport, queue allocation, admin command details, BSG application interfaces, and SAS transport helpers are mostly implemented in sibling files, but this file orchestrates their use.

## Important APIs, Types, and Functions

Global driver/module state:

- `mrioc_list`, `mrioc_list_lock`, and `mrioc_ida` track live controller instances and allocate stable small controller IDs.
- Module parameters `prot_mask`, `prot_guard_mask`, `logging_level`, and `max_sgl_entries` control SCSI protection capability advertisement, guard type, debug verbosity, and SGL sizing.
- `event_counter` is exported through the driver attribute `event_counter`.
- `warn_non_secure_ctlr` records probe refusal due to controller security status and changes the unload log message.

Core per-command helpers:

- `mpi3mr_host_tag_for_scmd()` converts a blk-mq unique tag into an MPI host tag, initializes `struct scmd_priv`, and records the operational request queue index.
- `mpi3mr_scmd_from_host_tag()` reconstructs the blk-mq unique tag from MPI host tag plus reply queue index and validates that the command is still in driver scope.
- `mpi3mr_clear_scmd_priv()` clears `scmd_priv`, releases any allocated chain SGL buffers, and marks the command no longer owned by the low-level driver.

Firmware event management:

- `struct mpi3mr_fwevt` carries copied event payload, event ID, ack context, bottom-half flags, discard flags, and a `kref`.
- `mpi3mr_alloc_fwevt()`, `mpi3mr_fwevt_add_to_list()`, `mpi3mr_fwevt_del_from_list()`, `mpi3mr_dequeue_fwevt()`, and `mpi3mr_cleanup_fwevt_list()` manage the ordered workqueue-backed event lifecycle.
- `mpi3mr_os_handle_events()` is the event top half called from firmware reply processing. It performs immediate event-side effects, saves log data, issues or defers acks, and schedules bottom-half work when needed.
- `mpi3mr_fwevt_bh()` dispatches bottom-half handling for device add/info/status, enclosure, SAS topology, PCIe topology, log data, reset-refresh, throttle, and diagnostic trigger events.
- `mpi3mr_send_event_ack()` and `mpi3mr_complete_evt_ack()` send nonblocking firmware event acknowledgments with a small command pool and delayed ack list.

Target and SCSI device state:

- `struct mpi3mr_tgt_dev` is the driver's cached target object keyed primarily by firmware persistent ID and secondarily by device handle. It stores device form, exposure state, queue depth, write-same limits, WWID, enclosure data, throttle data, and device-form-specific data.
- `struct mpi3mr_stgt_priv_data` is attached to `scsi_target->hostdata`; it stores the firmware handle/persistent ID, block/remove flags, target type, throttling state, and a reference back to `mpi3mr_tgt_dev`.
- `struct mpi3mr_sdev_priv_data` is attached to `scsi_device->hostdata`; it stores the LUN ID, target-private pointer, NCQ priority flag, pending count, and write-same limit.
- `mpi3mr_create_tgtdev()` creates or updates target objects from firmware Device Page 0.
- `mpi3mr_update_tgtdev()` copies Device Page 0 into target state, classifies SAS/SATA, PCIe/NVMe, and virtual disk forms, computes hidden/non-STL exposure, queue-depth, write-same, DIF/DIX, timeout, and throttle metadata.
- `mpi3mr_report_tgtdev_to_host()` exposes non-SAS-transport devices through `scsi_scan_target()` or delegates SAS/SATA devices to `mpi3mr_report_tgtdev_to_sas_transport()`.
- `mpi3mr_remove_tgtdev_from_host()` removes exposed devices through `scsi_remove_target()` or SAS transport removal.
- `mpi3mr_refresh_tgtdevs()` reconciles target exposure after reset by removing missing/hidden devices and scanning or updating valid devices.

SCSI I/O path:

- `mpi3mr_qcmd()` is the `queuecommand` implementation. It rejects commands during unrecoverable, reset, PCI error, removal, or target-blocked states; handles SAS4116 NVMe UNMAP quirks; creates an MPI3 SCSI IO request; sets CDB, LUN, handle, data direction, priority, EEDP, write-same divert, throttling, and SGEs; then posts to the operational request queue with `mpi3mr_op_request_post()`.
- `mpi3mr_setup_eedp()` maps SCSI protection operations and flags into MPI3 EEDP flags and metadata SGL requirements.
- `mpi3mr_prepare_sg_scmd()` and `mpi3mr_build_sg_scmd()` DMA-map data and protection SG lists into MPI3 SGLs, using chain buffers when the frame cannot hold all SGEs.
- `mpi3mr_process_op_reply_desc()` handles operational reply descriptors, maps MPI/SCSI status to `scmd->result`, copies sense data, maps EEDP errors into sense, updates throttle accounting, unmaps DMA, clears command-private state, reposts sense buffers, and completes the command with `scsi_done()`.

Task management and error handling:

- `mpi3mr_issue_tm()` posts synchronous MPI3 SCSI Task Management requests for abort, LUN reset, and target reset. It blocks the target during TM, adapts timeout by device type, polls pending completions after success, and updates pending command counts.
- `mpi3mr_eh_abort()`, `mpi3mr_eh_dev_reset()`, `mpi3mr_eh_target_reset()`, `mpi3mr_eh_bus_reset()`, and `mpi3mr_eh_host_reset()` implement SCSI error-handler callbacks.
- `mpi3mr_wait_for_host_io()`, `mpi3mr_flush_host_io()`, and `mpi3mr_flush_cmds_for_unrecovered_controller()` drain or force-complete outstanding I/O during reset and unrecoverable-controller flows.
- `mpi3mr_dev_rmhs_send_tm()`, `mpi3mr_dev_rmhs_complete_tm()`, and `mpi3mr_dev_rmhs_complete_iou()` implement the firmware device-removal/hidden-ack handshake using target reset followed by IO Unit Control, with bounded command slots and delayed work lists.

Lifecycle and registration:

- `mpi3mr_driver_template` registers the SCSI host callbacks and capabilities, including blk-mq queue mapping, polling, queue depth change, scan callbacks, target/device allocation and destruction, and EH handlers.
- `mpi3mr_probe()` validates controller security status, allocates `Scsi_Host` plus `struct mpi3mr_ioc`, initializes locks/lists/internal commands/workqueue/module settings, sets protection capabilities, sets up PCI/controller resources, initializes the IOC, adds the SCSI host, scans, and registers BSG.
- `mpi3mr_remove()`, `mpi3mr_shutdown()`, `mpi3mr_suspend()`, and `mpi3mr_resume()` coordinate request blocking, event cleanup, watchdog shutdown/start, IOC/resource cleanup or reinit, device-handle invalidation, target removal, SAS transport cleanup, and instance teardown.
- `mpi3mr_pcierr_error_detected()`, `mpi3mr_pcierr_slot_reset()`, `mpi3mr_pcierr_resume()`, and `mpi3mr_pcierr_mmio_enabled()` integrate with PCI AER/error recovery.
- `mpi3mr_init()` attaches the SAS transport template, registers the PCI driver, and creates the `event_counter` driver attribute; `mpi3mr_exit()` removes them.

## Control Flow

Module load starts in `mpi3mr_init()`, which attaches SAS transport support and registers `mpi3mr_pci_driver`. For each matching PCI device, `mpi3mr_probe()` rejects invalid/tampered/debug-secure controllers, allocates host/controller state, initializes command trackers and locks, clamps SGL limits, advertises SCSI protection support, creates the firmware event workqueue, calls firmware-side resource setup and IOC init, adds the SCSI host, starts scanning, and initializes the BSG interface.

Initial scan begins through `mpi3mr_scan_start()`, which posts Port Enable asynchronously. `mpi3mr_scan_finished()` polls for completion, fault, reset-history, or timeout, then starts the watchdog and clears loading/BSG-blocked flags.

Firmware events arrive through `mpi3mr_os_handle_events()`. Some events are handled immediately in the top half to block I/O, mark devices removed, start removal handshakes, update shutdown timeout, or save log data. Events that require SCSI/SAS topology work or deferred acknowledgment are copied into `mpi3mr_fwevt`, queued on an ordered workqueue, and dispatched by `mpi3mr_fwevt_bh()`. The bottom half exposes devices, removes devices, updates target metadata, refreshes SAS topology, updates enclosures, processes diagnostic buffer trigger events, restores devices after reset, and sends event acknowledgments when required.

Normal I/O enters `mpi3mr_qcmd()`. The command is rejected or requeued if controller/target state is not suitable. Otherwise the driver assigns a blk-mq-derived host tag, fills an MPI3 SCSI IO request, maps SGLs, applies EEDP/write-same/throttle flags, and posts the request to the selected operational request queue. Completions flow from firmware queue processing into `mpi3mr_process_op_reply_desc()`, which identifies the descriptor type, resolves the original `scsi_cmnd`, translates firmware status and sense into SCSI mid-layer result fields, releases DMA/SGL resources, and calls `scsi_done()`.

SCSI error handling calls the EH callbacks. Abort/LUN reset/target reset all converge through `mpi3mr_issue_tm()`. Host reset calls `mpi3mr_soft_reset_handler()`. Bus reset avoids resetting the adapter for RAID volumes if outstanding I/O drains within `MPI3MR_RAID_ERRREC_RESET_TIMEOUT`; otherwise it reports failure and prints pending commands so SCSI EH can escalate.

Reset, resume, and PCI error recovery flows invalidate cached device handles, block requests, clean up or rebuild controller resources, flush or drain host I/O, refresh topology, and rescan/remove targets. Unrecoverable paths force-complete pending SCSI commands with `DID_RESET` and flush internal delayed command lists.

## State and Persistence Behavior

The persistent runtime state is in memory; there is no on-disk persistence in this file. Durable device identity comes from firmware-provided persistent IDs, WWIDs, SAS addresses, and handles cached in `mpi3mr_tgt_dev` and propagated into SCSI target/device hostdata.

Controller state is anchored by `struct mpi3mr_ioc` in `Scsi_Host` private memory. This state includes request/reply queue descriptors, command trackers, target lists, event workqueue/list, reset flags, PCI error flags, SAS topology lists, enclosure list, BSG/log buffers, diagnostic buffer descriptors, throttle counters, and watchdog state. Access is protected by spinlocks, mutexes, atomics, krefs, and ordered workqueue serialization depending on the data path.

Command state is transient and tied to blk-mq tags. Host tag zero is avoided for normal SCSI I/O by storing `blk_mq` tag plus one. `scmd_priv->in_lld_scope` is the key ownership bit preventing stale completions and EH code from acting on commands no longer held by the driver.

Firmware event state is copied from reply payloads into independently allocated `mpi3mr_fwevt` objects. Krefs account for initial allocation, list membership, and queued work. Cleanup paths mark in-progress events for discard if canceling would deadlock against SCSI mid-layer add/remove calls.

Target state persists across reset long enough to reconcile topology. `mpi3mr_invalidate_devhandles()` marks handles invalid and blocks I/O for exposed devices, then reset refresh paths update Device Page 0 data and either re-expose, update, hide, or remove devices. Device handles are not treated as stable across resets; persistent IDs and transport identities drive reconciliation.

I/O throttling state is in controller-level and per-throttle-group atomic pending-large-data counters. Large I/Os can trigger firmware-divert flags and queue-depth reduction events; completions decrement counters and clear divert when low watermarks are reached.

## Dependencies and Integration Points

Kernel subsystems:

- PCI driver core and PCI error handlers: probe/remove/shutdown, PM suspend/resume, AER recovery, config-space security-status reads.
- SCSI mid-layer: `Scsi_Host`, `scsi_host_template`, `scsi_scan_target()`, `scsi_remove_target()`, SCSI EH callbacks, `scsi_done()`, queue depth, sense helpers, protection information APIs.
- blk-mq: tag mapping, busy iterators, queue maps, polling, request priorities, and request timeout configuration.
- DMA API: `scsi_dma_map()`, `scsi_dma_unmap()`, `dma_map_sg()`, SG DMA addresses, and chain-buffer DMA pools allocated elsewhere.
- Workqueue/list/kref/spinlock/mutex/atomic APIs for concurrency and lifetime.
- SAS transport class: `sas_attach_transport()`, `sas_remove_host()`, rphy/phy/port integration via `mpi3mr_transport.c`.

Driver-internal dependencies:

- `mpi3mr_fw.c` supplies resource setup/cleanup, IOC init/reinit/cleanup, operational/admin queue posting, reply queue processing, sense/reply buffer helpers, watchdog, reset handling, and port enable.
- `mpi3mr_app.c` supplies BSG registration, log-data storage, diagnostic buffer and trigger handling.
- `mpi3mr_transport.c` supplies SAS host/expander/port operations, target exposure through SAS transport, rphy lookup, link updates, and transport template callbacks.
- MPI3 protocol definitions from `mpi/mpi30_*.h` define firmware event IDs, request/reply frames, status codes, device page formats, topology event formats, and IO Unit Control operation codes.

## Risks and Edge Cases

- Lifetime correctness is delicate. `mpi3mr_tgt_dev` and `mpi3mr_fwevt` use krefs, but several flows mix list removal, SCSI mid-layer callbacks, and explicit puts. Bugs here can become leaks, use-after-free, or double-put failures.
- Event cleanup has a known deadlock hazard when the current event is blocked inside SCSI device add/remove; the code uses `pending_at_sml` and `discard` to avoid canceling current work in that case. Changes to event cleanup must preserve this behavior.
- Host tag mapping depends on matching blk-mq hardware queue indices with reply queue indices. Incorrect queue mapping or stale `in_lld_scope` state can produce invalid completions and trigger reset paths.
- SGL preparation returns host-busy on DMA mapping or chain allocation failures. On failure paths, data/protection DMA mapping and chain bitmap cleanup must remain balanced.
- Protection information handling spans EEDP flags, metadata SGLs, DMA direction, and error-sense mapping. NVMe devices force DIX0 capability off because the HBA does not support DIX0 for NVMe drives.
- Throttling uses atomic counters but also mutates group/device `io_divert` and queue depths across target lists. Races can affect temporary queue-depth behavior or divert state if device removal/reset overlaps throttling.
- Device removal uses a two-step firmware handshake with limited command slots and delayed lists. If a TM or IO Unit Control completion is lost due to reset, command state must be cleared without losing pending removals.
- Reset and PCI recovery paths block/unblock SCSI requests and tear down/recreate resources. Missing an unblock, watchdog restart, or forced flush can leave I/O stuck.
- `mpi3mr_check_return_unmap()` rewrites UNMAP parameter length for some SAS4116 revisions and may complete commands directly with sense. This quirk is command-buffer-sensitive and should be tested against both legacy and revised hardware behavior.
- `mpi3mr_process_op_reply_desc()` panics on impossible reply/sense-buffer conditions. If firmware or memory corruption produces those paths, the system is intentionally stopped rather than continuing with corrupted completions.
- Probe returns `1` for invalid/tampered controllers rather than a conventional negative errno. Callers and tests should treat this as intentional current behavior.

## Test Signals

Build and static signals:

- The kernel tree or module build should compile `drivers/scsi/mpi3mr/mpi3mr_os.c` with no new warnings.
- `modinfo mpi3mr` should show the expected author, description, GPL license, and version from `mpi3mr.h`.
- Driver sysfs should expose a readable `event_counter` attribute after successful module registration.

Probe/lifecycle signals:

- Loading on supported Broadcom MPI3 PCI IDs should attach SAS transport, register the PCI driver, allocate one `mrioc`, initialize the IOC, add the SCSI host, issue Port Enable, scan targets, start watchdog, and initialize BSG.
- Removing/unloading should stop BSG and driver processing, drain firmware events, destroy the event workqueue, remove SCSI/SAS host exposure, remove cached target devices, stop watchdog, clean IOC/resources, free SAS/enclosure/HBA-port lists, free the IDA ID, and release SAS transport.
- Suspend/resume should block requests, clean the IOC/resources, then set up resources, reinitialize the IOC, unblock requests, refresh devices, and restart watchdog.

I/O path signals:

- Normal read/write commands should receive host tags, post to the expected operational queue, complete through `mpi3mr_process_op_reply_desc()`, unmap DMA, clear `in_lld_scope`, repost sense buffers when used, and call `scsi_done()`.
- Queue-full or SGL/chain exhaustion should return `SCSI_MLQUEUE_HOST_BUSY` without leaking chain bits or DMA mappings.
- Target-blocked states should return `SCSI_MLQUEUE_DEVICE_BUSY`; removed or invalid-handle devices should complete with `DID_NO_CONNECT`.
- SCSI status, residuals, sense data, EEDP guard/app/ref errors, SATA NCQ collateral aborts, busy/resource statuses, and underrun/overrun cases should map to the expected `scmd->result`.

Event/topology signals:

- Device add/info/status events should create/update target cache entries, expose or remove SCSI targets, update queue limits, and send required event acknowledgments.
- SAS and PCIe topology not-responding events should mark devices removed, block/unblock I/O during delay/responding transitions, issue removal handshakes, and remove targets in the bottom half.
- Reset-refresh synthetic events should wait for device refresh and PCI-error blocks, then refresh SAS ports/expanders and target exposure.
- Enclosure add/status events should maintain `mrioc->enclosure_list` and update target enclosure logical IDs through later device updates.

Recovery signals:

- Abort, LUN reset, and target reset EH callbacks should issue TM requests, honor device-specific timeouts, poll pending completions after success, and report success only when the affected command/device/target no longer has pending commands.
- Host reset and TM timeout paths should invoke `mpi3mr_soft_reset_handler()` with the appropriate reset reason.
- Unrecoverable-controller handling should wait for reply queues to leave active poll/ISR use, zero pending I/O counts, complete outstanding SCSI commands with reset status, and flush delayed internal command lists.
- PCI frozen-state recovery should block SCSI requests, stop watchdog, clean resources, request slot reset, rebuild resources on slot reset, run firmware reset, and unblock/restart watchdog on resume.
