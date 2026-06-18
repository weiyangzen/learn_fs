# Group Research: group_818_linux_sources_os_linux_linux_fs_ocfs2_xattr_c_sources_os_linux_linux_8f90d6cf8d05

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/xattr.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/xattr.c

OCFS2 extended attribute implementation. This file owns the full xattr backend for OCFS2: listing, lookup, set/remove, security initialization, ACL/security integration, external value extent management, indexed xattr trees, refcount/reflink handling, journaling, metadata ECC, and VFS xattr handlers.

Primary storage models:
- Inline inode xattrs live at the tail of the inode block after space is carved from inline data, fast symlink payload, or extent-record capacity.
- External unindexed xattrs live in one `ocfs2_xattr_block` referenced by `di->i_xattr_loc`.
- Large xattr sets are stored as an indexed xattr tree rooted in that xattr block; leaf storage is a set of fixed-size xattr buckets.
- Values larger than `OCFS2_XATTR_INLINE_SIZE` are stored outside the name/value area through an embedded `ocfs2_xattr_value_root` extent tree.
- Bucket storage keeps entries sorted by `xe_name_hash`; in-block storage compacts name/value pairs and does not require hash ordering.

Important local abstractions:
- `struct ocfs2_xattr_bucket` wraps the buffer heads that make up one bucket and centralizes bucket read, release, journaling, ECC validation, copying, and dirtying.
- `struct ocfs2_xattr_info` is the normalized set/get request: namespace index, name, value pointer, and value length.
- `struct ocfs2_xattr_search` records the current search result across inode, xattr block, or bucket storage.
- `struct ocfs2_xa_loc` plus `ocfs2_xa_loc_operations` abstracts mutation of inline inode, unindexed block, and indexed bucket entries behind common prepare/store/remove logic.
- `struct ocfs2_xattr_set_ctxt` carries the active transaction, metadata/data allocators, cached deallocations, and abort state.

Lookup and listing:
- `ocfs2_listxattr()` takes the inode cluster lock and `ip_xattr_sem`, lists inline entries first, then external block or indexed tree entries.
- Namespace filtering is done by `ocfs2_xattr_list_entry()`: user xattrs honor `NOUSERXATTR`, POSIX ACL entries require `SB_POSIXACL`, and trusted entries require `CAP_SYS_ADMIN`.
- `ocfs2_xattr_get()` locks the inode and reads under `ip_xattr_sem`; `ocfs2_xattr_get_nolock()` searches inline storage first and falls back to the external xattr block.
- `ocfs2_xattr_find_entry()` validates entry bounds while comparing namespace, name length, and name bytes.
- Indexed lookup hashes the name with the filesystem UUID hash seed, finds the matching extent record, binary-searches buckets by hash range, then linearly scans same-hash entries inside the bucket.

Set/remove flow:
- `ocfs2_xattr_set()` performs VFS flag checks for `XATTR_CREATE` and `XATTR_REPLACE`, prepares refcounted values if needed, flushes the truncate log, reserves metadata/data allocators, starts a journal transaction, and calls `__ocfs2_xattr_set_handle()`.
- `ocfs2_xattr_set_handle()` is the create-inode path used by security/ACL initialization when credits and allocators were already reserved by inode creation.
- New values are attempted in inode-inline xattr space first; if that fails with space pressure, the code falls back to external block or indexed bucket storage.
- If setting succeeds in one storage location while an old copy exists in the other, the old copy is removed in the same logical operation after extending credits.
- Removes truncate external value trees to zero, remove packed entry metadata, update ctime, and may try to remove now-unused refcount trees.
- Mutation updates inode ctime and fsync transaction state.

Name/value mutation details:
- `ocfs2_xa_set()` is the common entry set/remove engine. It journals the backing location, prepares or removes an entry, stores the inline or external value, and dirties the location even on many error paths to keep metadata consistent.
- Block-style storage compacts name/value areas by shifting packed bytes upward on removal and inserting new name/value pairs from the end of the storage area.
- Bucket-style storage can leave holes when a name/value pair cannot be reused; `ocfs2_defrag_xattr_bucket()` later compacts all pairs and restores hash ordering.
- Bucket values must not straddle filesystem block boundaries; helpers align `xh_free_start` before inserting a name/value pair.
- Large-value setup installs a default value root, grows or shrinks the value extent tree, then writes value data block by block under journal access.

