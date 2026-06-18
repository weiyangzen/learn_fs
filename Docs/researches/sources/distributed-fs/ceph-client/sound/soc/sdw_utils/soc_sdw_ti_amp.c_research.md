# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_ti_amp.c

Purpose: initializes TI TAS2783 SoundWire amplifier speaker routes and volume limits.

Important APIs: `asoc_sdw_ti_amp_initial_settings()` limits `<prefix> Speaker Volume` to `TIAMP_SPK_VOLUME_0DB`. `asoc_sdw_ti_spk_rtd_init()` iterates codec DAIs named `tas2783`, maps prefixes `tas2783-1` through `tas2783-4` to `Left Spk`, `Right Spk`, `Left Spk2`, and `Right Spk2`, applies volume limits, and adds DAPM routes from the selected speaker widget to `<prefix> SPK`. `asoc_sdw_ti_amp_init()` increments `info->amp_num` only for playback.

Control flow and state: runtime init loops over all codec DAIs in a link and returns on unhandled prefix, volume-limit failure, or route-add failure. Persistent state is mixer limit, DAPM route, and amp count.

Dependencies and integration: TAS2783 entry in `codec_info_list` supplies four-speaker widgets and controls and binds these helpers. Uses ASoC DAPM and mixer volume limiting.

Risks: `asoc_sdw_ti_amp_initial_settings()` logs volume-limit errors but returns 0, so route init may proceed after a failed limit. Prefix parsing is hard-coded to four amps. Buffers assume short prefixes/widget names.

Test signals: four-speaker systems expose all left/right speaker pins, each TAS2783 volume control is capped, unrecognized prefixes produce `unhandled prefix`, and playback DAPM routes target the right physical speaker.
