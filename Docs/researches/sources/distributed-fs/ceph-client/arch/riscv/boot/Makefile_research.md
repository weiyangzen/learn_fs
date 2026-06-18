<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/Makefile

## Purpose
Builds RISC-V bootable kernel images from vmlinux, including raw Image, compressed images, M-mode loader, XIP image, and EFI zboot artifacts.

## Important APIs, Types, And Functions
Key targets and variables are `OBJCOPYFLAGS_Image`, `OBJCOPYFLAGS_loader.bin`, `OBJCOPYFLAGS_xipImage`, `targets`, `$(obj)/Image`, compression targets, `$(obj)/loader.o`, `$(obj)/loader`, `$(obj)/loader.bin`, `EFI_ZBOOT_PAYLOAD`, `EFI_ZBOOT_BFD_TARGET`, and `EFI_ZBOOT_MACH_TYPE`.

## Control Flow
Kbuild objcopies vmlinux to `Image`, compresses it on demand, assembles loader.o by embedding Image, links loader with loader.lds, converts loader to loader.bin, and includes the shared EFI zboot makefile for `vmlinuz.efi`.

## State And Persistence
State is generated boot artifacts in the object tree. No runtime state is owned here, but linker/objcopy choices define what bootloaders consume.

## Dependencies And Integration Points
Depends on top-level RISC-V Makefile targets, objcopy, compression tools, LD, `loader.S`, `loader.lds.S`, and EFI libstub zboot infrastructure.

## Risks And Edge Cases
Bad objcopy stripping, missing Image dependencies, or incorrect EFI target metadata can produce unbootable images. Loader linking is specific to M-mode/K210-style paths.

## Test Signals
Signals are `make ARCH=riscv Image`, compressed image targets, `loader.bin`, `xipImage`, and `vmlinuz.efi`, plus bootloader/QEMU smoke tests.

Source read size: 59 lines, 1633 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/Makefile -->
