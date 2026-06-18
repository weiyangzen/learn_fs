# subset-b-006022 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/capability.c -->
# sources/distributed-fs/ceph-client/kernel/capability.c

## Purpose

`capability.c` implements the kernel capability syscall surface and common capability-check helpers. It translates legacy userspace capability ABI versions into `kernel_cap_t`, delegates policy decisions to the Linux Security Module hooks, updates process credentials through the normal copy-on-write credential path, and exports capability predicates used by filesystem, ptrace, namespace, and general kernel authorization code.

The file is not Ceph-specific despite its repository path; it is generic Linux kernel privilege plumbing. It also owns the `no_file_caps` boot setup switch through the global `file_caps_enabled`.

## Important APIs, types, and functions

- `file_caps_enabled` is initialized to enabled and can be cleared by `file_caps_disable()` via `__setup("no_file_caps", ...)`.
- `cap_validate_magic()` validates `_LINUX_CAPABILITY_VERSION_1`, `_VERSION_2`, and `_VERSION_3`, returns the number of 32-bit words userspace expects, warns once for legacy/deprecated ABI use, and writes `_KERNEL_CAPABILITY_VERSION` back for unknown versions.
- `SYSCALL_DEFINE2(capget)` reads `header->pid`, calls `cap_get_target_pid()`, splits effective/permitted/inheritable `kernel_cap_t` values into legacy 32-bit user fields, and copies only the ABI-requested word count.
- `SYSCALL_DEFINE2(capset)` accepts only the current task, copies user capability data, masks it with `CAP_VALID_MASK` through `mk_kernel_cap()`, creates new credentials with `prepare_creds()`, validates and applies them through `security_capset()`, audits, and commits or aborts.
- `has_ns_capability()`, `has_ns_capability_noaudit()`, and `has_capability_noaudit()` query another task's credentials under RCU.
- `ns_capable()`, `ns_capable_noaudit()`, `ns_capable_setid()`, and `capable()` check the current task through `ns_capable_common()` and set `PF_SUPERPRIV` on success.
- `file_ns_capable()` checks the file opener's saved credentials, not current credentials.
- `privileged_wrt_inode_uidgid()` and `capable_wrt_inode_uidgid()` combine namespace capability checks with idmapped mount UID/GID mapping checks.
- `ptracer_capable()` checks `tsk->ptracer_cred` for `CAP_SYS_PTRACE` in the requested namespace without auditing.

## Control flow

`capget` first validates the capability header. If userspace probes the version with a null data pointer and an invalid version, the syscall follows the historical ABI and returns success after writing the supported version. For real requests it rejects negative PIDs, reads either current credentials or another task via `find_task_by_vpid()` under RCU, then serializes capabilities into one or two `__user_cap_data_struct` records.

`capset` performs the reverse path. It rejects attempts to alter any task other than the caller, copies the ABI-sized data, builds bounded `kernel_cap_t` masks, then uses the credential transaction helpers. The LSM hook controls the actual policy, including restrictions that raised inheritable/permitted/effective bits remain valid. Successful changes are audited before `commit_creds()`.

The capability predicates are thin but security-sensitive wrappers around `security_capable()`. Current-task checks validate `cap` with `cap_valid()` and deliberately BUG on invalid capability constants. File and ptracer checks use stored credentials so authorization is tied to open-time or ptrace-time authority rather than the caller's current mutable credentials.

## State and persistence behavior

The durable kernel state touched here is task credential state. `capset` never mutates credentials in place; it builds a new `struct cred`, lets the security layer update it, then atomically installs it. `file_caps_enabled` is process-independent global boot state. Capability checks may set the transient `PF_SUPERPRIV` task flag to record that the task used privilege. The inode helper has no persistence; it only evaluates whether VFS UID/GID mappings make namespace privilege meaningful for the inode.

## Dependencies and integration points

The file depends on `linux/capability.h`, `linux/security.h`, `linux/audit.h`, user access helpers, PID namespaces, user namespaces, and credential helpers. LSM integration is through `security_capget()`, `security_capset()`, and `security_capable()`. Audit integration is through `audit_log_capset()`. Exported helpers are consumed broadly by VFS, process control, namespace, and driver code needing capability gates.

