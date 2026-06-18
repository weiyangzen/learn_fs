# sources/distributed-fs/ceph-client/drivers/firmware/tegra/Makefile

Build recipe for Tegra firmware drivers. It composes `tegra-bpmp.o` from `bpmp.o` plus SoC-specific transport files and optional debugfs support, and builds `ivc.o` when `CONFIG_TEGRA_IVC` is enabled.

`bpmp-tegra210.o` is included for Tegra210. `bpmp-tegra186.o` is reused for Tegra186, Tegra194, Tegra234, and Tegra264 because those generations share the HSP mailbox plus IVC transport model. `bpmp-debugfs.o` is conditional on `CONFIG_DEBUG_FS`. `obj-$(CONFIG_TEGRA_BPMP)` emits the composite BPMP object; `obj-$(CONFIG_TEGRA_IVC)` emits the transport library.

The file has no runtime state. Integration risks are link-coverage related: SoC data in `bpmp.c` references `tegra186_bpmp_ops` or `tegra210_bpmp_ops` only under matching `IS_ENABLED()` guards, so Makefile conditions must stay aligned with those guards. Test signals are allmodconfig/randconfig builds across Tegra SoC symbols and DEBUG_FS enabled/disabled combinations.
