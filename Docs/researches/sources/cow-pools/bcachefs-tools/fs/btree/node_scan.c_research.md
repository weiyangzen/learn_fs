# File Research: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.c

Read completeness: full file read, 608 lines.

Purpose: recovery scanner for discovering valid btree nodes directly on member devices. It is used when topology/root information is missing or needs reconstruction. The scanner probes possible btree-node locations, validates candidate nodes through normal btree read validation, merges replicas, removes overwritten ranges, and can emit reconstructed btree pointer keys into the journal.

Key structures and helpers:
- `struct find_btree_nodes_worker` carries a closure, shared scan state, and one device for a scanning kthread.
- `bch2_found_btree_node_to_text()` and `found_btree_nodes_to_text()` format discovered nodes, key ranges, sequence/journal sequence, cookie, and extent pointers.
- `found_btree_node_to_key()` converts a `found_btree_node` into a `KEY_TYPE_btree_ptr_v2` key with min/max range, replica pointers, sectors written, and range-updated bit.
- Comparator families sort by cookie for replica merging, by btree/level/range/time for overwrite handling, and by range start for eytzinger lookup.

Control flow:
- `try_read_btree_node()` first reads one filesystem block at a candidate sector, checks magic, decrypts the header area if needed, rejects reconstructable/internal IDs and invalid level/id values, then builds a candidate pointer and reads the full btree node size.
- Full candidate validation delegates to `bch2_btree_node_read_done()`. Only candidates that pass normal btree-node validation are appended to `f->nodes`.
- `read_btree_nodes_worker()` allocates temporary btree memory and a bio, walks btree-marked buckets when the on-disk member bitmap is available, scans btree-node-sized offsets, and periodically logs progress.
- `read_btree_nodes()` starts one worker per online member that can contain btree data, waits with `closure_sync_unbounded()`, and returns the shared scan error.
- `bch2_scan_for_btree_nodes()` runs workers once, merges same-cookie replicas, sorts nodes by logical position, trims or drops overwritten ranges with a min-heap, verifies no overlaps remain, and stores the final array in eytzinger order.
- `bch2_btree_node_is_stale()` looks for newer scanned nodes overlapping a cached node.
- `bch2_btree_has_scanned_nodes()` and `bch2_get_scanned_nodes()` trigger the scan recovery pass and query discovered nodes; `bch2_get_scanned_nodes()` also validates generated pointer keys and inserts them into the journal.

Dependencies and integration:
- Uses allocation bucket metadata for generation numbers, btree cache memory allocation for temporary nodes, `read.h` validation, journal insertion, recovery pass orchestration, kthreads, bios, heaps, and eytzinger search.
- The output type `found_btree_node` is declared in `node_scan_types.h`; declarations are in `node_scan.h`.
- Recovery code calls these helpers when rebuilding roots/interior nodes from scanned leaf/interior node evidence.

Risks and validation notes:
- Encrypted metadata cannot be scanned without `c->chacha20_key_set`.
- Endian conversion is not handled in `try_read_btree_node()` after validation; mismatched endian marks the scan with `-EINVAL`.
- Replica merging assumes same cookie means the same logical node; more than `BCH_REPLICAS_MAX` replicas is a hard recovery error.
- Overwrite trimming depends on sequence and journal sequence ordering; equal-time leaf overlap handling keeps later ranges by positional trimming while interior equal-time overlap is dropped.
