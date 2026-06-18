# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8mp-audiomix.c

## Purpose
This platform driver exposes the i.MX8MP Audio BLK_CTRL clock and reset-facing registers. It registers audio block gates, SAI MCLK selectors, PDM selector, an audio SAI PLL, its bypass/output/div2 clocks, optional auxiliary reset controller, and runtime PM save/restore for the audio block registers.

## Important APIs, Types, And Functions
`struct clk_imx8mp_audiomix_sel` models either a gate with one parent or a mux with parent data. `struct clk_imx8mp_audiomix_priv` stores the MMIO base, saved register values, and trailing onecell clock data. Macros `CLK_GATE`, `CLK_GATE_PARENT`, `CLK_PDM`, and `CLK_SAIn()` generate the table entries for gates and SAI MCLK mux/gate groups. `clk_imx8mp_audiomix_probe()` allocates `priv`, maps registers, enables runtime PM before registering clocks, iterates `sels[]`, registers the SAI PLL path, publishes the provider, and creates an auxiliary reset device if `#reset-cells` is present. Runtime suspend/resume call `clk_imx8mp_audiomix_save_restore()`.

## Control Flow
Probe makes the block active with `pm_runtime_get_noresume()`, `pm_runtime_set_active()`, and `pm_runtime_enable()` so clock registration can safely access runtime-PM-aware parents. It registers each table entry as either `devm_clk_hw_register_gate_parent_data()` or `devm_clk_hw_register_mux_parent_data_table()`. It then registers `sai_pll_ref_sel`, the PLL14xx `sai_pll`, `sai_pll_bypass`, `sai_pll_out`, and fixed-factor `sai_pll_out_div2`, publishes `of_clk_hw_onecell_get`, optionally registers reset support, and drops the runtime PM reference. Error paths disable runtime PM.

## State And Persistence
The driver saves `CLKEN0/1`, EARC, SAI MCLK selectors, PDM selector, SAI PLL registers, and `IPG_LP_CTRL` into `regs_save[]` during runtime suspend and restores them on resume. The onecell data is embedded in the private allocation for driver lifetime. Gate state is hardware-backed in Audio BLK_CTRL registers. Reset support is delegated to an auxiliary device.

## Dependencies And Integration Points
Dependencies include `dt-bindings/clock/imx8mp-clock.h`, compatible `fsl,imx8mp-audio-blk-ctrl`, parent clocks from the main CCM and audio sources (`ahb`, `axi`, `sai*`, `sai*_mclk`, `pdm`, `spdif_extclk`, `osc_24m`), PLL14xx support, runtime PM, optional reset-controller support through the auxiliary bus, and OF clock provider registration. Audio, DSP, SDMA/eDMA, EARC, PDM, SAI, and MQS users consume these clocks.

## Risks And Test Signals
Risks include registering clocks before runtime PM is active, wrong table-generated register bit positions, incomplete save/restore across low-power audio suspend, optional reset-controller mismatch, and parent-name mismatches between main CCM and audiomix. Test signals include probe on `fsl,imx8mp-audio-blk-ctrl`, clock summary entries for SAI/PDM/PLL gates, audio playback/capture across SAI1/2/3/5/6/7, PDM and EARC operation, runtime suspend/resume preserving muxes and PLL settings, and reset auxiliary device creation when `#reset-cells` is present.
