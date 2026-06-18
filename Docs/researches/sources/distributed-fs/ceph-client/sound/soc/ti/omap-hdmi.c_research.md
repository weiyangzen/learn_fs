<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-hdmi.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-hdmi.c

## Purpose
ASoC HDMI audio glue for OMAP4/OMAP5 DSS. It creates a playback-only card and CPU DAI around DSS HDMI audio callbacks, DMAengine PCM, IEC60958 channel status, and CEA-861 audio infoframes.

## APIs, Types, and Functions
`struct hdmi_audio_data` stores the card, DSS ops/device, DMA data, DSS audio metadata, IEC/CEA structs, and current PCM stream guarded by a mutex. Core functions are `hdmi_dai_abort()`, `hdmi_dai_startup()`, `hdmi_dai_hw_params()`, `hdmi_dai_trigger()`, `hdmi_dai_shutdown()`, and `omap_hdmi_audio_probe()`. Two DAI templates differ by supported formats: OMAP4 permits S16/S24, OMAP5 only S16.

## Control Flow, State, and Persistence
Probe consumes platform data with DSS device, ops, version, and DMA address, registers the component on the DSS device, registers sDMA using `audio_tx`, and creates a dummy-codec ASoC card. Startup imposes 128-byte period/buffer alignment, binds DMA data, records the current stream, and calls DSS `audio_startup()` with an abort callback. `hw_params` chooses DMA maxburst, fills IEC60958 status and CEA infoframe fields based on format/rate/channels, then calls DSS `audio_config()`. Trigger starts/stops DSS audio; shutdown calls DSS `audio_shutdown()` and clears current stream.

## Dependencies and Integration
Depends on `sound/omap-hdmi-audio.h` platform data callbacks, ALSA IEC/CEA definitions, ASoC DAI/card APIs, DMAengine PCM, and TI sDMA registration. The display subsystem can asynchronously abort playback through the registered callback.

## Risks and Test Signals
Risks include platform-data-only binding, channel allocation limited to hard-coded 2/6/other mappings, current-stream WARNs rather than recoveries, OMAP5 format restriction mismatch with hardware expectations, and concurrent display disable during PCM operations. Test signals are probe for version 4 and 5, DSS callback ordering, abort on display disable, all supported rates in IEC status, 2/6/8 channel CEA mappings, S16/S24 rejection by version, and aligned DMA periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-hdmi.c -->
