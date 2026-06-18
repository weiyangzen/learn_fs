<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/Makefile

## Purpose
Controls PA-RISC architecture compiler/linker flags, build directories, boot image targets, decompressor selection, vdso preparation, install targets, and cleanup.

## Important APIs, Types, And Functions
Sets `boot := arch/parisc/boot`, default `KBUILD_IMAGE`, 32/64-bit compiler flags, ABI flags, alignment and long-call options, `head-y`, core/libs/drivers paths, `KBUILD_CFLAGS_KERNEL`, `KBUILD_AFLAGS_MODULE`, and boot aliases such as `bzImage`, `zImage`, `Image`, and `vmlinuz`.

## Control Flow
Kbuild evaluates architecture width and config options, constructs flags, builds vDSO offsets when not external-module builds, routes image targets into boot sub-Makefiles, and defines install/zinstall behavior.

## State And Persistence
No runtime state; persists build choices in produced objects/images and generated vDSO offset headers.

## Dependencies And Integration Points
Depends on compiler support for PA-RISC flags, boot directory Makefile, kernel/vdso Makefiles, and install tooling.

## Risks
Wrong ABI flags produce unbootable or incompatible kernels. Long-call and huge-kernel decisions affect link reachability. Build target aliases must match boot loader expectations.

## Test Signals
32-bit and 64-bit PA-RISC builds, compressed/uncompressed images, module builds, vdso_prepare, `make install`, and clean targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Makefile -->
