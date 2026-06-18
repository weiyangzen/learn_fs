# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.c

## Purpose
This is the ASoC driver for the RK3328 internal codec. It primarily sequences DAC/headphone playback hardware, exposes one `rk3328-hifi` DAI, configures I2S/PCM format and word length, controls an optional external mute GPIO, and initializes the codec through MMIO regmap and GRF syscon.

## Important APIs, types, and functions
`struct rk3328_codec_priv` stores regmap, mute GPIO, `mclk`, `pclk`, cached sample clock, and speaker depop delay. Important functions are `rk3328_codec_reset()`, `rk3328_set_dai_fmt()`, `rk3328_mute_stream()`, `rk3328_codec_power_on/off()`, `rk3328_codec_open_playback()`, `rk3328_codec_close_playback()`, `rk3328_hw_params()`, startup/shutdown callbacks, component probe/remove, regmap predicates, and platform probe. Power sequencing data lives in `playback_open_list` and `playback_close_list`.

## Control flow and integration
Platform probe enables GRF `i2s_acodec_en`, reads `spk-depop-time-ms` with default 200 ms, obtains optional `mute` GPIO, handles a Rock64 legacy implicit mute path, enables `mclk` and `pclk`, maps MMIO registers, creates a cached regmap, and registers the ASoC component and DAI. Component probe resets and precharges the codec. PCM startup opens playback by applying the ordered register list, waiting for depop, unmuting GPIO, and setting output gains. Shutdown mutes GPIO, clears gains, applies the close list, resets the codec to avoid a 48 kHz to 44.1 kHz silence issue, and restores precharge current.

## State and persistence
Register state is cached with `REGCACHE_FLAT`; only reset is volatile. The mute GPIO state persists across open/close. `spk_depop_time` comes from DT and directly affects user-visible stream startup latency. Clocks remain enabled for the device lifetime after probe.

## Dependencies
The driver depends on Rockchip GRF syscon, MMIO resource mapping, regmap, clocks `mclk` and `pclk`, optional GPIO descriptor, ASoC DAI/component registration, and `rk3328_codec.h` for register definitions.

## Risks and test signals
Probe lacks a remove callback to disable clocks on driver removal because registration is devm-only; this may be acceptable for built-in SoC audio but is a resource-lifetime concern. The DAI advertises capture despite the driver only meaningfully sequences playback. The close path resets hardware as a sample-rate workaround, so cache coherency and next-open state should be tested. Test signals include startup/shutdown pop behavior, mute GPIO polarity, legacy Rock64 behavior, all supported DAI formats and PCM widths, regcache defaults after reset, and sample-rate switching from 48 kHz to 44.1 kHz.
