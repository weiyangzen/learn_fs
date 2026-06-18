# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.c

## Purpose
Implements DCN3 audio formatter setup for HDMI and DisplayPort audio packet generation, stream audio mapping, mute/power behavior, and infoframe update.

## Important APIs, Types, And Functions
`afmt3_setup_hdmi_audio()` powers on the block and programs IEC 60958 channel status defaults and channel numbers. `speakers_to_channels()` maps `audio_speaker_flags` to CEA channel allocation bits. `afmt3_se_audio_setup()` selects the audio source instance and writes channel allocation. `afmt3_audio_mute_control()` powers down/up conditionally and toggles audio sample transmission. `afmt3_audio_info_immediate_update()` forces double-buffered audio infoframe update. `afmt3_setup_dp_audio()` programs DP audio packet defaults. `afmt3_construct()` initializes the object and function table.

## Control Flow
HDMI/DP setup optionally powers on through function pointers, then writes packet-control and 60958/infoframe registers. Stream setup asserts and null-checks `audio_info`, maps speakers to channels, selects audio source, enables channels, and clears forced memory power-off if no poweron callback exists. Mute powers down before disabling packets and powers on before enabling packets.

## State And Persistence
Hardware state persists in AFMT packet, source, channel-status, infoframe, and memory-power registers. Software state is the initialized `dcn30_afmt` object and optional power callbacks in the base function table.

## Dependencies And Integration Points
Depends on `dc_bios_types`, `hw_shared`, `dcn30_afmt.h`, and `reg_helper`. It integrates with stream encoder/audio setup paths for HDMI and DP on DCN3.

## Risks
`audio_info == NULL` is asserted then tolerated by return, so release builds silently skip setup. Power callback ordering matters for mute/unmute. Channel mapping logic encodes speaker exclusivity rules and can produce wrong CEA allocation if flags are inconsistent.

## Test Signals
HDMI and DP audio playback, channel allocation for stereo/5.1/7.1 layouts, mute/unmute power transitions, infoframe update readback, and no audio packet transmission while muted.
