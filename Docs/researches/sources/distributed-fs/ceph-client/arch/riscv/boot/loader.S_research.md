<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.S -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/loader.S

## Purpose
Creates a minimal loader object that embeds the raw RISC-V `Image` payload.

## Important APIs, Types, And Functions
Exports `_start` in the `.payload` executable section and includes `arch/riscv/boot/Image` with `.incbin`.

## Control Flow
There is no instruction flow beyond the symbol/section definition. Linker placement makes the payload available at the configured kernel link address.

## State And Persistence
State is the embedded Image bytes in the resulting loader object/binary.

## Dependencies And Integration Points
Depends on `loader.lds.S`, the boot Makefile, and a previously built `Image` file.

## Risks And Edge Cases
If the Image path, section name, or linker placement changes, M-mode loader binaries can be malformed.

## Test Signals
Signals are successful `loader.o`, `loader`, and `loader.bin` builds and boot tests for loader-based platforms.

Source read size: 8 lines, 143 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.S -->
