<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/Makefile

## Purpose
Defines RISC-V architecture compiler, assembler, linker, Rust, image, VDSO, and install rules for the kernel build.

## Important APIs, Types, And Functions
Important variables and targets include `LDFLAGS_vmlinux`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_LDFLAGS`, `KBUILD_RUSTFLAGS`, `BITS`, `UTS_MACHINE`, `riscv-march-y`, `KBUILD_BASE_ISA`, `CC_FLAGS_FPU`, `KBUILD_IMAGE`, `libs-y`, `vdso_prepare`, `BOOT_TARGETS`, `install`, `rv32_randconfig`, `rv64_randconfig`, and `archhelp`.

## Control Flow
The Makefile derives ABI and ELF format from RV32/RV64 config, builds an ISA string from enabled extensions, strips F/D/V where inappropriate, applies relocation/ftrace/LTO/shadow-call-stack flags, prepares VDSO offsets, and routes image targets through `arch/riscv/boot`.

## State And Persistence
State is build-system state: generated flags, image target selection, VDSO generated headers, and install target behavior. It does not create runtime state directly but strongly shapes emitted instructions and boot image format.

## Dependencies And Integration Points
Integrated with top-level kbuild, toolchain feature probes, RISC-V Kconfig, EFI libstub zboot, arch/riscv/lib, VDSO builds, module builds, and `arch/riscv/boot/install.sh`.

## Risks And Edge Cases
Wrong ISA string construction can emit instructions unsupported by the boot CPU or by module builds. Relocatable/ftrace/LTO relaxation flags are subtle and can cause incorrect relocations. Stack protector offset extraction depends on generated asm offsets.

## Test Signals
Signals are successful RV32/RV64 builds, `make Image*`, `make vmlinuz.efi`, module builds with no relaxation issues, VDSO offset generation, sparse predefines, and boot tests on hardware or QEMU.

Source read size: 223 lines, 7947 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Makefile -->
