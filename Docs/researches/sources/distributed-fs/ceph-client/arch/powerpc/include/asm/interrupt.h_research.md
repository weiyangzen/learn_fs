# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/interrupt.h

Purpose: Centralizes PowerPC interrupt vector numbers, exception entry/exit preparation, NMI handling, and declaration/definition macros for C interrupt handlers.

Important APIs, types, and functions: Defines `INTERRUPT_*` vector offsets, soft-mask assertions, restart-table search prototypes, `interrupt_enter_prepare()`, `interrupt_exit_prepare()`, async and NMI prepare/exit helpers, `struct interrupt_nmi_state`, handler attributes, `DECLARE_*` and `DEFINE_*` handler macros, many exception handler declarations, syscall/interrupt exit helpers, and replay functions.

Control flow: Low-level assembly calls generated C wrappers. Wrappers run enter preparation, invoke the typed handler, run exit preparation, and mark functions not probeable. NMI paths save/restore ftrace and irq state separately.

State and persistence: Uses pt_regs, soft-mask state, interrupt restart tables, tracing/lockdep state, and temporary NMI state. No persistent storage exists.

Dependencies and integration points: Integrates low-level exception vectors, tracing, lockdep, KCSAN/KASAN attributes, syscall exit, soft interrupt replay, page fault, machine check, HMI, and IRQ handlers.

Risks: Entry/exit ordering is delicate: IRQ state, tracing, RCU, and restart table handling must match context. Handler macros encode ABI and probe restrictions. Reentrancy around NMI and masked interrupts is high risk.

Test signals: Exception entry for all declared handlers, syscall exit restart paths, soft-mask assertion coverage, NMI/ftrace disable behavior, machine check/HMI paths, and lockdep/RCU tracing under interrupt storms.
