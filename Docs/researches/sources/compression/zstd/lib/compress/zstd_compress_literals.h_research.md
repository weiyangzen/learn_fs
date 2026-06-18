# sources/compression/zstd/lib/compress/zstd_compress_literals.h

## Purpose
Declares the private literal-section compression API used inside zstd's compression library. It exposes raw, RLE, and Huffman/repeat literal compression entry points to block and superblock encoders.

## Important APIs, Types, And Functions
The header declares `ZSTD_noCompressLiterals()`, `ZSTD_compressRleLiteralsBlock()`, and `ZSTD_compressLiterals()`. The full compression API accepts previous and next `ZSTD_hufCTables_t`, a `ZSTD_strategy`, an entropy workspace, literal compression mode controls, a suspect-uncompressible hint, and a BMI2 flag. The comments document key preconditions: RLE input must contain one repeated byte and the entropy workspace must be 4-byte aligned and at least `HUF_WORKSPACE_SIZE`.

## Control Flow
The header is declarative. Callers choose the raw helper when literals must be stored uncompressed, the RLE helper when a single repeated byte is known, or `ZSTD_compressLiterals()` when the implementation should choose compressed, repeat, RLE, or raw output based on strategy and profitability.

## State And Persistence
No state is stored in the header. The API makes Huffman-table persistence explicit through `prevHuf` and `nextHuf`, allowing block-to-block repeat-mode reuse.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` for `ZSTD_hufCTables_t`, `ZSTD_minGain()`, `ZSTD_strategy`, and shared error/types. It is consumed by normal block compression and `zstd_compress_superblock.c`.

## Risks And Edge Cases
The risk is caller misuse of preconditions: insufficient destination capacity for RLE/raw headers, misaligned or undersized workspaces, or incorrect `prevHuf`/`nextHuf` lifetime. Because this is a private header, ABI stability is less important than keeping all internal callers synchronized with the implementation.

## Test Signals
Compile coverage across modules is the first signal. Runtime tests should exercise each declared function through block compression, including raw fallback, RLE literals, compressed literals, and repeat-Huffman reuse.
