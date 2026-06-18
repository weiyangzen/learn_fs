<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_64.h

## Purpose
This header defines SPARC64 boot-header constants and early image metadata.

## Important APIs, Types, and Functions
It provides boot signature/layout values consumed by SPARC64 head assembly and boot tools, including fields patched for initrd support.

## Control Flow
Early assembly emits header fields; `piggyback` and bootloaders locate the `HdrS` signature and patch/read ramdisk metadata.

## State and Persistence Behavior
State is the persistent boot image header. Runtime code consumes values during early boot.

## Dependencies and Integration Points
It integrates with PROM/a.out image handling, `piggyback`, early kernel entry, and initrd setup.

## Risks
Header layout drift breaks in-place image patching and bootloader expectations.

## Test Signals
Build `vmlinux.aout` and `tftpboot.img`, inspect `HdrS` location, and boot SPARC64 images with and without initrd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/head_64.h -->
