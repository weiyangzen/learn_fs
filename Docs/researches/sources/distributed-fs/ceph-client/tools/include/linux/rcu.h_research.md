<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rcu.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rcu.h

## Purpose
`rcu.h` supplies the tiny RCU and lockdep-facing stubs needed by liblockdep-style tools code.

## APIs And Flow
It defines a global `rcu_scheduler_active`, inline status helpers `rcu_lockdep_current_cpu_online()`, `rcu_is_cpu_idle()`, and `rcu_is_watching()`, plus `rcu_assign_pointer()` and `RCU_INIT_POINTER()`. Flow is stubbed: CPU-online and idle checks return true, watching returns false, and pointer publication is a plain assignment.

## State, Dependencies, Risks, Tests
The only declared state is `rcu_scheduler_active`; there is no grace-period engine or read-side tracking. Integration points are lockdep and imported kernel code that probes RCU state while running in a single-process tools context. Risks are treating these stubs as concurrency protection, missing memory barriers around pointer publication, and multiple-definition hazards if the non-extern global is included in several linked objects. Tests should compile current consumers, inspect linkage for `rcu_scheduler_active`, and verify shared data structures use separate synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rcu.h -->