External value extent management:
- `ocfs2_xattr_extend_allocation()` adds clusters to an xattr value tree using the normal OCFS2 btree allocator and can extend transactions when data allocation restarts.
- `ocfs2_xattr_shrink_size()` and `__ocfs2_remove_xattr_range()` remove value extents, update `xr_clusters`, drop extent-cache entries, and either decrement refcounts or cache cluster deallocation.
- `__ocfs2_xattr_set_value_outside()` writes the actual large value data into allocated clusters and zero-fills trailing block bytes.
- Cleanup after partial truncate/grow failures intentionally removes corrupt entries or leaks clusters rather than committing inconsistent xattr metadata.

External xattr blocks and indexed trees:
- `ocfs2_create_xattr_block()` allocates and initializes an `ocfs2_xattr_block`, sets signature, block number, suballocator fields, generation, optional indexed root, and links it from the dinode.
- If an unindexed xattr block fills, `ocfs2_xattr_create_index_block()` allocates a bucket cluster, copies/sorts the existing block entries into a bucket, and converts the xattr block body into an indexed tree root.
- `ocfs2_add_new_xattr_bucket()` grows indexed storage by splitting buckets, adding clusters, shifting buckets, or moving bucket ranges across cluster boundaries.
- Bucket splitting preserves the invariant that all entries with the same hash stay in the same bucket; all-same-hash buckets reject further same-hash insertions with `-ENOSPC`.
- Tree traversal walks extent records from high hash to low hash and then iterates buckets in each record.

Refcount and reflink handling:
- Refcounted inodes require special preparation before replacing/removing existing external xattr values.
- `ocfs2_prepare_refcount_xattr()` locks the refcount tree, CoWs existing external xattr value clusters when needed, or computes delete metadata/credits for truncate-driven refcount updates.
- `ocfs2_xattr_attach_refcount_tree()` marks all external xattr value extents refcounted when an inode becomes refcounted.
- `ocfs2_reflink_xattrs()` copies inline xattrs and external xattr blocks/trees from one inode to another, increments refcounts for external value clusters, and can omit security/ACL xattrs when `preserve_security` is false.
- Indexed reflink recreates bucket clusters for the destination and rebuilds xattr tree extents while preserving or recalculating value roots as needed.

Security and namespace handlers:
- Exports `ocfs2_xattr_user_handler`, `ocfs2_xattr_trusted_handler`, and `ocfs2_xattr_security_handler`.
- `ocfs2_init_security_get()` captures LSM-provided security xattrs for create-time sizing or sets them immediately through `security_inode_init_security()`.
- `ocfs2_init_security_set()` installs the captured security xattr through the pre-reserved create path.
- `ocfs2_init_security_and_acl()` reinitializes security and ACL xattrs after reflink when security is not preserved.

Concurrency and journaling invariants:
- `ip_xattr_sem` serializes xattr lookup and mutation.
- `ip_alloc_sem` is used while carving inline xattr space and while converting/growing indexed xattr storage.
- Bucket metadata ECC is validated on read and recomputed before dirtying bucket buffers.
- Mutations must acquire journal access for the exact backing container: dinode, xattr block, bucket, or value data block.
- Truncate-log flushing is coordinated before xattr cluster frees where stale pending deallocations could conflict.
- Refcount tree locks and allocator reservations are ordered before transactions that mutate shared xattr values.

Failure and corruption behavior:
- Bad xattr block signatures, block numbers, fs generations, malformed inline sizes, invalid counts, missing extent records, and bad hash chains are treated as filesystem corruption or I/O errors.
- Many storage-layout BUG_ONs enforce assumptions about bucket size, value locality, block alignment, and extent-tree state.
- Space accounting is conservative and may reserve extra clusters/credits because xattrs can move between inode, block, and indexed tree storage during a set operation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/xattr.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/xattr.h

Public OCFS2 xattr interface shared by the xattr implementation and the rest of OCFS2.

Key contents:
- Defines OCFS2 xattr namespace indexes for user, POSIX ACL access/default, trusted, security, and max sentinel.
- Defines `struct ocfs2_security_xattr_info`, the create-time carrier for LSM security xattr name/value data and enable state.
- Declares the OCFS2 user, trusted, and security `xattr_handler`s plus the handler table used by inode operation tables.
- Declares list/get/set/remove APIs, including `ocfs2_xattr_get_nolock()` for callers that already hold required locks and inode buffer state.
- Declares `ocfs2_xattr_set_handle()`, used during inode creation when the caller already owns a transaction and reserved allocators.
- Declares create-time sizing helpers `ocfs2_calc_security_init()` and `ocfs2_calc_xattr_init()`.
- Defines `struct ocfs2_xattr_value_buf`, a small wrapper that identifies the buffer head, journal access function, and value root for an external xattr value tree.
- Declares refcount/reflink helpers for attaching refcount trees, copying xattrs during reflink, and reinitializing security/ACL state.

