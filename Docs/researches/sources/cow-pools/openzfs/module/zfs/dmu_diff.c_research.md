# File Research: sources/cow-pools/openzfs/module/zfs/dmu_diff.c

## Scope

Implements snapshot dnode allocation diff reporting for `zfs diff`. It traverses the target snapshot from the source snapshot’s creation txg and writes compact ranges of in-use/free dnodes to a file.

## Main Interfaces

- `dmu_diff(tosnap_name, fromsnap_name, fp, offp)` is the public entry.
- Internal record helpers: `write_record()`, `report_free_dnode_range()`, `report_dnode()`.
- Traversal callback: `diff_cb()`.

## State And Control Flow

`dmu_diff()` validates both names are snapshots, holds the DSL pool, holds both snapshots, verifies `fromsnap` is before `tosnap`, records the source snapshot creation txg, long-holds the target snapshot, then calls `traverse_dataset()` with metadata prefetch, no-decrypt, and logical traversal flags.

`diff_cb()` ignores non-metadnode traversal and dnode-level bookmarks. For holes in the metadnode tree, it computes the dnode object span covered by the missing block and reports a free range. For level-0 metadnode blocks, it reads the block through ARC, iterates physical dnodes while honoring `dn_extra_slots`, and reports either in-use or free object ranges. Data blocks under file dnodes are skipped with `TRAVERSE_VISIT_NO_CHILDREN`.

Records are coalesced in `dmu_diffarg_t`: adjacent free dnodes become one `DDR_FREE` record and adjacent allocated dnodes become one `DDR_INUSE` record. `write_record()` flushes the pending record to the output file and advances the caller’s offset.

## Dependencies

Uses DSL dataset/pool holds, dataset ordering checks, traversal infrastructure, ARC reads, ZFS file write abstraction, dnode physical layout, block pointer protected/raw handling, and signal interruption.

## Correctness Notes

The traversal uses `TRAVERSE_NO_DECRYPT` because dnode allocation state is plaintext enough for this operation. Protected BPs are read raw. The callback only reports dnode allocation changes; higher-level name/path/stat interpretation is performed elsewhere by `zfs diff` tooling. Pending records are flushed at the end even when the final range has not naturally changed type.
