# sources/compression/zstd/lib/legacy/zstd_v06.c

## Purpose
Implements the complete legacy Zstandard v0.6 decompression stack used when the main zstd library is built with legacy support. The file is intentionally self-contained: it embeds low-level memory helpers, bitstream decoding, Finite State Entropy decoding, Huffman decoding, v0.6 frame/block decompression, dictionary loading, direct streaming, and buffered streaming wrappers.

This is decompression-only code for frames identified by `ZSTDv06_MAGICNUMBER` (`0xFD2FB526`). Current decompression paths do not call it directly; `zstd_legacy.h` detects the v0.6 magic, exposes legacy size helpers, allocates v0.6 contexts, and routes one-shot or streaming work into the APIs defined here.

## Important APIs, Types, And Functions
Public APIs implemented for callers of `zstd_v06.h` include `ZSTDv06_decompress()`, `ZSTDv06_decompressDCtx()`, `ZSTDv06_decompress_usingDict()`, `ZSTDv06_getFrameParams()`, `ZSTDv06_findFrameSizeInfoLegacy()`, `ZSTDv06_createDCtx()`, `ZSTDv06_freeDCtx()`, `ZSTDv06_decompressBegin_usingDict()`, `ZSTDv06_copyDCtx()`, `ZSTDv06_nextSrcSizeToDecompress()`, `ZSTDv06_decompressContinue()`, and the buffered `ZBUFFv06_*` decompression API. Hidden/static-linkage style declarations inside the file also expose `ZSTDv06_decompressBegin()`, `ZSTDv06_decompressBlock()`, `ZSTDv06_decompress_usingPreparedDCtx()`, and `ZSTDv06_sizeofDCtx()`.

`struct ZSTDv06_DCtx_s` is the central direct decompression state. It stores literal-length, match-length, and offset FSE decode tables; an X4 Huffman table for repeat-table literals; rolling history pointers (`previousDstEnd`, `base`, `vBase`, `dictEnd`); current frame parameters; direct streaming stage and expected input size; the current block type; repeat-table state; literal pointers and literal buffer; and a frame header buffer.

`struct ZBUFFv06_DCtx_s` wraps a `ZSTDv06_DCtx` for size-flexible streaming. It tracks its own stage machine, header accumulation, input buffer, output ring-like buffer, output flush cursors, and block size derived from the decoded frame window.

Important internal helpers are grouped by codec layer:
- MEM helpers (`MEM_readLE16/32/64`, `MEM_readLEST`, endian tests, swaps) provide unaligned little-endian access.
- BIT helpers (`BITv06_initDStream`, `BITv06_readBits`, `BITv06_reloadDStream`) read compressed entropy streams backwards.
- FSE helpers (`FSEv06_readNCount`, `FSEv06_buildDTable`, `FSEv06_decompress_usingDTable`) decode normalized-count tables and sequence tables.
- HUF helpers (`HUFv06_readStats`, `HUFv06_readDTableX2/X4`, `HUFv06_decompress1X2/4X2/1X4/4X4`) decode compressed literal sections.
- ZSTD helpers parse frame and block headers (`ZSTDv06_frameHeaderSize`, `ZSTDv06_getcBlockSize`), literal blocks (`ZSTDv06_decodeLiteralsBlock`), sequence headers (`ZSTDv06_decodeSeqHeaders`), sequence bodies (`ZSTDv06_decodeSequence`), and LZ match/literal execution (`ZSTDv06_execSequence`).

The file declares but does not define `ZSTDv06_compressBound()`, even though the public header declares it. It also declares FSE/HUF compress-bound prototypes but implements no compression path. In this repository the file is used as a decoder implementation, so any new link target expecting the compress-bound symbol from this translation unit would fail.

