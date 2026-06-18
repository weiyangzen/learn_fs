<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/traps.c

Purpose: Handles RISC-V traps, exceptions, breakpoints, syscalls, page faults, IRQ entry, BUG validation, and bad kernel stacks.

Important APIs/types/functions: Key functions include `die()`, `do_trap()`, generated `DO_ERROR_INFO` handlers, `do_trap_insn_illegal()`, misaligned trap dispatchers, `handle_break()`, `do_trap_break()`, `do_trap_ecall_u()`, `handle_user_cfi_violation()`, `do_trap_software_check()`, `do_page_fault()`, `do_irq()`, `is_valid_bugaddr()`, and `handle_bad_stack()`.

Control flow: Synchronous exceptions enter specific handlers that either fix up kernel faults, emulate supported user faults, deliver signals, or die. Illegal instruction traps try vector first-use handling before SIGILL. User ecall advances EPC, dispatches through `sys_call_table`, and enters syscall tracing/audit hooks. Breakpoints route kprobes/uprobes/BPF before SIGTRAP. IRQ entry switches through generic IRQ handling.

State and persistence: Mutates pt_regs, syscall return registers, signal state, probe state, per-CPU overflow stacks, and global `show_unhandled_signals`. It has no durable storage beyond diagnostics.

Dependencies and integration points: Central integration for page fault code, syscall table, kprobes/uprobes, vector first-use, misaligned emulation, user CFI, BPF breakpoints, IRQ subsystem, and oops/panic machinery.

Risks: Trap handlers run in sensitive contexts; wrong EPC advancement can replay or skip instructions. CFI and probe breakpoints must be ordered correctly. Kernel/user mode classification controls whether faults are fixed up or fatal.

Test signals: Syscall tracing, illegal vector first-use, breakpoints with kprobes/uprobes/BPF, misaligned load/store behavior, page fault tests, BUG/oops decoding, bad-stack overflow handling, and CFI violation signals.

Source read size: 486 lines, 12279 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps.c -->
