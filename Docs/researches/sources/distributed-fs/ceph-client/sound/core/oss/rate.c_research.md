# sources/distributed-fs/ceph-client/sound/core/oss/rate.c

## Purpose

`rate.c` implements the OSS PCM rate-conversion plugin. It resamples signed 16-bit PCM between different source and destination rates using fixed-point linear interpolation, preserving per-channel history across transfer calls.

## Important APIs, Types, and Functions

`struct rate_priv` stores fixed-point `pitch`, current fractional `pos`, selected conversion function, cached frame-count mappings, and per-channel `last_S1`/`last_S2` samples. `snd_pcm_plugin_build_rate()` validates same channel count, S16 source and destination formats, and different rates, then installs `rate_transfer()`, `rate_src_frames()`, `rate_dst_frames()`, and `rate_action()`.

## Control Flow

The builder computes `pitch` in 11-bit fractional units and selects `resample_expand()` for upsampling or `resample_shrink()` for downsampling. `rate_transfer()` computes destination frames, clamps to destination capacity, and calls the selected resampler. The resamplers walk each channel, skip disabled inputs with optional silence output, interpolate between saved samples, update destination samples, and persist the final interpolation position and sample history.

## State and Persistence Behavior

Conversion state is per plugin instance and persists in `plugin->extra_data`. `rate_init()` resets position and channel sample history on `INIT` and `PREPARE`. `old_src_frames` and `old_dst_frames` cache recent frame-size calculations to stabilize reciprocal sizing in the plugin chain.

## Dependencies and Integration Points

The rate plugin depends on `pcm_plugin.h`, ALSA format assumptions, and `snd_pcm_area_silence()` for disabled channels. It is inserted by `snd_pcm_plug_format_plugins()` when client and slave rates differ by more than the framework's tolerance and the stream has been converted to signed 16-bit samples.

## Risks and Edge Cases

The converter is deliberately basic, not high-quality audio resampling. It assumes byte-aligned S16 channel areas and matching channel counts. Bad frame-count calculations can create buffer underruns in the chain. Fractional position and saved samples must reset on prepare to avoid carrying old audio across stream restarts.

## Test Signals

Test OSS playback/capture at rates that require upsampling and downsampling, including multi-channel streams, disabled-channel paths, repeated prepare/start cycles, and small period sizes that stress frame-count rounding.
