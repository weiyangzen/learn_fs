# sources/distributed-fs/ceph-client/fs/f2fs/checkpoint.c

## Purpose

`fs/f2fs/checkpoint.c` implements F2FS checkpointing and related metadata orchestration. It manages checkpoint locks and priority uplift, metadata folio I/O, block-address validation, dirty inode tracking, orphan inode recovery and persistence, checkpoint pack validation and selection at mount, freezing filesystem operations for checkpoint, writing checkpoint packs, and the optional merged checkpoint request thread.

## Important APIs, Types, and Functions

Lock tracing and priority helpers include `f2fs_down_read_trace()`, `f2fs_down_read_trylock_trace()`, `f2fs_up_read_trace()`, `f2fs_down_write_trace()`, `f2fs_down_write_trylock_trace()`, `f2fs_up_write_trace()`, `f2fs_lock_op()`, `f2fs_trylock_op()`, and `f2fs_unlock_op()`.

Metadata folio APIs include `f2fs_grab_meta_folio()`, `f2fs_get_meta_folio()`, `f2fs_get_meta_folio_retry()`, `f2fs_get_tmp_folio()`, `f2fs_ra_meta_pages()`, `f2fs_ra_meta_pages_cond()`, `f2fs_sync_meta_pages()`, and `f2fs_meta_aops`. Address validation is exposed by `f2fs_is_valid_blkaddr()` and `f2fs_is_valid_blkaddr_raw()`.

Inode tracking APIs include `f2fs_add_ino_entry()`, `f2fs_remove_ino_entry()`, `f2fs_exist_written_data()`, `f2fs_release_ino_entry()`, `f2fs_set_dirty_device()`, `f2fs_is_dirty_device()`, `f2fs_acquire_orphan_inode()`, `f2fs_release_orphan_inode()`, `f2fs_add_orphan_inode()`, and `f2fs_remove_orphan_inode()`. Recovery and checkpoint APIs include `f2fs_recover_orphan_inodes()`, `f2fs_get_valid_checkpoint()`, `f2fs_sync_dirty_inodes()`, `f2fs_wait_on_all_pages()`, `f2fs_write_checkpoint()`, `f2fs_issue_checkpoint()`, `f2fs_start_ckpt_thread()`, `f2fs_stop_ckpt_thread()`, `f2fs_flush_ckpt_thread()`, and init/destroy helpers for checkpoint caches and request control.

## Control Flow

Mount-time checkpoint selection begins in `f2fs_get_valid_checkpoint()`. It reads both checkpoint packs, validates the first and last checkpoint block of each pack through checksum and version checks, chooses the newer valid version, copies the checkpoint payload into `sbi->ckpt`, records `cur_cp_pack`, and performs sanity checking before reading any additional payload blocks.

Runtime checkpointing enters through `f2fs_write_checkpoint()` or `f2fs_issue_checkpoint()`. `f2fs_issue_checkpoint()` may write synchronously or enqueue a request to the checkpoint thread when merge-checkpoint mode is active. The synchronous path takes `gc_lock`, then `f2fs_write_checkpoint()` takes `cp_global_sem` except during resize, skips clean checkpoints for selected reasons, rejects read-only or checkpoint-error states, and calls `block_operations()`.

`block_operations()` freezes mutating filesystem activity by taking `cp_rwsem`, flushing quota when needed, writing dirty dentries, taking `node_change`, syncing dirty inode metadata, taking `node_write`, syncing dirty node pages, and preparing the checkpoint block counters. `unblock_operations()` releases `node_write` and `cp_rwsem`.

After operations are blocked, `f2fs_write_checkpoint()` flushes merged writes, advances the checkpoint version, flushes NAT and SIT entries, saves in-memory current segment state, and calls `do_checkpoint()`. `do_checkpoint()` writes dirty metadata, fills checkpoint counters and current segment fields, updates flags, copies NAT/SIT bitmaps, computes the checkpoint checksum, writes NAT bits, checkpoint payload, orphan blocks, data summaries, node summaries when needed, flushes metadata and device cache, and finally writes the second checkpoint block through `commit_checkpoint()` with `META_FLUSH`. It then invalidates temporary meta mapping pages for encrypted/verity/compressed files, releases inode tracking entries, resets dirty/checkpoint flags, switches to the next checkpoint pack, and reports `-EIO` if checkpoint error state appeared.

Orphan recovery is handled separately by `f2fs_recover_orphan_inodes()`, which reads orphan blocks from the current checkpoint pack, igets each orphan inode, clears nlink, drops it through `iput()` to trigger truncation, and sets `SBI_NEED_FSCK` if cleanup cannot prove the node block was removed.

## State and Persistence Behavior

The central persistent object is `struct f2fs_checkpoint` plus checkpoint payload blocks, orphan inode blocks, segment summaries, NAT/SIT bitmaps, optional NAT bits, and two alternating checkpoint packs. `checkpoint_ver` determines the newer pack. Checkpoint flags persist mount/recovery state such as orphan presence, umount, fastboot, trimmed, fsck-needed, resize, checkpoint-disabled, quick-disabled, quota-needs-fsck, and CRC recovery mode.

In memory, the file maintains metadata folios in `META_MAPPING(sbi)`, dirty page counters, inode-management radix trees and lists for orphan/append/update/flush tracking, checkpoint timing stats, and merged checkpoint request queues. It also maintains slab caches for `ino_entry` and `inode_entry`.

## Dependencies and Integration Points

This file is deeply integrated with F2FS node, segment, data, quota, discard, GC, recovery, iostat, tracepoint, fault-injection, and mount-option code. It uses Linux folio/pagecache APIs, writeback controls, bio submission, blk plugs, wait queues, kthreads, delay accounting, ioprio, and block-device statistics. It provides synchronization used by write paths, GC, quota writes, compression writes, and recovery.

## Risks and Edge Cases

Risks concentrate around ordering and failure handling. Checkpoint correctness depends on freezing the right operations, flushing NAT/SIT/meta/data in order, writing the final checkpoint block only after prior metadata is durable, and switching packs only after success. Address validation must distinguish metadata, recovery, and data contexts and set `SBI_NEED_FSCK` or checkpoint error state appropriately. Orphan recovery on read-only hardware is skipped, which preserves media but leaves cleanup to later writable mounts. Quota flushing can retry and eventually set quota repair flags. The merged checkpoint thread must complete queued requests even when the thread stops or a request was already dispatched.

## Test Signals

High-value tests include mount with one valid checkpoint pack, both valid packs with different versions, invalid checksum, invalid payload count, orphan recovery success/failure, readonly orphan skip, dirty dentry/node/imeta flushing, quota flush retries, checkpoint disabled and pause behavior, discard-only checkpoints with no candidates, NAT/SIT flush errors, device flush errors, cp_error propagation, merged checkpoint queue latency and shutdown, fault injection for locks/block addresses/orphans, and fsck-needed flag setting after validation failures.
