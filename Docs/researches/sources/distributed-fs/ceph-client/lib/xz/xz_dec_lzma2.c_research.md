# sources/distributed-fs/ceph-client/lib/xz/xz_dec_lzma2.c

## Purpose
Implements raw LZMA2 decompression and optional MicroLZMA decoding for the kernel XZ decoder, covering dictionary management, range decoding, LZMA probability models, chunk control parsing, and allocation modes.

## APIs and control flow
Internal APIs are `xz_dec_lzma2_create`, `xz_dec_lzma2_reset`, `xz_dec_lzma2_run`, and `xz_dec_lzma2_end`; MicroLZMA adds allocation/reset/run/end APIs under config. State structures include `dictionary`, `rc_dec`, `lzma_len_dec`, `lzma_dec`, `lzma2_dec`, and `xz_dec_lzma2`. `xz_dec_lzma2_run` walks states for control byte, sizes, properties, range-coder preparation, LZMA run, or uncompressed copy. `lzma_main` decodes literals and matches; `dict_repeat` validates match distances; `lzma2_lzma` stages boundary input so the core can safely read up to `LZMA_IN_REQUIRED` bytes.

## State, dependencies, and integration
State persists per decoder across multi-call input: dictionary positions, probability arrays, recent match distances, range coder state, chunk counters, and temp bytes. `XZ_SINGLE` points the dictionary at caller output, `XZ_PREALLOC` uses a fixed `dict_max`, and `XZ_DYNALLOC` grows up to stream requirements. It is called by `xz_dec_stream.c` directly or through BCJ.

## Risks and test signals
Risks are malformed control bytes, invalid dictionary distances, range-coder boundary reads, size-counter mistakes, and large dictionary memory pressure. Tests should cover all chunk classes, resets/properties, max matches, invalid distances, truncation, tiny buffers, allocation modes, memory-limit failures, and MicroLZMA exact-size behavior.
