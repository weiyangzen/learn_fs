# subset-b-006040 Research

Grouped research for the listed `sources/distributed-fs/ceph-client/kernel` namespace, PID, padata, panic, params, and power/energy-model files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/notifier.c -->
# sources/distributed-fs/ceph-client/kernel/notifier.c

Purpose: Implements the Linux notifier-chain core: priority-ordered callback lists for atomic, blocking, raw, and SRCU execution contexts, plus the global die notifier chain used by low-level exception paths.

Important APIs/types/functions: `notifier_chain_register()`, `notifier_chain_unregister()`, `notifier_call_chain()`, and `notifier_call_chain_robust()` are the shared internals. Exported families include `atomic_notifier_chain_register()`, `atomic_notifier_chain_unregister()`, `atomic_notifier_call_chain()`, `blocking_notifier_chain_register()`, `blocking_notifier_call_chain()`, `blocking_notifier_call_chain_robust()`, `raw_notifier_*()`, `srcu_notifier_*()`, `srcu_init_notifier_head()`, `notify_die()`, `register_die_notifier()`, and `unregister_die_notifier()`. The file relies on `struct notifier_block` and notifier head types from `<linux/notifier.h>`.

Control flow: registration walks the callback list by descending priority, rejects duplicate block pointers, optionally rejects duplicate priorities, then publishes with `rcu_assign_pointer()`. Calls dereference the head, run callbacks in order, count calls if requested, and stop when a return value contains `NOTIFY_STOP_MASK`. Robust calls first issue an up event, then replay a down event over already-called notifiers on stop/error. Atomic chains protect mutation with a spinlock and use RCU for lockless calls. Blocking chains use `rwsem`, with boot-time bypass before scheduling works. Raw chains delegate all locking to callers. SRCU chains protect mutation with a mutex and readers with SRCU.

State and persistence: notifier chains are in-memory linked lists owned by their heads. The die chain is a static `ATOMIC_NOTIFIER_HEAD(die_chain)`. Unregister waits for RCU/SRCU grace periods for atomic/SRCU heads. Tracepoints record register, unregister, and run events.

Dependencies/integration: Used by subsystems that need event fan-out without tight coupling. Integrates with RCU, SRCU, lock primitives, `CONFIG_DEBUG_NOTIFIERS`, trace events, and kdebug die handling. `notify_die()` packages `struct die_args` and dispatches through the atomic die chain in exception-sensitive paths.

Risks: Callback context rules are critical: atomic callbacks must not sleep, blocking callbacks must be process-context safe, and raw chains must be externally synchronized. Robust rollback assumes the chain does not change between passes and explicitly rules out RCU mutation. Priority uniqueness is optional, so callers depending on total ordering must choose the unique-priority APIs. Debug notifier checks only catch invalid function pointers when configured.

Test signals: Register/unregister order and duplicate handling, priority insertion, `NOTIFY_STOP_MASK` short-circuiting, robust rollback call counts, unregister while readers are active, SRCU cleanup requirements, boot-time blocking/SRCU registration paths, and `notify_die()` delivery under RCU-watching conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nscommon.c -->
# sources/distributed-fs/ceph-client/kernel/nscommon.c

Purpose: Provides common namespace object initialization, inode allocation/freeing, owner discovery, active-reference propagation, and a helper that decides whether the current task may see all namespaces.

Important APIs/types/functions: `__ns_common_init()`, `__ns_common_free()`, `ns_owner()`, `__ns_ref_active_put()`, `__ns_ref_active_get()`, and `may_see_all_namespaces()`. The core type is `struct ns_common`, including refcounts, namespace id/type, proc operations, stashed file state, and namespace tree nodes.

Control flow: initialization sets the normal refcount to one, initializes the namespace tree nodes and owner root, validates the proc operations under `CONFIG_DEBUG_VFS`, allocates a proc inode unless one is supplied, and marks initial namespaces active. `ns_owner()` asks the namespace's `proc_ns_operations.owner()` hook for the owning user namespace, ignoring `init_user_ns` as always active. Active put decrements the namespace, and if it reaches zero, walks upward through owning user namespaces dropping one active reference per owner until it reaches an active owner or no owner. Active get increments the namespace and, only when resurrecting from zero, walks upward adding owner references until it reaches an already-active owner.

State and persistence: State is purely kernel memory: proc inode numbers, `__ns_ref`, `__ns_ref_active`, namespace tree nodes, and owner roots. Active references form a cascading ownership graph rooted at init namespaces, which are never deactivated.

Dependencies/integration: Integrates with proc namespace operations, namespace tree helpers, user namespaces, PID namespace access checks, and VFS debug warnings. `may_see_all_namespaces()` ties global visibility to being in `init_pid_ns` with `CAP_SYS_ADMIN` in `init_pid_ns.user_ns`.

Risks: The active-reference cascade is subtle; missed owner references can make namespaces invisible or prematurely inactive, while extra references leak active namespace trees. `ns_owner()` depends on every namespace type supplying correct `owner()` operations. Initial namespace identity checks must remain aligned with namespace id/inode initialization.

Test signals: Namespace creation/destruction across nested user namespaces, resurrection from inactive namespace references such as proc namespace files or sockets, active refcount underflow warnings, debug validation of namespace operation tables, and visibility checks for root namespace administrators versus contained namespace tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nscommon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nsproxy.c -->
# sources/distributed-fs/ceph-client/kernel/nsproxy.c

Purpose: Owns task namespace sets (`struct nsproxy`) and implements cloning, unsharing, switching, exiting, exec-time time namespace updates, credential namespace active-reference transitions, and the `setns(2)` syscall.

