# Group Research: group_913_linux_apfs_rw_sources_local_fs_linux_apfs_rw_Makefile_sources_local__e7011f6d617f

Scope confirmed against `Docs/research_subset_a.md`: `sources/local-fs/linux-apfs-rw` is included in subset A. All requested files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/Makefile -->
# File Research: sources/local-fs/linux-apfs-rw/Makefile

This is the out-of-tree Linux kernel module build file for the APFS driver. It builds one module, `apfs.o`, using kbuild with `obj-m = apfs.o`.

The module object list is explicit in `apfs-y`: APFS core sources such as `btree.o`, `compress.o`, `dir.o`, `extents.o`, `file.o`, `inode.o`, `node.o`, `object.o`, `spaceman.o`, `super.o`, `transaction.o`, `xattr.o`, and bundled LZFSE/LZVN decoder objects.

Build variables default to the running kernel: `KERNELRELEASE ?= $(shell uname -r)`, `KERNEL_DIR ?= /lib/modules/$(KERNELRELEASE)/build`, and `PWD := $(shell pwd)`.

`ccflags-y += $(APFS_CONFIG)` allows optional compile-time flags. The file documents `APFS_CONFIG=-DCONFIG_APFS_RW_ALWAYS`, which makes mounts writable by default and is explicitly marked risky.

Targets:
- `default`: runs `./genver.sh`, then invokes `make -C $(KERNEL_DIR) M=$(PWD)`.
- `install`: runs kbuild `modules_install`.
- `clean`: removes generated `version.h`, then runs kbuild clean.

Research relevance: this file defines the module composition and the feature flag entry point for default read-write behavior.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/apfs.h -->
# File Research: sources/local-fs/linux-apfs-rw/apfs.h

This is the central private header for the APFS kernel module. It includes Linux kernel headers, `apfs_raw.h`, compatibility wrappers, in-memory APFS data structures, inline helpers, logging/assertion macros, and cross-file function declarations.

Compatibility coverage is broad. It handles RHEL-specific version tests, pre-4.14 superblock flag names, pre-5.3 lockdep helpers, `submit_bh()` API differences, newer `fileattr` naming, inode state accessors for newer kernels, `read_folio`/`readpage` era APIs through declarations, and block-device handle/file mode differences.

Major in-memory structures:
- `struct apfs_object`: generic APFS object wrapper with superblock, block number, object id, buffer head, raw data pointer, and ephemeral flag.
- `struct apfs_node`: in-memory b-tree node metadata, table/free/key/value offsets, free-list lengths, and backing `apfs_object`.
- `struct apfs_spaceman`: in-memory space manager, chunk geometry, free counts, free-cache range, internal-pool bitmap metadata.
- `struct apfs_nx_transaction`: shared container transaction state, delayed commit work, joined inodes/buffers, and transaction counters.
- `struct apfs_blkdev_info`: portability wrapper for block device state, including newer kernel handles/files and optional Fusion tier path.
- `struct apfs_nxsb_info`: container-wide state: devices, raw container superblock, xid, ephemeral list, mounted volume list, spaceman, transaction, and `nx_big_sem`.
- `struct apfs_omap` and cache types: object-map root, small direct-mapped omap cache, latest snapshot xid, and refcount.
- `struct apfs_sb_info`: per-volume state, including catalog root, omap, mounted snapshot metadata, mount options, default crypto state, private directory, and orphan cleanup work.
- `struct apfs_query`: b-tree query state with key, parent chain, flags, found key/value offsets, and recursion depth.
- `struct apfs_dstream_info`: file/xattr data stream state, cached extent, sparse byte count, dirty flag, and sharing state.
- `struct apfs_inode_info`: APFS inode extension with 64-bit inode id, parent id, creation time, APFS flags, optional dstream, cleanup state, and embedded VFS inode.

