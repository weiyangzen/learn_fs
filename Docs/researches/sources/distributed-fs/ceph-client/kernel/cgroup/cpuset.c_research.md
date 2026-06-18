# sources/distributed-fs/ceph-client/kernel/cgroup/cpuset.c

## Purpose

`cpuset.c` implements the cpuset cgroup controller: CPU and NUMA-node placement constraints for tasks, including cgroup v1 compatibility, cgroup v2 effective masks, partition roots, isolated partitions, scheduler-domain rebuilding, hotplug propagation, fork/attach integration, memory-policy rebinding, and allocator-facing hardwall checks.

## Important APIs, Types, and Functions

Key global state includes `top_cpuset`, `subpartitions_cpus`, `isolated_cpus`, `isolated_hk_cpus`, `force_sd_rebuild`, and static keys tracking cpuset enablement and unsupported memory-only configurations. Locking is explicitly layered as `cpuset_top_mutex`, CPU hotplug lock, `cpuset_mutex`, then `callback_lock`.

Important exported or externally used APIs include `cpuset_full_lock()`, `cpuset_update_tasks_cpumask()`, `cpuset_update_tasks_nodemask()`, `cpuset_write_resmask()`, `cpuset_common_seq_show()`, `cpuset_cpus_allowed()`, `cpuset_cpus_allowed_fallback()`, `cpuset_mems_allowed()`, `cpuset_current_node_allowed()`, `cpuset_nodes_allowed()`, `cpuset_mem_spread_node()`, `cpuset_print_current_mems_allowed()`, and `cpuset_task_status_allowed()`. The controller registers as `cpuset_cgrp_subsys` with allocation, online/offline/killed/free, attach, bind, fork, and default hierarchy file callbacks.

The main local data structures are `struct cpuset` from `cpuset-internal.h`, `struct tmpmasks`, and the private `struct cpuset_migrate_mm_work`. Partition state uses `PRS_MEMBER`, `PRS_ROOT`, `PRS_ISOLATED`, `PRS_INVALID_ROOT`, and `PRS_INVALID_ISOLATED`, with user-facing errors described by `perr_strings`.

## Control Flow and State

Configuration writes enter through `cpuset_write_resmask()` or `cpuset_partition_write()`. `cpuset_write_resmask()` duplicates the current cpuset into a trial object, parses `cpus`, `cpus.exclusive`, or `mems`, validates hierarchy and exclusivity through `validate_change()`, commits under `callback_lock`, and propagates effective-mask changes down the tree.

CPU-mask changes flow through `update_cpumask()` or `update_exclusive_cpumask()`. Both compute effective exclusive CPUs, validate sibling conflicts, update local or remote partition state through `partition_cpus_change()`, and call `update_cpumasks_hier()` to recompute descendants. Local partitions use `update_parent_effective_cpumask()` to remove or return exclusive CPUs from parent effective masks. Remote partitions are allowed only with `CAP_SYS_ADMIN` and pull CPUs from `top_cpuset` through `remote_partition_enable()`, `remote_cpus_update()`, and `remote_partition_disable()`.

NUMA changes flow through `update_nodemask()` and `update_nodemasks_hier()`. Task memory state is updated by `cpuset_change_task_nodemask()` using the task `mems_allowed_seq` sequence counter, and mm/vma memory policies are rebound. If `CS_MEMORY_MIGRATE` is set, page migration is queued to `cpuset_migrate_mm_wq`.

Task migration uses `cpuset_can_attach()` to enforce usable effective masks, security checks, and SCHED_DEADLINE bandwidth accounting. `cpuset_attach()` then updates CPU affinity, memory masks, spread flags, memory policies, and queued page migration. Fork integration has separate paths for normal inheritance and `CLONE_INTO_CGROUP`.

Hotplug enters through `cpuset_update_active_cpus()` or the node notifier, both reaching `cpuset_handle_hotplug()`. The root cpuset is synchronized to active CPUs and memory nodes, descendant effective masks are recomputed, partitions may become invalid due to lost CPUs, and scheduler domains or housekeeping CPU masks are rebuilt. `cpuset_update_sd_hk_unlock()` deliberately drops locks before `housekeeping_update()` to avoid lock-order deadlocks.

## Dependencies and Integration Points

This file integrates with cgroup core (`cftype`, css lifecycle, taskset migration, cgroup file notifications), scheduler affinity and scheduler domains (`set_cpus_allowed_ptr()`, `partition_sched_domains()`, deadline bandwidth/root-domain accounting), CPU/memory hotplug, NUMA memory policy (`mpol_rebind_task()`, `mpol_rebind_mm()`), page migration, security hooks (`security_task_setscheduler()`), OOM and page allocator hardwall checks, housekeeping/isolation masks, and cgroup v1 helpers in `cpuset-v1.c`.

## Risks and Edge Cases

The highest risk is lock ordering around cpuset locks, CPU hotplug locks, scheduler-domain locks, task locks, and housekeeping updates. Partition handling is also fragile: invalid-to-valid transitions depend on sibling exclusivity, active CPU availability, populated cgroups, and housekeeping constraints. Remote partitions add privilege-sensitive paths that mutate `top_cpuset` effective CPUs and global masks. Hotplug can invalidate partitions, clear `subpartitions_cpus`, and force task affinity updates while attaches are in progress. Memory rebinding and page migration are asynchronous, so ordering is split between cpuset locks and the migration workqueue. User-visible mask reads are not atomic across partial reads.

## Test Signals

Useful test coverage includes v2 `cpuset.cpus`, `cpuset.mems`, `cpuset.cpus.exclusive`, and `cpuset.cpus.partition` writes; invalid partition error strings; sibling exclusivity conflicts; remote partition privilege checks; isolated partition conflicts with housekeeping/nohz settings; CPU and memory hotplug with populated and empty cgroups; SCHED_DEADLINE task migration; memory migration and policy rebinding; fork and `CLONE_INTO_CGROUP`; cgroup v1 cpuset behavior; and allocator hardwall behavior through `cpuset_current_node_allowed()`.
