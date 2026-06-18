# sources/distributed-fs/ceph-client/include/uapi/drm/v3d_drm.h

## Purpose
This header defines the Broadcom V3D DRM UAPI for newer V3D GPUs. It covers BO creation/mapping/address lookup, CL/TFU/CSD/CPU queue submissions, syncobj and timeline-sync extensions, device parameter queries, performance monitor creation/querying, and reset/timestamp/performance query helper jobs.

## Important APIs and types
Ioctls include `SUBMIT_CL`, `WAIT_BO`, `CREATE_BO`, `MMAP_BO`, `GET_PARAM`, `GET_BO_OFFSET`, `SUBMIT_TFU`, `SUBMIT_CSD`, perfmon create/destroy/get-values/get-counter/set-global, and `SUBMIT_CPU`. `drm_v3d_extension` is a linked-list extension base with IDs for multi-sync, indirect CSD, timestamp query reset/copy, and performance query reset/copy. `drm_v3d_sem` describes binary or timeline syncobj wait/signal entries. `drm_v3d_submit_cl` submits binner and render command lists, BO handles, QMA/QMS/QTS tile allocation data, syncobjs, flags, perfmon ID, and extensions. `drm_v3d_submit_tfu` and `drm_v3d_submit_csd` define texture-formatting and compute dispatch submissions. CPU jobs use extension-specific records and BO-handle expectations.

## Control flow and state
Userspace creates BOs, obtains mmap offsets and V3D virtual offsets, queries capabilities, builds CL/TFU/CSD submissions with BO handle lists, and coordinates queue dependencies with in/out syncobjs or multi-sync extensions. CL submission stages binner before render and has per-FD ordering rules, but cross-FD or cross-queue ordering is explicit via syncobjs. Perfmon objects are created with selected counters, attached to jobs or made global, then values are read after explicit synchronization.

## State and persistence behavior
BO offsets are private to the DRM fd and valid for the GEM handle lifetime. Per-FD queue ordering persists across submissions. Perfmon IDs persist until destroyed, and a global perfmon affects all jobs while active. Syncobj operations can be binary or timeline-based. CPU query jobs write timestamp/performance results and availability state into BOs and syncobjs.

## Dependencies and integration points
The header depends on `drm.h`, DRM GEM, DRM syncobjs/timeline syncobjs, Broadcom V3D queues, CL command streams, TFU and CSD hardware packets, and Mesa query/performance infrastructure. Device capability queries gate optional submission paths such as TFU, CSD, cache flush, perfmon, multi-sync, CPU queue, and super pages.

## Risks and test signals
Risks include extension-chain validation bugs, stale BO offsets, missing cross-queue synchronization, incorrect cache-flush flag handling, perfmon/global perfmon conflicts, timeline point mishandling, and CPU-job extension/BO-count mismatches. Tests should cover each queue, wait-bo timeout, get-param capability gates, multi-sync with multiple waits/signals, indirect CSD uniform rewrite offsets, timestamp/performance query reset/copy, perf counter metadata bounds, global perfmon exclusion, and reserved MBZ field rejection.
