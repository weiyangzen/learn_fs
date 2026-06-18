# sources/distributed-fs/ceph-client/arch/loongarch/Makefile

## Purpose

`Makefile` is the top-level LoongArch architecture Makefile. It selects default defconfig, image names, cross-compile prefixes, ABI/toolchain flags, relocation policy, objtool/Rust flags, load address, VDSO preparation, libraries, drivers, install, and help targets. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the set of Kbuild variables and targets such as `KBUILD_DEFCONFIG`, `KBUILD_IMAGE`, `cflags-y`, `ld-emul`, `KBUILD_AFLAGS`, `KBUILD_CFLAGS`, `KBUILD_RUSTFLAGS`, `load-y`, `vdso_prepare`, `vmlinux.elf`, `vmlinux.efi`, and `install`. Concrete declarations observed in the file: Build/script rules: `boot	:= arch/loongarch/boot`, `KBUILD_DEFCONFIG := loongson32_defconfig`, `KBUILD_DEFCONFIG := loongson64_defconfig`, `KBUILD_DTBS      := dtbs`, `image-name-y			:= vmlinux`, `image-name-$(CONFIG_EFI_ZBOOT)	:= vmlinuz`, `KBUILD_IMAGE	:= $(boot)/vmlinux.elf`, `KBUILD_IMAGE	:= $(boot)/$(image-name-y).efi`, `32bit-tool-archpref	= loongarch32`, `64bit-tool-archpref	= loongarch64`, `32bit-bfd		= elf32-loongarch`, `64bit-bfd		= elf64-loongarch`, `32bit-emul		= elf32loongarch`, `64bit-emul		= elf64loongarch`, `CC_FLAGS_FPU		:= -mfpu=64`, `CC_FLAGS_NO_FPU		:= -msoft-float`, `orc_hash_h := arch/$(SRCARCH)/include/generated/asm/orc_hash.h`, `orc_hash_sh := $(srctree)/scripts/orc_hash.sh`, and 75 more.

## Control Flow, State, And Persistence

Build flow resolves 32-bit versus 64-bit toolchain mode, probes compiler/assembler options, prepares ORC/VDSO generated headers, selects EFI or ELF image generation, and delegates boot image creation to `arch/loongarch/boot`.

## Dependencies And Integration Points

It integrates with Kconfig feature probes, scripts/orc_hash.sh, objtool, Rust target settings, EFI stub libraries, VDSO build, and platform install scripts.

## Risks And Test Signals

Risks are toolchain option incompatibility, wrong ABI/load address, broken relocatable/EFI image flags, or VDSO generation failures. Test signals are 32-bit/64-bit defconfig builds, `make Image` equivalents, EFI zboot builds, objtool-enabled builds, and cross-compile prefix detection.
 A local static signal for this file is that it has 232 lines and 7932 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