Important inline helpers:
- Node predicates: leaf/root/fixed key-value size.
- Superblock accessors: `APFS_SB`, `APFS_NXI`, `APFS_SM`.
- Volume predicates: sealed, encrypted, case-insensitive, normalization-insensitive.
- Key initializers for omap, free queue, extents, inode, file extents, dstream id, crypto state, sibling links/maps, xattrs, snapshots.
- Catalog key header helpers: `apfs_key_set_hdr`, `apfs_cat_type`, `apfs_cat_cnid`.
- Query storage selection for physical, virtual, and ephemeral b-trees.
- 64-bit inode helpers `apfs_ino` and `apfs_set_ino`.
- Buffer-head mapping/read/get helpers that route APFS block numbers to the main or Fusion tier-2 device.

The file declares the module’s internal API across `btree.c`, `compress.c`, `dir.c`, `extents.c`, `file.c`, `inode.c`, `key.c`, `node.c`, `object.c`, `snapshot.c`, `spaceman.c`, `super.c`, `transaction.c`, `xattr.c`, and `xfield.c`.

Research relevance: this header is the contract tying the driver together. It defines the shared locking model, object/query abstractions, APFS metadata state, VFS operation declarations, and block-device mapping policy.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/apfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/apfs_raw.h -->
# File Research: sources/local-fs/linux-apfs-rw/apfs_raw.h

This header defines packed APFS on-disk data structures, constants, flags, masks, and record formats. It is the driver’s local APFS disk-format specification.

It starts with object identifiers, object type masks, storage flags, APFS object types, and `struct apfs_obj_phys`, the common on-disk object header containing checksum, oid, xid, type, and subtype.

Object-map definitions include omap flags, `struct apfs_omap_phys`, omap value flags, `struct apfs_omap_val`, and snapshot omap records. These feed object-id to block-number resolution in `btree.c` and object loading elsewhere.

B-tree definitions cover node flags, key/value location structs, `struct apfs_btree_node_phys`, b-tree info flags, fixed b-tree info, and root b-tree info counters. These are consumed by node and btree logic for searching, insertion, splitting, replacement, and metadata count updates.

Catalog and file metadata definitions include:
- Directory record values and dentry key formats, both hashed and unhashed.
- Physical extent values, kind masks, file extent values, and file extent flags.
- Dstream id values and crypto state records.
- APFS inode numbers, inode internal flags, BSD flags, and `struct apfs_inode_val`.
- Extended field blob/key format and xfield type constants.
- Dstream, directory stats, sibling link, and sibling map values.
- Catalog record type enum and key header format.

Space management definitions include chunk info records, chunk info blocks, chunk info address blocks, free queue structures, device allocation info, allocation zone data, internal-pool bitmap constants, and `struct apfs_spaceman_phys`.

Container-level definitions include NX magic, limits, feature flags, incompatibility masks, block-size limits, counter indices, `struct apfs_nx_superblock`, checkpoint mapping records, and checkpoint map blocks.

Volume-level definitions include volume magic, flags, roles, supported feature masks, incompatible feature masks, modified-by history, protection classes, crypto identifiers, wrapped metadata crypto state, and `struct apfs_superblock`.

Extended attributes and sealed-volume definitions include xattr names, xattr value/dstream formats, integrity metadata, hash algorithm constants, file extent tree key/value formats, file info records, sealed catalog index value format, and compressed file formats.

Compression definitions enumerate APFS decmpfs algorithms: zlib, LZVN, plain, LZFSE, and lzbitmap, in both attribute and resource-fork storage forms. Snapshot metadata/name records and keybag/locker formats are also defined.

Research relevance: this file is purely structural but critical. It establishes exact byte layouts and masks for every higher-level operation in the implementation files.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/apfs_raw.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/btree.c -->
# File Research: sources/local-fs/linux-apfs-rw/btree.c

This file implements APFS b-tree query and update operations plus object-map lookup/update support. It is copy-on-write aware and is used by catalog, omap, free queue, extent-reference, sealed fext, snapshot, and other trees.

