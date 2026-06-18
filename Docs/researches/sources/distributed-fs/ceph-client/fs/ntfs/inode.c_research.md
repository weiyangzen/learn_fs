# sources/distributed-fs/ceph-client/fs/ntfs/inode.c

Purpose: owns NTFS inode lifecycle, MFT record loading/writing, fake attribute and index inodes, extent inode attachment, attribute-list creation, VFS operation selection, mount-time `$MFT` bootstrap, eviction, truncate/initialized-size helpers, and raw attribute pread/pwrite.

Important APIs and functions:
- `ntfs_iget()`, `ntfs_attr_iget()`, and `ntfs_index_iget()` obtain normal, attribute, and index inodes through `iget5_locked()`.
- `ntfs_test_inode()` and `ntfs_init_locked_inode()` key inode-cache identity by MFT number plus optional attribute type/name.
- `__ntfs_init_inode()` initializes NTFS-private inode state, locks, runlists, index/compression fields, extent state, and cached MFT locations.
- `ntfs_read_locked_inode()`, `ntfs_read_locked_attr_inode()`, and `ntfs_read_locked_index_inode()` populate VFS and NTFS inode state from MFT records and attributes.
- `ntfs_read_inode_mount()` bootstraps the `$MFT` inode before normal page-cache based MFT mapping is available.
- `__ntfs_write_inode()` syncs standard information, filename index entries, mapping pairs, base MFT records, and extent MFT records.
- `ntfs_inode_sync_filename()` updates parent directory `$I30` entries with current sizes, flags, times, and reparse tag.
- `ntfs_inode_attach_all_extents()` and `ntfs_inode_add_attrlist()` manage multi-record inodes.
- `ntfs_inode_attr_pread()` and `ntfs_inode_attr_pwrite()` provide byte I/O for fake attribute inodes.

Control flow:
- Normal inode read sets mount uid/gid defaults, maps the MFT record, validates in-use/base record/link count, loads `$STANDARD_INFORMATION`, optional `$ATTRIBUTE_LIST`, optional EA/WSL metadata, determines mode from directory/reparse/data state, validates directory `$INDEX_ROOT` or file `$DATA`, sets runlist/compression/sparse/encrypted sizes, releases the MFT record, and installs VFS operations.
- Attribute inode read mirrors base inode metadata, looks up the selected attribute, validates resident/nonresident constraints and compression/encryption/sparse flags, sets size/block accounting, and pins the base inode with `igrab()`.
- Index inode read validates `$INDEX_ROOT`, optional `$INDEX_ALLOCATION`, matching `$BITMAP`, block size, VCN size, and then pins the base inode.
- Mount-time `$MFT` loading reads record 0 directly from the block device, applies MST fixups, optionally loads `$ATTRIBUTE_LIST`, incrementally decompresses `$DATA` mapping pairs, calls normal inode read once the first extent is known, and then restores no-VFS-operation tables for `$MFT`.
- Writeback ignores fake attribute inodes, maps the base MFT record, updates dirty runlist mapping pairs, syncs standard information, optionally syncs filename indexes while the filesystem is active, writes base and extent records, and marks volume errors on non-memory failures.
- Eviction truncates pages, frees unlinked base inode clusters and extent MFT records, commits dirty linked inodes, frees extent arrays, releases base references from fake inodes, and frees cached runlists/attrlists/names/reparse targets.
- Raw attribute pwrite enlarges/truncates the attribute as needed, writes resident data into the MFT record and page-cache folio, or writes nonresident data through folios and optional synchronous bios.

State and persistence behavior:
- NTFS inode state includes runlist, size trio, MFT sequence, flags, attrlist, compression geometry, directory index geometry, extent list/base pointer, cached target, deallocation cluster count, and cached MFT LCNs.
- `NInoDirty`, `NInoRunlistDirty`, `NInoFileNameDirty`, `NInoAttrList`, `NInoIndexAllocPresent`, and related bits coordinate persistence between helpers.
- Standard information sync writes NTFS creation/mtime/ctime/atime and file attributes without redirtying the VFS inode.
- Filename sync persists duplicated NTFS filename metadata in every parent directory index.
- Attribute-list creation can move records out of the base MFT record to free space, then rolls back by moving attributes back and removing the added record on failure.
- Unlinked inode deletion frees nonresident clusters, extent MFT records, and base MFT record, but logs and leaves inconsistent metadata on some failures.

Dependencies and integration points:
- Depends on allocation, time conversion, index, attrlist, reparse, EA, attrib, iomap, and object-id support.
- Provides inode operations consumed by `file.c`, directory/index open helpers consumed by `dir.c` and `index.c`, and raw attribute I/O consumed by `ea.c` and `index.c`.
- Integrates with VFS inode cache, folio/page cache, writeback, superblock mount options, block-device reads/writes, and lockdep classes.
- Uses `ntfs_make_symlink()` to convert reparse points to symlinks and EA helpers to populate WSL metadata.

Risks and edge cases:
- `ntfs_inode_close()` assumes `base_ni = ni->ext.base_ntfs_ino` before checking for NULL, so calling it on a base inode without a base pointer would dereference NULL; comments imply it is for extent-style closing but the public name is broad.
- Several corruption paths mark volume errors and advise chkdsk; tests should confirm when `NVolSetErrors()` is raised versus suppressed.
- Mount-time `$MFT` bootstrap has circular dependency assumptions around first `$DATA` extent availability.
- Attribute-list creation rollback is complex and can leave attributes moved if rollback helpers fail.
- Raw nonresident synchronous pwrite computes cluster counts from `attr_len`; partial-page writes across multiple clusters require careful coverage.
- Eviction can delete unlinked metadata while earlier writeback/truncate failures have already logged inconsistency, so fault injection is important.

Test signals:
- Inode load tests should cover normal files, directories, reparse symlinks, missing `$DATA` for `$Extend` system files, resident/nonresident data, sparse/compressed/encrypted validation, WSL EAs, and invalid attrlist/index bounds.
- Mount tests should exercise `$MFT` with single and multiple extents, resident and nonresident attrlists, bad MST fixups, and oversized record rejection.
- Writeback tests should cover standard information updates, dirty runlist mapping-pair updates, filename index synchronization for hardlinks, extent record writes, and error handling for `-ENOMEM` versus I/O errors.
- Extent/attrlist tests should force adding attrlists, moving attributes out of the base record, attaching all extents, and rollback failures.
- Raw attr I/O tests should cover resident read/write, nonresident buffered write, synchronous write, enlarge/truncate transitions, compressed/encrypted rejection, and page-cache consistency.
