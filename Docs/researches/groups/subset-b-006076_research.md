# subset-b-006076 research

Grouped research for the listed Ceph-client Linux kernel sources. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_syscalls.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_syscalls.c

Purpose: implements ftrace/perf trace events for syscall entry and exit. It maps syscall numbers to `struct syscall_metadata`, creates trace event classes for `sys_enter_*` and `sys_exit_*`, formats event output, and optionally snapshots selected user-space arguments into dynamic trace fields for more useful syscall records.

Important APIs and data: `init_ftrace_syscalls()` builds `syscalls_metadata` or the sparse xarray from linker-provided syscall metadata and `arch_syscall_addr()`. `get_syscall_name()` exposes metadata lookup. `event_class_syscall_enter` and `event_class_syscall_exit` provide raw initialization, field definitions, and registration callbacks. `check_faultable_syscall()` annotates metadata with `user_mask`, `user_arg_size`, and `user_arg_is_str` for syscalls whose pointer arguments are copied.

Control flow: enable paths call `syscall_enter_register()` or `syscall_exit_register()`, then `reg_event_syscall_enter()`/`reg_event_syscall_exit()` install global syscall tracepoint callbacks when the first event is enabled. `ftrace_syscall_enter()` validates the syscall number, finds the per-array `trace_event_file`, copies register arguments, optionally reads user memory through `trace_user_fault_read()`, reserves a ring buffer event, writes static args and dynamic data locations, and commits. Exit tracing writes syscall number plus return value. Perf mirrors the same entry/exit flow using `perf_trace_buf_alloc()` and BPF prefilters.

State and persistence: per-trace-array refcounts and file arrays decide which syscalls are active. `syscall_buffer` is a shared fault buffer with tracing refcounts and RCU Tasks Trace cleanup. Perf state uses bitmaps and global refcounts. There is no durable storage; events are transient ring-buffer or perf records.

Dependencies and integration: depends on arch syscall helpers, tracepoints `sys_enter`/`sys_exit`, trace event metadata, ring buffers, perf, BPF, xarray, and user access fault helpers. It integrates with tracefs event enablement and perf event registration.

Risks: incorrect syscall metadata mapping disables or mislabels events; compat syscall handling is arch-sensitive. Dynamic user copies must avoid faults and truncation bugs. Registration/unregistration races are protected by `syscall_trace_lock`, but lifetime depends on file pointers being published with `WRITE_ONCE()` and callback unregistration. Test signals include enabling individual syscall events, verbose openat formatting, perf+BPF syscall events, compat tasks, and syscalls with truncated/faulting user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_uprobe.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_uprobe.c

Purpose: implements dynamic tracefs and perf events backed by uprobes and uretprobes. It parses user commands from `uprobe_events`, registers probes on executable file offsets, fetches arguments from user register/stack/memory contexts, emits ftrace events, and supports perf/BPF consumers.

Important APIs and types: `struct trace_uprobe` combines a dynamic event, `struct uprobe_consumer`, file path, offsets, hit counters, and a `struct trace_probe`. `trace_uprobe_ops` wires dynamic event create/show/free/match. `trace_uprobe_create()` and `__trace_uprobe_create()` parse `p:`/`r:` commands. `create_local_trace_uprobe()` supports perf-local uprobe events. Dispatcher callbacks are `uprobe_dispatcher()` and `uretprobe_dispatcher()`.

Control flow: command parsing validates probe type, path syntax, regular-file target, offset, optional `%return`, optional ref-counter offset, event name, and fetch arguments. Registration either appends compatible siblings to an existing event or creates a new trace event call. Enabling an event allocates per-CPU page buffers, registers uprobes, and sets trace/profile flags. On a hit, dispatchers set per-task uprobe dispatch context, prepare a per-CPU buffer with fetched args, and fan out to ftrace links and/or perf. Return probes include both function and return instruction addresses.

State and persistence: dynamic events persist while registered in tracefs. Per-probe hit counters are percpu. `uprobe_cpu_buffer` is refcounted under `event_mutex` and stores temporary formatted data. Perf target filtering is stored in `trace_uprobe_filter` with an rwlock, supporting system-wide and per-mm consumers.

Dependencies and integration: relies on uprobes core, trace dynamic events, trace probe argument parser, tracefs files, security lockdown checks, perf, BPF, RCU list traversal, and user memory access helpers.

Risks: command parsing and ref-counter consistency are policy-sensitive. Per-CPU buffer sizing is capped at one page and can truncate/warn if argument data grows. Probe removal must synchronize with uprobe core and event-file links. Perf filters must keep breakpoints applied only to intended mm targets. Test signals include tracefs create/delete, sibling probes with same name, ref-counter mismatch rejection, return probes, fetchargs from stack/registers/file offsets, perf per-task filters, BPF uprobe info, and lockdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_uprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.c -->
# sources/distributed-fs/ceph-client/kernel/trace/tracing_map.c