Important APIs/types/functions: `init_nsproxy`, `copy_namespaces()`, `unshare_nsproxy_namespaces()`, `switch_task_namespaces()`, `exit_nsproxy_namespaces()`, `switch_cred_namespaces()`, `get_cred_namespaces()`, `exit_cred_namespaces()`, `exec_task_namespaces()`, `setns`, and `nsproxy_cache_init()`. Internal helpers include `create_new_namespaces()`, `prepare_nsset()`, `validate_nsset()`, `commit_nsset()`, `check_setns_flags()`, and `put_nsset()`.

Control flow: clone fast-paths by taking an extra ref when no new non-user namespaces are requested and the time namespace is already committed. Otherwise it checks `CAP_SYS_ADMIN`, rejects incompatible `CLONE_NEWIPC|CLONE_SYSVSEM`, creates a new nsproxy by copying mount, UTS, IPC, PID-for-children, cgroup, net, and time namespaces, then activates it and attaches it to the task. Unshare converts `UNSHARE_EMPTY_MNTNS` to `CLONE_EMPTY_MNTNS` before creating a detached nsproxy. `setns(2)` accepts either proc namespace files or pidfds: proc namespace files validate one namespace, while pidfds snapshot the target task's namespace set under RCU/task lock and validate requested namespaces in user, mount, UTS, IPC, PID, cgroup, net, and time order before commit.

State and persistence: Namespace membership is in task `nsproxy` pointers and credential user namespace active references. `nsproxy_free()` releases each namespace reference and frees from `nsproxy_cachep`. `switch_task_namespaces()` activates the incoming set before swapping under `task_lock()` and drops the old set after unlock.

Dependencies/integration: Integrates with every namespace implementation (`copy_mnt_ns`, `copy_utsname`, `copy_ipcs`, `copy_pid_ns`, `copy_cgroup_ns`, `copy_net_ns`, `copy_time_ns`), credentials, fs root/pwd switching, IPC semaphore cleanup, perf namespace notifications, proc namespace files, pidfd lookup, ptrace access control, and the namespace active-reference helpers.

Risks: `setns()` correctness depends on validating all requested namespaces before the point of no return in `commit_nsset()`. Temporary `fs_struct` ownership differs for mount-only versus multi-namespace transitions. PID namespace installation is constrained by ancestry and active namespace semantics. Time namespaces require special exec/fork commit handling; missing it can leave `time_ns_for_children` inconsistent with `time_ns`.

Test signals: clone/unshare/setns combinations for every namespace flag, permission failures without `CAP_SYS_ADMIN`, pidfd setns with target exit races, mount namespace root/pwd updates, `CLONE_NEWIPC|CLONE_SYSVSEM` rejection, time namespace commit on fork/exec, credential active ref accounting, and nsproxy cache initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nsproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nstree.c -->
# sources/distributed-fs/ceph-client/kernel/nstree.c

Purpose: Maintains global namespace id indexes and implements `listns(2)`, allowing namespace ids to be looked up and enumerated globally, by type, or by owning user namespace.

Important APIs/types/functions: namespace roots `mnt_ns_tree`, `net_ns_tree`, `uts_ns_tree`, `user_ns_tree`, `ipc_ns_tree`, `pid_ns_tree`, `cgroup_ns_tree`, `time_ns_tree`, plus `ns_tree_node_init()`, `ns_tree_root_init()`, `ns_tree_node_empty()`, `ns_tree_node_add()`, `ns_tree_node_del()`, `__ns_tree_add_raw()`, `__ns_tree_remove()`, `ns_tree_lookup_rcu()`, `__ns_tree_adjoined_rcu()`, `__ns_tree_gen_id()`, and `SYSCALL_DEFINE4(listns)`.

Control flow: Each namespace is inserted into a type-specific rbtree/list, a unified rbtree/list, and, if it has an owning user namespace, that owner's `ns_owner_root`. `ns_tree_lock` is a seqlock: writers take write seqlock; lookup readers retry on sequence changes; listns point lookups use exclusive read seqlock helpers when they need a stable tree walk. Lookup supports unified or type-specific ids. `listns()` copies and validates `struct ns_id_req`, checks flags and user buffer size, prepares a `klistns`, then either enumerates namespaces owned by a user namespace or enumerates unified/type-specific trees.

State and persistence: All state is volatile kernel memory in rbtrees and RCU lists. Namespace ids come from a static atomic64 cookie after `NS_LAST_INIT_ID` unless a fixed initial id is supplied. `klistns` temporarily holds userspace output pointers, requested type mask, pagination id, optional user namespace, and a pinned first namespace.

Dependencies/integration: Depends on `struct ns_common`, namespace proc operations for get/put, owner user namespace roots, RCU list helpers, rbtrees, `copy_struct_from_user()`, `put_user()`, namespace visibility helpers, and `ns_get_unless_inactive()`.

Risks: The file mixes seqlock-protected rbtrees with RCU list iteration; insertion/deletion order and grace-period assumptions must remain consistent. `ns_tree_node_add()` adds to the list after `rb_find_add_rcu()` and warns on duplicate only after all inserts, so duplicate-id bugs can corrupt multiple indexes before warning. `listns()` permission filtering is subtle: current namespace, owner capability, and global visibility are separate paths. Pagination uses `last_ns_id + 1`, so overflow and sparse id behavior need attention.

Test signals: namespace id generation uniqueness, insertion/removal from all three indexes, RCU lookup while namespaces are destroyed, `listns()` with unified/type masks, owner-restricted listing, pagination from `ns_id`, invalid `ns_id_req` sizes/spare bits/type masks, inaccessible namespaces, and inactive namespace filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nstree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/padata.c -->
# sources/distributed-fs/ceph-client/kernel/padata.c

Purpose: Implements padata, a generic facility for parallel processing with ordered serialization callbacks, plus an init-time multithreaded job runner used to split large boot-time work across CPUs.