## Control Flow
One-shot decompression starts in `ZSTDv06_decompress()`. In heap mode it allocates a `ZSTDv06_DCtx`, calls `ZSTDv06_decompressDCtx()`, and frees the context. `ZSTDv06_decompressDCtx()` delegates to `ZSTDv06_decompress_usingDict()` with no dictionary. Dictionary mode initializes context state, optionally loads dictionary entropy and references dictionary content, checks output continuity, and calls `ZSTDv06_decompressFrame()`.

Frame decompression parses the frame header, validates the v0.6 magic and reserved descriptor bit, derives `windowLog` and optional frame content size, then loops over 3-byte block headers. Compressed blocks go through `ZSTDv06_decompressBlock_internal()`, raw blocks are copied, end blocks terminate the frame, and RLE blocks currently return a generic error. Block headers encode type in the top two bits and compressed size in the remaining header bits.

Compressed block flow is literal-section decode followed by sequence-section decode. Literal sections can be Huffman-compressed, precomputed-Huffman (`IS_PCH`), raw, or RLE. Huffman and RLE literals are materialized in `dctx->litBuffer`; raw literals may reference the compressed input directly unless padding/overread safety requires a copy. Sequence headers decode `nbSeq` and build or reuse the LL, offset, and ML FSE tables. Sequence payloads initialize three FSE states over a backwards bitstream, decode literal length, match length, and offset codes, update repeat offsets, then execute each sequence into the destination. Final remaining literals are copied after all sequences.

`ZSTDv06_execSequence()` is the LZ copy hot path. It validates literal availability and output capacity, wild-copies literals, resolves match offsets either in the current prefix or an external dictionary, handles matches spanning dictionary and prefix, and uses special small-offset tables to make overlapping copies efficient.

Direct streaming is a strict state machine driven by exact input sizes. `ZSTDv06_decompressBegin()` sets `expected` to the 5-byte minimum frame header and stage `ZSTDds_getFrameHeaderSize`. Callers alternate `ZSTDv06_nextSrcSizeToDecompress()` and `ZSTDv06_decompressContinue()`. The continue function accepts exactly `expected` bytes, accumulates or decodes the frame header, reads block headers, then decodes exactly one block payload. A complete frame resets the stage and sets `expected` to zero.

Buffered streaming (`ZBUFFv06_decompressContinue()`) adapts arbitrary input/output sizes to the exact-size direct API. It accumulates frame headers, sizes input/output buffers from `windowLog`, feeds direct decompression from caller input when possible or from its internal input buffer otherwise, and flushes decoded blocks from `outBuff` according to caller output capacity. Its return value is a hint for the next preferred input size, adjusted for partially loaded data.

## State And Persistence Behavior
All state is in caller-owned heap contexts or stack contexts. There is no filesystem, global mutable, or cross-process persistence. Public `create`/`free` functions allocate with `malloc()`/`free()`, and `ZBUFFv06_freeDCtx()` also releases owned input/output buffers.

`ZSTDv06_DCtx` persists entropy tables, repeat-table availability, dictionary references, and rolling output history across blocks and streaming calls. It does not own dictionary memory; dictionary content is referenced by pointer, so callers must keep dictionary memory alive for the whole decompression operation. `ZSTDv06_copyDCtx()` copies the prepared dictionary/entropy portion of a context while intentionally skipping large work buffers.

`ZBUFFv06_DCtx` may retain allocated buffers across reinitialization and grows them when a larger `windowLog` requires it. Its buffered output cursor can keep decoded-but-unflushed bytes between calls. After a frame completes, it returns to `ZBUFFds_init`, requiring a new init call for another operation.

The direct context uses `previousDstEnd`, `base`, `vBase`, and `dictEnd` to detect contiguous output and to model external dictionary or previous-prefix history. If the caller provides non-contiguous destination buffers in direct mode, `ZSTDv06_checkContinuity()` converts the old prefix into an external dictionary segment.

## Dependencies And Integration Points
This file includes `zstd_v06.h`, standard C headers, `../common/compiler.h`, and `../common/error_private.h`. Error handling is through the repository's `ERROR(...)`, `ERR_isError()`, and `ERR_getErrorName()` conventions, so public APIs return `size_t` error codes compatible with the rest of zstd.

