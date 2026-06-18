# sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3399_gru_sound.c

Purpose: RK3399 GRU machine driver supporting a variable set of codecs: CDN DP/HDMI, DA7219 headset codec, DMIC codec, MAX98357A speaker amp, RT5514 I2C capture codec, and RT5514 SPI DSP wake path.

Important APIs, types, and functions: `rockchip_sound_*_hw_params` functions set per-link MCLK policy; DA7219 also sets PLL sysclk. `rockchip_sound_cdndp_init` and `rockchip_sound_da7219_init` create jack objects and button mappings. `rockchip_dais` defines six DAI templates. `rockchip_routes` maps DAPM route sets per link. `dailink_match` and `rockchip_sound_codec_node_match` identify codecs by compatible string and optional bus type. `rockchip_sound_of_parse_dais` builds the active DAI-link array dynamically from `rockchip,cpu` and `rockchip,codec` phandles.

Control flow: Probe parses available codec phandles in order, filters unavailable nodes, matches each to a DAI template, picks CPU0 for most links, CPU1 for DP, and the codec node itself for RT5514 DSP SPI, copies matching DAPM routes, reads optional `dmic-wakeup-delay-ms`, and registers the card. Startup limits formats to S16_LE and rates to 8-96 kHz. Runtime hw_params sets MCLK to rate*256 or fixed audio-family clocks and delays after DMIC/RT5514 capture if configured.

State and persistence: Static card and jack objects persist for the module. Dynamic dai_link and routes arrays are devm-allocated. `dmic_wakeup_delay` is a module-global property value.

Dependencies and integration: Depends on Rockchip I2S, codec drivers for MAX98357A/RT5514/DA7219/HDMI/DMIC, I2C and SPI bus devices, ALSA jack/input key mapping, and device tree ordering of codec phandles.

Risks and edge cases: Codec matching silently skips unavailable or unmatched nodes, so missing audio paths may not fail probe. Static global `dmic_wakeup_delay` and jack objects are not multi-instance safe. CPU phandle references are not released. Rate constraints are broad but codec-specific fixed MCLK code rejects 192 kHz for DA7219.

Test signals: Boot should register links only for available GRU codecs. Jack events should appear for DP and headset buttons. Per-link playback/capture should set MCLKs and apply DMIC delay. Device-tree permutations should be tested for absent optional codecs.
