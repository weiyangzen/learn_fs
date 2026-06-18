# sources/distributed-fs/ceph-client/arch/m68k/coldfire/entry.S

Purpose: low-level ColdFire exception, interrupt, syscall, and context-switch entry code. It bridges m68k trap frames with Linux syscall dispatch, `do_IRQ()`, signal/reschedule handling, and task switching.

Important entry points: `system_call`, `ret_from_exception`, `inthandler`, and `resume`. Optional `sw_ksp`/`sw_usp` exist when `CONFIG_COLDFIRE_SW_A7` needs software stack-pointer shadows. The code relies on `SAVE_ALL_SYS`, `SAVE_ALL_INT`, `RESTORE_USER`, `SAVE_SWITCH_STACK`, `RESTORE_SWITCH_STACK`, `GET_CURRENT`, and `PT_OFF_*` offsets from architecture headers.

Control flow and state: `system_call` saves registers, enables interrupts, bounds-checks `NR_syscalls`, fetches `sys_call_table[d0]`, supports syscall trace entry/exit, writes the return value into `PT_OFF_D0`, then falls into `ret_from_exception`. `ret_from_exception` disables interrupts, separates kernel from user returns, handles preemption for kernel returns, and loops through reschedule/signal work for user returns. `inthandler` extracts the vector from the exception frame, pushes vector and pt_regs, and calls `do_IRQ`. `resume` saves previous thread SR/KSP/USP, restores next thread state, updates current on MMU builds, and returns.

Dependencies and integration: Linux scheduler, ptrace/syscall tracing, signal delivery, IRQ core, and m68k task/thread layout. No persistence beyond per-task saved register state.

Risks and test signals: offset or frame-layout drift is catastrophic. Test with syscall smoke tests, ptrace/seccomp tracing, interrupt storms, preemption-enabled kernels, signal delivery, and task switching under MMU and no-MMU ColdFire configs.
