# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186-emc.c

## Purpose
This file implements the Tegra186-family External Memory Controller platform driver used on Tegra186, Tegra194, Tegra234, and Tegra264 compatibles. It acquires BPMP and EMC clocks, optionally queries BPMP for EMC DVFS latency pairs, exposes debugfs rate controls, and registers an EMC-side interconnect provider that bridges MC bandwidth requests to the external memory node.

## Important APIs, Types, And Functions
`struct tegra186_emc` stores the BPMP handle, device, EMC and DBB clocks, DVFS table, debugfs limits, and ICC provider. `tegra186_emc_get_emc_dvfs_latency()` sends `MRQ_EMC_DVFS_LATENCY` through BPMP, converts firmware frequencies from kHz to Hz, computes min/max rates, sets the clock rate range, and creates debugfs files. `tegra186_emc_interconnect_init()` creates `TEGRA_ICC_EMC` and `TEGRA_ICC_EMEM` nodes, links EMC to EMEM, and registers the provider. Probe/remove are `tegra186_emc_probe()` and `tegra186_emc_remove()`.

## Control Flow
Probe allocates `tegra186_emc`, gets BPMP, gets the `emc` clock, optionally enables the `dbb` clock, stores driver data, and queries DVFS latency if BPMP advertises that MRQ. If the parent MC exists and has ICC ops, probe checks `MRQ_BWMGR_INT`; when supported, it marks `mc->bwmgr_mrq_supported`, stores the BPMP pointer in `mc->bpmp`, and uses a barrier before registering the EMC ICC provider. ICC registration happens even without BWMGR support so client paths exist, but later MC set hooks can fail cleanly. Remove deletes debugfs, clears `mc->bpmp`, and releases BPMP.

## State And Persistence
Persistent runtime state is held in `struct tegra186_emc` and in the parent `struct tegra_mc`: debugfs min/max reflect the last successfully applied limits, `dvfs` stores firmware-provided rates until device removal, `mc->bpmp` is borrowed from the EMC node for MC bandwidth requests, and `mc->bwmgr_mrq_supported` captures firmware capability. No state is saved across reboot; suspend behavior is delegated to clocks/firmware and there are no explicit PM callbacks here.

## Dependencies And Integration Points
The driver integrates with BPMP (`tegra_bpmp_get()`, `tegra_bpmp_transfer()`, `tegra_bpmp_mrq_is_supported()`), the Linux clock API, debugfs, of-platform child population under the parent MC, and the interconnect framework. It expects the parent device's driver data to be a `struct tegra_mc`. Its ICC aggregate callback is taken from `mc->soc->icc_ops`, while EMC `set` intentionally does nothing because BPMP bandwidth programming is performed by the MC provider for newer chips.

## Risks
The BPMP pointer sharing into `mc->bpmp` is a lifecycle-sensitive integration point; remove clears it, but concurrent ICC users depend on normal device lifetime ordering. Debugfs rate setters only accept exact DVFS rates, so firmware table changes directly affect user-visible control. If `MRQ_EMC_DVFS_LATENCY` returns zero pairs, min/max initialization would produce unusable rate limits. `tegra186_emc_interconnect_init()` removes nodes on failure but remove does not explicitly unregister the ICC provider, relying on provider/device lifetime conventions. Missing or wrong parent MC data can disable ICC setup or cause null assumptions in remove.

## Test Signals
Probe logs should show successful BPMP and clock acquisition, debugfs `/sys/kernel/debug/emc/available_rates` should list firmware rates, and min/max writes should reject invalid values and apply valid ones through `clk_set_min_rate()`/`clk_set_max_rate()`. ICC tests should verify EMC/EMEM nodes register even when `MRQ_BWMGR_INT` is unsupported, and MC bandwidth requests fail or pass according to firmware capability. Device removal or bind failure paths should be checked for BPMP release and debugfs cleanup.
