# sources/distributed-fs/ceph-client/arch/microblaze/kernel/entry.S

Purpose: contains the central MicroBlaze low-level entry machinery for syscalls, traps, interrupts, debug traps, context switching, reset vectors, MB manager callbacks, and syscall table inclusion.

Important APIs and symbols: exports `_user_exception`, `ret_from_trap`, `ret_from_fork`, `ret_from_kernel_thread`, `full_exception_trap`, `unaligned_data_trap`, `page_fault_*_trap`, `ret_from_exc`, `_interrupt`, `_debug_exception`, `_switch_to`, `_reset`, optional `xmb_inject_err`, and `xmb_manager_register`. Macro blocks save/restore `pt_regs`, toggle BIP/EIP/IE/UMS/VMS, and switch physical/virtual mode.

Control flow: syscall entry builds a `pt_regs`, handles syscall tracing/seccomp/audit through `do_syscall_trace_enter()`, dispatches through `sys_call_table`, and returns through signal/reschedule work. Exception entries save state and call C handlers (`full_exception`, `do_page_fault`, `_unaligned_data_exception`). IRQ entry calls `do_IRQ` then handles user reschedule/signals or preemption. `_switch_to` saves/restores `cpu_context` and current-task state. The `.init.ivt` section emits physical branch vectors.

State and persistence: updates per-CPU `ENTRY_SP`/`CURRENT_SAVE`, `thread_info.cpu_context`, `pt_regs`, MSR bits, and optional MB-manager globals. No heap allocation.

Dependencies and integration: tightly coupled to `asm-offsets`, `thread_info`, `pt_regs`, `hw_exception_handler.S`, signal/ptrace/fault C code, and linker placement of `.init.ivt`.

Risks and test signals: register-save offsets, delay-slot return offsets, and physical/virtual transitions are high-risk. Test syscall tracing, fork/kernel threads, IRQ return to user/kernel, page faults, kgdb, MB manager builds, and boot vector copying.
