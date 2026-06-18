<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kconfig -->
# sources/distributed-fs/ceph-client/arch/riscv/Kconfig

## Purpose
Defines the primary RISC-V architecture configuration surface for Linux, including architecture capabilities, ISA options, memory models, SMP, alternatives, toolchain feature gates, unaligned-access policy, boot options, ACPI/EFI, KASLR, compatibility, power management, and KVM inclusion.

## Important APIs, Types, And Functions
Key symbols include `RISCV`, `64BIT`, `32BIT`, `RISCV_M_MODE`, `RISCV_SBI`, `MMU`, `PGTABLE_LEVELS`, `NONPORTABLE`, `ARCH_RV32I`, `ARCH_RV64I`, `CMODEL_MEDLOW`, `CMODEL_MEDANY`, `SMP`, `NR_CPUS`, `RISCV_ALTERNATIVE`, many `RISCV_ISA_*` extension symbols, `FPU`, `IRQ_STACKS`, scalar/vector unaligned access choices, `RISCV_BOOT_SPINWAIT`, `RELOCATABLE`, `RANDOMIZE_BASE`, `RISCV_USER_CFI`, `EFI`, `PORTABLE`, and source includes for SoC, errata, vendor, power, cpufreq/cpuidle, KVM, ACPI, and virtio.

## Control Flow
Kconfig starts by declaring architecture-wide `select` capabilities, then derives toolchain compatibility symbols, memory and platform choices, ISA extension choices, unaligned access policy, kernel feature menus, boot option menus, and downstream subsystem menus. The resulting configuration drives the RISC-V Makefile, compiler ISA strings, runtime patching, drivers, and ABI support.

## State And Persistence
State is configuration-time state persisted in `.config` and generated headers. It controls boot ABI, supported ISA extensions, page-table layout, runtime alternatives, module support, and whether firmware, ACPI, EFI, KVM, crypto, and power features are compiled.

## Dependencies And Integration Points
Depends on global kernel Kconfig infrastructure, compiler/binutils feature probes, RISC-V SoC/errata/vendor Kconfig fragments, kernel power and virtualization menus, ACPI, virtio, and architecture source files that test these symbols.

## Risks And Edge Cases
Bad dependencies can produce kernels that boot on the wrong privilege level, emit unsupported instructions, expose unsupported user ABI, or miss required runtime patching. `NONPORTABLE` options and assumed unaligned access settings are intentionally risky. Toolchain probes are brittle across compiler/assembler versions.

## Test Signals
Signals are defconfig/randconfig coverage for RV32/RV64, toolchain option probes, successful builds with and without MMU/SMP/EFI/ACPI/KVM, boot logs showing detected ISA and alternatives, and hwprobe/user ABI behavior for vector and unaligned access.

Source read size: 1381 lines, 45085 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kconfig -->
