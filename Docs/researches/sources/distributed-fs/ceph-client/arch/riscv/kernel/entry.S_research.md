# sources/distributed-fs/ceph-client/arch/riscv/kernel/entry.S

Purpose: Implements the RISC-V trap/interrupt entry and return path, fork return assembly, IRQ stack switch, context switch, and exception vector table.

Important APIs/types/functions: Defines `handle_exception`, `ret_from_exception`, optional `handle_kernel_stack_overflow`, `ret_from_fork_kernel_asm`, `ret_from_fork_user_asm`, `call_on_irq_stack`, `__switch_to`, `excp_vect_table`, and no-MMU `__user_rt_sigreturn`.

Control flow: Trap entry swaps `tp` with scratch to distinguish user/kernel origin, handles new vmalloc retry/fence checks on kernel page faults, saves all registers and CSRs into `pt_regs`, disables SUM/FP/vector/ELP state, saves user shadow stack state when CFI is enabled, then dispatches interrupts to `do_irq` or exceptions through `excp_vect_table`. Return restores state, handles user work via C code before reentry when applicable, clears load reservations with an SC, restores CSRs/registers, and executes `sret` or `mret`.

State and persistence: Maintains per-task kernel/user stack pointers, scratch CSR, shadow call stack pointers, optional user SSP, per-CPU IRQ stack, and callee-saved thread context.

Dependencies and integration points: Tied to `pt_regs` offsets, trap C handlers, scheduler `__switch_to`, VMAP stack overflow handling, vector preemption hooks, shadow call stack, user CFI, alternatives, and syscall/signal paths.

Risks and test signals: Any register, CSR, stack, or alternate patch bug corrupts execution globally. Test syscall/interrupt/trap stress, page faults after vmalloc, VMAP stack overflow, FP/vector illegal-use detection, context switch torture, IRQ stacks, KASAN/stackleak, and user CFI shadow stack transitions.
