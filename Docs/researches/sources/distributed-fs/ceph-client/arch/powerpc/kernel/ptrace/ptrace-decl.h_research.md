# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-decl.h

## Purpose
`ptrace-decl.h` is the internal contract for the split PowerPC ptrace implementation. It centralizes writeability limits, regset IDs, layout-offset helpers, and cross-file prototypes.

## Important APIs, Types, And Functions
Key macros include `MSR_DEBUGCHANGE`, `PT_MAX_PUT_REG`, `TVSO()`, `TFSO()`, and `TSO()`. `enum powerpc_regset` defines regset indexes for GPR, FPR, VMX, VSX, SPE, transactional memory checkpointed sets, PPR, DSCR, TAR, EBB, PMU, DEXCR, HASHKEYR, and PKEY depending on configuration. Prototypes cover FPR/VSX/Altivec/SPE accessors, GPR32 helpers, TM accessors, scalar register helpers, debug breakpoint handlers, and `user_ppc_native_view`.

## Control Flow
The header has no runtime flow, but its conditional declarations must match the Makefile-selected object files and the regset arrays in `ptrace-view.c`.

## State And Persistence
It stores no state. It defines which parts of `thread_struct`, `thread_fp_state`, and `thread_vr_state` other files are allowed to address.

## Dependencies And Integration Points
It depends on kernel regset definitions and PowerPC register constants. It is included by every C file in the ptrace subdirectory and is the binding between build-time feature selection and exported implementation symbols.

## Risks
Mismatched configuration guards can cause missing or duplicate symbols. Incorrect `PT_MAX_PUT_REG` or `MSR_DEBUGCHANGE` can accidentally allow userspace to modify privileged register bits. Regset enum ordering must remain consistent with array initialization in `ptrace-view.c`.

## Test Signals
Build coverage across feature matrices and `pt_regs_check()` failures are the main guardrails. Regset note ordering can also be validated through coredump and `PTRACE_GETREGSET` tests.
