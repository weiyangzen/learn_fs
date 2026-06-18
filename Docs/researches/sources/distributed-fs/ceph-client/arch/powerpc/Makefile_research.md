# sources/distributed-fs/ceph-client/arch/powerpc/Makefile

## Purpose
PowerPC architecture makefile. It sets cross-compiler defaults, ABI/endian/compiler/linker flags, default configs, boot image targets, generated defconfigs, VDSO preparation, stack protector guard flags, and a binutils guard.

## Important APIs, Types, And Control Flow
The file auto-detects `CROSS_COMPILE`, exports `BITS`, constructs `UTS_MACHINE`, sets endian flags, handles ELFv1/ELFv2 ABI flags, module save/restore linkage, relocatable link flags, model flags, ftrace instrumentation flags, CPU tuning, no-FPU/no-vector kernel flags, and pcrel/prefixed options. The default build target is `zImage`; boot targets recurse into `arch/powerpc/boot`. Generated defconfig targets merge fragments for pseries, powernv, 85xx, corenet, ppc32/ppc64 rand/allmod configs, and others. `prepare` builds VDSO offsets after `prepare0`, and stack protector preparation derives TLS guard offsets from generated asm offsets.

## State, Dependencies, Risks, And Tests
State is the kbuild variable environment and generated configuration targets. Dependencies include toolchain option probes, linker type/version, `scripts/Makefile.defconf`, arch configs, VDSO makefiles, and generated `asm-offsets.h`. Risks include wrong endian/ABI flags, clang/gcc divergence, module TOC model breakage, ftrace flag mismatch, broken cross32 boot wrapper builds, and binutils 2.37 recordmcount incompatibility. Test signals are ppc64le/ppc64/ppc32 builds with GCC and clang, module builds, boot wrapper targets, generated defconfigs, VDSO offset generation, and `checkbin` failure on known-bad linker combinations.
