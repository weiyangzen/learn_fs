<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscall.h

## Purpose
Implements the generic syscall-inspection API for OpenRISC `pt_regs`.

## Important APIs, Types, And Functions
`syscall_get_nr()` and `syscall_set_nr()` use `orig_gpr11`; rollback restores `gpr[11]`. Return/error accessors treat `gpr[11]` as the return register. Argument helpers copy six arguments from `gpr[3]` through `gpr[8]`. `syscall_get_arch()` returns `AUDIT_ARCH_OPENRISC`.

## Control Flow
Generic tracing, audit, seccomp, and restart paths call these small inlines while `entry.S` owns the low-level syscall dispatch.

## State And Persistence
Only modifies the live saved register frame. `orig_gpr11` is persistent across a syscall return path for restart and tracing decisions.

## Dependencies And Integration Points
Depends on `pt_regs` layout, audit constants, `IS_ERR_VALUE()`, and string copying. Integrates with `ptrace.c`, `signal.c`, and syscall entry assembly.

## Risks
Any register convention mismatch breaks syscall restart, tracing, audit arguments, or return values. Argument copy count must stay aligned with the OpenRISC syscall ABI.

## Test Signals
Run ptrace/audit/seccomp syscall tests, syscall restart after signals, and six-argument syscall cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscall.h -->