The main integration point is `sources/compression/zstd/lib/legacy/zstd_legacy.h`. That dispatcher includes `zstd_v06.h`, recognizes `ZSTDv06_MAGICNUMBER`, uses `ZSTDv06_getFrameParams()` for legacy decompressed-size discovery, calls `ZSTDv06_decompress_usingDict()` for one-shot legacy decode, calls `ZSTDv06_findFrameSizeInfoLegacy()` for frame size/bound discovery, and maps streaming v0.6 contexts to `ZBUFFv06_createDCtx()`, `ZBUFFv06_decompressInitDictionary()`, `ZBUFFv06_decompressContinue()`, and `ZBUFFv06_freeDCtx()`.

The current decompressor integrates legacy support from `decompress/zstd_decompress.c` and `decompress/zstd_ddict.c` through `zstd_legacy.h`. Static decompression contexts are incompatible with legacy streaming in the surrounding code because legacy contexts allocate their own heap state.

The v0.6 decoder embeds historical FSE/HUF code instead of using current shared entropy modules, which isolates old format behavior but duplicates security-sensitive bitstream and table-building logic.

## Risks And Edge Cases
This code parses untrusted compressed input with extensive pointer arithmetic, backwards bitstreams, wild-copy routines that intentionally over-copy within guarded bounds, and large stack tables. It has many corruption checks, but its legacy and monolithic nature makes it high-risk for maintenance changes.

RLE data block support is explicitly missing in both one-shot and direct streaming frame block handling: `bt_rle` returns `ERROR(GENERIC)`. Literal RLE inside compressed blocks is supported, but whole-frame RLE blocks are not.

`ZSTDv06_findFrameSizeInfoLegacy()` reports decompressed bound as `nbBlocks * ZSTDv06_BLOCKSIZE_MAX`, not the exact frame content size. It does not decode or trust the optional content-size field for this bound. This is acceptable as a bound helper but can overestimate substantially.

Dictionary handling has ownership and bounds risks. Pure-content dictionaries are referenced directly; formatted dictionaries require a v0.6 dictionary magic and embedded HUF/FSE tables. Malformed entropy headers return `dictionary_corrupted`, but callers must still respect dictionary lifetime.

The public header advertises `ZSTDv06_compressBound()`, but this file has no implementation for it. Any build path that exposes the header and expects that symbol from the legacy decoder object would see a link failure.

Some APIs assume non-NULL parameters by contract. For example, `ZSTDv06_findFrameSizeInfoLegacy()` assumes `cSize` and `dBound` are not NULL, and several decompression entry points assume valid context pointers.

## Test Signals
Useful test coverage includes v0.6 legacy frames with every supported frame content size encoding, unknown content size, invalid magic, reserved frame descriptor bit, truncated frame headers, truncated block headers, compressed blocks with HUF, raw, RLE literal sections, precomputed-Huffman literals from dictionaries, empty sequence sections, long sequence counts, repeat offsets, external dictionary matches, and non-contiguous direct streaming output.

Streaming tests should exercise exact-size direct calls via `ZSTDv06_nextSrcSizeToDecompress()`, arbitrary chunking through `ZBUFFv06_decompressContinue()`, small destination buffers that force partial flushes, frame completion returning hint zero, missing initialization returning `init_missing`, and dictionary initialization reuse.

Integration tests should enter through modern legacy dispatch (`ZSTD_decompressLegacy()` and `ZSTD_decompressLegacyStream()` in `zstd_legacy.h`) rather than only calling `ZSTDv06_*` directly, because the real production path depends on magic-number detection and legacy context allocation.

Negative tests should include malformed FSE normalized counts, Huffman stats with invalid weights, block sizes beyond remaining input, offsets beyond prefix/dictionary history, whole-block RLE frames, and 32-bit window-log rejection paths.
