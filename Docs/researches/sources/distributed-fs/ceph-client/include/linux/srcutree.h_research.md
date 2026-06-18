<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutree.h -->
# sources/distributed-fs/ceph-client/include/linux/srcutree.h

Purpose: Defines the scalable tree SRCU implementation data structures, initializers, state-machine constants, and fast reader inline paths.

Important APIs/types/functions: `struct srcu_ctr`, `struct srcu_data`, `struct srcu_node`, `struct srcu_usage`, `struct srcu_struct`, `SRCU_SIZE_*`, `SRCU_STATE_*`, `SRCU_EC_*`, `__SRCU_USAGE_INIT()`, `__DEFINE_SRCU()`, `DEFINE_SRCU*()`, `__srcu_read_lock()`, `synchronize_srcu_expedited()`, `srcu_barrier()`, `srcu_expedite_current()`, `__srcu_ptr_to_ctr()`, `__srcu_ctr_to_ptr()`, `__srcu_read_lock_fast()`, `__srcu_read_unlock_fast()`, fast-updown variants, and `srcu_check_read_flavor()`.

Control flow: Static definitions allocate per-CPU `srcu_data` and a `srcu_usage`. Fast read locks load `ssp->srcu_ctrp`, increment per-CPU lock counters with `this_cpu_inc()` or NMI-safe atomic increments, apply barriers to keep critical sections contained, and return the counter pointer. Unlock increments the corresponding unlock counter. The update-side implementation elsewhere uses `srcu_usage`/`srcu_node` state to aggregate callbacks and advance grace periods.

State and persistence behavior: Persistent SRCU domain state includes per-CPU lock/unlock counters, callback segmented lists, GP-needed sequence numbers, work/timer/irq_work items, combining tree nodes, barrier completion state, sizing transition state, and reader flavor. The `SRCU_SIZE_*` state machine gradually transitions from small to fully initialized tree operation.

Dependencies: `rcu_node_tree.h`, `completion.h`, atomics, per-CPU accessors, raw spinlocks, mutexes, timers, workqueues, and RCU sequence/callback infrastructure.

Integration points: Used by `srcu.h` under `CONFIG_TREE_SRCU`; supports scalable callback and grace-period management for high-CPU-count systems.

Risks: Reader flavor mismatches, incorrect per-CPU pointer/index conversion, premature use of partially initialized combining tree data, or missing RCU-watching constraints in fast readers can break grace-period ordering.

Test signals: TREE_SRCU rcutorture, PROVE_RCU flavor checks, high-CPU callback stress, small-to-big transition coverage, expedited and barrier tests, and NMI-safe fast-reader tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutree.h -->
