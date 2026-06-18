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