## Risks and edge cases

- Capability ABI compatibility is subtle: older callers receive truncated upper capability bits by design, which is fail-safe but can surprise capget/modify/capset flows.
- `capset` only allows current-task changes. Any code assuming historical group or arbitrary-pid behavior will receive `-EPERM`.
- Stored-credential checks in `file_ns_capable()` and `ptracer_capable()` are intentional. Replacing them with current credentials would reopen inherited-fd or tracer-credential races.
- `ns_capable_common()` BUGs on invalid capability numbers. Callers must validate dynamic capability values before passing them here.
- `capable_wrt_inode_uidgid()` requires both capability and mapped inode owner IDs. Namespace privilege alone is insufficient over unmapped idmapped mount owners.

## Test signals

Useful tests include syscall ABI probes for all three capability versions, invalid version writeback, null `dataptr` probing, negative PID rejection, non-current `capset` rejection, and upper-bit truncation for v1 callers. Security tests should exercise LSM denial paths, audit records on successful `capset`, `PF_SUPERPRIV` setting on successful `capable()`, idmapped mount owner mapping failures, and file-descriptor checks that continue to use opener credentials after caller credential changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/capability.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cfi.c -->
# sources/distributed-fs/ceph-client/kernel/cfi.c

## Purpose

`cfi.c` implements common kernel support for Clang Control Flow Integrity failure reporting, CFI type hashes used by BPF JIT code, and optional trap-address recognition for architectures that emit KCFI trap tables. It decides whether a CFI violation is reported as a warning or a fatal bug according to `CONFIG_CFI_PERMISSIVE`.

## Important APIs, types, and functions

- `cfi_warn` is `__ro_after_init` and defaults from `IS_ENABLED(CONFIG_CFI_PERMISSIVE)`.
- `report_cfi_failure()` logs the failed call site, optional target symbol, and expected type hash, then either calls `__warn()` and returns `BUG_TRAP_TYPE_WARN` or returns `BUG_TRAP_TYPE_BUG`.
- `DEFINE_CFI_TYPE(cfi_bpf_hash, __bpf_prog_runX)` and `DEFINE_CFI_TYPE(cfi_bpf_subprog_hash, __bpf_callback_fn)` publish KCFI type hashes for `bpf_func_t` and `bpf_callback_t` compatible call targets.
- Under `CONFIG_ARCH_USES_CFI_TRAPS`, `trap_address()` resolves relative `s32` trap entries, `is_trap()` scans a trap-table range, and `is_cfi_trap()` checks built-in and module trap tables.
- Under `CONFIG_MODULES`, `module_cfi_finalize()` finds a module's `__kcfi_traps` section and records the start/end pointers in `struct module`; `is_module_cfi_trap()` looks up the containing module under RCU.

## Control flow

On a CFI failure, architecture-specific trap or call checking code calls `report_cfi_failure()`. The function emits a precise kernel log message and returns a trap disposition to the generic bug handling path. In permissive mode it also emits a warning at the faulting address; otherwise the caller treats the failure as a bug.

For trap recognition, built-in kernel trap tables are provided by linker symbols `__start___kcfi_traps` and `__stop___kcfi_traps`. Module loading calls `module_cfi_finalize()` after ELF sections are available; it searches section names for `__kcfi_traps` and stashes the address range. Later `is_cfi_trap()` scans the built-in table first and then the relevant module table.

## State and persistence behavior

`cfi_warn` becomes read-only after init. Module state persists in `mod->kcfi_traps` and `mod->kcfi_traps_end` for each loaded module. The BPF CFI type hash variables are static kernel data emitted by `DEFINE_CFI_TYPE`; they are used as constants by architecture-specific BPF JIT implementations. No filesystem or user-visible persistent state is written.

## Dependencies and integration points

The file integrates with compiler-emitted CFI metadata (`linux/cfi_types.h`), kernel bug handling (`enum bug_trap_type`, `__warn()`), BPF JITs (`linux/bpf.h`), the module loader, ELF section headers, RCU-protected module address lookup, and linker-provided KCFI section boundaries. Architecture code supplies the actual trap handling and calls into `is_cfi_trap()` where supported.

