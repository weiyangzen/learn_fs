# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-audio.c

Purpose: platform driver for the MMP2 audio clock controller, exposing the audio PLL plus SYSCLK, SSPA0, and SSPA1 output clocks through a onecell OF provider.

Important APIs/functions: `audio_pll_recalc_rate`, `audio_pll_determine_rate`, and `audio_pll_set_rate` implement the custom PLL `clk_ops` from known pre-divider/post-divider tables. `register_clocks` wires the PLL, muxes, dividers, and gates with `devm_clk_hw_register`. `mmp2_audio_clk_probe`, `mmp2_audio_clk_remove`, and runtime PM callbacks manage resources and saved registers.

Control flow: probe allocates `struct mmp2_audio_clk`, maps MMIO, enables runtime PM and PM clock support, adds the external audio clock, then registers the internal clock tree and `of_clk_add_hw_provider`. Rate changes search the precomputed table for an exact VCO/post-divider match and write `SSPA_AUD_PLL_CTRL0/1`.

State and persistence: MMIO register state is live hardware state. Suspend stores `SSPA_AUD_CTRL` and PLL control registers in the driver private struct; resume restores them after `pm_clk_resume`.

Dependencies and integration: depends on CCF helpers, `pm_clock`, runtime PM, platform resources, and `dt-bindings/clock/marvell,mmp2-audio.h`. Consumers use the three exported clock IDs from device tree.

Risks: unsupported parent rates return zero or rounded rates; `audio_pll_set_rate` only accepts exact table-derived rates. Register restore ordering and PM clock failures can leave audio clocks unusable after suspend. There is a spinlock in the private struct, but the CCF subclocks are not configured to use it.

Test signals: boot on MMP2 audio DT, `clk_summary` showing audio PLL and SSPA clocks, rate round/set tests for 11.2896/12.288 MHz families, suspend/resume audio playback, and module bind/unbind error paths.
