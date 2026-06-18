# Research Report: subset-b-005742

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/xattr.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/xattr.c

Purpose: implements OCFS2 extended attribute support for VFS `getxattr`, `setxattr`, `listxattr`, security xattr initialization, POSIX ACL bootstrap sizing, xattr deletion during inode teardown, and reflink/refcount handling. It supports three storage forms: inline xattrs in the inode block, unindexed external xattr blocks, and indexed xattr trees whose leaves are fixed-size buckets containing sorted hash entries and name/value payloads.

Important APIs and functions: public entry points are `ocfs2_listxattr`, `ocfs2_xattr_get_nolock`, `ocfs2_xattr_set`, `ocfs2_xattr_set_handle`, `ocfs2_xattr_remove`, `ocfs2_has_inline_xattr_value_outside`, `ocfs2_init_security_get`, `ocfs2_init_security_set`, `ocfs2_calc_security_init`, `ocfs2_calc_xattr_init`, `ocfs2_xattr_attach_refcount_tree`, `ocfs2_reflink_xattrs`, and `ocfs2_init_security_and_acl`. Handler objects `ocfs2_xattr_user_handler`, `ocfs2_xattr_trusted_handler`, and `ocfs2_xattr_security_handler` integrate with the VFS xattr layer. Core internal structures include `ocfs2_xattr_info`, `ocfs2_xattr_search`, `ocfs2_xattr_bucket`, `ocfs2_xattr_set_ctxt`, and the location abstraction `ocfs2_xa_loc` plus `ocfs2_xa_loc_operations`.

Control flow: lookup first checks inode inline xattrs, then the external block if `i_xattr_loc` is present. Unindexed blocks are linearly searched by type/name/length. Indexed blocks hash names with the filesystem UUID seed, find an extent record by hash, binary-search the bucket range, then scan hash-equal entries inside the selected bucket. Listing walks the same storage forms and filters by namespace policy: user xattrs honor `nouserxattr`, ACL names require `SB_POSIXACL`, and trusted names require `CAP_SYS_ADMIN`. Setting takes the inode cluster lock, `ip_xattr_sem`, and sometimes `ip_alloc_sem`; validates `XATTR_CREATE`/`XATTR_REPLACE`; prepares refcounted values when needed; estimates metadata, cluster, and journal credits; starts a transaction; tries inline storage first; falls back to an xattr block; and converts a full unindexed block into an indexed bucket tree. Removal truncates any external value tree, updates the header, and then clears inode feature flags or frees the external xattr block.

State and persistence behavior: persistent state is stored in `ocfs2_dinode` feature bits, `i_xattr_inline_size`, `i_xattr_loc`, `ocfs2_xattr_block` headers, xattr tree extent records, bucket headers, xattr entries, and per-value `ocfs2_xattr_value_root` extent lists. Values up to `OCFS2_XATTR_INLINE_SIZE` are stored in the name/value area; larger values are stored in separate clusters described by a value-root extent tree. Bucket writes recompute metadata ECC over all bucket buffers before dirtying. External values use OCFS2 extent-tree helpers for allocation, truncation, refcount decrement, cached deallocation, and truncate-log flushing. Inode ctime is updated on successful set/remove paths.

Dependencies and integration points: depends on OCFS2 journaling, suballoc, extent trees, truncate logs, metadata ECC, DLM/inode locking, refcount trees, ACL and security initialization, VFS xattr handlers, Linux capability checks, and tracepoints in `ocfs2_trace.h`. `ocfs2_calc_xattr_init` is consumed by create/mknod reservation paths, while `ocfs2_xattr_set_handle` is used when security/ACL xattrs are installed inside an already-open create transaction. Reflink integration copies xattr containers to a new inode and increments refcounts for external value clusters, optionally omitting security and ACL xattrs when the caller does not preserve security.

Risks: the highest-risk area is consistency across partial allocation/truncation failures. `ocfs2_xa_cleanup_value_truncate` may remove entries and intentionally leak clusters rather than leaving corrupt metadata, so error paths must preserve a journal-consistent header. Bucket code relies on name/value payloads not crossing block boundaries, sorted hash entries, valid `xh_free_start`, and correct `xh_num_buckets` when splitting or moving buckets across clusters. Refcounted xattrs require the refcount tree to be locked before allocator reservations to avoid deadlock, and metaecc buckets need post-refcount dirtying. Corruption checks are uneven: inline list validates inline size and entry count, but many internal paths still assume valid entry offsets after earlier validation. Hash-collision overflow returns `-ENOSPC`, so adversarial names can expose bucket split limits.

