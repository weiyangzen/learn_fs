<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.c

### Purpose
`ivpu_sysfs.c` exposes read-only device attributes for NPU busy time, resident NPU memory utilization, scheduling mode, maximum DPU frequency, and current DPU frequency.

### Important APIs, Types, And Functions
The sysfs show functions are `npu_busy_time_us_show()`, `npu_memory_utilization_show()`, `sched_mode_show()`, `npu_max_frequency_mhz_show()`, and `npu_current_frequency_mhz_show()`. `ivpu_sysfs_init()` registers an attribute group with `devm_device_add_group()`.

### Control Flow
Each show function derives a value from driver state and formats it with `sysfs_emit()`. Busy time locks `submitted_jobs_lock`, adds accumulated `busy_time` and current active interval if jobs are in flight. Memory utilization locks `bo_list_lock` and sums resident BO sizes. Current frequency only reads hardware if `pm_runtime_get_if_active()` succeeds, then releases runtime PM.

### State, Persistence, And Dependencies
The attributes do not store state. They read `submitted_jobs_xa`, busy timestamps, `bo_list`, firmware scheduling mode, and hardware frequency registers. Dependencies include runtime PM, `ivpu_bo`, firmware state, and hardware frequency helpers.

### Integration Points
Registered during device setup and consumed by userspace monitoring. Busy time is maintained by job submission/completion in `ivpu_job.c`; memory residency is maintained by GEM/BO code; scheduling mode is firmware boot state.

### Risks
Frequent busy-time reads take `submitted_jobs_lock` and can affect submission performance, as documented. Current frequency returns zero when suspended, which userspace must distinguish from active low frequency. Memory utilization is resident BO size, not necessarily physical total allocation or firmware internal memory.

### Test Signals
Check attribute presence, formatting as decimal values, busy time increases only while jobs are submitted, memory utilization changes with BO residency, sched mode matches OS/HW firmware mode, max frequency is stable, and current frequency is zero while runtime suspended but nonzero when active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.c -->
