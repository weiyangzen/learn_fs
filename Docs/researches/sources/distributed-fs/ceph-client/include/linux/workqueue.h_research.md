# sources/distributed-fs/ceph-client/include/linux/workqueue.h

## Purpose
`workqueue.h` defines Linux deferred work APIs: work item encoding, delayed and RCU work, workqueue attributes, initialization macros, queueing/flushing/cancellation, system workqueues, CPU hotplug/freezer/sysfs integration, and worker diagnostics.

## Important APIs, Types, and Functions
The header defines work data bit layout, pending/inactive/pwq/linked/static flags, flush colors, off-queue pool/disable encoding, `WORK_CPU_UNBOUND`, busy bits, and worker description length. Types include `struct delayed_work`, `struct rcu_work`, `enum wq_affn_scope`, `struct workqueue_attrs`, and `struct execute_work`. Initializers include `DECLARE_WORK`, delayed/deferrable variants, `INIT_WORK*`, `INIT_DELAYED_WORK*`, and `INIT_RCU_WORK*`. Flags include `WQ_BH`, `WQ_UNBOUND`, `WQ_FREEZABLE`, `WQ_MEM_RECLAIM`, `WQ_HIGHPRI`, `WQ_CPU_INTENSIVE`, `WQ_SYSFS`, `WQ_POWER_EFFICIENT`, `WQ_PERCPU`, and internal draining/ordered/legacy flags. APIs include `alloc_workqueue()`, devm/ordered variants, legacy create macros, destroy, attrs allocation/application, queue work/delayed/RCU work, flush/drain, schedule-on-each-CPU, process-context execution, cancel/disable/enable variants, current worker helpers, congestion/busy queries, diagnostics, system workqueue globals, softirq workqueue hooks, freezer/sysfs/watchdog/hotplug hooks, and init functions.

## Control Flow
Callers initialize a `work_struct` with a callback, queue it to a chosen workqueue, and worker threads or BH context execute callbacks asynchronously. Delayed work arms a timer whose callback queues the embedded work. RCU work queues after a grace period. Flush waits for work queued before the flush color to finish; drain prevents new work while existing work completes. Cancellation removes pending work and optionally waits for running callbacks. Workqueue attributes select per-CPU, unbound, NUMA/cache affinity, priority, ordering, and memory-reclaim behavior.

## State and Persistence
Work item state is encoded in `work_struct.data`, list entries, timers, and lockdep maps. Workqueue state is opaque in `struct workqueue_struct`, with pools, active limits, attrs, rescuer threads, and sysfs state managed in implementation files. State persists while workqueues and work items exist; no durable persistence exists.

## Dependencies and Integration Points
Dependencies include timers, allocation tagging, bitops, lockdep, thread/CPU masks, atomics, RCU, workqueue types, freezer, sysfs, CPU hotplug, softirq, and scheduler. Integration points span almost all kernel subsystems needing process-context or deferred execution, including memory reclaim, driver probing, filesystems, networking, and PM.

## Risks
Work item lifetime is critical: queued or running work must not be freed. Flushing system-wide workqueues is warned against because unrelated works can deadlock or delay. `WQ_MEM_RECLAIM` is required for reclaim paths to guarantee forward progress. Delayed work timers must be canceled during teardown. Disable depth is encoded in work data and can overflow if misused. Ordered and max-active limits can deadlock interdependent work.

## Test Signals
Signals include queue/execute/cancel/flush races, delayed work timer behavior, RCU work grace-period ordering, workqueue destruction with pending work, memory-reclaim rescuer tests, freezer suspend/resume, CPU hotplug, sysfs attrs, BH work execution, lockdep, and KASAN lifetime stress.
