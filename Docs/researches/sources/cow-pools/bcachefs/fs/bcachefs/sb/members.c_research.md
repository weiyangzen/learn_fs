# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.c

This file implements superblock member-device metadata handling, validation, text output, error tracking, B-tree allocation bitmaps, member slot allocation, and member-field upgrades.

Key responsibilities:
- Reports pointers to missing/removed devices and schedules allocation-check recovery passes.
- Exports member IO error strings and IOPS measurement names.
- Reads members from v1 or v2 sections and returns mutable v2 member pointers.
- Initializes v2 members from v1 and grows `member_bytes` to the current `struct bch_member` size.
- Mirrors v2 members back to v1 while old metadata compatibility requires it.
- Validates member geometry: bucket count, bucket range, bucket size versus block/B-tree node size, B-tree bitmap shift, and freespace/feature consistency.
- Renders detailed and short member/device descriptions.
- Validates/renders both `members_v1` and `members_v2` superblock fields.
- Serializes runtime per-device error counters into the superblock and loads member info back into `bch_dev`.
- Renders and resets device IO error counters, including reset baseline and flush errors.
- Maintains per-member “range has B-tree nodes” bitmaps to speed recovery scans.
- Runs B-tree bitmap GC by scanning B-tree roots/interior levels and rewriting compacted member bitmaps.
- Schedules daily/rate-limited bitmap GC when marked B-tree bitmap coverage is much larger than current B-tree allocation.
- Counts existing member devices, allocates new member slots, cleans deleted member UUID markers, and upgrades missing member fields such as rotational state.

Important invariants:
- `members_v2` is canonical for modern metadata; `members_v1` is kept only for compatibility when required.
- `member_bytes` allows forward-compatible larger member records but must be nonzero and large enough for current access during validation/resizing.
- Deleted devices use `BCH_SB_MEMBER_DELETED_UUID`; zero UUID slots may be reused, preferring the least-recently-mounted slot when full.
- B-tree bitmap marking may resize bitmap granularity by folding existing bits; the shift must stay below `BCH_MI_BTREE_BITMAP_SHIFT_MAX`.
- Bitmap GC writes updated member bitmap state under `sb_lock` and persists it with `bch2_write_super()`.

Dependencies include allocation/bucket helpers, disk groups, replicas, B-tree iterators/cache, progress reporting, recovery pass scheduling, superblock IO, init/error handling, and per-device runtime state.
