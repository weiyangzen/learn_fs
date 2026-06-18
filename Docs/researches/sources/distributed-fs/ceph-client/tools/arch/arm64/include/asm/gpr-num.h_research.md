# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/gpr-num.h

## Purpose
Supplies assembler-visible numeric aliases for arm64 general-purpose registers so macro-generated `mrs_s`/`msr_s` instructions can encode register operands by name.

## Important APIs, Types, and Functions
Defines `.L__gpr_num_x0` through `.L__gpr_num_x30`, matching `w0` aliases, plus `xzr`/`wzr` as 31. In C mode it provides `__DEFINE_ASM_GPR_NUMS`, a string fragment that emits the same `.equ` definitions inside inline assembly.

## Control Flow, State, and Persistence
There is no runtime flow. Consumers include this before defining assembler macros that need to map textual register names to instruction bits.

## Dependencies and Integration Points
Integrated by arm64 `sysreg.h` for unsupported-by-GAS system register access. It depends only on the assembler/C preprocessor split.

## Risks and Test Signals
Risk is limited but precise: a wrong register number corrupts generated system instructions. Test signals are assembly of `mrs_s`/`msr_s` macros for regular and zero registers and tools builds with older binutils paths.
