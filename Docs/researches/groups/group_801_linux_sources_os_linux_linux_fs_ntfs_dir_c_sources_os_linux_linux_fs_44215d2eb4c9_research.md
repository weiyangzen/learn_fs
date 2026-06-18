# Group Research: group_801_linux_sources_os_linux_linux_fs_ntfs_dir_c_sources_os_linux_linux_fs_44215d2eb4c9

Subset scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/dir.c -->
# File Research: sources/os/linux/linux/fs/ntfs/dir.c

## Purpose
Implements NTFS directory operations for the Linux NTFS driver, centered on `$I30` directory indexes: name lookup, directory iteration, empty-directory checks, open/release state, and directory fsync.

## Key Elements
Defines the global little-endian `$I30` name used by directory index attributes. `ntfs_lookup_inode_by_name()` searches a directory's `$INDEX_ROOT` first, then descends through `$INDEX_ALLOCATION` blocks when the B+tree has child nodes. It performs exact case-sensitive matching first, keeps a single case-insensitive fallback for non-case-sensitive mounts and DOS namespace aliases, and returns an NTFS MFT reference rather than a plain inode number.

Directory iteration is built around `ntfs_readdir()`, `ntfs_index_ctx_get()`, `ntfs_index_walk_down()`, and `ntfs_index_next()`. It emits `.` and `..`, walks index entries in collation order, converts UTF-16 NTFS names through the mount NLS table, skips DOS-only aliases, root self references, optionally hidden/system files, and chooses `d_type` from directory, reparse tag, or regular file attributes. `struct ntfs_file_private` stores the last key and logical position so a later iterate call can resume through `ntfs_index_lookup()` instead of restarting with a linear walk.

The file adds directory-oriented readahead in two places: `ntfs_ia_blocks_readahead()` reads ahead index allocation pages, while an rb-tree of `ntfs_index_ra` ranges batches readahead for referenced MFT records during iteration.

## Dependencies And Integration
Depends on `dir.h`, `mft.h`, `ntfs.h`, `index.h`, and `reparse.h`. It calls low-level MFT mapping, attribute search, index validation, NTFS collation/name comparison, reparse d_type classification, and generic VFS directory/file operation helpers. `ntfs_dir_ops` wires the implementation into VFS `.iterate_shared`, `.fsync`, `.open`, `.release`, ioctl, compat ioctl, and lease hooks.

## Behavior/Risks
Index parsing is corruption-sensitive and uses extensive bounds checks for entry length, key length, index block VCN, INDX magic, block size, and page-boundary assumptions. Lookup allocates `struct ntfs_name` only when dcache alias handling needs the on-disk spelling or DOS-name marker. `ntfs_check_empty_dir()` treats a directory as empty only when the resident index root contains only the terminal entry. `ntfs_dir_fsync()` is broad: it writes parent directory index allocation inodes for hard links, the directory data, the index bitmap, MFT bitmap, LCN bitmap, `$MFT`, and finally syncs the block device.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/dir.h -->
# File Research: sources/os/linux/linux/fs/ntfs/dir.h

## Purpose
Declares the NTFS directory lookup and empty-directory interfaces plus the small result structure used to report name aliasing information back to namei code.

## Key Elements
`struct ntfs_name` packages the matched MFT reference, NTFS file-name namespace type, UTF-16 name length, and optional little-endian UTF-16 name payload. `ntfs_lookup_inode_by_name()` uses it when a case-insensitive or DOS namespace match requires callers to handle dcache aliasing against the canonical long name. The header also exports the global `$I30` UTF-16 constant and `ntfs_check_empty_dir()`.

## Dependencies And Integration
Includes `inode.h` for `struct ntfs_inode` and related NTFS types. The declarations are consumed by NTFS name lookup, directory operation, inode sync, index, and xattr code that needs directory `$I30` access.

## Behavior/Risks
The `ntfs_name` flexible array is packed and allocated to exact name size by callers. Consumers must respect the documented ownership convention: lookup may allocate a result, may set `*res` to NULL for exact non-DOS matches, and uses `len == 0` for DOS namespace matches where only the MFT reference/type is needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/ea.c -->
# File Research: sources/os/linux/linux/fs/ntfs/ea.c

