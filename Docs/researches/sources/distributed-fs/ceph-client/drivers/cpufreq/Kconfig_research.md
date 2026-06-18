# sources/distributed-fs/ceph-client/drivers/cpufreq/Kconfig

Purpose: top-level Kconfig menu for Linux CPU frequency scaling support, governors, generic DT/virtual drivers, and architecture-specific cpufreq driver inclusion.

Important APIs/types/functions: defines `CPU_FREQ`, governor infrastructure options (`CPU_FREQ_GOV_ATTR_SET`, `CPU_FREQ_GOV_COMMON`), stats option, default-governor choice, individual governor configs, generic DT/Rust/virtual platform driver configs, `CPUFREQ_DT_PLATDEV`, and selected platform driver symbols such as `QORIQ_CPUFREQ`, `ACPI_CPPC_CPUFREQ`, and `ACPI_CPPC_CPUFREQ_FIE`. Sources architecture-specific Kconfig files for x86, ARM, PowerPC, MIPS, LoongArch, SPARC, and SuperH.

Control flow: configuration is gated by `if CPU_FREQ`. The default governor choice selects the corresponding governor and often performance as fallback. Generic and architecture blocks expose driver symbols based on architecture and dependency predicates. `source` directives pull deeper driver menus into this top-level menu.

State and persistence: Kconfig state persists in the kernel `.config`; it controls which objects are compiled, which governor is default at boot, and whether sysfs stats and FIE support exist. It has no runtime state.

Dependencies and integration: integrates with the cpufreq core build, scheduler utilization through schedutil, OPP/clock/DT subsystems for DT drivers, ACPI processor/CPPC support, and architecture-specific Kconfig fragments.

Risks: dependency expressions influence build coverage and runtime availability; selecting a default governor implicitly pulls modules into the build. New driver options must be matched with `Makefile` object lines. Architecture `source` paths must stay synchronized with the tree layout.

Test signals: `olddefconfig`/`allyesconfig`/`allmodconfig` across architectures, Kconfig linting, verifying default governor symbols select expected modules, and ensuring every enabled driver symbol has a Makefile object and required dependencies.
