# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Kconfig

Purpose: Defines pseries platform build-time feature selection for IBM PowerVM/PAPR systems, including LPAR, shared-processor accounting, event IRQs, LPAR config, shared memory/CMM, HTM dump, hypervisor counters, IBM VIO/eBus, SVM, PAPR SCM, and keystore features.

Important APIs/types/functions: Major symbols are `PPC_PSERIES`, `PARAVIRT`, `PARAVIRT_SPINLOCKS`, `PARAVIRT_TIME_ACCOUNTING`, `PPC_SPLPAR`, `DTL`, `PSERIES_ENERGY`, `IO_EVENT_IRQ`, `LPARCFG`, `PPC_PSERIES_DEBUG`, `PPC_SMLPAR`, `CMM`, `HTMDUMP`, `HV_PERF_CTRS`, `VPA_PMU`, `IBMVIO`, `IBMEBUS`, `PSERIES_PLPKS`, `PAPR_SCM`, and `PPC_SVM`.

Control flow: Kconfig has no runtime flow; it establishes dependency and `select` relationships. Enabling `PPC_PSERIES` pulls in RTAS, XICS/XIVE, MSI, dynamic OF, hotplug CPU, SWIOTLB, and other architecture infrastructure. Optional entries gate compilation of the source files in this subset through the Makefile.

State and persistence: State is build configuration. Defaults such as `PPC_PSERIES=y`, `PPC_SPLPAR=y`, `IO_EVENT_IRQ=y`, `CMM=y`, `HTMDUMP=m`, and `HV_PERF_CTRS=y` influence the generated kernel image and modules.

Dependencies and integration points: This file integrates pseries platform code with architecture-wide config symbols such as `PPC64`, `PPC_BOOK3S`, `DEBUG_FS`, `MEMORY_HOTPLUG`, `LIBNVDIMM`, `ARCH_HAS_CC_PLATFORM`, and `KVM_BOOK3S_64_HV`.

Risks: Heavy `select` usage can enable large subsystem surfaces implicitly. Feature defaults compile pseries functionality into many PPC64 builds. Incorrect dependencies can produce link failures or runtime code on unsupported firmware.

Test signals: Config-matrix builds for pseries with and without debugfs, hotplug, CMM, HTM, secure guest, IBM eBus, and PAPR SCM; `scripts/config` dependency checks; and boot smoke tests on PowerVM LPARs are the main signals.

Source read size: 217 lines, 6753 bytes.
