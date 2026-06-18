# sources/distributed-fs/ceph-client/drivers/memory/emif-asm-offsets.c

## Purpose
`emif-asm-offsets.c` is a tiny build helper used to emit TI EMIF SRAM/assembly offsets. It exists so generated assembly constants stay synchronized with C structure layouts from `linux/ti-emif-sram.h`.

## Important APIs, Types, And Functions
The file includes `linux/ti-emif-sram.h` and calls `ti_emif_asm_offsets()` from `main()`. It defines no runtime driver state and no kernel entry point.

## Control Flow
The generated host/build program starts at `main()`, invokes `ti_emif_asm_offsets()`, and exits with zero. The called helper is expected to print or emit offset definitions as part of the kernel build.

## State And Persistence
There is no runtime state, persistence, MMIO, or device-tree behavior. Its output is a build artifact consumed by low-level EMIF PM assembly code.

## Dependencies And Integration Points
The only integration point is the EMIF SRAM header and the build system rule that compiles and runs offset generators. It is logically coupled to `emif.h` and TI EMIF suspend/resume assembly.

## Risks
Any mismatch between this generator and the assembly consumers can break suspend/resume or self-refresh code at runtime. Because the file is minimal, most risk is in the included header and build-system invocation rather than this source body.

## Test Signals
Build tests should confirm the offset generator compiles for the target configuration and that assembly files consuming the generated offsets assemble successfully. Runtime PM tests indirectly validate that generated offsets match the C layout.
