# sources/distributed-fs/ceph-client/arch/m68k/68000/entry.S

Purpose: non-MMU 68000 exception, syscall, interrupt, return-to-user, and task-switch assembly glue. It bridges CPU trap frames to generic kernel services.

Important entry points are `system_call`, `ret_from_exception`, `bad_interrupt`, `resume`, and the fixed autovector wrappers `inthandler1` through `inthandler7`. `system_call` saves registers with `SAVE_ALL_SYS`, calls `set_esp0`, bounds-checks `ORIG_D0` against `NR_syscalls`, dispatches through `sys_call_table`, and stores the return value in the saved pt_regs slot. If `TIF_SYSCALL_TRACE` is set, `do_trace` wraps dispatch with `syscall_trace_enter()` and `syscall_trace_leave()`.

Interrupt flow uses `SAVE_ALL_INT`, pushes a vector number and the pt_regs pointer, calls `process_int()`, then returns through `ret_from_exception`. The numbered handlers synthesize vectors 65-71 because this 68000 path cannot rely on richer exception-frame vector information. `bad_interrupt` increments `irq_err_count` and returns with `rte`.

State is almost entirely CPU register and stack state. `resume` persists task context by saving `sr`, kernel stack, and USP into `prev->thread`, restoring the same fields from `next->thread`, and returning to the scheduler caller. User return handling samples `thread_info->flags`, allows interrupts only near final restore, calls `do_notify_resume()` for signals, and branches to `reschedule` when requested.

Dependencies include `asm/entry.h` frame offsets, `thread_info` layout, `asm-offsets.h`, syscall table symbols, `process_int()`, `set_esp0()`, signal/reschedule hooks, and generic m68k trap code. Integration is direct: vector setup in `ints.c` installs these handlers, scheduler code calls `resume`, and syscall ABI correctness depends on the exact saved-register layout.

Risks and test signals: any pt_regs offset, stack adjustment, or interrupt-enable timing change can corrupt syscall arguments, lose signals, or overflow kernel stacks under interrupt load. Useful checks are m68k defconfig builds, syscall trace/strace behavior, forced invalid syscall returning `-ENOSYS`, timer interrupt delivery, signal delivery on return to user mode, and context-switch stress on non-MMU 68000 targets.
