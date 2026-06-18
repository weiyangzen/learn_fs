<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.c

## Purpose
`zstd_compress_superblock.c` implements target-compressed-block-size support. It takes one compressor block's sequence store and entropy statistics, splits it into several compressed Zstd subblocks around `targetCBlockSize`, and falls back to raw blocks when subblock compression is not beneficial or would violate entropy/header contracts.

## Important APIs, Types, and Functions
The exported entry point is `ZSTD_compressSuperBlock()`. Key internal functions include `ZSTD_compressSubBlock_literal()`, `ZSTD_seqDecompressedSize()`, `ZSTD_compressSubBlock_sequences()`, `ZSTD_compressSubBlock()`, `ZSTD_estimateSubBlockSize_literal()`, `ZSTD_estimateSubBlockSize_sequences()`, `ZSTD_estimateSubBlockSize()`, `ZSTD_needSequenceEntropyTables()`, `countLiterals()`, `sizeBlockSequences()`, and `ZSTD_compressSubBlock_multi()`. `EstimatedBlockSize` carries estimated literal and total block sizes.

## Control Flow
`ZSTD_compressSuperBlock()` first calls `ZSTD_buildBlockEntropyStats()` over the whole block, producing next entropy tables plus metadata. `ZSTD_compressSubBlock_multi()` estimates full-block compressed size, computes average literal and sequence costs, derives a subblock count from `targetCBlockSize`, and chooses sequence ranges with `sizeBlockSequences()`. Each subblock writes a Zstd block header, literal section, and sequence section through `ZSTD_compressSubBlock()`. Literal entropy is written only once when needed, and following subblocks use repeat/treeless forms. Sequence entropy is written on the first successful compressed subblock, then repeat mode is used. Failed or non-beneficial subblocks are coalesced or, at the end, emitted raw.

## State and Persistence
The function mutates `zc->blockState.nextCBlock->entropy` and possibly its repeat offsets. It consumes `zc->seqStore` arrays but does not own them. It tracks local pointers into literals, sequences, LL/ML/OF code tables, input, and output so partial compressed and raw subblocks still cover the original block in order.

## Dependencies and Integration Points
The file depends on common block constants, histogram counting, sequence cost helpers, literal helpers, and internal context structures. It is used when `ZSTD_CCtx_params.targetCBlockSize` requests bounded compressed block sizes. It integrates with old-decoder compatibility checks for small FSE NCount/bitstream combinations and tiny repeat-mode sequence bodies.

## Risks
The split heuristic is estimate-driven and can coalesce or raw-fallback when estimates are wrong. It must preserve entropy table contracts: if table metadata says new sequence entropy must be emitted but no subblock writes it, compression must fail back to raw. Literal header sizing can be guessed too small when entropy is included. If some input tail is raw-emitted after skipped sequences, repeat offsets must be regenerated from committed sequences to keep the next block correct.

## Test Signals
Tests should cover target sizes below, near, and above normal block compressed sizes; no-sequence blocks; many-sequence blocks; first/last subblock boundaries; entropy tables written once then repeated; raw fallback for incompressible data; decoder compatibility guards; repcode regeneration after partial raw tail; destination-too-small errors; and round trips with dictionaries and large windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.c -->
