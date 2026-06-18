# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-device.c

Provides a virtual platform driver that ties selected Tegra clocks to core power-domain performance states. It lets independent PLLs and system clocks raise/lower GENPD performance state as their rates change.

`struct tegra_clk_device` stores the device, target `clk_hw`, notifier block, and mutex. `tegra_clock_set_pd_state()` finds a ceiling OPP for a rate, falls back to floor for unused overly high clocks, obtains required pstate, and calls `dev_pm_genpd_set_performance_state()`. The clock notifier raises pstate before rate increases, restores old pstate on abort, and lowers pstate after rate decreases. Probe gets the clock, initializes OPPs, registers the notifier, and syncs initial pstate. Suspend resumes runtime PM to keep these clocks available during system suspend.

State is the registered notifier and current power-domain performance state. Runtime PM is expected to already be enabled by parent clock infrastructure. The driver stores no persistent rate; it derives it from the clock. It depends on PM domains, PM OPP, runtime PM, Tegra core OPP helpers, and clock notifiers. OF matches include Tegra sclk/pllc/plle/pllm compatibles.

OPP table gaps or missing PM domains fail probe or rate transitions. Notifier error propagation can abort clock changes if pstate cannot be set. Test signals include pstate changes during `clk_set_rate()`, suspend behavior, and boards with unused high-rate clocks taking the floor fallback path.
