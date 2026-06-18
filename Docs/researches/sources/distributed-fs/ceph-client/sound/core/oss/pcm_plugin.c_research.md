# sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.c

## Purpose

`pcm_plugin.c` provides the shared OSS PCM plugin framework used by `pcm_oss.c` to adapt legacy OSS client streams to the actual ALSA hardware stream. It builds and runs ordered conversion chains for format conversion, mu-law conversion, channel routing, rate conversion, copy/deinterleave, and final I/O plugins.

## Important APIs, Types, and Functions

The key public helpers are `snd_pcm_plugin_build()`, `snd_pcm_plugin_free()`, `snd_pcm_plug_alloc()`, `snd_pcm_plug_client_size()`, `snd_pcm_plug_slave_size()`, `snd_pcm_plug_slave_format()`, `snd_pcm_plug_format_plugins()`, `snd_pcm_plug_client_channels_buf()`, `snd_pcm_plug_write_transfer()`, `snd_pcm_plug_read_transfer()`, `snd_pcm_area_silence()`, and `snd_pcm_area_copy()`. The framework operates on `struct snd_pcm_plugin` and `struct snd_pcm_plugin_channel` from `pcm_plugin.h`.

## Control Flow

`snd_pcm_plug_format_plugins()` compares client and slave formats, then appends plugins in the order needed for playback/capture: optional mu-law linearization, channel reduction, rate conversion through signed 16-bit, format conversion, channel extension, and interleaving conversion. `snd_pcm_plug_write_transfer()` walks the chain forward from `plugin_first`, allocating downstream channel buffers and invoking each plugin's `transfer()` callback. `snd_pcm_plug_read_transfer()` computes required source frames, then runs the same chain forward so captured driver data becomes OSS client data.

## State and Persistence Behavior

Plugin chain nodes are linked through `runtime->oss.plugin_first` and `plugin_last`. Each plugin owns optional scratch `buf`, `buf_frames`, `buf_channels`, private conversion data in `extra_data`, and an optional `private_free` callback. Scratch buffers are resized per period by `snd_pcm_plug_alloc()` and released through `snd_pcm_plugin_free()` when OSS params change or the substream closes.

## Dependencies and Integration Points

The framework depends on ALSA format helpers, OSS runtime plugin lists, and concrete plugin builders declared in `pcm_plugin.h`. `pcm_oss.c` decides when direct access is impossible, builds the chain, and calls transfer helpers during read/write.

## Risks and Edge Cases

Frame-count transforms must remain inverse enough for buffer sizing; a wrong `src_frames()` or `dst_frames()` result can underallocate scratch buffers or truncate audio. `snd_pcm_area_copy()` and `snd_pcm_area_silence()` assume byte-oriented areas except for special IMA ADPCM nibble handling. The framework caps plugin buffers at 1 MiB per period and rejects unsupported access patterns.

## Test Signals

Exercise OSS playback and capture where app format, hardware format, rate, channel count, and interleaving differ. Build coverage should include `CONFIG_SND_PCM_OSS_PLUGINS`; runtime coverage should confirm format fallback selection, mu-law conversion, noninterleaved hardware, and large-period rejection.
