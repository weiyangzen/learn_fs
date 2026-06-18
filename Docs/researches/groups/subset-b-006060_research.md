# sources/distributed-fs/ceph-client/kernel subset-b-006060 research

Grouped source-tree-aligned research for subset `subset-b-006060`. Each section is bounded for reconciliation into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/smpboot.c -->
# sources/distributed-fs/ceph-client/kernel/smpboot.c

## Purpose
`smpboot.c` provides common SMP CPU bring-up/teardown helpers for idle threads and per-CPU hotplug kthreads. It lets subsystems describe a `struct smp_hotplug_thread` and receive one parked/unparked kernel thread per CPU as CPUs become online or offline.

## Important APIs, types, and functions
- `idle_thread_get()`, `idle_thread_set_boot_cpu()`, `idle_threads_init()`: manage per-CPU idle task pointers when `CONFIG_GENERIC_SMP_IDLE_THREAD` is enabled.
- `struct smpboot_thread_data`: per-created-thread private state containing CPU id, lifecycle status, and owning `struct smp_hotplug_thread`.
- `smpboot_thread_fn()`: generic body for registered hotplug threads. It handles stop, park, setup, unpark, sleep, and runnable callbacks.
- `smpboot_create_threads()`, `smpboot_park_threads()`, `smpboot_unpark_threads()`: CPU hotplug entry points that iterate all registered descriptors.
- `smpboot_register_percpu_thread()` / `smpboot_unregister_percpu_thread()`: exported registration API for subsystems such as softirq and stop-machine.

## Control flow
Idle initialization stores the boot CPU's current task and calls `fork_idle()` for every other possible CPU. Hotplug thread registration acquires `cpus_read_lock()` and `smpboot_threads_lock`, creates a parked kthread on every online CPU, unparks it, then adds the descriptor to `hotplug_threads`. The per-thread loop transitions from `HP_THREAD_NONE` to `HP_THREAD_ACTIVE` through optional `setup()`, responds to `kthread_should_park()` through optional `park()` and `kthread_parkme()`, responds to stop by running optional `cleanup()`, and otherwise sleeps until `thread_should_run()` permits `thread_fn()` to execute on the bound CPU.

## State and persistence
Persistent runtime state is all in-kernel: `idle_threads` per-CPU task pointers, `hotplug_threads` global list, per-descriptor task storage addressed by `ht->store`, and each thread's `HP_THREAD_*` status. Threads for offline CPUs are kept parked so they can be reused, and `smpboot_destroy_threads()` stops possible-CPU threads on unregister.

## Dependencies and integration points
This file depends on CPU hotplug locks, percpu storage, kthreads, scheduler CPU binding, and `linux/smpboot.h`. It is consumed by per-CPU worker subsystems including `softirq.c` (`ksoftirqd` and optional `ktimers`) and `stop_machine.c` (`migration/%u` stopper threads). `wait_task_inactive(TASK_PARKED)` is used before `create()` callbacks that require the task to be off-runqueue.

## Risks
Lifecycle callbacks must tolerate exact CPU affinity and the status transitions enforced here. `BUG_ON(td->cpu != smp_processor_id())` turns CPU-affinity violations into fatal errors. `selfparking` descriptors are not unparked/parked by generic helpers, so descriptor authors must implement their own synchronization. Registration failure destroys threads already created for that descriptor.

## Test signals
Useful validation is CPU hotplug stress with registered users (`ksoftirqd`, stopper threads), boot on SMP and UP-like configs, and lockdep coverage of the register/unregister paths. Failures usually appear as missing per-CPU threads, warnings from `wait_task_inactive()`, CPU mismatch `BUG_ON()`, or hotplug stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/smpboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/smpboot.h -->
# sources/distributed-fs/ceph-client/kernel/smpboot.h

## Purpose
`smpboot.h` is the local kernel header for SMP boot helpers implemented in `smpboot.c`. It exposes idle-thread setup only when generic SMP idle threads are configured and declares hotplug thread lifecycle hooks used by CPU hotplug code.

## Important APIs, types, and functions
- `struct task_struct` forward declaration avoids pulling scheduler internals into every includer.
- `idle_thread_get()`, `idle_thread_set_boot_cpu()`, `idle_threads_init()` are real declarations under `CONFIG_GENERIC_SMP_IDLE_THREAD` and no-op/NULL inlines otherwise.
- `smpboot_create_threads()`, `smpboot_park_threads()`, `smpboot_unpark_threads()` are CPU-specific hotplug lifecycle calls.
- `cpuhp_threads_init()` is declared as an init-time CPU hotplug thread setup hook.

## Control flow
The header itself has no runtime control flow, but its config guards select either real idle-thread helpers or inert stubs. That lets generic code compile across architectures that do not use the common idle-thread implementation.

## State and persistence
No state is defined here. State lives in `smpboot.c` or in descriptors owned by users of the public `linux/smpboot.h` API.

## Dependencies and integration points
The header is included by common SMP bring-up code and indirectly supports subsystem integration with CPU hotplug. It must stay synchronized with `smpboot.c` function definitions and the CPU hotplug state machine.

