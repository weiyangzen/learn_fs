# sources/distributed-fs/ceph-client/sound/core/oss/io.c

## Purpose
`io.c` implements the terminal OSS PCM I/O plugin. It bridges plugin-channel buffers to actual OSS PCM read and write helpers for playback and capture.

## Important APIs, Types, and Functions
Macros map local calls to `snd_pcm_oss_write3()`, `snd_pcm_oss_writev3()`, `snd_pcm_oss_read3()`, and `snd_pcm_oss_readv3()`. `io_playback_transfer()` writes interleaved or vector channel data. `io_capture_transfer()` reads into interleaved or vector channel buffers. `io_src_channels()` prepares client channels for interleaved playback. `snd_pcm_plugin_build_io()` builds the `"I/O io"` plugin and selects transfer callbacks based on stream direction.

## Control Flow and State
The builder extracts format/rate/channels/access from hardware params, allocates extra per-channel pointer storage, and records access mode. Playback transfer writes `src_channels->area.addr` for interleaved access; for noninterleaved access it fills the extra pointer array with enabled channel addresses or NULL and calls writev. Capture mirrors this into destination channel buffers. Interleaved playback source channels are marked wanted.

## Dependencies and Integration Points
It depends on OSS PCM read/write helpers, PCM hw params accessors, and plugin infrastructure. It is the boundary between conversion plugins and the real OSS PCM substream.

## Risks and Test Signals
Risks include mismatched source/destination channel counts, NULL vector entries for disabled channels, and wrong access mode selection. Tests should cover playback and capture, interleaved and noninterleaved access, disabled channels, short reads/writes, and hardware parameter combinations.