## Risks and edge cases

- `is_trap()` linearly scans trap ranges. Very large trap tables could make fault-path lookup cost visible, though the path is exceptional.
- `module_cfi_finalize()` relies on exact section naming and section address/size correctness. Missing or malformed `__kcfi_traps` data leaves module trap detection disabled for that module.
- `report_cfi_failure()` may omit target details when the architecture cannot supply them; diagnostics remain useful but less specific.
- Permissive mode intentionally allows execution to continue after warning. That is valuable for bring-up but reduces hardening.
- BPF JIT code must use the published hashes consistently with the function pointer types; mismatches can cause false CFI failures.

## Test signals

Build tests should cover CFI enabled with and without `CONFIG_CFI_PERMISSIVE`, with and without `CONFIG_MODULES`, and on architectures with `CONFIG_ARCH_USES_CFI_TRAPS`. Runtime signals include intentional KCFI violation tests that verify warning versus bug behavior, module load tests confirming `__kcfi_traps` range population, and BPF JIT tests confirming generated indirect call targets carry the expected `cfi_bpf_hash` or `cfi_bpf_subprog_hash`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/Makefile -->
# sources/distributed-fs/ceph-client/kernel/cgroup/Makefile

## Purpose

`kernel/cgroup/Makefile` selects the object files that make up the kernel cgroup subsystem. It always builds the core cgroup implementation, rstat accounting, namespace support, cgroup v1 compatibility, and freezer core, then conditionally includes controller-specific implementations based on Kconfig symbols.

## Important build entries

- `obj-y := cgroup.o rstat.o namespace.o cgroup-v1.o freezer.o` makes the core cgroup subsystem built-in for this kernel tree.
- `obj-$(CONFIG_CGROUP_FREEZER) += legacy_freezer.o` adds the legacy freezer controller when enabled.
- `obj-$(CONFIG_CGROUP_PIDS) += pids.o`, `obj-$(CONFIG_CGROUP_RDMA) += rdma.o`, `obj-$(CONFIG_CGROUP_MISC) += misc.o`, and `obj-$(CONFIG_CGROUP_DMEM) += dmem.o` add optional controllers.
- `obj-$(CONFIG_CPUSETS) += cpuset.o` and `obj-$(CONFIG_CPUSETS_V1) += cpuset-v1.o` split common cpuset support from v1-specific behavior.
- `obj-$(CONFIG_CGROUP_DEBUG) += debug.o` includes debug controller/files only in debug builds.

## Control flow

This file has no runtime control flow. Kbuild evaluates the `obj-y` and `obj-$(CONFIG_...)` assignments to decide which C sources are compiled and linked into the kernel. Runtime availability of controllers, files, and mount options is shaped by these build choices.

## State and persistence behavior

There is no state in the Makefile itself. Its build-time decisions determine which runtime global state exists, such as pids controller state, rdma resource accounting state, cpuset state, debug files, and cgroup v1 support.

## Dependencies and integration points

The Makefile depends on cgroup-related Kconfig symbols and Kbuild conventions. It integrates the source files in this directory into the kernel's built-in object list. `cgroup-v1.o` is always present here, so boot-time and mount-time logic must disable v1 features through runtime configuration rather than absence of this object unless the broader tree changes the build model.

## Risks and edge cases

- Adding a new controller source requires both Kconfig and Makefile updates; missing the Makefile entry silently omits the implementation from builds.
- Always building `cgroup-v1.o` means v1 compatibility code remains compiled even if no v1 controllers are enabled.
- Build configurations with cpuset common support but without `CONFIG_CPUSETS_V1` must keep v1 references properly conditional.

## Test signals

Validation is primarily matrix build coverage. Compile representative configs with all controllers enabled, minimal cgroup controllers, cpusets with and without v1 support, and cgroup debug enabled. Link failures or missing symbols indicate incorrect object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-internal.h -->
# sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-internal.h

## Purpose