Purpose: provides a preallocated, lock-free hash map used by tracing aggregation paths such as hist triggers. It associates arbitrary fixed-size keys with `tracing_map_elt` objects that carry sum fields, variables, key copies, and optional client private data.

Important APIs: map setup uses `tracing_map_create()`, `tracing_map_add_key_field()`, `tracing_map_add_sum_field()`, `tracing_map_add_var()`, and `tracing_map_init()`. Runtime operations are `tracing_map_insert()`, `tracing_map_lookup()`, `tracing_map_update_sum()`, `tracing_map_set_var()`, and read helpers. Sorting is exposed through `tracing_map_sort_entries()` and `tracing_map_destroy_sort_entries()`. Numeric and string comparison helpers drive sorting.

Control flow: creation allocates a sparse hash entry array twice the requested element count. Initialization allocates all elements before tracing starts. Insert hashes the key with jhash, probes linearly, claims empty slots with `cmpxchg()`, initializes a free element from an atomic pool, copies the full key, publishes the element with a write barrier, and increments hits. Lookup uses the same probing without insertion. Clear resets counters, map entries, and element fields. Sorting snapshots current entries into a vmalloc array and sorts by key or sum, with optional secondary sort.

State and persistence: all state is in memory and tied to the map lifetime. Keys are never deleted or resized during active use. Hits and drops are atomic counters. Sum fields are atomic64; vars include separate set flags. Client callbacks manage private per-element state.

Dependencies and integration: uses vmalloc, slab, jhash, sort, kmemleak annotations, atomics, and tracing-specific allocation helpers. It is an internal library for tracing aggregators.

Risks: the map deliberately stops inserting after the fixed pool is exhausted, so callers must handle NULL and drops. Correctness depends on no active writers during clear/destroy and on publish ordering in insert. Duplicate hash/key publication is guarded with probing and duplicate detection during sort. Test signals include concurrent insertion of equal and colliding keys, pool exhaustion, key and sum sorting, secondary sort ordering, variable read-once semantics, and client callback cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.h -->
# sources/distributed-fs/ceph-client/kernel/trace/tracing_map.h

Purpose: declares the tracing aggregation map ABI used inside the kernel tracing subsystem. The header documents the relationship between map entries, element pools, key/sum fields, sort entries, and client callbacks.

Important types and constants: `TRACING_MAP_BITS_*` bounds map size; `TRACING_MAP_KEYS_MAX`, `TRACING_MAP_VALS_MAX`, `TRACING_MAP_FIELDS_MAX`, and `TRACING_MAP_VARS_MAX` bound field capacity. Core types include `struct tracing_map`, `struct tracing_map_entry`, `struct tracing_map_elt`, `struct tracing_map_field`, `struct tracing_map_array`, `struct tracing_map_sort_key`, and `struct tracing_map_sort_entry`. `struct tracing_map_ops` defines optional `elt_alloc`, `elt_free`, `elt_clear`, and `elt_init` hooks.

Control flow and API contract: clients create a map, add key and sum fields, optionally add variables, call `tracing_map_init()` to preallocate elements, then use insert/lookup/update during tracing. Sorting returns an allocated array that the caller must destroy. The array macros map logical indices onto page-backed arrays and are central to the implementation.

State and persistence: the header describes a no-delete in-memory table with a preallocated element pool. `hits` and `drops` counters are part of `struct tracing_map`. `private_data` exists at both map and element levels for client ownership.

Dependencies and integration: this is included by tracing map implementation and tracing clients. It exports comparison helpers and update/read helpers rather than exposing internal insertion details.

