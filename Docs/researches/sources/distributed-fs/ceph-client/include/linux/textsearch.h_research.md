<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch.h -->
# sources/distributed-fs/ceph-client/include/linux/textsearch.h

## Purpose
declares the generic textsearch framework used by networking and other subsystems to prepare pattern-matching configurations and scan blocks of text or packet data.

## Important APIs, Types, and Functions
The file is 181 lines and exports these visible symbol families: types/enums `module`, `ts_config`, `ts_state`, `ts_ops`; macros/constants `TS_AUTOLOAD`, `TS_IGNORECASE`, `TS_PRIV_ALIGNTO`; function-like macros `TS_PRIV_ALIGN`; inline helpers `textsearch_next`, `textsearch_find`, `textsearch_get_pattern_len`; external prototypes `int`, `get_next_block`, `if`, `textsearch_next`, `textsearch_register`, `textsearch_unregister`, `textsearch_destroy`, `textsearch_find_continuous`, `ERR_PTR`.

## Control Flow
An algorithm registers `ts_ops`. Users call `textsearch_prepare()` with an algorithm name, pattern, length, flags, and gfp mask, then repeatedly call `textsearch_find()` or continuous search helpers. `textsearch_next()` abstracts block-by-block data access through callbacks.

## State and Persistence Behavior
`ts_config` holds algorithm ops, flags, pattern length, algorithm-private data, and module owner. `ts_state` tracks block offset, consumed offset, finish flag, and caller-provided storage across searches.

## Dependencies and Integration Points
It depends on module refcounts, skbuff-style block access patterns, and alignment helpers; it integrates with netfilter/string matching and any caller needing pluggable string search. Direct includes are `linux/types.h`, `linux/list.h`, `linux/kernel.h`, `linux/err.h`, `linux/slab.h`.

## Risks and Edge Cases
Search state must be initialized and preserved correctly across fragmented buffers. Algorithm modules must remain referenced while configs live; ignore-case and pattern length handling can diverge by algorithm.

## Test Signals
Register/unregister algorithms, scan contiguous and fragmented buffers, test ignore-case/autoload paths, run netfilter string-match tests, and check module unload while configs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/textsearch.h -->