## Risks
The main risk is declaration drift: mismatched init attributes or function signatures would break early-boot/hotplug code. The fallback `idle_thread_get()` returns `NULL`, so callers must only rely on it where generic idle threads are enabled or handle the stub result.

## Test signals
Build coverage across `CONFIG_GENERIC_SMP_IDLE_THREAD=y/n` is the primary signal. CPU hotplug boot tests validate that the declared lifecycle hooks are wired to definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/smpboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/softirq.c -->
# sources/distributed-fs/ceph-client/kernel/softirq.c

## Purpose
`softirq.c` implements Linux softirq dispatch, bottom-half enable/disable accounting, tasklets, interrupt entry/exit softirq invocation, and the per-CPU `ksoftirqd` fallback threads. It is the common deferred interrupt work engine used by networking, timers, RCU, block IRQ polling, scheduler, tasklets, and workqueue softirq actions.

## Important APIs, types, and functions
- Global/per-CPU state: `softirq_vec[NR_SOFTIRQS]`, `irq_stat`, `ksoftirqd`, `softirq_to_name`, and tasklet per-CPU queues.
- Bottom-half APIs: `__local_bh_disable_ip()`, `__local_bh_enable_ip()`, `_local_bh_enable()` on non-RT, and `local_bh_blocked()` on RT.
- Dispatch APIs: `open_softirq()`, `raise_softirq()`, `raise_softirq_irqoff()`, `__raise_softirq_irqoff()`, `do_softirq()`, `__do_softirq()`.
- IRQ integration: `irq_enter_rcu()`, `irq_enter()`, `irq_exit_rcu()`, `irq_exit()`, `do_softirq_post_smp_call_flush()` on RT.
- Tasklet APIs: `tasklet_setup()`, `tasklet_init()`, `__tasklet_schedule()`, `__tasklet_hi_schedule()`, `tasklet_kill()`, `tasklet_unlock_wait()`, `tasklet_unlock_spin_wait()`.
- Threading: `softirq_threads` descriptor for `ksoftirqd/%u`; optional forced-threading `timer_thread` for `ktimers/%u`.

## Control flow
Softirq producers set a per-CPU pending bit with interrupts disabled. Interrupt exit checks pending work after decrementing hardirq context and either runs softirqs inline/on the IRQ stack or wakes `ksoftirqd`, depending on context and forced IRQ threading. `handle_softirqs()` snapshots pending bits, clears the per-CPU pending word, enables interrupts, invokes each registered action with tracing/stat accounting, then loops for bounded restarts until time, reschedule, or restart limits force wakeup of `ksoftirqd`. Tasklet scheduling appends to a per-CPU list and raises `TASKLET_SOFTIRQ` or `HI_SOFTIRQ`; the action drains the list, runs enabled tasklets under per-tasklet serialization, and requeues locked/disabled tasklets.

## State and persistence behavior
Softirq state is transient, CPU-local kernel state: pending bitmaps, per-CPU tasklet lists, `ksoftirqd` task pointers, optional timer-thread pending masks, and RT-specific `softirq_ctrl` counters/locks. No userspace-persistent state is stored. Pending work migrates during CPU hotplug through `takeover_tasklets()` and `workqueue_softirq_dead()`.

## Dependencies and integration points
This file integrates with interrupt entry code, RCU context tracking, tick/nohz handling, hrtimer deferred rearming, workqueues, tracing (`trace/events/irq.h`), kernel stats, lockdep, freezer/kthreads, `smpboot_register_percpu_thread()`, and optional PREEMPT_RT behavior. It relies on architecture softirq stack helpers and optional `CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK`.

## Risks
Softirq dispatch is latency-critical and concurrency-sensitive. Incorrect preempt count restoration is detected and repaired with an error log, but indicates broken handlers. Starvation risk is bounded by `MAX_SOFTIRQ_TIME` and `MAX_SOFTIRQ_RESTART`; changing these affects latency/fairness. PREEMPT_RT paths split accounting between task and per-CPU counters, so lock/unlock imbalance can block softirq progress. Tasklets are legacy and risky when killed or waited from interrupt/atomic contexts.

## Test signals
Signals include boot-time softirq init, CPU hotplug with pending tasklets, networking/timer/RCU load, lockdep IRQ flag tests, PREEMPT_RT bottom-half tests, forced IRQ threading, and tracepoints for raise/entry/exit. Runtime warnings about preempt count mismatch, tasklet state mismatch, or local BH misuse are high-value regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/softirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/kernel/stacktrace.c

## Purpose
`stacktrace.c` provides generic stack trace collection and formatting wrappers over architecture stack walkers, with fallback support for architectures that still expose legacy `save_stack_trace*()` helpers. It also filters IRQ-stack frames for callers that need to trim traces at interrupt boundaries.

## Important APIs, types, and functions
- Formatting: `stack_trace_print()` and `stack_trace_snprint()` print symbolized entries.
- Collection with `CONFIG_ARCH_STACKWALK`: `stack_trace_save()`, `stack_trace_save_tsk()`, `stack_trace_save_regs()`, optional `stack_trace_save_tsk_reliable()`, and `stack_trace_save_user()`.
- Legacy fallback: weak `save_stack_trace_tsk()` / `save_stack_trace_regs()` warnings and wrappers around `struct stack_trace`.
- Internal `struct stacktrace_cookie` tracks output buffer, size, skip count, and number stored.
- `filter_irq_stacks()` returns the count up to and including the first irq/softirq entry text frame.

