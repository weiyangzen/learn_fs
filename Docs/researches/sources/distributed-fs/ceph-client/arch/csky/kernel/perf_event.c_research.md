# sources/distributed-fs/ceph-client/arch/csky/kernel/perf_event.c

Purpose: C-SKY CPU PMU registration, event mapping, counter programming, and overflow handling.

Important APIs/types/functions: functions: `csky_pmu_read_cc`, `csky_pmu_write_cc`, `csky_pmu_read_ic`, `csky_pmu_write_ic`, `csky_pmu_read_icac`, `csky_pmu_write_icac`, `csky_pmu_read_icmc`, `csky_pmu_write_icmc`, `csky_pmu_read_dcac`, `csky_pmu_write_dcac`, `csky_pmu_read_dcmc`, `csky_pmu_write_dcmc`, `csky_pmu_read_l2ac`, `csky_pmu_write_l2ac`, `csky_pmu_read_l2mc`, `csky_pmu_write_l2mc`, `csky_pmu_read_iutlbmc`, `csky_pmu_write_iutlbmc`; types: `pmu_hw_events`, `perf_event`, `pmu`, `platform_device`, `hw_perf_event`, `perf_sample_data`, `pt_regs`, `device_node`; macros: `CSKY_PMU_MAX_EVENTS`, `DEFAULT_COUNT_WIDTH`, `HPCR`, `HPSPR`, `HPEPR`, `HPSIR`, `HPCNTENR`, `HPINTENR`, `HPOFSR`, `to_csky_pmu(p)`, `cprgr(reg)`, `cpwgr(reg,`

Control flow: Probe allocates per-CPU PMU state, maps perf attributes to counter indexes, programs coprocessor registers, requests per-CPU IRQs, registers CPU hotplug callbacks, and handles overflow by updating counts, sampling, and reloading periods.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/errno.h`, `linux/interrupt.h`, `linux/module.h`, `linux/of.h`, `linux/perf_event.h`, `linux/platform_device.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; perf stat/record, callchain, and overflow tests.
