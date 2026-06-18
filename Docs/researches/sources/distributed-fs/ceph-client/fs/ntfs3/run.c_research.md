# sources/distributed-fs/ceph-client/fs/ntfs3/run.c

## Purpose
`run.c` implements NTFS3 runlists: VCN-to-LCN or sparse mappings plus packing and unpacking of NTFS mapping-pairs arrays stored in nonresident attributes.

## Important APIs and Functions
`ntfs_run` stores `vcn`, `len`, and `lcn`. `run_lookup()` binary-searches entries and `run_consolidate()` merges or trims neighbors. Public APIs include lookup, mapped-range checks, add, truncate, collapse, insert, delayed-allocation insert, get-entry, pack, unpack, checked unpack, highest-VCN scan, clone, remove-range, length, and max-VCN helpers.

## Control Flow
Mutations locate the affected VCN, split entries when needed, shift array elements, and consolidate around the changed index. `run_add_entry()` handles overlap, sparse transitions, contiguous physical runs, and tail reinsertion. `run_pack()` verifies complete coverage, encodes run lengths and signed LCN deltas, and terminates with zero. `run_unpack()` decodes mapping pairs, checks overflow and volume bounds, optionally deallocates clusters, and inserts decoded runs. `run_unpack_ex()` verifies allocated runs against `$Bitmap` and repairs/marks dirty on inconsistency.

## State and Persistence Behavior
`runs_tree` is an in-memory cache of persistent mapping pairs. Packed buffers persist in nonresident attributes. `RUN_DEALLOCATE` and checked unpacking can update allocation bitmap state.

## Dependencies and Integration Points
The file depends on overflow helpers, allocation APIs, `wnd_bitmap`, `mark_as_free_ex()`, `ntfs_set_state()`, and `ntfs_refresh_zone()`. Attribute allocation, truncation, fallocate, inode loading, and log replay depend on it.

## Risks
Arithmetic overflow, signed delta sign extension, sparse sentinel confusion, memory growth, incorrect consolidation, and bitmap repair races are key risks. Non-64-bit builds must reject oversized cluster references.

## Test Signals
Test fragmented, sparse, backwards-delta, large, boundary, and malformed mapping pairs; fallocate collapse/insert; punch-hole removal; delayed allocation; MFT-specific run growth; and bitmap inconsistency detection.
