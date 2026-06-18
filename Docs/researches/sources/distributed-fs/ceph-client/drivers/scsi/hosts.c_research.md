# sources/distributed-fs/ceph-client/drivers/scsi/hosts.c

## Purpose

`hosts.c` is SCSI midlayer infrastructure for allocating, publishing, looking up, reference-counting, removing, and iterating `struct Scsi_Host` instances. It is the common bridge between low-level SCSI drivers and the driver core, transport classes, procfs/sysfs exposure, runtime PM, blk-mq tag sets, error handling, and host workqueues. Low-level drivers such as the HiSilicon SAS v3 PCI backend ultimately flow through this file when they call `scsi_host_alloc()`, `scsi_add_host()` or `scsi_add_host_with_dma()`, `scsi_scan_host()`, `scsi_remove_host()` or `sas_remove_host()`, and `scsi_host_put()`.

## Important APIs, Types, and Functions

The exported host lifecycle API is `scsi_host_alloc()`, `scsi_add_host_with_dma()`, `scsi_remove_host()`, `scsi_host_lookup()`, `scsi_host_get()`, `scsi_host_put()`, `scsi_host_busy()`, `scsi_queue_work()`, `scsi_flush_work()`, `scsi_host_complete_all_commands()`, and `scsi_host_busy_iter()`. Module/core lifecycle functions are `scsi_init_hosts()` and `scsi_exit_hosts()`, and `scsi_is_host_device()` identifies generic SCSI host devices.

The host state model is enforced by `scsi_host_set_state()`, which accepts transitions among `SHOST_CREATED`, `SHOST_RUNNING`, `SHOST_RECOVERY`, `SHOST_CANCEL`, `SHOST_DEL`, `SHOST_CANCEL_RECOVERY`, and `SHOST_DEL_RECOVERY`. Internal release and lookup helpers are `scsi_host_cls_release()`, `scsi_host_dev_release()`, `__scsi_host_match()`, `scsi_host_check_in_flight()`, `complete_all_cmds_iter()`, and `__scsi_host_busy_iter_fn()`.

Global state includes the `eh_deadline` module parameter stored in `shost_eh_deadline`, the `host_index_ida` allocator used for host numbers, and `shost_class`, the device class named `scsi_host` with `scsi_shost_groups` attributes. The file relies on `struct scsi_host_template` to seed `struct Scsi_Host` limits and callbacks.

## Control Flow

`scsi_host_alloc()` allocates one `struct Scsi_Host` plus driver private bytes, initializes locks, lists, waitqueues, the scan mutex, host state, default transport template, SCSI limits, DMA/segment constraints, active mode, host-blocked behavior, and blk/SCSI template-derived fields. It allocates a stable host number with `ida_alloc()`, sets up `shost_gendev` on `scsi_bus_type` with `scsi_host_type`, initializes the class device `shost_dev` under `shost_gendev`, starts the per-host error-handler kthread `scsi_eh_%d`, creates a TMF workqueue, and creates the per-template proc host directory. Failure while still in `SHOST_CREATED` drops the generic device reference so `scsi_host_dev_release()` handles partial cleanup.

`scsi_add_host_with_dma()` publishes an allocated host. It validates that `can_queue` is nonzero and that reserved commands have a `queue_reserved_command` method, clamps `cmd_per_lun` to `can_queue`, initializes the sense cache, chooses the generic parent and DMA device, caps `max_sectors` using the DMA device's maximum mapping size, sets up blk-mq tags through `scsi_mq_setup_tags()`, initializes the tag-set refcount and completion, enables runtime PM on `shost_gendev`, adds the generic device, transitions the host to `SHOST_RUNNING`, takes a parent reference, adds the class device, allocates transport-private `shost_data`, optionally allocates a transport workqueue, adds sysfs host attributes, creates a pseudo sdev for reserved commands, adds proc host entries, and runtime-idles the host.

