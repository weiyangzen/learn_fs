# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.c

Purpose: common PowerPC signal-delivery logic shared by 32-bit and 64-bit tasks, including FPR/VSX copy helpers, minimum frame sizing, signal stack selection, syscall restart handling, delivery dispatch, notify-resume work, transactional-memory stack handling, and bad-frame logging.

Important APIs/types/functions: `copy_fpr_to_user()`, `copy_fpr_from_user()`, `copy_vsx_to_user()`, `copy_vsx_from_user()`, checkpointed TM variants, `show_unhandled_signals`, `get_min_sigframe_size()`, `get_min_sigframe_size_compat()`, `get_sigframe()`, `check_syscall_restart()`, `do_signal()`, `do_notify_resume()`, `get_tm_stackpointer()`, and `signal_fault()`.

Control flow: user-return paths call `do_notify_resume()` with thread flags; it processes uprobes, livepatch state, pending signals, and generic resume work. `do_signal()` fetches a pending signal, applies syscall restart or EINTR conversion, restores the sigmask if none is delivered, re-enables hardware breakpoints, notifies rseq, dispatches to 32-bit legacy/RT or 64-bit RT frame builders, and calls `signal_setup_done()`. `get_sigframe()` chooses altstack and alignment, using a checkpointed TM stack pointer when an active transaction is reclaimed for signal delivery. `check_syscall_restart()` handles both sc/scv calling conventions and adjusts NIP by four bytes when restarting.

State and persistence: signal delivery mutates the current thread's user register image, saved signal mask, hardware breakpoint state, FPR/VSX checkpoint state, transaction state, and thread flags. It does not persist kernel data beyond task state.

Dependencies and integration points: integrates with generic signal core, rseq, uprobes, livepatch, hardware breakpoint code, TM reclaim/recheckpoint support, `signal_32.c`, `signal_64.c`, ptrace-visible registers, and architecture syscall trap helpers.

Risks: restart logic must preserve ABI differences between sc and scv. TM stack handling is delicate: writing the signal frame to the speculative stack would corrupt rollback state, so reclaim and MSR TS clearing must be ordered with preemption disabled. Bad user frames must be logged rate-limited and terminate safely.

Test signals: signal selftests for restart/EINTR behavior, 32/64-bit delivery, altstack alignment, rseq interruption, uprobes/livepatch return work, hardware breakpoint re-enable, VSX/FPR preservation, and TM signal delivery/abort cases.
