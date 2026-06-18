# sources/compression/zstd/lib/compress/huf_compress.c

## Purpose
`huf_compress.c` implements zstd's Huffman encoder for literals. It builds canonical Huffman compression tables, writes/reads table descriptions, estimates compressed sizes, validates repeat tables, and compresses data using either one bitstream or four independently compressed segments.

## Important APIs, Types, and Functions
Important exported functions include `HUF_writeCTable_wksp()`, `HUF_readCTable()`, `HUF_getNbBitsFromCTable()`, `HUF_buildCTable_wksp()`, `HUF_estimateCompressedSize()`, `HUF_validateCTable()`, `HUF_compressBound()`, `HUF_compress1X_usingCTable()`, `HUF_compress4X_usingCTable()`, `HUF_cardinality()`, `HUF_minTableLog()`, `HUF_optimalTableLog()`, `HUF_compress1X_repeat()`, and `HUF_compress4X_repeat()`. Internal types include `nodeElt`, `rankPos`, `HUF_CStream_t`, `HUF_CompressWeightsWksp`, `HUF_WriteCTableWksp`, and `HUF_compress_tables_t`.

## Control Flow, State, and Persistence
Workspace is caller-owned and aligned by `HUF_alignUpWorkspace()`. Table construction starts with a histogram from `hist.c`, sorts symbols by count with bucketed ranking plus per-bucket sorting, builds an unlimited-depth Huffman tree, enforces a maximum height through `HUF_setMaxHeight()`, then emits canonical values by rank. `HUF_writeCTable_wksp()` converts bit lengths to weights and tries FSE compression for the weight table, falling back to raw 4-bit weights. Encoding uses a custom high-bit-first `HUF_CStream_t`; symbols are encoded backwards, flushed with table-log-specific unroll choices, and closed with a one-bit end mark. The 4X path divides input into four segments, stores the first three compressed sizes as a 6-byte jump table, and compresses each segment with the 1X encoder.

## Dependencies and Integration Points
The file depends on zstd dependency macros, compiler helpers, bitstream/memory primitives, `hist.h`, static FSE APIs, `huf.h`, error handling, and `ZSTD_highbit32`. It integrates with zstd block compression through repeat-table state (`HUF_repeat`) and flags such as BMI2 dispatch, optimal-depth probing, prefer-repeat, and suspect-incompressible sampling. It also uses FSE to compress Huffman weights.

## Risks and Test Signals
Risks include canonical-code correctness, height-limiting edge cases, workspace sizing/alignment, destination-bound fast paths, repeat-table validation, and incompressibility heuristics returning zero. Tests should cover single-symbol RLE, tiny inputs, all-symbol alphabets, repeat table reuse/check/invalid transitions, 1X and 4X output round trips, optimal-depth probing, BMI2 and default dispatch, raw versus FSE-compressed table headers, and sanitizer coverage of tight destination buffers.
