<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.h

Purpose: register offsets, filter bits, event encoding helpers, and optional prototypes for Intel IOMMU PMU support.

Important APIs/types/functions: macros define PMU offset-register layout, filter enable bits, config/counter capability offsets, counter capability extractors, and `iommu_event_select()`/`iommu_event_group()` decoders. Prototypes cover allocation, free, register, and unregister, with no-op stubs when `CONFIG_INTEL_IOMMU_PERF_EVENTS` is disabled.

Control flow: `perfmon.c` uses these helpers to parse hardware capabilities, format perf event config, locate per-counter filter registers, and conditionally compile PMU entry points.

State and persistence: no runtime state; it codifies the hardware ABI used to populate `struct iommu_pmu`.

Dependencies and integration: included by Intel IOMMU probe/remove and PMU code; relies on kernel bit helpers and Intel VT-d register definitions from `iommu.h`.

Risks: incorrect offsets or shifts would silently program wrong MMIO registers. Stubs returning success for allocation/register in disabled builds mean callers must not assume a PMU exists afterward.

Test signals: build with PMU enabled/disabled, static validation of event encodings, sysfs format strings matching macros, and hardware counter capability parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.h -->