## Purpose
Implements NTFS extended attribute handling, Linux xattr exposure, WSL metadata EAs, DOS/NTFS attribute xattrs, and optional POSIX ACL storage on top of NTFS `AT_EA` and `AT_EA_INFORMATION`.

## Key Elements
`ntfs_get_ea()` and `ntfs_set_ea()` read, replace, create, append, or remove EA entries while keeping `EA_INFORMATION` query length, packed length, and needed-EA count coherent. `ntfs_ea_lookup()` walks the packed EA list with size and alignment checks, and `ntfs_write_ea()` writes through an attribute inode using `ntfs_inode_attr_pwrite()`, optionally truncating old trailing data.

WSL metadata support maps `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` to Linux uid, gid, mode, and device number through `ntfs_ea_get_wsl_inode()` and `ntfs_ea_set_wsl_inode()`. Generic xattr listing enumerates EA names from `AT_EA`, while `ntfs_getxattr()` and `ntfs_setxattr()` special-case `system.dos_attrib`, `system.ntfs_attrib`, and `system.ntfs_attrib_be` before falling back to EA storage.

`ntfs_new_attr_flags()` reconciles NTFS file attribute bits with resident/non-resident attribute record flags for sparse and compressed regular files. With POSIX ACL support, ACLs are serialized to xattrs, cached in the inode, and mode changes are mirrored back to `$LXMOD`.

## Dependencies And Integration
Uses Linux xattr and POSIX ACL APIs plus NTFS layout, attribute, index, directory, and EA headers. It relies on `ntfs_attr_readall()`, `ntfs_attr_add/remove/exist()`, `ntfs_attr_truncate()`, MFT record mapping, and attribute record resizing/mapping-pair update helpers.

## Behavior/Risks
EA mutation has partial rollback limits: `EA_INFORMATION` may be updated before `AT_EA`, so errors are surfaced and MFT records are dirtied carefully. Name length is capped at 255 bytes. Sparse/compressed flag changes are rejected for non-empty non-resident files and for invalid sparse+compressed combinations. Most public entry points reject operations after forced volume shutdown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/ea.h -->
# File Research: sources/os/linux/linux/fs/ntfs/ea.h

## Purpose
Declares NTFS extended attribute, WSL metadata, xattr listing, and optional POSIX ACL interfaces.

## Key Elements
Defines `NTFS_EA_UID`, `NTFS_EA_GID`, and `NTFS_EA_MODE` bit flags used to select which WSL metadata EAs should be written. Exports `ntfs_xattr_handlers`, WSL EA get/set helpers, `ntfs_listxattr()`, and ACL hooks when `CONFIG_NTFS_FS_POSIX_ACL` is enabled.

## Dependencies And Integration
Included by file and inode operation code to bind Linux inode operations to NTFS EA-backed metadata. When POSIX ACL support is disabled, `ntfs_get_acl` and `ntfs_set_acl` are defined as NULL so inode operation tables can be built unconditionally.

## Behavior/Risks
The interface assumes callers hold the appropriate NTFS MFT record mutex around low-level EA updates where needed. `ntfs_ea_set_wsl_inode()` can optionally return the packed EA size for on-disk FILE_NAME metadata updates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/ea.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/file.c -->
# File Research: sources/os/linux/linux/fs/ntfs/file.c

## Purpose
Provides NTFS regular-file VFS operations: open/release, fsync, setattr/getattr, read/write iterators, mmap preparation, fiemap, symlink target lookup, filesystem ioctls, and fallocate range operations.

## Key Elements
`ntfs_file_open()` rejects shutdown volumes, enforces 32-bit page-cache limits, and enables nowait and direct-I/O capability. `ntfs_file_release()` trims unused preallocated hole runlist tail space for non-compressed files. `ntfs_file_fsync()` writes dirty page ranges, MFT records, parent directory index allocations, dirty non-resident named attributes, volume bitmaps, `$MFT`, the block device, and issues a flush on success.

Size and metadata changes go through `ntfs_setattr()` and `ntfs_setattr_size()`, which reject compressed/encrypted size changes, update NTFS readonly flags, apply masks, and persist uid/gid/mode to WSL EAs. `ntfs_getattr()` reports NTFS birth time, compressed/encrypted/immutable/append attributes, adjusted block counts, and DIO alignment for normal regular files.

