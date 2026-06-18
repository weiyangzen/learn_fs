# sources/compression/zstd/lib/common/huf.h

## Purpose
`huf.h` declares zstd's Huffman literal entropy API, including compression table construction, table reuse, serialized table reads, and single-stream or four-stream decompression variants. It is the boundary between zstd block logic and the lower-level Huff0/FSE entropy machinery.

## Important APIs, Types, and Functions
The header defines bounds and allocation contracts such as `HUF_BLOCKSIZE_MAX`, `HUF_WORKSPACE_SIZE`, `HUF_CTABLEBOUND`, `HUF_DTABLE_SIZE()`, `HUF_CREATE_STATIC_CTABLE()`, and `HUF_CREATE_STATIC_DTABLEX1/X2()`. Important types include opaque-ish `HUF_CElt`, `HUF_DTable`, `HUF_flags_e`, `HUF_repeat`, and `HUF_CTableHeader`. Compression declarations include `HUF_minTableLog()`, `HUF_cardinality()`, `HUF_optimalTableLog()`, `HUF_buildCTable_wksp()`, `HUF_writeCTable_wksp()`, `HUF_compress1X_repeat()`, `HUF_compress4X_repeat()`, and `HUF_compress*X_usingCTable()`. Decompression declarations include `HUF_readStats[_wksp]()`, `HUF_readCTable()`, `HUF_selectDecoder()`, `HUF_readDTableX1/X2_wksp()`, and the `HUF_decompress*` workspace/table variants.

## Control Flow, State, and Persistence
Compression flow counts input bytes, optionally optimizes the table depth, builds a CTable, serializes the Huffman weights, and emits either one stream or four streams. Repeat mode lets callers validate or reuse a previous CTable based on `HUF_repeat` and flags such as `HUF_flags_preferRepeat`. Decompression flow selects X1 or X2, reads the compact tree through FSE-backed stats parsing, builds a DTable, and decodes one or four segments into caller output. All persistent state is caller-owned in previous Huffman tables and repeat flags.

## Dependencies and Integration Points
It includes `zstd_deps.h`, `mem.h`, and static-linking `fse.h`. Zstd literal block compression/decompression uses this header directly, while FSE provides table-header entropy decoding for Huffman weights. Runtime flags bridge to CPU feature selection (`HUF_flags_bmi2`), assembly policy (`HUF_flags_disableAsm`), and fast-loop policy (`HUF_flags_disableFast`).

## Risks and Test Signals
Risks include workspace alignment and size requirements, repeat-table misuse, choosing an X1/X2 decoder incompatible with a table, and configuration drift in `HUF_TABLELOG_MAX` beyond the absolute maximum. Since compressed literals are security-sensitive parser input, malformed table headers, zero weights, oversized symbol counts, and tiny destination buffers need fuzz coverage. Strong signals are literal-block round trips, repeat-table and no-repeat parity, BMI2 parity, one-stream/four-stream coverage, decoder selection boundaries, and sanitizer-clean handling of corrupted Huffman headers.
