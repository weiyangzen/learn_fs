# sources/distributed-fs/ceph-client/fs/hfs/part_tbl.c

Purpose: parses old and new Macintosh partition maps to locate the selected HFS partition when the MDB is not found at the current device/session offset.

Important APIs and control flow: `struct new_pmap` models an Apple partition map entry with signature, map count, physical start/count, name, and type. `struct old_pmap` models the older fixed array of 42 entries. `hfs_part_find()` reads the first partition-map block with `sb_bread512()`, switches on old (`HFS_OLD_PMAP_MAGIC`) or new (`HFS_NEW_PMAP_MAGIC`) signatures, scans entries for HFS/TFS1 or `Apple_HFS`, applies the mount option selected partition index when present, and updates `part_start`/`part_size`.

State and persistence: this file is read-only. It mutates only caller-owned sector offsets used by `hfs_mdb_get()` to reread the MDB and compute filesystem geometry.

Dependencies and integration: depends on `hfs_fs.h` constants and `HFS_SB(sb)->part`. It is called from `mdb.c` during mount discovery after an initial direct MDB check fails.

Risks and test signals: old-map parsing can return the last matching entry rather than breaking, while new-map parsing stops at the first match. The code assumes 512-byte partition-map blocks and limited structural validation. Tests should cover explicit `part=` selection, invalid signatures, truncated maps, multiple HFS entries, and loop/CD images with both direct and partitioned layouts.
