# Group Research: group_1060_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_xattr_c_sources_c18260654d13

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/xattr.c

## Scope

This file implements OCFS2 extended attributes: VFS xattr handlers, inline-inode xattrs, external xattr blocks, indexed xattr bucket trees, large xattr value extent trees, refcount/reflink handling, security xattr initialization, ACL/security preallocation accounting, and full xattr teardown.

## Main Entry Points

- `ocfs2_listxattr()` lists inode-inline and external/block/tree xattrs under inode and xattr semaphores.
- `ocfs2_xattr_get_nolock()` and internal `ocfs2_xattr_get()` locate and return a named xattr from inline inode storage or external storage.
- `ocfs2_xattr_set()` is the normal create/replace/remove path, handling inode locking, xattr lookup, flag validation, refcount preparation, allocator reservation, journaling, truncate-log flushing, ctime update, and cleanup.
- `ocfs2_xattr_set_handle()` is the create-time path used by inode creation/security/ACL setup when transaction credits and allocators were reserved by the caller.
- `ocfs2_xattr_remove()` frees all xattr resources for inode teardown.
- `ocfs2_xattr_attach_refcount_tree()` and `ocfs2_reflink_xattrs()` integrate xattr value extents with OCFS2 reflink/refcount trees.
- Handler exports implement `user.*`, `trusted.*`, and `security.*`; POSIX ACL types are in the internal handler map through nop ACL handlers.

## Data Model

- Xattrs may live in three containers: inline at the end of the dinode, in a single external `ocfs2_xattr_block`, or in indexed xattr buckets addressed by an extent tree rooted in an xattr block.
- Small values up to `OCFS2_XATTR_INLINE_SIZE` are stored directly in the name/value area. Larger values are represented by `ocfs2_xattr_value_root`, an extent tree whose clusters contain value bytes.
- `ocfs2_xattr_bucket` wraps the fixed-size bucket buffer-head array. Bucket metadata includes sorted entries, free-start tracking, name/value byte count, and bucket-run count.
- `ocfs2_xa_loc` abstracts mutation of inode-inline, unindexed block, and bucket storage through `ocfs2_xa_loc_operations`. This is the central unifier for add/remove/reuse/store logic.

## Control Flow

- Lookup first searches inline inode xattrs when present, then external xattr storage if `i_xattr_loc` exists. Indexed blocks hash the xattr name, locate the matching extent record, binary-search bucket ranges, then linearly scan same-hash entries.
- Set prefers inode-inline storage. If there is no room, it falls back to external block storage. If an unindexed block fills, it is converted to an indexed xattr tree and existing entries are copied into a bucket.
- Mutation uses `ocfs2_xa_set()`: journal access, remove-or-prepare entry, allocate/truncate external value storage when needed, store local or external bytes, then dirty the owning storage.
- Bucket insertion handles sorted-by-hash entries, defragments bucket holes on ENOSPC, and allocates/splits buckets or clusters when needed.
- Indexed bucket growth can extend a contiguous extent, split a bucket, split a cluster, or move buckets into a new non-contiguous cluster while preserving hash range boundaries.
- Large external value changes grow or shrink the value extent tree. Shrink paths remove extents, update `xr_clusters`, drop/refcount clusters, update the xattr cluster cache, and schedule truncate-log/dealloc work.
- Refcounted xattrs are prepared before allocator locking to avoid deadlocks. Existing refcounted external values may be CoWed wholesale before overwrite, or metadata/credits are reserved for delete/truncate paths.
- Reflink copies inline/block/tree xattrs into the new inode, optionally filters security/ACL xattrs, recreates value trees when needed, and increases refcounts for every external value extent.

## Dependencies

- OCFS2 locking and metadata: inode locks, `ip_xattr_sem`, `ip_alloc_sem`, journal handles, dinode/xattr-block accessors, metadata ECC, truncate log, cached dealloc contexts, allocation contexts, extent trees, and refcount trees.
- Linux VFS/xattr/LSM: xattr handler callbacks, security initialization, capability checks for trusted xattrs, POSIX ACL visibility, idmapped set signatures, buffer heads, and inode ctime helpers.
- OCFS2 tree helpers: `ocfs2_find_leaf()`, `ocfs2_insert_extent()`, `ocfs2_remove_extent()`, `ocfs2_add_clusters_in_btree()`, `ocfs2_xattr_get_clusters()`, and refcount CoW/increase/decrease helpers.

## Invariants And Risks

