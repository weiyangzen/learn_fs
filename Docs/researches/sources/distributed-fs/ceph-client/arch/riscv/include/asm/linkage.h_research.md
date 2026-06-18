<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/linkage.h

## Purpose
Defines RISC-V function alignment used by assembler linkage macros.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
It has no direct includes. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 12 lines, 267 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/linkage.h -->
