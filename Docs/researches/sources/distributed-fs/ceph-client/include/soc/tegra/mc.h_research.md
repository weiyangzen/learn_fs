# sources/distributed-fs/ceph-client/include/soc/tegra/mc.h

## Purpose

`mc.h` defines the Tegra memory-controller and Tegra SMMU integration model: memory clients, timings, reset/hotreset operations, interconnect hooks, error-register layouts, SoC descriptors, and runtime controller state.

## Important APIs, Types, and Functions

`struct tegra_mc_timing` maps a rate to EMEM register data. `struct tegra_mc_client` describes memory-client IDs, BPMP IDs, ICC type, SWGROUP/SID, FIFO size, SMMU enable bits, latency allowance fields, and SID override registers. SMMU support uses `struct tegra_smmu_swgroup`, `struct tegra_smmu_group_soc`, and `struct tegra_smmu_soc`, with optional `tegra_smmu_probe()` and `tegra_smmu_remove()`.

Reset support uses `struct tegra_mc_reset` and `struct tegra_mc_reset_ops`. Interconnect support uses `struct tegra_mc_icc_ops`, `TEGRA_MC_ICC_TAG_DEFAULT`, `TEGRA_MC_ICC_TAG_ISO`, `tegra_mc_icc_xlate()`, and exported `tegra_mc_icc_ops`. `struct tegra_mc_soc` describes SoC-specific clients, timings, address bits, carveouts, SMMU, reset ops, ICC ops, register layouts, interrupts, and masks. `struct tegra_mc` is runtime state with BPMP, device, SMMU, MMIO, clocks, timings, channels, BWMGR support, reset controller, ICC provider, lock, and debugfs root.

Public APIs include `tegra_mc_write_emem_configuration()`, `tegra_mc_get_emem_device_count()`, `devm_tegra_memory_controller_get()`, `tegra_mc_probe_device()`, and `tegra_mc_get_carveout_info()`.

## Control Flow

Probe maps registers, loads SoC descriptors, attaches SMMU and ICC providers, registers reset controls, and installs interrupt handlers. Runtime paths program EMEM timing for rates, translate interconnect nodes, aggregate bandwidth, probe clients, handle faults, and perform hotreset while blocking and unblocking DMA.

## State and Persistence

State persists in MC/SMMU registers, stream-ID overrides, latency allowance, reset bits, ICC aggregate state, timing arrays, and debugfs. `struct tegra_mc.lock` protects shared runtime state.

## Dependencies and Integration Points

The header integrates Linux clocks, reset-controller, debugfs, interrupts, interconnect, Tegra ICC, BPMP, SMMU/IOMMU, device tree phandles, and carveout users.

## Risks

Incorrect client IDs or stream IDs can break DMA isolation. Bad latency allowance or bandwidth aggregation can starve ISO clients. Hotreset without DMA idling can corrupt transfers. SoC-specific interrupt/register layouts must match hardware.

## Test Signals

Test SMMU probe/remove, ICC bandwidth requests with ISO tags, reset/hotreset sequencing, carveout queries, memory-controller fault interrupts, EMEM timing writes, suspend/resume, and disabled-config stubs.
