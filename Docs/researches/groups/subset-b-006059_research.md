# Research Report: subset-b-006059

This grouped report covers the six kernel files assigned to `subset-b-006059`. Each file section is bounded with reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/wait.c -->
# sources/distributed-fs/ceph-client/kernel/sched/wait.c

## Purpose

`kernel/sched/wait.c` implements the generic wait-queue primitives used across the kernel to put tasks to sleep until a condition changes and to wake them with well-defined ordering. It owns wait-queue initialization, queue insertion and removal, common wake-up scanning, helper preparation/finish APIs used by wait-event macros, interruptible wait helpers, and the `wait_woken()` protocol for waiters that need explicit wake-state tracking.

## Important APIs, Types, and Functions

The file works primarily on `struct wait_queue_head` and `struct wait_queue_entry`. Public entry points include `__init_waitqueue_head()`, `add_wait_queue()`, `add_wait_queue_exclusive()`, `add_wait_queue_priority()`, `add_wait_queue_priority_exclusive()`, `remove_wait_queue()`, `__wake_up()`, `__wake_up_locked()`, `__wake_up_locked_key()`, `__wake_up_sync_key()`, `__wake_up_locked_sync_key()`, `__wake_up_sync()`, `__wake_up_pollfree()`, `prepare_to_wait()`, `prepare_to_wait_exclusive()`, `init_wait_entry()`, `prepare_to_wait_event()`, `do_wait_intr()`, `do_wait_intr_irq()`, `finish_wait()`, `autoremove_wake_function()`, `wait_woken()`, and `woken_wake_function()`.

Internally, `__wake_up_common()` is the central queue scanner. It invokes each entry's wake callback, stops if a callback returns a negative value, and consumes exclusive wakeups until the requested `nr_exclusive` reaches zero. `__wake_up_common_lock()` wraps this with `wq_head->lock` and IRQ save/restore. Waiter ordering is controlled by `WQ_FLAG_EXCLUSIVE`, `WQ_FLAG_PRIORITY`, and `WQ_FLAG_WOKEN`.

## Control Flow

Wait queues are initialized by setting up the spinlock, lockdep class/name, and list head. Non-exclusive waiters are normally inserted at the head, exclusive waiters at the tail, and priority waiters at the head. `add_wait_queue_priority_exclusive()` allows only one priority waiter at the front of a queue and returns `-EBUSY` if a priority waiter already occupies that position.

Wake-up flow starts with a caller such as `__wake_up()` taking the wait-queue lock and running `__wake_up_common()`. The scanner is safe against callback-side deletion by using `list_for_each_entry_safe_from()`. Exclusive entries let "wake one" and "wake N" behavior coexist with non-exclusive broadcast entries. Sync wakeups pass `WF_SYNC`; current-CPU wakeups pass `WF_CURRENT_CPU`; pollfree wakeups pass a poll key containing `EPOLLHUP | POLLFREE` and assert that the queue was drained.

Wait setup follows a consistent pattern: insert the entry while holding the queue lock, then set the current task state before releasing the lock. `prepare_to_wait_event()` additionally handles pending signals and removes a waiter that should abort with `-ERESTARTSYS`, while preserving the rule that an exclusive waiter already selected by a wakeup must not silently lose the event. `finish_wait()` restores `TASK_RUNNING` and removes the entry if still queued, using `list_empty_careful()` before taking the lock.

`wait_woken()` and `woken_wake_function()` implement a paired barrier protocol around `WQ_FLAG_WOKEN`. The waiter sets its task state, schedules only if the flag is not set and the kthread is not stopping/parking, then clears `WQ_FLAG_WOKEN` with `smp_store_mb()`. The waker executes `smp_mb()`, sets `WQ_FLAG_WOKEN`, and delegates to `default_wake_function()`.

## State and Persistence

The persistent state is in caller-owned wait-queue heads and wait entries: queue membership, flags, callback pointers, and the task stored in `wq_entry->private`. The file does not allocate long-lived objects. It mutates `current->state` through `set_current_state()` and `__set_current_state()`, and relies on the queue spinlock plus memory barriers to publish queue membership before condition checks and wake decisions.

