<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/extable_fixup_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/extable_fixup_types.h

## Purpose
Exception-table fixup type encoding for x86 fault recovery. It defines packed type/register/flag/immediate fields used by assembly exception table annotations. The header is 71 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_EXTABLE_FIXUP_TYPES_H`; `#define EX_DATA_TYPE_MASK ((int)0x000000FF)`; `#define EX_DATA_REG_MASK ((int)0x00000F00)`; `#define EX_DATA_FLAG_MASK ((int)0x0000F000)`; `#define EX_DATA_IMM_MASK ((int)0xFFFF0000)`; `#define EX_DATA_REG_SHIFT 8`; `#define EX_DATA_FLAG_SHIFT 12`; `#define EX_DATA_IMM_SHIFT 16`; `#define EX_DATA_REG(reg) ((reg) << EX_DATA_REG_SHIFT)`; `#define EX_DATA_FLAG(flag) ((flag) << EX_DATA_FLAG_SHIFT)`; `#define EX_DATA_IMM(imm) ((imm) << EX_DATA_IMM_SHIFT)`; `#define EX_REG_DS EX_DATA_REG(8)`; `#define EX_REG_ES EX_DATA_REG(9)`; `#define EX_REG_FS EX_DATA_REG(10)`; `#define EX_REG_GS EX_DATA_REG(11)`; `#define EX_FLAG_CLEAR_AX EX_DATA_FLAG(1)`; `#define EX_FLAG_CLEAR_DX EX_DATA_FLAG(2)`; `#define EX_FLAG_CLEAR_AX_DX EX_DATA_FLAG(3)`

Notable declarations and inline helpers: `#define _ASM_X86_EXTABLE_FIXUP_TYPES_H`; `#define EX_DATA_TYPE_MASK ((int)0x000000FF)`; `#define EX_DATA_REG_MASK ((int)0x00000F00)`; `#define EX_DATA_FLAG_MASK ((int)0x0000F000)`; `#define EX_DATA_IMM_MASK ((int)0xFFFF0000)`; `#define EX_DATA_REG_SHIFT 8`; `#define EX_DATA_FLAG_SHIFT 12`; `#define EX_DATA_IMM_SHIFT 16`; `#define EX_DATA_REG(reg) ((reg) << EX_DATA_REG_SHIFT)`; `#define EX_DATA_FLAG(flag) ((flag) << EX_DATA_FLAG_SHIFT)`; `#define EX_DATA_IMM(imm) ((imm) << EX_DATA_IMM_SHIFT)`; `#define EX_REG_DS EX_DATA_REG(8)`; `#define EX_REG_ES EX_DATA_REG(9)`; `#define EX_REG_FS EX_DATA_REG(10)`; `#define EX_REG_GS EX_DATA_REG(11)`; `#define EX_FLAG_CLEAR_AX EX_DATA_FLAG(1)`; `#define EX_FLAG_CLEAR_DX EX_DATA_FLAG(2)`; `#define EX_FLAG_CLEAR_AX_DX EX_DATA_FLAG(3)`; `#define EX_TYPE_NONE 0`; `#define EX_TYPE_DEFAULT 1`; `#define EX_TYPE_FAULT 2`; `#define EX_TYPE_UACCESS 3`; `#define EX_TYPE_CLEAR_FS 5`; `#define EX_TYPE_FPU_RESTORE 6`

## Control Flow
No runtime control flow; macros compose fixup metadata consumed by the exception table search and fixup handlers after a faulting instruction.

## State and Persistence
Persistent state is absent; correctness is in the numeric ABI shared with assembly, uaccess, MSR, BPF, FPU restore, SGX, and ERETU fixups.

## Dependencies and Integration Points
Integrated by asm/extable.h users through _ASM_EXTABLE_TYPE* macros and by fault handlers decoding EX_TYPE_* and EX_DATA_* fields.

## Risks
Risks are ABI drift, sign-extension mistakes in EX_DATA_IMM, and mismatches between annotated register fields and recovery code.

## Test Signals
Build tests should assemble all extable users; fault-injection should cover uaccess, MSR safe access, FPU restore, MCE-safe, pop, and zeropad paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/extable_fixup_types.h -->
