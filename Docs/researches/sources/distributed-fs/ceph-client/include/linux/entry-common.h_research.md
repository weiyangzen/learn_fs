# sources/distributed-fs/ceph-client/include/linux/entry-common.h

Purpose: generic syscall entry/exit work orchestration shared by architectures.

Important APIs/types/functions: `SYSCALL_WORK_ENTER`, `SYSCALL_WORK_EXIT`, arch override wrappers for ptrace entry/exit, `syscall_user_dispatch()`, trace hooks, `syscall_enter_audit()`, `syscall_trace_enter()`, `syscall_enter_from_user_mode_work()`, `syscall_enter_from_user_mode()`, `report_single_step()`, `syscall_exit_work()`, `syscall_exit_to_user_mode_work()`, and `syscall_exit_to_user_mode()`.

Control flow: architecture code enters from user mode, enables instrumentation/IRQs at defined points, handles syscall user dispatch first, rseq slice work, ptrace, seccomp, tracepoints, audit, and then executes or skips the syscall. Exit handles rseq return, audit, tracepoints, ptrace/singlestep, disables IRQs, processes return-to-user work, and finalizes context tracking.

State/persistence: uses per-thread `syscall_work`, current task audit/seccomp/rseq/dispatch state, and pt_regs. No persistent state beyond task flags.

Dependencies/integration: audit, ptrace, seccomp, rseq, livepatch/user-mode resume, IRQ/context tracking, arch syscall accessors, tracepoints.

Risks/test signals: risks are wrong ordering of dispatch/ptrace/seccomp, IRQ state leaks, instrumentation in non-instrumentable regions, skipped syscall return semantics, and single-step handling. Test tracing, seccomp, ptrace SYSEMU, syscall user dispatch, audit, rseq, lockdep IRQ warnings, and architecture entry selftests.