## Control flow
Formatting functions iterate the stored addresses and emit `%pS` symbol names. Modern collection initializes a cookie, then calls `arch_stack_walk()` or variants; callback functions skip initial frames and stop when storage fills. Task collection pins the target task stack with `try_get_task_stack()` and drops it afterward. Reliable stack traces delegate validation to `arch_stack_walk_reliable()`. User stack tracing refuses kernel threads and walks from `task_pt_regs(current)`.

## State and persistence behavior
The file stores no persistent state. All state is per-call stack buffers supplied by callers. Task stack references are temporary and refcounted.

## Dependencies and integration points
It depends on scheduler task-stack helpers, kallsyms formatting, interrupt text section symbols, and architecture stackwalk implementations. Exported functions are used by diagnostics, procfs/debugfs, tracing, livepatch/reliability checks, and subsystem error paths.

## Risks
Reliability depends on architecture support; weak fallback emits one-time warnings and cannot guarantee completeness. Callers must size buffers correctly and respect that stack traces can be truncated. Non-current task traces are only safe when the task stack can be pinned, and reliable traces require caller-side inactivity guarantees for non-current tasks.

## Test signals
Build both `CONFIG_ARCH_STACKWALK` and legacy paths, exercise `/proc`/debug stack trace consumers, run livepatch reliable stacktrace tests where available, and verify user stack traces skip kernel threads. `WARN_ON(!entries)` and once-per-boot "not implemented" warnings identify misuse or missing arch support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/static_call.c -->
# sources/distributed-fs/ceph-client/kernel/static_call.c

## Purpose
`static_call.c` provides a tiny default static-call target, `__static_call_return0()`, that returns zero. It is used as a safe no-op/zero-return function for static call sites that need a valid callable target.

## Important APIs, types, and functions
- `long __static_call_return0(void)`: returns `0`.
- `EXPORT_SYMBOL_GPL(__static_call_return0)`: makes the helper available to GPL modules and core static call users.

## Control flow
There is no branching. Callers enter the helper and receive `0`.

## State and persistence behavior
No state is read or written.

## Dependencies and integration points
It includes `linux/static_call.h` and integrates with the static-call framework implemented by architecture code and `static_call_inline.c`.

## Risks
The helper is intentionally simple. The main risk is ABI/semantic mismatch if a static call site expects a non-`long` return or side effects; those sites must use correctly typed wrappers from the static-call macros.

## Test signals
Build/link coverage and static-call selftests are sufficient. Runtime signal is absence of unresolved `__static_call_return0` references when static calls or modules use a zero-return default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/static_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/static_call_inline.c -->
# sources/distributed-fs/ceph-client/kernel/static_call_inline.c

## Purpose
`static_call_inline.c` initializes, sorts, tracks, and patches inline static call sites for the core kernel and modules. Static calls let a call site be dynamically retargeted with near-direct-call performance by patching text rather than using an indirect call.

## Important APIs, types, and functions
- `static_call_initialized` and `static_call_force_reinit()` manage init state and early reinit behavior.
- Address/key helpers decode relative `struct static_call_site` fields and site flags (`INIT`, `TAIL`).
- `__static_call_update()` changes a key's target function, patches the trampoline, then patches all eligible call sites for built-in and module users.
- `__static_call_init()` sorts call sites by key, marks init-section sites, links sites into key metadata, and applies initial architecture transforms.
- Module integration: `static_call_add_module()`, `static_call_del_module()`, `static_call_module_notify()`, and `static_call_module_nb`.
- Text reservation: `static_call_text_reserved()` checks whether a text range overlaps static-call patch sites.
- Optional selftest defines `sc_selftest`, updates it between `func_a` and `func_b`, and verifies results.

## Control flow
Early init calls `static_call_init()`, which locks CPU hotplug and `static_call_mutex`, initializes all built-in sites, registers the module notifier, then marks the framework initialized. Updating a key locks the same domains, exits early if the target did not change, patches the trampoline, and walks each associated site list, skipping init-only sites after init and warning on non-text addresses. When modules load, raw trampoline references are fixed up to real keys, module sites are initialized and linked; on unload their `static_call_mod` records are removed.

## State and persistence behavior
State is stored in static-call keys, their `func` pointer, their site pointer or module list, and module-owned `static_call_mod` allocations. The framework permanently patches executable text until later updates repatch it. Init-section markers prevent patching discarded init text after boot.

## Dependencies and integration points
It depends on linker sections for `__start/__stop_static_call_sites` and `__start/__stop_static_call_tramp_key`, architecture `arch_static_call_transform()`, CPU hotplug read locking, module notifier callbacks, `sort()`, kernel text address validation, and module text lookup. It integrates with live text patching reservations through `static_call_text_reserved()`.

## Risks
Text patching requires strict synchronization and accurate site metadata. Bad module fixups can expose sensitive static-call keys, so non-exported module references are resolved through trampoline-key lookup. Allocation failure during module init must unwind partial state. Incorrect init-section classification could patch freed text or leave live sites stale.

