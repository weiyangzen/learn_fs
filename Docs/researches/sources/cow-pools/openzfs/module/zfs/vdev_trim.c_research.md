# File Research: sources/cow-pools/openzfs/module/zfs/vdev_trim.c

## Purpose
Implements OpenZFS TRIM/discard support for vdevs, including manual `zpool trim`, automatic background trimming of recently freed ranges, simple one-shot leaf trimming, and whole-device L2ARC trim.

## Main Responsibilities
- Persists manual TRIM state, progress, and options in leaf vdev ZAP entries.
- Issues physical `zio_trim()` requests with max/min extent sizing, optional secure trim, per-leaf queue limiting, and manual rate limiting.
- Walks metaslab free/trim range trees and translates logical top-level ranges into physical leaf-vdev ranges.
- Runs manual TRIM threads per leaf vdev.
- Runs autotrim threads per top-level vdev, using `ms_trim` recently-freed ranges and a TXG-batched metaslab stride.
- Stops/restarts manual trim and autotrim safely during export, removal, detach, offline, expansion, and property changes.
- Trims full L2ARC cache devices when needed and clears the L2ARC device header afterward.

## Key Data And State
- Tunables:
  - `zfs_trim_extent_bytes_max`: max command size, default 128 MiB.
  - `zfs_trim_extent_bytes_min`: min useful command size, default 32 KiB.
  - `zfs_trim_metaslab_skip`: manual partial-trim behavior for uninitialized metaslabs.
  - `zfs_trim_queue_limit`: max queued TRIM I/Os per leaf.
  - `zfs_trim_txg_batch`: minimum TXG spacing between autotrim visits to a metaslab.
- `trim_args_t`: per-range walker context containing target leaf vdev, disabled metaslab, range tree, trim type, extent limits, flags, start time, and bytes done.
- Per-vdev fields managed here include `vdev_trim_state`, `vdev_trim_thread`, `vdev_trim_last_offset`, `vdev_trim_rate`, `vdev_trim_partial`, `vdev_trim_secure`, `vdev_trim_inflight[]`, and autotrim thread/cv fields.

## Important Functions
- `vdev_trim_change_state()`: transitions manual TRIM state, schedules ZAP persistence, records options, emits sysevents/history, and wakes waiters on non-active transitions.
- `vdev_trim_zap_update_sync()`: sync task that writes manual TRIM offset, action time, rate, partial/secure flags, and state to the leaf ZAP.
- `vdev_trim_range()` / `vdev_trim_ranges()`: issue sized physical trim I/O, enforce rate/queue limits, update stats, wait for completion before re-enabling metaslabs, and select callback by trim type.
- `vdev_trim_calculate_progress()` / `vdev_trim_load()`: reconstruct manual TRIM progress from persisted offset and current metaslab free state.
- `vdev_trim_thread()`: manual trim worker that sequentially disables metaslabs, loads allocatable space, translates ranges for one leaf, issues trims, and completes/cancels state.
- `vdev_trim()` / `vdev_trim_stop()` / `vdev_trim_stop_all()` / `vdev_trim_restart()`: public lifecycle operations for manual trim.
- `vdev_autotrim_thread()`: top-level background worker that periodically swaps `ms_trim`, builds per-leaf trim trees, issues best-effort automatic trims, and re-enables metaslabs after safe TXG waits.
- `vdev_autotrim()`, `vdev_autotrim_kick()`, `vdev_autotrim_stop_all()`, `vdev_autotrim_restart()`: autotrim lifecycle operations.
- `vdev_trim_l2arc_thread()` / `vdev_trim_l2arc()`: trim full cache devices and update L2ARC headers.
- `vdev_trim_simple()`: helper for direct leaf vdev trim over a supplied physical range.

## Control Flow Notes
- Manual TRIM disables one metaslab at a time so no allocation can race ahead of outstanding lower-priority trim I/O for the same ranges.
- Manual TRIM progress is offset-based and persistent; autotrim has no on-disk progress and is best effort.
- Autotrim processes non-consecutive metaslab groups to distribute trim load and enforce a minimum revisit interval.
- Manual trim yields over autotrim: autotrim skips leaves already running a manual trim and manual trim vacates `ms_trim` for the processed metaslab.
- TRIM is suppressed for detached/unwritable vdevs, vdevs being removed, and vdevs undergoing raidz expansion.

## Error Handling And Invariants
- Manual trim rolls back the last persisted offset when a trim fails due to vdev unavailability.
- Trim callbacks update per-vdev trim error counters and SPA I/O stats, then decrement in-flight counters and release config locks.
- `vdev_trim_ranges()` waits for all manual trim I/O before returning so re-enabled metaslabs cannot receive writes before overlapping trim completes.
- Autotrim abandons unprocessed `ms_trim` ranges when autotrim is disabled, reclaiming memory.
- Assertions protect against trimming non-leaf/non-concrete/detached/removing/expanding vdevs.

## Dependencies
Depends on SPA config locks, DMU transactions, DSL sync tasks, ZAP leaf metadata, metaslab range trees, vdev translation, zio trim I/O, ARC/L2ARC state, pool autotrim properties, and vdev removal/raidz-expansion state.

## Research Notes
TRIM safety hinges on metaslab disable/enable ordering, in-flight trim accounting, and config-lock release by callbacks. Tests should cover manual resume, cancellation, L2ARC removal, autotrim property toggles, unavailable devices, secure trim, and interaction with vdev removal/expansion.
