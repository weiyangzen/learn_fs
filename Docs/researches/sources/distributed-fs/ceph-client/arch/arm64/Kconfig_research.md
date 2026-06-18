## sources/distributed-fs/ceph-client/arch/arm64/Kconfig

### Purpose
Defines the ARM64 architecture configuration surface: base architecture capabilities, erratum workarounds, page/VA/PA geometry, CPU and memory features, security extensions, virtualization, boot, power management, and included subsystem Kconfigs.

### Important APIs, Types, And Functions
Major symbols include `ARM64`, `RUSTC_SUPPORTS_ARM64`, `PGTABLE_LEVELS`, `ARCH_SUPPORTS_UPROBES`, many `ARM64_ERRATUM_*` workarounds, page-size choices, `ARM64_VA_BITS`, `ARM64_PA_BITS`, `CPU_BIG_ENDIAN/LITTLE_ENDIAN`, `NR_CPUS`, `NUMA`, `PARAVIRT`, `XEN`, `ARM64_PTR_AUTH`, `ARM64_BTI`, `ARM64_MTE`, `ARM64_SVE`, `ARM64_SME`, `RANDOMIZE_BASE`, `EFI`, and many included subsystem sources.

### Control Flow
Kconfig selects generic kernel capabilities from `config ARM64`, then presents menus for errata, kernel features, boot, power management, CPU power, ACPI, KVM, livepatch, and architectural extensions. Choices and defaults derive page-table levels, virtual address bits, physical address bits, endianness, and security feature enablement.

### State, Persistence, And Dependencies
The persistent output is the kernel `.config` and generated config headers. Dependencies encode compiler, assembler, linker, CPU feature, firmware, and subsystem constraints. It also sources `arch/arm64/Kconfig.platforms`, `arch/arm64/kvm/Kconfig`, and many generic Kconfigs.

### Integration Points
Controls nearly every ARM64 build and runtime integration point: memory management, tracing, BPF, KASAN, CFI, SCS, PAC/BTI, MTE, SVE/SME, ACPI/EFI, Xen/KVM, NUMA, hibernation, and boot command line handling.

### Risks
Defaults can enable hardware workarounds or features that depend on firmware/toolchain support. Incorrect dependency expressions may expose unsupported instructions, ABI flags, or security features. Config combinations around page size, VA/PA bits, KASAN, LPA2, and compat affect ABI and boot viability.

### Test Signals
Run `allnoconfig`, `defconfig`, `allyesconfig`, big-endian, KASAN, KVM, Xen, EFI, SVE/SME, MTE, PAC/BTI, and multiple page-size builds; boot representative configurations and validate generated `autoconf.h`.
