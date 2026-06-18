<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/boot.lds.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/boot.lds.S

## Purpose
Linker script for the Xtensa uncompressed ELF boot image. It places the reset vector, embedded kernel image, and bootstrap BSS at the addresses required by the Xtensa loader and kernel memory layout.

## Important APIs, Types, And Functions
Defines `OUTPUT_ARCH(xtensa)`, `ENTRY(_ResetVector)`, `.ResetVector.text`, `.image`, `_image_start`, `_image_end`, `.bss`, `__bss_start`, and `__bss_end`.

## Control Flow
At link time, reset-vector code is located at `XCHAL_RESET_VECTOR_VADDR`; the embedded `image` section is linked at `KERNELOFFSET` but loaded at `CONFIG_KERNEL_LOAD_ADDRESS`; BSS follows the loaded image aligned to four bytes.

## State And Persistence
It creates image-layout symbols consumed by bootstrap assembly. No runtime state beyond linker-defined addresses.

## Dependencies And Integration Points
Depends on `asm/vectors.h`, `CONFIG_KERNEL_LOAD_ADDRESS`, `KERNELOFFSET`, and `bootstrap.S`.

## Risks And Edge Cases
Wrong load or virtual address breaks early jump into the kernel. BSS placement must not overlap the embedded image. Reset vector address must match the core configuration.

## Test Signals
Inspect linked `Image.elf` with `readelf`, verify `_ResetVector` entry and section addresses, and boot under the chosen Xtensa platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/boot.lds.S -->
