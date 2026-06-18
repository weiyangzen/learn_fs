# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.c

`panthor_drv.c` is the Panthor DRM entry point. It implements versioned uAPI object copying, ioctl handlers, syncobj/timeline dependency handling, VM and group operations, BO ioctls, tiler heap ioctls, mmap dispatch, fdinfo/debugfs, sysfs profiling, platform probe/remove, and module init/exit.

Important local types are `struct panthor_sync_signal`, `struct panthor_job_ctx`, and `struct panthor_submit_ctx`. Helpers include `panthor_set_uobj()`, `panthor_get_uobj_array()`, sync-op validators, submit-context collection/dependency/arming/push functions, `panthor_query_timestamp_info()`, and `group_priority_permit()`. Ioctl handlers cover device queries, VM create/destroy/bind/state, BO create/mmap/label/sync/query, group create/destroy/submit/state, tiler heap create/destroy, and user MMIO offset selection.

Open allocates `panthor_file`, creates VM and group pools, and picks an MMIO aperture. Submit paths copy arrays, create scheduler jobs, collect signal ops, prepare reservations with `drm_exec`, add wait dependencies including intra-batch fences, arm jobs, update signal fences, push jobs, and publish syncobjs after the no-fail point. Mmap dispatches to user MMIO or GEM based on a READ_ONCE copy of the per-file offset.

Dependencies include DRM ioctl/auth/syncobj/exec/GEM, Panthor GEM/MMU/FW/scheduler/heap/device/devfreq, platform OF, PM, arch timers, and uAPI structs. Risks are uAPI validation, fence lifetime, no-fail submit boundaries, priority permission, timestamp IRQ-off windows, and user MMIO offset races. Tests should cover invalid structs/flags, VM bind sync/async, group submit with timeline syncobjs, mmap compat, fdinfo, profiling sysfs, and probe/remove.
