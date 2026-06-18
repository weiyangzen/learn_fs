<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oom.h -->
# sources/distributed-fs/ceph-client/include/linux/oom.h

## Purpose
This header declares the out-of-memory killer interface, OOM context data, task OOM-origin helpers, OOM reaper safety checks, notifiers, and global enable/disable controls.

## Important APIs, types, and functions
`enum oom_constraint` identifies cpuset, memory-policy, memcg, or unconstrained OOM contexts. `struct oom_control` carries zonelist, nodemask, memcg, GFP mask, allocation order/sysrq marker, total pages, chosen victim, badness points, and constraint. It exports `oom_lock`, `oom_adj_mutex`, origin helpers, `tsk_is_oom_victim()`, `check_stable_address_space()`, `oom_badness()`, `out_of_memory()`, `exit_oom_victim()`, OOM notifier registration, `oom_killer_disable()/enable()`, and `find_lock_task_mm()`.

## Control flow
Allocation failure builds an `oom_control`, determines constraints, computes victim badness, selects/kills a task, and marks OOM-victim state. Page fault paths call `check_stable_address_space()` before installing mappings if the OOM reaper may have made the mm unstable. Notifiers and disable/enable gates coordinate global OOM behavior.

## State and persistence
Persistent runtime state includes global locks, task signal flags (`oom_flag_origin`, `oom_mm`), mm `MMF_UNSTABLE`, notifier chains, and chosen victim fields during OOM handling. State is in-memory scheduler/mm state, not durable.

## Dependencies and integration points
It depends on scheduler signal state, nodemasks, memcg, mm fault codes, page allocation GFP/order, task/mm locking, and uapi OOM score definitions.

## Risks and test signals
Risks include killing the wrong task due to constraint calculation, OOM reaper races causing data corruption, deadlocks under OOM locks, notifier side effects, and failing to clear victim/origin state. Test global and memcg OOM, cpuset/mempolicy constraints, sysrq-triggered OOM, OOM reaper with concurrent faults, oom_killer_disable timeout, notifier registration, and victim exit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oom.h -->
