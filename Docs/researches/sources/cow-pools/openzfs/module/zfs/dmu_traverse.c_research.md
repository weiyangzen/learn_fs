# File Research: sources/cow-pools/openzfs/module/zfs/dmu_traverse.c

Implements generic block-pointer tree traversal for datasets, destroyed objsets, and pools.

Key points:
- `traverse_impl()` is the shared walker behind `traverse_dataset_resume()`, `traverse_dataset()`, `traverse_dataset_destroyed()`, and `traverse_pool()`.
- Traversal is txg-filtered: blocks at or below `td_min_txg` are skipped, using logical birth time when `TRAVERSE_LOGICAL` is set and physical birth otherwise.
- Handles resumable traversal with `resume_skip_check()`, avoiding already-completed subtrees and converting indirect-block failures to level-0 resume bookmarks.
- Traverses ZIL blocks/records for mutable datasets when appropriate, including claimed-but-not-replayed log blocks.
- Supports pre-order and post-order callbacks with `TRAVERSE_PRE` and `TRAVERSE_POST`; callbacks may return `TRAVERSE_VISIT_NO_CHILDREN`.
- Distinguishes holes, redacted blocks, indirect blocks, dnode blocks, objset blocks, spill blocks, and ZIL blocks.
- Applies hole-birth logic so zero-birth holes are visited or skipped depending on feature state, possible object ID reuse, and `send_holes_without_birth_time`.
- `TRAVERSE_HARD` suppresses `EIO`/`ECKSUM` traversal failures after callback/resume handling.
- `TRAVERSE_NO_DECRYPT` causes protected metadata reads to use raw zio flags where needed.
- Metadata prefetch is issued by `traverse_prefetch_metadata()` and capped for indirect fanout by `zfs_traverse_indirect_prefetch_limit`.
- Optional data prefetch runs in `traverse_prefetch_thread()`, bounded by `zfs_pd_bytes_max` and coordinated through `prefetch_data_t`.

Important routines:
- `traverse_visitbp()` is the recursive block visitor and central control-flow point.
- `traverse_dnode()` invokes callbacks for dnodes and walks all block pointers plus spill block pointers.
- `prefetch_dnode_metadata()` schedules metadata prefetch for dnode block pointers and spills.
- `traverse_pool()` walks the MOS and each DSL dataset object, adjusting each dataset’s start txg by previous-snapshot txg.

Dependencies and interactions:
- Used by `dmu_send.c` to enumerate changed logical blocks in canonical order.
- Uses ARC reads for metadata traversal, ZIL parsing for intent-log blocks, dnode/object-set structures for recursion, and spa feature state for hole-birth decisions.
- Exports `traverse_dataset` and `traverse_pool`.

Research relevance:
- This file is the reusable block-tree scanner that makes send, scrub-like tools, and pool-level scans possible without each caller reimplementing dnode/indirect/ZIL traversal.
