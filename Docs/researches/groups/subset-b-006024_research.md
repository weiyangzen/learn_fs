# Research Report: subset-b-006024

This grouped report covers the cgroup and kernel support files assigned to `subset-b-006024`. Each section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cpuset.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cpuset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/debug.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/debug.c

## Purpose

`debug.c` implements an unstable cgroup debug controller for inspecting cgroup core internals. It is intended for diagnostics rather than stable user ABI.

## Important APIs, Types, and Functions

The controller registers `debug_cgrp_subsys`. It allocates a bare `struct cgroup_subsys_state` in `debug_css_alloc()` and frees it in `debug_css_free()`. Read handlers include `debug_taskcount_read()`, `current_css_set_read()`, `current_css_set_refcount_read()`, `current_css_set_cg_links_read()`, `cgroup_css_links_read()`, `cgroup_subsys_states_read()`, `cgroup_masks_read()`, and `releasable_read()`. `enable_debug_cgroup()` enables v2 debug files implicitly when the `cgroup_debug` boot parameter is used.

## Control Flow and State

The file is mostly read-only. Debugfs-like cgroup files walk `css_set`, `cgrp_cset_link`, task lists, subsystem state arrays, and cgroup masks while holding either `css_set_lock` or a live kernfs/cgroup lock. v1 exposes names such as `cgroup_css_links`, `cgroup_subsys_states`, and `cgroup_masks`; v2 uses shorter names such as `css_links`, `csses`, and `masks`.

## Dependencies and Integration Points

It depends tightly on cgroup core internals from `cgroup-internal.h`, including `css_set_lock`, `task_css_set()`, `cgroup_kn_lock_live()`, `cgroup_task_count()`, css ids, threaded css sets, cgroup masks, and population/release state.

## Risks and Edge Cases

The output exposes kernel addresses with `%pK`, so pointer visibility follows kernel pointer-printing policy. Reads can be expensive on large cgroup/task graphs and are intentionally unstable. `WARN_ON(count != cset->nr_tasks)` can surface internal accounting mismatches. Because this is diagnostic code, users must not depend on file names or formats as ABI.

## Test Signals

Test with `cgroup_debug` enabled and disabled; read all legacy and v2 files; create threaded cgroups and migrating tasks; verify task-count and css-set refcount displays; and check that removing cgroups makes live-lock checks return `-ENODEV` rather than stale data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/dmem.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/dmem.c

## Purpose

`dmem.c` implements a device-memory cgroup controller. It lets device subsystems register named memory regions and charge per-cgroup usage against hierarchical `min`, `low`, and `max` limits using `page_counter`.

## Important APIs, Types, and Functions

Core types are `struct dmem_cgroup_region`, `struct dmemcg_state`, and `struct dmem_cgroup_pool_state`. Exported APIs include `dmem_cgroup_register_region()`, `dmem_cgroup_unregister_region()`, `dmem_cgroup_try_charge()`, `dmem_cgroup_uncharge()`, `dmem_cgroup_pool_state_put()`, and `dmem_cgroup_state_evict_valuable()`.

The controller uses a global `dmemcg_lock`, an RCU-protected `dmem_cgroup_regions` list, region `kref`s, pool `refcount_t`s, and css lifecycle callbacks `dmemcs_alloc()`, `dmemcs_offline()`, and `dmemcs_free()`.

## Control Flow and State

Devices first call `dmem_cgroup_register_region()` with a size and formatted name. Per-cgroup pools are created lazily by `get_cg_pool_unlocked()` and `get_cg_pool_locked()`, recursively ensuring ancestors have pools and that `page_counter.parent` links are initialized. Charges call `dmem_cgroup_try_charge()`, which pins the current dmem css, gets or creates a pool for the region, and uses `page_counter_try_charge()`. On limit failure it can return the limiting pool for eviction decisions. Uncharge paths drop page-counter usage, css references, and pool references.

Limit writes parse `region value` lines for `min`, `low`, and `max`, where `max` maps to `PAGE_COUNTER_MAX`. Reads iterate registered regions and show capacity, current, min, low, or max. Offline css resets all limits to unlimited-style defaults; freeing a css removes its pools from both css and region lists.

