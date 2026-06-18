# sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-v1.c

## Purpose

`cgroup-v1.c` implements legacy cgroup v1 behavior on top of the common cgroup core: v1 task migration helpers, sorted `tasks` and `cgroup.procs` seq_file output, writes to those files, base v1 control files, `/proc/cgroups`, taskstats cgroup summaries, release-agent execution, v1 kernfs syscall operations, mount option parsing, root selection/creation, remount handling, and boot parameters that disable v1 controllers or alter `/proc/cgroups` output.

## Important APIs, types, and functions

- Global v1 policy state: `cgroup_no_v1_mask`, `cgroup_no_v1_named`, and `proc_show_all`, set by `cgroup_no_v1=` and `cgroup_v1_proc=` boot parameters.
- `cgroup1_ssid_disabled()` and `cgroup1_subsys_absent()` decide whether a controller is available to v1 mounts or `/proc/cgroups`.
- `cgroup_attach_task_all()` attaches a task to the same cgroups as another task across every hierarchy.
- `cgroup_transfer_tasks()` migrates all tasks from one v1 cgroup to another using a `cgroup_mgctx`.
- `struct cgroup_pidlist` caches sorted pid arrays per cgroup, file type, and PID namespace.
- `cgroup1_pidlist_destroy_all()` and `cgroup_pidlist_destroy_work_fn()` flush and destroy delayed pidlist caches.
- `pidlist_array_load()`, `cgroup_pidlist_start()`, `next()`, `stop()`, and `show()` implement v1 `tasks`/`cgroup.procs` seq_file reads.
- `__cgroup1_procs_write()`, `cgroup1_procs_write()`, and `cgroup1_tasks_write()` parse task IDs through common helpers, check open-time credentials, and attach a process or single thread.
- `cgroup1_base_files[]` defines `cgroup.procs`, `cgroup.clone_children`, `cgroup.sane_behavior`, `tasks`, `notify_on_release`, and `release_agent`.
- `proc_cgroupstats_show()` implements `/proc/cgroups`.
- `cgroupstats_build()` fills taskstats counts by task state for a cgroup directory.
- `cgroup1_check_for_release()` and `cgroup1_release_agent()` schedule and run the configured release agent for empty releasable cgroups.
- `cgroup1_parse_param()`, `check_cgroupfs_options()`, `cgroup1_root_to_use()`, `cgroup1_get_tree()`, and `cgroup1_reconfigure()` implement v1 mount and remount semantics.
- `cgroup1_kf_syscall_ops` binds v1 rename, mount option display, mkdir, rmdir, and path display to kernfs.
- `task_get_cgroup1()` finds and references a task's cgroup in a specific v1 hierarchy ID.

## Control flow

Task migration starts by taking cgroup and attach locks. `cgroup_transfer_tasks()` validates the destination, marks every css_set linked from the source as a migration source, prepares destination css_sets, then repeatedly finds a non-exiting task in the source and calls `cgroup_migrate()` until the source is empty or a controller rejects the attach. The migration context is always finished and locks are dropped on exit.

Reading `tasks` or `cgroup.procs` uses a cached pidlist. `start()` locks `cgrp->pidlist_mutex`, reuses a matching list if still present, or calls `pidlist_array_load()` to count tasks, allocate a pid array, iterate tasks, select TGIDs for `cgroup.procs` or PIDs for `tasks`, sort, deduplicate, and store the list. The seq position is the last emitted PID, so `start()` binary-searches for the next PID after seeks or partial reads. `stop()` schedules delayed destruction to keep consecutive reads cheap.

Writing `tasks` or `cgroup.procs` locks the live cgroup kernfs node, parses the target task through `cgroup_procs_write_start()`, checks permissions using `of->file->f_cred` against the target's real and saved UID unless the opener is global root, then calls `cgroup_attach_task()` for either the whole thread group or a single thread.

Mount flow parses options into `cgroup_fs_context`, validates enabled and disabled controllers, defaults to `all` when no name/subsystem/none option is supplied, rejects invalid combinations, then either finds an existing compatible root or creates a new root in the initial cgroup namespace. `cgroup1_get_tree()` requires `CAP_SYS_ADMIN` in the cgroup namespace user namespace and restarts if a matching root is still dying. Remount validates option compatibility, rejects populated hierarchy controller changes, rebinds added controllers from the default root, moves removed controllers back, and updates `release_agent` if requested.

Release notification checks that `notify_on_release` is set, the cgroup is unpopulated, has no online children, and is not dead. The work item copies the release-agent path under spinlock, computes the cgroup path in the initial cgroup namespace, and invokes userspace with a minimal environment via `call_usermodehelper(..., UMH_WAIT_EXEC)`.

## State and persistence behavior

Most state is in cgroup core objects. V1-specific persistent root state includes subsystem masks, root flags, hierarchy names, `release_agent_path`, root cgroup flags such as `CGRP_NOTIFY_ON_RELEASE` and `CGRP_CPUSET_CLONE_CHILDREN`, and boot-time v1 disable masks. Pidlists are transient cached arrays keyed by cgroup, file type, and PID namespace; they are delayed-destroyed after reads and flushed when a cgroup is destroyed. Release-agent work is asynchronous kernel work and may outlive the condition that scheduled it, so the user command must tolerate failed removal.

## Dependencies and integration points

The file depends on the private cgroup header, kernfs, PID namespaces, task iteration, sorting, vmalloc/kvmalloc helpers, kmod usermode helper execution, fs parser APIs, taskstats, and cgroup tracepoints. It calls common cgroup core functions for locking, root setup, controller rebinding, migration, task attachment, cgroup path formatting, mkdir/rmdir, and kernfs tree creation. Capability integration appears in mount permission checks and release-agent writes (`ns_capable()`, `capable()`, `file_ns_capable()`).

## Risks and edge cases

- Pidlist caching is performance-sensitive and namespace-sensitive. A stale cached list is acceptable for read consistency across a seq_file read, but destruction must not race with reuse; `pidlist_mutex` and delayed work ordering are central.
- `pidlist_uniq()` assumes sorted input. Calling it on unsorted arrays would silently keep duplicates.
- Permission checks for `tasks`/`cgroup.procs` intentionally use file-open credentials to prevent inherited-fd privilege changes. Changing to current credentials would be a security regression.
- Release agents execute with full capabilities, so setting `release_agent` is restricted to init user namespace and `CAP_SYS_ADMIN`. Any relaxation is high risk.
- Remount controller changes are deprecated and rejected for populated hierarchies, but still supported for empty ones; rebinding failures must leave controllers consistent.
- `cgroup1_root_to_use()` returns positive values to request syscall restart while roots are dying. Callers must preserve this convention.
- Named hierarchy creation is blocked outside the initial cgroup namespace and can be disabled globally by `cgroup_no_v1=named`.
- Rename forbids newline and only permits same-parent directory renames to keep `/proc/<pid>/cgroup` parseable and avoid cross-parent moves.

## Test signals

High-value tests include v1 mount option matrices (`all`, `none`, named hierarchies, disabled controllers, `noprefix`, release agents, cpuset modes), remount attempts on empty and populated hierarchies, boot parameters `cgroup_no_v1=all,named,<controller>` and `cgroup_v1_proc=`, concurrent task migration with forking, `tasks` and `cgroup.procs` reads across PID namespaces and large cgroups, partial seq_file reads and seeks, pidlist delayed destruction and cgroup teardown flushes, write permission checks with inherited file descriptors, release-agent scheduling and empty-agent behavior, `/proc/cgroups` visibility rules, and taskstats state counting.
