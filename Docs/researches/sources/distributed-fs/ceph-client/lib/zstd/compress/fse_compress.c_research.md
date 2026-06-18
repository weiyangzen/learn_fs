# sources/distributed-fs/ceph-client/lib/zstd/compress/fse_compress.c

## Purpose
`fse_compress.c` implements FSE compression table construction, normalized-count serialization, normalization, RLE table creation, and bitstream encoding. It supplies the compressor-side entropy primitive used by Zstd sequence coding and by `huf_compress.c` to compress Huffman weight headers.

## Important Functions
`FSE_buildCTable_wksp()` lays out the CTable header, state table, and symbol transform table from normalized counts. `FSE_NCountWriteBound()` and `FSE_writeNCount()` serialize normalized distributions. `FSE_optimalTableLog[_internal]()` chooses table log based on source size and symbol range. `FSE_normalizeCount()` and fallback `FSE_normalizeM2()` convert raw counts to a power-of-two distribution. `FSE_buildCTable_rle()` builds a single-symbol table. `FSE_compress_usingCTable()` selects checked or fast bit flushing based on destination capacity.

## Control Flow and State
CTable construction first computes cumulative positions, reserves high slots for low-probability `-1` entries, spreads symbols via `FSE_TABLESTEP()`, fills the sorted state table, then builds per-symbol transforms used by inline `FSE_encodeSymbol()`. Normalization assigns zeros, low-probability weights, scaled probabilities, then adjusts the largest symbol or falls back to method M2 for corner cases. Compression initializes two states from the last one or two input symbols and encodes input backward, flushing states at the end.

## Dependencies and Integration Points
The file depends on `hist.h`, `bitstream.h`, `fse.h`, `error_private.h`, `zstd_deps.h`, and `bits.h`. `ZSTD_div64()` is required for normalization scaling. `HUF_compressWeights()` depends on the NCount writer and CTable builder. Zstd sequence encoding relies on normalized count output matching `FSE_readNCount()`.

## Risks and Test Signals
Risks include workspace under-sizing, distribution sums not equaling `1 << tableLog`, buffer-bound mistakes in `FSE_writeNCount_generic()`, and reverse-encoding mistakes for odd input sizes. Low-probability handling differs depending on `useLowProbCount`, affecting decoder speed and compressed size. Tests should round-trip varied histograms, all-zero except one symbol, low-frequency sparse alphabets, small inputs under three bytes, insufficient destination buffers, max table logs, and normalized-count corruption.