## Dependencies and Integration Points

This file is part of scheduler infrastructure via `sched.h`. It depends on list primitives, spinlocks, lockdep, task states, signal state checks, `schedule()`, `schedule_timeout()`, default wake functions, kthread stop/park checks, poll key conversion, and exported wait-queue helpers consumed by drivers, filesystems, networking, mm, and other kernel subsystems.

## Risks and Edge Cases

The main risks are lost wakeups, incorrect exclusive wake consumption, and memory-ordering regressions. The ordering comment in `prepare_to_wait()` is central: waiters must be visible to wakers before subsequent condition checks can move past state publication. `finish_wait()` intentionally uses a careful lockless list-empty test that is safe only because other modifiers take the queue lock. Wake callbacks that delete themselves or return negative values affect scan progress. `__wake_up_pollfree()` is sensitive because poll users must detach before the wait-queue head is destroyed. Interruptible helpers return with the queue lock still held on signal failure, matching their documented calling convention.

## Test Signals

Useful tests include repeated wait-event and wake-up races under SMP stress, exclusive waiter fairness and wake count behavior, priority-exclusive insertion conflict handling, signal interruption of `prepare_to_wait_event()` and `do_wait_intr*()`, pollfree teardown with epoll users, kthread stop/park while in `wait_woken()`, and lockdep coverage for locked versus unlocked wake APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/wait_bit.c -->
# sources/distributed-fs/ceph-client/kernel/sched/wait_bit.c

## Purpose

`kernel/sched/wait_bit.c` builds bit- and address-keyed waiting APIs on top of generic wait queues. It supports waiters sleeping until a bit clears, waiting while acquiring a bit lock, waking waiters for a specific `(word, bit)` key, and the related `wait_var_event()` mechanism for arbitrary variable addresses.

## Important APIs, Types, and Functions

The file defines a cacheline-aligned global hash table `bit_wait_table` with 256 wait queues. `bit_waitqueue()` maps an `(unsigned long *word, int bit)` pair to a bucket, and `__var_waitqueue()` maps an arbitrary variable address to a bucket. The key types are `struct wait_bit_key` and `struct wait_bit_queue_entry`, with wake callbacks `wake_bit_function()` and `var_wake_function()`.

Main APIs include `__wait_on_bit()`, `out_of_line_wait_on_bit()`, `out_of_line_wait_on_bit_timeout()`, `__wait_on_bit_lock()`, `out_of_line_wait_on_bit_lock()`, `__wake_up_bit()`, `wake_up_bit()`, `init_wait_var_entry()`, `wake_up_var()`, `bit_wait()`, `bit_wait_io()`, `bit_wait_timeout()`, and `wait_bit_init()`.

## Control Flow

`__wait_on_bit()` repeatedly prepares a non-exclusive wait entry, tests the target bit, and invokes the supplied `wait_bit_action_f` callback while the bit remains set. The loop exits when `test_bit_acquire()` observes the bit clear or when the action returns nonzero, then calls `finish_wait()`.

`__wait_on_bit_lock()` uses exclusive waiting and attempts to acquire the bit with `test_and_set_bit()`. It waits while the bit is already set, runs the action callback if sleeping is needed, and returns success when it changes the bit from clear to set. The barrier behavior of `test_and_set_bit()` is part of the correctness contract, especially when an action returns early and `finish_wait()` may not take the queue lock on the fast path.

Wake-up flow constructs a `wait_bit_key`, checks `waitqueue_active()`, and calls `__wake_up()` for one normal waiter. `wake_bit_function()` filters hash-bucket collisions by matching `flags` and `bit_nr`, and it refuses to wake if the bit is still set. Variable waiting uses the same table with `bit_nr = -1`; `var_wake_function()` matches only the address and sentinel bit.

## State and Persistence

The persistent global state is the fixed wait-queue table initialized by `wait_bit_init()`. Individual waits allocate no persistent heap state; wait entries are stack- or caller-owned. Timeout waits store an absolute `jiffies` deadline in `wq_entry.key.timeout`. Correctness depends on external owners clearing bits or updating variables with release/ordered semantics before calling `wake_up_bit()` or `wake_up_var()`.

