# File Research: sources/block-storage/parted/libparted/fs/r/hfs/hfs.c

Main classic HFS and HFS+ open/close/resize implementation.

Classic HFS behavior:
- `hfs_open()` validates 512-byte-sector geometry, reads the MDB, opens extents/catalog files, reads allocation bitmap, duplicates geometry, and sets checked state from the unmounted bit.
- `hfs_close()` frees opened files, bad-block list, MDB, private data, geometry, and filesystem object.
- `hfs_get_resize_constraint()` fixes start alignment and computes minimum size from `hfs_get_empty_end() + 2`.
- `hfs_resize()` supports same-start shrink only, clears unmounted bit, packs data away from the tail, verifies freed tail, marks out-of-volume blocks used, updates MDB block/free counts and geometry, then writes MDB.

HFS+ behavior:
- `hfsplus_open()` detects optional HFS wrapper, sets `plus_geom`, reads volume header, validates HFS+/HFSX signature/version, replays journal if needed, opens special files, loads allocation bitmap, and sets checked state from unmounted/inconsistent flags.
- `hfsplus_close()` frees bad-block list, allocation maps, special files, wrapper, geometry, volume header, and private state.
- `hfsplus_get_resize_constraint()` uses `hfsplus_get_min_size()`.
- `hfsplus_volume_resize()` supports shrink of the HFS+ volume: clears unmounted bit, sets implementation code, packs data, updates total/free blocks, marks out-of-volume and reserved tail blocks used, writes allocation bitmap, and updates volume header.
- `hfsplus_wrapper_update()` updates the HFS wrapper MDB, wrapper allocation bitmap, and bad-block extents record for embedded HFS+.
- `hfsplus_resize()` orchestrates bare or wrapped HFS+ shrink with nested timers.

Optional debug code:
- Under `HFS_EXTRACT_FS`, can extract low-level HFS/HFS+ metadata files for debugging rather than repair.

Important dependencies:
- Probe helpers, file accessors, advanced FS helpers, relocation modules, and journal replay.
- Packed on-disk structures from `hfs.h`.

Notable constraints:
- No grow or start-move support for HFS/HFS+ resize.
- HFS+ journal replay can require restarting Parted if the volume header or MDB changed.
