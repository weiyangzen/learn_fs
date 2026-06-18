# sources/distributed-fs/ceph-client/sound/core/pcm_iec958.c

## Purpose

`pcm_iec958.c` creates and fills consumer IEC958/S/PDIF channel-status bytes from ALSA PCM runtime or hardware parameters. It gives drivers a small helper layer for default status generation plus rate and word-length completion.

## Important APIs, Types, and Functions

Exported functions are `snd_pcm_create_iec958_consumer_default()`, `snd_pcm_fill_iec958_consumer()`, `snd_pcm_fill_iec958_consumer_hw_params()`, `snd_pcm_create_iec958_consumer()`, and `snd_pcm_create_iec958_consumer_hw_params()`. `fill_iec958_consumer()` maps PCM rates and sample widths into IEC958 AES status bits when the caller left those fields unspecified.

## Control Flow

Default creation validates a minimum four-byte buffer, clears it, and fills consumer, no-copyright, no-emphasis, general category, unspecified source/channel, 1000 ppm clock, and unknown sample-rate/word-length markers. Fill helpers then replace the unspecified sample-rate field for supported rates from 32 kHz through 192 kHz and optionally replace byte-four word-length bits for 16, 18, 20, 24, or 32-bit PCM. Create helpers perform default creation followed by fill.

## State and Persistence Behavior

All state is caller-owned in the `u8 *cs` channel-status buffer. The helpers intentionally preserve fields already specified by the caller and only fill `NOTID` rate or word-length values. There is no global or runtime-persistent state.

## Dependencies and Integration Points

The file depends on IEC958 AES bit definitions, ALSA PCM runtime/hw-param helpers, and exported kernel symbols for use by PCM and digital audio drivers. Runtime variants read `runtime->rate` and `runtime->format`; hw-param variants read `params_rate()` and `params_width()`.

## Risks and Edge Cases

Buffers shorter than four bytes are invalid, and word-length filling only occurs when a fifth byte is present. Unsupported rates or widths return `-EINVAL`. The helper treats 32-bit samples as 24-bit IEC958 word length, matching common S/PDIF packing assumptions.

## Test Signals

Validate default buffer contents, fill behavior for each supported sample rate and width, preservation of prefilled status bits, short-buffer rejection, unsupported rate/width rejection, and use from both runtime and hw-param based driver paths.
