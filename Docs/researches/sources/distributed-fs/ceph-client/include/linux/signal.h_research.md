# sources/distributed-fs/ceph-client/include/linux/signal.h

## Purpose

`signal.h` provides kernel signal helpers built on `signal_types.h`: siginfo copying, sigset manipulation, pending signal initialization, signal delivery declarations, kernel-thread signal policy helpers, default signal-action masks, altstack helpers, proc rendering, and architecture address untagging for signal fault delivery.

## Important APIs, Types, And Functions

Key helpers include `copy_siginfo()`, `clear_siginfo()`, `copy_siginfo_to_external()`, `copy_siginfo_to_user()`, `copy_siginfo_from_user()`, `siginfo_layout()`, `sigaddset()`, `sigdelset()`, `sigismember()`, `sigisemptyset()`, `sigequalsets()`, `sigmask()`, `sigorsets()`, `sigandsets()`, `sigandnsets()`, `signotset()`, `sigemptyset()`, `sigfillset()`, low-32-bit mask helpers, `siginitset()`, `siginitsetinv()`, `init_sigpending()`, `flush_sigqueue()`, `valid_signal()`, `next_signal()`, `do_send_sig_info()`, `group_send_sig_info()`, `send_signal_locked()`, `sigprocmask()`, `set_current_blocked()`, `__set_current_blocked()`, `get_signal()`, `signal_setup_done()`, `exit_signals()`, `kernel_sigaction()`, `allow_signal()`, `allow_kernel_signal()`, `disallow_signal()`, `unhandled_signal()`, `signals_init()`, `restore_altstack()`, `__save_altstack()`, `unsafe_save_altstack()`, `sigaltstack_size_valid()`, `render_sigset_t()`, and `arch_untagged_si_addr()`.

It defines `enum siginfo_layout`, `SIG_KTHREAD`, `SIG_KTHREAD_KERNEL`, default-action masks, `sig_kernel_only()`, `sig_kernel_coredump()`, `sig_kernel_ignore()`, `sig_kernel_stop()`, `sig_specific_sicodes()`, and `sig_fatal()`.

## Control Flow

Sigset helpers manipulate per-task blocked or pending signal masks. Signal send paths select process or thread delivery through the declared APIs. `get_signal()` obtains a deliverable signal for architecture return-to-user paths, after which `signal_setup_done()` completes frame setup. Kernel thread helpers install special handlers so selected signals are not silently dropped or converted. The default-action masks classify whether a signal is uncatchable, stopping, coredumping, ignored, or fatal.

## State And Persistence

Signal state lives in task, sighand, pending queues, sigsets, and altstack fields. This header manipulates bitsets in-place and initializes `struct sigpending` by emptying the mask and list. It also references global policy/debug variables such as `print_fatal_signals`, `show_unhandled_signals`, and `sighand_cachep`.

## Dependencies And Integration Points

Dependencies include bug/build assertions, lists, `signal_types.h`, string/memory helpers, user access through surrounding includes, task structures, pid types, seq files, and architecture overrides. Integration points include syscall signal APIs, return-to-user architecture code, procfs status rendering, coredump/stop/job-control behavior, kernel threads, seccomp/perf/fault siginfo layouts, and tagged address architectures.

## Risks And Test Signals

Risks are off-by-one signal bit handling, unsupported `_NSIG_WORDS` values, copying kernel siginfo without zeroing external expansion bytes, wrong default-action masks, and architecture mismatches in altstack or tagged address handling. Test signals include signal syscall selftests, realtime signal queueing, ptrace/seccomp/fault siginfo tests, job-control tests, coredump tests, kernel-thread signal behavior, dynamic sigframe altstack validation, and procfs signal mask rendering.
