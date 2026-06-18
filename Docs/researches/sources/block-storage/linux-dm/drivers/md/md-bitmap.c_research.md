# File Research: sources/block-storage/linux-dm/drivers/md/md-bitmap.c

## Purpose
Implements MD write-intent bitmap support: persistent bitmap superblocks, bitmap file/internal storage I/O, in-memory dirty-region counters, write-start/write-end accounting, recovery synchronization, bitmap resizing, clustered bitmap slot copying, and bitmap sysfs controls.

## Main Interfaces
- Lifecycle: `md_bitmap_create()`, `md_bitmap_load()`, `md_bitmap_destroy()`, `md_bitmap_free()`, `md_bitmap_flush()`.
- Persistent metadata: `md_bitmap_read_sb()`, `md_bitmap_new_disk_sb()`, `md_bitmap_update_sb()`, `md_bitmap_print_sb()`.
- I/O tracking: `md_bitmap_startwrite()`, `md_bitmap_endwrite()`, `md_bitmap_unplug()`, `md_bitmap_daemon_work()`.
- Recovery tracking: `md_bitmap_start_sync()`, `md_bitmap_end_sync()`, `md_bitmap_close_sync()`, `md_bitmap_cond_end_sync()`, `md_bitmap_sync_with_cluster()`.
- Dirtying and resize: `md_bitmap_dirty_bits()`, `md_bitmap_resize()`, `md_bitmap_write_all()`.
- Cluster helpers: `get_bitmap_from_slot()`, `md_bitmap_copy_from_slot()`.
- Sysfs group: `md_bitmap_group` with `location`, `space`, `time_base`, `backlog`, `chunksize`, `metadata`, `can_clear`, and `max_backlog_used`.

## Control Flow
Bitmap creation allocates the `bitmap` object, initializes locks and wait queues, pins an optional backing file, reads or creates the bitmap superblock unless metadata is external, then calls `md_bitmap_resize()` to allocate in-memory counters and persistent filemap pages. Loading creates serial pools, optionally loads cluster slot bitmaps, marks old sync information clean, chooses a recovery start point, reads persistent bitmap bits into memory, clears stale state, schedules recovery, and updates the bitmap superblock.

Writes call `md_bitmap_startwrite()` before data I/O. For each affected chunk it allocates or hijacks a counter page, sets the persistent bitmap bit if the counter was clean, increments the in-memory counter, and records write-behind state if applicable. `md_bitmap_endwrite()` decrements counters, marks failed writes as resync-needed, updates `events_cleared` when safe, and marks pages pending for the daemon.

`md_bitmap_daemon_work()` periodically promotes pending pages to need-write, updates `events_cleared` in the superblock when needed, sweeps counters from `2` to `1` to `0`, clears persistent bits when safe, and writes cleanable pages. `md_bitmap_unplug()` writes dirty or need-write pages before underlying device queues are unplugged.

## State And Synchronization
In-memory counters live in `bitmap->counts.bp` and are protected by `bitmap->counts.lock`. Counter high bits represent resync-needed and resync-active; low bits count pending writes plus the persistent bit. Storage pages and per-page attributes track dirty, pending, and need-write states. `pending_writes` plus `write_wait` track bitmap page I/O. `overflow_wait` handles saturated counters. `behind_writes` and `behind_wait` track write-behind backlog.

`mddev->bitmap_info.mutex` serializes daemon work with destruction and bitmap load. Bitmap destruction disconnects `mddev->bitmap` under `mddev->lock`. Resizing active arrays quiesces the personality while replacing storage and counters.

## Integration Points
Uses MD core metadata (`mddev->events`, `sb_flags`, `recovery`, `recovery_cp`, `resync_max_sectors`), per-device superblock I/O (`md_super_write()`, `md_super_wait()`), personality quiesce hooks, md recovery threads, sysfs notifications, block tracing, optional clustered MD operations, and optional file-backed bitmaps via `bmap()` and buffer-head I/O.

## Notable Behaviors
- If no persistent bitmap storage exists, initialization marks all chunks dirty so full recovery occurs.
- If bitmap superblock events are stale relative to array events, the bitmap is marked stale and full recovery is forced.
- File-backed bitmaps pre-read and attach buffer heads so later writes bypass filesystem allocation paths.
- Internal bitmaps write near member superblocks and include alignment checks to avoid overwriting data or metadata.
- Allocation failure for an in-memory counter page can hijack the page pointer as two counters, except clustered RAID forbids hijack and requires preallocation.
- `can_clear` is false while `need_sync` is set and cannot be forced true while degraded.
- File-based bitmap resizing while active is rejected.

## Risks And Review Focus
- Bitmap correctness depends on ordering persistent bitmap-bit writes before corresponding data writes.
- Counter transitions among dirty, pending, resync-needed, and resync-active states are subtle and recovery-critical.
- Internal bitmap offset/alignment checks must prevent metadata/data overlap across external and native metadata layouts.
- Cluster slot offset math must match bitmap page allocation and superblock layout.
- Active resize replaces both filemap and counter arrays while preserving needed bits; rollback paths must not leak or corrupt state.
