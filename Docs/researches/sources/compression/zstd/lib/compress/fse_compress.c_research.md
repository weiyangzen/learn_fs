# sources/compression/zstd/lib/compress/fse_compress.c

## Purpose
`fse_compress.c` implements the Finite State Entropy encoder used by zstd for sequence-code streams and by Huffman header compression. It builds compression tables from normalized symbol counts, serializes normalized counts, chooses table logs, normalizes histograms, and encodes symbols into a reverse bitstream.

## Important APIs, Types, and Functions
Key exported functions are `FSE_buildCTable_wksp()`, `FSE_NCountWriteBound()`, `FSE_writeNCount()`, `FSE_optimalTableLog_internal()`, `FSE_optimalTableLog()`, `FSE_normalizeCount()`, `FSE_buildCTable_rle()`, `FSE_compress_usingCTable()`, and `FSE_compressBound()`. Important internal helpers are `FSE_writeNCount_generic()`, `FSE_minTableLog()`, `FSE_normalizeM2()`, and `FSE_compress_usingCTable_generic()`.

## Control Flow, State, and Persistence
`FSE_buildCTable_wksp()` lays out the CTable header, cumulative counts, symbol spread table, state table, and symbol transform table using caller-provided workspace. Low-probability symbols are placed in a high-threshold area; other symbols are distributed by `FSE_TABLESTEP()`. `FSE_writeNCount_generic()` bit-packs table log and normalized counts with compact zero-run encoding. `FSE_normalizeCount()` scales raw counts to sum to `1 << tableLog`, assigning low-probability symbols as `-1` or `1` and falling back to `FSE_normalizeM2()` for difficult rounding cases. `FSE_compress_usingCTable_generic()` initializes two encoder states from the input tail, walks input backwards, emits symbols into `BIT_CStream_t`, flushes states, and closes the stream.

## Dependencies and Integration Points
The file depends on memory helpers, bitstream writing, FSE public/static definitions, error macros, `ZSTD_div64`, and `ZSTD_highbit32`. `huf_compress.c` reuses this encoder to compress Huffman weight tables. Zstd block compression uses these routines after histograms have been collected by `hist.c`.

## Risks and Test Signals
Risks include workspace misalignment/size errors, invalid normalized distributions, tableLog underflow/overflow, bitstream buffer exhaustion, and subtle off-by-one issues in zero-run and low-probability encoding. Strong tests cover RLE inputs, incompressible distributions, tiny source sizes, maximum alphabet/table log, safe versus fast destination capacity paths, round-trip decode of NCount headers, and sanitizer runs over workspace overlap cases.
