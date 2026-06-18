# sources/distributed-fs/ceph-client/include/linux/soc/dove/pmu.h

Purpose: This Marvell Dove header declares power-management unit interfaces for controlling or querying Dove SoC PM state.

Important APIs/types/functions: `struct dove_pmu_domain_initdata` names a power domain and its power, reset, and isolation masks. `struct dove_pmu_initdata` carries PMC/PMU MMIO bases, IRQ data, IRQ-domain start, and a domain table. The exported functions are `dove_init_pmu_legacy` and `dove_init_pmu`.

Control flow: Legacy board code supplies explicit init data to `dove_init_pmu_legacy`; DT/platform paths can call `dove_init_pmu`. The PMU implementation uses the domain masks to sequence power, reset, and isolation.

State and persistence: PMU/PMC registers hold domain power, reset, isolation, and IRQ state. Domain metadata is static init data supplied at boot.

Dependencies and integration: Integrates with Marvell Dove ARM platform support, suspend/resume code, clocks, reset, and power-domain users.

Risks and test signals: Incorrect masks can hold a domain in reset or expose an unpowered bus. Test domain on/off transitions, IRQ-domain numbering, legacy and DT initialization, suspend/resume, and device probe after PMU registration.
