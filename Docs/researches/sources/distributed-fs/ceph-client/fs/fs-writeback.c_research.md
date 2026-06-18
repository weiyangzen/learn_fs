# sources/distributed-fs/ceph-client/fs/fs-writeback.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fs-writeback.c` implements the VFS writeback engine for dirty inodes and pagecache data. It manages dirty inode lists, flusher work items, background and periodic writeback, sync writeback, lazytime expiration, cgroup writeback ownership, and exported helpers for inode metadata flushing. The complete 2996-line file was read for this report.

## Important APIs, Types, and Functions

Core structures and state include `struct wb_writeback_work`, `dirtytime_expire_interval`, `bdi_writeback` dirty lists, and optional `struct inode_switch_wbs_context`. Exported APIs include `wb_wait_for_completion()`, `wbc_attach_fdatawrite_inode()`, `wbc_detach_inode()`, `wbc_account_cgroup_owner()`, `inode_io_list_del()`, `writeback_inodes_sb_nr()`, `writeback_inodes_sb()`, `try_to_writeback_inodes_sb()`, `sync_inodes_sb()`, `write_inode_now()`, `sync_inode_metadata()`, and `__mark_inode_dirty()`. Other important functions include `wb_queue_work()`, `inode_io_list_move_locked()`, `queue_io()`, `__writeback_single_inode()`, `writeback_single_inode()`, `writeback_sb_inodes()`, `wb_writeback()`, `wb_do_writeback()`, and `wb_workfn()`.

## Control Flow

Dirtying starts in `__mark_inode_dirty()`: filesystem dirty callbacks run for inode dirtiness, state bits are set with memory barriers, the inode is attached to a writeback context, and it is queued on `b_dirty` or `b_dirty_time`. Flusher workers take queued `wb_writeback_work` items, move expired dirty inodes to `b_io`, group work by superblock, set `I_SYNC`, call `do_writepages()`, optionally wait data, sync lazytime, write inode metadata, then requeue or detach the inode based on remaining dirty state. Sync paths split work across cgroup writeback instances, wait for completions, and then wait for existing writeback on the superblock's writeback inode list.

## State and Persistence Behavior

Runtime state spans inode dirty bits (`I_DIRTY_*`, `I_SYNC`, `I_SYNC_QUEUED`, `I_WB_SWITCH`), per-wb lists (`b_dirty`, `b_io`, `b_more_io`, `b_dirty_time`, `b_attached`), work queues, completion counters, bandwidth stats, and sysctl-controlled lazytime expiration. Persistent effects occur through filesystem `writepages`, `write_inode`, and `sync_lazytime` operations that write data and metadata to storage.

## Dependencies and Integration Points

The file integrates with pagecache tags, backing-device writeback, block plug flushing, memcg/cgroup writeback, superblock locking, filesystem super operations, dirty throttling thresholds, tracepoints, sysctl, workqueues, RCU, and hung-task progress reporting.

## Risks and Edge Cases

High-risk areas are lock ordering between inode locks, wb list locks, superblock `s_umount`, and cgroup switch semaphores; memory barriers around dirty-bit clearing and lockless dirty checks; inode lifetime while waiting on `I_SYNC`; cgroup ownership switching across RCU/workqueues; lazytime inodes not counted as dirty I/O; and avoiding livelock under continuously redirtied mappings.

## Test Signals

Signals include xfstests generic sync/fsync/writeback cases, cgroup writeback ownership tests, memcg dirty throttling, lazytime expiration sysctl tests, writeback under umount, fault injection in `writepages`/`write_inode`, lockdep/KCSAN, tracepoint inspection, hung-task wait progress, and stress with concurrent dirtying, reclaim, sync, and cgroup deletion.
