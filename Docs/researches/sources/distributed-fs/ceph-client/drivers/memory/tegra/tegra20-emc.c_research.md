# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20-emc.c

## Purpose
This file implements the Tegra20 External Memory Controller driver. It initializes EMC hardware, loads memory timing tables from device tree, coordinates EMC clock changes with timing-register programming, exposes debugfs rate controls, registers an EMC ICC provider, implements devfreq scaling through OPPs, reads LPDDR2 mode registers for memory identity, and reports refresh-overflow interrupts.

## Important APIs, Types, And Functions
`struct tegra_emc` is the main state container: device, MC pointer, ICC provider, clock notifier, EMC clock, MMIO base, timing table, debugfs limits, rate requests, devfreq governor data, LPDDR2 identity, and MRR error flag. Key functions include `emc_setup_hw()`, `tegra20_emc_find_node_by_ram_code()`, `tegra20_emc_load_timings_from_dt()`, `emc_prepare_timing_change()`, `emc_complete_timing_change()`, `tegra20_emc_clk_change_notify()`, `emc_request_rate()`, `emc_icc_set()`, `tegra20_emc_devfreq_target()`, `tegra20_emc_devfreq_get_dev_status()`, and `tegra20_emc_probe()`.

## Control Flow
Probe maps registers, verifies bootloader-selected DRAM auto-suspend mode, enables EMC/CAR clock-change handshake, configures interrupts/debug defaults, detects DRAM width/type/devices, and reads LPDDR2 JEDEC mode registers where applicable. It selects a timing-table node by RAM code or LPDDR2 identity, loads child timing entries, converts bus kHz to EMC Hz, and sorts them. It requests the IRQ, registers a Tegra clock round-rate callback and clock notifier, initializes OPPs, sets up debugfs, ICC, and devfreq, then pins the module loaded. Rate changes enter through devfreq, debugfs, or ICC; all converge on `emc_request_rate()` under `rate_lock`, which combines min/max constraints and calls `dev_pm_opp_set_rate()`. Clock notifier PRE writes timing shadow registers; POST waits for CAR handshake; ABORT restores old timing and forces update.

## State And Persistence
The driver persists timing data in devm memory, current min/max requests in `requested_rate[]`, debugfs limits, measured DRAM identity, and counters/timers managed by devfreq. Hardware state includes EMC timing registers, power/statistics counters, interrupt masks/status, MRR state, and clock rate. Timing tables are not persisted by the driver; they come from device tree each boot. `mrr_error` suppresses RAM-code timing selection if mode-register reads fail.

## Dependencies And Integration Points
It integrates with the Tegra clock driver via `tegra20_clk_set_emc_round_callback()` and clock notifiers, the OPP framework for voltage-aware rate changes, devfreq simple_ondemand, the interconnect framework, the common Tegra MC provider via `devm_tegra_memory_controller_get()`, JEDEC LPDDR2 helpers, and device tree timing nodes compatible with `nvidia,tegra20-emc-table`. ICC receives EMEM bandwidth votes and converts peak/average bytes per second to an EMC clock floor using detected DRAM bus width.

## Risks
Clock/timing ordering is sensitive: incorrect timing tables or notifier failures can destabilize memory. Timing lookup picks the first table with rate greater than or equal to the target, so table sorting and full rate coverage are essential. `emc_request_rate()` applies OPP rate to the aggregate minimum, not directly to the requested rate, so conflicting debug/devfreq/ICC min/max values can return `-ERANGE`. MRR timeouts mark `mrr_error` and skip memory-timing selection. Devfreq statistics depend on counter semantics and a low threshold. Probe ignores return values from ICC/devfreq init, so failures may be non-fatal but reduce functionality.

## Test Signals
Hardware validation should include boot with valid and missing timing tables, RAM-code matching, LPDDR2 identity matching, debugfs available/min/max rates, devfreq transitions, ICC bandwidth votes, suspend-like clock changes with abort paths, and refresh-overflow IRQ logging. OPP tests should confirm voltage changes precede higher EMC rates. Stress tests should run display/video/storage DMA while changing rates and should monitor MC/EMC error logs for decode, refresh, or timing failures.
