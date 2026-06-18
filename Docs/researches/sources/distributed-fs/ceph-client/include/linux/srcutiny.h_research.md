<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutiny.h -->
# sources/distributed-fs/ceph-client/include/linux/srcutiny.h

Purpose: Provides the tiny SRCU implementation for small/non-tree configurations, using compact counters and a workqueue-driven grace-period mechanism.

Important APIs/types/functions: `struct srcu_struct`, `srcu_drive_gp()`, `srcu_tiny_irq_work()`, `__SRCU_STRUCT_INIT()`, `DEFINE_SRCU*()`, `struct srcu_usage` dummy, `__srcu_read_lock()`, `__srcu_ptr_to_ctr()`, `__srcu_ctr_to_ptr()`, fast/updown read wrappers, `synchronize_srcu_expedited()`, `srcu_barrier()`, `srcu_expedite_current()`, and `srcu_torture_stats_print()`.

Control flow: `__srcu_read_lock()` disables preemption, selects the active counter from `srcu_idx`, increments nesting, reenables preemption, and returns the counter index. Fast APIs encode that index as a fake per-CPU pointer for compatibility with the public API. Expedited synchronize and barrier collapse to `synchronize_srcu()`.

State and persistence behavior: State is local to `struct srcu_struct`: two nesting counters, GP running/waiting flags, current and maximum requested index, waitqueue, callback list head/tail, work item, irq_work item, and optional lockdep map.

Dependencies: `irq_work_types.h`, `swait.h`, workqueue and RCU types from `srcu.h`.

Integration points: Selected by `srcu.h` under `CONFIG_TINY_SRCU`. Provides API compatibility with tree SRCU while minimizing storage and complexity.

Risks: Tiny SRCU lacks tree scalability and flavor checking is a no-op. Fast variants are compatibility wrappers rather than separate scalable fast paths.

Test signals: Tiny SRCU builds, rcutorture tiny flavor, nested read sections, callback wakeups, and stats printing for grace-period progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutiny.h -->