Important APIs/types/functions: exported APIs include `padata_do_parallel()`, `padata_do_serial()`, `padata_do_multithreaded()`, `padata_set_cpumask()`, `padata_alloc()`, `padata_free()`, `padata_alloc_shell()`, `padata_free_shell()`, and `padata_init()`. Key types are `struct padata_instance`, `struct padata_shell`, `struct parallel_data`, `struct padata_priv`, `struct padata_work`, and `struct padata_mt_job_state`.

Control flow: `padata_do_parallel()` validates instance flags and callback CPU under RCU-bh, takes a `parallel_data` ref, assigns a sequence number under the global work lock, allocates a bounded work item, and either queues parallel work or runs it inline if the work pool is exhausted. Parallel callbacks must later call `padata_do_serial()`, which inserts completed objects into a per-CPU reorder list unless it is the next expected sequence. `padata_reorder()` advances sequence order and queues serial callbacks on the selected callback CPU's serial workqueue. Serial workers drain local lists and drop `parallel_data` references in batches. Multithreaded init jobs allocate helper work items, compute aligned chunks, queue helpers across nodes if requested, and let the caller's thread participate.

State and persistence: `parallel_data` contains per-cpu reorder and serial queues, cpumasks, sequence counters, processed cursor, and a refcount. Instances own parallel/serial workqueues, cpumasks, flags (`PADATA_INIT`, `PADATA_RESET`, `PADATA_INVALID`), a shell list, kobject sysfs state, and optional CPU hotplug node. A global fixed-size `padata_works` pool bounds outstanding queued work.

Dependencies/integration: Integrates with workqueues, CPU masks, RCU-bh, CPU hotplug callbacks, sysfs kobjects, cpus read lock, mutexes/spinlocks, and kernel init jobs. Sysfs exposes `serial_cpumask` and `parallel_cpumask`.

Risks: Every object accepted by `padata_do_parallel()` must eventually call `padata_do_serial()` or the `parallel_data` refcount and ordering stream stall. Sequence wrap handling depends on CPU hash/cursor consistency. Cpumask changes replace `parallel_data` under RCU while old work may still reference it. CPU hotplug can mark an instance invalid and stop it. The fixed work pool forces inline execution under load, so callers must tolerate synchronous parallel callbacks.

Test signals: ordered serialization under out-of-order parallel completion, work-pool exhaustion inline fallback, cpumask sysfs changes, CPU online/offline replacement, invalid empty masks, shell allocation/free while work is outstanding, sequence wrap behavior, multithreaded chunk alignment and NUMA-aware dispatch, and sanitizer/lockdep coverage for refcount and lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/padata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/panic.c -->
# sources/distributed-fs/ceph-client/kernel/panic.c

Purpose: Implements kernel panic/oops/warning handling, panic sysctls and boot parameters, panic notifier dispatch, taint tracking, warning count limits, all-CPU backtrace triggering, crash-kexec handoff, and stack protector failure panic.

Important APIs/types/functions: exported symbols include `panic_timeout`, `panic_notifier_list`, `panic_blink`, `panic_try_start()`, `panic_reset()`, `panic_in_progress()`, `panic_on_this_cpu()`, `panic_on_other_cpu()`, `nmi_panic()`, `vpanic()`, `panic()`, `test_taint()`, `add_taint()`, `warn_slowpath_fmt()` or `__warn_printk()`, and `__stack_chk_fail()`. Other key helpers are `check_panic_on_warn()`, `panic_other_cpus_shutdown()`, `print_tainted()`, `oops_enter()`, `oops_exit()`, and `__warn()`.

Control flow: sysctls expose panic timeout, taint, oops behavior, warning limit, panic sys info, and deprecated `panic_print`. `vpanic()` disables interrupts/preemption, optionally redirects panic to a configured CPU for crash dump, claims `panic_cpu`, prints the panic message and stack, lets kgdb run, optionally executes crash kexec before notifiers, shuts down other CPUs, runs panic notifiers, prints configured system info, dumps kmsg, optionally kexecs after notifiers, flushes consoles, waits/reboots according to `panic_timeout`, or loops forever while blinking/touching watchdogs. Warnings print context, check panic-on-warn/warn-limit, taint, and emit trace events.

State and persistence: Global runtime state includes `panic_cpu`, `panic_redirect_cpu`, `panic_on_oops`, `panic_on_warn`, `panic_on_taint`, `panic_timeout`, `panic_print`, `warn_count`, `tainted_mask`, and pause-on-oops counters. Sysfs exposes `warn_count`; debugfs can reset WARN_ONCE state. State persists only until reboot except taint visibility in proc/sysfs while running.

Dependencies/integration: Integrates with notifier chains, kexec/crash dump, printk/nbcon consoles, kmsg dumpers, kgdb, sysctl/sysfs/debugfs, lockdep, ftrace/tracing, sysrq/reboot, SMP stop/backtrace facilities, watchdogs, and architecture weak hooks for CPU stopping and panic redirection.

Risks: Panic paths run in broken contexts, so lock ordering, console ownership, notifier side effects, and crash-kexec timing are safety-critical. `crash_kexec_post_notifiers` improves diagnostics but can reduce dump reliability. `panic_force_cpu` depends on target CPU online state and async IPI/NMI delivery. Taint buffer sizing must track `TAINT_FLAGS_COUNT`. Warning-limit behavior can panic on expected noisy warnings if configured.

Test signals: boot parameters (`panic`, `oops=panic`, `panic_on_taint`, `panic_force_cpu`), sysctl writes and permissions, warning count limit, taint additions and verbose string formatting, panic notifier ordering, crash-kexec before/after notifiers, console replay, SMP/NMI panic contention, pause-on-oops coordination, WARN_ONCE reset debugfs, and stack protector failure panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/params.c -->
# sources/distributed-fs/ceph-client/kernel/params.c