If publish fails after `device_add()`, the function unwinds in reverse: delete `shost_dev`, release its reference when needed, delete `shost_gendev`, disable async suspend and runtime PM, mark runtime suspended, drop the temporary PM reference, and drop the tag-set refcount with `scsi_mq_free_tags()`. Any allocations owned by the host are left for `scsi_host_dev_release()`.

`scsi_remove_host()` cancels an already published host. It serializes with scanning through `scan_mutex`, attempts to transition to `SHOST_CANCEL` or `SHOST_CANCEL_RECOVERY` under `host_lock`, gets a runtime PM reference, flushes the TMF workqueue, calls `scsi_forget_host()` to remove devices, drops proc entries, releases the tag-set reference and waits for `tagset_freed` so command private destructors can still use the host pointer, transitions to `SHOST_DEL` or `SHOST_DEL_RECOVERY`, unregisters the transport device, unregisters the class device, and deletes the generic device.

`scsi_host_dev_release()` is the final memory release path for `shost_gendev`. It waits for pending RCU command callbacks, destroys the TMF workqueue, stops the error-handler kthread, destroys the optional transport workqueue, handles the special never-added `SHOST_CREATED` cleanup for proc hostdir and `shost_dev` name, frees transport-private data, releases the host number to the IDA, drops the parent device reference for published hosts, and frees the `Scsi_Host`.

Lookup and reference handling use the class device. `scsi_host_lookup()` finds the `scsi_host` class device by host number, converts it to `Scsi_Host`, attempts `scsi_host_get()`, and then drops the class lookup reference. `scsi_host_get()` refuses hosts already in `SHOST_DEL` and otherwise references `shost_gendev`; `scsi_host_put()` drops that reference.

Busy/iteration helpers are blk-mq tag-set walks. `scsi_host_busy()` counts requests whose `struct scsi_cmnd` has `SCMD_STATE_INFLIGHT`. `scsi_host_complete_all_commands()` iterates all busy tags, unmaps DMA, clears the result, sets a caller-supplied host byte, and calls `scsi_done()`; the caller must stop concurrent submission/completion. `scsi_host_busy_iter()` adapts a caller callback over `struct scsi_cmnd` to `blk_mq_tagset_busy_iter()`. `scsi_queue_work()` and `scsi_flush_work()` operate on a transport-created host workqueue and warn with stack dumps if the transport did not request one.

## State and Persistence Behavior

The durable runtime object is `struct Scsi_Host`. Its state persists only while device references exist. Host numbering is process-wide kernel state managed by `host_index_ida`; host numbers are freed only in `scsi_host_dev_release()`. `shost_state` is the gate for legal host lifecycle transitions and for refusing late references after deletion starts.

Resource ownership is split between driver-private memory appended to the host allocation, the generic device `shost_gendev`, the class device `shost_dev`, blk-mq tag-set resources, runtime PM state, workqueues, the error-handler kthread, transport-private `shost_data`, proc/sysfs/transport registrations, pseudo sdev state, and parent device references. The release path intentionally centralizes most cleanup in the generic device release callback so partial allocation and failed add paths can be handled consistently.

The only module parameter in this file is `eh_deadline`. It is copied into each host at allocation time, converted from seconds to jiffies if the low-level template has `eh_host_reset_handler`, clamped to `INT_MAX`, and disabled with `-1` otherwise. Changing the module parameter affects later allocations, not already allocated hosts.

## Dependencies and Integration Points

`hosts.c` depends on the Linux driver core (`struct device`, classes, device types, `device_add()`, `device_del()`, `device_unregister()`), runtime PM, async suspend, IDA allocation, kthreads, workqueues, completions, RCU, blk-mq tag iteration, SCSI sysfs/proc/transport helpers, and the SCSI error handler. It includes `scsi_priv.h` and `scsi_logging.h` for internal midlayer operations and logging.

