# sources/distributed-fs/ceph-client/fs/f2fs/debug.c

## Purpose

`debug.c` implements F2FS runtime statistics collection and debugfs presentation. It builds per-superblock `f2fs_stat_info`, maintains all mounted instances on a global stats list, calculates segment distribution and memory footprint, and exposes a consolidated `/sys/kernel/debug/f2fs/status` view when `CONFIG_DEBUG_FS` is enabled.

The file does not implement filesystem behavior directly. Its job is observability: surfacing allocation, checkpoint, GC, extent-cache, dirty-page, IO, discard, compression, swapfile, atomic-write, multi-device, and memory statistics in a single status report.

## Important APIs, Types, And Functions

Global state includes `f2fs_stat_list`, protected by `f2fs_stat_lock`, plus `f2fs_debugfs_root` under `CONFIG_DEBUG_FS`.

`f2fs_build_stats()` allocates and initializes `struct f2fs_stat_info` and per-device stats, resets related counters in `sbi`, stores `sbi->stat_info`, and links the instance into the global list. `f2fs_destroy_stats()` removes the instance and frees its stats.

`f2fs_create_root_stats()` creates the `f2fs` debugfs directory and `status` file. `f2fs_destroy_root_stats()` removes the tree. `DEFINE_SHOW_ATTRIBUTE(stat)` binds `stat_show()` to the debugfs file operations.

`f2fs_update_sit_info()` calculates a bimodal distribution factor and average valid blocks among dirty sections. `update_multidevice_stats()` summarizes per-device segment and section states. `update_general_status()` snapshots most live counters from `sbi`, node manager, segment manager, SIT, NAT, checkpoint merge state, discard/flush queues, extent caches, dirty pages, and curseg positions. `update_mem_info()` estimates static, cache, extent-cache, and page-cache memory footprint.

`stat_show()` is the main renderer. It takes the global spinlock, walks all mounted stat objects, refreshes status, and prints a human-readable report with policy, utilization, segment layout, checkpoint and GC counts, extent cache hit ratios, async IO counters, dirty pages, NAT/SIT stats, user-block distribution, IPU/SSR/LFS counts, segment BDF, and memory usage.

## Control Flow

Stats are built at mount-time through `f2fs_build_stats()`, then debugfs root creation is handled once through `f2fs_create_root_stats()`. When a user reads the debugfs `status` file, `stat_show()` iterates over `f2fs_stat_list`. For each `sbi`, it calls `update_general_status()`, then prints partition identity and checkpoint state, superblock layout, policy, utilization, current segment positions, multi-device summaries, checkpoint merge statistics, GC movement counts, extent-cache metrics, dirty/writeback/read counters, metadata cache counts, user-block distribution, IPU/SSR/LFS counters, SIT distribution statistics, and memory footprint.

`update_general_status()` is a broad snapshot. It reads raw superblock fields that may change during online resize, pulls extent-cache hit counters and tree/node counts, reads dirty and IO page counters, snapshots flush/discard queues when present, copies checkpoint merge timing under its own lock, calculates segment/free/dirty/prefree counts, reads page-cache sizes for node/meta/compress inodes, collects NAT/SIT/free-nid counts, records current segment offsets and locations, and scans all main segments by type to aggregate dirty/full segment counts and valid blocks.

`update_mem_info()` lazily computes static/base allocations only once, then recomputes dynamic cache and page-cache memory on each status read.

## State And Persistence Behavior

The state in this file is in-memory diagnostic state. It does not persist to disk and does not change filesystem metadata except for initializing and resetting counters in `sbi` during stats setup.

The global list determines what mounted filesystems appear in the debugfs report. Per-mount `f2fs_stat_info` stores cached snapshots and memory estimates, but most values are refreshed from authoritative runtime structures when the debugfs file is read.

Counter initialization in `f2fs_build_stats()` is important because many counters live in `sbi` rather than only in `f2fs_stat_info`. Reset fields include extent-cache hit counters, inline/compressed/swapfile inode counters, atomic-file counts, inplace counts, metadata write counters, checkpoint call counters, and maximum atomic-write count.

## Dependencies And Integration Points

`debug.c` depends on F2FS core headers plus `node.h`, `segment.h`, and `gc.h`. It reads from the segment manager (`SM_I`), node manager (`NM_I`), SIT (`SIT_I`), free segment maps (`FREE_I`), current segment arrays, checkpoint merge control, discard and flush command controls, extent cache structures, dirty inode counts, and compression mappings.

It integrates with Linux debugfs and seq_file APIs. It is conditional in two layers: the stats build/destroy routines are always present, while debugfs file creation and rendering helpers are compiled under `CONFIG_DEBUG_FS`.

## Risks And Edge Cases

The debugfs report reads many live fields. The code uses targeted locking for the global stats list and checkpoint timing, but many counters are read locklessly or through atomics. This is acceptable for observability but means output is a best-effort snapshot, not a transactionally consistent state.

Multi-device stats depend on correct device block ranges and segment conversion. Off-by-one mistakes would misclassify segments or sections in debug output. Online resize is handled by refreshing raw superblock main-area fields during status generation.

`f2fs_update_sit_info()` divides by a derived distribution denominator and then by `ndirty` only when `si->dirty_count` is nonzero. The code assumes dirty-count and `ndirty` remain coherent enough for diagnostic use.

Memory footprint reporting is approximate. `base_mem` is calculated once and may not reflect all dynamic structural changes after mount, while cache/page memory is refreshed.

## Test Signals

Validation should include mounting F2FS with `CONFIG_DEBUG_FS`, reading `/sys/kernel/debug/f2fs/status`, and confirming no lockdep splats or crashes across single-device, multi-device, compression-enabled, discard-enabled, and resize scenarios. Output should show sane segment totals, nonnegative dirty/free/prefree counts, extent-cache hit ratios matching workload behavior, and changing checkpoint/GC/IO counters under stress.

Unmount tests should confirm `f2fs_destroy_stats()` removes entries from the status output and frees per-device stats. Counter-reset tests should verify a newly mounted filesystem starts with zeroed debug counters where expected.
