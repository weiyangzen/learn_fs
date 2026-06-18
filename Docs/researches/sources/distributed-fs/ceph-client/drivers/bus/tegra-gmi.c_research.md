# sources/distributed-fs/ceph-client/drivers/bus/tegra-gmi.c

## Purpose
This driver configures the NVIDIA Tegra20/Tegra30 Generic Memory Interface for an external child device, usually SNOR-like parallel memory, including chip-select selection, timing registers, reset sequencing, runtime PM clock control, and child population.

## Important APIs, Types, and Functions
`struct tegra_gmi` stores MMIO base, clock, reset, and computed SNOR config/timing register values. `tegra_gmi_parse_dt()` reads one child node’s SNOR flags, chip-select from `ranges` or `reg`, and timing properties. `tegra_gmi_enable()` enables runtime PM, resets the block, writes timing/config registers, and sets `TEGRA_GMI_CONFIG_GO`. `tegra_gmi_disable()` clears GO, asserts reset, and suspends PM. Probe maps resources, gets clock/reset, initializes OPP data, parses DT, enables the controller, and populates children.

## Control Flow
Only one child is effectively supported; additional children trigger a warning. Probe computes register values before enabling hardware. If child population fails after enabling, it disables GMI. Runtime PM callbacks only gate the GMI clock; enable/disable perform the reset and programming sequence.

## State and Persistence
Computed config/timing values persist in `struct tegra_gmi` and are programmed to hardware during enable. Hardware state is lost across reset/power loss and restored only through the explicit enable path.

## Dependencies and Integration Points
It depends on OF parsing, platform MMIO, CCF clocks, reset control, runtime PM, and `devm_tegra_core_dev_init_opp_table_common()`. It integrates with the single external-memory child populated below the GMI node.

## Risks and Test Signals
Risks include limited multi-child support, chip-select decoding fallback ambiguity, no full register reprogramming in runtime resume after deep loss, and timing property truncation by bit masks without validation. Test signals include correct CS/timing register values, external memory access after probe, failure unwinding after child population errors, and runtime PM clock balance.
