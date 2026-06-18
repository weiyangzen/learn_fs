# Research: subset-b-006023

Grouped research for:

- `sources/distributed-fs/ceph-client/kernel/cgroup/cgroup.c`
- `sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-internal.h`
- `sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-v1.c`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cgroup.c -->
# `sources/distributed-fs/ceph-client/kernel/cgroup/cgroup.c`

## Purpose

`cgroup.c` is the Linux cgroup core implementation. It owns hierarchy roots, cgroup directories, subsystem state (`struct cgroup_subsys_state`, or css) lifetime, task-to-cgroup membership through `struct css_set`, cgroup v2 controller enable/disable transactions, process/thread migration via `cgroup.procs` and `cgroup.threads`, filesystem mounting for `cgroup`, `cgroup2`, and legacy `cpuset`, and boot-time registration of cgroup subsystems. It is the coordination layer between kernfs, scheduler/task lifecycle, namespaces, PSI, BPF cgroup storage/hooks, controller-specific callbacks, and legacy cgroup v1 support in `cgroup-v1.c`.

The file implements both persistent kernel state for cgroup hierarchies and transient operations that modify that state. User-visible persistence is kernfs-backed cgroup directories and files; internal persistence is kept in global roots, css IDRs, reference-counted css objects, css_sets, task lists, and delayed destruction workqueues.

## Important APIs, Types, and Globals

- `cgroup_mutex` is the master hierarchy mutation lock. `css_set_lock` protects task membership, css_set lists, task lists, and populated counters.
- `cgrp_dfl_root` is the always-present cgroup v2 root. `cgroup_roots`, `cgroup_root_count`, and `cgroup_hierarchy_idr` track all mounted hierarchies.
- `cgroup_subsys[]`, `cgroup_subsys_name[]`, and per-subsystem static keys are generated from `<linux/cgroup_subsys.h>`.
- `init_css_set` is the initial `css_set` for init and early tasks. `css_set_table` hashes css pointer vectors to share identical cgroup memberships.
- `cgroup_offline_wq`, `cgroup_release_wq`, and `cgroup_free_wq` separate css offlining, release, and final free work to avoid serialized workqueue deadlocks in teardown.
- Exported helpers include `cgroup_get_e_css()`, `of_css()`, `cgroup_path_ns()`, `cgroup_file_notify()`, descendant iterators such as `css_next_descendant_pre()`, task iterators such as `css_task_iter_start()/next()/end()`, `cgroup_get_from_id()`, `cgroup_get_from_path()`, `cgroup_get_from_fd()`, and `cgroup_parse_float()`.
- Filesystem types: `cgroup_fs_type` for v1, private `cgroup2_fs_type` for v2, and optional `cpuset_fs_type` compatibility mount when `CONFIG_CPUSETS_V1` is enabled.
- Core v2 interface files are declared in `cgroup_base_files[]`: `cgroup.type`, `cgroup.procs`, `cgroup.threads`, `cgroup.controllers`, `cgroup.subtree_control`, `cgroup.events`, hierarchy limit files, stats, freezer, kill, and CPU stat files. PSI files are declared separately in `cgroup_psi_files[]`.

## Control Flow and Lifecycle

Boot starts in `cgroup_init_early()`, which initializes the default root, attaches `init_task` to `init_css_set`, assigns subsystem IDs/names, and initializes early subsystems. `cgroup_init()` then initializes cftype tables, rstat, the init namespace, BPF lifetime notifiers, the default root kernfs tree, late subsystems, cftypes, filesystem registration, `/proc/cgroups`, and optional `cpuset` compatibility filesystem registration. `cgroup_wq_init()` creates the three teardown workqueues after workqueues are available.

Mounting uses fs-context operations. `cgroup_init_fs_context()` allocates `struct cgroup_fs_context`, binds the current cgroup namespace and user namespace, and selects v1 or v2 operations. `cgroup_get_tree()` exposes the default root and applies v2 root flags such as `nsdelegate`, `favordynmods`, and memory/pids behavior flags. `cgroup1_get_tree()` and v1 parsing are delegated to the cgroup v1 companion code. `cgroup_do_get_tree()` calls kernfs and, inside non-init cgroup namespaces, replaces the returned dentry with the namespace root cgroup's dentry.

