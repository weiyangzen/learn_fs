# File Research: sources/block-storage/lvm2/lib/writecache/writecache.c

## Purpose
Implements LVM2 segment-type support for dm-writecache. It imports/exports writecache metadata, probes target support, records optional writecache settings, and emits writecache target lines during activation.

## Main Responsibilities
- Import an origin LV, fast writecache LV, writecache block size, and optional writecache tuning settings.
- Export only configured optional settings.
- Track kernel support for `cleaner` and `max_age`.
- Add `writecache` dm target using origin and cache-device UUIDs.
- Register the `writecache` segment type.

## Key Functions
- `_writecache_text_import()` reads `origin`, `writecache`, `writecache_block_size`, and settings such as watermarks, writeback jobs, autocommit values, FUA/nofua, cleaner, max age, metadata-only, pause-writeback, and one arbitrary key/value setting.
- `_writecache_text_export()` serializes the base relationship and all settings whose `_set` flags are present.
- `_target_present()` probes `dm-writecache` target version and records whether kernel minor version supports cleaner/max-age.
- `writecache_cleaner_supported()` exposes cleaner support to the rest of LVM.
- `_writecache_add_target_line()` validates the segment, suppresses unsupported settings on older kernels, checks whether the cache LV is on persistent memory, and calls `dm_tree_node_add_writecache_target()`.
- `init_writecache_segtypes()` registers `SEG_TYPE_NAME_WRITECACHE`.

## Edge Cases and Invariants
- Both origin and cache LVs must resolve during metadata import.
- The writecache LV is added to `segs_using_this_lv`.
- Unsupported `cleaner` and `max_age` settings are cleared with warnings rather than failing activation.
- Device UUID layers are fixed as `"real"` for origin and `"cvol"` for cache volume.
