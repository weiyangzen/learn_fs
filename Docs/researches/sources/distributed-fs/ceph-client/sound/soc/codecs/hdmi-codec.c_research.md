# sources/distributed-fs/ceph-client/sound/soc/codecs/hdmi-codec.c

## Purpose
This file implements the generic ALSA SoC HDMI codec shim used by HDMI encoder, bridge, and display drivers that expose audio through `struct hdmi_codec_pdata`. It is not a register-level HDMI controller driver; it registers I2S and/or S/PDIF DAIs, exposes IEC958 and ELD ALSA controls, derives HDMI channel allocation and channel maps from ELD speaker allocation, reports HDMI jack state, and delegates real hardware programming to parent-provided `hdmi_codec_ops`.

## Important APIs, types, and functions
The main state is `struct hdmi_codec_priv`, which stores copied platform data, raw and parsed ELD, PCM channel-map control state, a stream serialization mutex and `busy` flag, optional jack state, IEC958 channel status, and an optional procfs ELD entry. Static CEA allocation data is represented by `enum hdmi_codec_cea_spk_placement`, `struct hdmi_codec_cea_spk_alloc`, `hdmi_codec_stereo_chmaps`, `hdmi_codec_8ch_chmaps`, and `hdmi_codec_channel_alloc`.

Important ALSA controls are implemented by `hdmi_eld_ctl_info/get`, `hdmi_codec_iec958_*`, `hdmi_codec_chmap_ctl_get`, and `hdmi_codec_pcm_new`. Runtime callbacks are `hdmi_codec_startup`, `hdmi_codec_shutdown`, `hdmi_codec_hw_params`, `hdmi_codec_prepare`, `hdmi_codec_i2s_set_fmt`, and `hdmi_codec_mute`. DAI/component lifecycle is handled by `hdmi_dai_probe`, `hdmi_dai_spdif_probe`, `hdmi_probe`, `hdmi_remove`, and `hdmi_codec_probe`. `plugged_cb` and `hdmi_codec_set_jack` integrate hotplug reporting with ASoC jack handling.

## Control flow
Platform probe validates platform data, requires at least one DAI and either `hw_params` or `prepare`, initializes default IEC958 consumer status, builds a DAI array from the requested I2S/S/PDIF capabilities, applies parent-provided channel and format limits, optionally removes unidirectional playback/capture stream descriptors, and registers one ASoC component.

DAI probe adds DAPM routes from playback streams to `TX` and from `RX` to capture streams, allocates a per-DAI `hdmi_codec_daifmt`, stores it as playback DMA data, and creates a procfs ELD entry when enabled. PCM creation attaches playback channel-map controls and adds per-PCM IEC958 mask/default and ELD controls.

Startup serializes active streams with `hcp->busy`, optionally calls parent `audio_startup`, retrieves and parses ELD for playback, applies ELD-derived runtime constraints, and selects stereo or multichannel chmap tables. `hw_params` and `prepare` fill `struct hdmi_codec_params`, calculate CEA channel allocation for PCM audio, fill IEC958 status from ALSA runtime parameters, update the DAI bit format, and call the corresponding parent operation. Shutdown resets the chmap state, calls parent `audio_shutdown`, and clears `busy`.

## State and persistence behavior
All state is in memory and ALSA/kernel objects; there is no on-disk persistence. The copied platform data and current IEC958 status persist for the lifetime of the platform device. Raw ELD is refreshed on playback startup and hotplug callbacks, cleared on unplug, and mirrored through an ALSA byte control and optional procfs text entry. `busy` enforces a single active stream across the component, while `chmap_idx` records the last chosen CEA allocation or unknown state.

## Dependencies and integration points
The driver integrates ASoC component/DAI/DAPM APIs, ALSA PCM constraints and chmap controls, IEC958 helpers, DRM ELD parsing, HDMI audio infoframe helpers, procfs, and ASoC jack reporting. Hardware-specific behavior is entirely delegated through `struct hdmi_codec_ops`: `audio_startup`, `audio_shutdown`, `get_eld`, `hw_params`, `prepare`, `mute_stream`, `hook_plugged_cb`, and `get_dai_id`.

## Risks and edge cases
The channel-allocation table is ordered policy and only covers the documented CEA speaker placements in the file; newer HDMI layouts or unusual ELD speaker masks can fail with `-EINVAL`. `hdmi_codec_fill_codec_params` stores `ca_id` in `chmap_idx`, while `hdmi_codec_chmap_ctl_get` treats the field as an index into the chmap table; this depends on CA IDs lining up with `hdmi_codec_8ch_chmaps` entries. The single `busy` flag rejects simultaneous streams even when hardware might support more. Parent callbacks are mandatory in selected paths, so incomplete platform data fails probe or later operations. Hotplug updates and PCM startup share ELD state without deep synchronization beyond callback sequencing.

## Test signals
Useful signals are successful component registration with I2S-only, S/PDIF-only, and mixed platform data; ALSA controls for IEC958, ELD, and channel maps on created PCMs; playback startup with valid, absent, and stereo-only ELD; CEA allocation choices for 2, 4, 6, and 8 channel PCM; non-PCM IEC958 status avoiding PCM channel allocation; parent callback ordering for startup, hw_params/prepare, mute, and shutdown; hotplug jack reports and ELD clearing; and negative tests for missing platform data, unsupported DAI format, unsupported ELD channel layout, and second simultaneous stream attempts.
