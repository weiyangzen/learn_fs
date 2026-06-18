# sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.c

Purpose: common NVIDIA Tegra Memory Controller platform driver. It binds SoC data tables to MMIO, error interrupts, SMMU, reset-controller hot resets, EMEM timing programming, latency allowance defaults, carveout queries, and interconnect provider nodes.

Important APIs/types/functions: exported APIs include `devm_tegra_memory_controller_get()`, `tegra_mc_probe_device()`, `tegra_mc_get_carveout_info()`, `tegra_mc_write_emem_configuration()`, and `tegra_mc_get_emem_device_count()`. Internal core paths include hotreset assert/deassert/status, `tegra_mc_setup_latency_allowance()`, `tegra_mc_setup_timings()`, `tegra30_mc_probe()`, `tegra30_mc_handle_irq()`, `tegra_mc_interconnect_setup()`, and `tegra_mc_probe()`.

Control flow: `arch_initcall()` registers the platform driver early. Probe selects SoC data by OF match, coerces DMA mask to SoC address width, maps registers, creates debugfs root, runs SoC probe hooks, detects enabled channels, registers IRQs and writes masks, registers reset controller if available, initializes interconnect provider nodes, and optionally probes Tegra SMMU. Error IRQ handling identifies channel, decodes status/address/client/error type, logs rate-limited diagnostics, and clears channel/global status. Hotreset assert blocks DMA, waits for idling, then asserts SoC reset; deassert releases reset and unblocks DMA.

State and persistence: `struct tegra_mc` holds SoC data, MMIO pointers, channel count, loaded timing table, reset controller, interconnect provider, SMMU pointer, spinlock, and debugfs root. Hardware state includes interrupt masks, latency allowance registers, EMEM timing registers, reset control bits, and SMMU configuration. No disk persistence exists.

Dependencies and integration: integrates with SoC description files such as `tegra114.c`, `soc/tegra/mc.h`, reset framework, IRQ subsystem, interconnect framework, debugfs, device tree timings selected by RAM code, Tegra fuse RAM code, and optional `CONFIG_TEGRA_IOMMU_SMMU`.

Risks: SoC data must keep client IDs, masks, error status formats, reset bits, and register offsets aligned with silicon. `prevent_deferred_probe` makes missing resources more visible. Error handling for >32-bit addresses requires correct `has_addr_hi_reg` or `mc_addr_hi_mask`. Hotreset waits are bounded and can fail if DMA never idles. Interconnect setup errors are logged but do not fail probe.

Test signals: boot each supported compatible, inject SMMU/page/security errors and verify decoded client/address logs, exercise reset controls for clients, load RAM-code-specific timings and call EMC reconfiguration, validate ICC node registration and sync_state, and test carveout base/size queries.