## Test signals
`CONFIG_STATIC_CALL_SELFTEST` provides a direct behavior check. Additional signals are module load/unload tests with static calls, architecture text-patching tests, lockdep around `static_call_mutex`/CPU locks, warnings from "can't patch static call site", and failures from module fixup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/static_call_inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/stop_machine.c -->
# sources/distributed-fs/ceph-client/kernel/stop_machine.c

## Purpose
`stop_machine.c` implements high-priority per-CPU stopper threads and the `stop_machine()` family. It can run callbacks with one or many CPUs monopolized, including full-machine stop phases for text patching, CPU hotplug, migration, and other synchronization-heavy kernel operations.

## Important APIs, types, and functions
- `struct cpu_stopper`: per-CPU stopper state, including stopper thread, raw spinlock, enabled flag, pending work list, static `stop_work`, caller, and current function.
- `struct cpu_stop_done`: shared completion and return aggregation for queued stopper works.
- Public APIs: `stop_one_cpu()`, `stop_two_cpus()`, `stop_one_cpu_nowait()`, `stop_machine_cpuslocked()`, `stop_machine()`, optional `stop_core_cpuslocked()`, and `stop_machine_from_inactive_cpu()`.
- State machine: `enum multi_stop_state`, `struct multi_stop_data`, `set_state()`, `ack_state()`, and `multi_cpu_stop()`.
- Hotplug integration: `cpu_stop_threads`, `cpu_stop_init()`, `stop_machine_park()`, `stop_machine_unpark()`.

## Control flow
`cpu_stop_init()` initializes per-CPU locks/lists, registers `migration/%u` stopper threads via smpboot, and enables the boot CPU stopper. Single-CPU stop queues a work item and waits on completion. Multi-CPU stop initializes `multi_stop_data`, queues work on target stoppers under serialization, and each stopper advances through prepare, IRQ-disable, run, and exit phases using an atomic acknowledgement counter. `stop_machine()` holds the CPU hotplug read lock and queues `multi_cpu_stop` on all online CPUs; early boot falls back to direct local execution with IRQs disabled. Inactive CPU hotplug callers busy-wait on `stop_cpus_mutex`, queue active CPUs, and execute locally without sleeping.

## State and persistence behavior
Runtime state is per-CPU and transient: stopper work queues, enabled flags, current callback/caller for diagnostics, and completion counters. `stop_cpus_mutex` serializes multi-CPU stop requests using static work storage. `stop_machine_initialized` gates early-boot fallback.

## Dependencies and integration points
The implementation integrates with smpboot hotplug threads, scheduler stop tasks, CPU masks, CPU hotplug locks, raw spinlocks, completions, NMI watchdog/RCU stall suppression, SMT sibling masks, and diagnostic `print_stop_info()`. It is a common substrate for kernel text patching and CPU migration machinery.

## Risks
Stopper callbacks must not sleep; the stopper thread increments preempt count to enforce atomic-like context and warns if callbacks leak preempt count. Queue ordering between `stop_two_cpus()` and `stop_cpus()` is deadlock-sensitive and guarded by `stop_cpus_in_progress`. Offline CPUs can cause `-ENOENT` or partial execution, so callers must hold appropriate hotplug locks when CPU stability matters.

## Test signals
CPU hotplug stress, stop_machine users such as static key/text patching, SMT stop-core tests, lockdep, and watchdog behavior are key. Warnings for leaked preempt count, non-empty work lists at park, or deadlocked stop operations indicate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/stop_machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sys.c -->
# sources/distributed-fs/ceph-client/kernel/sys.c

## Purpose
`sys.c` is a large collection of core process, credential, resource-limit, UTS, accounting, `prctl`, CPU, and system-information syscalls. It provides user/kernel ABI glue for identity changes, process groups/sessions, uname/hostname/domainname, rlimits, rusage, process controls, `getcpu()`, and `sysinfo()`.

## Important APIs, types, and functions
- Overflow identity sysctls: `overflowuid`, `overflowgid`, `fs_overflowuid`, `fs_overflowgid`, and `init_overflow_sysctl()`.
- Priority syscalls: `setpriority()`/`getpriority()` plus permission helpers `set_one_prio_perm()` and `set_one_prio()`.
- Credential syscalls under `CONFIG_MULTIUSER`: `__sys_setregid()`, `__sys_setgid()`, `__sys_setreuid()`, `__sys_setuid()`, `__sys_setresuid()`, `__sys_setresgid()`, `__sys_setfsuid()`, `__sys_setfsgid()`, and matching syscall wrappers/getters.
- Basic IDs/timing: `getpid()`, `gettid()`, `getppid()`, UID/GID getters, `times()`, compat `times()`.
- Process groups/sessions: `setpgid()`, `getpgid()`, `getsid()`, `ksys_setsid()`, `setsid()`.
- UTS operations: `newuname()`, legacy uname variants, `sethostname()`, `gethostname()`, `setdomainname()`.
- Resource usage/limits: `do_prlimit()`, `getrlimit()`, `setrlimit()`, `prlimit64()`, `getrusage()`, compat variants, `umask()`.
- `prctl()` and helpers for MM metadata, auxv, child subreaper, no-new-privs, THP disable, MDWE, syscall user dispatch, KSM, RISC-V/vector hooks, CFI/shadow stack hooks, timers, futex, rseq, and architecture-specific controls.
- Misc: `getcpu()`, `do_sysinfo()`, `sysinfo()`, compat `sysinfo()`.