Creating a cgroup goes through `cgroup_mkdir()`: reject newline names, lock the live parent through `cgroup_kn_lock_live()`, check `cgroup.max.descendants` and `cgroup.max.depth`, allocate and initialize the cgroup in `cgroup_create()`, populate core files, apply enabled controller csses, trace the mkdir, and activate kernfs. `cgroup_create()` sets ancestor arrays, freezer inherited state, cgroup1 flags like notify-on-release and cpuset clone-children, lifetime notifiers, descendant counters, parent refs, and initial subtree control masks.

Removing a cgroup goes through `cgroup_rmdir()` and `cgroup_destroy_locked()`. Destruction first verifies no user-visible task and no online child remains, marks the cgroup/css_sets dead, calls the synchronous half of css teardown (`kill_css_sync()`), removes interface files and the kernfs directory, updates descendant and frozen-descendant counters, emits lifetime notifications, kills the self ref, and either finishes immediately or waits for the populated subtree to drain. `cgroup_finish_destroy()` starts `kill_css_finish()` for subsystem csses. Final css teardown follows `percpu_ref_kill_and_confirm()` to `css_killed_ref_fn()`, `css_killed_work_fn()`, `offline_css()`, `css_release_work_fn()`, and finally `css_free_rwork_fn()` after an RCU grace period.

Controller changes in cgroup v2 are transactional. `cgroup_subtree_control_write()` parses `+controller`/`-controller` tokens, validates availability and child use, vets domain/threaded constraints, saves old masks, updates `subtree_control`, applies the new state, and finalizes. The transaction runs through `cgroup_save_control()`, `cgroup_propagate_control()`, `cgroup_apply_control_enable()` to create or show csses, `cgroup_update_dfl_csses()` to migrate tasks to css_sets matching new effective css associations, and `cgroup_finalize_control()` to restore on failure and hide/kill obsolete csses through `cgroup_apply_control_disable()`.

Task migration flows through `cgroup.procs`, `cgroup.threads`, and `CLONE_INTO_CGROUP`. `__cgroup_procs_write()` locks the destination cgroup, parses and pins the target task in `cgroup_procs_write_start()`, validates source/destination permissions and v2 domain rules, calls `cgroup_attach_task()`, then releases attach locks and task refs. `cgroup_attach_task()` builds a migration context: source css_sets are preloaded with `cgroup_migrate_add_src()`, destinations are found or created by `cgroup_migrate_prepare_dst()`, tasks are moved into `mg_tasks`, controllers run `can_attach`, commit moves happen under `css_set_lock`, and controllers run `attach` after the commit. Failure before commit calls earlier `cancel_attach` hooks and restores task lists.

Fork and exit integration is split across scheduler/process hooks. `cgroup_fork()` initializes child fields to `init_css_set`. `cgroup_can_fork()` prepares the child's css_set with `cgroup_css_set_fork()`, including optional `CLONE_INTO_CGROUP` file descriptor validation and permission checks, then runs subsystem `can_fork` callbacks. `cgroup_post_fork()` links the child into the selected css_set, applies freezer/kill sequencing, runs subsystem `fork` callbacks, and updates `CLONE_NEWCGROUP` namespace root css_set. Exit paths run subsystem `exit`, move dead tasks out of live task lists in `do_cgroup_task_dead()`, handle PREEMPT_RT deferred dead-task work, run `release` callbacks, and drop final css_set refs in `cgroup_task_free()`.

## State and Persistence Behavior

Hierarchy state is rooted in `struct cgroup_root`, with one `struct cgroup` root and a kernfs root. Non-root cgroups are allocated dynamically, referenced by their self css refcount, parent refs, kernfs refs, and links from css_sets. Controller css state is per cgroup/subsystem and identified in each subsystem's `css_idr`; IDs are allocated with `cgroup_idr_lock` so release can occur without `cgroup_mutex`.

Task membership persists in `task->cgroups` pointing to a reference-counted `css_set`. A css_set is a vector of effective css pointers plus links to one cgroup per hierarchy. Identical membership vectors are shared through `css_set_table`, and each css_set tracks normal tasks, migration tasks, dying tasks, threaded css_sets, and in-flight iterators. Populated state is derived from css_set task lists and propagated through cgroup counters to drive `cgroup.events` notifications and deferred destruction.

