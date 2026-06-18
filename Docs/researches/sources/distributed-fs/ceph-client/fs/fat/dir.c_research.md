# sources/distributed-fs/ceph-client/fs/fat/dir.c

## Purpose
`dir.c` implements FAT directory entry iteration, VFAT long-name parsing, short-name display conversion, directory ioctls, directory emptiness/scanning helpers, and low-level slot insertion/removal. It is the shared directory engine used by both `msdos` and `vfat` namei layers.

## Important APIs, Types, and Functions
- `fat_get_entry()` and `fat__get_entry()` walk directory entries by logical byte offset, using `fat_bmap()` and block reads.
- `fat_parse_long()` reconstructs VFAT long names from `ATTR_EXT` slots, validates ordering and alias checksums, and falls back cleanly on malformed slot chains.
- `fat_parse_short()` converts 8.3 entries into visible names using mount shortname policy and NLS conversion.
- `fat_search_long()`, `fat_scan()`, and `fat_scan_logstart()` locate entries by long/short name or start cluster and fill `struct fat_slot_info`.
- `__fat_readdir()` backs normal readdir and legacy `VFAT_IOCTL_READDIR_*` ioctls.
- `fat_dir_empty()`, `fat_subdirs()`, and `fat_get_dotdot_entry()` provide namei and NFS helper logic.
- `fat_add_entries()`, `fat_alloc_new_dir()`, and `fat_remove_entries()` mutate directory slots.

## Control Flow
Directory reads use `fat_get_entry()` as a fast path when the next entry is still in the same buffer; otherwise `fat__get_entry()` maps the next directory block, optionally readaheads an entire cluster, and reads the block. `__fat_readdir()` serializes on `sbi->s_lock`, emits synthetic root `.` and `..`, filters free/deleted/volume entries, optionally reconstructs long names, and emits either the long name or the short name to the VFS `dir_context`.

Search uses similar parsing but compares the requested name against both the short display form and reconstructed VFAT long name. On a match, `fat_slot_info` records the starting slot offset, slot count, short entry pointer, buffer head, and encoded `i_pos`.

Mutation is staged for crash tolerance. `fat_remove_entries()` marks the short slot deleted first, then removes preceding long slots. `fat_add_entries()` first searches for enough free contiguous slots, writes long slots before the short slot, and if no space exists allocates one or two new clusters, initializes them with the new entries, appends the cluster chain, and updates directory size.

## State and Persistence
Persistent directory state is a sequence of 32-byte `struct msdos_dir_entry` and `struct msdos_dir_slot` records. Dirty buffers are tracked through `MSDOS_I(dir)->i_metadata_bhs` using metadata-buffer helpers, then synchronously flushed for `IS_DIRSYNC(dir)`. Directory ctime/mtime are truncated via `fat_truncate_time()`, i_version is bumped on removals and additions where needed by callers, and cluster allocation changes are delegated to `fatent.c` and `misc.c`.

## Dependencies and Integration Points
`dir.c` depends on block mapping from `cache.c`, cluster allocation and FAT entry writes from `fatent.c` / `misc.c`, timestamp conversion from `misc.c`, inode lookup/build from `inode.c`, and VFS directory APIs. `namei_msdos.c` and `namei_vfat.c` call the exported scan/add/remove helpers. `nfs.c` uses dotdot and logstart scanning when reconnecting exported directories.

## Risks and Test Signals
Malformed long-name slot chains are common on damaged media; this code must distinguish invalid records from EOF and from a short entry that is not part of a long name. Slot insertion spans block and cluster boundaries, so rollback through `__fat_remove_entries()` matters after partial writes. Useful tests include VFAT long-name lookup/readdir, deleted slot reuse, directory growth at 512-byte cluster boundaries, sync-directory mounts, root directory limits on FAT12/16, hidden/dots display on msdos, and NFS reconnect.
