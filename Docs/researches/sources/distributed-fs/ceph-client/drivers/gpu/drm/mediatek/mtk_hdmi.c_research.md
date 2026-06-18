# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi.c

## Purpose
Implements the original MediaTek HDMI transmitter driver for MT2701/MT8167/MT8173-era HDMI IP. It provides DRM bridge callbacks, hardware register programming, CEC-backed HPD, EDID reads over DDC, audio codec callbacks, infoframe emission, PLL/PHY sequencing, and SoC-specific mode limits.

## Important APIs, types, and functions
- Uses shared `struct mtk_hdmi` from `mtk_hdmi_common.h`.
- Hardware helpers cover register write authorization, reset, DVI/HDMI mode, AV mute/unmute, video blacking, deep color, N/CTS, audio routing, I2S/SPDIF setup, and infoframes.
- Bridge callbacks are collected in `mtk_hdmi_bridge_funcs`.
- Codec callbacks are collected in `mtk_hdmi_audio_codec_ops`.
- `mtk_hdmi_probe()` calls `mtk_hdmi_common_probe()`, requires CEC, and enables audio clocks.

## Control flow
Common probe performs allocation and DT parsing; this v1 probe then requires a CEC device because HPD status is delegated through `mtk_cec_hpd_high()` and registers a CEC HPD event callback on bridge attach. Atomic pre-enable makes HDMI registers writable, optionally through secure monitor call unless `tz_disabled`, enables HDMI 1.4 mode, and marks the block powered. Atomic enable retrieves the connector from atomic state, calls `mtk_hdmi_output_set_display_mode()`, enables PLL/pixel clocks, powers the PHY, sends audio/AVI/SPD/vendor infoframes, and marks enabled.

Mode programming blacks video, mutes audio, sends AV mute, powers the PHY off, sets the HDMI PLL to pixel clock, toggles system FIFO/deep-color bits, resets/configures HDMI registers, powers PHY on, configures audio output, then unblacks/unmutes. Audio hw params validate shared audio parameters, program channel mapping, input type, sample size, channel status, MCLK, and N/CTS, then enable audio packets.

## State and persistence
`struct mtk_hdmi` persists current mode, `dvi_mode`, `powered`, `enabled`, `audio_enable`, audio params, current connector pointer, CEC/DDC devices, clocks, PHY, and callback registration. Hardware state persists in GRL and syscon registers, PHY state, PLL clock rate, infoframe registers, and CEC HPD callback wiring.

## Dependencies and integration points
Depends on the shared HDMI common library, `mtk_cec`, HDMI codec framework, DRM bridge/EDID/infoframe helpers, regmap/syscon, SMC secure-register service, clocks, PHY, DDC I2C adapter, and OF graph bridge chaining. It integrates as a DRM bridge and as a platform-provided HDMI codec device.

## Risks
Power sequencing is delicate: register write authorization, HDMI_ON/ANLG_ON, 1.4 mode, PLL, PHY, and infoframes must happen in the right order. HPD depends on CEC, making v1 probe fail without CEC. EDID read sets `dvi_mode` using raw EDID audio detection rather than the newer connector display-info path. Audio hw params ignore return from `mtk_hdmi_audio_params()` in the callback. Mode validation has both generic HDMI limits and SoC-specific CEA/max-clock filters.

## Test signals
Signals include HPD notifications from CEC, EDID read success, mode validation at 27 MHz/297 MHz and MT8167 148.5 MHz CEA-only limits, audio startup/hw_params/mute/shutdown, N/CTS values, DVI-mode behavior for no-audio monitors, suspend/resume audio clock recovery, and visible AV mute/unmute during modesets.
