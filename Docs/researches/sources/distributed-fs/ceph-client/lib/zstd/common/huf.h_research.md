# sources/distributed-fs/ceph-client/lib/zstd/common/huf.h

## Purpose
`huf.h` declares the Huffman codec interface used for Zstd literal block compression and decompression. It exposes static allocation macros, workspace sizes, compression table APIs, repeat-table behavior, decoder selection, and flags controlling optimal depth, repeated tables, suspected incompressibility, BMI2, assembly, and fast-loop behavior.

## Important APIs and Types
Key constants are `HUF_BLOCKSIZE_MAX`, `HUF_TABLELOG_MAX`, `HUF_TABLELOG_DEFAULT`, `HUF_SYMBOLVALUE_MAX`, `HUF_WORKSPACE_SIZE`, and `HUF_DECOMPRESS_WORKSPACE_SIZE`. `HUF_CElt` is an opaque `size_t` compression-table element, and `HUF_DTable` is a `U32` decode table. `HUF_flags_e` controls compression/decompression features. Compression APIs include `HUF_buildCTable_wksp()`, `HUF_writeCTable_wksp()`, `HUF_compress1X_usingCTable()`, `HUF_compress4X_usingCTable()`, `HUF_compress1X_repeat()`, and `HUF_compress4X_repeat()`. Decompression APIs include DTable readers, 1X/4X decode variants, and `HUF_selectDecoder()`.

## Control Flow and State
The header documents the Huffman flow: count symbols, choose or refine table log, build a canonical table, serialize the tree, and encode one or four streams. Repeat state is represented by `HUF_repeat_none`, `HUF_repeat_check`, and `HUF_repeat_valid`, allowing Zstd blocks to reuse a previous Huffman table when valid and beneficial.

## Dependencies and Integration Points
It includes `zstd_deps.h`, `mem.h`, and `fse.h` with static-linking declarations. Huffman tree serialization uses FSE for compact weight compression, so `FSE_DECOMPRESS_WKSP_SIZE_U32()` also sizes `HUF_READ_STATS_WORKSPACE_SIZE_U32`. Zstd literal block code chooses between HUF raw, RLE, compressed, and repeat-table paths using these interfaces.

## Risks and Test Signals
Risks include mismatch between opaque table allocation macros and implementation layout, repeat-table misuse when new input contains symbols absent from the previous table, and flag handling divergence between compression and decompression builds. Tests should cover 1X and 4X streams, repeat valid/check/none transitions, zero-weight symbols, max table log 12, workspace alignment, compressed and raw tree headers, and decoder selection thresholds.
