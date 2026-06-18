# sources/distributed-fs/ceph-client/sound/soc/codecs/inno_rk3036.c

## Purpose
This file is the ASoC codec driver for the Rockchip RK3036 internal Inno audio codec. It maps the codec MMIO registers through regmap, selects the internal codec through the GRF syscon, enables the peripheral clock, exposes a stereo playback DAI, and provides DAPM routes and mixer controls for DAC-to-headphone playback.

## Important APIs, types, and functions
`struct rk3036_codec_priv` stores the MMIO base, peripheral clock, codec regmap, and device pointer. The custom anti-pop ALSA control is implemented by `rk3036_codec_antipop_info`, `rk3036_codec_antipop_get`, and `rk3036_codec_antipop_put`. Static control, widget, and route arrays describe headphone volume, zero-cross, headphone mute, anti-pop, DAC switches, DAC power supplies, headphone mixers, PGAs, and outputs.

DAI operations are `rk3036_codec_dai_set_fmt` and `rk3036_codec_dai_hw_params`. Component lifecycle and power handling are `rk3036_codec_reset`, `rk3036_codec_probe`, `rk3036_codec_remove`, and `rk3036_codec_set_bias_level`. Platform lifecycle is handled by `rk3036_codec_platform_probe` and `rk3036_codec_platform_remove`.

## Control flow
Platform probe allocates private state, maps the MMIO resource, creates a 32-bit/stride-4 regmap, looks up the `rockchip,grf` syscon phandle, writes `GRF_ACODEC_SEL` to select the internal codec, gets and enables `acodec_pclk`, stores private data, and registers the ASoC component and one playback DAI. Remove disables the clock.

Component probe toggles codec reset bits from reset to work. DAI format selection programs master/slave pin direction, I2S/PCM/right-justified/left-justified mode, LR clock polarity, and bit clock polarity. `hw_params` maps sample format to valid word length, forces normal LR polarity, selects 32-bit frame word length, and brings DAC reset into work state. Bias standby writes maximum charge current and precharge state; bias off writes maximum discharge current and discharge state.

## State and persistence behavior
Runtime state lives in hardware registers, regmap cache behavior, the enabled clock, and DAPM/control state. The driver has no suspend/resume code and no disk persistence. Register symbolic definitions live in `inno_rk3036.h`; this file uses them for all hardware writes.

## Dependencies and integration points
The driver depends on the platform bus, MMIO resources, `acodec_pclk`, the Rockchip GRF syscon phandle, regmap MMIO, ASoC component/DAI/DAPM/control APIs, and the RK3036 codec register definitions in `inno_rk3036.h`. Device tree binding uses `rockchip,rk3036-codec`.

## Risks and edge cases
Probe fails if the GRF phandle or clock is missing, even if the codec registers map correctly. The regmap config has no defaults or volatile/writeable filters, so all accesses rely on correct call-site masks. DAI `hw_params` supports only playback formats and does not inspect sample rate, relying on the clocking side to supply a valid rate. Bias transitions overwrite `INNO_R06`, which also contains zero-cross and DAC enable bits, so ordering with DAPM routes matters. Anti-pop get/put uses two-bit fields for left/right and returns boolean state only.

## Test signals
Useful checks are device tree probe with valid MMIO, GRF, and clock; GRF write selecting the codec; component reset writes; playback open with S16_LE, S20_3LE, S24_LE, and S32_LE; DAI format programming for I2S, DSP_A, right-justified, and left-justified modes; headphone volume/switch/anti-pop controls; DAPM route activation to `HPL` and `HPR`; clock disable on remove; and negative probe tests for absent `rockchip,grf` or `acodec_pclk`.
