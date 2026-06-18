# sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hdmi.c

## Purpose

This file implements an Intel HDA-HDMI ASoC codec driver. It discovers digital converters and pins, creates one HDMI DAI per converter, builds DAPM converter/pin-port/mux widgets dynamically, handles HDMI/DP ELD and jack reporting through the DRM audio component, programs infoframes and channel maps, and manages HD-audio link/display power through runtime and system PM.

## Important APIs, types, and functions

Important state structs are `hdac_hdmi_priv`, `hdac_hdmi_cvt`, `hdac_hdmi_pin`, `hdac_hdmi_port`, `hdac_hdmi_pcm`, and `hdac_hdmi_dai_port_map`. Major functions include `hdac_hdmi_parse_and_map_nid()`, `hdac_hdmi_create_dais()`, `create_fill_widget_route_map()`, `hdac_hdmi_present_sense()`, `hdac_hdmi_eld_notify_cb()`, `hdac_hdmi_pcm_open()`, `hdac_hdmi_set_hw_params()`, `hdac_hdmi_set_stream()`, `hdac_hdmi_setup_audio_infoframe()`, `hdac_hdmi_pin_output_widget_event()`, `hdac_hdmi_cvt_output_widget_event()`, `hdac_hdmi_set_pin_port_mux()`, `hdmi_codec_probe()`, `hdac_hdmi_dev_probe()`, `hdac_hdmi_runtime_suspend()`, and `hdac_hdmi_runtime_resume()`.

## Control flow

HD-audio device probe allocates private state, registers channel-map callbacks, selects vendor NID data, powers display audio, enables Intel all-pin/DP1.2 vendor features, walks AFG child nodes to collect audio-out converters and pin widgets, creates DAIs from converter PCM capabilities, initializes DAI-to-converter maps, refreshes HDA widgets, and registers the ASoC component. Component probe gets the HD-audio link, dynamically creates DAPM widgets/routes, registers the DRM audio notifier, senses all pins, stores the ALSA card pointer, adds a runtime-PM device link from card to codec, enables runtime PM, and suspends the codec. ELD notifications map DRM port/pipe to HDA pin/port, skip system suspend and PM-in-progress, then call present-sense. Present-sense reads ELD through the audio component, parses speaker allocation, updates jack/DAPM state for the selected PCM, and notifies ELD controls when validity changes.

## State and persistence behavior

`hdac_hdmi_priv` persists converter, pin, PCM, and DAI maps plus mutexes and channel-map ops. Each port stores ELD buffer/validity, jack pin, DAPM work, and connection state. Each PCM stores selected converter, attached port list, stream tag, format, channels, user channel map, jack event count, lock, and ELD control pointer. Runtime PM powers the AFG/link/display down on idle and re-enables vendor features on resume. System resume re-senses pins because notifications are ignored while suspended.

## Dependencies and integration points

It depends on HDA extended bus, HDA codec verbs, HDA i915/DRM audio component ELD callbacks, DRM ELD parsing, HDMI infoframe helpers, ALSA jack, ASoC DAPM/DAI/control APIs, HDA channel-map helpers, and runtime PM. The HDA device ID table binds Skylake/Broxton/Kabylake/Cannonlake/Geminilake HDMI codecs with vendor-NID differences.

## Risks and test signals

Risks include dynamic DAPM route index mistakes, port/pin mapping assumptions (`pin - 4`, `port + 0x04`), MST port count fixed at three, race-prone `port_list` updates versus ELD work, jack event reference counts across shared PCMs, 44.1/88.2/176.4 kHz rates filtered out despite converter support, missing ELD control pointer before notifications, PM/link/display-power imbalance, and incorrect infoframe/channel allocation for DP versus HDMI. Test converter/pin discovery, DAI count, mux selection, hotplug/unplug on SST and MST, ELD constraints, channel-map set while prepared, infoframe programming, runtime suspend/resume, system suspend/resume, component remove with pending DAPM work, and each HDA ID table entry.
