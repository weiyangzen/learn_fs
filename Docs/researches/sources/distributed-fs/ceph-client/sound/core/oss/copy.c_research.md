# sources/distributed-fs/ceph-client/sound/core/oss/copy.c

## Purpose
`copy.c` implements the trivial OSS PCM plugin that copies audio frames unchanged between identical source and destination formats. It is used in plugin chains where a pass-through stage is needed.

## Important APIs, Types, and Functions
`copy_transfer()` is the plugin transfer callback. `snd_pcm_plugin_build_copy()` validates identical format, rate, and channel count, builds a plugin named `"copy"`, and installs the transfer callback.

## Control Flow and State
For each channel, transfer verifies byte-aligned areas, silences wanted destination channels when the source channel is disabled, marks destination enable state, and calls `snd_pcm_area_copy()` for enabled channels. It returns the requested frame count unless input validation fails. The plugin holds no custom private state.

## Dependencies and Integration Points
It depends on OSS PCM plugin infrastructure from `pcm_plugin.h`, PCM area helpers, and format metadata. It is linked only when OSS PCM plugin support is enabled.

## Risks and Test Signals
Risks are incorrect enabled/wanted channel propagation and area alignment assumptions. Tests should pass identical interleaved and noninterleaved formats, disabled source channels, zero frames, and invalid mismatched format/rate/channel inputs.