The default hierarchy stores visible controller availability in `subtree_control` and effective availability in `subtree_ss_mask`. `old_subtree_control`, `old_subtree_ss_mask`, and `old_dom_cgrp` are transaction rollback fields. Threaded subtree state is represented by `dom_cgrp`, `nr_threaded_children`, and domain validity helpers.

User-visible cgroup state persists while kernfs nodes and cgroup refs exist. Dying cgroups can remain after rmdir until references, dying tasks, and RCU readers drain. `/proc/<pid>/cgroup` appends ` (deleted)` for dead v2 cgroups still referenced by zombies. cgroup namespace boundaries affect visible paths through `cgroup_path_ns_locked()` and mount-root substitution.

## Dependencies and Integration Points

- kernfs provides directory/file creation, active protection, polling/notification, mount tree integration, path lookup, and syscall hooks.
- cgroup v1 code supplies legacy mount parsing, legacy base files, release-agent behavior, pidlist destruction, and v1 release checks.
- Subsystems supply `css_alloc/free/online/offline/killed/released/reset`, fork/exit/release/can_fork/can_attach/attach/cancel_attach, cftype arrays, rstat flushers, and bind callbacks.
- Scheduler/task code integrates through fork/exit hooks, `cgroup_threadgroup_rwsem`, `cpus_read_lock()`, freezer helpers, deadline task accounting, and CPU stat display.
- PSI integration provides pressure files and triggers, hidden/shown by `cgroup.pressure`.
- BPF integration uses cgroup lifetime notifier initialization and storage cleanup plus socket cgroup data helpers under `CONFIG_SOCK_CGROUP_DATA`.
- Namespace integration uses `struct cgroup_namespace`, user namespaces, `nsdelegate`, `/proc/<pid>/cgroup`, fd/path/id lookup restrictions, and `CLONE_NEWCGROUP`.
- Optional cpuset compatibility is handled by the `cpuset` filesystem shim, which mounts cgroup v1 with the cpuset subsystem, no prefixes, and a default release agent.

## Risks and Edge Cases

- Lock ordering is critical. Attach paths deliberately take `cpus_read_lock()` before global or per-threadgroup cgroup rwsems to avoid CPU-hotplug deadlocks with controller attach hooks.
- Controller enable/disable is transactional but not fully undoing all intermediate css creation on early failure; `cgroup_finalize_control()` handles rollback masks and subsequent disable/hide/kill cleanup.
- css teardown is intentionally asynchronous. Re-enabling controllers must drain offlined csses with `cgroup_lock_and_drain_offline()` to avoid racing old dying css instances.
- Namespace delegation checks must use file-open credentials to avoid inherited-fd attacks and must reject non-delegatable writes at namespace roots.
- css/task iterators are vulnerable to concurrent task movement; the iterator registration and skip logic is essential and should be preserved in any refactor.
- `CLONE_INTO_CGROUP` must reject dead cgroups, invalid descriptors, cgroup.procs descriptors, and disallowed migrations before the child is exposed.
- cgroup destruction waits for kernel-internal dying tasks even after user-visible `cgroup.procs` is empty, because hidden exiting tasks can still consume resources.
- Workqueue separation exists to avoid teardown deadlocks; merging these queues or increasing assumptions about order can regress unmount/destruction behavior.
- Socket allocation falls back to the default cgroup in interrupt context to avoid associating sockets with unrelated interrupted tasks.

## Test Signals

- Boot with early and non-early cgroup subsystems, verify `/proc/cgroups`, sysfs `kernel/cgroup/{delegate,features}`, and cgroup2 mount behavior.
- Mount/remount cgroup2 with `nsdelegate`, `favordynmods`, `memory_localevents`, `memory_recursiveprot`, `memory_hugetlb_accounting`, and `pids_localevents`; verify option display and behavior.
- Exercise cgroup v2 controller enable/disable, including dependency controllers, threaded controllers, domain controllers, failure rollback, and re-enable after asynchronous css teardown.
- Move processes and individual threads through `cgroup.procs` and `cgroup.threads`; cover permission failures, namespace delegation boundaries, no-internal-process rules, threaded subtree restrictions, and `PF_NO_SETAFFINITY` rejection.
- Create/destroy cgroups under active fork/exit load and verify `cgroup.events`, `cgroup.stat`, `nr_dying_*` counters, and no use-after-free under RCU/KASAN/KCSAN.
- Test `cgroup.max.descendants`, `cgroup.max.depth`, newline name rejection, and rmdir on cgroups with live children, visible tasks, and hidden dying tasks.
- Validate freezer and `cgroup.kill` behavior for v2 domain versus threaded cgroups.
- Run `CLONE_INTO_CGROUP` tests for O_PATH cgroup directory fds, invalid fds, dead cgroups, permission checks, and cgroup kill sequence races.
- Exercise PSI pressure triggers and `cgroup.pressure` show/hide behavior when `CONFIG_PSI` is enabled, including irq pressure when configured.
- With `CONFIG_PREEMPT_RT`, verify deferred dead-task handling through irq work does not leak task refs or cgroup refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-internal.h -->
# `sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-internal.h`