Test signals: exercise xattr get/list/set/remove for user, trusted, security, and POSIX ACL namespaces; inline-to-block fallback; block-to-indexed-tree conversion; large external values; replacing external with local values; deleting refcounted/reflinked xattrs; reflink with and without security preservation; bucket defrag and split paths; hash collision behavior; 512-byte block-size fallback; metadata ECC validation; forced ENOSPC and journal restart paths; truncate-log flushing after xattr cluster deallocation; and mount options that disable user xattrs or POSIX ACL listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/xattr.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/xattr.h

Purpose: declares the OCFS2 xattr namespace identifiers, VFS handler exports, public xattr manipulation APIs, security initialization helpers, reflink/refcount hooks, and the value-buffer bridge used by xattr value extent-tree code.

Important APIs and types: `enum ocfs2_xattr_type` maps OCFS2 on-disk namespace indexes for user, ACL access, ACL default, trusted, and security xattrs. `struct ocfs2_security_xattr_info` carries deferred LSM xattr initialization data during inode creation. `struct ocfs2_xattr_value_buf` pairs a buffer head, journal access callback, and `ocfs2_xattr_value_root` pointer so common value-tree code can operate on inline inode storage, external xattr blocks, or bucket-contained roots. The header declares `ocfs2_xattr_get_nolock`, `ocfs2_xattr_set`, `ocfs2_xattr_set_handle`, `ocfs2_xattr_remove`, `ocfs2_reflink_xattrs`, and `ocfs2_init_security_and_acl`.

Control flow: this file has no executable control flow, but it separates locked and lockless contracts. `ocfs2_xattr_get_nolock` assumes the caller already holds the inode lock and xattr semaphore, while `ocfs2_xattr_set` owns normal locking and transaction setup. `ocfs2_xattr_set_handle` is the create-time variant that receives an existing handle and pre-reserved allocation contexts.

State and persistence behavior: all persistent layout is defined in `ocfs2_fs.h`; this header exposes only the helper state required to reach and journal value roots. `ocfs2_security_xattr_info.value` can own a kmemdup'd LSM value until `ocfs2_init_security_set` installs it.

Dependencies and integration points: includes Linux xattr definitions and is included by OCFS2 inode creation, ACL, security, reflink, and teardown code. Handler declarations feed the superblock xattr handler table, while refcount/reflink declarations connect xattrs to OCFS2 copy-on-write support.

Risks: callers must respect the locking distinction between public and `_nolock` APIs. Passing the wrong `vb_access` function or buffer head in `ocfs2_xattr_value_buf` can journal the wrong metadata class. Security init callers must free or consume deferred `ocfs2_security_xattr_info.value` according to the surrounding create path.

Test signals: compile coverage with ACL/security/reflink paths, create-time LSM xattr installation, direct `getxattr` under existing inode locks, xattr removal during evict, and reflink tests that preserve or drop security xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/Kconfig -->
## sources/distributed-fs/ceph-client/fs/omfs/Kconfig

Purpose: defines the kernel configuration switch for SonicBlue Optimized MPEG File System support, covering Rio Karma and ReplayTV disks.

Important APIs and options: `config OMFS_FS` is a tristate option depending on `BLOCK`, selecting `BUFFER_HEAD` and `CRC_ITU_T`. The help text documents the module name `omfs` and positions the feature as device-specific filesystem support.

Control flow: no runtime control flow. Build selection controls whether the OMFS module or built-in filesystem is compiled.

State and persistence behavior: no filesystem state is stored here. The selected CRC and buffer-head dependencies enable runtime metadata checksum and block-buffer operations in `inode.c`, `dir.c`, `file.c`, and `bitmap.c`.

Dependencies and integration points: integrates with Kbuild and kernel configuration. `CRC_ITU_T` is required for OMFS inode header CRC generation, and `BUFFER_HEAD` is required by the implementation's `sb_bread`, `mark_buffer_dirty`, mpage, and block mapping paths.