Low-level drivers integrate by filling `struct scsi_host_template`, calling `scsi_host_alloc()` with private size, setting host limits or transport pointers, publishing through `scsi_add_host()`/`scsi_add_host_with_dma()`, scanning, removing the host, and releasing their reference with `scsi_host_put()`. Transport classes integrate through `transportt->host_size`, `transportt->create_work_queue`, and `transport_unregister_device()`. blk-mq integration is through `scsi_mq_setup_tags()`, `scsi_mq_free_tags()`, `tagset_refcnt`, and `tagset_freed`.

User-visible integration is indirect: successful host add creates `/sys/class/scsi_host/hostN`, a generic `hostN` device under the SCSI bus, transport/sysfs attributes, proc host entries when configured, runtime PM state, and SCSI error-handler threads/workqueues named per host.

## Risks and Edge Cases

Lifecycle ordering is the main risk. `scsi_remove_host()` must prevent new devices by changing host state before forgetting existing devices, and it must wait for the tag-set refcount to drop before freeing tags because low-level `.exit_cmd_priv` callbacks may need the host pointer. Illegal state transitions only log and return `-EINVAL`; callers that ignore failures can leave a host in a surprising state, although remove handles recovery-state alternatives.

`scsi_host_complete_all_commands()` is deliberately unsafe against concurrent queue changes; callers must quiesce submission/completion before using it or risk double completion or stale request access. `scsi_host_busy_iter()` similarly delegates locking requirements to its caller. Busy counting only checks `SCMD_STATE_INFLIGHT`, so it is a snapshot rather than a full synchronization primitive.

Runtime PM setup in `scsi_add_host_with_dma()` temporarily increments usage and then calls `scsi_autopm_put_host()` after proc/sysfs setup. Error unwinds must preserve runtime PM balance. Parent references are only dropped in release when the host left `SHOST_CREATED`, so incorrect state changes could affect parent lifetime.

The `eh_deadline` parameter is global and copied at allocation time; extremely large values are clamped, and hosts without a host-reset handler get deadline disabled. Drivers setting `nr_reserved_cmds` without `queue_reserved_command` are rejected at add time. Drivers with `can_queue == 0` are rejected because zero queue depth is no longer supported.

Workqueue helpers assume `transportt->create_work_queue` was set before add. Calling `scsi_queue_work()` or `scsi_flush_work()` on a host without `work_q` returns/logs errors and dumps the stack, which is useful diagnostically but noisy if callers do not check transport capabilities.

## Test Signals

Lifecycle tests should cover successful `scsi_host_alloc()` plus `scsi_add_host_with_dma()`, allocation failures before and after host-number assignment, error-handler kthread creation failure, TMF workqueue failure, `scsi_add_host_with_dma()` failures at sense cache, tag setup, generic device add, class device add, transport-private allocation, workqueue allocation, sysfs add, and pseudo-sdev allocation, verifying release of IDA numbers, PM references, tag sets, device names, proc hostdirs, and parent references.

State-machine tests should verify every legal transition accepted by `scsi_host_set_state()` and representative illegal transitions logged and rejected. Remove tests should cover hosts in `SHOST_RUNNING` and `SHOST_RECOVERY`, active scans guarded by `scan_mutex`, runtime PM reference handling, TMF workqueue flush, device forgetting, tag-set refcount wait, transport unregister, class unregister, and final generic device release.

Integration tests should validate `/sys/class/scsi_host/hostN` creation/removal, proc host entry lifecycle, transport-private `shost_data` allocation, transport-created workqueue use through `scsi_queue_work()` and `scsi_flush_work()`, lookup/reference behavior with `scsi_host_lookup()` during and after removal, and `scsi_is_host_device()` for generic host devices.

Command-iteration tests should exercise `scsi_host_busy()` with in-flight and completed commands, `scsi_host_busy_iter()` callback ordering/early-stop behavior, and `scsi_host_complete_all_commands()` only under quiesced queues, checking DMA unmap, host-byte result, and `scsi_done()` completion. Parameter tests should allocate hosts with `eh_deadline = -1`, valid positive values, overflow-sized values, and templates with and without `eh_host_reset_handler`.