## Purpose

`cpuset-internal.h` is the private shared header for the cpuset controller implementation. It defines the central `struct cpuset`, shared enums for flags and cgroup file types, helpers for converting between css/task/cpuset objects, traversal macros over online cpuset children and descendants, and the internal API boundary between common cpuset code and the legacy v1-specific implementation in `cpuset-v1.c`.

The header is not a standalone module; it is the contract used by `cpuset.c` and `cpuset-v1.c` to keep cgroup css state, CPU masks, memory-node masks, partition state, deadline accounting, and legacy knobs consistent.

## Important APIs, Types, and Globals

- `struct fmeter` stores the legacy memory-pressure low-pass filter state: pending count, current value, timestamp, and spinlock.
- `enum prs_errcode` enumerates partition-root validation failures such as invalid CPUs, invalid parent, not exclusive, no CPUs, hotplug, empty CPU set, housekeeping violation, access failure, and remote partition errors.
- `cpuset_flagbits_t` defines bits stored in `struct cpuset::flags`: CPU/memory exclusivity, memory hardwall, memory migration, scheduler load balancing, page spread, and slab spread.
- `cpuset_filetype_t` assigns identifiers for all cpuset files handled by shared or v1 code, including CPU/mem lists, effective masks, partition files, exclusivity flags, scheduler relax level, memory pressure, and spread flags.
- `struct cpuset` embeds `struct cgroup_subsys_state css` and contains configured masks (`cpus_allowed`, `mems_allowed`), effective masks, default-hierarchy exclusive CPU masks, old memory mask, attach tracking, partition state, remote partition flag, SCHED_DEADLINE migration accounting, partition file handle, and v1-only fields.
- `top_cpuset` is declared as the root cpuset object, defined in `cpuset.c`.
- Inline accessors: `css_cs()`, `task_cs()`, `parent_cs()`, `is_cpuset_online()`, and flag tests like `is_cpu_exclusive()`, `is_memory_migrate()`, `is_spread_page()`.
- Iteration helpers: `cpuset_for_each_child()` and `cpuset_for_each_descendant_pre()` wrap css iterators and filter to online cpusets under RCU.
- Common cpuset API declarations include `rebuild_sched_domains_locked()`, callback lock helpers, task CPU/memory mask update helpers, `cpuset_update_flag()`, `cpuset_write_resmask()`, `cpuset_common_seq_show()`, and full lock/unlock helpers.
- Under `CONFIG_CPUSETS_V1`, v1 APIs and `cpuset1_files[]` are declared. Without v1 support, static inline no-op or success stubs preserve common code call sites.

## Control Flow and State Model

The core state model distinguishes configured and effective masks. In cgroup v2/default hierarchy, `cpuset.cpus` and `cpuset.mems` are user-configured and are not automatically constrained by the parent. Effective masks are the masks actually applied to tasks, derived from configured masks and ancestors, inheriting parent masks if intersection becomes empty. In legacy hierarchy, configured masks and effective masks are always the same.

Default hierarchy partitioning adds `exclusive_cpus` and `effective_xcpus`. `exclusive_cpus` is user-requested capacity that can be granted to a partition root or descendants; `effective_xcpus` is the granted set after ancestor and sibling constraints. For a valid partition root, `effective_cpus` comes from `effective_xcpus` minus CPUs handed to subpartitions, not necessarily from `cpus_allowed`.

