# sources/distributed-fs/ceph-client/include/linux/sched/numa_balancing.h

Purpose: declares scheduler/MM hooks for automatic NUMA balancing based on memory access faults.

Important APIs and types: `TNF_*` fault flags, `enum numa_vmaskip_reason`, `task_numa_fault()`, `task_numa_group_id()`, `set_numabalancing_state()`, `task_numa_free()`, and `should_numa_migrate_memory()` are the key contracts.

Control flow: NUMA hinting faults report source/destination nodes and locality flags to scheduler placement logic; scheduler state influences whether a folio should migrate toward a task’s CPU; task teardown frees NUMA grouping/fault state.

State and persistence: per-task NUMA fields live in `task_struct` and associated NUMA groups/fault arrays. They persist while NUMA balancing is active for the task.

Dependencies and integration points: depends on `sched.h`, folios, NUMA balancing config, MM hinting faults, and scheduler placement.

Risks and test signals: risks include migrating shared or inaccessible memory incorrectly, stale NUMA group IDs, disabled-config behavior returning overly permissive migration, and scan-period feedback errors. Test NUMA balancing sysctl toggles, multi-node workloads, shared memory, migration failure paths, task exit, and disabled builds.
