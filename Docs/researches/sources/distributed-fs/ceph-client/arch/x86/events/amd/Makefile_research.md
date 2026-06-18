## sources/distributed-fs/ceph-client/arch/x86/events/amd/Makefile

Purpose: Kbuild rules for AMD-specific x86 performance monitoring support.

Important build objects: `core.o lbr.o` for AMD CPU support, `brs.o` for `CONFIG_PERF_EVENTS_AMD_BRS`, `power.o`, `ibs.o` with local APIC, `amd-uncore.o` from `uncore.o`, and `iommu.o` when `CONFIG_AMD_IOMMU` is set.

Control flow: compile-time selections combine CPU vendor support, PMU features, local APIC, uncore, and IOMMU availability.

State/persistence: produces AMD PMU drivers and modules/objects registered at init.

Integration points: AMD core PMU, branch stack mechanisms, IBS, power, uncore, IOMMU perf, and Kconfig.

Risks: dependencies must match hardware and exported helper availability. Test signals include AMD allmodconfig builds, perf PMU registration logs, IBS/BRS configurations, and IOMMU-enabled builds.
