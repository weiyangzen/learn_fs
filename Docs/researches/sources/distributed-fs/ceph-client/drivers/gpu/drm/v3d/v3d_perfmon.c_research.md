<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_perfmon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_perfmon.c

Purpose: Defines V3D performance counter metadata and implements performance-monitor lifetime, start/stop capture, per-file xarray management, and perfmon ioctls including global perfmon selection.

Important APIs/types/functions: Static counter descriptor arrays cover V3D 4.2 and 7.1 events. `v3d_perfmon_init()` selects descriptors by generation. `v3d_perfmon_start()` programs counter source muxes, enables/clears counters, and records `active_perfmon`. `v3d_perfmon_stop()` optionally accumulates counter values and disables counters. Create/destroy/get-values/get-counter/set-global ioctls validate inputs, manage refcounts, copy values/descriptors, and update `global_perfmon`.

Control flow: File open initializes the perfmon xarray; close deletes all perfmons. Job submission can attach/start a perfmon; completion or get-values stops/captures. Global perfmon uses atomic exchange/compare-exchange style updates.

State and persistence: Per-file state is an xarray of `v3d_perfmon` objects with refcount, lock, counters, and accumulated values. Device state tracks active and global perfmon. Values persist only for the object lifetime.

Dependencies and integration points: Integrates V3D performance counter registers, UAPI ioctl structs, xarray, user copy, mutex/refcount helpers, and job submission/perfmon attachment outside this file.

Risks and test signals: Risks include leaked references in `set_global` clear/error paths, active/global perfmon races, generation counter-index validation, and no counter reset except object recreation. Tests should cover invalid counters, create/destroy while active, get-values capture, global set/clear/busy, concurrent files, and V3D generations without perfmon support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_perfmon.c -->
