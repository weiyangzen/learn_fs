# sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8916.c

## Purpose
`apcs-msm8916.c` registers the MSM8916 APCS CPU mux/divider clock. It selects between an auxiliary GPLL0-derived parent and the A53 PLL, and uses a notifier to move the CPU clock to a safe 400 MHz configuration before PLL rate changes.

## Important APIs, Types, And Functions
Important pieces are `struct clk_regmap_mux_div`, `gpll0_a53cc_map`, `pdata`, `a53cc_notifier_cb()`, `qcom_apcs_msm8916_clk_probe()`, and `qcom_apcs_msm8916_clk_remove()`. The clock uses `clk_regmap_mux_div_ops`, `mux_div_set_src_div()`, `clk_notifier_register()`, and `devm_of_clk_add_hw_provider()`.

## Control Flow, State, And Persistence
Probe obtains the parent regmap from the APCS IPC parent device, allocates the mux/divider, names it uniquely using the parent's unit address, programs register layout at offset `0x50`, gets the parent PLL clock, registers a PLL notifier, registers the regmap clock, and publishes it to DT. On `PRE_RATE_CHANGE`, the notifier selects source 4 and divider 3 as a safe temporary rate. Remove unregisters the notifier. State is hardware-backed in the APCS mux/divider register and notifier membership.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include a parent APCS regmap device, `aux`/`gpll0_vote` and `pll`/`a53pll` clocks, qcom mux-div helpers, common clock notifiers, and DT clock consumers for CPUfreq. Risks include CPU instability if the safe source/divider is wrong, notifier cleanup only after successful registration, probe deferral for the PLL parent, and fragile parent-name fallback. Test signals include CPUfreq PLL changes, notifier execution before PLL changes, clock provider availability, removal/unbind notifier cleanup, and boot logs without failed regmap or parent clock acquisition.
