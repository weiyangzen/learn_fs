# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-aud.c

## Purpose

This MT7622 audio clock driver registers audsys gates and populates child platform devices below the audio node. It covers AFE, HDMI/SPDIF/APLL, I2S input/output, ASRC, A1/A2 system, memory ASRC, and playback/capture data-path gates.

## Important APIs, types, and functions

Data includes four gate-register banks `audio0_cg_regs` through `audio3_cg_regs`, `audio_clks[]`, and `audio_desc`. The custom `clk_mt7622_aud_probe()` wraps `mtk_clk_simple_probe()` and then calls `devm_of_platform_populate()`. Remove depopulates children and calls `mtk_clk_simple_remove()`.

## Control flow, state, and persistence

Probe first registers the clock provider from `audio_desc`. If child population fails, it removes the clocks. Gate operations use no-setclr registers, with offsets `0x0`, `0x10`, `0x14`, and `0x634`. State is clock-provider registration, child platform-device population, and hardware gate bits.

## Dependencies and integration points

Dependencies include OF platform helpers, `clk-mtk.h`, `clk-gate.h`, and MT7622 bindings. Parent clocks include `rtc`, `apll1_ck_sel`, `a1sys_hp_sel`, `a2sys_hp_sel`, `asm_h_sel`, `intdir_sel`, and `aud_mux1_sel`. It integrates with ASoC and audio front-end child devices.

## Risks and test signals

Risks include no-setclr polarity errors, child-device ordering problems, and audio-parent mismatches. Test ASoC probe, I2S playback/capture, SPDIF/HDMI audio, ASRC use, child device population, and runtime PM gate transitions.