`old_mems_allowed` records the previous memory-node set used for migration when `cpuset.mems` changes. `attach_in_progress` keeps a cpuset considered populated between `can_attach` and `attach`, avoiding transitions to empty CPU/memory masks while a task is entering. Deadline fields track attached and migrating SCHED_DEADLINE tasks and reserved bandwidth during cpuset attachment.

The v1-only block adds `fmeter`, `relax_domain_level`, and a union-find node used by legacy sched-domain generation. This keeps legacy memory pressure and custom load-balancing domain behavior out of builds without `CONFIG_CPUSETS_V1`.

## Dependencies and Integration Points

- Includes cgroup core definitions, CPU and cpumask APIs, cpuset public APIs, spinlocks, union-find, and scheduler isolation/housekeeping definitions.
- Relies on cgroup css helpers such as `task_css()`, `css_is_online()`, `css_is_dying()`, `css_for_each_child()`, `css_for_each_descendant_pre()`, and `css_rightmost_descendant()`.
- Common code in `cpuset.c` implements the declared shared functions and uses the v1 stubs/hooks to compile the same logic with or without legacy support.
- `cpuset-v1.c` implements the v1 declarations, including legacy file table registration through `cpuset1_files[]`.
- Scheduler integration runs through sched-domain rebuild declarations, load balance flags, relax-domain level, housekeeping CPU masks, and SCHED_DEADLINE accounting fields.
- Memory management integration uses nodemasks, old memory masks, memory migration, hardwall/exclusive flags, and page/slab spread flags.

## Risks and Edge Cases

- The configured/effective mask distinction differs sharply between v1 and v2. Code that assumes `cpus_allowed == effective_cpus` is only valid for legacy mode or selected top-level cases.
- `attach_in_progress` is part of population semantics; ignoring it can permit an invalid empty cpuset while a task is being attached.
- Online traversal macros require RCU read locking and filter through `is_cpuset_online()`. Missing RCU coverage risks seeing dying css state.
- Partition state is partly not lock-protected (`prs_err` is explicitly called out), so readers must tolerate transient status.
- The v1 stubs deliberately return success/no-op when `CONFIG_CPUSETS_V1` is off. Callers must not depend on v1 side effects in non-v1 builds.
- The union-find node is embedded in `struct cpuset`, so sched-domain generation must not run concurrently in a way that reuses the same nodes without the cpuset lock.

## Test Signals

- Build with and without `CONFIG_CPUSETS_V1` to verify the stub boundary and v1 field use.
- Validate cpuset v2 mask inheritance, empty configured masks, parent hotplug propagation, and partition-root transitions.
- Validate legacy mode keeps configured/effective masks identical and exposes v1-only files.
- Exercise task attach while changing cpuset masks to ensure `attach_in_progress` prevents invalid empty transitions.
- Exercise RCU traversal under concurrent cpuset creation/removal with lockdep and KASAN/KCSAN.
- Cover SCHED_DEADLINE attach/migration accounting and sched-domain rebuild triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-v1.c -->
# `sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-v1.c`

## Purpose

`cpuset-v1.c` implements legacy cgroup v1 cpuset behavior that is not shared with the default hierarchy. It provides v1-only memory pressure accounting, deprecated legacy file read/write handlers, legacy validation rules, hotplug evacuation of empty cpusets, clone-children inheritance, custom scheduler-domain generation, `/proc/<pid>/cpuset`, and the `cpuset1_files[]` cftype table consumed by the cpuset subsystem's legacy cftypes.

The file is compiled only when `CONFIG_CPUSETS_V1` is enabled and is explicitly separated from common cpuset code so modern v2 behavior can avoid legacy API and semantic baggage.

## Important APIs and Functions

