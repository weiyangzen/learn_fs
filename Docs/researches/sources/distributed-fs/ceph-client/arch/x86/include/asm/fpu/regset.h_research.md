<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/regset.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/regset.h

## Purpose
Ptrace/core-dump regset declarations for x87, FXSR, software FPU, xstate, and xstate metadata exposure. The header is 23 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/regset.h>`

Notable constants/macros: `#define _ASM_X86_FPU_REGSET_H`; `#define xstateregs_active regset_fpregs_active`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_REGSET_H`; `extern user_regset_active_fn regset_fpregs_active, regset_xregset_fpregs_active,`; `extern user_regset_get2_fn fpregs_get, xfpregs_get, fpregs_soft_get,`; `extern user_regset_set_fn fpregs_set, xfpregs_set, fpregs_soft_set,`; `#define xstateregs_active regset_fpregs_active`

## Control Flow
No local logic; it exports regset active/get/set callback symbols selected by ptrace, coredump, and compat regset tables.

## State and Persistence
State is task FPU state marshalled through regset callbacks; aliases map xstateregs_active to regset_fpregs_active when needed.

## Dependencies and Integration Points
Depends on linux/regset.h and the implementation in arch/x86/kernel/fpu/regset.c.

## Risks
Risks are UABI size/layout mismatches, inactive-state reporting errors, and divergence between native, compat, and xstate regsets.

## Test Signals
Tests should include ptrace get/set for FP/FX/XSTATE, coredump notes, inactive tasks, compat tasks, and CPUs with/without XSAVE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/regset.h -->
