# File Research: sources/block-storage/lvm2/lib/metadata/lv.h

Purpose: defines the in-memory logical volume structures and declares LV relationship, property, reporting, kernel-state, mutation, activation, percentage, and RAID-health helper APIs.

Read coverage: complete file read, 224 lines.

Key contents:
- Defines `struct lv_list`, `struct logical_volume`, `struct historical_logical_volume`, and `struct generic_logical_volume`.
- `struct logical_volume` contains LVID/name/VG, profile, status flags, size and LE count, allocation/read-ahead/minor-major state, snapshot counters/links, segment/tag/user lists, historical ancestry links, timestamps, lockd state bits, hostname, and lock args.
- Historical LV support represents removed LVs through dummy live `logical_volume` objects whose `this_glv` points to historical metadata.
- Declares LV dependency discovery helpers for parent, conversion layer, origin, mirror log, data LV, metadata LV, and pool LV.
- Declares LV property helpers for sizes, segment properties, lock holder, committed LV lookup, mirror/RAID sync, segment device/range lists, and RAID health.
- Declares kernel-property helpers for major/minor/read-ahead/discards.
- Declares LV mutation helpers for creation metadata, name/VG assignment, and activation changes.
- Declares many report-string duplication helpers and percent calculation helpers.

Dependencies:
- Includes `lib/metadata/vg.h` and relies on metadata types such as `union lvid`, `lv_segment`, `profile`, `dm_list`, `dm_pool`, `dm_percent_t`, and activation enums.
- Implemented primarily by `lv.c`, with some declarations implemented in other metadata modules.

Risk and edge cases:
- `lvid` must remain the first member of `struct logical_volume` because report code relies on its offset.
- Historical LV representation intentionally blurs live and removed LV handling, so callers must check `lv_is_historical()` when accessing fields that may be blank.
- Function declarations expose many allocation-returning helpers; callers must pass a valid memory pool and handle `NULL`.
