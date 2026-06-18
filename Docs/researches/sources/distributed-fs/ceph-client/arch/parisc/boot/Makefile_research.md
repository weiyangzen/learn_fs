<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/Makefile

## Purpose
Builds PA-RISC boot image artifacts.

## Important APIs, Types, And Functions
Defines targets for `image`, `bzImage`, and `compressed/vmlinux`. `image` copies `vmlinux`; `bzImage` copies either uncompressed `vmlinux` or compressed `boot/compressed/vmlinux` depending on `CONFIG_KERNEL_UNCOMPRESSED`; compressed target invokes the compressed subdirectory.

## Control Flow
Top-level PA-RISC image targets recurse here. Kbuild uses `$(call if_changed,shipped)` for copy-style outputs and `$(Q)$(MAKE)` for compressed image generation.

## State And Persistence
Produces boot image files under `arch/parisc/boot`.

## Dependencies And Integration Points
Depends on top-level `vmlinux`, compressed boot Makefile, and `CONFIG_KERNEL_UNCOMPRESSED`.

## Risks
Incorrect dependency selection can ship stale compressed or uncompressed images. Boot target names must match `arch/parisc/Makefile` aliases.

## Test Signals
Build `image`, `bzImage`, and `vmlinuz` with compressed and uncompressed kernel configurations; verify output timestamps and boot loader consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/Makefile -->
