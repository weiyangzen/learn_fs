# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi-mcp.c

## Purpose

This is the legacy NVIDIA MCP HDMI codec driver for older two-channel and multi-channel NVIDIA HDMI codecs that do not fit the fully generic HDMI parser.

## Important APIs, types, and functions

It uses `snd_hda_hdmi_simple_probe` with fixed master converter and pin NIDs, then overrides init, PCM, controls, and 8-channel stream programming. Important functions are `nvhdmi_mcp_probe`, `nvhdmi_mcp_init`, `nvhdmi_8ch_7x_pcm_prepare`, `nvhdmi_8ch_7x_pcm_close`, `nvhdmi_8ch_7x_set_info_frame_parameters`, `nvhdmi_mcp_build_pcms`, and `nvhdmi_mcp_build_controls`.

## Control flow

Probe builds simple HDMI state around NIDs `0x04` and `0x05`, overrides PCM capabilities because the codec does not report a complete list, and for 8-channel models replaces the playback stream with a custom stream. Prepare writes stream id and format to the master converter and four paired converter NIDs, temporarily toggling SPDIF enable when needed so IEC958 status updates stick. Close clears all stream ids and formats, then restores a valid 8-channel infoframe mask.

## State and persistence behavior

The driver uses `hdmi_spec.multiout`, `pcm_playback`, `hw_constraints_channels`, and `nv_dp_workaround`. Hardware state persists in vendor-specific infoframe channel allocation/checksum verbs and in converter stream programming until cleanup/close.

## Dependencies and integration points

It depends on simple HDMI helpers, HDA multi-out digital helpers, SPDIF state, channel-map controls, and NVIDIA vendor verbs for channel allocation, checksum, and audio protection. Device IDs distinguish two-channel and eight-channel legacy models.

## Risks and test signals

Risks include incorrect manual stream-id/channel-id mapping, broken IEC958 status propagation, invalid channel allocation checksum, and model-specific channel constraints. Test two-channel and 8-channel playback, 2/6/8 channel constraints by vendor ID, IEC958 non-audio status changes, channel-map control masks, close/reopen, and jack unsolicited reporting.