Risks: dependency omissions would surface as build failures rather than runtime errors. The option does not depend on a specific architecture or endian mode because the code uses big-endian on-disk accessors.

Test signals: `CONFIG_OMFS_FS=y`, `m`, and `n` build coverage; module load/unload when built as `m`; and allmodconfig/allyesconfig coverage for selected dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/Makefile -->
## sources/distributed-fs/ceph-client/fs/omfs/Makefile

Purpose: describes the OMFS object composition for Kbuild.

Important APIs and targets: `obj-$(CONFIG_OMFS_FS) += omfs.o` builds the filesystem object when configured, and `omfs-y := bitmap.o dir.o file.o inode.o` links allocation, directory, file-mapping, and super/inode logic into one module or built-in object.

Control flow: no runtime control flow. The file controls link composition and therefore which translation units provide the symbols declared in `omfs.h`.

State and persistence behavior: no persistent state. Build output shape affects module packaging under the name `omfs`.

Dependencies and integration points: integrates with Kbuild and the `OMFS_FS` Kconfig symbol. The object order is straightforward and does not encode initialization ordering; module init/exit live in `inode.c`.

Risks: omitting any listed object would break cross-file references such as `omfs_aops`, `omfs_make_empty`, `omfs_count_free`, or `omfs_iget`.

Test signals: incremental and clean builds for built-in and module configurations, plus `modinfo omfs` when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/bitmap.c -->
## sources/distributed-fs/ceph-client/fs/omfs/bitmap.c

Purpose: implements OMFS free-space accounting and allocation over an in-memory bitmap mirrored from the on-disk free-space bitmap when present.

Important APIs and functions: `omfs_count_free` counts zero bits across all bitmap pages. `omfs_allocate_block` tries to reserve one exact block. `omfs_allocate_range` finds and marks a contiguous run satisfying `min_request` and up to `max_request`. `omfs_clear_range` clears an allocated run. Internal helpers `count_run` and `set_run` scan and modify runs that may cross bitmap buffer boundaries.

Control flow: allocation locks `s_bitmap_lock`, searches `s_imap` for zero bits, uses `count_run` to measure a free run across bitmap pages, and calls `set_run` to update both memory and the on-disk bitmap buffers. Exact block allocation computes the bitmap page and bit using division by bits per filesystem block. Clearing computes the starting page/bit and delegates to `set_run`.

State and persistence behavior: `s_imap` is the authoritative in-memory allocation map during the mount. If `s_bitmap_ino > 0`, changes are also written to bitmap blocks at `clus_to_blk(sbi, s_bitmap_ino) + map` and marked dirty. The bitmap lock serializes concurrent allocation and freeing. No journaling is used; dirty buffer writeback persists updates.

Dependencies and integration points: depends on `omfs_sb_info`, `clus_to_blk`, `sb_bread`, Linux bitmap helpers, and buffer-head dirtying. It is called from inode allocation in `inode.c`, file extent growth and truncation in `file.c`, and inode eviction.

Risks: if the on-disk bitmap read fails inside `set_run`, bits may already have been changed in earlier pages before returning an error. `omfs_allocate_block` sets the in-memory bit before reading the on-disk bitmap and does not roll back on `sb_bread` failure. Filesystems without a loaded bitmap have `s_imap_size == 0`, making allocation impossible unless a future tree-walk path is added. Bounds checking in `omfs_clear_range` only checks the starting map.

Test signals: mount with a valid bitmap, free-space counts before and after create/write/unlink, allocation crossing bitmap-block boundaries, ENOSPC behavior, exact contiguous extension via `omfs_allocate_block`, simulated bitmap I/O failures, and concurrent file creation/truncation under the bitmap mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/dir.c -->
## sources/distributed-fs/ceph-client/fs/omfs/dir.c

Purpose: implements OMFS directory lookup, create, mkdir, unlink, rmdir, rename, readdir, empty-directory initialization, and on-disk hash-chain validation.

Important APIs and functions: exported operations are `omfs_dir_inops` and `omfs_dir_operations`, plus helpers `omfs_make_empty` and `omfs_is_bad`. Key internals are `omfs_hash`, `omfs_get_bucket`, `omfs_scan_list`, `omfs_find_entry`, `omfs_add_link`, `omfs_delete_entry`, `omfs_dir_is_empty`, `omfs_remove`, `omfs_add_node`, `omfs_lookup`, `omfs_fill_chain`, `omfs_rename`, and `omfs_readdir`.