## Control flow
Most syscalls validate user arguments, translate namespace IDs, perform capability/LSM checks, then update task, signal, mm, fs, or UTS state under the appropriate lock. Credential setters allocate new credentials with `prepare_creds()`, modify UID/GID fields, update user accounting/ucounts where needed, call LSM fixup hooks, flag deferred NPROC overflow, and `commit_creds()`. Process group/session syscalls hold `tasklist_lock` to stabilize parent and PID relationships. `prlimit64()` copies optional new limits, checks cross-task permissions under RCU, pins the target task, optionally holds `tasklist_lock`, calls `do_prlimit()`, and copies old limits back. `prctl()` first lets LSM handle options, then dispatches a large option switch to core or architecture hooks.

## State and persistence behavior
The file mutates long-lived kernel state: current credentials, user structs, ucounts, task nice values, signal rlimits/accounting, process group/session PID links, UTS namespace names, mm metadata and flags, task flags, timer slack, no-new-privs, KSM merge state, and filesystem umask. These changes persist for the task, thread group, namespace, or system until explicitly changed or the object exits. Sysinfo/getrusage/times are read-only snapshots.

## Dependencies and integration points
`sys.c` integrates with namespaces, credentials, capabilities, LSM hooks, proc connectors, scheduler/autogroup, PID/tasklist locking, UTS namespace notifications, resource limits, POSIX timers, memory management, checkpoint/restore, seccomp, perf, syscall user dispatch, futex, rseq, KSM, architecture prctl macros, time namespaces, memory statistics, and compat ABI conversion.

## Risks
This is security- and ABI-critical code. Risks include privilege escalation through incomplete namespace/capability checks, credential lifetime mistakes, tasklist/RCU races, ABI regressions in legacy/compat syscalls, integer conversion errors in rlimits/sysinfo, and unsafe `prctl(PR_SET_MM*)` validation. Many setters intentionally return old values or defer errors for historical compatibility, so behavior changes can break userspace.

## Test signals
Strong signals come from LTP syscall tests, kselftests for prctl/seccomp/rseq/futex/user namespaces, compat ABI testing, container namespace tests, rlimit/CPU timer tests, and security regression tests. Kernel warnings, LSM denials, failed copy_to/from_user paths, and tracepoint `task_prctl_unknown` are useful runtime indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sys_ni.c -->
# sources/distributed-fs/ceph-client/kernel/sys_ni.c

## Purpose
`sys_ni.c` provides weak/fallback entries for system calls that are not implemented by the current architecture or kernel configuration. Missing syscalls resolve to `sys_ni_syscall()` and return `-ENOSYS`.

## Important APIs, types, and functions
- `sys_ni_syscall()`: generic not-implemented syscall body.
- `COND_SYSCALL(name)` and `COND_SYSCALL_COMPAT(name)`: macros that map missing `sys_*` or `compat_sys_*` symbols to conditional syscall stubs, optionally overridden by architecture syscall wrapper support.
- The ordered list mirrors `include/uapi/asm-generic/unistd.h`, followed by architecture-specific, deprecated, obsolete, restartable sequence, uprobe, and uretprobe entries.

## Control flow
There is no runtime dispatch beyond a caller landing in a missing syscall stub and receiving `-ENOSYS`. Compile/link-time `cond_syscall()` machinery resolves absent implementations in the syscall table.

## State and persistence behavior
No state is read or written.

## Dependencies and integration points
It depends on architecture syscall wrapper conventions, `asm/unistd.h`, and weak syscall resolution. The file is part of the syscall table link contract, especially for optional features like AIO, io_uring, ipc, sockets, timers, BPF, seccomp, fanotify, memory policy, compat time32, and arch-specific syscalls.

## Risks
Ordering drift from `asm-generic/unistd.h` or missing a new optional syscall can create link failures or wrong ABI behavior. Accidentally providing a fallback for a syscall that should be mandatory can hide configuration bugs; omitting one can break allmodconfig/defconfig variants.

## Test signals
Build matrix coverage across architectures and feature configs is primary. Runtime tests should observe `ENOSYS` for configured-out optional syscalls and real behavior for enabled syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sys_ni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sysctl-test.c -->
# sources/distributed-fs/ceph-client/kernel/sysctl-test.c

## Purpose
`sysctl-test.c` is a KUnit suite for proc sysctl integer handling, focused on `proc_dointvec()` edge cases and basic read/write behavior.

## Important APIs, types, and functions
- Test constants `KUNIT_PROC_READ` and `KUNIT_PROC_WRITE`.
- Edge-case tests for NULL `.data`, zero `.maxlen`, zero user length, and non-zero read file position.
- Happy-path tests for reading positive/negative integers and writing positive/negative integers.
- Boundary tests for values below `INT_MIN` and above `INT_MAX`.
- `sysctl_test_cases` and `sysctl_test_suite`, registered with `kunit_test_suites()`.

