# sources/distributed-fs/ceph-client/lib/lz4/lz4_decompress.c

## Purpose
`lz4_decompress.c` implements the kernel LZ4 block decompressor. It provides safe, partial, fast, dictionary-backed, and streaming decode entry points over one shared inlined decoder. It is the defensive side of the LZ4 implementation used by crypto, filesystems, and boot-time decompression paths.

## Important APIs, types, and functions
Public exports are `LZ4_decompress_safe()`, `LZ4_decompress_safe_partial()`, `LZ4_decompress_fast()`, `LZ4_setStreamDecode()`, `LZ4_decompress_safe_continue()`, `LZ4_decompress_fast_continue()`, `LZ4_decompress_safe_usingDict()`, and `LZ4_decompress_fast_usingDict()`. `LZ4_decompress_generic()` is the main engine and is parameterized by `endCondition_directive`, `earlyEnd_directive`, and `dict_directive` from `lz4defs.h`. Private wrappers instantiate prefix, small-prefix, external-dictionary, and double-dictionary cases. Streaming state is `LZ4_streamDecode_t_internal`, carrying `prefixEnd`, `prefixSize`, `externalDict`, and `extDictSize`.

## Control flow
The generic decoder reads a token, decodes literal length, copies literals, reads the match offset, decodes match length, and copies match bytes until the block ends. It has a fast shortcut for common small literal and match lengths when input and output have enough slack. In safe mode it validates input consumption, output capacity, offset lookbehind, and arithmetic overflow. Partial mode can stop after filling the requested target output. Dictionary handling splits matches into prefix-only, external-dictionary-only, and dictionary-plus-current-block copies. Streaming decode chooses a path based on whether `dest` directly follows the previous prefix, whether a small prefix or external dictionary is active, or whether the ring buffer/wrapped buffer requires double-dictionary mode.

## State and persistence
One-shot decode is stateless. Streaming decode persists only the location and size of the previous decoded prefix and, when buffers move, the external dictionary range. The implementation does not copy dictionary bytes itself; callers must keep prior decoded data or an explicitly supplied dictionary readable for the next block. Return values are decoded byte counts for safe modes, bytes read for fast modes, or negative error positions for malformed input.

## Dependencies and integration points
The file depends on `lz4defs.h`, `linux/lz4.h`, unaligned little-endian reads, `LZ4_wildCopy()`, `LZ4_copy8()`, and kernel module exports. It is reached from `crypto/lz4.c`, `crypto/lz4hc.c`, `lib/decompress_unlz4.c`, and filesystem wrappers. `#ifndef STATIC` allows inclusion-style builds to avoid module export boilerplate.

## Risks and test signals
The critical risk surface is malicious compressed input. Safe paths must reject input overrun, output overrun, invalid lookbehind offsets, invalid final literals, and size overflows. Fast paths deliberately trust the compressed stream and should be used only when the compressed data and original size are trusted. Dictionary tests should cover prefix, small-prefix, external-dictionary, and double-dictionary cases. Good signals include exact output lengths, negative returns for malformed blocks, partial decode stopping at target capacity, in-place/overlap literal behavior, and cross-checking data compressed by both fast and HC compressors.
