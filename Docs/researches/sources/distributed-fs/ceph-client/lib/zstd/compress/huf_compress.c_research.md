# sources/distributed-fs/ceph-client/lib/zstd/compress/huf_compress.c

## Purpose
`huf_compress.c` implements Huffman table construction, table serialization/deserialization for compression tables, one-stream and four-stream Huffman bitstream encoding, repeat-table handling, and incompressibility heuristics for Zstd literal compression.

## Important Functions and Types
`nodeElt` represents Huffman tree nodes. `HUF_compressWeights()` uses FSE to compress Huffman weights. `HUF_writeCTable_wksp()` serializes a CTable as FSE-compressed or raw 4-bit weights. `HUF_readCTable()` reconstructs a compression table from serialized weights. `HUF_setMaxHeight()`, `HUF_sort()`, `HUF_buildTree()`, and `HUF_buildCTable_wksp()` build canonical Huffman tables within `HUF_TABLELOG_MAX`. `HUF_CStream_t` and helpers `HUF_addBits()`, `HUF_flushBits()`, and `HUF_closeCStream()` implement a custom high-bit-first encoder. `HUF_compress1X_usingCTable()` and `HUF_compress4X_usingCTable()` encode data, while `HUF_compress_internal()` handles histogramming, repeat tables, table choice, and output-size checks.

## Control Flow and State
Compression starts by validating workspace, block size, table log, and symbol range. Optional sampling skips likely incompressible large inputs. The full histogram then detects RLE and low-gain data. If a previous table is valid and preferred or cheaper, the old CTable is reused. Otherwise the code chooses an optimal table log, builds a new canonical table, writes its description, saves it into `oldHufTable`, and encodes either a single reverse stream or four independently compressed segments with a 6-byte jump table. Repeat state is caller-owned through `HUF_repeat`.

## Dependencies and Integration Points
The file depends on `zstd_deps.h`, `compiler.h`, `bitstream.h`, `hist.h`, `fse.h`, `huf.h`, `error_private.h`, and `bits.h`. It integrates tightly with FSE for weight header compression, with histogram counting for table construction, and with Zstd literal block encoding for repeat-table and RLE/raw decisions.

## Risks and Test Signals
Risks include workspace alignment and union sizing, canonical tree height repair in `HUF_setMaxHeight()`, quicksort/bucket sorting correctness, bit-container overflow in fast flush paths, jump-table segment size limits of 65535 bytes, and repeat-table validation when symbols appear that the old table cannot encode. Tests should cover empty input, RLE input, incompressible sampling, single-stream and four-stream outputs, max block size 128 KiB, optimal-depth flag, prefer-repeat behavior, zero-weight tables, insufficient output buffers, 32-bit versus 64-bit bit containers, and round trips against known Zstd vectors.
