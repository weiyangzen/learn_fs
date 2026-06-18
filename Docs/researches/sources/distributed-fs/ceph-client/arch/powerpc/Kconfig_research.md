# sources/distributed-fs/ceph-client/arch/powerpc/Kconfig

## Purpose
Main PowerPC architecture configuration file. It declares architecture capabilities, compiler feature probes, memory layout defaults, security/trace/debug options, page-size choices, bus options, and includes platform/sysdev/kvm/livepatch configuration.

## Important APIs, Types, And Control Flow
The `PPC` symbol selects a large set of generic kernel features: ELF, BPF JIT, seccomp, ftrace, KASAN/KCSAN support, memory hotplug, VDSO, PCI/IOMMU helpers, module format, and PowerPC-specific facilities. Early feature probes include `CC_HAS_ELFV2`, `CC_HAS_PREFIXED`, and `CC_HAS_PCREL`. The file controls `32BIT`, `64BIT`, `MMU`, address-space randomization bits, IRQ counts, compatibility mode, DCR support, debug register counts, math emulation, transactional memory, ultravisor support, ftrace modes, hotplug CPU, crash dump, NUMA, memory models, page size, command-line policy, secure boot, bus options, and advanced 32-bit memory layout overrides.

Kconfig flow is declarative: defaults and dependencies derive architecture behavior, while `source` statements include cputype, sysdev, platforms, power management, kvm, and livepatch menus.

## State, Dependencies, Risks, And Tests
Persistent state is generated `.config` and derived headers. Dependencies span compiler/linker feature tests, platform symbols, generic kernel Kconfig, and PowerPC platform Kconfigs. Risks are unsatisfied `select` chains, impossible option combinations, page/layout defaults that produce broken early mappings, and compiler probe drift for pcrel/prefixed/ftrace. Test signals are `olddefconfig`, `randconfig`, representative ppc32/ppc64/ppc64le defconfigs, Kconfig warning-free runs, and build/boot coverage for page-size, crash, NUMA, secure boot, and tracing combinations.