## Dependencies and Integration Points

The file depends on cgroup core, `linux/cgroup_dmem.h`, RCU list traversal, global spin locking, `page_counter`, parser helpers, css references, and external device-memory callers that manage region lifetime and call charge/uncharge symmetrically.

## Risks and Edge Cases

Lifetime is subtle: a region can unregister while pools still exist, so lookups rely on RCU plus `kref_get_unless_zero()`, and pool freeing is deferred through RCU. Pool initialization is recursive and can allocate outside the spinlock on `-ENOMEM`, so partial initialization paths need stress coverage. Charge failure returns `-EAGAIN` and may hand out a referenced limiting pool that callers must release. Eviction decisions depend on calculated effective min/low protections and ancestor relationships.

## Test Signals

Tests should cover region register/unregister while cgroups exist, repeated concurrent charges and uncharges, max-limit failures, `ret_limit_pool` release, min/low eviction behavior with and without `ignore_low`, multi-line limit writes, css offline reset, and RCU teardown under concurrent reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/dmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/freezer.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/freezer.c

## Purpose

`freezer.c` implements the cgroup v2 freezer behavior. It tracks requested freeze state, effective freeze inherited from ancestors, task frozen counters, frozen descendants, and user notifications through `cgroup.events`.

## Important APIs, Types, and Functions

Important functions are `cgroup_update_frozen()`, `cgroup_enter_frozen()`, `cgroup_leave_frozen()`, `cgroup_freezer_migrate_task()`, and `cgroup_freeze()`. Internal helpers include `cgroup_update_frozen_flag()`, `cgroup_propagate_frozen()`, `cgroup_freeze_task()`, and `cgroup_do_freeze()`.

## Control Flow and State

`cgroup_freeze()` is called with `cgroup_mutex` held when a cgroup freeze knob changes. It updates the requested state, walks descendants, recomputes effective freeze from parent and self requests, and calls `cgroup_do_freeze()` only for subtrees whose effective state changed. `cgroup_do_freeze()` sets or clears `CGRP_FREEZE`, records freeze timing in a seqcount-protected freezer state, sends tracepoints, and sets or clears `JOBCTL_TRAP_FREEZE` on non-kernel tasks.

Tasks call `cgroup_enter_frozen()` when they enter a frozen or stopped state and `cgroup_leave_frozen()` when leaving. These update `nr_frozen_tasks`, recompute `CGRP_FROZEN`, and propagate frozen-state changes to ancestors when all descendants/tasks are frozen. Migration adjusts counters for source and destination cgroups under `css_set_lock`.

## Dependencies and Integration Points

The implementation depends on cgroup core flags and freezer fields, `css_set_lock`, task signal/jobctl state, cgroup task iteration, trace events, `ktime_get_ns()`, and `cgroup.events` notification.

## Risks and Edge Cases

Races between task thawing and a concurrent freeze request are handled by leaving the frozen counter in place and re-arming `JOBCTL_TRAP_FREEZE`. Kernel threads are skipped, so cgroups containing kthreads cannot be fully frozen by this path. Empty cgroups and already-frozen descendants require explicit state revisits to notify waiters. Counter underflow is guarded by `WARN_ON_ONCE`.

## Test Signals

Tests should freeze and thaw non-empty and empty cgroups, nested cgroups with inherited freeze, task migration between freezing and non-freezing cgroups, stopped tasks, exiting tasks, cgroup.events notifications, tracepoints, and frozen time accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/freezer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/legacy_freezer.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/legacy_freezer.c

## Purpose

`legacy_freezer.c` implements the cgroup v1 freezer controller with `freezer.state`, `freezer.self_freezing`, and `freezer.parent_freezing` files. It is described as imperfect and points users toward the cgroup v2 freezer.

## Important APIs, Types, and Functions

