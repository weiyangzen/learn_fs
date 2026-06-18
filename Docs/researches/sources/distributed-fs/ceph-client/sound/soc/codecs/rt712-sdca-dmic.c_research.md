# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.c

Purpose: Implements a standalone RT712 SDCA digital microphone SoundWire codec function. Unlike `rt712-sdca.c`, this file registers only the mic-array component and a single capture DAI, with its own regmaps, controls, DAPM graph, attach initialization, and PM handling.

Important APIs and functions: `rt712_sdca_dmic_sdw_probe()` initializes 8-bit SDCA and 16-bit MBQ regmaps and calls `rt712_sdca_dmic_init()`. `rt712_sdca_dmic_io_init()` programs DMIC/ADC/HDA floating entity maps, enables the input terminal, ultrasound detector, RC calibration value, and marks `hw_init`. `rt712_sdca_dmic_hw_params()` configures SoundWire TX port 2 and writes mic-array sample-frequency controls. Control helpers manage four-channel FU1E mute/volume and FU15 boost.

Control flow: Probe creates regmaps cache-only and registers the ASoC component/DAI. On SoundWire attach, `update_status` calls `io_init`, which disables cache-only, optionally bypasses cache on reattach, performs vendor index programming, toggles first-init state, and autosuspends. ALSA mixer controls convert user gain values to SDCA fixed-point MBQ values. DAPM events combine software mixer mutes with DAPM mute state before writing per-channel FU1E mute controls, and PDE 11 power events request PS0/PS3.

State and persistence: `struct rt712_sdca_dmic_priv` stores regmaps, component, slave, bus params, init flags, `fu1e_dapm_mute`, and four per-channel mixer mute bits. Regcache is synchronized on resume and made dirty after cache-bypassed reinitialization.

Dependencies and integration: Uses common RT712 SDCA constants from `rt712-sdca.h`, standalone defaults from `rt712-sdca-dmic.h`, SoundWire slave ops, regmap, runtime PM, and ASoC DAPM/control APIs. It matches SDW part IDs `0x1712`, `0x1713`, `0x1716`, and `0x1717`.

Risks and test signals: The source uses some casts to `struct rt712_sdca_priv *` in gain helpers even though component drvdata is the DMIC private type; the accessed leading fields currently align but this is a maintenance hazard. Test four-channel capture, rates 16/32/44.1/48/96/192 kHz, port-2 SoundWire setup, mux selection, per-channel mute/volume, suspend/resume regcache sync, and attach/unattach reinitialization.
