<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.c

## Purpose
`zstd_compress_sequences.c` selects FSE encoding modes for sequence symbol streams, builds FSE compression tables, estimates repeat/default/compressed costs, and encodes sequences into the Zstd bitstream.

## Important APIs, Types, and Functions
Public-internal APIs are `ZSTD_selectEncodingType()`, `ZSTD_buildCTable()`, `ZSTD_encodeSequences()`, `ZSTD_fseBitCost()`, and `ZSTD_crossEntropyCost()`. Important helpers include `ZSTD_getFSEMaxSymbolValue()`, `ZSTD_useLowProbCount()`, `ZSTD_NCountCost()`, `ZSTD_entropyCost()`, `ZSTD_encodeSequences_body()`, `ZSTD_encodeSequences_default()`, and the optional BMI2 wrapper. `ZSTD_BuildCTableWksp` provides normalized-count and FSE build workspace.

## Control Flow
`ZSTD_selectEncodingType()` first handles RLE/basic single-symbol cases, then for fast strategies uses heuristics favoring repeat or default tables, and for lazy-or-better strategies estimates bit costs for default, repeat, and freshly compressed FSE tables. `ZSTD_buildCTable()` materializes the selected type: RLE writes one symbol byte, repeat copies the previous CTable, basic builds from default norms, and compressed normalizes counts, writes an NCount header, and builds a new CTable. `ZSTD_encodeSequences()` dispatches to BMI2 or default encoding, initializes final FSE states from the last sequence, writes extra bits and FSE symbols in reverse sequence order, then flushes the three states.

## State and Persistence
The file keeps only static lookup data for inverse probability costs. It mutates caller-owned FSE CTables and count arrays. Encoded persistence is the sequences section body: optional FSE table descriptions followed by a reverse-order bitstream whose interpretation depends on LL/ML/OF code tables and repeat/default state selected earlier.

## Dependencies and Integration Points
The file depends on `zstd_compress_sequences.h`, FSE APIs, bitstream APIs, default normalized distributions, LL/ML extra-bit tables, `SeqDef`, and CPU feature macros. It is used by block entropy construction and by `zstd_compress_superblock.c` to write each subblock's sequence section.

## Risks
The reverse bitstream has tight 32-bit vs 64-bit flush requirements. Long offsets require special splitting so the bit accumulator is not overfilled. Repeat-table use must reject tables that cannot represent active symbols or assign zero probability to used symbols. `ZSTD_buildCTable()` deliberately decrements the final symbol count in compressed mode when possible; mistakes there affect normalization and decoder compatibility.

## Test Signals
Tests should cover set_basic, set_rle, set_repeat, and set_compressed choices for LL/ML/OF streams; repeat table rejection; default table allowed/disallowed paths; low and high sequence counts around the low-probability heuristic; long offsets with large window logs; BMI2/non-BMI2 encoding; small destination buffers; and decode round trips for blocks with one, two, many, and maximum-code symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.c -->
