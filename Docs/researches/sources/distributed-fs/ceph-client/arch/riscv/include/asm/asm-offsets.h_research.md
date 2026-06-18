<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-offsets.h

## Purpose
Forwards generated C-structure offsets to RISC-V assembly sources.

## Important APIs, Types, And Functions
include-time glue with no public C type or function declarations.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `generated/asm-offsets.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 1 lines, 35 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-offsets.h -->