## Dependencies and Integration Points

This file depends on generic wait-queue APIs from `wait.c`, bitops, hashing helpers, `jiffies`, signal-pending checks, `schedule()`, `io_schedule()`, and `schedule_timeout()`. It is used by page, buffer, filesystem, block, and driver code that represents lock or readiness state as bits or address-associated conditions.

## Risks and Edge Cases

Hash buckets can contain unrelated waiters, so key matching in wake callbacks is mandatory. Missing memory barriers after clearing a bit or updating a variable can let waiters wake before the condition's data is visible. `wake_up_bit()` comments explicitly require a full barrier unless the clear/update operation is fully ordered. Timeout handling uses absolute `jiffies`, so wrap-safe `time_after_eq()` behavior is important. `__wait_on_bit_lock()` must not lose exclusive waiters when the action returns an error or signal interruption.

## Test Signals

Useful coverage includes clear-and-wake ordering tests on SMP, hash-collision tests with different words and bits, signal-interruptible waits, IO wait accounting through `bit_wait_io()`, timeout expiry and success before timeout, bit-lock acquisition under contention, and `wait_var_event()` wakeups for address-only conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/wait_bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/scs.c -->
# sources/distributed-fs/ceph-client/kernel/scs.c

## Purpose

`kernel/scs.c` implements generic Shadow Call Stack allocation and lifetime support for tasks. It allocates per-task shadow stacks from vmalloc memory, keeps a small per-CPU cache for interrupt-safe freeing, accounts memory usage in VM statistics, integrates with KASAN poisoning, and verifies/records usage during release when debug stack usage is enabled.

## Important APIs, Types, and Functions

The file exports or defines `dynamic_scs_enabled` for `CONFIG_DYNAMIC_SCS`, `scs_alloc()`, `scs_free()`, `scs_init()`, `scs_prepare()`, and `scs_release()`. Internal helpers include `__scs_account()`, `__scs_alloc()`, `scs_cleanup()`, and `scs_check_usage()`.

The main state is `static DEFINE_PER_CPU(void *, scs_cache[NR_CACHED_SCS])`, with `NR_CACHED_SCS` set to 2 to mirror the vmap stack cache depth. Task integration uses `task_scs(tsk)` and `task_scs_sp(tsk)`, and stack integrity relies on `__scs_magic(s)`, `SCS_END_MAGIC`, and `task_scs_end_corrupted()`.

## Control Flow

Allocation begins in `scs_prepare()`, which exits early if `scs_is_enabled()` is false. Otherwise it calls `scs_alloc()`. `__scs_alloc()` first tries to pop a stack from the current CPU cache with `this_cpu_xchg()`, unpoisons and zeros it when found, and falls back to `__vmalloc_node_range()` with `GFP_SCS` on cache miss. `scs_alloc()` resets the KASAN tag, writes the end magic, poisons the vmalloc area to catch accidental accesses, and increments `NR_KERNEL_SCS_KB` for the allocation's NUMA node.

Freeing begins in `scs_release()`, which ignores disabled or empty task SCS state, warns on end-magic corruption, optionally records highest observed usage, and calls `scs_free()`. `scs_free()` decrements accounting and tries to insert the stack into a per-CPU cache using `this_cpu_cmpxchg()`. If the cache is full, it unpoisons the vmalloc area and uses `vfree_atomic()` because release can happen in interrupt context.

CPU hotplug cleanup is registered by `scs_init()` with `cpuhp_setup_state()`. `scs_cleanup()` drains another CPU's cache with regular `vfree()` and clears slots when that CPU is being prepared or torn down by the hotplug state callback.

## State and Persistence

The durable task state is the shadow-stack base and current SCS stack pointer stored in `task_struct`. Cached freed stacks persist per CPU until reused or hotplug cleanup. VM accounting persists through `NR_KERNEL_SCS_KB`. The static `highest` value in `scs_check_usage()` tracks the largest observed shadow-stack usage for debug logging.

## Dependencies and Integration Points

