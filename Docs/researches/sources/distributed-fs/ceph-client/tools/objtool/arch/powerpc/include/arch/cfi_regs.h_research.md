# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/cfi_regs.h

Purpose: PowerPC CFI register constants for objtool.

Important APIs/types/functions: aliases `CFI_BP` and `CFI_SP` to register 1, defines `CFI_RA` as 32, and sets `CFI_NUM_REGS` to 33.

Control flow: none; compile-time constants only.

State and persistence behavior: controls CFI array sizing and initial RA/SP register references. Because PowerPC stack validation support is limited, these mostly support basic initial state.

Dependencies and integration points: included by generic `cfi.h`, PowerPC decoder, and any shared CFI code compiled for PowerPC.

Risks: using `CFI_BP` as SP is a simplification; if full frame validation is added, more register semantics may be required.

Test signals: simple branch-only objtool operation should compile; future stack validation tests should verify register numbering against PPC ABI.