## Control flow
Each test builds a local `struct ctl_table`, allocates a user-like buffer with KUnit allocation helpers, calls `proc_dointvec()`, and checks return codes, length/position updates, output strings, and stored integer values. The suite is collected into an array and registered as module/built-in KUnit tests.

## State and persistence behavior
All state is test-local and allocated through KUnit. No global sysctl state is registered or mutated.

## Dependencies and integration points
The suite depends on KUnit and the sysctl proc handler API in `linux/sysctl.h`. It directly exercises implementation from `sysctl.c`, and its module metadata declares GPL licensing.

## Risks
The tests cast KUnit kernel allocations to `__user` pointers because the handler API is shaped around proc user buffers; this is intentional in KUnit context but should not be copied into production code. Coverage is narrow: it does not cover unsigned handlers, min/max success/failure, strings, large bitmaps, or strict write-position modes beyond the read non-zero case.

## Test signals
The signal is the KUnit suite `sysctl_test`. Failures point to regressions in length handling, position handling, integer parsing, overflow rejection, or signed conversion in `proc_dointvec()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sysctl-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sysctl.c -->
# sources/distributed-fs/ceph-client/kernel/sysctl.c

## Purpose
`sysctl.c` implements generic sysctl proc handlers for strings, signed/unsigned integer vectors, bools, u8 values, unsigned long vectors, large bitmaps, and static keys. It also registers a few base `kernel.*` sysctls and provides `-ENOSYS` stubs when proc sysctl support is disabled.

## Important APIs, types, and functions
- Shared exported constants: `sysctl_vals[]` and `sysctl_long_vals[]`.
- String handler: `_proc_do_string()` and exported `proc_dostring()`.
- Numeric parsing/output helpers: `strtoul_lenient()`, `proc_get_long()`, `proc_put_long()`, `proc_put_char()`, whitespace/skipping helpers.
- Conversion helpers: `proc_uint_u2k_conv_uop()`, `proc_uint_k2u_conv()`, `proc_uint_conv()`, `proc_int_k2u_conv_kop()`, `proc_int_u2k_conv_uop()`, `proc_int_conv()`.
- Proc handlers: `proc_dointvec()`, `proc_douintvec()`, `proc_dointvec_minmax()`, `proc_douintvec_minmax()`, `proc_dou8vec_minmax()`, `proc_doulongvec_minmax()`, `proc_doulongvec_minmax_conv()`, `proc_dointvec_conv()`, `proc_douintvec_conv()`, `proc_do_large_bitmap()`.
- Static-key handler: `proc_do_static_key()`.
- Base table: `sysctl_subsys_table` and `sysctl_init_bases()`.

## Control flow
Read handlers validate table data/maxlen and file position, convert kernel values to ASCII, append delimiters/newlines, update `lenp` and `ppos`, and use `READ_ONCE()` where appropriate. Write handlers enforce strict/warn/legacy write-position policy, cap input parsing to page-sized chunks, parse ASCII numbers, validate sign/range/min/max, write values with `WRITE_ONCE()`, and update file position. Large bitmap writes parse comma/range syntax into a temporary bitmap and copy/or it into the destination depending on position. Static-key writes require `CAP_SYS_ADMIN`, read/update a temporary int through min/max int handling, then enable or disable the static key under a mutex.

## State and persistence behavior
Most handlers mutate external kernel variables referenced by `struct ctl_table::data`; this file supplies parsing and validation but not ownership of those variables. Internal persistent state includes `sysctl_writes_strict` and the base kernel sysctl table. When `CONFIG_PROC_SYSCTL` is absent, exported handlers persist as stubs returning `-ENOSYS`.

## Dependencies and integration points
It integrates with procfs sysctl registration, `struct ctl_table`, capability checks, static keys, bitmap allocation/parsing, `kstrtox` internals, user-copy conventions, and exported symbols consumed by many kernel subsystems registering sysctls. `sys.c` uses `proc_dointvec_minmax()` for overflow UID/GID sysctls.

## Risks
Parsing is ABI-sensitive. Strict file-position behavior affects userspace that writes sysctl values in multiple writes. Numeric overflow, signed negation, truncation at `PAGE_SIZE`, and range checks are common bug surfaces. `proc_do_large_bitmap()` must avoid partial malformed range commits; it uses a temporary bitmap to reduce that risk. External callers must provide correct `maxlen`, data type, and min/max pointer types.

## Test signals
`sysctl-test.c` covers `proc_dointvec()` edge cases. Additional signals are procfs sysctl selftests, LTP sysctl coverage, fuzzing malformed numeric/bitmap input, strict write-position tests, capability tests for `proc_do_static_key()`, and build coverage with `CONFIG_PROC_SYSCTL=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/task_work.c -->
# sources/distributed-fs/ceph-client/kernel/task_work.c

## Purpose
`task_work.c` implements per-task callback queues that run at safe task transition points such as return to userspace, guest entry, or task exit. It is a lightweight mechanism for subsystems to defer work to the context of a specific task.