Object-map support:
- Maintains a small direct-mapped omap cache keyed by oid.
- Resolves virtual object ids to physical block numbers for mounted xid or newest xid.
- Handles snapshot-aware CoW: if writing an object whose omap record belongs to a snapshot, it inserts a new omap record for the current xid; otherwise it replaces the existing mapping.
- Provides `apfs_create_omap_rec()` and `apfs_delete_omap_rec()` for object lifecycle updates.

Query support:
- `apfs_alloc_query()` creates query-chain nodes and inherits key/flags from parents.
- `apfs_free_query()` releases the chain and non-root nodes.
- `apfs_btree_query()` descends from root to leaf, using `apfs_node_query()` at each level, `apfs_child_from_query()` to read child ids, and a depth cap of 12 to reject corrupt trees.
- It supports reverse/forward multiple-record traversal, exact matches, and insertion-before-first positioning.
- `apfs_query_direct_forward()` flips a successful query chain into forward listing mode.

Mutation support:
- `apfs_query_join_transaction()` CoWs non-root nodes into the current transaction and updates parent physical child pointers when needed.
- `apfs_btree_insert()` wraps `__apfs_btree_insert()` with retry after node split and refreshes invalidated query ancestors.
- `apfs_btree_remove()` removes leaf records, recursively removes empty child nodes, updates parent first keys, and changes root leaf status if the tree empties.
- `apfs_btree_replace()` replaces key/value material without changing ordering and retries after splits.
- Root b-tree metadata is updated for record count, node count, longest key, and longest value.

Integrity checks include validation of nonleaf child value length, sealed catalog index value length, max tree depth, expected leaf/root state, and stale record clearing on failed queries.

Research relevance: this is the generic metadata-tree engine. Most higher-level APFS changes depend on its query-chain refresh, transaction joining, node splitting, and root counter maintenance.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/compress.c -->
# File Research: sources/local-fs/linux-apfs-rw/compress.c

This file implements transparent read support for APFS compressed files stored through `com.apple.decmpfs` and optionally `com.apple.ResourceFork`.

Supported algorithms:
- zlib attribute/resource.
- LZVN attribute/resource.
- plain attribute/resource.
- LZFSE attribute/resource.
- lzbitmap attribute/resource.

`apfs_compress_file_open()` rejects write opens with `-EOPNOTSUPP`, reads the decmpfs header from xattrs, validates the algorithm, allocates a 64 KiB decompression buffer, and obtains compressed data either from the compressed xattr or resource fork.

`apfs_compress_file_read_block()` maps the APFS compressed layout to one decompressed 64 KiB logical block. It handles resource-fork block tables, inline attribute compression, and per-algorithm framing quirks. It then decompresses or copies data into the cached buffer.

`apfs_compress_file_read_from_block()` clamps reads to the uncompressed size, prereads nonsparse dstreams for xattr/resource data, loads the target compressed block if not cached, and copies the requested slice.

`apfs_compress_file_read_page()` fills one page through repeated block reads. The address-space operations expose either `read_folio` or `readpage` depending on kernel version, zeroing the remainder and marking the page uptodate on success.

`apfs_compress_file_operations` provides open, llseek, read_iter, release, and mmap. A comment notes these operations lack proper locking. Writes are intentionally unsupported rather than transparently decompressing/replacing content.

`apfs_compress_get_size()` reads the decmpfs header and reports the uncompressed size if the algorithm is supported.

Research relevance: this file provides read-path integration for compressed APFS files and shows a clear limitation: compressed files are read-only through this driver.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/dir.c -->
# File Research: sources/local-fs/linux-apfs-rw/dir.c

This file implements directory lookup, readdir, create, link, unlink, rmdir, rename, hard-link sibling metadata, and orphan-link handling.

Lookup/readdir:
- `apfs_drec_from_query()` decodes directory records, validates key/value sizes and null-terminated names, extracts optional sibling-id xfields, and maps APFS dentry flags to Linux dirent types.
- `apfs_dentry_lookup()` queries the catalog tree for a child name. For normalization-insensitive volumes it deals with hash collisions by iterating candidates and comparing names.
- `apfs_inode_by_name()` wraps lookup under `nx_big_sem`.
- `apfs_readdir()` emits dots, then queries all matching child records for the directory cnid and emits entries through `dir_emit()`.

