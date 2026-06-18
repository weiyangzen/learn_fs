## sources/distributed-fs/ceph-client/arch/arm64/include/asm/entry-common.h

Purpose: arm64 hooks for generic kernel entry/exit code.

Important APIs/types/functions: defines `ARCH_EXIT_TO_USER_MODE_WORK`, `arch_exit_to_user_mode_work`, and `arch_irqentry_exit_need_resched`.

Control flow: on return to user mode, pending MTE async faults are converted to `SIGSEGV`, and foreign FP state triggers FPSIMD restore. IRQ exit avoids preemption when pseudo-NMI DAIF state or unfinished CPU feature finalization makes it unsafe.

State and persistence: clears thread flags, sends signals, and restores current task FP state.

Dependencies and integration: depends on thread flags, cpufeature finalization, DAIF, FPSIMD, MTE, stacktrace, and generic entry code.

Risks: missed exit work leaks FP state or loses MTE faults; unsafe preemption can restore stale PSTATE. Test signals are MTE async fault tests, FPSIMD context-switch tests, IRQ/preempt stress, and CPU feature bring-up races.