- `struct cpuset_remove_tasks_struct` carries asynchronous work for moving tasks out of an empty legacy cpuset after hotplug.
- Frequency-meter helpers `fmeter_init()`, `fmeter_update()`, `fmeter_markevent()`, and `fmeter_getrate()` implement a scaled integer IIR low-pass filter for legacy `memory_pressure`.
- `cpuset_memory_pressure_enabled` globally gates memory-pressure event collection. `__cpuset_memory_pressure_bump()` marks a reclaim event on the current task's cpuset.
- `update_relax_domain_level()` validates and applies `sched_relax_domain_level`, rebuilding sched domains when needed.
- `cpuset_write_s64()` and `cpuset_read_s64()` handle signed legacy files, currently `sched_relax_domain_level`.
- `cpuset1_update_task_spread_flags()` and `cpuset1_update_tasks_flags()` apply legacy page/slab spread flags to tasks.
- `cpuset1_hotplug_update_tasks()` updates masks on CPU/memory hotplug and schedules asynchronous migration when a cpuset becomes empty.
- `cpuset1_validate_change()` enforces v1 subset and non-empty-populated constraints.
- `cpuset1_cpus_excl_conflict()` checks sibling CPU exclusivity conflicts.
- Optional `proc_cpuset_show()` renders `/proc/<pid>/cpuset`.
- `cpuset_read_u64()` and `cpuset_write_u64()` implement legacy boolean/stat files such as `cpu_exclusive`, `mem_exclusive`, `mem_hardwall`, `sched_load_balance`, `memory_migrate`, `memory_pressure_enabled`, and spread flags.
- `cpuset1_init()` initializes v1 fields, and `cpuset1_online_css()` inherits spread flags or clones parent masks when `CGRP_CPUSET_CLONE_CHILDREN` is set.
- `cpuset1_generate_sched_domains()` builds scheduler load-balancing domains from legacy load-balanced cpusets, using union-find to merge overlapping CPU masks.
- `cpuset1_files[]` declares the legacy cpuset cgroup files: `cpus`, `mems`, effective masks, exclusivity flags, scheduler knobs, memory migration/pressure, spread flags, and root-only `memory_pressure_enabled`.

## Control Flow and Behavior

Memory pressure starts with the global `cpuset_memory_pressure_enabled` knob. When enabled, reclaim paths call `__cpuset_memory_pressure_bump()`, which RCU-locks, finds `task_cs(current)`, and increments that cpuset's `fmeter`. Reads of `memory_pressure` call `fmeter_getrate()`, which updates elapsed ticks, decays the previous value by `FM_COEF`, folds in pending events, and returns a scaled recent rate.

Legacy file writes route through cgroup cftype operations. Boolean writes use `cpuset_write_u64()`, which takes `cpuset_full_lock()`, rejects offline cpusets, dispatches to `cpuset_update_flag()` for most flags, and emits one-time deprecation messages for obsolete v1 knobs. `memory_pressure_enabled` is root-only and directly updates the global gate. Signed writes use `cpuset_write_s64()` for `sched_relax_domain_level`; a value change can trigger `rebuild_sched_domains_locked()` when the cpuset has CPUs and load balancing is enabled.

Hotplug updates in `cpuset1_hotplug_update_tasks()` copy new CPU/memory masks into both configured and effective masks under the callback lock, then updates existing task CPU and memory masks if the cpuset remains non-empty. If CPUs or memory nodes become empty and the cgroup has populated css_sets, the code takes a live css ref and schedules `cpuset_migrate_tasks_workfn()`. The worker finds the nearest ancestor with non-empty CPU and memory masks and calls `cgroup_transfer_tasks()` to evacuate tasks asynchronously, avoiding a full cgroup migration from inside the hotplug update path.

Validation in `cpuset1_validate_change()` is legacy-specific: children must remain subsets of the trial cpuset, the trial cpuset must remain a subset of its parent, and populated cpusets cannot transition from non-empty CPU or memory masks to empty masks. The helper `is_cpuset_subset()` includes CPU and memory masks plus exclusivity flag constraints.

When a new legacy cpuset css comes online, `cpuset1_online_css()` inherits parent spread flags. If the cgroup has `CGRP_CPUSET_CLONE_CHILDREN`, it refuses to clone when siblings have CPU or memory exclusivity; otherwise it copies the parent's CPU and memory masks into both configured and effective masks under the callback lock.

Legacy sched-domain generation has a fast path: if `top_cpuset` is load-balanced, return one domain covering top effective CPUs intersected with housekeeping CPUs and aggregate relax-domain attributes over the tree. Otherwise, it walks descendants under RCU, collects relevant load-balanced cpusets, initializes their embedded union-find nodes, merges overlapping effective CPU masks, allocates one sched-domain mask per disjoint merged set, intersects with `housekeeping_cpumask(HK_TYPE_DOMAIN)`, and computes per-domain relax attributes from descendant load-balanced cpusets. Allocation failure falls back to the scheduler default-domain behavior by returning `ndoms = 1` with `domains == NULL`.

## State and Persistence Behavior

