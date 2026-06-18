<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdw.h -->
# sources/distributed-fs/ceph-client/include/sound/sdw.h

## Purpose
`sdw.h` provides ALSA/ASoC SoundWire helper glue. Its main utility converts PCM hardware parameters into SoundWire stream and port configuration.

## Important APIs, types, and functions
The inline helper `snd_sdw_params_to_config()` accepts a PCM substream, `snd_pcm_hw_params`, `sdw_stream_config`, and `sdw_port_config`. It fills frame rate, channel count, bits per sample, SoundWire direction, and channel mask.

## Control flow
ASoC SoundWire drivers call the helper during `hw_params`. The helper reads `params_rate()`, `params_channels()`, and `params_format()`, maps playback to `SDW_DATA_DIR_RX` and capture to `SDW_DATA_DIR_TX`, then sets `port_config->ch_mask` from the channel count. Drivers still supply port number and any hardware-specific settings.

## State and persistence behavior
The helper mutates only the caller-provided config structs. There is no persistent state.

## Dependencies and integration points
It includes Linux SoundWire definitions plus ALSA PCM headers. It bridges standard ALSA PCM parameters to SoundWire bus stream configuration.

## Risks and test signals
Risks include invalid channel counts causing a bad `GENMASK()`, unsupported PCM formats yielding unexpected sample width, and drivers forgetting to fill port number or override complex routing. Test signals include playback/capture direction mapping, mono/stereo/multichannel masks, non-16-bit formats, and driver-specific post-helper overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdw.h -->