Creation:
- Builds hashed or unhashed dentry keys depending on normalization behavior.
- Builds dentry values with date-added, file type, and optional sibling-id xfield.
- `apfs_mkany()` starts a transaction, creates a new inode, creates the inode record, creates dentry/sibling records, optionally stores symlink target xattr, commits, and instantiates the dentry.
- `apfs_mknod`, `apfs_mkdir`, and `apfs_create` are version-adapted wrappers around `apfs_mkany()`.

Hard links:
- Sibling link records list hard-link names for an inode.
- Sibling map records map sibling ids back to file ids.
- When linking the second name to an inode, the original primary dentry may be rewritten to acquire sibling metadata.
- `apfs_link()` increments link count, creates required sibling/dentry records, commits, and instantiates the new dentry.

Deletion/orphans:
- `apfs_delete_dentry()` removes the dentry record and any sibling records, updates parent timestamps and child count, and joins parent inode to the transaction.
- `__apfs_unlink()` drops link count. If it reaches zero, it creates an invisible orphan link under the APFS private directory and decrements volume file counts; otherwise it finds the new primary link.
- `apfs_delete_orphan_link()` removes orphan records during cleanup.
- `apfs_any_orphan_ino()` scans the private directory for regular-file orphan links named `0x<ino>-dead`.

Rename:
- Supports normal rename and `RENAME_NOREPLACE`; rejects unsupported flags such as exchange.
- If replacing a target, unlinks it first.
- Then links the old inode at the new dentry and unlinks the old dentry within one transaction, with undo helpers for abort/commit failure paths.

Research relevance: this file is the APFS catalog mutation layer for namespace operations. It coordinates b-tree records, inode metadata, link counts, private-directory orphan recovery, and Linux VFS API version differences.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/dkms.conf -->
# File Research: sources/local-fs/linux-apfs-rw/dkms.conf

This is the DKMS packaging configuration for the module.

Fields:
- `PACKAGE_NAME="linux-apfs-rw"`.
- `PACKAGE_VERSION="0.3.20"`.
- Builds module name `apfs`.
- Installs to `/extra`.
- Enables `AUTOINSTALL="yes"`.
- Runs `PRE_BUILD="genver.sh"`.

Research relevance: DKMS uses this file to build and install the out-of-tree `apfs` kernel module automatically. `genver.sh` also uses `PACKAGE_VERSION` as a fallback version source when git metadata is unavailable.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/dkms.conf -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/extents.c -->
# File Research: sources/local-fs/linux-apfs-rw/extents.c

This file implements APFS file/data-stream extent mapping, allocation, truncation, sparse holes, physical extent reference tracking, cloning, and nonsparse dstream reads.

Read mapping:
- `apfs_extent_from_query()` decodes logical extent records from either the catalog tree or sealed-volume fext tree.
- `apfs_extent_read()` locates and caches the extent covering a logical dstream block.
- `apfs_logic_to_phys_bno()` converts logical block to physical block, returning zero for holes.
- `__apfs_get_block()` maps existing extents to buffer heads for read paths without taking locks; `apfs_get_block()` wraps it under `nx_big_sem`.

Dirty extent cache/write allocation:
- Newly allocated blocks are initially accumulated in `ds_cached_ext` and marked dirty.
- `apfs_dstream_get_new_block()` allocates a physical block, maps/join buffers to the transaction, handles zeroing for new/stale partial blocks, checks whether the cached extent overlaps snapshots, creates sparse holes when extending beyond EOF, and flushes or extends the dirty cache as needed.
- `apfs_flush_extent_cache()` writes the dirty logical extent and physical extent records.

Logical extent updates:
- Extents can be shrunk at head or tail, split, replaced, or inserted.
- Tail updates handle append/growth and replacement of the last extent.
- Mid-file updates are restricted to single-block extents and carefully handle replacing holes, shrinking existing extents, and splitting extents around the new block.
- Sparse hole records use physical block zero and update `ds_sparse_bytes`.

