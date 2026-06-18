# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpassaudiocc-sc7280.c

## Purpose

This is the SC7280/QCM6490 LPASS audio/AON clock-controller driver. It registers LPASS Q6 bus clocks, AUDIO CC clocks, AON CC clocks, audio PLLs, audio memory and MCLK branches, an audio HM GDSC, and SoundWire reset lines.

## Important APIs, types, and functions

Important objects include Zonda `lpass_audio_cc_pll` at 1128.96 MHz, Lucid `lpass_aon_cc_pll` at 614.4 MHz, postdivs, read-only dividers, AON main/TX RCGs, audio EXT MCLK/RX MCLK RCGs, codec memory branches, TX/RX MCLK branches, Q6 AHBM/AHBS branches, `lpass_aon_cc_lpass_audio_hm_gdsc`, reset maps, and three descriptors: `lpass_cc_sc7280_desc`, `lpass_audio_cc_sc7280_desc`, and `lpass_aon_cc_sc7280_desc`. Probe helpers include `lpass_audio_setup_runtime_pm()`, `lpass_audio_cc_sc7280_probe()`, and `lpass_aon_cc_sc7280_probe()`.

## Control flow, state, and persistence

Runtime PM setup uses autosuspend and an `"iface"` PM clock. AUDIOCC probe either registers only QCM6490 reset controls by index 1, or maps the AUDIO CC, configures the Zonda PLL, writes PLL setup registers `0x4` and `0x8`, registers clocks, then registers reset controls by index 1. AONCC probe either registers LPASS Q6 clocks in ADSP PIL mode or maps AONCC, configures the Lucid PLL, and registers AON clocks/GDSC. State is PLL programming, RCG/divider/branch registers, reset bits, and genpd state.

## Dependencies and integration points

It depends on SC7280 LPASS and LPASSAUDIOCC bindings, runtime PM, PM clocks, Qualcomm alpha PLL/RCG/branch/GDSC/reset helpers, and LPASS audio, codec, SoundWire, ADSP, and power-domain consumers.

## Risks and test signals

Risks include dual-compatible behavior, index-based resource mapping, ADSP PIL mode changing which clocks are registered, reset-only QCM6490 handling, and audio-rate table coverage for 44.1 kHz and 48 kHz families. Test by probing SC7280 and QCM6490 DTs, checking AON/AUDIO PLL rates, setting TX/RX/EXT MCLK rates, validating codec memory clocks and the HM GDSC, toggling SoundWire resets, and running audio playback/capture across runtime suspend.
