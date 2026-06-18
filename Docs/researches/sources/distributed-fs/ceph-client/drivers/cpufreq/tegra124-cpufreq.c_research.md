# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra124-cpufreq.c

Purpose: prepares Tegra114/Tegra124/Tegra210 CPU clocking for generic `cpufreq-dt` by switching the CPU clock source to DFLL and handling suspend/resume clock parent transitions.

Important APIs and functions: probe obtains CPU0 OF node, CPU device, and clocks named `cpu_g`, `dfll`, `pll_x`, and `pll_p`. `tegra124_cpu_switch_to_dfll()` aligns DFLL rate with the current CPU clock, temporarily reparents CPU to PLLP, enables DFLL, then reparents CPU to DFLL. `tegra124_cpufreq_suspend()` reparents CPU to safe PLLP and disables DFLL; resume reenables DFLL and reparents back, calling `disable_cpufreq()` on failure. Successful probe registers `cpufreq-dt` via `cpufreq_dt_pdev_register()`.

Control flow and state: a private devm-allocated struct holds clock handles and the `cpufreq-dt` platform device. Module init gates by Tegra machine compatible, registers a platform driver, then creates a synthetic platform device to allow probe deferral.

Dependencies and integration points: depends on CCF clocks named in CPU0 DT, DFLL/regulator readiness, OPP data consumed by `cpufreq-dt`, system sleep PM ops, and the local `cpufreq-dt.h` helper.

Risks and test signals: risks include manual `clk_put()` handling despite devm allocation of the container, unused `pllx_clk` except for lifetime acquisition, no rollback from successful DFLL switch if `cpufreq-dt` registration fails, and resume disabling cpufreq globally on DFLL reparent failure. Test signals include clock lookup deferral, CPU parent switching sequence observable in clk debugfs, cpufreq-dt registration, suspend using PLLP 408 MHz, and resume restoring DFLL without frequency loss.