Read/write paths use iomap: buffered reads delegate to `generic_file_read_iter()`, aligned direct reads use `iomap_dio_rw()`, writes support compressed-file writes through `ntfs_compress_write()`, direct writes with buffered fallback, and buffered iomap writes. Error paths roll back initialized size and data size when possible. mmap write faults are handled by iomap page-mkwrite and shared writable mappings pre-extend initialized size.

The ioctl layer supports forced shutdown, get/set filesystem label, compat ioctl forwarding, and FITRIM. Fallocate supports allocate/keep-size, punch hole, collapse range, and insert range by combining page-cache invalidation, cluster alignment checks, sparse checks, runlist transformations, and inode size updates.

## Dependencies And Integration
Depends on Linux writeback, blkdev, iomap, uio, compat, fallocate, POSIX ACL, file locks, plus NTFS allocation, reparse, EA, iomap, and bitmap helpers. Exports `ntfs_file_ops`, regular-file inode ops, symlink inode ops, special inode ops, and empty ops used for inaccessible system files such as `$MFT`.

## Behavior/Risks
Compressed and encrypted files have intentionally limited support: no encrypted writes, no compressed DIO, no compressed mmap, and no compressed/encrypted size or fallocate transformations. Range operations require cluster alignment except punch-hole edge zeroing. Many operations mark the volume dirty before metadata-changing writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/index.c -->
# File Research: sources/os/linux/linux/fs/ntfs/index.c

## Purpose
Implements the generic NTFS index B+tree engine used by directories and NTFS metadata indexes, including lookup, traversal, insertion, block splitting, bitmap management, deletion, and dirty writeback of index blocks.

## Key Elements
`ntfs_index_context` instances are allocated by `ntfs_index_ctx_get()` and hold the current root/block entry, attribute context, index allocation inode, parent VCN stack, parent positions, block geometry, and dirty state. `ntfs_index_lookup()` locates keys by reading resident `$INDEX_ROOT`, validating collation rules, descending into `$INDEX_ALLOCATION` blocks via child VCNs, and returning either a found entry or the insertion position for `-ENOENT`.

The file contains low-level index entry helpers for first/next/previous/last entry lookup, deletion, insertion, VCN pointer access, duplication with or without child VCN, and entry counting. Validation routines check index entry key/data bounds and index block magic, VCN, allocation size, entry offset, and index length.

Mutation support manages `$BITMAP` for index blocks (`ntfs_ibm_add()`, set/clear/get-free), creates `$INDEX_ALLOCATION` when a small resident root becomes large, moves root entries into a new index block (`ntfs_ir_reparent()`), expands or truncates resident roots, splits full blocks around a median, propagates medians upward, and retries when splits change the tree shape. `ntfs_index_add_filename()` wraps FILE_NAME attributes into directory index entries.

Deletion handles simple root/block removal, internal-node removal by replacing with successor entries, leaf block deletion, bitmap clearing, parent reparenting, and root collapse back to a leaf when the tree shrinks. Traversal helpers `ntfs_index_walk_down()`, private walk-up logic, and `ntfs_index_next()` provide in-order iteration for directory reads.

## Dependencies And Integration
Depends on NTFS collation, attribute-list, MFT, attribute I/O, and inode helpers. Directory code uses it for lookup/iteration and directory entry add/remove; inode sync uses it to update FILE_NAME entries in parent indexes.

## Behavior/Risks
The implementation assumes index blocks fit in `PAGE_SIZE` because inode setup rejects larger block sizes. Dirty index blocks are written with MST fixups through `ntfs_inode_attr_pwrite()`; synchronous write mode frees the in-memory block after success. Parent stack depth is capped by `MAX_PARENT_VCN` and returns `-EOPNOTSUPP` for overly deep trees.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/index.h -->
# File Research: sources/os/linux/linux/fs/ntfs/index.h

## Purpose
Defines the NTFS index context structure and declares the public index manipulation and traversal APIs.

## Key Elements
`struct ntfs_index_context` records the target index inode/name, current entry, entry data pointer/length, root-vs-allocation location, resident root context, current index block, opened index allocation inode, parent VCN/position stacks, dirty state, index block size, VCN shift, and sync-write flag. Constants define the synthetic root parent VCN and maximum traversal depth.

## Dependencies And Integration
Includes Linux `fs.h` plus NTFS attribute and MFT headers. Public functions are consumed by directory operations, namespace operations, inode synchronization, and xattr code that needs index-backed metadata.

