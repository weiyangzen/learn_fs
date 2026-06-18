<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.h

## Purpose
`zstd_compress_sequences.h` declares the private sequence entropy and bitstream encoding API for Zstd compression.

## Important APIs, Types, and Functions
It defines `ZSTD_DefaultPolicy_e` and declares `ZSTD_selectEncodingType()`, `ZSTD_buildCTable()`, `ZSTD_encodeSequences()`, `ZSTD_fseBitCost()`, and `ZSTD_crossEntropyCost()`.

## Control Flow
Callers count LL/ML/OF code frequencies, ask `ZSTD_selectEncodingType()` which encoding mode to use, call `ZSTD_buildCTable()` to write table metadata and prepare CTables, then call `ZSTD_encodeSequences()` with CTables, code arrays, sequence array, long-offset mode, and BMI2 mode.

## State and Persistence
The header owns no state. Its APIs operate on caller-provided FSE repeat modes, CTables, code tables, count arrays, and entropy workspaces. The resulting state persists in the next block's entropy tables and in the emitted sequence-section bytes.

## Dependencies and Integration Points
It includes `zstd_compress_internal.h` for `SeqDef`, `fse.h` for FSE tables/repeat modes, and `zstd_internal.h` for symbol encoding types and strategy. The header is consumed by sequence compression, block entropy building, and superblock compression.

## Risks
The API assumes frequency counts, max symbols, default norms, previous CTables, and workspace sizes are consistent. Passing a default table when defaults are disallowed, or a previous CTable that cannot encode the current symbol range, will lead to fallback/error paths in the implementation.

## Test Signals
Compile and runtime coverage should verify all declared paths through normal block compression, dictionary repeat-table reuse, superblock subblocks, long-offset blocks, and destination-capacity failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.h -->