The implementation depends on `linux/scs.h`, vmalloc, KASAN vmalloc poisoning/unpoisoning, NUMA page accounting through `vmalloc_to_page()` and `mod_node_page_state()`, CPU hotplug, task lifecycle hooks that call `scs_prepare()` and `scs_release()`, and architecture/compiler SCS support that consumes `task_scs_sp()`.

## Risks and Edge Cases

The most sensitive behavior is lifetime and context: `scs_free()` must not sleep, so cache insertion and `vfree_atomic()` are required. Reused cached stacks must be unpoisoned, zeroed, retagged, then poisoned again in the right order. Accounting assumes `vmalloc_to_page(s)` succeeds for SCS allocations. Corruption detection only happens on release. Hotplug cleanup must not race with cache users on the target CPU outside the CPU hotplug lifecycle.

## Test Signals

Useful tests include task fork/exit with SCS enabled and disabled, allocation failure returning `-ENOMEM`, cache reuse on repeated short-lived tasks, cache overflow falling back to `vfree_atomic()`, CPU hotplug draining cached stacks, KASAN reports for accidental SCS access, end-magic corruption warnings, and `CONFIG_DEBUG_STACK_USAGE` highest-usage logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/scs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/seccomp.c -->
# sources/distributed-fs/ceph-client/kernel/seccomp.c

## Purpose

`kernel/seccomp.c` implements Linux secure computing mode. It supports strict mode, BPF-filter mode, filter chaining and thread synchronization, syscall-time filter evaluation, ptrace and user-notification actions, listener file descriptors, seccomp addfd injection, checkpoint/restore metadata access, audit logging, and sysctl controls for action logging.

## Important APIs, Types, and Functions

Key types include `struct seccomp_filter`, `struct notification`, `struct seccomp_knotif`, `struct seccomp_kaddfd`, and `struct action_cache`. `struct seccomp_filter` carries reference counts, user counts, a BPF program, previous filter pointer, optional notification state, a mutex, wait queue, logging flags, and cached always-allow bitmaps where supported.

Core filter APIs include `populate_seccomp_data()`, `seccomp_check_filter()`, `seccomp_prepare_filter()`, `seccomp_prepare_user_filter()`, `seccomp_attach_filter()`, `seccomp_run_filters()`, `seccomp_cache_prepare()`, `get_seccomp_filter()`, `seccomp_filter_release()`, `__put_seccomp_filter()`, and `__seccomp_filter_release()`. Mode and syscall APIs include `seccomp_assign_mode()`, `seccomp_set_mode_strict()`, `seccomp_set_mode_filter()`, `do_seccomp()`, `SYSCALL_DEFINE3(seccomp)`, `prctl_set_seccomp()`, `prctl_get_seccomp()`, `secure_computing_strict()`, and `__secure_computing()`.

User-notification APIs are implemented by `seccomp_do_user_notification()`, `init_listener()`, `seccomp_notify_recv()`, `seccomp_notify_send()`, `seccomp_notify_addfd()`, `seccomp_notify_id_valid()`, `seccomp_notify_poll()`, `seccomp_notify_release()`, and `seccomp_notify_detach()`. Sysctl/logging support centers on `seccomp_log()`, `seccomp_actions_logged_handler()`, and the `kernel/seccomp/actions_avail` and `actions_logged` tables.

## Control Flow

Filter installation starts through `seccomp()` or `prctl()`. Strict mode verifies the current task can transition, optionally disables TSC on architectures that support that hook, then assigns mode under `sighand->siglock`. Filter mode validates flags, copies and verifies the user BPF program, optionally creates a notification listener fd, optionally takes `cred_guard_mutex` for TSYNC, attaches the new filter under `siglock`, prepares the allow cache, and finally sets `SYSCALL_WORK_SECCOMP`.

At syscall entry, `__secure_computing()` checks checkpoint/restore suspension, fetches the syscall number, and dispatches by mode. Strict mode only allows read, write, exit, sigreturn, and uprobe exceptions. Filter mode populates `struct seccomp_data`, runs all filters from newest to oldest, and chooses the lowest action value ignoring data. `SECCOMP_RET_ERRNO` sets an errno return, `TRAP` rolls back registers and sends SIGSYS, `TRACE` notifies ptrace and may recheck if the tracer changes the syscall, `USER_NOTIF` blocks for a listener response, `LOG` audits and allows, `ALLOW` returns normally, and kill actions mark mode dead and deliver SIGSYS or exit.