The controller state is `struct freezer` with state bits `CGROUP_FREEZER_ONLINE`, `CGROUP_FREEZING_SELF`, `CGROUP_FREEZING_PARENT`, and `CGROUP_FROZEN`. Public integration includes `cgroup1_freezing()` and `freezer_cgrp_subsys`. Main handlers include `freezer_css_alloc()`, `freezer_css_online()`, `freezer_css_offline()`, `freezer_attach()`, `freezer_fork()`, `freezer_read()`, `freezer_write()`, and `freezer_change_state()`.

## Control Flow and State

Writing `FROZEN` or `THAWED` to `freezer.state` calls `freezer_change_state()`, which walks descendants in preorder under `freezer_mutex` and CPU read lock. The target cgroup receives or loses `CGROUP_FREEZING_SELF`; descendants inherit `CGROUP_FREEZING_PARENT` from their parents. Freezing calls `freeze_task()` for all tasks; thawing calls `__thaw_task()` once no freezing bits remain. Reads perform a bottom-up pass with `update_if_frozen()` so cgroups lazily transition from `FREEZING` to `FROZEN` once all children and tasks are frozen.

## Dependencies and Integration Points

It depends on cgroup v1 css lifecycle, `freezer_active` static branch, CPU hotplug read locking, task freezer APIs, task iteration, RCU, and cgroup task migration/fork hooks.

## Risks and Edge Cases

Task migration can temporarily make task state disagree with freezer state; `freezer_attach()` compensates and clears ancestor `FROZEN` bits when needed. State transitions are lazy and read-driven. The root cgroup is non-freezable. The code increments/decrements the `freezer_active` static branch as freezing state appears or disappears, so missed transitions would affect scheduler freezer checks globally.

## Test Signals

Tests should cover writing `FROZEN`/`THAWED`, inherited freezing through nested cgroups, task attach into frozen and thawed cgroups, fork inside a frozen cgroup, bottom-up `freezer.state` reads, static-branch enable/disable balance, and legacy-only file visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/legacy_freezer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/misc.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/misc.c

## Purpose

`misc.c` implements the miscellaneous cgroup controller for scalar host resources that do not justify a dedicated controller, such as AMD SEV/SEV-ES ASIDs and Intel TDX HKIDs when configured.

## Important APIs, Types, and Functions

The controller uses `struct misc_cg` and `struct misc_res` from `linux/misc_cgroup.h`, a root `misc_cg`, and global `misc_res_capacity[]`. Exported APIs are `misc_cg_set_capacity()`, `misc_cg_try_charge()`, and `misc_cg_uncharge()`. User files are `misc.max`, `misc.current`, `misc.peak`, `misc.capacity`, `misc.events`, and `misc.events.local`.

## Control Flow and State

Resource providers set host capacity with `misc_cg_set_capacity()`. Charging walks from the target cgroup to the root, atomically adding usage and checking both the cgroup's `max` and host capacity. On failure, it increments local and hierarchical event counters, notifies the relevant cgroup files, and cancels all partial charges. Uncharge walks the same hierarchy and subtracts usage. Watermarks are maintained with a compare/exchange loop.

## Dependencies and Integration Points

The file integrates with cgroup core cftypes, atomic64 counters, cgroup file notification, and resource providers in KVM/TDX code that call the exported charge APIs around resource allocation and free.

## Risks and Edge Cases

No global mutex protects limit updates or capacity updates, so correctness relies on atomic counters and `READ_ONCE`/`WRITE_ONCE`; racing changes may make a charge observe old limits. The capacity value `0` means unsupported/uninitialized and causes charge failure. Charge/uncharge symmetry is essential, and underflow produces a warning. Event propagation differs between local and hierarchical files.

## Test Signals

Tests should register nonzero and zero capacities, write numeric and `max` limits, charge below and above limits, check rollback after failures, verify peak/current/capacity output, assert events and events.local notifications, and run concurrent charge/uncharge stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/namespace.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/namespace.c

## Purpose

`namespace.c` implements cgroup namespace creation, installation, lookup, release, and proc namespace operations. Cgroup namespaces virtualize cgroup paths relative to a namespace root css set.

## Important APIs, Types, and Functions

