<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/Makefile

## Purpose
Defines Xtensa architecture build flags, variant/platform include paths, linker emulation, default cross-compiler prefix, boot targets, syscall header generation, and user-facing build help.

## Important APIs, Types, And Functions
Key variables are `variant-y`, `VARIANT`, `platform-*`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_LDFLAGS`, `CHECKFLAGS`, `vardirs`, `plfdirs`, `KBUILD_CPPFLAGS`, `KBUILD_DEFCONFIG`, `libs-y`, and `boot`.

## Control Flow
Kbuild derives the variant from `CONFIG_XTENSA_VARIANT_NAME`, optionally sets `CROSS_COMPILE`, selects a platform directory from `CONFIG_XTENSA_PLATFORM_*`, adds Xtensa-specific compiler flags such as `-mlongcalls` and `-mtext-section-literals`, enables call0 ABI flags when requested, adds variant/platform include paths, and forwards `Image`, `zImage`, `uImage`, or `xipImage` to `arch/xtensa/boot`.

## State And Persistence
No runtime state. It controls object code ABI, include resolution, generated boot artifacts, and sparse endianness defines.

## Dependencies And Integration Points
Depends on Kconfig symbols, Xtensa toolchain support, variant/platform directories, `arch/xtensa/lib`, boot Makefiles, and syscall-generation make targets.

## Risks And Edge Cases
Wrong ABI flags break assembly/C linkage. Missing variant include directories fail builds. `--no-relax` and PIC/FDPIC flags depend on toolchain behavior. Boot target forwarding must match files produced by boot subdirectories.

## Test Signals
Build representative Xtensa defconfigs with windowed and call0 ABI, big/little endian toolchains, all boot targets, and custom variant/platform paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Makefile -->
