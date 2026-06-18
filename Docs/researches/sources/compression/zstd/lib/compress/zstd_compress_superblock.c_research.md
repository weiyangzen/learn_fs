# sources/compression/zstd/lib/compress/zstd_compress_superblock.c

## Purpose
Implements target-compressed-block-size support by compressing one logical zstd block as a superblock split into multiple zstd sub-blocks. It reuses a single set of entropy statistics across sub-blocks, writes entropy tables once, emits later sub-blocks in repeat mode, and falls back to uncompressed output when splitting cannot satisfy compression or compatibility constraints.

## Important APIs, Types, And Functions
The public entry point is `ZSTD_compressSuperBlock()`. Internal literal and sequence emitters are `ZSTD_compressSubBlock_literal()` and `ZSTD_compressSubBlock_sequences()`. `ZSTD_compressSubBlock()` assembles one compressed zstd block from literal and sequence sections and writes the block header. `ZSTD_compressSubBlock_multi()` estimates split points, compresses sub-blocks, writes a raw tail when needed, and maintains entropy/repcodes.

Sizing helpers include `ZSTD_seqDecompressedSize()`, `ZSTD_estimateSubBlockSize_literal()`, `ZSTD_estimateSubBlockSize_symbolType()`, `ZSTD_estimateSubBlockSize_sequences()`, `ZSTD_estimateSubBlockSize()`, `ZSTD_needSequenceEntropyTables()`, `countLiterals()`, and `sizeBlockSequences()`. `EstimatedBlockSize` holds estimated literal and full block sizes.

## Control Flow
`ZSTD_compressSuperBlock()` first calls `ZSTD_buildBlockEntropyStats()` over the full sequence store to produce next entropy tables and metadata. It then delegates to `ZSTD_compressSubBlock_multi()`.

`ZSTD_compressSubBlock_multi()` estimates the full compressed size. If the full estimate is larger than the source size, it bails out with 0 so the caller can emit a raw block. Otherwise it derives average literal and sequence costs, estimates the number of sub-blocks, and repeatedly chooses sequence counts with `sizeBlockSequences()`. Each non-final sub-block is compressed only if its compressed size is non-zero and smaller than its decompressed size; otherwise the candidate is coalesced with following data. The final sub-block is compressed similarly with the caller's `lastBlock` flag.

Literal entropy is written only when the superblock's Huffman metadata requires a new table. Sequence entropy starts as required for the first compressed sub-block, and later sub-blocks use `set_repeat`. If required entropy was never actually written, the function restores previous Huffman state or returns 0 to force raw output. If some source remains after compressed sub-blocks, it writes that suffix with `ZSTD_noCompressBlock()` and recomputes repeat offsets for the subset of sequences actually emitted.

## State And Persistence
The function consumes `zc->seqStore`, `zc->blockState.prevCBlock`, `zc->blockState.nextCBlock`, `zc->appliedParams`, `zc->tmpWorkspace`, and `zc->bmi2`. It mutates `nextCBlock->entropy` during entropy-stat building and may restore `nextCBlock->entropy.huf` from the previous block if literal entropy was not emitted. It updates `nextCBlock->rep` when skipped sequences require repeat-code repair. The workspace is temporary.

## Dependencies And Integration Points
This file depends on common zstd block format helpers, `hist.h`, `zstd_compress_internal.h`, `zstd_compress_sequences.h`, and `zstd_compress_literals.h`. It integrates with the main compression path when `targetCBlockSize` is set. The output is a sequence of valid zstd blocks representing the input range, with only the last sub-block carrying the frame's last-block marker.

## Risks And Edge Cases
The highest-risk logic is entropy table emission across split sub-blocks. If a new table is selected but no compressed sub-block writes it, later repeat-mode blocks would be invalid, so the implementation forces fallback. Compatibility guards avoid old decoder bugs when sequence headers/bodies are too small. Literal header size is guessed before final compressed size is known; expansion beyond the guessed header width triggers raw literal fallback.

Split estimates are heuristic and can choose sub-blocks that do not compress; the code handles this by coalescing, but ratio and target size can vary. Recomputing repcodes after skipped sequences is subtle and must match `ZSTD_updateRep()` semantics. `ZSTD_seqDecompressedSize()` asserts literal accounting, so long-length handling through `ZSTD_getSequenceLength()` is required.

## Test Signals
Tests should enable `targetCBlockSize` across compressible, incompressible, mixed, and dictionary inputs; validate round trips; inspect that produced block sizes roughly follow target constraints; cover first-sub-block entropy, repeat-mode later sub-blocks, zero-sequence sub-blocks, raw tail fallback, and old-decoder compatibility guards. State tests should verify repeat offsets after partially compressed superblocks.