Physical extent-reference tree:
- Physical extents are decoded with `apfs_phys_ext_from_query()`.
- New physical extents are inserted or extended where possible.
- Reference changes split physical extent records at range boundaries, then increment/decrement refcounts.
- Dropping the last reference removes the physical extent record and, for new extents, returns blocks to the free queue and updates volume allocation/free counters.
- Snapshot overlap detection conservatively forces copy-on-write when needed.

Truncation/deletion:
- `apfs_truncate()` flushes cached extents, invalidates the cache, shrinks for smaller sizes, or creates hole extents for larger sparse growth after zeroing the old tail.
- `apfs_shrink_dstream_last_extent()` repeatedly removes or shrinks tail extents until the target size is reached.
- `apfs_inode_delete_front()` deletes as many leading extents as possible, stopping with `-EAGAIN` when the free queue grows too full.

Clone/remap:
- `apfs_remap_file_range()` / `apfs_clone_file_range()` only supports whole-file clone replacement into a freshly created destination.
- It rejects self-clones, partial ranges, compressed/existing dstream targets, and targets with certain xfields.
- Cloning shares the source dstream id, increments the dstream refcount, marks source/destination shared, copies inode flags/size/key class, and forces a transaction commit to make future source writes CoW.
- `apfs_clone_extents()` can create logical extent records under a new dstream id and increment physical references.

Nonsparse dstream helpers:
- `apfs_nonsparse_dstream_read()` reads exact byte ranges from dstreams expected to have no holes, issuing buffer reads and copying requested slices.
- `apfs_nonsparse_dstream_preread()` submits asynchronous reads for all blocks, used by compression/resource-fork paths.

Research relevance: this is the core APFS data-block management layer. It connects logical file extents, physical block allocation, snapshot/clone reference counts, sparse files, truncation, and Linux buffer-head mapping.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/file.c -->
# File Research: sources/local-fs/linux-apfs-rw/file.c

This file implements regular-file VFS operations, mmap write-fault handling, fsync, clone/remap hooks, and inode operation wiring.

`apfs_page_mkwrite()` handles mmap write faults. It starts a regular APFS transaction, joins the inode, ensures the inode has an exclusive dstream, locks and validates the page, creates page buffers if needed, clears mapped state on existing buffers so APFS CoW allocation can occur, then calls `block_page_mkwrite()` with `apfs_get_new_block`. It marks the page dirty and defers immediate transaction commit because commit would unlock the page too early.

`apfs_file_vm_ops` uses generic filemap fault/map_pages and APFS `page_mkwrite`. `apfs_file_mmap()` verifies that the mapping has a read operation for the kernel era, marks the file accessed, and installs those vm ops.

`apfs_fsync()` currently syncs the whole filesystem transaction with `apfs_sync_fs(sb, true)`. A comment notes this is broad but correct and easy.

Regular file operations include generic llseek/read/write/open, APFS mmap, APFS fsync, file ioctl, copy-file-range support depending on kernel version, APFS remap/clone range support, and splice read/write compatibility choices.

For Linux 5.3 only, `apfs_fiemap()` is provided through `generic_block_fiemap()` for clone testing. `apfs_file_inode_operations` wires getattr, listxattr, setattr, update_time, fileattr get/set on newer kernels, and optional fiemap.

Research relevance: this file is the VFS-facing regular-file adapter. The most important behavior is mmap write CoW integration through transactions and `apfs_get_new_block`.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/genver.sh -->
# File Research: sources/local-fs/linux-apfs-rw/genver.sh

This shell script generates `version.h` for the kernel module build.

Behavior:
- If `git` is available and `.git` exists, it sets `GIT_COMMIT` from `git describe HEAD | tail -c 9`.
- Otherwise, it reads `PACKAGE_VERSION` from `dkms.conf` and appends `?`.
- It writes `#define GIT_COMMIT "<value>"` to `version.h`.

Research relevance: this is build metadata generation. It gives the module a compile-time version/commit string, with DKMS package version fallback outside a git checkout.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/genver.sh -->