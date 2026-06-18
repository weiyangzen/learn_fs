# sources/distributed-fs/ceph-client/drivers/clk/meson/meson8b.c

## Purpose
Defines the early clock and reset controller for Amlogic Meson8, Meson8b, and Meson8m2 SoCs. It publishes a large HHI clock tree through `CLK_OF_DECLARE_DRIVER` rather than a normal platform driver, including fixed/system/video/HDMI/GPU/VPU/VDEC/audio/peripheral clocks, CPU clock switching support, SoC-specific clock ID arrays, and reset-controller lines in clock registers.

## Important APIs, Types, And Functions
The file declares many `struct clk_regmap`, `struct clk_fixed_factor`, PLL parameter tables, init register sequences, parent arrays, and sparse `clk_hw` ID arrays: `meson8_hw_clks`, `meson8b_hw_clks`, and `meson8m2_hw_clks`. Key reset types are `struct meson8b_clk_reset` and `meson8b_clk_reset_bits`; operations are `meson8b_clk_reset_update()`, `meson8b_clk_reset_assert()`, and `meson8b_clk_reset_deassert()`. CPU rate-change handling uses `struct meson8b_nb_data` and `meson8b_cpu_clk_notifier_cb()`. `meson8b_clkc_init_common()` performs syscon lookup, reset-controller registration, clock registration, notifier setup, and OF provider registration.

## Control Flow
During early OF clock initialization, the compatible-specific wrapper chooses the Meson8, Meson8b, or Meson8m2 clock array and calls common init. Common init obtains the parent HHI syscon regmap, allocates reset state, registers the reset controller, iterates non-null clocks starting at `CLKID_PLL_FIXED`, registers each with `of_clk_hw_register()`, registers a notifier on `cpu_scale_out_sel`, then installs the provider callback. During CPU rate changes, the notifier switches `cpu_clk` to xtal before the rate change and back to `cpu_scale_out_sel` afterward, with a short delay.

## State And Persistence
Clock and reset state is stored in HHI syscon registers. The code programs clocks through regmap ops and reset lines through `regmap_update_bits()`. Early init uses `kzalloc_obj()` rather than devm allocation, so state persists for the lifetime of the booted kernel. PLL init sequences for HDMI and Meson8m2 GP PLL write hardware defaults through the underlying PLL ops. CPU notifier state is global in `meson8b_cpu_nb_data`.

## Dependencies And Integration Points
Depends on CCF, early OF clock declarations, syscon/regmap, reset-controller framework, local Meson clk-regmap/PLL/MPLL utilities, and binding headers for clock and reset IDs. Integrates with cpufreq/CPU clock consumers, display pipelines, HDMI/LVDS, GPU, VPU, VDEC, NAND, audio AIU/IEC958, peripheral bus gates, AO gates, and reset consumers. The parent syscon node must be present.

## Risks And Edge Cases
This is high-risk table-driven code. ID arrays differ among Meson8, Meson8b, and Meson8m2; Meson8 lacks glitch-free Mali/VPU second paths exposed by later variants, while Meson8m2 adds GP PLL and different VPU parents. The CPU notifier is a workaround for safe rate switching and can destabilize systems if parent ordering changes. Some parent values are skipped due to unstable duty cycle or unknown documentation. Reset lines include both active-high and active-low bits, so polarity errors can hold hardware in reset. Early-init allocation and registration have limited cleanup on partial failure.

## Test Signals
Boot all three compatibles and verify early console, CPU frequency transitions, clk debugfs topology, reset-controller phandles, HDMI/display clocks, GPU/VPU rate changes, VDEC decode clocks, audio clocks, and NAND/peripheral consumers. Static validation should compare all three clock arrays with `dt-bindings/clock/meson8b-clkc.h` and reset bits with `amlogic,meson8b-clkc-reset.h`. CPU stress plus cpufreq transitions is the best signal for the notifier path.