Important contract:
- Xattrs may live in an inode, an external xattr block, or an indexed-tree bucket, but callers that operate on external value roots can use `ocfs2_xattr_value_buf` to avoid caring about the container.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/omfs/Kconfig

Kconfig entry for the Linux OMFS filesystem driver.

Key contents:
- Defines `CONFIG_OMFS_FS` as a tristate option named “SonicBlue Optimized MPEG File System support”.
- Depends on `BLOCK`, because OMFS is mounted from block devices.
- Selects `BUFFER_HEAD`, matching the implementation’s buffer-head based metadata and block I/O.
- Selects `CRC_ITU_T`, used by inode/header checksum generation.
- Help text identifies OMFS as the proprietary filesystem used by Rio Karma and ReplayTV devices and notes the module name is `omfs`.
- Default guidance is conservative: say N if unsure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/Makefile -->
# File Research: sources/os/linux/linux/fs/omfs/Makefile

Build glue for the OMFS filesystem module.

Key contents:
- Builds `omfs.o` when `CONFIG_OMFS_FS` is enabled.
- Links the module from `bitmap.o`, `dir.o`, `file.o`, and `inode.o`.
- No conditional subfeatures are split out; the OMFS driver is built as one small module.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/bitmap.c -->
# File Research: sources/os/linux/linux/fs/omfs/bitmap.c

OMFS free-space bitmap management. This file keeps the in-memory allocation bitmap synchronized with the on-disk bitmap when one exists.

Main responsibilities:
- `omfs_count_free()` counts free bits across all in-memory bitmap pages.
- `omfs_allocate_block()` tries to allocate exactly one filesystem block/cluster number.
- `omfs_allocate_range()` finds and marks a contiguous run, used for inode mirror blocks and file cluster allocation.
- `omfs_clear_range()` clears a contiguous allocation run during truncate or inode eviction.
- Internal helpers count free runs across bitmap-buffer boundaries and set/clear runs in both memory and disk bitmap buffers.

Implementation details:
- Allocation state is protected by `sbi->s_bitmap_lock`.
- The bitmap is held as `unsigned long **s_imap`, one allocation per filesystem block of bitmap data.
- On-disk bitmap blocks are addressed from `s_bitmap_ino` through `clus_to_blk()`.
- `set_run()` handles runs that cross bitmap blocks by dirtying and releasing one bitmap buffer before loading the next.
- `omfs_allocate_range()` returns the selected starting block and the full available run length up to `max_request`, provided it meets `min_request`.

Important behavior:
- `omfs_allocate_block()` returns boolean success rather than a negative errno.
- `omfs_allocate_range()` returns `-ENOSPC` when no run satisfies the request.
- `omfs_clear_range()` treats an out-of-range starting map as a no-op.
- If a disk bitmap read fails during allocation after the in-memory bit was set, the function exits without rolling back that bit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/dir.c -->
# File Research: sources/os/linux/linux/fs/omfs/dir.c

OMFS directory operations. Directories are hash tables stored in the directory inode block, with each bucket pointing to a linked list of inode blocks via `i_sibling`.

Main responsibilities:
- Hash names with a simple case-folding XOR hash and map them to fixed directory buckets.
- Lookup entries by reading the bucket head and scanning the sibling chain.
- Create files/directories by allocating a new inode, initializing its on-disk table, and linking it into the parent bucket.
- Delete entries by unlinking the target inode from its bucket chain.
- Implement readdir using `ctx->pos` split into high bits for bucket index and low bits for position inside a hash chain.
- Implement rename by deleting the old link first, then adding the inode under the new dentry name.
- Export OMFS directory inode and file operation tables.

Key functions:
- `omfs_get_bucket()` computes the bucket offset and reads the directory inode block.
- `omfs_scan_list()` follows a bucket chain and validates each inode block with `omfs_is_bad()`.
- `omfs_make_empty()` initializes an inode block as either a directory bucket table filled with `0xff` terminators or a file extent table.
- `omfs_add_link()` prepends the new inode to the target bucket and writes name, sibling, and parent fields to the child inode.
- `omfs_delete_entry()` removes a chain node by updating either the bucket head or the previous inode’s sibling pointer.
- `omfs_fill_chain()` emits directory entries while following a hash chain.
- `omfs_readdir()` emits dots, then iterates buckets and chains with resumable position encoding.