- Bucket name/value records must not cross filesystem block boundaries; several helpers assert this when computing value roots.
- Bucket entries are sorted by `xe_name_hash`; same-hash entries must remain in the same bucket when splitting. Excessive same-hash collisions intentionally return `-ENOSPC`.
- Journal credit calculation is complex because one set operation can touch the inode, xattr block, buckets, xattr value extents, refcount tree, data clusters, metadata allocators, and truncate log.
- Error handling deliberately dirties containers after partial mutation so on-disk xattr headers remain structurally consistent. Some failures leak clusters rather than leave corrupt entries.
- Refcount/reflink paths depend on correct post-refcount bucket ECC recomputation and on avoiding allocator/refcount lock deadlocks.
- Inline xattr size validation protects against corrupted `i_xattr_inline_size` and entry counts before listing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/xattr.h

## Scope

This header declares OCFS2 xattr types, VFS xattr handlers, security-xattr state, public xattr operations, refcount/reflink hooks, and the value-buffer wrapper shared by xattr implementation code.

## APIs And Structures

- `enum ocfs2_xattr_type` defines on-disk namespace indexes for user, POSIX ACL access/default, trusted, security, and max sentinel.
- `ocfs2_security_xattr_info` carries security initialization state: enable flag, name, allocated value, and value length.
- Declares exported handlers: `ocfs2_xattr_user_handler`, `ocfs2_xattr_trusted_handler`, `ocfs2_xattr_security_handler`, and `ocfs2_xattr_handlers`.
- Declares main operations: list, get without locks, set, create-time set with existing transaction, inline-outside check, remove, security get/set, init credit calculators, refcount attach, reflink, and post-reflink security/ACL initialization.
- `ocfs2_xattr_value_buf` bundles a buffer head, journal access callback, and `ocfs2_xattr_value_root *` so generic value-tree code can operate on inline, block, or bucket storage.

## Dependencies And Notes

- Depends on Linux xattr definitions plus OCFS2 types such as `handle_t`, `ocfs2_alloc_context`, `ocfs2_dinode`, `ocfs2_caching_info`, and cached dealloc contexts.
- The comment above `ocfs2_xattr_value_buf` explains the core design used by `xattr.c`: xattr values can be stored in multiple physical containers but are manipulated through a common wrapper.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/omfs/Kconfig

## Scope

This file defines the kernel configuration option for OMFS, the SonicBlue Optimized MPEG File System used by Rio Karma and ReplayTV devices.

## Behavior

- `config OMFS_FS` is a tristate option named “SonicBlue Optimized MPEG File System support”.
- It depends on block-device support.
- It selects `BUFFER_HEAD` and `CRC_ITU_T`, matching OMFS use of buffer-head I/O and on-disk CRC checksums.
- Help text documents the historical devices, warns the filesystem is not actually more efficient for MPEG files, and names the module `omfs`.

## Dependencies

- Build-time dependency is `BLOCK`.
- Selected helpers are required by `inode.c` and related OMFS code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/omfs/Makefile

## Scope

This Makefile wires the OMFS module into the kernel build.

## Behavior

- Builds `omfs.o` when `CONFIG_OMFS_FS` is enabled.
- The module is composed from `bitmap.o`, `dir.o`, `file.o`, and `inode.o`.

## Dependencies

- Mirrors the implementation split: allocation bitmap, directory operations, file extent/page-cache operations, and inode/superblock/module lifecycle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/omfs/bitmap.c

## Scope

This file implements OMFS free-space accounting and allocation over the in-memory bitmap mirror loaded by `inode.c`.

## Main APIs

- `omfs_count_free()` counts free bits across `sbi->s_imap`.
- `omfs_allocate_block()` tries to allocate one exact block, updating both memory bitmap and on-disk bitmap when present.
- `omfs_allocate_range()` scans for a zero-bit run and allocates between requested minimum and maximum length.
- `omfs_clear_range()` clears allocated bits during truncation or inode eviction.

## Control Flow

- `count_run()` counts consecutive free bits across multiple bitmap buffers.
- `set_run()` updates a run in memory and in the corresponding on-disk bitmap blocks, dirtying each buffer.
- Allocation and clearing are serialized by `s_bitmap_lock`.
- Block numbers are split into bitmap page index and bit offset using `do_div()` against `8 * sb->s_blocksize`.

## Risks And Invariants

- Bitmap operations assume `s_imap` has been initialized by `omfs_get_imap()`.
- `set_run()` may span multiple bitmap blocks; failure after partial updates can leave some in-memory/on-disk bits changed.
- `omfs_allocate_block()` sets the in-memory bit before reading/updating the on-disk bitmap and does not roll it back if `sb_bread()` fails.
- The code treats missing/corrupt map indexes defensively by failing allocation or ignoring out-of-range clear requests.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/omfs/dir.c