Thread synchronization first validates every live sibling with `seccomp_can_sync_threads()`. `seccomp_sync_threads()` then attaches the caller's filter tree to each eligible thread, updates filter counts, propagates `no_new_privs`, and assigns filter mode if a thread was disabled. Filter lifetime is tree-shaped through `prev`; `refs` owns memory lifetime and `users` owns orphan/HUP notification semantics.

User notification creates a listener backed by anon inode file operations. When a syscall returns `USER_NOTIF`, the task creates a stack `seccomp_knotif`, links it under the matching filter, wakes pollers, then sleeps until the listener replies, dies, or injects addfd work. Listener `RECV` transitions notifications from INIT to SENT and copies syscall data to userspace. `SEND` transitions SENT to REPLIED and completes the target. `ADDFD` queues a `seccomp_kaddfd` for the blocked task to install with `receive_fd()` or `receive_fd_replace()`.

## State and Persistence

Per-task persistent state lives in `task_struct.seccomp`: mode, filter pointer, and filter count. Filters persist as refcounted chained objects; attached filters are never mutated except for reference counts and notification data protected by `notify_lock`. Notification listener state persists while its fd is open. Logging state persists globally in `seccomp_actions_logged`. Caches persist in each filter and are inherited from previous filters so a cached allow remains valid only if every filter in the path constantly allows that syscall/arch pair.

## Dependencies and Integration Points

This file integrates with syscall entry work flags, BPF classic verifier/runtime, audit, ptrace events, signals (`force_sig_seccomp()`), task credentials and `no_new_privs`, user namespaces and `CAP_SYS_ADMIN`, `cred_guard_mutex` and `sighand->siglock`, anon inode files, poll/wait queues, fd installation helpers, checkpoint/restore ptrace APIs, sysctl, architecture syscall accessors, and architecture-specific speculative-execution mitigation hooks.

## Risks and Edge Cases

Security-sensitive risks include fail-open filter behavior, incorrect action precedence, unsafe ptrace rechecks after syscall mutation, listener lifetime races, and addfd injection before a notification is valid. TSYNC must avoid races with exec and exiting threads. Reference accounting is subtle because each attached task, dependent filter, and listener fd contributes differently to `refs` and `users`. The BPF cache must only mark constant allow decisions; anything depending on non-constant args cannot be cached. `SECCOMP_USER_NOTIF_FLAG_CONTINUE` is dangerous if userspace relies on the listener as a privilege boundary because the tracee resumes the original syscall. `SECCOMP_MODE_DEAD` exists to make survival after kill actions impossible.

## Test Signals

Important tests include strict-mode allowed and denied syscall behavior, invalid BPF programs and invalid flags, no-new-privs and `CAP_SYS_ADMIN` permission checks, filter chaining precedence, TSYNC success and failure pid reporting, ptrace trace action with syscall rewrite and fatal-signal races, user-notification receive/send/poll/HUP paths, listener close while tasks wait, addfd success/failure/interruption, sysctl parsing and audit messages, checkpoint/restore filter export and metadata, compat filter copying, and cache debug output when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/seccomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/signal.c -->
# sources/distributed-fs/ceph-client/kernel/signal.c

## Purpose

`kernel/signal.c` implements the core Linux signal subsystem. It manages pending signal queues, signal permission checks, task and process-group signal generation, signal delivery and default actions, ptrace and job-control stops, POSIX timer signals, parent notifications, signal-mask syscalls, siginfo copy/compat translation, sigaction, alternate signal stacks, and signal subsystem initialization.

## Important APIs, Types, and Functions

Important state types are `struct sigpending`, `struct sigqueue`, `struct signal_struct`, `struct sighand_struct`, `struct k_sigaction`, `kernel_siginfo_t`, `struct ksignal`, and the `jobctl` bitfield in `task_struct`. The file initializes `sigqueue_cachep` and exposes `print_fatal_signals`.

