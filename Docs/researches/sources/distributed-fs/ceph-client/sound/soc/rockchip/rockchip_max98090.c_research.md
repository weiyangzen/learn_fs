# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_max98090.c

Purpose: Rockchip machine driver for boards using MAX98090 analog audio, HDMI audio, or both. It builds the appropriate ASoC card based on device-tree codec phandles and wires DAPM, jack detection, MCLK setup, and a TS3A227E headset accessory device.

Important APIs, types, and functions: Defines three card variants: analog, HDMI, and analog+HDMI. `rk_aif1_hw_params` selects MCLK for common 44.1/48 kHz families and skips codec sysclk errors for HDMI. `rk_aif1_startup` constrains period size to 240 for PL330 stress behavior. `rk_98090_headset_init` creates headset/button jack and calls `ts3a227e_enable_jack_detect`. `rk_jack_event` force-enables/disables `MICBIAS` and `SHDN` DAPM pins on microphone presence. Probe selects card variant from `rockchip,audio-codec` and `rockchip,hdmi-codec`.

Control flow: Probe parses I2S controller, optional audio and HDMI codecs, mutates the selected static DAI links with CPU/platform/codec nodes, requires `rockchip,headset-codec` when analog audio exists, parses card name, and registers the card. Runtime init registers the jack notifier or HDMI jack. Startup applies the period constraint, and hw_params programs CPU/codec clocks.

State and persistence: Static cards, links, jacks, notifier, and aux device are module-global. DAPM pin state changes on jack events. OF node pointers are stored in static link structures.

Dependencies and integration: Depends on Rockchip I2S, MAX98090, optional HDMI codec, TS3A227E headset codec, PL330-related period constraint, and device-tree phandles.

Risks and edge cases: Static globals make multiple cards unsafe. Probe does not release OF nodes. Requiring headset codec for any analog path may prevent analog audio without TS3A227E. The fixed period size is conservative but can surprise users. Comment typo names MAX90809.

Test signals: DT variants should create analog-only, HDMI-only, and combined cards. Headset insertion should toggle MICBIAS/SHDN and report buttons. Playback should work at supported rates and enforce 240-frame periods.
