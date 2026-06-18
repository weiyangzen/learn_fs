# File Research: sources/cow-pools/openzfs/module/zfs/spa_checkpoint.c

## Summary
Implements storage pool checkpoint creation, discard, statistics, and asynchronous discard processing. A checkpoint preserves a pool-wide rewind target by preventing checkpoint-referenced blocks from being reused.

## Main Responsibilities
- Creates a checkpoint from the most recently synced uberblock.
- Stores checkpoint state in the MOS and activates `SPA_FEATURE_POOL_CHECKPOINT`.
- Tracks freed checkpoint blocks in per-vdev checkpoint space maps.
- Discards checkpoint space maps incrementally over multiple TXGs.
- Reports checkpoint state, space, and start time.
- Completes discard by decrementing the feature refcount.

## Key APIs
- `spa_checkpoint_get_stats()`.
- `spa_checkpoint()`.
- `spa_checkpoint_discard()`.
- `spa_checkpoint_discard_thread_check()`.
- `spa_checkpoint_discard_thread()`.

## Important Behavior
Checkpoint create and discard use early sync tasks so state transitions happen before ordinary dirty data can free or reuse checkpoint-relevant blocks in the same TXG. Creation records `spa_ubsync` in `DMU_POOL_ZPOOL_CHECKPOINT` and sets `spa_checkpoint_txg`.

Discard first removes the checkpoint uberblock entry and clears `spa_checkpoint_txg`, then a zthr walks each top-level vdev checkpoint space map. Entries are prefetched in open context, then a sync task moves freed ranges into metaslab freeing trees and updates checkpoint space accounting. When all checkpoint space maps are gone, the feature is deactivated.

## Risks
Checkpoint semantics constrain pool operations that change topology or identity. Discard accounting spans vdev stats, pool checkpoint info, space maps, and metaslab trees; interruption and batching are intentional. The memory limit tunable controls prefetch/discard batch size.
