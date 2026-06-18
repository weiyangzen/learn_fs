# sources/distributed-fs/ceph-client/drivers/perf/Kconfig

Purpose: Defines kernel configuration options for platform and uncore performance monitor drivers under the `PERF_EVENTS` menu.

Important APIs and entries: Entries in this subset include `ARM_CCI_PMU`, `ARM_CCI400_PMU`, `ARM_CCI5xx_PMU`, `ARM_CCN`, `APPLE_M1_CPU_PMU`, `ALIBABA_UNCORE_DRW_PMU`, and inclusion of `drivers/perf/amlogic/Kconfig` for `MESON_DDR_PMU`. The file also configures many adjacent PMU drivers such as CMN, NI, ARM PMU, RISC-V PMU, SMMUv3 PMCG, SPE, DMC620, CXL, Marvell, Nvidia, and Hisilicon PMUs.

Control flow: Kconfig dependency resolution determines which objects the Makefile can build. `ARM_CCI_PMU` selects common CCI support and gates model-specific booleans. `APPLE_M1_CPU_PMU` depends on `ARM_PMU && ARCH_APPLE`. `ALIBABA_UNCORE_DRW_PMU` depends on ARM64 ACPI or COMPILE_TEST. The Amlogic PMU is sourced from its subdirectory.

State and persistence: Kconfig selections persist in `.config` and determine build products and module availability. Help text documents module names and hardware scope.

Dependencies and integration points: Integrated by the kernel Kconfig tree and paired with `drivers/perf/Makefile`. Architecture, ACPI, PCI, CXL, MSI, NUMA, and COMPILE_TEST dependencies prevent unsupported builds or expose compile coverage.

Risks: Incorrect dependencies can either hide usable drivers or allow build/runtime breakage on unsupported architectures. Model sub-options under CCI affect compiled event tables and validation paths. Source ordering matters for subdirectory Kconfigs.

Test signals: `olddefconfig`, `menuconfig` visibility, randconfig/COMPILE_TEST coverage, module names matching help text, and object inclusion matching Makefile entries.
