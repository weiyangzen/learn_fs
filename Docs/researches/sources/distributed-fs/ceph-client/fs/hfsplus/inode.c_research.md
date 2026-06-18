# sources/distributed-fs/ceph-client/fs/hfsplus/inode.c

## Purpose
`inode.c` implements HFS+ inode, file, address-space, attribute, and fork handling. It bridges generic VFS file I/O and metadata operations to HFS+ extent mapping, catalog records, resource forks, metadata B-tree writeback, file flags, size changes, and explicit filesystem synchronization.

## Important APIs, types, and functions
Exported objects are `hfsplus_aops`, `hfsplus_btree_aops`, and `hfsplus_dentry_operations`. Exported functions include `hfsplus_write_begin`, `hfsplus_new_inode`, `hfsplus_delete_inode`, `hfsplus_inode_read_fork`, `hfsplus_inode_write_fork`, `hfsplus_cat_read_inode`, `hfsplus_cat_write_inode`, `hfsplus_getattr`, `hfsplus_file_fsync`, `hfsplus_fileattr_get`, and `hfsplus_fileattr_set`.

Key internal helpers are `hfsplus_read_folio`, `hfsplus_write_failed`, `hfsplus_bmap`, `hfsplus_release_folio`, `hfsplus_direct_IO`, `hfsplus_writepages`, `hfsplus_get_perms`, `hfsplus_file_open`, `hfsplus_file_release`, and `hfsplus_setattr`. The file operation table uses generic llseek/read/write/mmap/splice helpers, `hfsplus_file_fsync`, open/release tracking, and `hfsplus_ioctl`.

## Control flow
Buffered writes enter `hfsplus_write_begin()`, call `cont_write_begin()` with `hfsplus_get_block`, and truncate partially instantiated blocks through `hfsplus_write_failed()` on error. Direct I/O uses `blockdev_direct_IO()` and also trims blocks beyond `i_size` after failed extending writes. Writeback uses `mpage_writepages()`. B-tree metadata mappings use a special `release_folio` path that evicts unreferenced B-node hash entries before freeing buffers.

Opening a file rejects non-largefile callers for oversized files and increments `opencnt` on the main inode, not the resource-fork proxy. Release decrements `opencnt`; the last close truncates allocation to logical size and, for dead inodes, removes the hidden-directory catalog entry and calls `hfsplus_delete_inode()`.

`hfsplus_setattr()` validates attributes, serializes direct I/O before size changes, expands sparse ranges when growing, truncates page cache and HFS+ extents when shrinking, updates times, copies attributes, and marks the inode dirty. `hfsplus_getattr()` reports birth time and append/immutable/nodump attributes.

New inode allocation consumes `sbi->next_cnid`, initializes private extent/resource-fork/open-dir state, selects directory/file/symlink/special operation tables, adjusts file/folder counters, inserts the inode hash, marks the inode dirty, and marks the volume header dirty. Deletion decrements counters and truncates regular or symlink fork storage when the last link is gone.

Catalog read loads either folder or file catalog records, validates record length and type, maps HFS+ permissions to Linux uid/gid/mode/flags, initializes times and fork state, and selects VFS operations. Catalog write locates the catalog record by CNID, updates permissions/times/valence/subfolder count or data/resource fork fields, writes the B-tree, and marks catalog dirty bits.

`hfsplus_file_fsync()` waits dirty file data, locks the inode, syncs inode metadata into catalog/extents, explicitly writes dirty catalog/extents/attributes/allocation metadata inodes, prepares and commits the volume header, and issues a block-device flush unless `nobarrier` is set.

## State and persistence behavior
Persistent inode state lives mainly in catalog records and fork records, with overflow extents in the extents B-tree and allocation state in the allocation file. The driver has no journal in this path; consistency depends on ordered writeback, dirty bits, volume-header commits, and optional cache flushes. File/folder counters and `next_cnid` are mutable superblock state. Fork state is cached in `hfsplus_inode_info` and written back with endian conversion.

Resource forks are represented by inodes with `HFSPLUS_I_RSRC` set and a back pointer to the main inode. File flags map between HFS+ permission flags and Linux `S_IMMUTABLE`, `S_APPEND`, and `FS_NODUMP_FL`.

## Dependencies and integration points
This file depends on Linux page cache, mpage, direct I/O, generic setattr/getattr/fileattr helpers, block mapping, VFS operation tables, xattrs, catalog and extent code, B-tree/B-node helpers, volume-header commit code, and `ioctl.c`. It also integrates with `unicode.c` through `hfsplus_dentry_operations`.

## Risks and test signals
Risks include resource-fork lifetime bugs, catalog record length/type validation gaps, dirty-bit loss causing metadata not to reach disk, truncate/extend races with direct I/O, B-node cache eviction while referenced, non-journaled ordering windows, incorrect link counts for hard links encoded in `permissions.dev`, and inconsistent file flag propagation. Test signals include buffered/direct extending writes with injected errors, truncate and last-close truncation, fsync after catalog/extent/attribute/allocation changes, resource-fork open/release/eviction, hard-link catalog entries, special files, immutable/append/nodump fileattr round trips, corrupted catalog records, and `nobarrier` vs barrier flush behavior.
