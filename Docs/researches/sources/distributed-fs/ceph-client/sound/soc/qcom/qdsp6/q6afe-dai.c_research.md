# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-dai.c

## Purpose
`q6afe-dai.c` implements the ASoC DAI component for QDSP6 Audio Front End ports. It exposes HDMI/DP, Slimbus, MI2S, TDM, codec DMA, and USB AFE ports as DAIs, translates ALSA hw_params and DAI ops into `q6afe_port_config`, starts/stops DSP AFE ports, registers DAPM widgets/routes, and parses OF per-port configuration.

## Important APIs, types, and functions
`struct q6afe_dai_data` stores one `q6afe_port *`, one `q6afe_port_config`, a started flag, and private config for each AFE port ID. `struct q6afe_dai_priv_data` stores MI2S/TDM-specific DT settings such as SD-line mask, sync mode/source, data output, invert sync, data delay, and data alignment.

Parameter functions include `q6slim_hw_params()`, `q6hdmi_hw_params()`, `q6afe_usb_hw_params()`, `q6i2s_hw_params()`, `q6tdm_hw_params()`, and `q6dma_hw_params()`. Configuration ops include `q6i2s_set_fmt()`, `q6tdm_set_tdm_slot()`, `q6tdm_set_channel_map()`, `q6dma_set_channel_map()`, `q6slim_set_channel_map()`, and `q6afe_mi2s_set_sysclk()`. Runtime control is handled by `msm_dai_q6_dai_probe()`, `msm_dai_q6_dai_remove()`, `q6afe_dai_prepare()`, and `q6afe_dai_shutdown()`.

## Control flow
Probe allocates `q6afe_dai_data`, parses child OF nodes for per-port MI2S/TDM properties, builds DAI drivers through `q6dsp_audio_ports_set_config()`, and registers the ASoC component with DAPM widgets/routes. Each DAI probe obtains a `q6afe_port` by ID. ALSA `hw_params` fills the appropriate union member in `port_config`. DAI-specific ops fill channel maps, TDM slot masks, sysclk settings, or I2S format.

On `prepare`, if the port is already started it is first stopped so new config can be applied. The function then dispatches by DAI ID to HDMI, Slimbus, I2S, TDM, codec DMA, or USB prepare helpers and starts the port with `q6afe_port_start()`. Shutdown stops an active port and clears the started flag.

## State and persistence behavior
Runtime state is per platform device in `q6afe_dai_data`. `is_port_started[]` prevents redundant stops and allows reprepare with changed config. Port handles are acquired on DAI probe and released on DAI remove. OF-derived private settings persist for the lifetime of the device. No disk state is written; DSP AFE state persists until stop or DSP reset.

## Dependencies and integration points
The file depends on Q6AFE port APIs, common Q6DSP audio-port DAI generation, channel allocation helpers, Qualcomm Q6AFE DT bindings, ALSA ASoC component/DAI/DAPM APIs, and OF child node parsing. It integrates with machine drivers through DAPM routes and with DSP firmware through `q6afe_port_prepare/start/stop`.

## Risks and test signals
Risks include array indexing by raw DAI ID up to `AFE_PORT_MAX`, incomplete validation for unsupported formats, OF child-node ref leaks in `for_each_child_of_node()` error paths, and not stopping ports when prepare partially succeeds then start fails. TDM and codec DMA channel maps need careful validation because masks and slot arrays differ by direction. Tests should cover each DAI family, repeated prepare with changed params, shutdown without prepare, invalid TDM slot widths/slot counts, channel-map bounds, sysclk IDs, OF parsing for MI2S/TDM properties, and DAPM route visibility.
