<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-twl4030.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-twl4030.c

## Purpose
Generic ASoC machine driver for TI OMAP boards with a TWL4030 codec. It replaces several older board-specific drivers by supporting DT or platform-data routing, HiFi and optional voice links, headset jack GPIO detection, and stereo/TDM format selection.

## APIs, Types, and Functions
`struct omap_twl4030` stores the headset jack. Important code paths are `omap_twl4030_hw_params()` for channel-count-dependent DAI format, `omap_twl4030_init()` for jack and optional pin disconnects, `twl4030_disconnect_pin()`, static HiFi/voice DAI links, and `omap_twl4030_probe()`.

## Control Flow, State, and Persistence
Probe handles either DT or legacy platform data. DT parses `ti,model`, required `ti,mcbsp`, optional `ti,mcbsp-voice`, and optional `ti,audio-routing`; with routing it marks the card fully routed. Platform data supplies card name, voice link presence, and optional custom routing booleans. HiFi `hw_params` sets I2S provider mode for stereo and DSP_A provider mode for four-channel TDM. Runtime init adds jack GPIO support only if `ti,jack-det-gpio` is present and disables unconnected pins for custom platform-data routing.

## Dependencies and Integration
Depends on TWL4030 codec DAI names `twl4030-hifi`/`twl4030-voice`, OMAP McBSP CPU DAIs, ASoC jack GPIO APIs, OF phandles, and legacy `omap-twl4030` platform data.

## Risks and Test Signals
Risks include static global card/link structures mutated per probe, optional `of_node_put()` omissions, property name mismatch between `ti,jack-det-gpio` and GPIO descriptor lookup, only 2- and 4-channel HiFi formats, and mixed DT/platform-data paths. Test signals are DT and platform-data probe, HiFi stereo and four-channel streams, optional voice link, jack GPIO reporting, custom routing pin disables, and audio-routing parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-twl4030.c -->
