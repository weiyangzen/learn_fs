# sources/distributed-fs/ceph-client/include/linux/writeback.h

## Purpose
`writeback.h` declares the kernel writeback control and dirty-throttling interfaces used by filesystems, backing devices, memory cgroups, and the page cache. It coordinates page writeout, dirty limits, cgroup writeback attribution, flusher threads, and folio dirty/writeback state.

## Important APIs, Types, and Functions
`enum writeback_sync_modes` distinguishes `WB_SYNC_NONE` and `WB_SYNC_ALL`. `struct writeback_control` carries caller-visible limits/ranges, sync mode, writeback reason flags, folio batch/index/error state, and optional cgroup-writeback fields for owning `bdi_writeback`, inode, foreign writeback detection, and byte accounting. Helpers include `wbc_to_write_flags()`, `wbc_blkcg_css()`, and `wbc_to_tag()`. `struct wb_domain` tracks writeback bandwidth proportions, period timer, dirty limit timestamp, and global dirty limit. `wb_domain_size_changed()` resets dirty-limit tracking under lock. Writeback APIs include superblock writeback/sync functions, flusher wakeups, inode writeback wait/list removal, cgroup writeback attach/detach/account/init-bio/umount/cleanup, `dirty_throttle_control`, `node_dirty_ok()`, `wb_domain_init/exit()`, `global_dirty_limits()`, threshold calculators, `wb_update_bandwidth()`, dirty throttling functions, `wb_over_bg_thresh()`, `writeback_iter()`, `do_writepages()`, ratelimit setup, page tagging, folio dirty/redirty helpers, inode writeback marking, and `MIN_WRITEBACK_PAGES`.

## Control Flow
Filesystems and VM code create a stack `writeback_control`, select a range and sync mode, tag dirty pages when needed, iterate folios with `writeback_iter()`, and call mapping `writepages` through `do_writepages()`. Background and kupdate writeback set request flags through `wbc_to_write_flags()`. Dirtying paths call balance-dirty-pages helpers to throttle writers against global/per-wb/cgroup thresholds. Cgroup writeback attaches inodes to a writeback context, associates bios with block cgroups, tracks foreign ownership, and may switch inode writeback ownership by work item.

## State and Persistence
`writeback_control` is stack-scoped and lockless by design. Persistent runtime state lives in backing-device writeback objects, writeback domains, inode `i_wb`, page-cache tags, per-CPU dirty throttle leaks, dirty thresholds, and flusher thread state. There is no durable persistence; data durability is achieved by the actual filesystem/block writeout that these APIs drive.

## Dependencies and Integration Points
Dependencies include scheduler state, workqueues, filesystems, flex proportions, backing device definitions, block operation flags, folio batches, cgroups, bios, blkcg CSS, superblocks, inodes, address spaces, and page-cache tags. Integration points include filesystem `address_space_operations`, page dirtying, balance_dirty_pages, memcg/blkcg writeback, flusher threads, sync/fsync, reclaim pageout, and block IO submission.

## Risks
Incorrect `nr_to_write`, range, or tag handling can cause livelock, skipped dirty data, or excessive writeback. `WB_SYNC_ALL` must wait where required for data integrity. Cgroup ownership accounting can misattribute IO if async layers continue accounting after the initial phase; `no_cgroup_owner` handles that case. `inode_detach_wb()` requires `I_CLEAR`. Dirty thresholds and bandwidth proportions are feedback loops and can throttle too much or too little if stale.

## Test Signals
Signals include filesystem writeback and sync tests, dirty throttling under memory pressure, background flusher behavior, cgroup writeback ownership and blkcg bio association, inode teardown, page-cache tag correctness, redirty paths, writeback error propagation, and stress with multiple backing devices of different speeds.
