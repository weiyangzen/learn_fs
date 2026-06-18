# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Makefile

Purpose: Maps HiSilicon perf Kconfig symbols to object files.

Important APIs/types/functions: `obj-$(CONFIG_HISI_PMU)` builds the common `hisi_uncore_pmu.o` plus L3C, HHA, DDRC, SLLC, PA, CPA, UC, NoC, and MN uncore PMU modules. `obj-$(CONFIG_HISI_PCIE_PMU)` builds `hisi_pcie_pmu.o`; `obj-$(CONFIG_HNS3_PMU)` builds `hns3_pmu.o`.

Control flow: Kernel kbuild expands selected config symbols into object lists during build.

State and persistence: No runtime state; build artifact selection is determined by `.config`.

Dependencies and integration: Closely tied to `Kconfig` and the shared `hisi_uncore_pmu` helper used by most objects in the `CONFIG_HISI_PMU` bundle.

Risks and test signals: Adding a new uncore file without updating this list prevents builds; building dependent uncore files without the helper object breaks links. Test by toggling each config and running ARM64 build/link checks.