Key functions are `copy_cgroup_ns()`, `free_cgroup_ns()`, `cgroupns_install()`, `cgroupns_get()`, `cgroupns_put()`, and `cgroupns_owner()`. The file registers `cgroupns_operations` with procfs namespace support. It uses `struct cgroup_namespace`, `struct ucounts`, `struct css_set`, `struct nsproxy`, and `struct ns_common`.

## Control Flow and State

Without `CLONE_NEWCGROUP`, `copy_cgroup_ns()` simply references the old namespace. With `CLONE_NEWCGROUP`, it requires `CAP_SYS_ADMIN` in the relevant user namespace, charges the per-user namespace count, pins the current task's css set under `css_set_lock`, allocates and initializes a namespace object, stores the user namespace, ucounts, and root css set, and adds it to the namespace tree. Release removes the namespace from the tree, drops the css set, ucounts, and user namespace references, calls `ns_common_free()`, and defers freeing with RCU.

## Dependencies and Integration Points

It depends on user namespace capabilities and ucounts, cgroup css-set lifetime rules, task `nsproxy`, proc namespace operations, namespace tree tracking, and RCU-safe namespace traversal.

## Risks and Edge Cases

Creation cannot take `cgroup_mutex`, so it relies on `css_set_lock` for current css-set pinning. Permission checks during `setns` require capability in both the caller's user namespace and the target cgroup namespace owner. Release order matters because namespace tree traversal can be concurrent and requires an RCU grace period.

## Test Signals

Tests should cover clone with and without `CLONE_NEWCGROUP`, ucount exhaustion, permission failures, `setns()` into another cgroup namespace, proc namespace get/put, namespace tree visibility, and release while namespace traversal is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/pids.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/pids.c

## Purpose

`pids.c` implements the pids cgroup controller, limiting the number of tasks that may be created in a cgroup hierarchy. It prevents fork-based PID exhaustion inside delegated cgroup subtrees.

## Important APIs, Types, and Functions

The main state is `struct pids_cgroup`, containing a hierarchical counter, limit, peak watermark, events, and cgroup file handles. Main callbacks include `pids_can_fork()`, `pids_cancel_fork()`, `pids_release()`, `pids_can_attach()`, and `pids_cancel_attach()`. Files include `pids.max`, `pids.current`, `pids.peak`, `pids.events`, and v2 `pids.events.local`.

## Control Flow and State

Fork charging enters `pids_can_fork()`, which calls `pids_try_charge()` on the destination css set. `pids_try_charge()` walks ancestors, atomically increments counters, checks limits, records the failing cgroup, and rolls back partial charges on failure. On success, task exit eventually calls `pids_release()` to uncharge. Task migration uses `pids_can_attach()` to charge the destination and uncharge the source, intentionally allowing organizational moves even if they make current usage exceed limits. `pids_cancel_attach()` reverses this if migration fails.

## Dependencies and Integration Points

It depends on cgroup task migration/fork/release hooks, atomic64 counters, cgroup event notifications, cgroup v1/v2 file registration, and cgroup root flags controlling whether pids events are local-only.

## Risks and Edge Cases

Limits are not locked against concurrent forks, but atomic charging and rollback enforce the observed hierarchy. Migration can produce `pids.current > pids.max` by design. Watermarks are racy and approximate. Event semantics differ between legacy/local-events mode and default hierarchical mode. Counter underflow warns because it indicates controller accounting bugs.

## Test Signals

Tests should set numeric and `max` limits, fork up to and beyond limits, verify `-EAGAIN`, check current/peak values, ensure event counters and file notifications increment correctly, migrate tasks into limited cgroups, cancel failed migrations, and exercise threaded cgroups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/pids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/rdma.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/rdma.c

## Purpose

`rdma.c` implements the RDMA cgroup controller, limiting per-cgroup, per-device RDMA resources such as HCA handles and HCA objects.

## Important APIs, Types, and Functions

