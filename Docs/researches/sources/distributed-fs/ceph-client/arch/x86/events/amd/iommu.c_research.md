## sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.c

Purpose: registers one perf PMU per AMD IOMMU performance-counter block and implements counting-mode events for IOMMU memory/translation/interrupt command counters.

Important APIs/types/state: `struct perf_amd_iommu`, `perf_iommu_event_init()`, `perf_iommu_add/del/start/stop/read()`, `perf_iommu_enable_event()`, `perf_iommu_disable_event()`, `_init_events_attrs()`, `init_one_iommu()`, and `amd_iommu_pc_init()`. It defines sysfs format fields for `csource`, `devid`, `domid`, `pasid`, and masks, plus named v2 events.

Control flow: init checks `amd_iommu_pc_supported()`, builds event attributes, iterates all IOMMUs, allocates a PMU wrapper, discovers bank/counter counts, and registers `amd_iommu_N`. Event init rejects sampling and per-task attach because counters are shared and counting-only. Add allocates a free bank/counter under spinlock; start enables source/match registers and optionally zeroes the counter; stop reads before disabling to avoid power-gating zeros; read masks the 48-bit counter and accumulates into `event->count`.

State/persistence: per-IOMMU PMU list, assignment bitmask, raw spinlock, global cpumask showing CPU0, MMIO/PC registers in the AMD IOMMU, and dynamically allocated sysfs event attribute array.

Integration points: AMD IOMMU driver APIs, generic perf PMU API, sysfs PMU enumeration, Kconfig/Makefile AMD IOMMU gating, and hardware power-gating behavior.

Risks: bank/counter bit indexing must match hardware limits; the bounds check uses max values and should be reviewed for `>=` semantics. Because counts restart from zero and are accumulated on read, missed stop/read ordering loses data. Test signals include `perf stat -e amd_iommu_0/.../`, concurrent counter allocation exhaustion, IOMMU power-state tests, sysfs event/format inspection, and multi-IOMMU systems.
