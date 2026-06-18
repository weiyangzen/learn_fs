# File Research: sources/cow-pools/nilfs-utils/sbin/nilfs-resize.c

## Purpose
`nilfs-resize.c` implements online NILFS2 filesystem resizing. It supports growing a mounted filesystem up to the block device size and shrinking by evacuating in-use segments from the truncated range before issuing the NILFS resize ioctl.

## Main Interfaces
- NILFS APIs: `nilfs_open`, `nilfs_close`, `nilfs_get_layout`, `nilfs_get_sustat`, `nilfs_set_alloc_range`, `nilfs_resize`, `nilfs_sync`, `nilfs_freeze`, `nilfs_thaw`, `nilfs_lock_cleaner`, `nilfs_unlock_cleaner`.
- Segment/GC APIs: `nilfs_get_suinfo`, `nilfs_suinfo_*`, `nilfs_segment_is_protected`, `nilfs_reclaim_segment`, `nilfs_delete_checkpoint`.
- Mount/device APIs: `check_mount`, `BLKGETSIZE64`.
- Runs only on mounted block devices; offline resizing is explicitly not supported.

## Command Options
- `-h`: usage.
- `-v`: verbose messages.
- `-y` / `--yes` / `--assume-yes`: skip confirmation prompts.
- `-V`: version.
- Positional arguments: `device [size]`.
- Size suffixes: `s`, `K`, `M`, `G`, `T`, `P`.

## Global State
Important globals include:
- `devsize`: actual block device size from `BLKGETSIZE64`.
- `layout`: `struct nilfs_layout` for current filesystem geometry.
- `sustat`: segment usage statistics.
- `trunc_start`, `trunc_end`: segment range being truncated.
- Fixed batch buffers: `suinfo[256]`, `segnums[256]`.
- Shrink cleaner pacing: `nsegments_per_clean = 2`, `clean_interval = 100ms`.
- Progress bar state printed to stderr.

## Control Flow
1. `main` parses options and validates the block device.
2. It reads device size, parses optional target size, aligns target size down to sector size, and checks mount status.
3. `nilfs_resize_online` opens NILFS raw/read-write/GC-lock capable, loads layout, syncs, and dispatches:
   - `nilfs_extend_online` when `newsize > layout.devsize`.
   - `nilfs_shrink_online` when `newsize < layout.devsize`.
4. Success prints `Done.`; failure prints `Aborted.`.

## Extend Path
`nilfs_extend_online`:
- Prints old and new sizes.
- Prompts unless `-y`.
- Locks the cleaner while blocking `SIGINT` and `SIGTERM`.
- Calls `nilfs_resize(nilfs, newsize)`.
- Unlocks cleaner and restores signal mask.

This is comparatively direct because no segment evacuation is required.

## Shrink Path
`nilfs_shrink_online` is the core of the file:
- Computes the new secondary superblock offset with `NILFS_SB2_OFFSET_BYTES(newsize)`.
- Converts the target size into a target segment count.
- Checks that enough free space remains after shrink using reserved segment calculations.
- Prompts unless `-y`.
- Calls `nilfs_set_alloc_range(nilfs, 0, newsize)` to prevent new allocations past the target boundary.
- Counts in-use segments in the truncation range and optionally initializes a progress bar.
- Reclaims/moves segments from the truncation range.
- Locks the cleaner and calls `nilfs_resize`.
- Retries on `EBUSY` after reloading layout and segment stats.
- Restores allocation range on failure.

## Segment Movement
Segment evacuation is built from smaller helpers:
- `nilfs_resize_find_movable_segments`: finds reclaimable and unprotected segments, allowing empty/scrapped segments immediately.
- `nilfs_resize_find_active_segments`: finds active non-error segments and optionally totals their used blocks.
- `nilfs_resize_find_reclaimable_segments`: finds dirty, non-error, non-active reclaimable segments.
- `nilfs_resize_move_segments`: calls `nilfs_reclaim_segment` in small batches, updates progress for moved segments in the truncation range, and sleeps between batches.
- `nilfs_resize_verify_failure`: distinguishes protected segments from unreclaimable segments after partial GC failures.
- `nilfs_resize_reclaim_nibble`: fallback strategy that tries the target range, then earlier segments, then log cursor updates, then forced filesystem updates.
- `nilfs_resize_reclaim_range`: overall shrink reclamation loop.

## Active Segment Handling
When active log-writer segments block shrink:
- `nilfs_resize_move_out_active_segments` retries active eviction up to several times.
- If no movable segment can be found, `nilfs_resize_try_update_log_cursor` syncs, freezes, and thaws to converge superblock log cursors.
- If active segments remain, `nilfs_resize_prod_fs` creates a temporary `.nilfs-balloon-<pid>` file in the filesystem root, writes random/fallback pseudo-random data, syncs, unlinks it, deletes checkpoints created during the operation, and syncs again.

## Safety Measures
- Cleaner lock protects final resize operations.
- `SIGINT` and `SIGTERM` are blocked around cleaner lock and balloon-file critical sections.
- Allocation range is restored if shrink fails after range limitation.
- Confirmation is required by default.
- The command refuses unmounted devices because offline resizing is unsupported.
- Progress display is kept separate from diagnostics with `msg`.

## Notable Risks and Edge Cases
- Size parsing shifts `uint64_t` values for suffixes but does not explicitly detect overflow after shifting.
- `nilfs_resize_parse_options` accepts option string characters `M` and `P` that are not handled in the switch.
- The shrink retry loop uses `retry < 4`, while comments describe fewer retries.
- Balloon filename is PID-based and created in the filesystem root with `O_CREAT | O_TRUNC`; collision is unlikely but not impossible.
- Fallback random data uses `rand()` intentionally because cryptographic randomness is unnecessary.
- The implementation is deeply tied to NILFS segment semantics and kernel resize ioctl support; `ENOTTY` gets a specific unsupported-kernel message.