Core pending/delivery helpers include `recalc_sigpending()`, `calculate_sigpending()`, `next_signal()`, `dequeue_signal()`, `dequeue_synchronous_signal()`, `signal_wake_up_state()`, `prepare_signal()`, `complete_signal()`, `send_signal_locked()`, `do_send_sig_info()`, `group_send_sig_info()`, `get_signal()`, `signal_setup_done()`, `exit_signals()`, and `retarget_shared_pending()`.

Public generation helpers include `send_sig_info()`, `send_sig()`, `force_sig()`, `force_fatal_sig()`, `force_exit_sig()`, `force_sigsegv()`, `force_sig_fault()`, `send_sig_fault()`, `force_sig_mceerr()`, `send_sig_mceerr()`, `force_sig_bnderr()`, `force_sig_pkuerr()`, `send_sig_perf()`, `force_sig_seccomp()`, `kill_pid()`, and `kill_pgrp()`. Syscall paths include `kill`, `pidfd_send_signal`, `tgkill`, `tkill`, `rt_sigqueueinfo`, `rt_tgsigqueueinfo`, `rt_sigprocmask`, `rt_sigpending`, `rt_sigtimedwait`, `rt_sigaction`, `sigaltstack`, `pause`, `rt_sigsuspend`, and legacy/compat variants.

Ptrace/job-control flow is implemented by `task_set_jobctl_pending()`, `task_clear_jobctl_pending()`, `task_participate_group_stop()`, `task_join_group_stop()`, `ptrace_stop()`, `ptrace_notify()`, `do_signal_stop()`, `do_jobctl_trap()`, `do_freezer_trap()`, and `ptrace_signal()`.

## Control Flow

Signal generation starts with permission and target selection. `check_kill_permission()` validates signal numbers, user credentials, pid namespace/session exceptions for SIGCONT, audit, and LSM hooks. `prepare_signal()` applies process-wide side effects for stop and continue signals: stop signals flush queued SIGCONT, SIGCONT flushes stop signals, wakes stopped tasks, and arranges parent CLD notifications. `__send_signal_locked()` chooses private versus shared pending queues, suppresses duplicate legacy signals, allocates `sigqueue` records when useful, falls back to lossy delivery when allowed, updates signalfd, marks pending bits, and calls `complete_signal()`.

`complete_signal()` chooses a thread that wants the signal. It prefers the suggested task, then rotates through the thread group via `curr_target`. Fatal non-coredump signals mark `SIGNAL_GROUP_EXIT`, set `group_exit_code`, clear jobctl stop/trap bits, add SIGKILL to every thread, and wake them. Otherwise, it wakes a chosen task to dequeue the shared signal.

Delivery to userspace is driven by `get_signal()`. It first runs task work, freezer handling, CLD continued/stopped notifications, group-exit checks, job-control stops, ptrace traps, and cgroup frozen-state transitions. It dequeues synchronous fault signals before normal pending signals so user frames point at the faulting instruction. Ptrace can observe and rewrite a signal, including requeueing if the new signal is blocked. Handled signals return a populated `ksignal`; ignored and default-ignore signals are skipped; default-stop signals enter group-stop handling; fatal signals perform coredump or `do_group_exit()`.

After an architecture sets up a signal frame, `signal_setup_done()` updates the blocked mask through `signal_delivered()`, handles `SA_NODEFER`, `SA_ONESHOT`, saved-mask restoration, alternate-stack autodisarm, and ptrace single-step notification. If frame setup fails, the code forces SIGSEGV.

Syscall support wraps these primitives. Mask-changing paths update `current->blocked` only through helpers that retarget shared pending signals before blocking them. `rt_sigtimedwait()` temporarily adjusts `blocked`/`real_blocked`, sleeps with an hrtimer timeout, then restores the mask and dequeues. `sigaction` installs handlers under `siglock`, filters unsupported flags, drops pending ignored signals, and can unignore queued POSIX timers. `sigaltstack` validates mode, minimum size, and on-stack restrictions; compat paths translate pointer-sized fields.

## State and Persistence

