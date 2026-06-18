# sources/distributed-fs/ceph-client/fs/adfs/inode.c

## Purpose
`inode.c` translates ADFS object records into Linux inodes and implements regular-file address-space behavior, attribute conversion, timestamp conversion, setattr, and directory-entry metadata writeback.

## Important APIs, types, and functions
Key entry points are `adfs_iget()`, `adfs_setattr()`, and `adfs_write_inode()`. Internal helpers include `adfs_get_block()`, `adfs_read_folio()`, `adfs_writepages()`, `adfs_write_begin()`, `_adfs_bmap()`, `adfs_atts2mode()`, `adfs_mode2atts()`, `adfs_adfs2unix_time()`, and `adfs_unix2adfs_time()`. The file defines `adfs_aops` for buffer-head based regular-file I/O.

## Control flow
`adfs_iget()` creates a new inode from an `object_info`, fills UID/GID from superblock defaults, stores ADFS parent/object/load/exec/attribute fields, converts permissions and time, then attaches directory or regular-file operations. Reads call `block_read_full_folio()` and map logical blocks through `__adfs_block_map()`. Write begin uses `cont_write_begin()`, but block creation returns `-EIO`, so the implementation remains allocation-limited. `adfs_write_inode()` reconstructs an `object_info` and delegates to `adfs_dir_update()`.

## State and persistence
Per-inode ADFS state includes `parent_id`, `indaddr`, `loadaddr`, `execaddr`, `attr`, and `mmu_private`. ADFS uses object IDs as inode numbers because metadata is stored in directories, so parent stability matters for writeback.

## Dependencies and integration points
It depends on `adfs_map_lookup()` through block mapping, directory update code, generic writeback/mpage helpers, VFS setattr validation, and superblock masks for permission translation.

## Risks and test signals
Risks include unsupported allocation/truncation paths, cross-directory rename assumptions, lossy permission conversion, stamped versus unstamped timestamp handling, and inode-number aliasing. Test signals include iget for dirs/files/symlinks, filetype `0xfc0` and `0xfe6`, chmod/chown rejection, mtime centisecond round trips, bmap, and writeback after setattr.
