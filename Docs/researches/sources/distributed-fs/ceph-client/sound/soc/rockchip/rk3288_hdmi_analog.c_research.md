# sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3288_hdmi_analog.c

Purpose: RK3288 machine driver for boards with an analog codec plus HDMI audio on a shared Rockchip I2S controller. It builds a multi-codec ASoC card with DAPM pins for analog headphone and HDMI output.

Important APIs, types, and functions: `struct rk_drvdata` stores optional headphone-enable GPIO. `rk_hp_power` drives that GPIO from DAPM events. `rk_hw_params` selects MCLK rates based on sample rate and calls `snd_soc_dai_set_sysclk` on CPU and analog codec DAIs. `rk_init` sets optional headphone jack GPIO detection. Probe parses `rockchip,model`, `rockchip,audio-codec`, codec DAI name, `rockchip,i2s-controller`, and `rockchip,routing`.

Control flow: Probe allocates machine data, binds card/device, requests optional `rockchip,hp-en` GPIO, parses card name and phandles, assigns CPU/platform/codec nodes into a single DAI link, parses routing, stores drvdata, and registers the card. During stream setup, `hw_params` chooses 12.288 MHz, 24.576 MHz, or 11.2896 MHz MCLK. DAPM toggles headphone power.

State and persistence: Static card and DAI link definitions are mutated with of-nodes during probe. Runtime state is limited to GPIO descriptor and jack object. GPIO state follows DAPM.

Dependencies and integration: Depends on Rockchip I2S CPU DAI, HDMI codec, analog codec named by device tree, optional headset GPIO, ALSA jack helpers, and device-tree routing.

Risks and edge cases: Static globals make multiple instances unsafe. HDMI codec component name `hdmi-audio-codec.2.auto` is hard-coded for the second codec slot. `snd_soc_jack_add_gpios` legacy GPIO jack setup has no explicit cleanup. Unsupported rates fail in `hw_params`.

Test signals: Device tree probe should create a card with "Analog" and "HDMI" controls. Jack GPIO should report headphone state when present. Playback at common 44.1/48/96/192 kHz rates should program expected MCLKs; unsupported rates should fail cleanly.
