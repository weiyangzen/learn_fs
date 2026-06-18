# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30-emc.c

Purpose: This is the Tegra30 External Memory Controller platform driver. It loads EMC timing tables from device tree, coordinates safe DRAM timing changes during EMC clock transitions, exposes debugfs rate controls, provides an ICC provider for memory bandwidth requests, handles refresh-overflow interrupts, and participates in suspend/resume.

Important APIs/types/functions: `struct emc_timing` stores one frequency's EMC register data and mode/calibration fields. `struct tegra_emc` owns registers, IRQ, clock notifier, MC handle, timing state, debugfs limits, ICC provider, rate requests, and bad-state tracking. Key functions are `emc_prepare_timing_change()`, `emc_complete_timing_change()`, `emc_clk_change_notify()`, `emc_load_timings_from_dt()`, `emc_setup_hw()`, `emc_round_rate()`, `emc_request_rate()`, debugfs get/set handlers, `emc_icc_set()`, `tegra30_emc_interconnect_init()`, `tegra30_emc_init_clk()`, probe, suspend, and resume.

Control flow: Probe maps registers, gets the shared MC, configures hardware handshake/interrupt/debug state, optionally loads RAM-code-specific timings from DT, registers IRQ and clock notifier, initializes OPP/rate requests/debugfs, and registers ICC nodes. PRE_RATE_CHANGE disables the IRQ and programs shadow/timing/MC values, POST waits for clock-change completion and restores refresh/calibration/self-refresh settings, and ABORT marks unrecoverable state. ICC and debugfs requests converge on `dev_pm_opp_set_rate()`.

State and persistence: State is runtime only: timing arrays, current mode registers, debugfs min/max, requested min/max by source, `bad_state`, MRR errors, and hardware registers. DT timing data is read but not modified. Suspend takes exclusive clock-rate control and refuses a bad state; resume reinitializes hardware.

Dependencies and integration: Depends on Tegra clock callbacks, OPP, ICC, debugfs, shared Tegra MC, `of_memory`, JEDEC LPDDR helpers, and Tegra fuses for RAM code. It is a platform driver for `nvidia,tegra30-emc`.

Risks and test signals: Risks are high because incorrect ordering can hang memory. Test signals include boot with and without DT timings, repeated OPP rate changes under memory load, valid LPDDR MRR reads, refresh-overflow interrupt logging, debugfs min/max behavior, ICC bandwidth scaling, and suspend/resume without `bad_state` warnings.
