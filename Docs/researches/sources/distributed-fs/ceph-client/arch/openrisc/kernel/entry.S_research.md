<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/entry.S

## Purpose
Contains OpenRISC runtime exception handlers, syscall dispatch, user return work handling, context switching, fork wrappers, signal-return trampoline entry, and the legacy atomic syscall.

## Important APIs, Types, And Functions
Key labels include `_bus_fault_handler`, `_data_page_fault_handler`, `_insn_page_fault_handler`, `_timer_handler`, `_external_irq_handler`, `_sys_call_handler`, `_ret_from_intr`, `_ret_from_exception`, `ret_from_fork`, `_switch`, `__sys_clone`, `__sys_clone3`, `__sys_fork`, `sys_rt_sigreturn`, and `sys_or1k_atomic`. Macros save/restore `pt_regs`, manage interrupt tracing, and clear `lwa_flag`.

## Control Flow
Exception stubs save register state then call C handlers in `traps.c`, `fault.c`, `time.c`, or generic IRQ code. Syscall entry saves ABI-required registers, enables interrupts, optionally traces, bounds-checks the syscall number, calls through `sys_call_table`, stores `r11`, handles syscall-exit tracing, checks `_TIF_WORK_MASK`, and either returns through a fast path or calls `do_work_pending()`. `_switch` saves callee-saved registers and swaps `thread_info->ksp`.

## State And Persistence
Persists task register frames on kernel stacks, updates `orig_gpr11`, changes EPCR/ESR for return, clears load/store-atomic emulation state, and changes current kernel stack pointer.

## Dependencies And Integration Points
Depends on generated asm offsets, `thread_info` flags, syscall table, C exception handlers, scheduler, signal handling, ptrace/audit, and SPR definitions.

## Risks
This is the highest-risk ABI and privilege boundary. Register save omissions break syscall restart, ptrace, fork, or context switch. Interrupt state around EPCR/ESR restore is critical. The atomic syscall disables interrupts and ignores its type argument, so compatibility relies on legacy expectations.

## Test Signals
Syscall ABI tests, ptrace/audit syscall tracing, signal restart tests, interrupt return tests, fork/clone stress, context-switch stress, and illegal/page/timer/IRQ exception coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/entry.S -->
