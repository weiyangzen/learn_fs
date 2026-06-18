# File Research: sources/cow-pools/openzfs/module/zfs/dmu_redact.c

## Purpose
Implements redaction bookmark/list generation for redacted ZFS sends. It traverses redaction snapshots, computes block ranges modified in all relevant snapshots, converts those ranges into concrete redaction-list entries for the target snapshot, and supports resumable redaction list creation.

## Main Responsibilities
- Traverses datasets at the target snapshot creation txg to identify blocks or object ranges modified by redaction snapshots.
- Emits sorted/coalesced `redact_record` ranges per traversal thread.
- Merges per-snapshot record streams to compute the intersection of ranges that must be redacted.
- Walks target objects and writes redaction-list entries in MOS syncing context.
- Creates or resumes a redaction bookmark with a redaction list.
- Validates redaction snapshots are before the target and are not themselves redacted datasets.
- Handles deleted objects and holes, including meta-dnode holes that cover whole object ranges.

## Key Data And State
- Tunables/constants:
  - `redact_sync_bufsize`
  - `redaction_list_update_interval_ns`
  - `zfs_redact_queue_length`
  - `zfs_redact_queue_ff`
- `redact_record`: logical candidate range with object/block bounds, block sizing, and EOS marker.
- `redact_thread_arg`: traversal thread state, queue, dataset/objset, resume bookmark, cancellation/error fields, deleted object list, and txg.
- `redact_node`: AVL wrapper around one current record per traversal thread, with start/end AVL nodes.
- `merge_data`: pending redaction blocks, coalescing state, per-txg block lists, furthest progress, redaction list pointer, and latest synctask txg.
- `redact_block_list_node`: list wrapper for `redact_block_phys_t`.
- Kernel-only `objnode` and `zfs_get_deleteq()`: sort ZFS delete queue object IDs into an `objlist_t`.

## Important Functions
- `record_merge_enqueue()`: coalesces adjacent logical redaction records before queueing; flushes pending record on EOS.
- `zfs_get_deleteq()`: kernel path that reads ZFS unlinked set from the master node ZAP, sorts object IDs with AVL, and builds an ordered objlist.
- `redact_cb()`: `traverse_dataset_resume()` callback. Produces candidate records for deleted objects, regular level-0 blocks, dnode holes, and meta-dnode holes.
- `redact_traverse_thread()`: builds deleted-object list, traverses the redaction dataset logically with metadata prefetch, emits EOS, and records errors.
- `redact_range_compare()`, `redact_node_compare_start()`, `redact_node_compare_end()`, `redact_record_before()`: comparison helpers for logical block ranges and AVL ordering.
- `update_avl_trees()`: advances one traversal thread’s current record in both start/end AVL trees.
- `perform_thread_merge()`: k-way range intersection algorithm over traversal queues; emits ranges covered by every redaction snapshot. With zero redaction snapshots, emits a record covering all objects except object 0.
- `redact_merge_thread()`: wraps `perform_thread_merge()` and appends EOS to the merged queue.
- `hold_next_object()`: finds the next non-metadata object in the target objset and holds its dnode.
- `update_redaction_list()`: coalesces physical redaction blocks, splits counts over `REDACT_BLOCK_MAX_COUNT`, and periodically commits pending entries.
- `commit_rl_updates()` / `redaction_list_update_sync()`: schedules and performs MOS redaction-list writes in syncing context, updating list length and progress fields.
- `perform_redaction()`: consumes merged logical ranges, maps them to existing target objects and block IDs, appends `redact_block_phys_t` entries, flushes final coalesced block, commits final progress as `UINT64_MAX`, and waits for sync.
- `redact_snaps_contains()`: GUID membership helper.
- `dmu_redact_snap()`: public entry point; holds target snapshot and redaction snapshots, creates/resumes redaction bookmark/list, starts traversal and merge threads, runs redaction-list materialization, then releases all holds.

## Control Flow Notes
- One traversal thread is created per redaction snapshot. Each produces sorted ranges because dataset traversal is ordered.
- A separate merge thread maintains two AVL trees: one sorted by range start and one by range end. The intersection `[latest start, earliest end]` is redacted when non-empty.
- `perform_redaction()` runs in open context but writes the redaction list through per-txg lists plus sync tasks because the list object lives in the MOS.
- Resume support uses `rlp_last_object` and `rlp_last_blkid` from the existing redaction list/bookmark to restart traversal and validate completion.
- The zero-redaction-snapshot case deliberately redacts all objects except object 0.

## Error Handling And Invariants
- Redaction target must be a snapshot with an objset and must not already have redacted dataset feature active.
- Redaction snapshots must be before the target and not redacted datasets.
- Resume validates bookmark has a redaction object, snapshot GUID set matches the requested redaction snapshots, and previous progress is not already complete.
- Cancellation propagates through `cancel` flags; workers drain queues to EOS on merge errors.
- `redact_cb()` ignores indirect non-hole blocks and only emits useful level-0/hole/deleted-object ranges.
- MOS redaction-list updates assert queued blocks do not pass the recorded furthest visited position.

## Dependencies
Depends on traversal, DMU object iteration, redaction list/bookmark DSL support, bqueues, AVL/list utilities, and, in kernel builds, ZFS unlink queue inspection: `dmu_traverse`, `dmu_objset`, `dmu_tx`, `dsl_dataset`, `dsl_bookmark`, `dmu_redact`, `objlist`, `bqueue`, `zap`, and ZFS znode/VFS headers.

## Research Notes
This file is the redaction-list construction engine. Its key correctness property is preserving ordered logical ranges from traversals, intersecting them accurately across all redaction snapshots, and only then translating them into concrete block entries in the target snapshot while maintaining resumable progress.
