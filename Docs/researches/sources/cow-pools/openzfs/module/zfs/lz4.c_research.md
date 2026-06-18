# File Research: sources/cow-pools/openzfs/module/zfs/lz4.c

## Role

`lz4.c` provides the modern LZ4 block decompressor used by OpenZFS. The file is BSD-2-Clause LZ4 code, noted as unmodified code from LZ4 1.9.3's decompressor plus compatibility macros/constants so it can satisfy the legacy `LZ4_uncompress_unknownOutputSize()` symbol expected by the OpenZFS LZ4 wrapper.

This file does not implement OpenZFS compression registration itself. Its exported integration point is the decompression routine called by `lz4_zfs.c`'s ZFS decompression wrapper.

## Public Interface

- `int LZ4_uncompress_unknownOutputSize(const char *source, char *dest, int compressedSize, int maxDecompressedSize)` is the only externally visible function in this file.
- The wrapper flattens upstream's current `LZ4_decompress_safe()` path by directly calling `LZ4_decompress_generic()` with `endOnInputSize`, `decode_full_block`, `noDict`, `lowPrefix = dest`, no external dictionary, and dictionary size zero.
- Return semantics are inherited from safe LZ4 decompression: nonnegative decoded byte count on success, negative value on malformed input or output-limit failure.

## Implementation Structure

The file starts with portability and tuning definitions: `COMPRESSIONLEVEL`, `NOTCOMPRESSIBLE_CONFIRMATION`, endian detection via `_ZFS_BIG_ENDIAN`, memory-access mode selection, forced software bitcount on illumos, `restrict` disabling, compiler version normalization, branch prediction macros, and optional ppc64le `-O2` annotations to avoid decompression regressions.

It defines LZ4 block constants and types, including match/literal bit widths, `MINMATCH`, `LASTLITERALS`, `MFLIMIT`, `MATCH_SAFEGUARD_DISTANCE`, `FASTLOOP_SAFE_DISTANCE`, and `LZ4_DISTANCE_MAX`. Memory access helpers use built-in `memcpy` when possible, packed unaligned access when selected, or portable `memcpy` reads otherwise. `LZ4_readLE16()` normalizes little-endian offset reads.

The core decompressor is `LZ4_decompress_generic()`. It is parameterized by:

- End condition: stop on output size or input size.
- Early-end mode: full-block or partial decode.
- Dictionary mode: no dictionary, prefix, external dictionary, or dictionary context.
- Low-prefix/dictionary pointers and dictionary size.

OpenZFS uses the safe full-block, end-on-input, no-dictionary instantiation.

## Decompression Flow

`LZ4_decompress_generic()` validates null source and negative output size, initializes input/output bounds, and handles empty source/output special cases. If `LZ4_FAST_DEC_LOOP` is enabled and enough output room remains, it enters a fast loop that decodes common literal/match sequences using 16- or 32-byte wild copies guarded by distance and end checks.

Both fast and safe paths follow the LZ4 block format:

- Read a token and split it into literal length and match length nibbles.
- Extend lengths through repeated `255` bytes using `read_variable_length()`.
- Copy literals from input to output while checking input and output parsing restrictions.
- Read the 16-bit little-endian match offset.
- Validate match offset against the current block or dictionary prefix.
- Copy the match, using special overlap handling for short offsets and safe byte-by-byte copying near the output end.
- Require the final sequence to satisfy LZ4's end-of-block restrictions, especially the trailing literal requirement.

Any malformed stream, invalid offset, integer overflow, input overrun, or output overrun jumps to `_output_error` and returns a negative source-position-derived error.

## State And Dependencies

The decompressor is stateless across calls. It depends on `sys/zfs_context.h` for kernel/userland compatibility definitions such as `ASSERT`, `MIN`, `MEM_INIT` backing functions, and standard integer/memory facilities in non-kernel builds.

There is no OpenZFS-specific allocation, lock, cache, or global state in this file. Its ABI dependency is the legacy LZ4 symbol name consumed by `lz4_zfs.c`.

## Risks And Invariants

Callers must pass the exact compressed byte count and maximum decompressed block size. OpenZFS's wrapper enforces exact output length after this routine returns, so a short successful decode is treated as a ZFS decompression failure by the caller.

The file is performance-sensitive and heavily macro-driven. Correctness depends on preserving the LZ4 parsing restrictions, overflow checks, offset validation, and special overlapping-copy cases. Seemingly local changes to memory-access macros or fast-copy bounds can affect kernel safety on alignment-sensitive architectures.