Control flow: directories are hash tables embedded in the directory inode block starting at `OMFS_DIR_START`, with each bucket storing the first inode block in a sibling chain. Lookup hashes the dentry name, reads the bucket pointer, then follows sibling inodes until a matching name is found. Create and mkdir allocate a new inode, initialize the inode block, prepend it to the target bucket, set the child name/sibling/parent fields, and instantiate the dentry. Unlink/rmdir remove an entry from the hash chain and clear the inode link count. Rename optionally removes an existing destination, deletes the old hash entry first, then adds the old inode under the new name.

State and persistence behavior: directory membership is persisted through bucket head pointers in the parent block and `i_sibling`, `i_parent`, and `i_name` fields in child inode blocks. Dirty parent and child inodes are later checksummed by `omfs_write_inode`. New directories initialize all bucket pointers to `~0`; regular files initialize an empty extent table. `ctx->pos` encodes readdir progress with high bits for bucket number and low 20 bits for chain index.

Dependencies and integration points: uses `omfs_bread`, `omfs_iget`, `omfs_new_inode`, `omfs_make_empty_table`, VFS dentry/inode operations, buffer-head dirtying, and dcache splice helpers. `omfs_is_bad` validates `h_self` and basic block range against superblock limits and is shared with file extent traversal.

Risks: `omfs_dir_is_empty` appears inverted: it returns `*ptr != ~0` after the loop, while callers treat false as empty, so empty-directory handling deserves targeted validation. Name comparisons use `strncmp` for `namelen` without checking that the on-disk name terminates at the same length, so prefix collisions may be possible. Rename is not atomic and can lose the old entry if adding the new link fails after deletion. Error mapping often returns `-ENOMEM` for read failures. Readdir position packing limits per-bucket chain indexes to 20 bits and rejects positions with bits above 32.

Test signals: lookup with case-insensitive hash collisions, create/unlink/rmdir, non-empty directory rejection, rename within and across directories, overwrite rename with `RENAME_NOREPLACE`, names at `OMFS_NAMELEN`, corrupt sibling self-pointers, readdir resume from nonzero cookies, and checksum updates after directory mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/file.c -->
## sources/distributed-fs/ceph-client/fs/omfs/file.c

Purpose: implements OMFS regular-file extent tables, block mapping, read/write address-space operations, truncate behavior, and file inode operations.

Important APIs and functions: exports `omfs_file_operations`, `omfs_file_inops`, `omfs_aops`, `omfs_make_empty_table`, and `omfs_shrink_inode`. Internal mapping helpers include `omfs_max_extents`, `omfs_grow_extent`, `find_block`, `omfs_get_block`, `omfs_read_folio`, `omfs_readahead`, `omfs_writepages`, `omfs_write_begin`, `omfs_write_failed`, `omfs_bmap`, `omfs_truncate`, and `omfs_setattr`.

Control flow: reads and writes call `omfs_get_block`, which reads the inode's inline extent table at `OMFS_EXTENT_START`, validates the table owner, scans extents for the logical block, follows continuation tables if present, and maps the corresponding physical block. If create is requested and no mapping exists, `omfs_grow_extent` first tries to extend the previous extent by allocating the immediate next block; otherwise it allocates a new contiguous range and inserts a new extent before the terminator. Truncate currently only supports freeing data when the resulting inode size is zero; it walks extent tables, clears allocated ranges, resets tables to an empty terminator, and frees continuation blocks.

State and persistence behavior: file layout is persisted in `struct omfs_extent` records embedded in the inode block and optional continuation blocks. Extent tables use a terminator entry whose fields are all ones, with `e_blocks` adjusted as new blocks are added. Allocation state is synchronized through the bitmap code. Dirty extent buffers and inode metadata are persisted through buffer and inode writeback; `simple_fsync` handles fsync at the file operations level.

Dependencies and integration points: uses Linux block helpers (`block_read_full_folio`, `block_write_begin`, `mpage_readahead`, `mpage_writepages`, `generic_block_bmap`), OMFS bitmap allocation/free, directory corruption helper `omfs_is_bad`, and inode writeback in `inode.c`. The VFS `setattr` path handles size changes and calls `omfs_truncate`.

