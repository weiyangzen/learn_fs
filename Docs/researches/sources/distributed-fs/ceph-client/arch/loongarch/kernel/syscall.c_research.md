## sources/distributed-fs/ceph-client/arch/loongarch/kernel/syscall.c

### Purpose
`syscall.c` defines LoongArch syscall table wiring and syscall entry handling. It also provides LoongArch-specific `mmap` and `mmap2` syscalls that validate offset alignment before delegating to `ksys_mmap_pgoff`.

### Important APIs, Types, And Functions
Public pieces are `SYSCALL_DEFINE6(mmap)`, `SYSCALL_DEFINE6(mmap2)`, `sys_call_table`, and `do_syscall`. The syscall table includes either `asm/syscall_table_32.h` or `asm/syscall_table_64.h`. Entry uses `syscall_enter_from_user_mode`, `syscall_exit_to_user_mode`, `array_index_nospec`, and `add_random_kstack_offset`.

### Control Flow
`do_syscall` reads syscall number from `a7` (`regs[11]`), records a restart marker in `regs[0]`, advances ERA past the syscall instruction, saves original `a0`, initializes return value to `-ENOSYS`, runs generic syscall-enter hooks, randomizes kernel stack offset, dispatches through the nospec-indexed table if in range, places return value in `a0`, and exits to user mode.

### State, Persistence, And Dependencies
Syscall restart state persists transiently in `regs[0]` and `orig_a0` for signal handling. The syscall table is static kernel ABI. Dependencies include generated syscall headers, LoongArch syscall ABI register assignments, and generic entry/exit tracing, audit, seccomp, and random-kstack code.

### Integration Points
Low-level exception assembly calls `do_syscall`. `signal.c` interprets `regs[0]`, `regs[4]`, `orig_a0`, and ERA for syscall restart. Seccomp/audit/tracing hooks run through generic entry code.

### Risks
ERA adjustment and restart flag handling must match signal restart code exactly. `mmap2` offset shifting depends on `PAGE_SHIFT`. The syscall table default to `sys_ni_syscall` is safe only if generated includes cover all valid numbers.

### Test Signals
Run syscall ABI tests, seccomp/audit/tracepoint tests, interrupted syscall restart scenarios, `mmap`/`mmap2` offset alignment tests, and 32-bit vs 64-bit table builds.
