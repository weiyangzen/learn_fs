# sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt.c

## Purpose
Implements C-side PowerPC syscall and interrupt exit preparation, including user work processing, lazy IRQ state reconciliation, KUAP restore, transactional memory/math restore, debug register reload, and restartable exit handling.

## Important APIs, Types, And Functions
Key functions are `syscall_exit_prepare`, `syscall_exit_restart`, `interrupt_exit_user_prepare`, `interrupt_exit_kernel_prepare`, `interrupt_exit_user_restart`, and `interrupt_exit_kernel_restart`. Internal helpers include `prep_irq_for_enabled_exit`, `booke_load_dbcr0`, `check_return_regs_valid`, and `interrupt_exit_user_prepare_main`. State includes `global_dbcr0`, `sk_dynamic_irqentry_exit_cond_resched`, and `interrupt_exit_not_reentrant`.

## Control Flow
Syscall exit stores the syscall result, applies PowerPC error signaling, handles per-syscall flags and tracing, disables local IRQs, then delegates to the common user-exit path. The user-exit loop enables IRQs to handle rescheduling or signal work, restores TM or math state, validates SRRs, enters context tracking user state, prepares for enabled interrupt return, reloads BookE debug registers, accounts CPU time, and restores KUAP user access locks. Kernel exit handles unrecoverable frames, optional preemption on IRQ return, SRR validation, pending soft-masked interrupts via `prep_irq_for_enabled_exit`, stack-store emulation, TM scratch, and KUAP kernel restore. Restart functions reestablish hard-disabled, soft-masked state and re-run the relevant prepare path.

## State And Persistence
State spans thread flags, `pt_regs`, PACA `irq_happened`/soft mask state, context tracking, KUAP AMR state, TM scratch, BookE debug DBCR0/DBSR, syscall result fields, and optional SRR-valid debug flags. All state is in-memory CPU/task state.

## Dependencies And Integration Points
Depends on low-level assembly in `interrupt_64.S` and 32-bit return paths, context tracking, scheduler, signal delivery, rseq, syscall tracing, KUAP, KVM/TM/math restore code, BookE advanced debug registers, and lazy IRQ helpers from `irq_64.c`. It is a central bridge between exception handlers and final return-to-user/kernel assembly.

## Risks And Edge Cases
High-risk areas are lost soft-masked interrupts, returning with wrong hard IRQ state, context tracking imbalance, KUAP unlocked across return, SRR clobbering by NMI/soft-NMI windows, transactional memory restore ordering, syscall error convention for `sc` versus `scv`, and stack-store emulation restart safety. Many functions are `notrace` because tracing in unreconciled interrupt state can recurse or touch unsafe vmaps.

## Test Signals
Signals include syscall ABI tests, signal/reschedule-on-exit tests, rseq selftests, ftrace/syscall tracing, KUAP fault tests, TM/math state restore tests, lockdep IRQ tracing, preemption-on-IRQ-return behavior, BookE debug single-step tests, and stress with soft-masked interrupt replay on Book3S64.
