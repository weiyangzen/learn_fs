<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_bm.c -->
# sources/distributed-fs/ceph-client/lib/ts_bm.c

## Purpose
Boyer-Moore implementation for the textsearch framework, optimized for performance on blocks where matches do not need to span block boundaries.

## APIs, Types, and Functions
Defines private `struct ts_bm` with uppercase or raw pattern bytes, pattern length, bad-character shift table, and flexible good-suffix shift table. Core functions are `bm_init()`, `bm_find()`, `bm_get_pattern()`, `bm_get_pattern_len()`, `compute_prefix_tbl()`, `subpattern()`, and `matchpat()`. `bm_ops` registers the algorithm name `"bm"`.

## Control Flow, State, and Persistence
`bm_init()` rejects zero length and allocation-size overflow, allocates one `ts_config` private area containing shift tables and pattern bytes, stores flags, uppercases the pattern for `TS_IGNORECASE`, and precomputes bad/good shifts. `bm_find()` starts from `state->offset`, fetches blocks through `conf->get_next_block()`, scans each block right-to-left within candidate windows, and returns the absolute match offset. It advances to the next block when no match is found within the current block and returns `UINT_MAX` at end. Module init/exit register/unregister with the core textsearch registry.

## Dependencies and Integration
Depends on `linux/textsearch.h`, ctype helpers, module infrastructure, overflow-check helpers, and the core registry in `textsearch.c`. Users select it via `textsearch_prepare("bm", ...)`.

## Risks and Test Signals
Risks include the documented inability to find matches spanning multiple blocks, correctness of shift-table arithmetic, case-folding limited to byte-wise `toupper()`, and allocation overflow handling. Test signals should compare against KMP on linear data, exercise fragmented data with boundary-spanning matches that BM should miss, test ignore-case bad-shift entries, zero-length rejection, and very large length overflow rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_bm.c -->
