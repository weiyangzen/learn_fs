# sources/distributed-fs/ceph-client/sound/soc/uniphier/evea.c

## Purpose
ASoC codec driver for the Socionext UniPhier EVEA ADC/DAC block. It provides line input, line output, headphone output, controls, DAPM widgets/routes, clock/reset sequencing, and MMIO regmap access.

## Important APIs, Types, and Functions
The driver-private state is `struct evea_priv`. Important helpers are `evea_set_power_state_on()`, `evea_set_power_state_off()`, `evea_update_switch_lin()`, `evea_update_switch_lo()`, `evea_update_switch_hp()`, `evea_update_switch_all()`, codec callbacks `evea_codec_probe()`, `evea_codec_suspend()`, `evea_codec_resume()`, and platform callbacks `evea_probe()`/`evea_remove()`. It defines DAPM widgets/routes, three switch controls, `soc_codec_evea`, and three DAIs: line1, hp1, and lo2.

## Control Flow, State, and Persistence
Probe allocates private state, gets `evea` and `exiv` clocks, gets shared resets, maps MMIO, creates a 32-bit regmap, enables clocks, deasserts resets in the required order, obtains/deasserts `adamv`, and registers the codec component. Component probe defaults line, line-out, and headphone switches to enabled and programs analog power/mute state. Suspend powers outputs down, asserts resets in reverse, and disables clocks; resume restores clocks/resets, powers the codec on, and reapplies switch state. Switch values persist in `evea_priv` and are replayed after resume.

## Dependencies and Integration Points
Depends on Linux clock/reset/regmap/platform APIs and ALSA SoC component, DAPM, and control APIs. It integrates with UniPhier AIO line/headphone DAIs through stream names such as `Line In 1`, `Line Out 1`, `Headphone 1`, and `Line Out 2`.

## Risks and Test Signals
Risks include register naming where power-down bits are set for active state, no regcache across suspend, ignored `regmap_update_bits()` return values, strict reset ordering because ADAMV hangs if EXIV reset is asserted, and switch controls bypassing richer DAPM event sequencing. Test signals are probe/resume reset order, switch get/put behavior, DAPM route visibility, 48 kHz S32_LE line capture/playback, headphone mute/unmute transitions, and suspend/resume audio recovery.