## Scope

This file implements OMFS directory hashing, lookup, create/mkdir, unlink/rmdir, rename, readdir, empty-directory initialization, and hash-chain validation.

## Main APIs

- `omfs_make_empty()` initializes an on-disk inode block either as a directory hash table or a regular-file extent table.
- `omfs_is_bad()` validates an inode/header self pointer and range.
- Directory inode ops: lookup, mkdir, create, unlink, rmdir, rename.
- Directory file ops: generic read, `iterate_shared` via `omfs_readdir()`, and generic llseek.

## Control Flow

- Directory entries are stored as hash buckets in the directory inode block. Each bucket points to a linked list of inode blocks through `i_sibling`.
- `omfs_hash()` lowercases bytes and XOR-shifts them into a bucket index.
- `omfs_find_entry()` reads the bucket head and follows the linked list with `omfs_scan_list()`.
- `omfs_add_link()` prepends a new inode into the proper bucket, stores its name, sibling, and parent pointers, and marks parent/child dirty for checksum rebuild.
- `omfs_delete_entry()` removes a target from either the bucket head or a previous inode’s sibling link.
- `omfs_remove()` rejects non-empty directories, unlinks the entry, clears link count, and marks metadata dirty.
- `omfs_rename()` supports only `RENAME_NOREPLACE`; it removes an existing target if present, deletes the old link, then adds the old inode under the new name.
- `omfs_readdir()` encodes bucket index and chain index in `ctx->pos`, emits dot entries first, then walks each bucket chain.

## Risks And Invariants

- `omfs_dir_is_empty()` appears semantically inverted: it returns `*ptr != ~0` after the loop, so callers use `!omfs_dir_is_empty()` to reject directories. The naming is misleading and fragile.
- Lookup compares `strncmp(oi->i_name, name, namelen)` without separately requiring a NUL or exact stored-name length match; names sharing the queried prefix can match.
- Hash-chain loops are not bounded except by corrupt self/range detection.
- Rename is not transactional; failures after deleting the old entry can leave namespace changes partially applied.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/omfs/file.c

## Scope

This file implements OMFS regular-file extent mapping, growth, truncate-to-zero cleanup, page-cache address-space operations, file operations, and setattr.

## Main APIs

- `omfs_make_empty_table()` initializes an extent table with a terminator entry.
- `omfs_shrink_inode()` frees all file extents and continuation blocks when file size is zero.
- `omfs_get_block()` maps logical file blocks to disk blocks and optionally extends the file.
- Address-space ops provide buffered read, readahead, writeback, write-begin/end, bmap, invalidation, dirtying, and migration.
- File ops use generic read/write/mmap/splice/llseek plus `simple_fsync`.
- `omfs_setattr()` validates size changes, truncates page cache, invokes OMFS truncation, copies attributes, and marks the inode dirty.

## Control Flow

- Extent tables live in the inode block at `OMFS_EXTENT_START`; continuation tables would start at `OMFS_EXTENT_CONT`.
- `find_block()` walks extent entries, converting OMFS clusters to Linux block numbers and returning how many blocks remain contiguous.
- `omfs_grow_extent()` first tries to extend the last extent by allocating the next exact block. If that fails, it allocates a new range and inserts a new extent before the terminator.
- Continuation-block creation is explicitly TODO; if the initial extent table fills, growth fails with `-EIO`.
- `omfs_shrink_inode()` supports only truncate to zero, clears bitmap ranges for every data extent, resets extent tables, frees continuation blocks, and leaves partial truncation unsupported.

## Risks And Invariants

- Partial truncate is unsupported; nonzero target size returns `-EIO` from shrink and `omfs_setattr()` has already adjusted `i_size` before calling `omfs_truncate()`.
- Hole handling is TODO. Writes extend at the end of available extents rather than representing sparse holes.
- Continuation extent creation is TODO, limiting maximum fragmented file extent count.
- Extent table corruption checks rely on `extent_count <= max_extents` and `omfs_is_bad()` self-pointer validation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/omfs/inode.c

## Scope

This file implements OMFS module registration, filesystem context parsing, superblock mounting, inode allocation/loading/writing/eviction, checksum generation, statfs, mount option display, and free-bitmap loading.

## Main APIs

- `omfs_bread()` reads an OMFS cluster/block after range checking.
- `omfs_new_inode()` allocates blocks, initializes VFS inode state, installs OMFS ops, hashes the inode, and marks it dirty.
- `omfs_iget()` loads an inode from disk, validates self pointer, applies mount uid/gid/masks, timestamps, mode, ops, size, and unlocks it.
- `omfs_sync_inode()` and `omfs_write_inode()` serialize in-memory inode state into on-disk OMFS inode blocks.
- Super operations: write inode, evict inode, put super, statfs, show options.
- Filesystem context ops parse `uid`, `gid`, `umask`, `dmask`, and `fmask`, then mount with `get_tree_bdev()`.