## Important APIs, types, and functions
- `task_work_add()`: atomically pushes a `struct callback_head` onto a task's LIFO work list and optionally notifies the task.
- `task_work_cancel_match()`, `task_work_cancel_func()`, `task_work_cancel()`: remove pending work by predicate, function, or exact callback.
- `task_work_run()`: drains the current task's callbacks and marks the list exited during task exit.
- `work_exited`: sentinel preventing new work on exiting/exited tasks.
- Optional IRQ work `irq_work_NMI_resume` supports `TWA_NMI_CURRENT`.

## Control flow
Adding work validates NMI mode, records KASAN auxiliary stack for normal modes, reads the current list head, fails on `work_exited`, and uses `try_cmpxchg()` to push the work. It then sets notify-resume, notify-signal, no-IPI signal, or NMI irq-work wakeup depending on mode. Cancellation locks `task->pi_lock`, walks the list, and removes a matching node with compare/exchange while tolerating races with add/run. Running work repeatedly detaches the whole list, optionally swaps in `work_exited` if the task is exiting and the list is empty, synchronizes with cancellation through `pi_lock`, invokes callbacks, and reschedules between callbacks.

## State and persistence behavior
State is stored in `task_struct::task_works` until callbacks run or are cancelled. The list is LIFO and not persisted beyond task lifetime. `work_exited` is a static sentinel only distinguished by address.

## Dependencies and integration points
The file integrates with `resume_user_mode`, signal/notify flags, IRQ work for NMI wakeups, spinlocks, KASAN stack recording, and scheduler rescheduling. It is used by io_uring, file/task cleanup, posix CPU timers in some configs, and other code needing task-context callbacks.

## Risks
There is no FIFO ordering guarantee. Callers must keep callback storage valid until execution or cancellation. Adding to exiting tasks fails with `-ESRCH`, so callers need fallback cleanup. Cancellation races are carefully handled but only remove pending work, not callbacks already detached and running.

## Test signals
Exercise callback add/run/cancel under task exit, return-to-user, signal notification, NMI-current mode with `CONFIG_IRQ_WORK`, and race tests between cancellation and run. KASAN/KCSAN and lockdep can expose lifetime and synchronization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/task_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/taskstats.c -->
# sources/distributed-fs/ceph-client/kernel/taskstats.c

## Purpose
`taskstats.c` exports per-task and per-thread-group accounting to userspace over generic netlink, and can send exit-time taskstats to listeners registered per CPU. It also provides cgroupstats query support through the same family.

## Important APIs, types, and functions
- Global state: per-CPU `taskstats_seqnum`, `family_registered`, `taskstats_cache`, generic netlink `family`, and per-CPU `listener_array`.
- Listener types: `struct listener` and `struct listener_list`.
- Netlink helpers: `prepare_reply()`, `send_reply()`, `send_cpu_listeners()`, `mk_reply()`.
- Stats collection: `fill_stats()`, `fill_stats_for_pid()`, `fill_stats_for_tgid()`, `fill_tgid_exit()`, `taskstats_tgid_alloc()`.
- User commands: `cmd_attr_pid()`, `cmd_attr_tgid()`, `cmd_attr_register_cpumask()`, `cmd_attr_deregister_cpumask()`, `taskstats_user_cmd()`, `cgroupstats_user_cmd()`.
- Lifecycle: `taskstats_exit()`, `taskstats_init_early()`, and late init `taskstats_init()`.

## Control flow
Early init creates the slab cache and initializes per-CPU listener lists. Late init registers the generic netlink family. User `TASKSTATS_CMD_GET` requests dispatch to listener registration/deregistration or PID/TGID stats replies. PID stats pin a task by vpid and fill one record; TGID stats lock signal state, combine dead accumulated stats with live thread stats, and return an aggregate. On task exit, if the family is registered and listeners exist for the current CPU, the code allocates a reply, fills PID stats and optionally TGID stats when the group is dead, then unicasts clones to registered listeners, cleaning dead listeners on `-ECONNREFUSED`.

## State and persistence behavior
Persistent kernel state includes the per-CPU listener lists and optional per-signal `taskstats` aggregate allocated from `taskstats_cache`. Exit accounting accumulates into `signal->stats` for thread groups. Netlink messages are transient.

## Dependencies and integration points
It integrates with generic netlink, pid/user namespaces, delay accounting, BSD/xacct accounting, executable file lookup, cgroupstats, CPU masks, per-CPU data, task cputime, task exit paths, and slab allocation.

## Risks
The interface crosses namespaces and permissions. Listener registration is restricted to init user and pid namespaces, and generic netlink ops use admin permissions for taskstats get. Per-CPU listener cleanup must handle clone allocation failure and dead netlink ports. TGID aggregation races are managed with RCU and signal locks, but live tasks can change while stats are sampled.

## Test signals
Use userspace taskstats tools or selftests to query PID/TGID stats, register/deregister CPU masks, observe exit notifications, and request cgroupstats by fd. CPU hotplug/listener behavior, net namespace behavior, and accounting fields under delayacct/xacct configs are important coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/taskstats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/time/Kconfig

