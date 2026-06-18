# sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c -->
## sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c

### Purpose
`lz_encoder_mf.c` implements hash-chain and binary-tree match finders for LZ encoders. These functions discover repeated byte sequences in the sliding input window and provide length-distance candidates to LZMA encoders.

### Important APIs, Types, And Functions
The exported wrapper `lzma_mf_find()` calls the configured finder and extends a longest nice-length match. Implemented find/skip pairs include `lzma_mf_hc3_*`, `lzma_mf_hc4_*`, `lzma_mf_bt2_*`, `lzma_mf_bt3_*`, and `lzma_mf_bt4_*` under feature macros. Internal helpers include `normalize()`, `move_pos()`, `move_pending()`, `hc_find_func()`, `bt_find_func()`, and `bt_skip_func()`.

### Control Flow
Each finder computes hash values at `mf_ptr(mf)`, updates fixed-prefix hash slots, obtains a candidate position, searches either a hash chain or binary tree up to `depth`, and emits matches sorted by increasing length. `lzma_mf_find()` validates matches in debug builds, extends a match that reached `nice_len` up to `match_len_max`, stores the count, and increments read-ahead. Skip functions update hash/tree structures without returning matches. When insufficient input is available during flush, `move_pending()` advances `read_pos` and counts bytes that must later be rehashed. `normalize()` subtracts an offset from all hash/son entries when relative positions approach `UINT32_MAX`.

### State, Persistence, And Dependencies
State is in the caller-owned `lzma_mf`: hash table, son table, cyclic position, offset, read positions, pending count, depth, and action. Dependencies include hash macros and `lzma_memcmplen()` for fast match extension.

### Integration Points
`lz_encoder.c` selects these callbacks from `lzma_lz_options.match_finder`. LZMA optimum parsing depends on the quality and ordering of returned matches.

### Risks
Match-finder code is pointer- and index-heavy. Off-by-one distance handling uses zero-based `dist = delta - 1`, while validation compares against `read_pos`. Binary-tree paths must maintain both child pointers on early termination. Normalization touches potentially uninitialized `son` entries by design, which can confuse dynamic analysis unless documented suppressions are used.

### Test Signals
Tests should compare match outputs against a reference for repeated patterns, random data, low-input flushes, normalization near `UINT32_MAX`, each HC/BT variant, and sanitizer/Valgrind runs around table bounds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c -->
