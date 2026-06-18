<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/Makefile

## Purpose
Coordinates Xtensa boot image generation: raw `Image`, compressed `zImage`, U-Boot `uImage`, and XIP image outputs.

## Important APIs, Types, And Functions
Important targets and variables are `vmlinux.bin`, `vmlinux.bin.gz`, `boot-*`, `Image`, `zImage`, `uImage`, `xipImage`, `OBJCOPYFLAGS`, `UIMAGE_LOADADDR`, and `UIMAGE_COMPRESSION`.

## Control Flow
Kbuild strips `vmlinux` into a flat binary, gzips it for compressed images, selects boot loaders by platform, descends into `boot-elf` for `Image` and `boot-redboot` for `zImage`, wraps `vmlinux.bin.gz` as a U-Boot image, and objcopies `vmlinux` directly for XIP.

## State And Persistence
Build artifacts persist under `arch/xtensa/boot`: binary, gzip, ELF, redboot, U-Boot, and XIP images. No runtime state exists.

## Dependencies And Integration Points
Depends on boot subdirectories, boot lib archive, `uimage` command support, and `CONFIG_KERNEL_LOAD_ADDRESS`.

## Risks And Edge Cases
Wrong platform-to-target mapping yields unsupported images. U-Boot load address must match memory layout. XIP image must not be compressed.

## Test Signals
Run `make Image`, `zImage`, `uImage`, and `xipImage` for ISS, XT2000, and XTFPGA configurations and verify artifact names and headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/Makefile -->
