# sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb.c

## Purpose
Describes the main EE-domain clock controller for Amlogic GXBB and GXL SoCs. The file publishes the clock tree behind `amlogic,gxbb-clkc` and `amlogic,gxl-clkc`: fixed, system, HDMI, GP0, fractional, MPLL, clk81, audio, MMC/NAND, GPU, VPU/VAPB, video encoder, HDMI, decoder, generic, AO, AIU, and large peripheral gate sets. It is data-heavy driver code whose correctness depends on register offsets, bit positions, parent topology, and DT clock ID alignment.

## Important APIs, Types, And Functions
Most declarations are static `struct clk_regmap`, `struct clk_fixed_factor`, `struct pll_params_table`, `struct reg_sequence`, and parent arrays. Important helpers and ops include `meson_clk_pll_ops`, `meson_clk_pll_ro_ops`, `meson_clk_mpll_ops`, `meson_vid_pll_div_ro_ops`, `clk_regmap_gate_ops`, `clk_regmap_mux_ops`, and divider variants. `GXBB_PCLK` and `GXBB_AIU_PCLK` generate many gate clocks through `MESON_PCLK`. `gxbb_hw_clks` and `gxl_hw_clks` expose sparse ID-to-clock maps from `dt-bindings/clock/gxbb-clkc.h`. `gxbb_clkc_data` and `gxl_clkc_data` are passed to `meson_clkc_syscon_probe` by the platform driver.

## Control Flow
At platform probe, OF matching chooses GXBB or GXL data. `meson_clkc_syscon_probe` obtains the parent syscon regmap and registers each non-null `clk_hw` in the selected array, then installs the OF clock provider. Rate changes are delegated to CCF ops supplied by the individual clock nodes. Some paths use parent name fallbacks, for example `gp0_pll`, `mpll0`, and `vid_pll_div`, so one common downstream node can bind to GXBB- or GXL-specific upstream hardware.

## State And Persistence
Hardware state lives in HHI registers in the parent syscon region. PLL lock, enable, reset, fractional, mux, divider, and gate bits persist in those registers and may also be touched by display firmware or drivers. Several video clocks carry `CLK_GET_RATE_NOCACHE` because HDMI/display code directly programs PLL registers outside this provider. Critical and ignored-unused clocks preserve boot-critical state for clk81, fclk dividers, video, VPU/VAPB, and historical peripheral gates.

## Dependencies And Integration Points
Depends on Linux CCF, platform-driver OF matching, Meson regmap clock helpers, PLL/MPLL/video-divider helpers, and clock binding IDs. It integrates with DTS clock provider nodes, display/HDMI, DRM/VPU/VAPB, MMC/NAND, SAR ADC, audio AIU and IEC958, USB, Ethernet, UART, reset-controller consumers, RNG, and video decoder drivers. Parent firmware names include `xtal`, while many internal parents are direct `clk_hw` links.

## Risks And Edge Cases
The highest risks are sparse array ID drift, SoC-specific differences sharing common names, and undocumented parent choices. GXL differs in HDMI PLL divider locations, GP0 parameters/init registers, and MPLL0 SDM enable placement. The file deliberately avoids using precious MPLL/GP0 parents for some MMC/NAND and GPU choices. Many gates use `CLK_IGNORE_UNUSED` for historical reasons, which can hide unmodelled dependencies but prevents regressions on boards whose consumers are incomplete. Video clocks using no-cache indicate possible races or stale rates if direct register writers are not coordinated.

## Test Signals
Useful signals are successful module build and probe on `amlogic,gxbb-clkc` and `amlogic,gxl-clkc`, complete `/sys/kernel/debug/clk/clk_summary` coverage for binding IDs, stable HDMI/display modes, working MMC/NAND clock rates, audio playback with MPLL-derived rates, GPU/VPU rate changes, and boot without disabling critical fclk/clk81 paths. Static checks should compare `gxbb_hw_clks` and `gxl_hw_clks` against `include/dt-bindings/clock/gxbb-clkc.h`.
