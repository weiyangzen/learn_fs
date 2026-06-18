# sources/distributed-fs/ceph-client/sound/core/oss/mulaw.c

## Purpose
`mulaw.c` implements an OSS PCM plugin for converting between Mu-Law encoded samples and linear PCM formats. It supports both encode and decode directions while preserving rate and channel count.

## Important APIs, Types, and Functions
Low-level conversion helpers are `val_seg()`, `linear2ulaw()`, and `ulaw2linear()`. `struct mulaw_priv` stores the chosen conversion function plus endian, offset, byte-count, and signedness flip settings. `mulaw_encode()` converts native linear samples to Mu-Law; `mulaw_decode()` converts Mu-Law bytes to native linear samples; `mulaw_transfer()` dispatches the selected direction. `snd_pcm_plugin_build_mulaw()` validates formats, chooses encode/decode direction, initializes private data, and installs the transfer callback.

## Control Flow and State
The builder requires equal rates and channel counts. If destination format is `SNDRV_PCM_FORMAT_MU_LAW`, it encodes from source linear format; if source is Mu-Law, it decodes to destination linear format. Transfer validates byte-aligned channel areas in debug builds, clamps frames to destination availability, and iterates channel/frame buffers. Decode maps each Mu-Law byte to signed 16-bit linear and writes it into the native destination format with endian and unsigned conversion. Encode reads native samples into signed 16-bit form and produces one Mu-Law byte per frame.

## Dependencies and Integration Points
It depends on PCM format helpers, OSS plugin infrastructure, and the reference Mu-Law companding algorithm. It is linked into OSS PCM emulation only when plugin support is configured.

## Risks and Test Signals
Risks include signedness flipping for unsigned native formats, endian offset mistakes for packed samples, and clipping/segment behavior around Mu-Law boundaries. Tests should round-trip known Mu-Law vectors, encode/decode all supported linear widths/endians, verify disabled-channel silence behavior, and compare against standard Mu-Law reference values.
