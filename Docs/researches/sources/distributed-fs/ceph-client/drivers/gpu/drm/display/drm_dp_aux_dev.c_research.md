# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_dev.c

Purpose: exposes DisplayPort AUX adapters as character devices `/dev/drm_dp_auxN`, allowing userspace to read and write DPCD address space through normal file operations.

Important APIs/types/functions: `struct drm_dp_aux_dev` stores minor index, `drm_dp_aux *`, device node, kref, and active-use count. A global IDR and mutex allocate up to 256 minors; `AUX_MAX_OFFSET` limits file offsets to 1 MiB. `drm_dp_aux_register_devnode()` allocates an aux dev, creates a class device named `drm_dp_aux%d`, and keeps the initial reference. `drm_dp_aux_unregister_devnode()` clears `aux->drm_dev`, removes the IDR entry, drops `usecount`, waits for active I/O to drain, destroys the device, and drops the kref. File ops implement open/kref acquisition, fixed-size llseek, chunked read/write using `DP_AUX_MAX_PAYLOAD_BYTES`, signal interruption, iterator copy, and release/kref put. `drm_dp_aux_dev_init()` creates the class and registers a dynamic char major; exit unregisters both. Sysfs `name` reports the AUX adapter name.

Control flow: read/write increment `usecount` only if nonzero, preventing I/O after unregister starts. They truncate I/O at the AUX address-space limit and loop in payload-sized chunks, updating file position by bytes successfully transferred.

State and persistence: global class, char major, IDR entries, per-device krefs/usecounts, and device nodes persist while AUX adapters are registered. Open file descriptors hold krefs until release; unregister waits for active operations but existing file private data is invalidated for new I/O by usecount zeroing.

Dependencies and integration points: depends on Linux char device/class/IDR/kref/uio APIs and DRM DP DPCD read/write helpers. Called by DP AUX registration paths through internal helper declarations.

Risks: direct userspace DPCD access can perturb display hardware. Partial reads/writes return transferred byte counts, so tools must handle short I/O. Unregister must avoid stale DRM device references, hence `aux->drm_dev=NULL`. Long-running userspace I/O can delay unregister until usecount drains.

Test signals: devnode creation/removal, sysfs name, concurrent open/read/write during unregister, offset bounds, signal-interrupted I/O, payload chunking, and no use-after-free with open descriptors.
