# sources/distributed-fs/ceph-client/drivers/hte/hte-tegra194.c

## Purpose
Implements the NVIDIA Tegra Generic/Hardware Timestamping Engine provider for AON GPIO and LIC interrupt sources across Tegra194, Tegra234, and Tegra264 variants.

## Important APIs, Types, and Functions
- SoC data: `struct tegra_hte_data` captures provider type, slice count, mapping tables, and timestamp clock rate.
- Runtime state: `struct tegra_hte_soc`, `struct hte_slices`, and `struct tegra_hte_line_data`.
- HTE provider ops: `tegra_hte_request()`, `tegra_hte_release()`, `tegra_hte_enable()`, `tegra_hte_disable()`, and `tegra_hte_clk_src_info()`.
- Translation: `tegra_hte_line_xlate()`, `tegra_hte_line_xlate_plat()`, and `tegra_hte_match_from_linedata()`.
- IRQ/FIFO path: `tegra_hte_isr()` and `tegra_hte_read_fifo()`.

## Control Flow
Probe selects SoC data from OF, reads optional slice and interrupt-threshold properties, maps registers, requests the provider IRQ, fills an `hte_chip`, resolves GPIO controller linkage for GPIO providers, registers with the HTE core, initializes slice locks, and enables the hardware with interrupt threshold. Consumers request lines through HTE core translation. GPIO requests enable hardware timestamping on the GPIO descriptor and then set the corresponding slice enable bit. On IRQ, the driver drains FIFO entries, reconstructs the timestamp counter, reads source slice and previous/current vectors, computes changed bits, converts each bit to a line ID, fills `hte_ts_data`, and calls `hte_push_ts_ns()`.

## State and Persistence
State includes mapped registers, slice enable shadow values for suspend, suspend flags per slice, GPIO line data, threshold, and clock-rate metadata. Suspend saves control and slice enable registers and marks slices suspended; resume restores control and enables. No persistent storage.

## Dependencies and Integration Points
Depends on HTE provider APIs, GPIO descriptor/device APIs, platform resources, OF compatible data, IRQ handling, MMIO, and Tegra-specific line maps. GPIO consumers can bind by DT phandle or platform line data.

## Risks and Test Signals
Risks include off-by-one bounds checks (`> nlines` versus `>= nlines` patterns), invalid GPIO map entries, FIFO drain under heavy event rates, suspend blocking enable/disable, GPIO controller lookup differences for Tegra194 versus later SoCs, and raw-level reads racing line release. Test signals include successful provider registration for each compatible, timestamp callbacks from GPIO and LIC sources, clock source info correctness, suspend/resume preserving enabled lines, and dropped timestamp counters remaining low.