## Control Flow

- Mount reads block 0 as OMFS superblock, checks magic, loads counts, block sizes, mirrors, root inode, and system block size.
- It validates maximum block count, sys block size, data block size, root-block consistency, bitmap location, and cluster size.
- The kernel block size is first set to 512, then reset to OMFS system block size; `s_block_shift` converts OMFS cluster numbers to Linux block numbers.
- Root block provides bitmap location, cluster size, and root directory inode.
- `omfs_get_imap()` loads the free-space bitmap into an array of block-sized memory copies. If no bitmap exists (`~0ULL`), it skips allocation.
- `__omfs_write_inode()` writes header fields, type, size, millisecond ctime, CRC, XOR checksum, and mirrors the inode block to `s_mirrors - 1` following blocks.
- `omfs_evict_inode()` truncates page cache, clears inode, frees regular-file extents for unlinked files, then frees inode mirror blocks.

## Risks And Invariants

- `omfs_put_super()` frees only the `s_imap` pointer array, not each per-block `kmemdup()` bitmap buffer, which looks like a memory leak on unmount.
- `omfs_fill_super()` frees `sbi` directly on mount failure without clearing `sb->s_fs_info` and without freeing loaded bitmap sub-buffers.
- `omfs_evict_inode()` clears two inode blocks unconditionally, while allocation used `sbi->s_mirrors`; this may mismatch mirror counts other than two.
- `omfs_iget()` has no default failure for unknown `i_type`; it can unlock and return an inode with incomplete mode/ops if disk type is invalid.
- On-disk checksum update is write-only here; read paths validate self pointer but do not verify CRC/XOR.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/omfs.h -->
# File Research: sources/os/linux/linux-stable/fs/omfs/omfs.h

## Scope

This internal header defines the OMFS in-memory superblock state, cluster-to-block conversion, accessor macro, and cross-file function/operation declarations.

## Data Model

- `struct omfs_sb_info` stores total blocks, bitmap inode, root inode, data/system block sizes, mirror count, cluster size, block-shift conversion factor, in-memory bitmap array, bitmap lock, uid/gid, and directory/file masks.
- `clus_to_blk()` converts OMFS cluster/block numbers to Linux sector/block numbers by left-shifting with `s_block_shift`.
- `OMFS_SB()` retrieves the OMFS private superblock from `sb->s_fs_info`.

## Declarations

- Bitmap operations: count free, allocate exact block, allocate range, clear range.
- Directory operations and helpers: directory file/inode ops, empty inode initialization, bad-chain detection.
- File operations and helpers: regular file ops, inode ops, address-space ops, empty extent table creation, shrink inode.
- Inode helpers: OMFS block read, iget, new inode, sync inode.

## Notes

- Declarations `omfs_reserve_block()` and `omfs_find_empty_block()` appear in this header but are not implemented in the listed OMFS files, suggesting stale prototypes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/omfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/omfs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/omfs/omfs_fs.h

## Scope

This header defines OMFS on-disk constants and packed-style disk structures used by the Linux OMFS driver.

## Constants

- Magic/type values: `OMFS_MAGIC`, `OMFS_IMAGIC`, `OMFS_DIR`, `OMFS_FILE`, inode type letters for normal/continuation/system.
- Layout limits and offsets: name length 256, directory table start `0x1b8`, first extent table start `0x1d0`, continuation extent start `0x40`, XOR header count 19, max block size 8192, max cluster size 8, max blocks `1 << 31`.

## On-Disk Structures

- `omfs_super_block` stores root block pointer, total blocks, magic, block size, mirror count, and system-block size.
- `omfs_header` is the common block header with self pointer, body size, CRC, version, type, magic, and XOR checksum.
- `omfs_root_block` stores global filesystem metadata: total blocks, root directory, bitmap location, block size, cluster size, mirrors, and volume label.
- `omfs_inode` stores common header, parent/sibling links, millisecond ctime, file type, filename, and byte size.
- `omfs_extent_entry` stores cluster start and block count.
- `omfs_extent` stores next extent-table block, extent count, filler, and flexible extent entries.

## Dependencies And Risks

- Fields are big-endian and require explicit conversion in implementation files.
- The structures are used as direct overlays on buffer-head data, so layout offsets in this header are part of the on-disk ABI.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/omfs/omfs_fs.h -->