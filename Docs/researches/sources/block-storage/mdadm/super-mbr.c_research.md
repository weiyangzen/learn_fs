# File Research: sources/block-storage/mdadm/super-mbr.c

Purpose: pseudo metadata handler for DOS/MBR partition tables.

Behavior:
- MBR is not usable for creating or assembling md arrays directly.
- It lets mdadm examine, load, store, and report partition table state for devices whose partitions may be used elsewhere.

Key functions:
- `load_super_mbr()` reads the first sector, validates `MBR_SIGNATURE_MAGIC`, and stores the 512-byte MBR.
- `examine_mbr()` prints magic and non-empty partition entries, using direct `sb->parts[i]` access because entries are not properly aligned.
- `store_mbr()` preserves the existing boot/pad area from disk, writes the updated MBR, calls `fsync()`, and issues `BLKRRPART`.
- `getinfo_mbr()` fills mdinfo text/name `"mbr"` and computes component size from the highest partition end.
- `validate_geometry()` always rejects MBR as normal md metadata.

Risks and notes:
- Store path allocates `old` but if the final write fails, `old` has already been freed and `super` remains owned by `st`.
- The code intentionally avoids treating partition tables as real RAID superblocks.