Purpose: Provides kernel/module command-line parameter parsing, standard parameter type operations, array/string handling, unsafe/lockdown checks, and sysfs exposure under `/sys/module/*/parameters`.

Important APIs/types/functions: `parse_args()`, `parameqn()`, `parameq()`, standard `param_set_*`, `param_get_*`, and `param_ops_*` for numeric, bool, invbool, bint, charp, string, and arrays; `param_set_uint_minmax()`, `kernel_param_lock()`, `kernel_param_unlock()`, `module_param_sysfs_setup()`, `module_param_sysfs_remove()`, `lookup_or_create_module_kobject()`, `__modver_version_show()`, and `module_destroy_params()`.

Control flow: `parse_args()` tokenizes space/comma-like kernel args using `next_arg()`, stops at `--`, and delegates each token to `parse_one()`. `parse_one()` matches dash/underscore-equivalent names, checks parameter level range, validates no-arg handling, locks the relevant module or built-in parameter mutex, checks unsafe/lockdown policy, invokes the setter, and reports errors. Standard setters parse with kstrtox helpers. `charp` parameters track kmalloced values for later freeing but can point into early boot command-line storage before slab is available. Sysfs setup builds a `parameters` attribute group per module/built-in module and routes reads/writes through parameter ops under lock.

State and persistence: Parameter values live in the variables pointed to by `kernel_param.arg`. `kmalloced_params` tracks dynamically allocated string parameter storage. Sysfs kobjects and attribute groups persist for built-in modules and loaded modules until removal. `module_kset` and `module_ktype` implement the `/sys/module` object model.

Dependencies/integration: Integrates with module loading, boot command-line parsing, sysfs/kobjects/ksets, security lockdown, kernel tainting, slab allocation, module version sections, and `CONFIG_MODULES`/`CONFIG_SYSFS`.

Risks: Setters may run during early boot before normal allocation/locking assumptions fully hold. `param_array()` temporarily writes NULs into the argument string, so callers must pass mutable buffers. Runtime DAC changes cannot make read-only params writable, but parameter ops themselves must enforce semantic constraints. Unsafe parameters taint the kernel; hardware parameters can be blocked by lockdown. `charp` lifetime depends on correct tracking through `kmalloced_params`.

Test signals: command-line parse of known/unknown params, dash versus underscore matching, `--` passthrough, null value rejection, no-arg bools, min/max validation, charp replacement/free before and after slab availability, array parsing limits/minimums, sysfs parameter permissions and writes, lockdown rejection of hardware parameters, unsafe tainting, and module unload parameter cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid.c -->
# sources/distributed-fs/ceph-client/kernel/pid.c

Purpose: Implements PID allocation, lookup, task attachment/detachment, PID namespace sysctls, pidfd creation/open/getfd helpers, and init PID namespace setup.

Important APIs/types/functions: `init_struct_pid`, `init_pid_ns`, `put_pid()`, `free_pid()`, `free_pids()`, `alloc_pid()`, `disable_pid_allocation()`, `find_pid_ns()`, `find_vpid()`, `attach_pid()`, `detach_pid()`, `change_pid()`, `exchange_tids()`, `transfer_pid()`, `pid_task()`, `find_task_by_pid_ns()`, `find_get_pid()`, `pid_nr_ns()`, `pid_vnr()`, `__task_pid_nr_ns()`, `task_active_pid_ns()`, `find_ge_pid()`, `pidfd_get_pid()`, `pidfd_get_task()`, `pidfd_open`, `register_pidns_sysctls()`, `unregister_pidns_sysctls()`, `pid_idr_init()`, and `pidfd_getfd`.

Control flow: `alloc_pid()` validates requested set_tid values against namespace levels and checkpoint/restore capability, allocates a variable-sized `struct pid`, initializes task lists and pidfs state, preloads IDR memory, then allocates ids from the nested namespace up to root under `pidmap_lock`. It stores NULLs in IDRs until all levels succeed, verifies namespace init PID constraints and `PIDNS_ADDING`, then publishes with `idr_replace()`, increments per-namespace allocation counters, activates the namespace, and adds pidfs state. `free_pid()` removes all namespace id mappings, wakes namespace reapers when only init remains, removes pidfs state, and drops refs after RCU. Task attachment uses `tasklist_lock` and RCU hlist updates.

State and persistence: PID state is in per-namespace IDRs, `pid_allocated`, pid cache objects, pidfs entries, per-PID task hlist heads, wait queues, and namespace sysctl sets. PID bitmap pages/IDR storage are effectively persistent for the lifetime of the namespace. `cad_pid` and per-namespace `pid_max` are exposed through sysctl.

Dependencies/integration: Integrates with PID namespaces, user namespaces, checkpoint/restore, proc/sysctl, pidfs, anon file descriptors/pidfds, tasklist locking, RCU, ptrace permission checks, fd passing via `receive_fd()`, and CPU-count-derived PID limits.

Risks: PID allocation must be atomic across all nested namespaces or unwind precisely. The IDR preload retry path drops and reacquires `pidmap_lock`, so callers depend on the code preserving allocation correctness. `pidfd_open()` does not enforce thread-group leader when `PIDFD_THREAD` is passed; callers must interpret pidfd type flags correctly. `pidfd_getfd()` crosses task fd tables and relies on ptrace and `exec_update_lock` to avoid races. Namespace shutdown depends on `PIDNS_ADDING` and child reaper lifetime.

Test signals: nested PID allocation/free with set_tid arrays, pid_max sysctl bounds, namespace init PID requirement, PID wrap around `RESERVED_PIDS`, allocation failure unwind, find/attach/detach under RCU, pidfd open/get task/getfd permission and exit races, cad_pid sysctl update, pidfs add/remove failure, and namespace teardown wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_namespace.c -->
# sources/distributed-fs/ceph-client/kernel/pid_namespace.c

