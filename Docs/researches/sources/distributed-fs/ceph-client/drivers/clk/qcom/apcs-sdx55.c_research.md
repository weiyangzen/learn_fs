# sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-sdx55.c

## Purpose
`apcs-sdx55.c` registers the SDX55 APCS CPU mux/divider clock and attaches the CPU device to its PM domain. Like MSM8916, it provides a safe temporary CPU clock path while the A7 PLL is reconfigured.

## Important APIs, Types, And Functions
The key functions are `a7cc_notifier_cb()`, `qcom_apcs_sdx55_clk_probe()`, and `qcom_apcs_sdx55_clk_remove()`. It uses `struct clk_regmap_mux_div`, `mux_div_set_src_div()`, `clk_notifier_register()`, `devm_clk_register_regmap()`, `dev_pm_domain_attach()`, `dev_pm_domain_detach()`, and `get_cpu_device(0)`.

## Control Flow, State, And Persistence
Probe obtains the parent regmap, allocates and initializes `a7mux` at register offset `0x8`, gets the `pll` clock from the parent, registers a notifier that switches to aux/divider safe configuration on `PRE_RATE_CHANGE`, registers and publishes the mux, stores driver data, and attaches CPU0 to its power domain with power-on semantics. Errors after notifier registration unwind by unregistering it. Remove unregisters the notifier and detaches the CPU PM domain.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APCS IPC/regmap parent, `ref`, `aux`, and `pll` clocks, CCF notifiers, qcom mux-div helpers, generic PM domains, and CPU device registration. Risks include a driver-name typo (`acps`), CPU0 device or PM-domain absence, notifier lifetime across partial probe failures, and safe mux values that are hardware-specific. Test signals include SDX55/SDX65 CPUfreq transitions, PM domain attachment in boot logs, PLL rate-change notifier activity, clean module unload, and correct `a7mux` parent/rate under debugfs.
