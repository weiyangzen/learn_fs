## sources/distributed-fs/ceph-client/arch/x86/entry/syscall_64.c

Purpose: 64-bit and x32 syscall dispatch for x86-64. It maps generated syscall tables to callable functions, runs common syscall-entry/exit work, and decides whether assembly may return with `SYSRET`.

Important APIs/functions: `x64_sys_call()`, `x32_sys_call()`, `do_syscall_x64()`, `do_syscall_x32()`, and `do_syscall_64()`. It exposes `sys_call_table[]` for tracing metadata even though direct syscall dispatch uses switch-generated calls.

Control flow: `do_syscall_64()` receives `pt_regs` and a signed syscall number from assembly, runs `syscall_enter_from_user_mode()`, adds a random kernel-stack offset, attempts native x64 dispatch, then x32 dispatch when `__X32_SYSCALL_BIT` is present, and otherwise returns `ni_syscall` for invalid syscall numbers except `-1`. After `syscall_exit_to_user_mode()`, it validates the saved user frame for `SYSRET`.

State/persistence: updates `regs->ax` with return values and depends on `regs->cx`, `regs->r11`, `regs->ip`, `regs->flags`, `regs->cs`, and `regs->ss` remaining compatible with the architectural `SYSCALL/SYSRET` ABI.

Integration points: `entry_SYSCALL_64`, generated `syscalls_64.h` and `syscalls_x32.h`, tracing, seccomp, ptrace, x32 ABI, Xen PV, and `TASK_SIZE_MAX` user-address validation.

Risks: `SYSRET` is unsafe for noncanonical or kernel-range RIP and cannot restore RF correctly. Any missing `array_index_nospec()` would expose table speculation. Test signals include syscall ABI suites, x32 tests, ptrace/seccomp mutation tests, bad-RIP SYSRET tests, Xen PV boot, and trace_syscalls symbol validation.
