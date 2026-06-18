<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_audio.c

## Purpose

`adv7511_audio.c` implements optional HDMI audio hooks for the ADV7511 bridge using the DRM HDMI audio bridge callbacks and ASoC HDMI codec parameters.

## Important APIs, Types, And Functions

- `adv7511_calc_cts_n()`: computes HDMI CTS/N values from TMDS clock and sample rate.
- `adv7511_update_cts_n()`: writes N and manual CTS registers.
- `adv7511_hdmi_audio_prepare()`: validates sample rate, width, and audio interface format; programs audio source, I2S format, bit clock inversion, sample length, sample-rate ID, CTS/N, and audio infoframe.
- `adv7511_hdmi_audio_startup()`: unmutes/enables audio-related packets, marks audio not copyrighted, disables AV mute, and enables SPDIF receiver if selected.
- `adv7511_hdmi_audio_shutdown()`: disables SPDIF receiver when needed and clears the audio infoframe.

## Control Flow

Prepare maps `hdmi_codec_params` and `hdmi_codec_daifmt` to ADV7511 register values, rejecting unsupported rates, widths, or formats. Startup enables packets and receiver state after a valid prepare. Shutdown reverses SPDIF receiver state and removes the advertised audio infoframe.

## State And Persistence Behavior

The file updates `adv7511->audio_source` and `adv7511->f_audio`. It persists audio state in hardware registers for N/CTS, audio source/config, I2S width/format, packet enables, general-control AV mute, and infoframes.

## Dependencies And Integration Points

It depends on ALSA/ASoC HDMI codec types, DRM HDMI state helpers, and register definitions from `adv7511.h`. It is wired into `adv7511_bridge_funcs` only when `CONFIG_DRM_I2C_ADV7511_AUDIO` is enabled.

## Risks And Edge Cases

CTS/N calculation assumes supported HDMI sample rates; unsupported values leave `n` uninitialized if new callers bypass validation. 32-bit samples are accepted only for IEC958 subframes. Startup uses the previously prepared `audio_source`, so calling order matters. Infoframe update failures from DRM helpers propagate only from prepare.

## Test Signals

HDMI audio playback at all supported sample rates and widths, I2S/right-justified/left-justified/SPDIF modes, IEC958 32-bit path, infoframe inspection, audio mute/start/stop cycles, and hotplug with active audio are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_audio.c -->
