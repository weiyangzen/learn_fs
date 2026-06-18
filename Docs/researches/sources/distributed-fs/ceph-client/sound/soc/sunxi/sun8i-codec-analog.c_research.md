# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec-analog.c

## Purpose
This ASoC component driver models the analog half of several Allwinner internal codecs. It provides mixer, amplifier, bias, headphone, line-in, line-out, and microphone DAPM widgets and controls for A23, H3, and V3s-style analog blocks. It complements the separate digital codec driver, which supplies stream-facing DAI widgets.

## Important APIs, types, and functions
The file defines analog register offsets and bit fields for HP volume, mixers, DAC/PA source control, line/mic gains, bias, ADC enable, and output enables. Feature-specific helper functions add controls/widgets/routes: `sun8i_codec_add_headphone()`, `sun8i_codec_add_mbias()`, `sun8i_codec_add_hmic()`, `sun8i_codec_add_linein()`, `sun8i_codec_add_lineout()`, and `sun8i_codec_add_mic2()`. `struct sun8i_codec_analog_quirks` selects which blocks exist per compatible. `sun8i_codec_analog_cmpnt_probe()` builds the component's dynamic DAPM topology based on quirks. `sun8i_codec_analog_probe()` maps MMIO, creates the ADDA PR regmap, and registers the component.

## Control flow
Component registration installs common Mic1/ADC/DAC controls and widgets. At component probe, the driver obtains match data, adds a generic mixer topology or a V3s-limited topology when neither MIC2 nor line-in exists, then conditionally adds headphone, HMIC bias, line-in, line-out, MBIAS, and MIC2 blocks. Headphone amplifier power-up is intercepted by `sun8i_headphone_amp_event()`, which enables the PA and sleeps 700 ms before completion; power-down clears the PA enable bit.

## State and persistence
The driver has no long-lived private state beyond the regmap registered with the component. Hardware state is DAPM-managed through analog registers behind the ADDA PR regmap. ALSA control state persists in hardware/register cache according to regmap/component behavior. The headphone event intentionally serializes a long analog settling delay into DAPM power sequencing.

## Dependencies and integration points
It depends on `sun8i_adda_pr_regmap_init()`, ASoC DAPM, TLV controls, and DT compatibles `allwinner,sun8i-a23-codec-analog`, `allwinner,sun8i-h3-codec-analog`, and `allwinner,sun8i-v3s-codec-analog`. The analog widgets are intended to be linked at card level to stream widgets from the digital codec because the analog and digital blocks are separate ASoC components.

## Risks and edge cases
Dynamic topology must match SoC capabilities exactly; a missing quirk can expose controls for nonexistent pins or omit needed routes. The H3 line-out enable reuses a bit named for headphone PA on other SoCs, so register semantics are compatible only under the selected quirk. The V3s mixer special case is explicitly incomplete for all possible feature combinations. The 700 ms headphone delay can be user-visible and can affect power event latency. `of_device_get_match_data()` is assumed non-null for DT-created devices.

## Test signals
Validate each compatible's ALSA mixer list and DAPM graph. Exercise headphone, line-in/out, MIC1/MIC2, HBIAS/MBIAS routes, and ADC/DAC paths with `dapm_pop_time`/debugfs route inspection. Confirm no controls reference absent feature bits on V3s and that headphone pop suppression timing works on A23-style hardware.
