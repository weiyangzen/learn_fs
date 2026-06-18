# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-view.c

## Purpose
`ptrace-view.c` defines the PowerPC user regset views, scalar register get/set policy, register-name lookup helpers, and 32-bit compat GPR conversion.

## Important APIs, Types, And Functions
It exports `regs_query_register_offset()`, `regs_query_register_name()`, `ptrace_get_reg()`, `ptrace_put_reg()`, `user_ppc_native_view`, and `task_user_regset_view()`. It also defines native and compat `struct user_regset` arrays. Important internal functions include `gpr_get()`, `gpr_set()`, `ppr_get/set`, `dscr_get/set`, `tar_get/set`, EBB/PMU/DEXCR/HASHKEYR/PKEY handlers, `gpr32_get_common()`, and `gpr32_set_common()`.

## Control Flow
Scalar register access validates `thread.regs`, special-cases MSR, trap, DSCR, and SOFTE, bounds indexes with `array_index_nospec`, and only permits writes up to `PT_MAX_PUT_REG` plus sanitized trap/MSR fields. Regset get/set paths copy `struct user_pt_regs` while substituting synthetic or sanitized fields. Native and compat arrays are initialized with feature-guarded entries, and `task_user_regset_view()` returns the compat view for 32-bit tasks under `CONFIG_COMPAT`.

## State And Persistence
The file reads and writes `thread.regs`, `thread.dscr`, `thread.dscr_inherit`, TAR, EBB, PMU, DEXCR, HASHKEYR, and AMR/IAMR state. It does not own persistence; it provides controlled ptrace/coredump access to task state.

## Dependencies And Integration Points
It integrates with the Linux regset core, ELF core note types, seccomp/ptrace syscall paths, pkeys, CPU feature flags, and feature-specific accessors from the sibling ptrace files. `UTS_MACHINE` comes from the Makefile for the native view name.

## Risks
This is ABI-sensitive code. Register ordering, note types, sizes, and compat conversions must not change casually. Writable MSR bits are intentionally restricted, SOFTE is forced to a benign value, PKEY writes are masked by UAMOR, and DEXCR HDEXCR is read-only. Mistakes can leak privileged state or break debuggers and coredump consumers.

## Test Signals
Signals include `PTRACE_GETREGS/SETREGS`, `PTRACE_GETREGSET/SETREGSET`, native and compat coredumps, register-name lookup tests, MSR/trap/DSCR write sanitization, PKEY AMR masking, CPU-feature-gated EBB/PMU/DEXCR/HASHKEYR availability, and `pt_regs_check()` build assertions.