Purpose: Implements PID namespace creation, destruction, process zapping on namespace init exit, PID namespace reboot behavior, proc namespace operations, and checkpoint/restore sysctl registration.

Important APIs/types/functions: `copy_pid_ns()`, `put_pid_ns()`, `zap_pid_ns_processes()`, `reboot_pid_ns()`, `pidns_is_ancestor()`, `pidns_operations`, `pidns_for_children_operations`, and `pid_namespaces_init()`. Internal helpers include `create_pid_cachep()`, `create_pid_namespace()`, `destroy_pid_namespace_work()`, `pid_ns_ctl_handler()`, `pidns_get()`, `pidns_for_children_get()`, `pidns_put()`, `pidns_install()`, `pidns_get_parent()`, and `pidns_owner()`.

Control flow: creating a PID namespace verifies user namespace ancestry, max nesting, and ucount limits, allocates a namespace object and level-specific PID cache, initializes common namespace state and sysctls, inherits `memfd_noexec_scope`, links parent/user refs, sets `PIDNS_ADDING`, initializes destroy work, and adds the namespace to the namespace tree. Destruction removes the namespace tree/sysctls, frees the proc inode and IDR, then RCU-frees user/ucount references. `zap_pid_ns_processes()` disables PID allocation, ignores SIGCHLD, sends SIGKILL to remaining namespace tasks by IDR iteration, waits for children, then sleeps until only namespace init tasks remain.

State and persistence: PID namespaces store IDRs, parent/user namespace refs, ucount charging, `pid_allocated`, `child_reaper`, reboot signal, pid cache pointer, sysctl set/header, active namespace nodes, and optional memfd noexec scope. Destruction is deferred through workqueue and RCU to avoid freeing while visible to lookups.

Dependencies/integration: Integrates with user namespace ucounts, proc namespace operations, namespace trees, sysctl, checkpoint/restore `ns_last_pid`, memfd sysctl helper, reboot syscall behavior, signal delivery, wait/reaping, tasklist lock, accounting exit, and PID allocation in `pid.c`.

Risks: Namespace destruction cascades through parents while using active refs; incorrect `ns_ref_put()` handling can leak or prematurely destroy parent namespaces. `zap_pid_ns_processes()` relies on child reaper signal disposition and `pid_allocated` wakeups to avoid hangs. `pidns_install()` must prevent escaping to ancestor/incomparable PID namespaces. `pid_ns_ctl_handler()` updates the IDR cursor and requires checkpoint/restore capability.

Test signals: nested PID namespace creation at max depth, ucount exhaustion, failed init fork cleanup, sysctl registration failures, namespace init exit with live children/zombies/parent-namespace tracers, reboot commands in nested namespaces, setns PID ancestry validation, proc namespace get/put/parent, and `ns_last_pid` writes under checkpoint/restore capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_sysctl.h -->
# sources/distributed-fs/ceph-client/kernel/pid_sysctl.h

Purpose: Provides the PID-namespace scoped `/proc/sys/vm/memfd_noexec` sysctl helper when both sysctl and memfd creation are enabled, with a no-op fallback otherwise.

Important APIs/types/functions: `pid_mfd_noexec_dointvec_minmax()`, `pid_ns_ctl_table_vm[]`, and `register_pid_ns_sysctl_table_vm()`. The key state is `pid_namespace.memfd_noexec_scope`.

Control flow: On sysctl access, the handler gets the current task's active PID namespace, rejects writes without `CAP_SYS_ADMIN` in that namespace's user namespace, copies the table, computes the effective current scope as the max of the namespace value and parent scope, sets the minimum to the parent scope so children cannot lower enforcement below parents, delegates to `proc_dointvec_minmax()`, and writes the namespace value back on successful write. The registration helper registers the table under `vm`.

State and persistence: State persists in each PID namespace's `memfd_noexec_scope`; the init namespace supplies the initial data pointer for sysctl registration. Parent scope acts as a dynamic lower bound.

Dependencies/integration: Depends on `CONFIG_SYSCTL`, `CONFIG_MEMFD_CREATE`, PID namespaces, user namespace capability checks, and the memfd noexec scope helpers/macros.

Risks: Because the handler rewrites a temporary effective value, bugs in parent-scope calculation could allow policy weakening or display misleading values. The header defines static functions/data and is included by PID namespace code; it must remain small and config-guarded to avoid duplicate symbol issues.

Test signals: reads/writes in init and nested PID namespaces, parent value greater than child value, attempts to lower below parent, unprivileged write rejection, range bounds 0..2, and fallback build without sysctl or memfd support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/power/Kconfig

Purpose: Defines kernel power-management configuration options for suspend, hibernation, autosleep, wakelocks, PM QoS wakeup latency, PM debug/test features, APM emulation, generic PM domains, workqueue power efficiency, CPU PM, and the Energy Model framework.

Important APIs/types/functions: This is Kconfig data rather than C APIs. Key symbols include `SUSPEND`, `SUSPEND_FREEZER`, `SUSPEND_SKIP_SYNC`, `HIBERNATE_CALLBACKS`, `HIBERNATION`, `HIBERNATION_SNAPSHOT_DEV`, `HIBERNATION_COMP_LZO`, `HIBERNATION_COMP_LZ4`, `HIBERNATION_DEF_COMP`, `PM_STD_PARTITION`, `PM_SLEEP`, `PM_SLEEP_SMP`, `PM_AUTOSLEEP`, `PM_USERSPACE_AUTOSLEEP`, `PM_WAKELOCKS`, `PM_QOS_CPU_SYSTEM_WAKEUP`, `PM`, `PM_DEBUG`, `PM_ADVANCED_DEBUG`, `PM_TEST_SUSPEND`, `DPM_WATCHDOG`, `PM_TRACE`, `PM_TRACE_RTC`, `APM_EMULATION`, `PM_CLK`, `PM_GENERIC_DOMAINS`, `WQ_POWER_EFFICIENT_DEFAULT`, `CPU_PM`, and `ENERGY_MODEL`.

