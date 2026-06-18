# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries.h

Purpose: Declares shared pSeries platform interfaces used across setup, RAS, DLPAR, PCI, memory, CPU hotplug, security mitigation, RNG, and CMO code.

Important APIs/types/functions: Declares event-source IRQ setup, machine-check/system-reset handlers, SMP init and stopped-state constants, kexec CPU down, PCI fixups/MSI/controller ops, DLPAR helpers, memory/pmem/cpu hotplug hooks with stubs, CMO accessors, security mitigation setup, HBLKRM reading, RNG init, and SPAPR IOMMU grouping.

Control flow: Header-only inline behavior supplies no-op or `-EOPNOTSUPP` stubs when optional configs are absent and exposes CMO globals through accessors.

State and persistence: Does not own state; it names globals such as `rtas_poweron_auto`, CMO PSP/page-size values, and `pseries_security_flavor`.

Dependencies and integration points: Included throughout `arch/powerpc/platforms/pseries`. It mediates compile-time dependencies for SMP, memory hotplug, CPU hotplug, hash MMU, and SPAPR IOMMU features.

Risks: Prototypes here are cross-file contracts; changing signatures or stub semantics can break optional configuration builds. CMO accessors expose mutable globals initialized in `setup.c`.

Test signals: Build matrix across SMP/non-SMP, MEMORY_HOTPLUG, HOTPLUG_CPU, HASH_MMU, and SPAPR_TCE_IOMMU; runtime DLPAR and PCI paths that depend on declarations.

Source read size: 131 lines, 3627 bytes.
