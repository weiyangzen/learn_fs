<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuset.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuset.h

## Purpose

`cpuset.h` declares the kernel-internal cpuset/cgroup interface for constraining task CPU and memory-node placement. It provides static-key gates, lock helpers, allowed-mask queries, memory allocation retry sequencing, scheduler-domain rebuild hooks, and no-op fallbacks when cpusets are disabled. The source was read as a complete 308-line file.

## Important APIs, Types, and Functions

With `CONFIG_CPUSETS`, it exposes static keys `cpusets_pre_enable_key`, `cpusets_enabled_key`, and `cpusets_insane_config_key`, plus `cpusets_enabled()`, `cpuset_inc()`, `cpuset_dec()`, and `cpusets_insane_config()`. Core APIs include `cpuset_init()`, `cpuset_init_smp()`, `cpuset_force_rebuild()`, `cpuset_update_active_cpus()`, `cpuset_lock()`, `cpuset_unlock()`, `cpuset_cpus_allowed*()`, `cpuset_mems_allowed()`, `cpuset_current_node_allowed()`, `cpuset_zone_allowed()`, `cpuset_mems_allowed_intersects()`, memory pressure hooks, proc/status output hooks, spread-page helpers, deadline accounting rebuilds, scheduler-domain rebuild/reset, `read_mems_allowed_begin()`, `read_mems_allowed_retry()`, `set_mems_allowed()`, and `cpuset_nodes_allowed()`.

## Control Flow

Cpuset setup enables static branches in a deliberate order so memory-allocation retry loops do not deadlock when static-branch text patching is partially applied. Allocation code snapshots `mems_allowed_seq`, attempts an operation, and retries if cpuset memory policy changed concurrently. CPU hotplug and cpuset changes rebuild scheduler domains and active CPU masks.

## State and Persistence Behavior

Persistent state lives in cgroups, task `mems_allowed`, task spreading flags, static keys, and scheduler-domain partitions. `set_mems_allowed()` updates current task memory policy under task lock, IRQ save/restore, and seqcount protection.

## Dependencies and Integration Points

It depends on scheduler, topology, task, cpumask, nodemask, mm, mmu context, and jump labels. It integrates with cgroups, page allocator, NUMA policy, scheduler domains, procfs task status, deadline scheduler accounting, and CPU hotplug.

## Risks and Edge Cases

Static-key enable/disable ordering is subtle; reversing it can break retry loops. Allocation paths must retry only when appropriate after `read_mems_allowed_retry()`. Disabled-cpuset fallbacks return broad possible masks and all memory nodes, which can hide bugs in cpuset-enabled builds. Scheduler-domain rebuilds must be synchronized with hotplug and cgroup changes.

## Test Signals

Signals include cgroup cpuset selftests, memory-node update race tests, page allocation retry under concurrent cpuset changes, CPU hotplug with cpuset partitions, proc/status allowed mask output, v1 memory pressure tests, and builds with `CONFIG_CPUSETS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuset.h -->