## Purpose
`kernel/time/Kconfig` defines timer, clocksource, clockevent, tick, high-resolution timer, context tracking, and time KUnit configuration symbols. It describes architecture-selected capabilities and user-visible timer subsystem choices.

## Important APIs, types, and functions
- Architecture/internal capability symbols: `CLOCKSOURCE_WATCHDOG`, `ARCH_CLOCKSOURCE_INIT`, `ARCH_WANTS_CLOCKSOURCE_READ_INLINE`, `GENERIC_TIME_VSYSCALL`, `GENERIC_CLOCKEVENTS`, `ARCH_HAS_TICK_BROADCAST`, broadcast/min-adjust/coupled clockevent symbols, `GENERIC_CMOS_UPDATE`.
- Deferred/timer-task-work symbols: `HRTIMER_REARM_DEFERRED`, `HAVE_POSIX_CPU_TIMERS_TASK_WORK`, `POSIX_CPU_TIMERS_TASK_WORK`.
- Legacy/test/context symbols: `LEGACY_TIMER_TICK`, `TIME_KUNIT_TEST`, `CONTEXT_TRACKING`, `CONTEXT_TRACKING_IDLE`.
- Timer subsystem menu: `TICK_ONESHOT`, `NO_HZ_COMMON`, `HZ_PERIODIC`, `NO_HZ_IDLE`, `NO_HZ_FULL`, `CONTEXT_TRACKING_USER`, `CONTEXT_TRACKING_USER_FORCE`, `NO_HZ`, `HIGH_RES_TIMERS`, `POSIX_AUX_CLOCKS`.

## Control flow
Kconfig evaluates dependencies and selections at build configuration time. The main choice selects periodic tick, idle dynticks, or full dynticks. `GENERIC_CLOCKEVENTS` gates the tick menu. `NO_HZ_IDLE` and `NO_HZ_FULL` select common oneshot/nohz infrastructure; `HIGH_RES_TIMERS` selects oneshot support.

## State and persistence behavior
The file creates persistent build configuration state in `.config`, which controls compiled objects and runtime behavior. It stores no runtime data itself.

## Dependencies and integration points
It drives the `kernel/time/Makefile` object selection and many runtime code paths in the timer, tick, RCU context tracking, scheduler clock, hrtimer, and POSIX timer subsystems. `NO_HZ_FULL` selects RCU nocb, virtual CPU accounting, IRQ work, and CPU isolation.

## Risks
Kconfig dependency mistakes can expose invalid timer combinations or hide required infrastructure. Full dynticks has broad scheduler/RCU/accounting implications and requires boot-parameter CPU selection. Legacy `NO_HZ` exists for compatibility and can confuse old configs if not handled carefully.

## Test signals
Build coverage across periodic, idle nohz, full nohz, high-resolution timer, legacy tick, and KUnit test configs is essential. Runtime signals include tick/nohz selftests, clockevent broadcast behavior, hrtimer behavior, and RCU context tracking tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/Makefile -->
# sources/distributed-fs/ceph-client/kernel/time/Makefile

## Purpose
`kernel/time/Makefile` selects the compiled objects for the kernel time subsystem according to Kconfig symbols. It wires core timekeeping, timers, hrtimers, POSIX timers or stubs, tick/nohz infrastructure, namespaces, tests, and debug helpers into the build.

## Important APIs, types, and functions
- Always-built objects include `time.o`, `timer.o`, `hrtimer.o`, `sleep_timeout.o`, `timekeeping.o`, `ntp.o`, `clocksource.o`, `jiffies.o`, `timer_list.o`, `timeconv.o`, `timecounter.o`, and `alarmtimer.o`.
- POSIX timer selection builds `posix-timers.o`, `posix-cpu-timers.o`, `posix-clock.o`, and `itimer.o`, or `posix-stubs.o` when disabled.
- Conditional objects cover generic clockevents, tick broadcast, sched clock, oneshot/nohz, legacy tick, SMP timer migration, vsyscall gettimeofday, debugfs, udelay test, time namespaces, VDSO namespace support, clocksource watchdog test, and time KUnit tests.
- `CFLAGS_sched_clock.o += -DDISABLE_BRANCH_PROFILING` disables branch profiling for noinstr-unsafe sched clock code when branch profiling is enabled.

## Control flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` lines at build time. POSIX timers and broadcast support use `ifeq` blocks to select groups of objects. There is no runtime control flow in this file.

## State and persistence behavior
The file affects build artifacts only. It creates no runtime state, but the selected objects implement persistent kernel timekeeping behavior.

## Dependencies and integration points
It is directly driven by `kernel/time/Kconfig` and global architecture symbols. It integrates time subsystem sources with Kbuild and ensures stubs replace POSIX timer implementations when needed.

## Risks
Incorrect object selection can produce unresolved symbols, duplicate implementations, or missing runtime features. The branch profiling flag is important because scheduler clock noinstr paths cannot safely call profiling instrumentation.

## Test signals
Build all relevant config combinations: POSIX timers on/off, generic clockevents/broadcast on/off, SMP nohz, legacy tick, debugfs, time namespaces, VDSO namespace, watchdog test, and `TIME_KUNIT_TEST`. Link failures or missing syscall behavior are primary indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/Makefile -->