## Behavior/Risks
The context owns borrowed pointers into mapped MFT records or allocated index blocks, so callers must release it with `ntfs_index_ctx_put()` after using `entry` or `data`. If callers modify an entry, they must mark it dirty or synchronously write it before releasing the context.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/index.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/inode.c -->
# File Research: sources/os/linux/linux/fs/ntfs/inode.c

## Purpose
Implements NTFS inode lifecycle and metadata synchronization: VFS inode cache identity, normal/attribute/index inode instantiation, mount-time `$MFT` bootstrap, extent inode management, eviction/deletion, mount option reporting, truncation/initialized-size updates, MFT record writeback, and attribute pread/pwrite.

## Key Elements
`ntfs_test_inode()` and `ntfs_init_locked_inode()` allow `iget5_locked()` to distinguish normal inodes from fake attribute and index inodes that share the same MFT number but differ by NTFS attribute type/name. `ntfs_iget()`, `ntfs_attr_iget()`, and `ntfs_index_iget()` instantiate those three inode classes and dispatch to specialized readers.

`ntfs_read_locked_inode()` decodes a normal MFT record: sequence number, link count, `$STANDARD_INFORMATION` timestamps and flags, optional `$ATTRIBUTE_LIST`, EA presence and WSL metadata, directory `$INDEX_ROOT` geometry, unnamed `$DATA` size/run attributes, reparse symlink mode, compression/sparse/encryption state, inode operations, immutable system-file state, and block accounting. It has special handling for `$Extend` metadata indexes such as `$Reparse` and `$ObjId`.

`ntfs_read_locked_attr_inode()` mirrors base inode ownership/times into fake attribute inodes, validates attribute flags, initializes resident or non-resident sizes, compression geometry, block counts, address-space ops, and holds a reference to the base inode. `ntfs_read_locked_index_inode()` performs the equivalent setup for `$INDEX_ALLOCATION`, including `$INDEX_ROOT` validation, optional missing allocation for small indexes, non-resident allocation checks, and `$BITMAP` size consistency.

`ntfs_read_inode_mount()` bootstraps `$MFT` before normal MFT mapping is available. It reads record 0 directly from the block device, applies MST fixups, validates `$MFT`, loads any attribute list directly, then builds the full `$MFT/$DATA` runlist extent by extent. Once the first runlist extent is known, it calls the normal inode reader and then restores `$MFT` as a protected internal inode with empty VFS operations.

Writeback flows through `__ntfs_write_inode()`: attribute inodes are cleaned through their base inode, base inodes update dirty mapping pairs, synchronize `$STANDARD_INFORMATION`, optionally update parent FILE_NAME index entries, write their own MFT record, map and write dirty extent MFT records, and mark the volume erroneous on non-memory failures. `ntfs_inode_sync_filename()` updates parent directory index entries with current flags, sizes, reparse tag, and times.

The lower part of the file manages extent inodes, attribute lists, MFT record free-space creation, and attribute raw I/O. `ntfs_inode_add_attrlist()` builds an in-memory and on-disk `$ATTRIBUTE_LIST`, freeing MFT record space by moving movable attributes if needed and rolling back on failure. `ntfs_inode_attr_pread()` and `ntfs_inode_attr_pwrite()` provide resident/non-resident attribute I/O for EA, bitmap, and index code, using page cache for normal writes and optional synchronous bio writes for non-resident attributes.

## Dependencies And Integration
Includes NTFS allocation, time conversion, core NTFS state, index, attribute-list, reparse, EA, attribute, iomap, and object-id headers. It supplies helpers used across directory, file, index, EA, MFT, and superblock code, and it selects `ntfs_dir_ops`, `ntfs_file_ops`, symlink/special ops, `ntfs_aops`, and `ntfs_mft_aops`.

## Behavior/Risks
This file is lock-sensitive. It defines separate lockdep classes for attribute, attribute-list, extent, MFT, and directory mapping locks; many paths require `mrec_lock`, `extent_lock`, or runlist locks in a fixed order. Corruption handling generally logs a chkdsk recommendation and sets volume errors except for unsupported features or memory pressure. Eviction deletes unlinked base inodes by freeing clusters, extent MFT records, and the base MFT record; dirty live inodes are committed before memory cleanup. Attribute raw writes reject compressed non-resident growth and encrypted non-resident enlargement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/inode.c -->