Risks: consumers must respect fixed limits and the required setup order. Destroying sort entries and map instances is caller-owned. Misusing field indexes, offsets, or sort keys can produce invalid comparisons. Test signals include compile-time consumers across histogram code, limit boundary tests, and API misuse tests that expect `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/undefsyms_base.c -->
# sources/distributed-fs/ceph-client/kernel/trace/undefsyms_base.c

Purpose: deliberately references a minimal set of compiler/toolchain generated primitives so pKVM/simple-ring-buffer builds can identify undefined symbols that are safe to ignore. It is not a runtime tracing feature.

Important API: `undefsyms_base(void *p, int n)` performs volatile `memset()`, `memcpy()`, `cmpxchg()`, and `WARN_ON()` operations. A page-aligned static `page` forces page-sized memory operations.

Control flow: the function initializes a stack buffer, writes to a static aligned page, copies the stack buffer into the caller pointer, performs a compare-exchange on a local `u32`, and warns on a sentinel input. This creates symbol references without complex behavior.

State and persistence: only the static `page` is persistent, and its contents are unimportant. There is no exported state, storage, or synchronization contract.

Dependencies and integration: includes atomic, string, and page headers. The file exists for build/link tooling around pKVM hypervisor constraints, where simple ring buffer code may lack normal kernel symbols.

Risks: this file should stay small and avoid pulling real subsystem dependencies into restricted builds. Tests are primarily build/link tests that verify expected undefined symbol filtering; runtime tests are not meaningful beyond ensuring the function compiles for target architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/undefsyms_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tracepoint.c -->
# sources/distributed-fs/ceph-client/kernel/tracepoint.c

Purpose: implements the core tracepoint probe registration machinery. It manages probe arrays, static branch/static call transitions, RCU/SRCU lifetime, module tracepoint discovery, tracepoint notifiers, and syscall tracepoint work flags.

Important APIs and types: exported registration APIs are `tracepoint_probe_register_prio_may_exist()`, `tracepoint_probe_register_prio()`, `tracepoint_probe_register()`, and `tracepoint_probe_unregister()`. Iteration APIs include `for_each_kernel_tracepoint()` and module variants. `struct tp_probes` owns RCU-freed probe arrays. Transition state is tracked by `tp_transition_snapshot`.

Control flow: registration builds a new priority-ordered probe array with `func_add()`, optionally calls tracepoint regfunc, publishes it with `rcu_assign_pointer()`, updates static calls for one-probe fast paths or iterator paths, and enables the static branch. Removal builds a smaller array or stubs removed functions if allocation fails, handles transitions from one to zero or many to one, updates static calls, and releases old arrays after SRCU or Tasks Trace grace periods depending on faultability.

State and persistence: `tracepoints_mutex` protects probe updates. Module tracepoints are tracked in a local list protected by `tracepoint_module_list_mutex`. Transition snapshots preserve grace-period state across specific 1-0-1 and N-2-1 static-call transitions. Syscall tracepoint refcount toggles `SYSCALL_TRACEPOINT` work flags on all tasks.

Dependencies and integration: depends on RCU, SRCU, static keys, static calls, module notifier chains, tasklist locking, and tracepoint linker sections. Modules can register coming/going notifiers to manage probes safely.

Risks: subtle ordering bugs can call a new function with old data or free arrays too early. Module teardown requires consumers to unregister probes. Allocation failure during removal leaves stubbed functions until a later successful update. Test signals include probe priority ordering, duplicate rejection, module load/unload notifier behavior, static-call one-probe transitions, faultable tracepoints, and syscall tracepoint enable/disable across live tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tsacct.c -->
# sources/distributed-fs/ceph-client/kernel/tsacct.c

Purpose: fills taskstats accounting records for basic and extended per-task resource usage. It is used by taskstats/acct paths to report elapsed time, CPU time, credentials, page faults, command names, IO counts, and memory-time integrals.

Important APIs: `bacct_add_tsk()` populates base task accounting fields. Under `CONFIG_TASK_XACCT`, `xacct_add_tsk()` adds extended memory and IO fields, `acct_update_integrals()` updates RSS/VM time integrals in interrupt-safe context, `acct_account_cputime()` updates after CPU time changes, and `acct_clear_integrals()` resets accumulators.

Control flow: base accounting calculates elapsed nanoseconds from task start times, converts to microseconds, derives boot time fields, records exit flags, pid/tgid/ppid in the requested pid namespace, maps uid/gid through a user namespace under RCU, collects CPU times, faults, and command name. Extended accounting converts stored page-nsec integrals to Mbyte-usec style taskstats units and samples mm high-water marks if an mm is available.

State and persistence: accounting accumulators live in `task_struct` fields such as `acct_rss_mem1`, `acct_vm_mem1`, and `acct_timexpd`. Output is copied into a caller-provided `struct taskstats`; this file does not persist records.

Dependencies and integration: depends on scheduler CPU time helpers, namespaces, credentials, mm references, task IO accounting, and taskstats structures.

Risks: unit conversions and overflow boundaries matter, especially legacy `ac_btime` clamping. `__acct_update_integrals()` skips kernel threads and mm-less tasks. Test signals include exited and live tasks, namespace uid/gid mapping, high-water RSS/VM reporting, IO accounting disabled builds, and sub-tick integral updates being ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tsacct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ucount.c -->
# sources/distributed-fs/ceph-client/kernel/ucount.c

Purpose: manages per-user, per-user-namespace usage counters and rlimit accounting across namespace ancestry. It backs limits such as max user namespaces, PID namespaces, UTS namespaces, inotify/fanotify counts, and rlimit-style counts.

Important APIs and state: `init_ucounts` is the root counter object. `alloc_ucounts()`, `put_ucounts()`, `inc_ucount()`, and `dec_ucount()` manage namespace object counters. Rlimit helpers include `inc_rlimit_ucounts()`, `dec_rlimit_ucounts()`, `inc_rlimit_get_ucounts()`, `dec_rlimit_put_ucounts()`, and `is_rlimit_overlimit()`. `setup_userns_sysctls()` and `retire_userns_sysctls()` expose per-namespace `/proc/sys/user/*` knobs.

Control flow: ucounts are hashed by namespace pointer plus kuid and protected by RCU plus `ucounts_lock` for insertion/removal. Allocation double-checks under lock to avoid duplicate objects. `inc_ucount()` allocates the leaf object, then walks parent `ns->ucounts` chain, incrementing each atomic count only below that namespace's max; on failure it unwinds prior increments and drops the leaf reference. Rlimit functions similarly walk ancestors and maintain references when counts transition from zero.

State and persistence: counters are in-memory, reference-counted by `rcuref`, and freed with RCU. Sysctl tables are dynamically duplicated per user namespace and point into `ns->ucount_max`.

Dependencies and integration: integrates with user namespace creation, UTS namespaces, pid/ipc/net/mount/cgroup/time namespaces, inotify/fanotify, and proc sysctl. Permissions allow CAP_SYS_RESOURCE in the target namespace to write limits.

Risks: ancestor unwind correctness is critical to avoid leaked counts. Negative atomic results are WARNed. Sysctl table lifetime must match namespace lifetime. Test signals include namespace creation at limits, concurrent alloc/free for same uid, sysctl permission checks in nested namespaces, and rlimit ref transitions to and from zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ucount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.c -->
# sources/distributed-fs/ceph-client/kernel/uid16.c

Purpose: implements legacy 16-bit UID/GID compatibility syscalls by translating between `old_uid_t`/`old_gid_t` and modern kernel uid/gid values.

Important APIs: syscall wrappers include `chown16`, `lchown16`, `fchown16`, `setregid16`, `setgid16`, `setreuid16`, `setuid16`, `setresuid16`, `getresuid16`, `setresgid16`, `getresgid16`, `setfsuid16`, `setfsgid16`, `getgroups16`, `setgroups16`, `getuid16`, `geteuid16`, `getgid16`, and `getegid16`. Helpers `groups16_to_user()` and `groups16_from_user()` convert supplementary group arrays.

Control flow: setter syscalls translate low 16-bit IDs with `low2highuid()` or `low2highgid()` and delegate to common credential syscalls declared in `uid16.h`. Getter syscalls map kernel credentials through the current user namespace using `from_kuid_munged()`/`from_kgid_munged()`, then truncate through `high2low*()` before copying to userspace. Group setting validates `may_setgroups()`, bounds by `NGROUPS_MAX`, allocates group info, converts each user gid with `make_kgid()`, sorts, and installs.

State and persistence: no independent state is stored here; all persistent effects are credential, ownership, or group changes performed by shared kernel helpers.

Dependencies and integration: depends on highuid conversion macros, user namespace id mapping, group_info allocation, and user access helpers. It exists only for architectures/configurations still exposing old 16-bit syscalls.

Risks: truncation and overflowuid/overflowgid behavior are compatibility-sensitive. Group conversion must reject unmapped gids. Test signals include legacy ABI syscall tests with mapped and unmapped IDs, invalid userspace pointers, negative group sizes, setgroups denial in user namespaces, and namespace overflow mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.h -->
# sources/distributed-fs/ceph-client/kernel/uid16.h

Purpose: declares internal modern credential helper syscalls used by the legacy 16-bit UID/GID syscall wrappers.

Important APIs: prototypes include `__sys_setuid()`, `__sys_setgid()`, `__sys_setreuid()`, `__sys_setregid()`, `__sys_setresuid()`, `__sys_setresgid()`, `__sys_setfsuid()`, and `__sys_setfsgid()`.

Control flow and integration: `uid16.c` translates 16-bit ABI arguments and delegates to these helpers so policy, capability checks, credential allocation, and LSM hooks stay centralized in the normal credential implementation.

State and persistence: the header stores no state. It defines a compile-time contract between compatibility wrappers and shared credential code.

Dependencies: depends on the standard Linux uid/gid typedefs being visible to including C files.

Risks and tests: signature drift between this header and the helper implementations would break builds or worse, call ABI expectations. Test signals are compile coverage for configurations enabling UID16 syscalls and runtime credential tests that compare old and modern syscall behavior after conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/umh.c -->
# sources/distributed-fs/ceph-client/kernel/umh.c

Purpose: implements the kernel usermode-helper facility used to spawn userspace programs from kernel context. It handles setup, credential preparation, wait modes, freezer/suspend disablement, running-helper accounting, static-helper disabling, and capability bounding sysctls.

Important APIs and state: public APIs are `call_usermodehelper_setup()`, `call_usermodehelper_exec()`, and `call_usermodehelper()`. Disable/locking APIs include `usermodehelper_read_trylock()`, `usermodehelper_read_lock_wait()`, `usermodehelper_read_unlock()`, `__usermodehelper_set_disable_depth()`, and `__usermodehelper_disable()`. Global state includes capability masks, `umhelper_sem`, `usermodehelper_disabled`, `running_helpers`, and waitqueues.

Control flow: setup allocates `subprocess_info`, initializes work, stores argv/envp/init/cleanup, and optionally replaces the path with `CONFIG_STATIC_USERMODEHELPER_PATH`. Exec rejects invalid paths or disabled state, handles an empty static path as a no-op, queues work to `system_unbound_wq`, and waits according to `UMH_NO_WAIT`, `UMH_WAIT_EXEC`, `UMH_WAIT_PROC`, `UMH_KILLABLE`, and `UMH_FREEZABLE`. Worker context creates a user-mode thread, prepares kernel creds, intersects capability masks, calls optional init, waits for initramfs, and executes the program.

State and persistence: helper lifetime is carried by `subprocess_info`; completion ownership uses `xchg()` to handle killable waiters and no-wait callers. Running-helper counts gate suspend/disable. Sysctls persist capability masks in memory.

Dependencies and integration: depends on workqueues, user-mode thread creation, credentials, freezer, initramfs, kernel execve, sysctl, and module trace events.

Risks: completion ownership is delicate; callers must not use `sub_info` after `UMH_NO_WAIT`. Disable depth races are controlled by rwsem and atomic helper counts. Capability sysctls only drop bits and require strong capabilities. Test signals include no-wait and wait-proc helpers, killable interruption, static helper empty path, suspend disable timeout, cleanup callbacks, and sysctl capability mask writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/umh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/Makefile -->
# sources/distributed-fs/ceph-client/kernel/unwind/Makefile

Purpose: builds the generic user-space unwind implementation when `CONFIG_UNWIND_USER` is enabled.

Important rule: `obj-$(CONFIG_UNWIND_USER) += user.o deferred.o` compiles both direct frame-pointer unwinding and deferred task-work unwinding as one feature.

Control flow and integration: the Makefile is the bridge from Kconfig to `kernel/unwind/user.o` and `kernel/unwind/deferred.o`. If the option is disabled, none of the generic user unwind code from this directory is linked.

State and persistence: no runtime state is defined here.

Dependencies and risks: build correctness depends on headers and architecture hooks required by both objects being available whenever `CONFIG_UNWIND_USER=y` or `m` is selected. Test signals are configuration build tests with the option enabled and disabled, including architectures with and without frame-pointer user unwind support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/deferred.c -->
# sources/distributed-fs/ceph-client/kernel/unwind/deferred.c

Purpose: provides deferred user-space stack unwinding for callers that request a user stack trace from contexts where faulting user memory is not safe. Requests are queued on task work and completed when the task reaches faultable exit-to-user context.

Important APIs and state: `unwind_deferred_init()` registers a callback work item and assigns a bit. `unwind_deferred_request()` schedules a trace for current. `unwind_deferred_cancel()` removes a callback and clears its bit from all tasks. `unwind_user_faultable()` performs or reuses the cached unwind. Task lifecycle hooks are `unwind_task_init()`, `unwind_task_free()`, and `unwind_deferred_task_exit()`. Per-task state lives in `current->unwind_info`; global callback state uses `callback_mutex`, `callbacks`, `unwind_mask`, and `unwind_srcu`.

Control flow: a request validates that current is a userspace task at a user-mode register frame, assigns a per-entry cookie with IRQs disabled, atomically sets the callback bit plus `UNWIND_PENDING`, and adds task work. On task work, `process_unwind_deferred()` clears pending, unwinds once into a per-task cache if needed, then walks registered callbacks under SRCU and invokes matching callbacks with the trace and cookie.

State and persistence: the cache survives within a task until freed or cleared on user return by users of `UNWIND_USED`. Callback bits remain reserved until cancellation. Cookies combine CPU and per-CPU context counters.

Dependencies and integration: depends on task_work, SRCU, user unwind core, task stack registers, mm presence, NMI-safe cmpxchg support, and task iteration for cancellation.

Risks: NMI use is architecture-gated. Atomic bit state must not lose callbacks. Cancellation must synchronize before clearing bits globally. Test signals include duplicate requests returning the same cookie, callback cancellation while tasks hold bits, NMI request behavior on unsupported architectures, task exit with pending unwind, and cache reuse across multiple callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/deferred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/user.c -->
# sources/distributed-fs/ceph-client/kernel/unwind/user.c

Purpose: implements generic user-space stack unwinding, currently centered on frame-pointer based unwinding when architecture support is present.

Important APIs: `unwind_user()` fills `struct unwind_stacktrace` with instruction pointers. Internal helpers include `unwind_user_start()`, `unwind_user_next()`, `unwind_user_next_fp()`, `unwind_user_next_common()`, and `get_user_word()`.

Control flow: start validates that current is not a kernel thread and that registers are in user mode, initializes IP, SP, FP, word size, and available unwind methods. The loop records the current IP, then advances using the selected method. Frame-pointer unwinding calculates CFA, validates stack growth, alignment, and user memory reads, loads return address and optional next frame pointer, and updates state. Failure marks the unwind done.

State and persistence: no global state is stored. The unwind state is stack-local, and output is caller-owned.

Dependencies and integration: depends on architecture macros such as `ARCH_INIT_USER_FP_FRAME`, `unwind_user_at_function_start()`, `unwind_user_word_size()`, register helpers, and `get_user()`. It is used directly and by deferred unwind.

Risks: user stacks are untrusted, so every frame transition must validate monotonic stack progress and alignment. Compat word-size handling matters on mixed 32/64-bit systems. Test signals include invalid user pointers, zero max entries, kernel threads, function-entry top frame handling, compat word size, and frame chains with malformed CFA/FP values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/up.c -->
# sources/distributed-fs/ceph-client/kernel/up.c

Purpose: provides uniprocessor implementations of selected SMP call APIs so common kernel code can use SMP-style helpers even when only CPU 0 exists.

Important APIs: `smp_call_function_single()`, `smp_call_function_single_async()`, `on_each_cpu_cond_mask()`, and `smp_call_on_cpu()` are exported.

Control flow: calls targeting any CPU other than 0 return `-ENXIO`. Synchronous and async single-CPU calls disable local interrupts, invoke the callback directly, and restore interrupts. `on_each_cpu_cond_mask()` disables preemption to mirror SMP calling conditions, tests the optional condition and mask for CPU 0, then calls with interrupts disabled. `smp_call_on_cpu()` optionally pins the vCPU through the hypervisor interface while calling the function.

State and persistence: no persistent state is maintained.

Dependencies and integration: integrates with generic SMP APIs, interrupt state handling, preemption, cpumasks, and hypervisor pinning.

Risks: the async variant ignores the `cpu` argument check present in the sync variant and directly invokes the callback, matching UP assumptions but relying on callers not passing invalid CPU in practice. Test signals include UP builds, callbacks observing interrupts disabled, conditional mask behavior, invalid CPU rejection, and hypervisor physical pin/unpin sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user-return-notifier.c -->
# sources/distributed-fs/ceph-client/kernel/user-return-notifier.c

Purpose: implements per-CPU notifier lists for callbacks that must run when the current CPU returns to userspace.

Important APIs: `user_return_notifier_register()`, `user_return_notifier_unregister()`, and `fire_user_return_notifiers()`.

Control flow: registration sets `TIF_USER_RETURN_NOTIFY` on current and links the notifier into the current CPU's per-CPU hlist. Unregistration removes the node and clears the thread flag if the current CPU list is empty. Firing pins the current CPU with `get_cpu_var()`, iterates safely over the hlist, invokes each notifier's `on_user_return()` callback, and releases the CPU variable.

State and persistence: state is per-CPU `return_notifier_list`; notifiers are caller-owned. Thread flag state marks whether return-to-user code should call the dispatcher.

Dependencies and integration: depends on scheduler thread flags, per-CPU storage, hlist helpers, and architecture return-to-user paths.

Risks: register/unregister must be called in atomic context and unregister must occur on the same CPU. Callback list mutation during firing is handled by safe iteration, but caller-owned lifetime remains critical. Test signals include same-CPU unregister, list-empty flag clearing, multiple notifiers firing, and callbacks unregistering themselves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user-return-notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user.c -->
# sources/distributed-fs/ceph-client/kernel/user.c

Purpose: defines the initial user namespace and manages `struct user_struct` objects used for per-UID resource accounting such as process counts, file counts, key quotas, ratelimits, and epoll watches.

Important APIs and state: `init_user_ns` is the root namespace with full uid/gid/projid maps. `root_user` is the initial user_struct. Public functions are `find_user()`, `alloc_uid()`, and `free_uid()`. Internal state includes `uid_cachep`, `uidhash_table`, and `uidhash_lock`. Optional `init_binfmt_misc` is exported for binfmt_misc.

Control flow: cache init creates the slab cache, initializes hash buckets, initializes root epoll counters, and inserts `root_user`. `alloc_uid()` first looks up under lock, allocates and initializes a new user if absent, then rechecks under lock before inserting to handle races. `free_uid()` decrements the refcount and frees under `uidhash_lock` when it reaches zero. `find_user()` returns an extra reference if found.

State and persistence: user_struct objects persist while referenced by credentials or resource users. Root namespace and root user are static. Epoll counters are allocated per user when configured.

Dependencies and integration: integrates with credentials, user namespaces, keyrings, binfmt_misc, epoll, ratelimit state, slab caches, and softirq-safe spin locking.

Risks: locking must be IRQ-safe because frees can happen with interrupts disabled or from softirq contexts. Allocation race handling must avoid duplicate user_structs. Test signals include concurrent `alloc_uid()` for the same UID, refcounted free, root_user lifetime, epoll counter allocation failure, and namespace root map correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user_namespace.c -->
# sources/distributed-fs/ceph-client/kernel/user_namespace.c

Purpose: implements user namespace creation, destruction, id mapping, `/proc/*/{uid,gid,projid}_map` writes, setgroups policy, and proc namespace operations. It is central to unprivileged namespace isolation and kernel ID translation.

Important APIs and state: creation APIs are `create_user_ns()` and `unshare_userns()`. Mapping APIs include `make_kuid()`, `from_kuid()`, `from_kuid_munged()`, kgid and kprojid variants, `map_id_down()`, `map_id_up()`, and range helpers. Proc write APIs are `proc_uid_map_write()`, `proc_gid_map_write()`, `proc_projid_map_write()`, and `proc_setgroups_write()`. `userns_operations` exposes namespace get/put/install/owner hooks. `userns_state_mutex` serializes map and setgroups state.

Control flow: namespace creation checks nesting depth, ucount limits, chroot restrictions, parent mappings for creator IDs, LSM approval, memory allocation, ns common init, inherited flags, sysctl setup, credential capability reset, and namespace-tree insertion. Freeing is deferred through work and walks parent references while freeing large idmap arrays, sysctls, keys, binfmt_misc, and ns common state. ID maps use small inline extent arrays or larger sorted forward/reverse arrays for bsearch.

Map writes are one-shot, page-sized, offset-zero only operations. `map_write()` parses extents, rejects wraparound, overlap, empty maps, excessive lines, unauthorized writers, and unmappable parent IDs, then sorts and publishes extents with a write barrier before setting `nr_extents`. `new_idmap_permitted()` allows narrow self maps, capability-based maps, and special project-id maps; `verify_root_map()` protects uid 0 mappings and file capabilities.

State and persistence: user namespaces persist via ns refs and parent chains. Maps become immutable after first successful write. Setgroups can be permanently denied before gid_map is written. Ucount and rlimit limits are inherited at creation.

Dependencies and integration: depends on credentials, LSM, procfs seq files, nsfs operations, ucounts, keyrings, binfmt_misc, nstree, sort/bsearch, and user access.

Risks: this is security-sensitive. Bugs can grant capabilities, incorrect ID mappings, or setgroups access. Barriers around map publication protect lockless readers. Test signals include unprivileged user namespace creation, chroot denial, nested depth, root uid map with/without CAP_SETFCAP, overlapping/wrapping extent rejection, large extent sorting, setgroups deny-before-gid-map, namespace install constraints, and id translation round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname.c -->
# sources/distributed-fs/ceph-client/kernel/utsname.c

Purpose: manages UTS namespaces, which isolate hostname and domainname values. It supports cloning, reference management, namespace install, ownership, and initialization.

Important APIs and state: `copy_utsname()` clones or references an existing namespace based on `CLONE_NEWUTS`. `free_uts_ns()` releases namespace resources. `utsns_operations` implements proc namespace get/put/install/owner. `uts_ns_init()` creates the slab cache and registers `init_uts_ns` with the namespace tree.

Control flow: cloning charges `UCOUNT_UTS_NAMESPACES` against the target user namespace and current euid, allocates a namespace, initializes ns_common, copies the old uts name under `uts_sem`, takes a user namespace reference, and inserts into nstree. Copying without `CLONE_NEWUTS` just takes a reference. Installation requires CAP_SYS_ADMIN in both the target UTS namespace owner and the caller credential namespace, then swaps `nsproxy->uts_ns`.

State and persistence: each UTS namespace stores copied `struct new_utsname`, user namespace owner, ucounts reference, and ns_common. Freeing removes it from nstree, decrements ucounts, drops user_ns, and RCU-frees after ns common cleanup.

Dependencies and integration: depends on ucounts, user namespaces, nsproxy, proc_ns, uts_sem, slab usercopy cache, and nstree.

Risks: namespace limits and references must unwind on clone failures. Installing across namespaces is capability-sensitive. Test signals include CLONE_NEWUTS hostname isolation, ucount exhaustion, setns permission checks, concurrent reads while cloning, and namespace tree traversal during free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname_sysctl.c -->
# sources/distributed-fs/ceph-client/kernel/utsname_sysctl.c

Purpose: exposes UTS namespace fields through `/proc/sys/kernel` sysctls such as hostname, domainname, ostype, osrelease, version, and arch.

Important APIs and state: `proc_do_uts_string()` is the namespace-aware sysctl handler. `uts_kern_table` defines entries and modes. `uts_proc_notify()` notifies poll waiters for selected UTS fields. `utsname_sysctl_init()` registers the table. Poll state exists for hostname and domainname.

Control flow: `get_uts()` translates a table data pointer based on the offset from `init_uts_ns` to the current task's UTS namespace. The handler copies the current value under `uts_sem`, drops the lock while calling `proc_dostring()`, and on write adds device randomness, writes the updated value back under write lock, and notifies pollers.

State and persistence: values live inside the current UTS namespace. Sysctl table entries are global but dynamically redirected to current namespace storage by pointer offset arithmetic.

Dependencies and integration: depends on proc sysctl, current nsproxy, `uts_sem`, random device entropy mixing, and sysctl poll notification.

Risks: the handler acknowledges parallel partial writes can produce theoretically incorrect combined results because it drops `uts_sem` during `proc_dostring()`. Pointer offset mapping assumes table data points into `init_uts_ns`. Test signals include per-namespace hostname/domainname reads and writes, poll notification, read-only entries, partial writes, and concurrent writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vhost_task.c -->
# sources/distributed-fs/ceph-client/kernel/vhost_task.c

Purpose: creates and manages specialized user-worker tasks for vhost. These tasks run a caller-provided work function in a loop, share selected process resources, and handle stop versus SIGKILL races.

Important APIs and state: `vhost_task_create()` allocates the wrapper and uses `copy_process()` with user-worker clone args. `vhost_task_start()` wakes the new task. `vhost_task_wake()` wakes a running task. `vhost_task_stop()` requests stop, waits for exit, drops task ref, and frees the wrapper. `struct vhost_task` stores callbacks, data, completion, flags, task pointer, and `exit_mutex`.

Control flow: the worker loop consumes pending signals, sets interruptible state, exits if STOP is set, calls `fn(data)`, and schedules when no work was done. On exit it serializes with `vhost_task_stop()`; if STOP was not set, it marks KILLED and calls `handle_sigkill(data)`, then completes and exits.

State and persistence: lifecycle state is in STOP and KILLED bits plus the completion. The wrapper persists from create until stop frees it. The task is inactive until explicitly started.

Dependencies and integration: depends on kernel clone internals, user-worker task flags, completions, signals, scheduler wakeups, and vhost layer callbacks.

Risks: stop and SIGKILL race handling is central; vhost stop assumes upper layers have stopped new work and flushed before freeing. Callback `fn` must cooperate by returning false when idle. Test signals include create/start/stop, wakeups from idle, SIGKILL handling before stop, concurrent stop and signal, callback work/no-work behavior, and copy_process failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vhost_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vmcore_info.c -->
# sources/distributed-fs/ceph-client/kernel/vmcore_info.c

Purpose: builds and updates the `VMCOREINFO` ELF note used by crash dump tooling to interpret kernel memory after kexec/kdump. It records kernel layout, type sizes, offsets, symbols, page flags, build ID, and crash-time data.

Important APIs and state: global state includes `vmcoreinfo_data`, `vmcoreinfo_size`, `vmcoreinfo_note`, `vmcoreinfo_data_safecopy`, and `hwerr_data`. Public helpers include `append_elf_note()`, `final_note()`, `crash_update_vmcoreinfo_safecopy()`, `crash_save_vmcoreinfo()`, `vmcoreinfo_append_str()`, weak `arch_crash_save_vmcoreinfo()`, weak/exported `paddr_vmcoreinfo_note()`, and `hwerr_log_error_type()`.

Control flow: init allocates a data buffer and note buffer, appends standard OS/build/page/memory-management metadata through `VMCOREINFO_*` macros, lets architecture code append extra data, and writes the ELF note. On crash save, it switches to a safe copy if one exists, appends `CRASHTIME`, and updates the note. Hardware error logging increments per-type counters and records timestamps.

State and persistence: vmcoreinfo buffers are allocated for kernel lifetime and consumed by crash/kexec paths. `vmcoreinfo_size` monotonically grows until full; overflow is truncated with a warning. Safe copy pointer can redirect writes for crash memory.

Dependencies and integration: depends on kexec/crash infrastructure, ELF notes, memblock/memory layout symbols, kallsyms, build ID, log buffer vmcoreinfo, architecture sections, and optional memory model configs.

Risks: truncation can omit metadata needed by dump tools. Note buffer allocation failure disables vmcoreinfo. Architecture overrides must preserve format. Test signals include boot-time vmcoreinfo allocation, generated note parsing by crash tools, crash-time CRASHTIME update, safe-copy use, memory model config coverage, and hardware error counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vmcore_info.c -->