Control flow: Dependencies and selects determine build inclusion: suspend requires `ARCH_SUSPEND_POSSIBLE`; hibernation requires swap and arch support and selects callbacks/crypto; `PM_SLEEP` becomes true for suspend or hibernate callbacks and selects `PM`; SMP sleep selects hotplug CPU; autosleep/wakelocks depend on `PM_SLEEP`; Energy Model depends on CPU frequency or devfreq support.

State and persistence: Kconfig choices persist in the kernel build configuration and control compiled objects, defaults, boot/runtime sysfs defaults, and available kernel parameters. No runtime code is executed here.

Dependencies/integration: Drives `kernel/power/Makefile` object selection and many compile-time conditionals across PM, scheduler energy-aware scheduling, cpufreq/devfreq, freezer, pstore watchdog, RTC wakealarm test, ACPI/APM, and generic PM domains.

Risks: Option dependencies encode policy and safety tradeoffs. `PM_USERSPACE_AUTOSLEEP` explicitly warns about aggressive Android-style suspend behavior. `SUSPEND_SKIP_SYNC` changes default data-safety behavior. `PM_TRACE_RTC` intentionally corrupts RTC time for debugging. `DPM_WATCHDOG` can intentionally panic systems on suspend/resume stalls.

Test signals: Kconfig dependency resolution for minimal PM, suspend-only, hibernation-only, debug, Android autosleep, and Energy Model builds; object inclusion in Makefile; visibility/defaults in `olddefconfig`; and runtime presence of sysfs/debug features implied by selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Makefile -->
# sources/distributed-fs/ceph-client/kernel/power/Makefile

Purpose: Selects kernel power-management object files based on Kconfig symbols and applies debug/KASAN build flags for specific power objects.

Important APIs/types/functions: Build targets include always-built `qos.o`; conditional `main.o`, `console.o`, `process.o`, `suspend.o`, `suspend_test.o`, `hibernate.o`, `snapshot.o`, `swap.o`, `user.o`, `autosleep.o`, `wakelock.o`, `poweroff.o`, and energy-model composite `em.o`. `em-y` contains `energy_model.o`; `em-$(CONFIG_NET)` adds `em_netlink_autogen.o` and `em_netlink.o`.

Control flow: `CONFIG_DYNAMIC_DEBUG=y` adds `-DDEBUG` to `swap.o`, `snapshot.o`, and `energy_model.o`. `KASAN_SANITIZE_snapshot.o := n` disables KASAN for snapshot code. Object inclusion follows the Kconfig PM matrix, while `CONFIG_ENERGY_MODEL` builds `em.o` and optionally includes netlink support only with networking.

State and persistence: No runtime state; this file persists build graph decisions. Composite object membership affects which symbols and initcalls appear in the final kernel.

Dependencies/integration: Consumes symbols from `kernel/power/Kconfig` and connects Energy Model core to optional generic netlink support. Integrates with Kbuild composite object syntax and sanitizer/debug flag plumbing.

Risks: Misaligned Kconfig/Makefile conditions can silently omit runtime features or include code without dependencies. Energy Model netlink functions are compiled only when both `ENERGY_MODEL` and `NET` are set, matching header stubs. Disabling KASAN for snapshot is deliberate and should not be broadened casually.

Test signals: Build matrix checks for `CONFIG_PM`, `CONFIG_SUSPEND`, `CONFIG_HIBERNATION`, `CONFIG_PM_AUTOSLEEP`, `CONFIG_PM_WAKELOCKS`, `CONFIG_MAGIC_SYSRQ`, `CONFIG_ENERGY_MODEL`, and `CONFIG_NET`; verify `em.o` composition and dynamic debug flags in verbose builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/autosleep.c -->
# sources/distributed-fs/ceph-client/kernel/power/autosleep.c

Purpose: Implements opportunistic system autosleep, queueing suspend/hibernate attempts whenever wakeup-source accounting indicates the system can enter a configured sleep state.

Important APIs/types/functions: `queue_up_suspend_work()`, `pm_autosleep_state()`, `pm_autosleep_lock()`, `pm_autosleep_unlock()`, `pm_autosleep_set_state()`, and `pm_autosleep_init()`. Internal state includes `autosleep_state`, `autosleep_wq`, `autosleep_lock`, `autosleep_ws`, and work item `suspend_work`.

Control flow: `try_to_suspend()` obtains a wakeup count, locks autosleep, saves the count, checks `SYSTEM_RUNNING`, skips if state is `PM_SUSPEND_ON`, then calls `hibernate()` for disk states or `pm_suspend()` for suspend states. After unlock it rechecks wakeup count; if no wakeup count changed, it sleeps half a second to avoid tight suspend/resume loops, then requeues if autosleep remains enabled. `pm_autosleep_set_state()` holds a wakeup source while changing state, toggles wakeup-source autosleep behavior, and queues work when enabling.

State and persistence: Runtime state is the selected sleep state, ordered workqueue, mutex, and wakeup source. State is not persistent across reboot; userspace typically drives it through PM sysfs.

Dependencies/integration: Integrates with wakeup source accounting, system suspend/hibernate core, system state, workqueues, and `power.h` PM internals.

Risks: The comment warns that `autosleep_lock` is safe to lock only while a wakeup source is active or interruptibly, otherwise deadlock with freezing is possible. Wakeup count races determine whether suspend attempts proceed. Autosleep can repeatedly suspend if userspace or drivers mismanage wakeup sources.

