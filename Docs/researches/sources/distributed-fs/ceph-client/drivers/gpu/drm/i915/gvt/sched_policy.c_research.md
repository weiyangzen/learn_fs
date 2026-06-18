# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.c

## Purpose
`sched_policy.c` implements the default time-based scheduling policy for GVT vGPUs. It maintains an LRU run queue, balances time slices by configured weights, gives newly started vGPUs a temporary priority window, selects the next busy or idle vGPU, and coordinates with the workload scheduler service thread.

## Important APIs, Types, And Functions
Public functions are `intel_gvt_schedule`, `intel_gvt_init_sched_policy`, `intel_gvt_clean_sched_policy`, `intel_vgpu_init_sched_policy`, `intel_vgpu_clean_sched_policy`, `intel_vgpu_start_schedule`, `intel_gvt_kick_schedule`, and `intel_vgpu_stop_schedule`. Private types are `vgpu_sched_data` and `gvt_sched_data`; the active ops table is `tbs_schedule_ops`.

## Control Flow
Global init allocates scheduler data, initializes run queue and hrtimer, and stores it in `gvt->scheduler.sched_data`. Per-vGPU init allocates weighted state. Start inserts the vGPU into the LRU queue, grants two seconds of priority, and starts the timer. The timer requests scheduling; the service thread calls `intel_gvt_schedule`, which rebalances every 100 ms, accounts time, selects a busy vGPU with priority or remaining timeslice, or chooses idle. Switch is deferred until current engine workloads finish, then dispatch waitqueues are woken. Stop removes the vGPU, clears current/next references, and switches owned engine MMIO context back to host.

## State And Persistence
Global state includes current/next vGPU, `need_reschedule`, per-engine current workloads, engine owners, waitqueues, scheduler data, and service bits. Per-vGPU state tracks active/priority flags, priority deadline, schedule-in time, accumulated time, remaining/allocated timeslice, and weight. `gvt->sched_lock` is the primary lock.

## Dependencies And Integration Points
The scheduler depends on workload queues, KVMGT service requests, i915 runtime PM during stop, `intel_gvt_switch_mmio`, MMIO ring-mode handlers that start scheduling, and workload dispatchers that consume `current_vgpu`.

## Risks
Lock ordering and in-flight workload checks are critical. `gvt_balance_timeslice` uses a static stage counter shared across instances. Weight totals must be nonzero. Stop must restore MMIO context before another owner runs.

## Test Signals
Timer-driven requests, fair weighted runtime, event kicks, new-vGPU priority, idle selection, dispatch blocked during reschedule, MMIO switch-back on stop, and no hrtimer activity after all vGPUs are removed.