Operation tables:
- `omfs_dir_inops`: lookup, mkdir, rename, create, unlink, rmdir.
- `omfs_dir_operations`: generic read dir, shared iterate, generic llseek.

Important invariants and risks:
- Directory bucket entries use `~0ULL` as the end-of-chain sentinel.
- `omfs_is_bad()` validates that an inode block’s self pointer matches the expected block and lies in the legal inode/data block range.
- `omfs_lookup()` rejects names longer than `OMFS_NAMELEN`.
- Rename supports only `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- `omfs_dir_is_empty()` is intended to detect any non-sentinel bucket, but the implementation dereferences `ptr` after the loop, which is risky when all buckets are sentinel values.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/file.c -->
# File Research: sources/os/linux/linux/fs/omfs/file.c

OMFS regular file and address-space operations. This file maps logical file blocks to OMFS extents, grows extent tables during writes, truncates files to zero, and wires the driver into generic buffered I/O helpers.

Main responsibilities:
- Initialize empty OMFS extent tables with a sentinel terminator.
- Shrink regular files by freeing all extents when file size becomes zero.
- Grow the current extent or add a new extent when writeback maps an unmapped block.
- Map logical file blocks to physical disk blocks for read, write, readahead, writeback, and bmap.
- Implement setattr-driven size changes.

Extent behavior:
- `omfs_extent` tables contain normal entries followed by a terminator entry.
- `omfs_max_extents()` calculates how many extent entries fit after the table offset.
- `find_block()` scans extent entries and maps a logical block into a physical block plus contiguous remainder.
- `omfs_grow_extent()` first tries to extend the last extent by allocating the immediately following block; otherwise it allocates a new cluster-sized range and inserts a new extent entry.
- Continuation extent blocks are recognized by the on-disk format, but new continuation allocation is still marked TODO; if the first table fills, growth returns `-EIO`.

Truncate behavior:
- `omfs_shrink_inode()` only supports truncate-to-zero.
- It walks the first extent table and any continuation tables, frees all non-terminator extent ranges, resets each table to empty, and frees continuation inode blocks.
- `omfs_truncate()` calls shrink and marks the inode dirty.
- `omfs_write_failed()` rolls back page cache and truncates if block allocation fails beyond current file size.

VFS integration:
- `omfs_get_block()` is the central block mapper used by buffered read/write, mpage readahead/writepages, and bmap.
- `omfs_read_folio()`, `omfs_readahead()`, `omfs_writepages()`, `omfs_write_begin()`, and `omfs_bmap()` are thin wrappers around generic block helpers.
- `omfs_file_operations` uses generic llseek/read/write, mmap preparation, simple fsync, and splice read.
- `omfs_file_inops` provides `setattr`.
- `omfs_aops` installs buffer-head based dirty, invalidate, read, readahead, writepages, write_begin/end, bmap, and migrate hooks.

Important limits:
- Holes are not implemented.
- Nonzero truncation is not supported by `omfs_shrink_inode()`.
- Extent continuation allocation for growth is not implemented.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/inode.c -->
# File Research: sources/os/linux/linux/fs/omfs/inode.c

OMFS inode, superblock, mount, writeback, and module registration implementation.

Main responsibilities:
- Provide safe block reads in OMFS block/cluster numbering through `omfs_bread()`.
- Allocate and initialize new VFS inodes with OMFS operation tables.
- Serialize dirty VFS inode state back into OMFS on-disk inode blocks and mirrored copies.
- Read OMFS inode blocks into VFS inodes with mount-option ownership and masks.
- Manage inode eviction and free bitmap cleanup.
- Parse mount options and fill the superblock from disk metadata.
- Register/unregister the `omfs` filesystem type.

Inode write/read behavior:
- `omfs_new_inode()` allocates `s_mirrors` contiguous blocks for a new inode, sets mode-specific operations, initializes timestamps, hashes the inode, and marks it dirty.
- `omfs_update_checksums()` computes the body CRC-CCITT and header XOR checksum.
- `__omfs_write_inode()` writes type, body size, version, magic, size, ctime in milliseconds, checksums, and mirrored inode copies.
- `omfs_iget()` validates the on-disk self pointer, assigns configured uid/gid, reconstructs timestamps from milliseconds, installs file or directory operations, and unlocks the inode.
- `omfs_evict_inode()` truncates page cache, frees regular-file extents for unlinked files, then clears inode allocation bits.

Superblock and mount flow:
- `omfs_fill_super()` allocates `omfs_sb_info`, applies parsed options, reads the primary superblock at block 0, validates `OMFS_MAGIC`, and loads block counts, block sizes, mirror count, root block, and system block size.
- It validates maximum block count, system block size, filesystem block size, bitmap location, and cluster size.
- It switches Linux blocksize to `s_sys_blocksize` and computes `s_block_shift` for mapping OMFS cluster numbers to Linux block numbers.
- It reads the OMFS root block, checks consistency with the superblock, loads bitmap location and cluster size, initializes the in-memory bitmap, loads the root directory inode, and creates the VFS root dentry.
- `omfs_get_imap()` loads the on-disk bitmap into per-block memory chunks; if the filesystem has no bitmap inode (`~0ULL`), it returns success without allocating `s_imap`.

Mount options:
- Supports `uid`, `gid`, `umask`, `dmask`, and `fmask` through fs_context parsing.
- Remount parameter changes are ignored.
- Defaults are current uid, current gid, and current umask for both file and directory masks.
- `omfs_show_options()` prints only options differing from current defaults.

Super operations and module hooks:
- `omfs_sops`: write_inode, evict_inode, put_super, statfs, show_options.
- `omfs_fs_type`: block-device filesystem named `omfs`, with fs_context support and `FS_REQUIRES_DEV`.
- Module init/exit register and unregister the filesystem.

Important invariants and risks:
- The driver assumes system block size is a valid power-of-two divisor relationship with filesystem block size when computing `s_block_shift`.
- `omfs_put_super()` frees `s_imap` as a pointer array but does not free each bitmap chunk; error paths in `omfs_get_imap()` do free chunks.
- `omfs_evict_inode()` clears exactly two inode blocks, while allocation used `s_mirrors`; this is notable if mirror count differs from two.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/omfs.h -->
# File Research: sources/os/linux/linux/fs/omfs/omfs.h

Internal OMFS header for in-memory state, helpers, and cross-file declarations.

Key contents:
- Includes the on-disk format header `omfs_fs.h`.
- Defines `struct omfs_sb_info`, the filesystem-private superblock state.
- Stores block counts, bitmap inode, root inode, filesystem and system block sizes, mirror count, cluster size, block shift, in-memory bitmap, bitmap lock, uid/gid, and masks.
- Provides `clus_to_blk()`, converting OMFS cluster/block numbers to Linux sector/block numbers using `s_block_shift`.
- Provides `OMFS_SB()` for typed access to `sb->s_fs_info`.

Declared module interfaces:
- Bitmap allocation/free/count functions from `bitmap.c`.
- Directory operation tables and helpers from `dir.c`.
- File operation/address-space tables and extent helpers from `file.c`.
- Inode/super helpers from `inode.c`.

Notable detail:
- The header declares `omfs_reserve_block()` and `omfs_find_empty_block()`, but the listed implementation files do not define them; they appear to be stale declarations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/omfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/omfs/omfs_fs.h -->
# File Research: sources/os/linux/linux/fs/omfs/omfs_fs.h

OMFS on-disk format definitions.

Key contents:
- Defines filesystem magic values, inode type characters, name length, fixed offsets, checksum constants, and size limits.
- `OMFS_MAGIC` identifies the superblock; `OMFS_IMAGIC` identifies inode/header records.
- `OMFS_DIR_START`, `OMFS_EXTENT_START`, and `OMFS_EXTENT_CONT` define where directory hash buckets and extent tables begin inside system blocks.
- Maximums include `OMFS_NAMELEN` 256, max block size 8192, max cluster size 8, and max blocks `1 << 31`.

On-disk structures:
- `struct omfs_super_block`: primary superblock with root block pointer, total blocks, magic, block size, mirror count, and system block size.
- `struct omfs_header`: shared metadata header containing self block, body size, CRC, version, type, magic, XOR checksum, and padding.
- `struct omfs_root_block`: root metadata containing total blocks, root directory block, bitmap block, block size, cluster size, mirror count, and volume name.
- `struct omfs_inode`: file/directory inode metadata with parent, sibling chain pointer, ctime, type, name, and file size.
- `struct omfs_extent_entry`: start cluster plus block count.
- `struct omfs_extent`: extent table header with next continuation pointer, extent count, fill field, and flexible array of extent entries.

Format conventions:
- Multi-byte fields are big-endian.
- `~0ULL` is used as a sentinel for absent bitmap, end-of-chain sibling, end-of-extent table, and empty bucket pointers.
- Directories and files share the inode structure; type-specific payload starts at fixed offsets inside the same system block.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/omfs/omfs_fs.h -->