Persistent per-task state includes private pending queues, blocked and real-blocked masks, saved masks, jobctl bits, ptrace fields, alternate-stack fields, and `TIF_SIGPENDING`. Shared thread-group state includes shared pending queues, signal actions, group stop counts, stop/continue flags, group-exit state, ignored POSIX timer lists, and current shared-signal target. `sigqueue` objects are slab-allocated and charged to per-user `RLIMIT_SIGPENDING` counts; POSIX timers use preallocated signal queue entries with special reference handling.

## Dependencies and Integration Points

The file integrates with scheduler wakeups, ptrace, cgroups/freezer, pid namespaces, user namespaces and credentials, audit, LSM hooks, signalfd, pidfd, POSIX timers, coredump, proc connector, uprobe signal denial, task work, syscall restart blocks, compat syscalls, architecture signal-frame code, uaccess helpers, sysctl, kgdb/kdb, and wait-parent notification paths.

## Risks and Edge Cases

The subsystem is dominated by race-sensitive lock ordering and state transitions. `sighand->siglock`, `tasklist_lock`, RCU, cgroup freezer state, and ptrace stop scheduling interact heavily. Lost wakeups or stale `TIF_SIGPENDING` can leave tasks sleeping with deliverable signals. Stop/continue semantics must correctly clear queued opposing signals and report CLD events once. `SIGKILL`/`SIGSTOP`, global/container init, `SIGNAL_UNKILLABLE`, ptraced tasks, kernel threads, and PF_USER_WORKER tasks all have special fatal/ignored behavior. `RLIMIT_SIGPENDING` can cause lossy siginfo delivery for non-RT signals but must fail selected RT sends. Compat siginfo layout and unknown `si_code` expansion checks protect ABI round-tripping. Alternate stack changes must reject modifications while currently on the signal stack.

## Test Signals

Useful coverage includes kill/tkill/tgkill/pidfd scope and permission checks, pid namespace restrictions, legacy non-RT coalescing versus RT queueing, `RLIMIT_SIGPENDING` overflow, signalfd notifications, SIGSTOP/SIGCONT group-stop transitions, ptrace signal rewrite and PTRACE_EVENT_STOP behavior, freezer traps, fatal signal coredumps and group exit, POSIX timer ignored/unignored delivery, signal-mask retargeting between threads, sigtimedwait timeout/interruption, sigaction ignored-signal flushing, altstack enable/disable/autodisarm, compat siginfo copy paths, seccomp SIGSYS generation, and kdb guarded signal sending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/smp.c -->
# sources/distributed-fs/ceph-client/kernel/smp.c

## Purpose

`kernel/smp.c` implements generic SMP call-function infrastructure. It queues callbacks to run on one CPU, many CPUs, all other CPUs, or a selected CPU via workqueue; sends the required IPIs; flushes per-CPU callback queues; manages callback data through CPU hotplug; provides debug detection for stuck call-single-data locks; and handles boot-time SMP activation parameters.

## Important APIs, Types, and Functions

Key state includes per-CPU `struct call_function_data cfd_data`, per-CPU `llist_head call_single_queue`, per-CPU reusable `call_single_data_t csd_data`, and optional CSD lock-debug state (`cur_csd`, `cur_csd_func`, `cur_csd_info`, `trigger_backtrace`, `n_csd_lock_stuck`). `struct call_function_data` owns per-target CSD storage and two cpumasks used by multi-CPU calls.

Public APIs include `smpcfd_prepare_cpu()`, `smpcfd_dead_cpu()`, `smpcfd_dying_cpu()`, `call_function_init()`, `__smp_call_single_queue()`, `generic_smp_call_function_single_interrupt()`, `flush_smp_call_function_queue()`, `smp_call_function_single()`, `smp_call_function_single_async()`, `smp_call_function_any()`, `smp_call_function_many()`, `smp_call_function()`, `setup_nr_cpu_ids()`, `smp_init()`, `on_each_cpu_cond_mask()`, `kick_all_cpus_sync()`, `wake_up_all_idle_cpus()`, `cpus_peek_for_pending_ipi()`, and `smp_call_on_cpu()`.

