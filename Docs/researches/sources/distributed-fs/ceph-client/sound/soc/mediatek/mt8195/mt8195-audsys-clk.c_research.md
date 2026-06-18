# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.c

## Purpose
Registers MT8195 audiosys gate clocks backed by AFE MMIO registers so DAPM clock supplies and driver code can use normal Linux clock APIs for audio sub-block power gating.

## Important APIs, Types, and Functions
`mt8195_audsys_clk_register(struct mtk_base_afe *afe)` is the public entry point. `mt8195_audsys_clk_unregister()` is registered as a device-managed cleanup action. `struct afe_gate` describes each gate with clock id, name, parent name, register offset, bit, flags, and gate polarity. `aud_clks[CLK_AUD_NR_CLK]` maps all audio clock ids to gate definitions across `AUDIO_TOP_CON0`, `AUDIO_TOP_CON1`, `AUDIO_TOP_CON3`, `AUDIO_TOP_CON4`, `AUDIO_TOP_CON5`, and `AUDIO_TOP_CON6`.

## Control Flow
Registration allocates `afe_priv->lookup`, then iterates all `aud_clks`, calling `clk_register_gate()` with `CLK_SET_RATE_PARENT` and `CLK_GATE_SET_TO_DISABLE` semantics. For each successfully registered clock it creates a `clk_lookup`, fills `con_id` with the gate name and `dev_id` with the AFE device name, then calls `clkdev_add()`. This lookup path allows `SND_SOC_DAPM_CLOCK_SUPPLY("aud_*")` widgets and `devm_clk_get()` style consumers to find the gates by name.

Cleanup walks the lookup array, obtains each `struct clk` from its lookup, unregisters the gate, and drops the clkdev lookup. The cleanup action is installed with `devm_add_action_or_reset()`, so partial probe failures or driver removal release registered gates.

## State and Persistence
The clock table itself is static. Runtime state is the device-managed `afe_priv->lookup[]` array and each allocated `clk_lookup`. Gate state persists in the audio top registers and is controlled by the common clock framework. No suspend state is kept in this file; higher-level AFE runtime PM and DAPM clock consumers drive enable/disable.

## Dependencies and Integration Points
Depends on Linux CCF (`clk_register_gate`, `clk_unregister_gate`), clkdev lookup support, MT8195 AFE private data, and register constants. Clock ids are defined by `mt8195-audsys-clkid.h`. The ADDA, eTDM, PCM, memif, and machine-driver paths consume these clocks through `afe_priv->clk[]` or DAPM clock supplies such as `aud_dac`, `aud_adc`, `aud_tdm_in`, `aud_i2s_out`, `aud_hdmi_out`, `aud_pcmif`, and memif gates.

## Risks
Failed individual gate registrations only log and continue, which can leave later users with missing clocks and delayed runtime failures. The manually allocated `clk_lookup` uses non-devm allocation but is paired with a devm cleanup action; failures after allocation but before storing can leak if not carefully audited. Gate polarity and parent names must match clock-controller topology and hardware reset values. `aud_clks` length is tied to `CLK_AUD_NR_CLK`; enum/table drift can misindex lookups.

## Test Signals
Build coverage should verify the clock id enum and table size stay aligned. Runtime signals are successful AFE clock initialization, visible clock names under debugfs, DAPM routes enabling/disabling audio gates, eTDM/ADDA/PCM stream startup without missing-clock errors, and clean probe deferral/removal without stale clkdev lookups.
