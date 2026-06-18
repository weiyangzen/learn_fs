# sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.c

Purpose: implements TI DaVinci Power and Sleep Controller clocks as common-clock gates, optional generic PM domains, and local reset controls.

Important APIs/types/functions: `davinci_lpsc_clk` wraps `clk_hw`, `generic_pm_domain`, a PSC regmap, module-domain ID, power-domain ID, and flags. `davinci_lpsc_config()` sequences MDCTL/PDCTL/PTCMD/EPCPR/PTSTAT/MDSTAT transitions. Registration APIs are `davinci_psc_register_clocks()` and `of_davinci_psc_clk_init()`. Reset ops map OF reset IDs back to LPSC module IDs.

Control flow: probe finds init data from OF match or platform ID, maps the PSC resource, obtains parent clocks in bulk, then calls the platform init callback. Registration creates sparse onecell clock and PM-domain arrays, initializes missing clock entries to `-ENOENT`, registers each LPSC, registers reset control for real devices, then publishes clkdev aliases or OF providers. Enable/disable drives PSC state transitions to ENABLE or DISABLE.

State and persistence: PSC hardware retains module/power states in registers. Software stores allocated clock data, PM domains, and reset controller structures. DT mode records each LPSC as a genpd domain whose attach path adds the LPSC clock to the consumer's pm-clk list.

Dependencies and integration points: depends on regmap-mmio, PM clock/domain frameworks, reset controller framework, clkdev, OF onecell providers, and DA850 init data from `psc-da850.c`.

Risks: `regmap_read_poll_timeout()` calls use zero timeout, so bad hardware state can hang. `clk_hw_register_clkdev()` return is not checked before PM domain setup. Reset xlate assumes the phandle also identifies a clock and casts returned `clk_hw` to an LPSC. Sparse arrays depend on descriptor IDs staying within `num_clks`.

Test signals: test enable/disable/is_enabled transitions, genpd attach/detach power-on behavior, reset assert/deassert for DSP, OF clock lookups for sparse IDs, and probe deferral when parent clocks are unavailable.
