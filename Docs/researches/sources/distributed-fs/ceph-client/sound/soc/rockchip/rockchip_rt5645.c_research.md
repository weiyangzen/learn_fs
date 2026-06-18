# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_rt5645.c

Purpose: Rockchip machine driver for boards using RT5645/RT5650 analog codec on a Rockchip I2S controller.

Important APIs, types, and functions: Defines one static DAI link named `rt5645` with codec DAI `rt5645-aif1`, DAPM widgets/routes for headphones, speakers, headset mic, and internal mic, and DAPM pin controls. `rk_aif1_hw_params` sets CPU and codec MCLK to 12.288 MHz or 11.2896 MHz families. `rk_init` creates headset/button jack and calls `rt5645_set_jack_detect`. Probe parses codec and I2S phandles plus `rockchip,model`; remove releases stored OF nodes.

Control flow: Probe assigns card device, parses `rockchip,audio-codec`, parses `rockchip,i2s-controller`, sets platform node to CPU node, parses card name, and registers the card. On error and remove, it drops OF references. Runtime init configures jack reporting. `hw_params` rejects unsupported sample rates and programs clocks.

State and persistence: Static card, DAI link, and jack objects are module-global. OF node references are stored until remove or probe error. No extra runtime-private allocation is used.

Dependencies and integration: Depends on Rockchip I2S, RT5645 codec driver, ALSA jack/input support, and device-tree phandles.

Risks and edge cases: Static globals are not multi-instance safe. Only specific rate families are accepted. Jack detect passes the same jack object for headphone, mic, and button reporting, matching codec API expectations but coupling all events to one object.

Test signals: Probe should create the named card and controls. Headset insertion/buttons should report through the RT5645 jack. Playback/capture at supported rates should set both CPU and codec clocks; missing phandles should fail and release references.
