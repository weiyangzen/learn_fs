# sources/distributed-fs/ceph-client/drivers/scsi/sg.c

## Purpose
Implements the Linux SCSI generic (`sg`) character driver, exposing SCSI command passthrough devices as `/dev/sgN` under major `SCSI_GENERIC_MAJOR`. It supports the legacy `struct sg_header` read/write ABI and the newer `sg_io_hdr_t` ABI used by `SG_IO`, plus polling, async notification, mmap-backed reserved buffers, direct I/O, blk tracing, sysfs class devices, and optional `/proc/scsi/sg` diagnostics.

## Important APIs, Types, And Functions
The central state types are `Sg_device`, `Sg_fd`, `Sg_request`, and `Sg_scatter_hold`. `Sg_device` tracks one SCSI device, its minor number, open/exclusive state, sysfs cdev, attached file descriptors, and detach state. `Sg_fd` is per-open state: request list, reserve buffer, timeout, command queue mode, orphan policy, fasync target, and refcount. `Sg_request` represents one queued SCSI command and contains the user header, sense buffer, block request, bio, scatter backing, and completion state. `Sg_scatter_hold` owns indirect I/O pages or references the reserved buffer.

The exported file operations are `sg_open`, `sg_release`, `sg_read`, `sg_write`, `sg_ioctl`, `sg_poll`, `sg_mmap`, and `sg_fasync`. Device lifecycle is handled by `sg_add_device`, `sg_remove_device`, `sg_alloc`, `sg_get_dev`, and `sg_device_destroy` through a `class_interface` registered with the SCSI midlayer. Request creation and completion flow through `sg_new_write`, `sg_common_write`, `sg_start_req`, `sg_rq_end_io`, `sg_new_read`, `sg_finish_rem_req`, and `sg_remove_request`.

The module parameters are `scatter_elem_sz`, `allow_dio`, and `def_reserved_size`. Procfs support, when enabled, adds `allow_dio`, `def_reserved_size`, `devices`, `device_strs`, `device_hdr`, `debug`, and `version` entries under `/proc/scsi/sg`.

## Control Flow
`init_sg` registers the character-device range, class, and SCSI interface. When a SCSI device appears, `sg_add_device` obtains the request queue, allocates a cdev and `Sg_device`, assigns an IDR minor, creates the sysfs device and `generic` backlink, and stores driver data on the class device.

`sg_open` resolves the minor through the IDR, takes a device reference, blocks or fails around `O_EXCL`, verifies error-recovery state unless nonblocking, initializes per-open `Sg_fd` state, reserves a buffer capped by queue limits, and increments open count. `sg_release` decrements open count, clears exclusive state when needed, wakes waiters, and drops the `Sg_fd` reference. Final per-fd cleanup runs in workqueue context in `sg_remove_sfp_usercontext`, which drains unread requests, unmaps bios, frees reserve pages, drops the SCSI device, and releases the module reference.

The write path accepts either old or v3 headers. Legacy writes parse `struct sg_header`, infer command length and transfer direction, copy the CDB, and populate an internal `sg_io_hdr_t`. New writes copy an `sg_io_hdr_t`, validate `interface_id == 'S'`, check mmap/direct-I/O compatibility, copy the user CDB, and optionally enforce read-only access restrictions through `sg_allow_access`. `sg_common_write` validates transfer size, builds and maps the block request in `sg_start_req`, stores `sg_rq_end_io` as completion, and submits with `blk_execute_rq_nowait`.

`sg_start_req` allocates a SCSI block request, copies the CDB into the `scsi_cmnd`, and maps data through direct I/O when allowed and aligned or through pages from the reserve/indirect allocator otherwise. The indirect allocator builds a page-pointer array, rounds buffers to 512-byte boundaries, tries the configured page order, and backs off to smaller orders on allocation failure.

On completion, `sg_rq_end_io` copies status, residual, sense, and duration from the SCSI command, updates removable-media change state for unit attention, frees the block request immediately, and either wakes readers/fasync subscribers or schedules user-context cleanup for dropped orphan requests. Reads locate a completed non-`SG_IO` request by pack id, mark it as being returned, copy legacy or v3 result fields and sense data to userspace, unmap user buffers, and remove the request.

`SG_IO` ioctl is synchronous on top of the same machinery: submit with `sg_new_write`, wait on `read_wait`, then call `sg_new_read`; if interrupted before completion, the request becomes an orphan. Other ioctls manage timeout, reserved size, command queueing, pack-id behavior, orphan retention, request-table introspection, SCSI identity, blk tracing, and delegation to `scsi_ioctl`.

## State And Persistence Behavior
Persistent kernel state is in the IDR minor map, per-device cdev/sysfs objects, per-open request arrays, per-open reserved buffer pages, module parameters, and optional procfs tunables. State is not persisted across module unload or reboot. Request state transitions are encoded in `Sg_request.done`: active (`0`), readable (`1`), and being returned (`2`). Detached devices are guarded by `atomic_t detaching`, which makes new opens fail, wakes waiters, emits `EPOLLHUP`, and allows final destruction only after references drain.

Concurrency is split across `sg_index_lock` for the global IDR, `sfd_lock` for open-file lists, `rq_list_lock` for request lists and completion flags, `open_rel_lock` for open/exclusive counters, and `f_mutex` for mutable per-fd buffer settings. Reference counts on `Sg_device` and `Sg_fd` bridge asynchronous request completion and release paths.

## Dependencies And Integration Points
The driver sits between user-space SCSI passthrough tools and the SCSI/block layers. It depends on SCSI core types and helpers (`scsi_device`, `scsi_cmnd`, `scsi_alloc_request`, `scsi_ioctl`, error handling, command permission checks), block request mapping/unmapping (`blk_rq_map_user_io`, `blk_rq_unmap_user`, blk trace), Linux char-device infrastructure, sysfs classes, IDR allocation, wait queues, fasync, procfs/seq-file support, and VM fault handling for mmap of reserve buffers.

## Risks
This is a security-sensitive raw device interface. The code explicitly restricts legacy read/write use to the opener credential context with `sg_check_file_access` because inherited file descriptors and splice-like paths have historically made this ABI dangerous. User-pointer handling is broad: headers, CDBs, sense buffers, iovecs, mmap buffers, and data buffers all cross the kernel boundary and must preserve exact ABI behavior.

The request lifecycle has several race-prone edges: detach vs open/read/write, `SG_IO` interrupted by a signal, orphan cleanup, request completion racing `release`, reserved-buffer reuse, and immediate block request freeing while user-buffer unmapping is deferred to user context. Buffer sizing is also delicate because it combines user lengths, queue limits, direct-I/O alignment, scatter table limits, and module/proc tunables. Compatibility behavior, including old header field reuse and odd return values such as `SG_GET_TIMEOUT`, should be considered ABI-stable even when surprising.

## Test Signals
Useful tests include `sg3_utils` passthrough smoke tests, `SG_IO` success/error/sense handling, legacy read/write command flow, nonblocking open/read/write behavior, `O_EXCL` open contention, command queue saturation, `poll`/`fasync`, forced pack-id reads, timeout and orphan behavior after signal interruption, reserved-buffer resize while idle vs busy, mmap I/O, direct-I/O enablement/alignment fallbacks, hot-unplug/detach while commands are pending, and `/proc/scsi/sg/debug` output with active and completed requests. Kernel build signals should include both `CONFIG_SCSI_PROC_FS` and compat syscall coverage.
