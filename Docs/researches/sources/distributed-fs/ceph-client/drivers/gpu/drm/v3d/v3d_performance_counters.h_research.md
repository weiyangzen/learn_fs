<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_performance_counters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_performance_counters.h

Purpose: Defines metadata structures for V3D performance counter descriptions and generation-selected counter tables.

Important APIs/types/functions: `struct v3d_perf_counter_desc` stores category, name, and description strings. `struct v3d_perfmon_info` stores `max_counters` and a pointer to the active descriptor array.

Control flow: `v3d_perfmon_init()` fills `v3d_perfmon_info`; ioctl handlers use it for validation and descriptor copyout.

State and persistence: The structures are embedded in device state or static arrays; no standalone persistence.

Dependencies and integration points: Included by `v3d_drv.h` and used by `v3d_perfmon.c`.

Risks and test signals: Fixed string sizes define UAPI copy limits. Tests should verify descriptor truncation behavior, counter count selection, and compile-time struct availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_performance_counters.h -->
