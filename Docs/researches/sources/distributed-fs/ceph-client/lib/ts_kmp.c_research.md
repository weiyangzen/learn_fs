<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_kmp.c -->
# sources/distributed-fs/ceph-client/lib/ts_kmp.c

## Purpose
Knuth-Morris-Pratt implementation for the textsearch framework, providing linear-time matching that can carry partial matches across data blocks.

## APIs, Types, and Functions
Defines private `struct ts_kmp` with pattern pointer, pattern length, and flexible prefix table. Core functions are `kmp_init()`, `kmp_find()`, `compute_prefix_tbl()`, `kmp_get_pattern()`, and `kmp_get_pattern_len()`. `kmp_ops` registers algorithm name `"kmp"`.

## Control Flow, State, and Persistence
`kmp_init()` rejects zero-length patterns and allocation overflow, allocates a config private area containing prefix table and pattern bytes, computes the prefix table using optional case folding, and stores an uppercase pattern for `TS_IGNORECASE`. `kmp_find()` initializes `q` from zero for each call, starts reading at `state->offset`, fetches blocks, advances through bytes while falling back through the prefix table on mismatch, and returns the absolute start offset once `q == pattern_len`. It updates `state->offset` to the end of the match so `textsearch_next()` can continue.

## Dependencies and Integration
Depends on textsearch core, ctype helpers, module registration, overflow-check helpers, and algorithm selection through `textsearch_prepare("kmp", ...)`.

## Risks and Test Signals
Risks include case folding being byte-oriented, prefix table correctness for repeated prefixes, and callers needing to preserve `ts_state` between successive calls. Test signals include matches spanning block boundaries, repeated-pattern fallback cases, ignore-case matching, zero-length and overflow rejection, and comparison against naive search on randomized data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_kmp.c -->