Risks: sparse files and nonzero truncation are explicitly not supported; holes return unmapped blocks until writes append at the end, so random writes beyond EOF are risky. Continuation block creation is marked TODO, but traversal supports existing continuations; growing past the inline extent-table capacity returns `-EIO`. `omfs_shrink_inode` clears ranges without propagating `omfs_clear_range` errors. `omfs_grow_extent` mutates the bitmap before the extent table is safely persisted, so writeback failure can leak or orphan blocks.

Test signals: sequential write/read, extent coalescing through exact next-block allocation, allocation of a new extent when contiguity fails, growth to max inline extents, existing continuation-table read/truncate, truncate-to-zero after writes, unsupported truncate-to-nonzero, write failure rollback via `omfs_write_failed`, bmap output, mmap read/write, and ENOSPC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/inode.c -->
## sources/distributed-fs/ceph-client/fs/omfs/inode.c

Purpose: implements OMFS module registration, mount option parsing, superblock probing, in-memory superblock setup, inode allocation/loading/writeback/eviction, statfs, and root creation.

Important APIs and functions: exported helpers are `omfs_bread`, `omfs_new_inode`, `omfs_sync_inode`, and `omfs_iget`. Superblock and module paths include `omfs_fill_super`, `omfs_get_tree`, `omfs_init_fs_context`, `omfs_free_fc`, `init_omfs_fs`, and `exit_omfs_fs`. Other core functions are `omfs_update_checksums`, `__omfs_write_inode`, `omfs_write_inode`, `omfs_evict_inode`, `omfs_put_super`, `omfs_statfs`, `omfs_show_options`, `omfs_get_imap`, `omfs_parse_param`, and `omfs_set_options`.

Control flow: mount initializes default uid/gid/masks, parses options through the fs_context parser, reads the 512-byte superblock, validates magic and size limits, switches the VFS block size to the OMFS system-block size, reads the root block, validates block counts, bitmap location, and cluster size, loads the free-space bitmap into `s_imap`, installs super operations, loads the root directory inode, and creates `sb->s_root`. Inode loading uses `iget_locked`, reads the OMFS inode block, validates `h_self`, sets uid/gid and timestamps from millisecond ctime, installs directory or file operations, and unlocks the inode. Dirty inode writeback rebuilds the OMFS header, updates CRC and XOR checksums, writes mirrored system blocks, and reports synchronous write failure.

State and persistence behavior: `struct omfs_sb_info` stores block counts, root and bitmap locations, block-size conversion, mirror count, allocation bitmap, mount ownership, masks, and the bitmap mutex. Inode metadata persisted by `__omfs_write_inode` includes self pointer, type, body size, version, magic, size, ctime, CRC, and XOR. `omfs_evict_inode` frees file data on last unlink and clears inode allocation bits, although it uses a hard-coded count of 2 blocks rather than `s_mirrors`.

Dependencies and integration points: integrates with Linux `fs_context`, block-device mounting via `get_tree_bdev`, VFS inode and super operations, crc-itu-t, buffer-head I/O, allocation functions in `bitmap.c`, file and directory operation tables, and Kbuild/module registration. Mount options use standard uid/gid/octal parsers and are displayed in `/proc/mounts`.

Risks: the error path in `omfs_fill_super` frees `sbi` without clearing `sb->s_fs_info`, while `omfs_put_super` also assumes ownership on successful mounts. `omfs_get_imap` returns success without allocating `s_imap` when `s_bitmap_ino == ~0ULL`, but allocation code depends on `s_imap_size`, so ReplayTV-style no-bitmap support is incomplete unless handled elsewhere. Superblock validation does not verify all power-of-two assumptions before computing `s_block_shift`. Inode eviction clears two blocks instead of `s_mirrors`, which can leak or incorrectly free mirrored inode blocks if mirror count differs. Checksum validation is written on output but not enforced on inode read.

Test signals: mount valid Rio Karma images, invalid magic, inconsistent super/root block counts, out-of-range block/sysblock/cluster sizes, corrupt bitmap location, uid/gid/umask/dmask/fmask mount options and show_options output, inode read/write checksum updates, mirrored inode writes with `s_mirrors > 1`, statfs free counts, unlink eviction freeing data and inode blocks, sync write error handling, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/omfs.h -->
## sources/distributed-fs/ceph-client/fs/omfs/omfs.h