Test signals: enable/disable autosleep states, suspend and hibernate paths, wakeup count save failure, wakeup-source active protection while changing state, `SYSTEM_RUNNING` rejection, tight-loop delay when final count equals initial count, workqueue allocation failure, and lockdep coverage for freeze interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/autosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/console.c -->
# sources/distributed-fs/ceph-client/kernel/power/console.c

Purpose: Saves/restores virtual console state around suspend/resume and lets drivers declare whether a VT switch is required.

Important APIs/types/functions: `pm_vt_switch_required()`, `pm_vt_switch_unregister()`, `pm_prepare_console()`, and `pm_restore_console()`. Key state includes `orig_fgconsole`, `orig_kmsg`, `vt_switch_done`, `vt_switch_mutex`, `pm_vt_switch_list`, and `struct pm_vt_switch`.

Control flow: Drivers register/update their switch requirement in a mutex-protected list. `pm_vt_switch()` returns true if no driver has registered, console suspend is disabled, or any registered driver requires switching; otherwise it skips switching. `pm_prepare_console()` moves to the reserved suspend console and redirects kmsg. `pm_restore_console()` moves back and restores kmsg redirection if a switch was done or current requirements indicate switching.

State and persistence: Runtime state tracks registered devices and original console/kmsg destinations. Entries are allocated per registering device and removed on unregister. No persistent storage is used.

Dependencies/integration: Integrates with VT console helpers, keyboard/VT state, `console_suspend_enabled`, PM suspend/resume sequencing, device drivers, and module exports.

Risks: Device unregister must remove list entries to avoid stale pointers. The switch decision can change between prepare and restore, so `vt_switch_done` protects restore behavior. Allocation failure in `pm_vt_switch_required()` leaves the previous behavior unchanged. The reserved console is `MAX_NR_CONSOLES-1`, so assumptions must match VT limits.

Test signals: no registered drivers, all drivers switchless, one driver requiring switch, no-console-suspend command-line behavior, registration update for an existing device, unregister cleanup, failed console move, and suspend/resume cycles with kmsg redirection restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.c -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink.c

Purpose: Exposes Energy Model performance domains and performance tables through generic netlink and emits multicast events when performance domains are created, updated, or deleted.

Important APIs/types/functions: netlink command handlers `dev_energymodel_nl_get_perf_domains_doit()`, `dev_energymodel_nl_get_perf_domains_dumpit()`, `dev_energymodel_nl_get_perf_table_doit()`, notifications `em_notify_pd_created()`, `em_notify_pd_updated()`, `em_notify_pd_deleted()`, and init `em_netlink_init()`. Helpers include `__em_nl_get_pd_size()`, `__em_nl_get_pd()`, `__em_nl_get_pd_table_size()`, `__em_nl_get_pd_table()`, and `__em_notify_pd_table()`.

Control flow: The get-domain doit path validates a performance domain id attribute, looks up the domain by id, sizes a reply, emits id/flags/cpu attributes, and replies. The dump path iterates `for_each_em_perf_domain()` and emits one generic-netlink message per domain after the starting index. The get-table path resolves the domain id, sizes for all perf states, reads the current RCU-protected EM table, and nests state attributes for performance, frequency, power, cost, and flags. Notifications first check multicast listeners, build the same table message for create/update or id-only delete message, and multicast on the event group.

State and persistence: The file owns no EM state; it serializes snapshots from `struct em_perf_domain` and RCU-protected perf tables. Generic netlink family state is generated in `em_netlink_autogen.c` and registered at postcore init.

Dependencies/integration: Depends on Energy Model core lookup/iteration from `energy_model.c`, generic netlink, UAPI `dev_energymodel.h`, init net namespace listeners, RCU table reads, and generated YNL family definitions.

Risks: `dev_energymodel_nl_get_perf_domains_dumpit()` reads `cb->args[0]` as a start index but does not update it after emitting domains, which is a concrete risk for multipart dump progress/repetition if the skb fills. Several error paths call `genlmsg_cancel()` or free skb after partial construction; header/nest handling must remain exact. Perf domain lookup returns pointers protected by the EM list mutex only during lookup/iteration; deletion races rely on higher-level EM lifetime behavior and netlink notification ordering.

Test signals: netlink doit for valid/invalid domain ids, dump across more domains than fit in one skb, table reads while EM updates replace the RCU table, listener/no-listener notification paths, create/update/delete event contents, policy validation, and kernel netlink selftests generated from `dev-energymodel.yaml`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.h -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink.h

Purpose: Declares the Energy Model core functions used by netlink support and provides no-op stubs when Energy Model netlink support is not compiled.

Important APIs/types/functions: `for_each_em_perf_domain()`, `em_perf_domain_get_by_id()`, `em_notify_pd_created()`, `em_notify_pd_deleted()`, and `em_notify_pd_updated()`.

Control flow: Under `CONFIG_ENERGY_MODEL && CONFIG_NET`, declarations are provided for the real implementations. Otherwise iteration returns `-EINVAL`, lookup returns `NULL`, and notification helpers do nothing.

State and persistence: No state. It defines the compile-time contract between `energy_model.c` and optional netlink files.

Dependencies/integration: Depends on `struct em_perf_domain` from Energy Model headers and mirrors `kernel/power/Makefile`, where netlink files are included in `em.o` only with `CONFIG_NET`.

Risks: The config condition must stay aligned with build rules; otherwise callers may link against missing real symbols or silently use stubs. Stub return values should be acceptable to callers in non-net builds.

Test signals: Build with Energy Model plus NET, Energy Model without NET, and without Energy Model; confirm notifications compile out and lookup/iteration users handle stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.c -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.c

Purpose: Auto-generated YNL generic-netlink family implementation for the device Energy Model UAPI.

Important APIs/types/functions: Defines policies `dev_energymodel_get_perf_domains_nl_policy[]` and `dev_energymodel_get_perf_table_nl_policy[]`, split ops `dev_energymodel_nl_ops[]`, multicast groups `dev_energymodel_nl_mcgrps[]`, and exported family object `dev_energymodel_nl_family`.

