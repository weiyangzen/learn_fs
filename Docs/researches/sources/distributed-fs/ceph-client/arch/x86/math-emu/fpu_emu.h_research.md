# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_emu.h

## Purpose
This is the main wm-FPU-emu shared header. It defines the internal floating-point register representation, tag values, exponent/sign constants, instruction prefixes, address-mode structures, stack macros, sign/exponent helpers, and prototypes for assembly arithmetic helpers.

## Important APIs, Types, and Functions
Key types are `struct address`, `struct fpu__reg`/`FPU_REG`, `FUNC`, `FUNC_ST0`, `overrides`, and `fpu_addr_modes`. Important constants include exponent bounds, tag values `TAG_Valid`/`TAG_Zero`/`TAG_Special`/`TAG_Empty`, special classifications `TW_Denormal`/`TW_Infinity`/`TW_NaN`, prefix constants, mode constants `VM86`, `PM16`, and `SEG32`, plus flags `REV`, `DEST_RM`, and `LOADED`. Helper macros include `st(x)`, `push()`, `poppop()`, sign manipulation, exponent manipulation, and `significand()`. It declares assembly helpers such as `FPU_u_add()`, `FPU_u_sub()`, `FPU_u_mul()`, `FPU_u_div()`, `wm_sqrt()`, `FPU_shrx()`, `FPU_div_small()`, and `FPU_round()`.

## Control Flow
The header has no standalone control flow, but it shapes almost every emulator branch by standardizing stack indexing, tag checks, sign operations, and conversion between stored extended exponent and internal exponent formats.

## State and Persistence
It maps persistent per-task soft-FPU state through macros from `fpu_system.h`: register stack memory, tag word, top pointer, control word, status word, and instruction/data pointers. It stores no file-local state.

## Dependencies and Integration Points
It includes `fpu_system.h`, signal context UAPI, math emulator task structures, and generated `fpu_proto.h`. It is included by nearly every emulator C file and by assembly files through the assembler branch.

## Risks and Test Signals
Risks are broad: structure layout or macro errors affect all arithmetic, decode, and state save/restore paths. Test signals include full soft-FPU instruction coverage, build coverage for assembler/C modes, regset save/restore tests, and comparison with hardware x87 behavior.
