# sources/compression/zlib/deflate.h

## Purpose
Defines the private compressor state and constants shared by `deflate.c` and `trees.c`. Applications are explicitly told not to include it; public users should use `zlib.h`. The header is the structural contract for zlib's compressor internals, including LZ77 window state, hash chains, Huffman trees, pending output, bit buffer accounting, gzip header progress, and compile-time layout variants.

## APIs, Types, And Macros
The file defines code-count constants (`LENGTH_CODES`, `LITERALS`, `L_CODES`, `D_CODES`, `BL_CODES`, `HEAP_SIZE`, `MAX_BITS`, `Buf_size`), stream status constants (`INIT_STATE`, optional `GZIP_STATE`, `EXTRA_STATE`, `NAME_STATE`, `COMMENT_STATE`, `HCRC_STATE`, `BUSY_STATE`, `FINISH_STATE`), `ct_data`, `tree_desc`, `Pos`, `IPos`, and the central `deflate_state`. Macros such as `put_byte()`, `MIN_LOOKAHEAD`, `MAX_DIST()`, `WIN_INIT`, `d_code()`, `_tr_tally_lit()`, and `_tr_tally_dist()` encode performance-critical assumptions. It declares tree integration functions `_tr_init()`, `_tr_tally()`, `_tr_flush_block()`, `_tr_flush_bits()`, `_tr_align()`, and `_tr_stored_block()`.

## Control Flow Role
The header has no executable control flow, but it defines the state machine values consumed by `deflate()` and the buffer layout consumed by both compressor and tree emitters. `deflate.c` advances `status` through wrapper/header, busy compression, and finish states. `trees.c` consumes the dynamic tree arrays, symbol buffers, heap, bit buffer, and pending buffer fields when constructing and emitting compressed blocks.

## State And Persistence
`deflate_state` is memory-resident stream state. It stores the caller back-pointer, pending output buffer and pointer, wrapper mode, gzip header pointer/index, compression parameters, sliding window, hash `head` and `prev` chains, match/lazy-match fields, Huffman trees, frequency/count heaps, symbol buffers (`sym_buf` or split `d_buf`/`l_buf` under `LIT_MEM`), debug counters, bit accumulator fields, `high_water` zeroing watermark, and the `slid` flag used for hash-copy correctness. There is no persistence outside the allocated `z_stream` state.

## Dependencies And Integration
Depends on `zutil.h` for zlib internal types, memory macros, and constants such as `MAX_MATCH` and `MIN_MATCH`. It conditionally enables gzip support unless `NO_GZIP` is defined. Its `_tr_tally_*` macros depend on `_length_code` and `_dist_code` exported by `trees.c` in non-debug builds. Because buffer overlays and symbol buffer offsets are encoded here, changes must be coordinated with `deflate.c` allocation and `trees.c` emission logic.

## Risks And Test Signals
Risks are structural: changing field order, buffer sizes, code constants, or tally macros can break ABI assumptions inside the library even though the header is private. The pending/symbol buffer overlay, `LIT_MEM` alternative layout, distance-code mapping, and `MAX_DIST()` limit are especially sensitive. Test signals should include full compressor/decompressor round trips at all levels and strategies, debug builds that route through `_tr_tally()`, builds with `NO_GZIP`, `FASTEST`, and `LIT_MEM`, and sanitizer coverage for window high-water behavior.