Purpose: provides OMFS in-memory superblock state, cluster-to-block conversion, and cross-file function declarations shared by bitmap, directory, file, and inode code.

Important APIs and types: `struct omfs_sb_info` stores total blocks, bitmap/root inode locations, block and system-block sizes, mirror count, cluster size, block shift, in-memory bitmap array, bitmap lock, and mount uid/gid/masks. `clus_to_blk` scales OMFS cluster/block numbers to VFS block numbers using `s_block_shift`. `OMFS_SB` retrieves private superblock state. Declarations cover allocation, directory operations, file operations, block reading, inode allocation/loading, and sync.

Control flow: no active control flow beyond inline conversion/accessor helpers. The declared APIs define module boundaries: bitmap allocation is used by inode and file code; directory helpers initialize inode blocks; file helpers provide address-space operations; inode helpers own superblock and inode lifecycle.

State and persistence behavior: this header defines in-memory mount state only. Persistent structures come from `omfs_fs.h`, included here. `s_imap` mirrors allocation state from disk and is protected by `s_bitmap_lock`.

Dependencies and integration points: includes Linux module/fs headers and `omfs_fs.h`. It is the central internal contract among all OMFS translation units. The declarations `omfs_reserve_block` and `omfs_find_empty_block` are present but not implemented or used in this source set, likely stale prototypes.

Risks: `clus_to_blk` assumes `s_block_shift` was correctly derived from compatible power-of-two sizes at mount. Callers assume `OMFS_SB(sb)` is valid after mount setup. Stale extern declarations can mislead future maintainers or hide missing cleanup when refactoring.

Test signals: compile with sparse/W=1 for unused or stale prototypes, mount images with different system/data block-size ratios, allocation and mapping tests that verify `clus_to_blk`, and teardown tests confirming `s_imap` ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/omfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/omfs_fs.h -->
## sources/distributed-fs/ceph-client/fs/omfs/omfs_fs.h

Purpose: defines the OMFS on-disk constants and packed-by-layout structures used to parse superblocks, root blocks, inode headers, directory/file inode records, and file extent tables.

Important APIs and types: constants include `OMFS_MAGIC`, `OMFS_IMAGIC`, inode type tags (`OMFS_DIR`, `OMFS_FILE`, `OMFS_INODE_*`), layout offsets (`OMFS_DIR_START`, `OMFS_EXTENT_START`, `OMFS_EXTENT_CONT`), `OMFS_NAMELEN`, checksum byte count, and max block/cluster limits. Structures are `omfs_super_block`, `omfs_header`, `omfs_root_block`, `omfs_inode`, `omfs_extent_entry`, and `omfs_extent`.

Control flow: no executable control flow. The constants drive offset arithmetic throughout directory initialization, readdir, file extent mapping, mount validation, and checksum generation.

State and persistence behavior: all multi-byte on-disk fields are big-endian and accessed by callers with `beXX_to_cpu`/`cpu_to_beXX`. Directory blocks store bucket arrays after `OMFS_DIR_START`; file inode blocks store extent tables after `OMFS_EXTENT_START`; continuation blocks store extent tables after `OMFS_EXTENT_CONT`. `omfs_header` carries a self block number, body size, CRC, version, type, magic, and XOR check byte.

Dependencies and integration points: included by `omfs.h` and therefore all OMFS implementation files. Its layout must match the proprietary on-disk format used by Rio Karma and ReplayTV devices, and its max constants are enforced during mount.

Risks: the structures are not explicitly marked packed, so correctness relies on field ordering and natural alignment matching the on-disk format on supported ABIs. No compile-time offset assertions are present. `OMFS_NAMELEN` names may not be NUL-terminated on disk, so callers must use bounded string operations consistently. The max block count and block-size constants are part of the mount-time trust boundary for crafted images.

Test signals: build-time offset/size checks if added, mounting known-good images, fuzzing malformed super/root/inode/extent structures, endian correctness on big- and little-endian systems, names at the 256-byte limit, and checksum validation tests if read-side validation is introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/omfs/omfs_fs.h -->
