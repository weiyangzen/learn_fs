# sources/distributed-fs/ceph-client/fs/ntfs/runlist.c

## Purpose
`runlist.c` implements in-memory NTFS VCN-to-LCN mapping management and mapping-pairs compression/decompression. It is used by non-resident attributes, allocation, sparse/compressed files, MFT extension, hole punching, and range collapse.

## Important APIs and Functions
Public functions include `ntfs_rl_realloc()`, `ntfs_runlists_merge()`, `ntfs_mapping_pairs_decompress()`, `ntfs_rl_vcn_to_lcn()`, `ntfs_rl_find_vcn_nolock()`, `ntfs_get_size_for_mapping_pairs()`, `ntfs_mapping_pairs_build()`, `ntfs_rl_truncate_nolock()`, `ntfs_rl_sparse()`, `ntfs_rl_get_compressed_size()`, `ntfs_rl_insert_range()`, `ntfs_rl_punch_hole()`, and `ntfs_rl_collapse_range()`. Internal helpers handle array movement, mergeability, insertion, append, replace, split, significant-byte encoding, and contiguous-run checks.

## Control Flow and State
Runlists are arrays of `{vcn,lcn,length}` terminated by a zero-length element whose `lcn` is usually `LCN_ENOENT` or `LCN_RL_NOT_MAPPED`. Negative LCN sentinels represent delayed allocation, sparse holes, unmapped regions, no entry, and error states. Merge logic locates where a source runlist fits into a destination runlist and chooses insert, append, replace, or split based on whether it starts/ends at a hole boundary. It preserves or creates unmapped regions and terminators as needed.

Mapping-pairs decompression walks on-disk variable-length pairs, decodes signed VCN lengths and relative LCN deltas, rejects negative lengths, invalid LCNs, overflow, and highest-VCN mismatches, then optionally merges the result into an old runlist. Building mapping pairs performs the inverse, encoding signed minimal-width lengths and LCN deltas, supporting partial ranges and `-ENOSPC` partial success with `stop_vcn` and `stop_rl`.

Truncation shrinks to a terminator or expands with sparse holes. Insert-range splices source runs into a destination at a VCN, splitting destination runs and merging contiguous holes/LCNs. Punch-hole extracts the removed physical runs into `punch_rl` and replaces the range with a hole. Collapse-range extracts a range and shifts following VCNs left.

## Dependencies and Integration
This file depends on NTFS volume geometry, attribute records, overflow helpers, memory allocation, and debug/logging. MFT and attribute allocation use merge/build/decompress to keep non-resident mapping pairs synchronized with in-memory runlists.

## Risks
Runlist correctness is critical: off-by-one VCN updates, terminator mishandling, or failure to merge/split sentinels can corrupt attribute mappings. Caller locking is required but not enforced. Several functions free input runlists on success, so ownership mistakes can cause use-after-free or leaks. Mapping-pair parsing is hardened for overflow, but crafted metadata remains high-risk.

## Test Signals
Unit-style tests should cover every merge shape, unmapped source prefixes, sparse holes, delayed allocation, partial first/last VCN ranges, mapping-pairs round trips, `-ENOSPC` partial builds, truncation shrink/expand, punch-hole and collapse across one or multiple runs, compressed-size accounting, and corrupt mapping-pair inputs.