Control flow: The ops table wires `DEV_ENERGYMODEL_CMD_GET_PERF_DOMAINS` to both doit and dump handlers and `DEV_ENERGYMODEL_CMD_GET_PERF_TABLE` to its doit handler. Policies constrain requested domain id attributes to `NLA_U32`. The family is netns-aware, uses parallel ops, and points to the generated multicast event group.

State and persistence: The generated `genl_family` is `__ro_after_init`; after registration it is the persistent kernel representation of the netlink family until shutdown.

Dependencies/integration: Generated from `Documentation/netlink/specs/dev-energymodel.yaml`; includes generic netlink headers, `em_netlink_autogen.h`, and UAPI `linux/dev_energymodel.h`. Runtime handlers live in `em_netlink.c`.

Risks: Manual edits would be overwritten by YNL regeneration. Policy maxattr values must match UAPI enum definitions. `parallel_ops = true` means handlers must be safe under concurrent netlink requests.

Test signals: Regenerate from YAML and compare, netlink policy validation for missing/wrong attrs, family registration, parallel requests, and multicast group presence in netlink introspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.h -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.h

Purpose: Auto-generated header declaring Energy Model generic-netlink handlers, multicast group ids, and the family object.

Important APIs/types/functions: Declarations for `dev_energymodel_nl_get_perf_domains_doit()`, `dev_energymodel_nl_get_perf_domains_dumpit()`, `dev_energymodel_nl_get_perf_table_doit()`, enum `DEV_ENERGYMODEL_NLGRP_EVENT`, and `extern struct genl_family dev_energymodel_nl_family`.

Control flow: No executable logic; it provides compile-time prototypes consumed by the generated family and the hand-written netlink encoder.

State and persistence: No state in the header. The declared family state is defined in `em_netlink_autogen.c`.

Dependencies/integration: Generated from `Documentation/netlink/specs/dev-energymodel.yaml`; includes netlink/genetlink and UAPI Energy Model headers.

Risks: Must not drift from the generated C file or UAPI enums. Since it declares command handlers implemented manually, signature changes in YNL generation require matching code changes in `em_netlink.c`.

Test signals: Full build after YNL regeneration, sparse/header self-containment checks, and netlink family registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/energy_model.c -->
# sources/distributed-fs/ceph-client/kernel/power/energy_model.c

Purpose: Implements the Energy Model framework for registering device/CPU performance domains, computing performance/cost/inefficiency data, updating runtime EM tables safely, exposing debugfs, notifying netlink, and coordinating scheduler/cpufreq integration.

Important APIs/types/functions: `em_table_alloc()`, `em_table_free()`, `em_dev_compute_costs()`, `em_dev_update_perf_domain()`, `em_pd_get()`, `em_cpu_get()`, `em_dev_register_perf_domain()`, `em_dev_register_pd_no_update()`, `em_dev_unregister_perf_domain()`, `em_adjust_cpu_capacity()`, `em_dev_update_chip_binning()`, `em_update_performance_limits()`, `em_rebuild_sched_domains()`, `for_each_em_perf_domain()`, and `em_perf_domain_get_by_id()`. Core state types include `struct em_perf_domain`, `struct em_perf_table`, `struct em_perf_state`, `struct em_data_callback`, IDA `em_pd_ida`, list `em_pd_list`, and mutexes `em_pd_mutex`/`em_pd_list_mutex`.

Control flow: Registration serializes under `em_pd_mutex`, rejects duplicate domains and invalid CPU masks/capacities, determines microwatt versus artificial-cost flags, allocates a performance domain and RCU table, asks driver callbacks for monotonically increasing frequency/power states, computes CPU performance and cost/inefficiency, assigns the domain to device/CPUs, creates debugfs, adds the domain to the global id list, and emits a create notification. Runtime updates allocate or duplicate a table, compute costs if needed, publish with `rcu_assign_pointer()`, update cpufreq inefficient frequencies, and kref/RCU-free the old table. Capacity update work revisits CPU domains when arch capacities become available. Unregister is only for non-CPU devices and removes list/debugfs/table/id state before freeing the domain.

State and persistence: EM state is runtime kernel memory attached to `dev->em_pd` and, for CPUs, every CPU device in the span. Tables are RCU-protected and kref-counted. Debugfs exposes per-domain id, flags, CPUs, and per-performance-state frequency/power/cost/performance/inefficient values. Global IDA/list state backs netlink lookup and iteration.

Dependencies/integration: Integrates with cpufreq policies and inefficient frequency marking, OPP power calculation, scheduler topology and energy-aware scheduling rebuilds, CPU device bus, debugfs, RCU/kref, IDA/list mutexes, delayed work, and optional Energy Model netlink notifications.

Risks: Callback data validation is central: non-increasing frequencies, zero/overflow power, mismatched CPU capacities, wrong microwatt/artificial flags, or bad cost callbacks reject registration. Lock ordering is explicit: code holding `em_pd_list_mutex` must not take `em_pd_mutex`. `em_perf_domain_get_by_id()` returns a raw pointer after releasing the list mutex, so callers must rely on the EM lifetime model; netlink reads during unregister need careful coverage. `em_dev_unregister_perf_domain()` ignores CPU devices, so CPU EM lifetime is effectively permanent. Performance limit updates change min/max indexes under mutex but readers must tolerate concurrent reads.

Test signals: CPU and non-CPU domain registration, duplicate registration, invalid callback data, artificial-cost domains, debugfs contents, cpufreq inefficient marking, runtime table update under concurrent readers, chip-binning OPP recalculation, capacity delayed work retry, netlink create/update/delete notifications, unregister non-CPU domains, and lockdep for mutex ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/energy_model.c -->
