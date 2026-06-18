# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cbf-8996.c

## Purpose
Provides the MSM8996 CPU bus fabric (CBF) clock driver. It configures a Huayra APSS alpha PLL, a fixed post-divider, and a small mux used as the exported CBF clock. When interconnect support is enabled, it also registers the CBF clock as an interconnect-backed bandwidth provider.

## Important APIs, Types, And Functions
Important objects are `cbfpll_config`, `cbf_pll`, `cbf_pll_postdiv`, `cbf_mux_parent_data`, `struct clk_cbf_8996_mux`, and `cbf_mux`. CCF callbacks are `clk_cbf_8996_mux_get_parent()`, `clk_cbf_8996_mux_set_parent()`, and `clk_cbf_8996_mux_determine_rate()`. Platform lifecycle functions include `qcom_msm8996_cbf_probe()`, remove, init, and exit. Interconnect hooks are `qcom_msm8996_cbf_icc_register()` and remove/sync-state shims.

## Control Flow
Probe maps the MMIO resource, initializes regmap, temporarily selects GPLL0, programs always-on auto clock selection, configures the CBF PLL, enables auto clock selection, switches the mux to the primary PLL, adjusts post-divider behavior for MSM8996 Pro, registers the fixed factor clock and regmap clocks, installs a notifier, exports the mux as the OF clock provider, and optionally registers the interconnect clock provider. The notifier switches to PLL/2 before downward crossings below 600 MHz and reverts on abort.

## State And Persistence
Persistent hardware state is the CBF mux register, auto-clock-select bits, PLL registers, and post-divider selection. Static software descriptors are global because the driver only supports the matching platform instance. Interconnect provider state is stored in platform driver data when `CONFIG_INTERCONNECT` is enabled.

## Dependencies And Integration Points
Depends on alpha PLL ops, regmap clock registration, platform device APIs, DT compatible strings `qcom,msm8996-cbf` and `qcom,msm8996pro-cbf`, CCF notifiers, optional interconnect clock provider APIs, and `dt-bindings/interconnect/qcom,msm8996-cbf.h`.

## Risks And Edge Cases
CBF is marked critical and initialized at `postcore_initcall` because CPU fabric rate changes are early and safety-sensitive. Incorrect threshold handling can overclock the mux during PLL reprogramming. The Pro variant mutates global config/divider values after initial PLL configuration in probe, so ordering matters. Without interconnect support, the driver warns that CBF is fixed.

## Test Signals
Boot on MSM8996 and MSM8996 Pro, OF clock provider resolution, CBF rate changes across 600 MHz, notifier abort behavior, interconnect bandwidth requests changing CBF rate, and no CPU fabric hang during PLL changes are key signals.