`cgroup-internal.h` is the private interface shared by cgroup core implementation files. It defines internal context structures for cgroup filesystem mounting, per-open-file state, css_set/cgroup association links, migration work state, trace-path helpers, root/subsystem iteration macros, and prototypes for cross-file cgroup core, rstat, namespace, and cgroup v1 functions.

## Important APIs, types, and data

- `TRACE_CGROUP_PATH(type, cgrp, ...)` builds a cgroup path under `trace_cgroup_path_lock` only when the relevant tracepoint static key is enabled, then emits the matching `trace_cgroup_*` event.
- `struct cgroup_fs_context` extends `kernfs_fs_context` with selected root, namespace, root flags, and cgroup v1-only mount options: clone-children, none/all selection, subsystem mask, hierarchy name, and release agent path.
- `cgroup_fc2context()` converts a generic `struct fs_context` to the private cgroup mount context.
- `struct cgroup_file_ctx` holds per-open cgroup file state for namespace context, PSI triggers, v2 task iterators, v1 cached pidlists, and peak-file tracking.
- `struct cgrp_cset_link` models the many-to-many relationship between `struct cgroup` and `struct css_set`.
- `struct cgroup_taskset` and `struct cgroup_mgctx` carry task/cset migration state, including source and destination cset lists, task counts, current iterator positions, preloaded csets, and affected subsystem masks.
- `for_each_root()` and `for_each_subsys()` provide internal iteration over roots and enabled subsystem slots.
- `notify_on_release()`, `get_css_set()`, and `put_css_set()` are inline helpers for common flag/refcount handling.
- Prototypes expose root setup, subsystem rebinding, kernfs live locking, migration, attach, mkdir/rmdir, path formatting, task counting, rstat init/exit, cgroup namespace proc operations, and cgroup v1 entry points.

## Control flow

As a header, it does not run control flow directly, but it shapes several core flows. Mount setup code allocates a `cgroup_fs_context`, parses v1/v2 options into it, then passes it to root setup and kernfs tree creation. Task migration code initializes a `cgroup_mgctx`, preloads source/destination css_sets, validates destination cgroups, migrates tasks, and finishes by dropping preload state. File operations use `cgroup_file_ctx` to keep iterator or pidlist state across seq_file calls.

The trace macro avoids path construction unless tracing is enabled, then serializes access to the global path buffer. `put_css_set()` performs a lockless fast path when the refcount will not reach zero and takes `css_set_lock` only for final destruction.

## State and persistence behavior

The header defines state containers but does not allocate most state. Persistent runtime state lives in cgroup roots, cgroups, css_sets, mount contexts, and open-file contexts owned by implementation files. `trace_cgroup_path` is a global scratch buffer protected by `trace_cgroup_path_lock`. css_set lifetime is refcounted and final release is serialized under `css_set_lock`.

## Dependencies and integration points

This private header depends on public cgroup, kernfs, workqueue, list, refcount, and fs parser APIs. It is included by cgroup core files such as `cgroup.c`, `cgroup-v1.c`, `rstat.c`, and `namespace.c`. It bridges kernfs filesystem operations, cgroup namespace handling, controller subsystem arrays, migration/attach logic, and trace events.

## Risks and edge cases

- Locking contracts are implicit in prototypes and inline helpers. Misusing `put_css_set_locked()`, `cgroup_kn_lock_live()`, or attach locks can introduce lifetime and migration races.
- `TRACE_CGROUP_PATH()` uses a single global buffer; any new trace path user must preserve the spinlock discipline and avoid sleeping while held.
- `for_each_subsys()` iterates all subsystem slots and tolerates null entries through its expression form. Callers must handle absent subsystems.
- Migration structs depend on list-head initialization macros. Stack allocations should use `DEFINE_CGROUP_MGCTX()` or exact initializers.
- v1-only fields live in the common mount context; v2 paths must not accidentally interpret v1 options.

## Test signals

Compile coverage across cgroup v1/v2, namespace, rstat, cpuset, and optional controller configs is the first signal. Runtime stress should cover task migration, concurrent fork/migration, cgroup removal during kernfs file access, tracepoint enable/disable while paths are emitted, css_set final put paths, and mixed v1/v2 mount option parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-v1.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/cgroup/cgroup-v1.c -->
