# sources/distributed-fs/ceph-client/arch/mips/Makefile

## Purpose
`arch/mips/Makefile` is the architecture build driver for MIPS kernels. It chooses endian- and word-size-specific toolchain prefixes, compiler and assembler flags, linker emulations, boot-image targets, firmware and library directories, platform includes, generated helper tools, generic defconfig generation, install targets, and architecture help text.

## Important APIs, Types, And Variables
Important build variables include `KBUILD_DEFCONFIG`, `KBUILD_DTBS`, `tool-archpref`, `UTS_MACHINE`, `ld-emul`, `vmlinux-32`, `vmlinux-64`, `cflags-y`, `mips-cflags`, `KBUILD_AFLAGS`, `KBUILD_CFLAGS`, `KBUILD_CPPFLAGS`, `KBUILD_LDFLAGS`, `load-y`, `load-ld`, `entry-y`, `bootvars-y`, `libs-y`, `drivers-y`, `boot-y`, `bootz-y`, `generic_defconfigs`, and `BOARDS`. The `archscripts` target builds MIPS helper tools such as `elf-entry`, optional `loongson3-llsc-check`, and relocation tooling. The `gen_generic_defconfigs` and `describe_generic_defconfig` make functions synthesize generic MIPS defconfig targets from bitness, ISA revision, endian fragments, and board fragments.

## Control Flow
Make includes this file from the top-level kernel build. Early logic selects BFD formats, emulations, cross-compiler prefixes, and `UTS_MACHINE` based on `CONFIG_CPU_LITTLE_ENDIAN`, `CONFIG_32BIT`, and `CONFIG_64BIT`. It then appends ABI, no-PIC, soft-float, endian, CPU, erratum, and toolchain feature flags to `cflags-y`. Toolchain feature probes add defines such as `TOOLCHAIN_SUPPORTS_MSA`, `TOOLCHAIN_SUPPORTS_VIRT`, `TOOLCHAIN_SUPPORTS_XPA`, `TOOLCHAIN_SUPPORTS_CRC`, `TOOLCHAIN_SUPPORTS_DSP`, and `TOOLCHAIN_SUPPORTS_GINV`.

Firmware directories and platform-specific variables are added through `include $(srctree)/arch/mips/Kbuild.platforms`. The final compile/link flags are exported into Kbuild variables, boot variables are constructed from load and entry addresses, and boot targets recurse into `arch/mips/boot` or `arch/mips/boot/compressed`. The file also declares conversion rules for `vmlinux.32` and `vmlinux.64`, install rules, syscall header generation, and a dynamic set of generic defconfig targets.

## State And Persistence
The Makefile itself does not persist runtime state, but it determines generated artifacts: `vmlinux`, format-converted `vmlinux.32`/`vmlinux.64`, zboot images, U-Boot images, S-record/ECOFF/raw images, DTBs, generated arch tools, installed kernel/config/System.map files, and generated generic defconfig outputs. It also persists architecture assumptions into object code through compiler flags and preprocessor definitions.

## Dependencies And Integration Points
It depends on Kconfig symbols from `arch/mips/Kconfig`, `arch/mips/Kbuild.platforms` for platform-specific directories/load addresses, `arch/mips/tools`, `arch/mips/boot`, firmware directories, MIPS libraries, optional math emulation, PCI, crypto, and power directories. It integrates with top-level Kbuild variables, compiler feature probes, linker emulation names, objcopy, defconfig fragments under `arch/mips/configs/generic`, and install path conventions.

## Risks
Build flag changes can silently alter ABI, relocation behavior, exception table labels, or CPU erratum handling. The file deliberately disables PIC, abicalls, stack checking, asynchronous unwind tables, and assembler Loongson3 LLSC fixes for kernel correctness; removing these can cause subtle runtime failures. Load-address normalization differs for 32-bit and 64-bit links, and wrong `load-y` or `load-ld` values can create unbootable images. Generic defconfig synthesis depends on fragment naming conventions and `BOARDS` expansion. Platform includes can change boot targets and load addresses outside this file, so build regressions may appear platform-specific.

## Test Signals
Run representative `make ARCH=mips ..._defconfig` targets, including generated generic targets and legacy/platform defconfigs. Compile with GCC and Clang where supported, with 32-bit and 64-bit, big- and little-endian, microMIPS, MSA, XPA, relocatable, zboot, and Loongson workaround configurations. Validate that `archscripts` tools build before the kernel, `entry-y` is computed, boot images recurse with expected `bootvars-y`, and `make ARCH=mips help` lists generated generic and legacy defconfigs. For Alchemy, verify `Kbuild.platforms` selects the Alchemy platform Makefile and that `MIPS_FIXUP_BIGPHYS_ADDR` influences `setup.c` when PCI is enabled.
