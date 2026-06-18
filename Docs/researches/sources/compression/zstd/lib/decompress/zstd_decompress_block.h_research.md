# sources/compression/zstd/lib/decompress/zstd_decompress_block.h

## Purpose
`zstd_decompress_block.h` is the internal interface for compressed-block decompression. It exposes the block decoder and FSE table builder to frame-level decompression and dictionary-loading code while keeping implementation details in `zstd_decompress_block.c`.

## Important APIs, Types, And Functions
The header defines `streaming_operation` with `not_streaming` and `is_streaming`, declares `ZSTD_decompressBlock_internal()`, declares `ZSTD_buildFSETable()`, and declares `ZSTD_decompressBlock_deprecated()` as the internal wrapper behind the deprecated public block API. It also documents that `ZSTD_decompressBlock()`, `ZSTD_getcBlockSize()`, and `ZSTD_decodeSeqHeaders()` are published elsewhere.

## Control Flow
There is no runtime control flow in the header. It determines how callers distinguish streaming from non-streaming literal-buffer allocation and gives frame decompression a single entry point for `bt_compressed` blocks.

## State And Persistence
The declared functions operate on `ZSTD_DCtx`; state is held by the context and by caller-owned buffers. The header itself contains no persistent state.

## Dependencies And Integration Points
It includes zstd dependency definitions, public `zstd.h`, common internal block types, and `zstd_decompress_internal.h` for `ZSTD_seqSymbol`. It is included by `zstd_decompress.c` and `zstd_decompress_block.c`, and `ZSTD_buildFSETable()` is also used when dictionaries load their precomputed entropy tables.

## Risks
Changing the `streaming_operation` contract can break literal placement and streaming history safety. Changing prototypes affects internal ABI expectations across decompression and dictionary modules. Workspace sizing for `ZSTD_buildFSETable()` must remain consistent with `ZSTD_BUILD_FSE_TABLE_WKSP_SIZE`.

## Test Signals
Compile coverage is the main direct signal. Behavioral signals come from frame decompression, dictionary-loading tests, block API tests, and streaming tests that exercise both `is_streaming` and `not_streaming` paths.
