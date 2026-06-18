# sources/distributed-fs/ceph-client/fs/btrfs/fiemap.c

## Purpose

`fiemap.c` implements Btrfs `FIEMAP` reporting. It walks file extent items, detects implicit/explicit holes, prealloc extents, inline extents, compressed extents, delalloc ranges, and shared extents, then emits merged `fiemap` records to userspace while avoiding deadlocks when the userspace fiemap buffer is mmaped to the target file.

## Important APIs, Types, And Functions

- `struct btrfs_fiemap_entry` is the buffered output tuple: logical offset, physical address, length, and fiemap flags.
- `BTRFS_FIEMAP_FLUSH_CACHE` is a private sentinel return code that tells the walker to drop locks/path, flush buffered entries, and restart at a safe offset.
- `struct fiemap_cache` buffers ready entries and one current merge candidate. It tracks array capacity/position, next search offset after a forced flush, mapped extent count, and cached extent fields.
- `flush_fiemap_cache()` writes buffered entries with `fiemap_fill_next_extent()`.
- `emit_fiemap_extent()` merges contiguous compatible records, trims stale overlaps caused by unlocked/researched tree walks, buffers ready entries, stops at `fi_extents_max`, and requests restart when the buffer fills.
- `emit_last_fiemap_cache()` emits the final cached extent.
- `fiemap_search_slot()` finds the first relevant file extent item and clones the leaf to avoid holding live tree locks during expensive shared-extent checks.
- `fiemap_next_leaf_item()` advances within cloned leaves and reclones the next live leaf as needed.
- `fiemap_process_hole()` reports delalloc inside holes/prealloc ranges and unwritten prealloc segments, including shared checks for prealloc extents.
- `fiemap_find_last_extent_offset()` finds the last non-hole file extent end so `FIEMAP_EXTENT_LAST` can be applied correctly.
- `extent_fiemap()` is the main walker; `btrfs_fiemap()` is the public entry point invoked by inode operations.

## Control Flow

`btrfs_fiemap()` first calls `fiemap_prep()`. If sync is requested, it waits for ordered ranges before and after taking the shared inode lock because compression can require a second wait after async compression has started. It then calls `extent_fiemap()`.

`extent_fiemap()` allocates a temporary output cache, backref share-check context, and Btrfs path. It rounds the requested range to sectorsize, locks the inode I/O tree range to stabilize delalloc and extent transitions, finds the last real extent, searches the subvolume tree, and iterates file extent items. Gaps before the next item are treated as implicit holes and passed to `fiemap_process_hole()`. Inline extents are emitted as inline/not-aligned; prealloc and explicit holes are processed for delalloc overlays; regular extents may be marked encoded and/or shared before emission.

When the fiemap cache fills, the code unlocks the I/O tree, releases the path, flushes buffered entries to userspace, adjusts `start`/`len` to `cache.next_search_offset`, and restarts. This avoids writing to a potentially mmaped output buffer while holding locks that `btrfs_page_mkwrite()` may need. At the end, it checks for EOF delalloc and applies `FIEMAP_EXTENT_LAST` when no later real or delalloc extent exists.

## State And Persistence Behavior

FIEMAP is observational and does not persist filesystem state. It temporarily locks `inode->io_tree` ranges to produce a coherent view relative to delalloc flushing and ordered extent completion. With `FIEMAP_FLAG_SYNC`, it actively waits for ordered extents so reported mappings reflect completed writeback. It uses cloned extent buffers to avoid holding live tree locks during expensive operations and a backref share-check context to identify shared extents.

## Dependencies And Integration Points

The file integrates Btrfs backref walking for shared extent detection, inode locking, extent I/O tree locking, file extent item accessors, delalloc search helpers, path/leaf traversal, and the generic Linux fiemap API. It is exposed through `btrfs_fiemap()` declared in `fiemap.h` and used by VFS ioctl/stat-style extent reporting paths.

## Risks And Edge Cases

- The walker may unlock and restart, so file extent items can change between passes. `emit_fiemap_extent()` contains overlap trimming logic to avoid duplicate or overlapping user-visible records.
- Holes and prealloc extents can contain delalloc ranges that are newer than tree items; missing this would underreport dirty data.
- FIEMAP buffers can be mmaped to the same file, so flushing while holding inode I/O tree locks or Btrfs paths can deadlock.
- Shared extent checks can be expensive and must use cloned leaves/backref context carefully.
- `FIEMAP_EXTENT_LAST` must consider both last file extent items and delalloc beyond the previous extent.
- Compression affects physical/logical merge rules; encoded extents cannot be merged simply by logical adjacency if physical layout does not match.

## Test Signals

Good signals include xfstests fiemap coverage for holes, prealloc, delalloc, inline extents, compressed extents, reflink/shared extents, no-holes mode, concurrent writeback/truncate while fiemap runs, sync vs non-sync fiemap, mmaped fiemap buffers, and fault injection for allocation/path failures.