Internal helpers include `send_call_function_single_ipi()`, `send_call_function_ipi_mask()`, `csd_do_func()`, `csd_lock()`, `csd_unlock()`, `csd_lock_wait()`, `generic_exec_single()`, `__flush_smp_call_function_queue()`, and `smp_call_function_many_cond()`.

## Control Flow

Single-CPU calls use `smp_call_function_single()`. The caller disables preemption with `get_cpu()`, warns about contexts that can deadlock, chooses an on-stack synchronous CSD or a per-CPU asynchronous CSD, fills `func` and `info`, and calls `generic_exec_single()`. Same-CPU calls execute directly with IRQs disabled after unlocking the CSD. Remote calls validate CPU online state, queue the CSD on the target CPU's lockless list, and send an IPI if the queue was previously empty. Synchronous callers wait for the target to clear the CSD lock.

Asynchronous single calls use a caller-owned CSD and return `-EBUSY` if its lock flag is still set from a prior invocation. Multi-CPU calls run through `smp_call_function_many_cond()`, which requires preemption disabled and IRQs enabled in normal online contexts. It builds an online remote mask, optionally filters CPUs with `cond_func`, locks and fills per-target CSDs, queues them, chooses single-IPI versus mask-IPI sending, optionally executes locally, and waits for remote CSD unlocks when requested.

Target CPUs handle IPIs in `generic_smp_call_function_single_interrupt()`, which calls `__flush_smp_call_function_queue()` with IRQs disabled. The flush path detaches and reverses the per-CPU llist, warns once for callbacks on offline CPUs, executes synchronous callbacks first, then asynchronous and IRQ-work callbacks, and finally batches scheduler TTWU callbacks through `sched_ttwu_pending()`. This ordering wakes synchronous waiters promptly while preserving special handling for task wakeups.

CPU hotplug preparation allocates cpumasks and per-CPU CSD arrays. Dying CPUs explicitly flush pending call-function queues and irq work with interrupts disabled so no callbacks remain queued as the CPU leaves. Boot-time code parses `nosmp`, `nr_cpus=`, and `maxcpus=`, initializes idle and CPU hotplug threads, brings up nonboot CPUs, and calls `smp_cpus_done()`.

## State and Persistence

Persistent state is per-CPU and boot-global. `call_single_queue` holds pending callback nodes until an IPI or explicit flush runs them. CSD lock bits serialize ownership of reusable CSD objects and act as completion state for waiters. `setup_max_cpus` and `nr_cpu_ids` persist boot-time SMP limits. Optional debug counters and module parameters persist CSD stall detection settings.

## Dependencies and Integration Points

This file integrates with architecture IPI hooks (`arch_send_call_function_single_ipi()`, `arch_send_call_function_ipi_mask()`), scheduler TTWU batching, irq work, CPU hotplug, cpumasks, NUMA CPU selection, idle wakeups, tracepoints for IPI and CSD events, hypervisor vCPU pinning, system per-CPU workqueue, RCU/list primitives, NMI backtraces, and boot parameter parsing.

## Risks and Edge Cases

The major risks are deadlocks and missed IPIs. Call-function APIs warn against use from interrupt-disabled or non-task contexts because synchronous waits can deadlock if interrupted between queueing and IPI sending, and asynchronous paths can reuse the same per-CPU CSD. CPU online/offline races are controlled by preemption disabling and explicit dying-CPU flushes. CSD lock debug deliberately sends backtraces and may resend IPIs when a remote CPU appears stuck. Queue flushing must handle callbacks queued to offline CPUs and must preserve type-specific unlock timing. Multi-CPU calls can see concurrent mask changes, so zero remote IPIs after filtering is valid.

## Test Signals

Useful tests include same-CPU and remote `smp_call_function_single()` with wait and no-wait modes, async `-EBUSY` behavior, multi-CPU calls with masks and conditional callbacks, local execution via `on_each_cpu_cond_mask()`, CPU hotplug while callbacks are queued, idle polling CPUs receiving pending work, CSD lock debug timeout paths, offline CPU warning paths, boot parameter limits, `kick_all_cpus_sync()`, `wake_up_all_idle_cpus()`, and `smp_call_on_cpu()` with and without physical vCPU pinning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/smp.c -->