Important types are `struct rdma_cgroup`, `struct rdmacg_device`, `struct rdmacg_resource_pool`, and `struct rdmacg_resource`. Exported APIs are `rdmacg_register_device()`, `rdmacg_unregister_device()`, `rdmacg_try_charge()`, and `rdmacg_uncharge()`. User files are `rdma.max` and `rdma.current`.

## Control Flow and State

RDMA device drivers register devices into the global `rdmacg_devices` list. Limits are configured as lines beginning with a device name followed by resource assignments such as `hca_handle=max hca_object=32`. `rdmacg_resource_set_max()` parses those assignments, finds or creates the cgroup/device resource pool, and updates limits.

Charging pins the current RDMA css and walks from the current cgroup to the root. For each ancestor it lazily creates an rpool for the target device, increments usage if below max, and rolls back via `rdmacg_uncharge_hierarchy()` on allocation or limit failure. Uncharge walks back up the hierarchy and decrements usage. Empty rpools whose limits are all unlimited are freed.

## Dependencies and Integration Points

The controller integrates with RDMA core through `linux/cgroup_rdma.h`, cgroup css lifetime, cgroup files, parser helpers, and a global mutex protecting both device and per-cgroup resource-pool lists.

## Risks and Edge Cases

Device unregister assumes no new RDMA resources will be created and frees all pools for that device. Charge rollback must stop at the failed ancestor to avoid over-uncharge. Resource parsing accepts `max` or nonnegative integers and must reject malformed input. Rpool lifetime is tied both to usage and configured finite limits, so cleanup depends on `usage_sum` and `num_max_cnt`.

## Test Signals

Tests should register/unregister devices, write valid and invalid `rdma.max` lines, charge below and above per-resource limits, verify rollback on failures, read current and max across multiple devices, free pools after uncharge/reset-to-max, and race reads/writes against device removal under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/rstat.c -->
# sources/distributed-fs/ceph-client/kernel/cgroup/rstat.c

## Purpose

`rstat.c` implements cgroup recursive statistics infrastructure. It tracks per-cpu stat updates cheaply, builds flush trees on demand, flushes subsystem and base cgroup stats, exposes CPU time totals, and registers BPF kfuncs for rstat integration.

## Important APIs, Types, and Functions

Main APIs are `css_rstat_updated()`, `css_rstat_flush()`, `css_rstat_init()`, `css_rstat_exit()`, `ss_rstat_init()`, `__cgroup_account_cputime()`, `__cgroup_account_cputime_field()`, and `cgroup_base_stat_cputime_show()`. It uses `struct css_rstat_cpu`, `struct cgroup_rstat_base_cpu`, `struct cgroup_base_stat`, per-subsystem locks and llist heads, and the global base-stat lock/list.

## Control Flow and State

Stat writers update per-cpu counters and call `css_rstat_updated()` with preemption disabled. This function atomically adds the css's per-cpu node to a lockless per-cpu backlog list, using a self-pointer/cmpxchg pattern to tolerate IRQ/NMI reentry. Flushers call `css_rstat_flush()`, which iterates possible CPUs, acquires the appropriate rstat lock, drains the lockless list into an updated tree, builds an ordered flush list with children before parents, and invokes either base-stat flushing/BPF hooks or the subsystem's `css_rstat_flush` callback.

Base CPU-time accounting stores per-cpu deltas protected by `u64_stats` seqcounts. `cgroup_base_stat_flush()` propagates deltas to cgroup and parent subtree totals. The root cgroup is handled specially by reading global kernel CPU stats directly.

## Dependencies and Integration Points

It integrates with cgroup core css lifetime, per-cpu allocation, llist, spinlocks, tracepoints, scheduler CPU time accounting, `u64_stats`, BPF/BTF kfunc registration, and optional scheduler core force-idle stats.

## Risks and Edge Cases

The memory-ordering comments are important: users needing a strict updater/flusher guarantee must provide a barrier before `css_rstat_updated()` and may need a paired barrier in flush processing. NMI updates are ignored on architectures lacking safe cmpxchg or percpu operations. Flushes can be expensive because they iterate all possible CPUs, but they drop/reacquire locks per CPU to avoid long IRQ-off sections. Exit sanity checks warn if updated lists are not clean after flush.

