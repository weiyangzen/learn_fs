## sources/distributed-fs/ceph-client/arch/x86/events/Kconfig

Purpose: Kconfig menu for x86 performance monitoring drivers.

Important configs: `PERF_EVENTS_INTEL_UNCORE`, `PERF_EVENTS_INTEL_RAPL`, `PERF_EVENTS_INTEL_CSTATE`, `PERF_EVENTS_AMD_POWER`, `PERF_EVENTS_AMD_UNCORE`, and `PERF_EVENTS_AMD_BRS`. Dependencies gate options on `PERF_EVENTS`, CPU vendor support, PCI, and AMD/Intel features.

Control flow: menu choices determine which perf-event modules/objects are compiled, including AMD BRS branch sampling.

State/persistence: selected config becomes compile-time state stored in `.config` and affects available PMUs and sysfs events.

Integration points: `arch/x86/events/Makefile`, AMD and Intel event drivers, perf userspace, and CPU feature detection.

Risks: incorrect dependencies can expose unsupported build combinations or hide supported PMUs. Test signals include allmodconfig/allyesconfig, vendor-specific builds, and perf PMU enumeration on Intel/AMD systems.
