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
