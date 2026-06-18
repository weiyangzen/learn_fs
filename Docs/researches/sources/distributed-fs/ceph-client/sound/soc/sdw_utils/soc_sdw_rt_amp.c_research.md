# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp.c

Purpose: supports Realtek RT1308/RT1316/RT1318/RT1320 SoundWire amplifiers, including DMI-specific BQ coefficient injection, DAPM speaker routing, RT1308 I2S clock setup, and lifecycle cleanup.

Important APIs and data: DMI table entries map Dell SKUs to coefficient arrays from `soc_sdw_rt_amp_coeff_tables.h`. `rt_amp_add_device_props()` installs `realtek,bq-params` and count properties. Route arrays map one or two amps per codec family. `asoc_sdw_rt_amp_spk_rtd_init()` selects the route map from DAI name and adds routes based on `name_prefix` suffix `-1` or `-2`. `soc_sdw_rt1308_i2s_ops` sets PLL/sysclk in `rt1308_i2s_hw_params()`. `asoc_sdw_rt_amp_init()` counts playback amps and, once two are present, applies software-node properties to both SDW devices. `asoc_sdw_rt_amp_exit()` removes those nodes and drops references.

Control flow and state: amp count is accumulated in `info->amp_num`; device refs are stored in `ctx->amp_dev1/2`; software nodes persist until exit. DAPM routes persist for the card lifetime.

Dependencies and integration: used by Realtek amp entries in `codec_info_list`; depends on DMI, SoundWire bus lookup, software nodes, ASoC DAPM/DAI clock APIs, and RT1308 codec constants.

Risks: if second device lookup fails, the first reference/property may already be held. Route selection defaults unknown codec names to RT1320. Prefix parsing supports only `-1`/`-2`, so larger arrays rely on other helpers.

Test signals: Dell SKU systems expose BQ properties to codec drivers, two-amp cards add both left/right routes, RT1308 I2S sets PLL at `rate * 512`, and remove unloads software nodes.