Per-cpuset legacy state lives in v1-only fields of `struct cpuset`: `fmeter`, `relax_domain_level`, and the union-find node. The memory pressure enable flag is global, not per hierarchy. File values are persistent kernel state while the cpuset css exists and are exposed through kernfs files created from `cpuset1_files[]`.

Hotplug mask updates mutate both configured and effective masks because legacy semantics do not separate them. Empty legacy cpusets are not allowed to keep tasks; task evacuation is deferred to a workqueue while a css reference keeps the cpuset alive. Spread flags are stored as bits in the shared `flags` field but only have v1 task flag side effects when the cpuset subsystem is not on the default hierarchy.

Scheduler-domain generation temporarily mutates each collected cpuset's embedded union-find node. That state is scratch space protected by the cpuset lock and should not be treated as persistent topology.

## Dependencies and Integration Points

- Includes `cgroup-internal.h` and `cpuset-internal.h`, using cgroup migration helpers, css/task iteration, path helpers, and cpuset shared locks.
- Relies on common cpuset code for `cpuset_update_flag()`, `cpuset_write_resmask()`, `cpuset_common_seq_show()`, task CPU/memory updates, callback locks, full locks, `top_cpuset`, and sched-domain rebuild entry points.
- Interacts with scheduler topology through `alloc_sched_domains()`, `struct sched_domain_attr`, `SD_ATTR_INIT`, `partition_sched_domains()` expectations, `sched_domain_level_max`, load-balance flags, and housekeeping CPU masks.
- Interacts with `/proc` through `proc_cpuset_show()` under `CONFIG_PROC_PID_CPUSET`.
- Uses cgroup core task migration (`cgroup_transfer_tasks()`), css references (`css_tryget_online()`, `css_put()`), and cgroup path rendering with namespace awareness.
- Uses task spread flag helpers for legacy page and slab spreading.

## Risks and Edge Cases

- `__cpuset_memory_pressure_bump()` assumes the current task has a valid cpuset under RCU; incorrect call sites outside task context would be unsafe.
- The frequency meter uses intentionally bounded integer arithmetic. Changes to scale, max tick, or max count can overflow or alter legacy ABI-visible values.
- Hotplug evacuation is asynchronous. Failures in `cgroup_transfer_tasks()` are logged but not retried here, so tests should cover failure handling and ensure css refs are always dropped.
- `cpuset1_hotplug_update_tasks()` skips direct task mask updates when the cpuset becomes empty because tasks should move to an ancestor. If evacuation fails, tasks may temporarily remain in an empty cpuset.
- `cpuset1_online_css()` clone-children behavior silently returns without cloning when siblings are exclusive. This is historical API behavior and can surprise callers expecting inheritance.
- `cpuset1_generate_sched_domains()` uses embedded union-find nodes and RCU traversal while depending on external cpuset lock serialization. Concurrent generation without the lock would corrupt scratch state.
- Deprecated v1 files still trigger real side effects; deprecation messages should not be confused with no-op behavior.
- The v1 file table uses unprefixed legacy names when mounted through the `cpuset` compatibility filesystem because cgroup core sets `CGRP_ROOT_NOPREFIX`.

## Test Signals

- Read/write every file in `cpuset1_files[]`, including invalid booleans, invalid `sched_relax_domain_level`, max write lengths for CPU/node lists, and root-only `memory_pressure_enabled`.
- Enable memory pressure, trigger direct reclaim in a cpuset, and verify `memory_pressure` decays over time and saturates safely under high event rates.
- CPU and memory hotplug tests where legacy cpusets lose CPUs/nodes, including populated cpusets that must evacuate tasks to the nearest non-empty ancestor.
- Validate v1 subset rules: child masks must stay within parent masks, populated cpusets cannot become empty, and exclusive siblings cannot overlap.
- Test clone-children inheritance with and without exclusive siblings.
- Exercise `memory_spread_page` and `memory_spread_slab` writes and confirm task flags update for existing and newly attached tasks in legacy mode.
- Generate sched domains for top-load-balanced, disjoint load-balanced, overlapping load-balanced, empty CPU, and housekeeping-excluded CPU cases.
- Verify `/proc/<pid>/cpuset` path output with cgroup namespaces and long paths when `CONFIG_PROC_PID_CPUSET` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cpuset-v1.c -->