## Test Signals

Tests should account CPU time in nested cgroups, flush from subtree roots, validate child-before-parent propagation, exercise subsystem rstat callbacks, run concurrent updater/flusher stress, verify BPF kfunc availability for tracing programs, test css exit cleanup, and compare root cgroup CPU output to global CPU stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/rstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/compat.c -->
# sources/distributed-fs/ceph-client/kernel/compat.c

## Purpose

`compat.c` provides 32-bit compatibility helpers and compat syscall implementations used by 64-bit kernels serving 32-bit userspace ABIs.

## Important APIs, Types, and Functions

Functions include optional `compat_sys_sigprocmask()`, `put_compat_rusage()`, `compat_sched_setaffinity()`, `compat_sched_getaffinity()`, `get_compat_sigevent()`, `compat_get_bitmap()`, `compat_put_bitmap()`, and exported `get_compat_sigset()`.

## Control Flow and State

`compat_sys_sigprocmask()` translates an old compat signal mask, rejects attempts to block `SIGKILL`/`SIGSTOP`, applies the requested operation to `current->blocked`, and optionally copies out the old mask. `put_compat_rusage()` narrows a native `rusage` into `compat_rusage` and copies it to userspace. Compat affinity syscalls allocate cpumasks, translate compat bitmaps, and call native scheduler affinity helpers. `get_compat_sigevent()` copies the fields the kernel needs from a compat sigevent. Bitmap helpers pack and unpack pairs of compat words into native words.

## Dependencies and Integration Points

It depends on compat ABI types, uaccess primitives, scheduler affinity APIs, signal APIs, rusage/timer structures, endian-specific signal-set layout, and architecture Kconfig such as `__ARCH_WANT_SYS_SIGPROCMASK`.

## Risks and Edge Cases

The main risks are userspace pointer faults, size/alignment validation, endian conversion for signal sets, truncation or layout mismatch between native and compat structures, and cpumask length handling. Affinity get rejects lengths too small for `nr_cpu_ids` and lengths not aligned to compat word size.

## Test Signals

Tests should run 32-bit programs on a compat kernel path for signal masks, affinity set/get with short, exact, long, and misaligned lengths, `getrusage()` field translation, sigevent creation, bitmap round trips on big- and little-endian builds, and fault injection for bad userspace pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/configs.c -->
# sources/distributed-fs/ceph-client/kernel/configs.c

## Purpose

`configs.c` embeds the compressed kernel build configuration into the kernel image and, when enabled, exposes it as `/proc/config.gz`.

## Important APIs, Types, and Functions

The file declares an assembly block containing `IKCFG_ST`, `kernel_config_data`, an `.incbin` of `kernel/config_data.gz`, `kernel_config_data_end`, and `IKCFG_ED`. When `CONFIG_IKCONFIG_PROC` is set, it defines `ikconfig_read_current()`, `config_gz_proc_ops`, `ikconfig_init()`, and `ikconfig_cleanup()`.

## Control Flow and State

The embedded config is static read-only data. Module init creates `/proc/config.gz`, points reads at the embedded byte range through `simple_read_from_buffer()`, and sets the proc entry size to the compressed config length. Module exit removes the proc entry.

## Dependencies and Integration Points

It depends on the build system producing `kernel/config_data.gz`, procfs, seq/read helpers, module init/exit, and `scripts/extract-ikconfig`, which looks for the `IKCFG_ST` and `IKCFG_ED` markers in binaries.

## Risks and Edge Cases

If the generated `kernel/config_data.gz` artifact is missing, the assembly include fails at build time. Runtime risk is low; proc entry creation can fail with `-ENOMEM`. Access is read-only, and the embedded data size is determined by linker symbols.

## Test Signals

Tests should build with and without `CONFIG_IKCONFIG_PROC`, verify `/proc/config.gz` exists only when configured, compare decompressed output to the build `.config`, run `scripts/extract-ikconfig` on the image/module, and test partial reads and seeks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/configs.c -->
