# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/cfi_regs.h

Purpose: LoongArch CFI register numbering used by objtool's architecture-neutral CFI state.

Important APIs/types/functions: defines `CFI_RA`, `CFI_SP`, argument register `CFI_A0`, frame pointer `CFI_FP`, callee-saved `CFI_S0` through `CFI_S8`, `CFI_NUM_REGS`, and aliases `CFI_BP` to `CFI_FP`.

Control flow: no runtime control flow; this header is compiled into CFI structures and architecture decoder logic.

State and persistence behavior: determines array sizes for `struct cfi_init_state` and `struct cfi_state`. Incorrect numbering persists indirectly into ORC metadata because saved registers are serialized by architecture ORC code.

Dependencies and integration points: included by `include/objtool/cfi.h`; consumed by LoongArch decode and ORC files plus shared `check.c` stack validation.

Risks: register numbers must match LoongArch GPR numbering and `arch_reg_name`. A mismatch corrupts unwinder state silently.

Test signals: compile-time coverage for LoongArch objtool plus ORC dump inspection showing SP/FP/RA mappings for simple functions.
