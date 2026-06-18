# Group Research: group_761_linux_sources_os_linux_linux_fs_hfs_brec_c_sources_os_linux_linux_fs_73961b3500e3

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/brec.c -->
# File Research: sources/os/linux/linux/fs/hfs/brec.c

Purpose: Implements low-level HFS B-tree record mutation: record length/key length decoding, insertion, deletion, node splitting, parent-key propagation, and root height growth.

Key functions:
- `hfs_brec_lenoff()` reads the offset table at the end of a node to derive record offset and length.
- `hfs_brec_keylen()` decodes fixed or variable HFS keys, including big-key handling and max-key validation.
- `hfs_brec_insert()` inserts a key+entry pair into a leaf or index node, splitting nodes and recursively adding index records when needed.
- `hfs_brec_remove()` removes a record, compacts node data/offset tables, unlinks empty nodes, and removes parent index records.
- `hfs_bnode_split()` allocates a B-tree node, moves upper records, relinks leaf/index sibling pointers, and adjusts the active search cursor.
- `hfs_brec_update_parent()` updates ancestor separator keys after first-record changes.
- `hfs_btree_inc_height()` creates a new root when the tree grows.

Dependencies and integration:
- Depends on `btree.h` node I/O helpers, bitmap allocation, search cursor state, and `__hfs_brec_find()`.
- Called by catalog and extent code through `hfs_brec_insert()`/`hfs_brec_remove()`.
- Marks the B-tree inode dirty when leaf counts, root, tail, or node metadata change.

Risk notes:
- Correctness depends on exact offset-table arithmetic and even-sized key layout.
- Error paths around parent updates and split recursion can leave partially modified B-tree structures if callers do not reserve nodes first.
- The code uses `panic("not enough room!")` if a split still cannot fit the record, so malformed trees or reservation bugs can escalate hard.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/brec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/btree.c -->
# File Research: sources/os/linux/linux/fs/hfs/btree.c

Purpose: Opens, closes, writes, extends, allocates, and frees nodes in classic HFS B-trees.

Key functions:
- `hfs_btree_open()` creates an in-memory `hfs_btree`, attaches the extents or catalog special inode, reads node 0, validates header fields, and configures node sizing.
- `hfs_btree_close()` drains the node hash and releases the B-tree inode.
- `hfs_btree_write()` writes updated root/leaf/node/free-count metadata into the header record.
- `hfs_bmap_reserve()` extends the B-tree file until at least a requested number of free nodes exists.
- `hfs_bmap_alloc()` scans header/map-node bitmap records for a free node bit, sets it, and returns a zeroed node object.
- `hfs_bmap_free()` clears a node bit in the B-tree bitmap and increments `free_nodes`.

Dependencies and integration:
- Uses MDB fork extents from `HFS_SB(sb)->mdb` and `hfs_inode_read_fork()` to model catalog/extents B-tree files.
- Uses `hfs_ext_find_block()` to locate physical blocks for the header read.
- Works with `bnode.c` helpers declared in `btree.h` and B-tree mutation logic in `brec.c`.

Risk notes:
- Header validation covers power-of-two node size, nonzero node count, and expected max-key lengths, but assumes node 0 can be read into the first folio.
- `hfs_bmap_new_bmap()` still has a `panic("FIXME!!!")` when no free nodes remain while creating a new bitmap node.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/btree.h -->
# File Research: sources/os/linux/linux/fs/hfs/btree.h

Purpose: Defines the in-memory HFS B-tree and B-node data structures, search cursor state, lock classes, flags, and public B-tree helper prototypes.

Key structures:
- `struct hfs_btree` stores superblock, backing inode, comparator, catalog/extents CNID, tree header fields, node size/depth, mutex, and node hash table.
- `struct hfs_bnode` stores node identity, sibling/parent links, type/height, record count, refcount, flags, wait queue, page offset, and variable page array.
- `struct hfs_find_data` carries search and current keys, target tree, current node, record index, and key/entry offsets and lengths.

Dependencies and integration:
- Includes `hfs_fs.h`, so all HFS B-tree users share the filesystem-private inode/superblock definitions.
- Exposes APIs implemented across `btree.c`, `bnode.c`, `brec.c`, and `bfind.c`.

Risk notes:
- This header is central to cross-file invariants: callers must hold `tree_lock` via `hfs_find_init()` while mutating records and must balance `hfs_bnode_get()`/`hfs_bnode_put()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/catalog.c -->
# File Research: sources/os/linux/linux/fs/hfs/catalog.c

Purpose: Implements classic HFS catalog B-tree key construction, comparison, create/delete/rename operations, and CNID thread lookup.

Key functions:
- `hfs_cat_build_key()` builds catalog keys from parent CNID and Mac-encoded name, or a thread lookup key when name is `NULL`.
- `hfs_cat_build_record()` initializes file or directory catalog records.
- `hfs_cat_build_thread()` creates file/folder thread records mapping CNID back to parent/name.
- `hfs_cat_keycmp()` sorts catalog keys by parent ID then Macintosh lexical filename order.
- `hfs_cat_find_brec()` resolves a CNID thread record and then finds the actual catalog record.
- `hfs_cat_create()` inserts thread and visible catalog records atomically enough to roll back the thread on later failure.
- `hfs_cat_delete()` removes the visible record, optional thread record, resource fork blocks, and updates open readdir positions.
- `hfs_cat_move()` implements rename by inserting the new record, removing the old record, and rewriting the thread record.

Dependencies and integration:
- Uses `hfs_asc2mac()`, `hfs_mac2asc()`, `hfs_strcmp()`, B-tree search/mutation APIs, and inode dirty marking.
- Coordinates directory `i_size` as valence plus `.`/`..` convention used by `dir.c`.
- Maintains `next_id` recovery via `hfs_correct_next_unused_CNID()` after deletion.

Risk notes:
- Data fork freeing is compiled out in delete paths; resource fork freeing remains active.
- Rename/create operations depend on prior `hfs_bmap_reserve()` to avoid mid-operation ENOSPC.
- CNID count overflow and corrupt catalog ordering are explicitly guarded in newer code paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/catalog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/dir.c -->
# File Research: sources/os/linux/linux/fs/hfs/dir.c

Purpose: Provides classic HFS directory VFS operations: lookup, readdir, create, mkdir, unlink/rmdir, rename, and operation tables.

Key functions:
- `hfs_lookup()` builds a catalog key from parent inode and dentry name, reads the catalog record, and returns `hfs_iget()` result via `d_splice_alias()`.
- `hfs_readdir()` emits synthetic `.` and `..`, then walks catalog records belonging to the directory using `hfs_brec_goto()`.
- `hfs_dir_release()` removes per-open readdir tracking from `open_dir_list`.
- `hfs_create()` and `hfs_mkdir()` allocate a new inode and add catalog entries.
- `hfs_remove()` checks directory emptiness, validates CNID counters, removes catalog entries, and clears the inode link.
- `hfs_rename()` supports only `RENAME_NOREPLACE`, removes existing destination, and updates the moved inode's cached catalog key.

Dependencies and integration:
- Uses catalog operations from `catalog.c`, inode constructors/deletion from `inode.c`, and B-tree search helpers.
- Maintains `hfs_readdir_data` so catalog deletion can adjust active directory file positions.

Risk notes:
- Directory `i_size` is treated as catalog valence plus two synthetic entries; bad catalog valence can affect iteration limits.
- `hfs_remove()` blocks mutation if CNID/file/folder counters exceed 32-bit limits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/extent.c -->
# File Research: sources/os/linux/linux/fs/hfs/extent.c

Purpose: Implements classic HFS extent overflow management, file block mapping, allocation, fork freeing, file extension, and truncation.

Key functions:
- `hfs_ext_keycmp()` sorts extent keys by file CNID, fork type, and allocation block number.
- `hfs_ext_find_block()` maps an allocation-block offset through a three-entry extent record.
- `hfs_ext_write_extent()` flushes dirty cached overflow extents into the extents B-tree.
- `hfs_free_fork()` frees inline and overflow extents for a file fork.
- `hfs_get_block()` maps or allocates logical file blocks for buffer/page-cache I/O.
- `hfs_extend_file()` allocates new allocation blocks, appends to inline/cached extents, or starts a new overflow extent record.
- `hfs_file_truncate()` frees excess allocation blocks and removes overflow extent records as needed.

Dependencies and integration:
- Uses volume bitmap APIs `hfs_vbm_search_free()` and `hfs_clear_vbm_bits()`.
- Uses B-tree search/mutation for overflow extents and marks MDB/alternate MDB dirty when allocation changes.
- Called by address-space operations in `inode.c`.

Risk notes:
- Uses 16-bit allocation block counts, matching classic HFS limits.
- Truncate error handling is explicitly incomplete in comments.
- Extent cache state flags must be kept consistent or dirty extents can be lost or duplicated.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/hfs.h -->
# File Research: sources/os/linux/linux/fs/hfs/hfs.h

Purpose: Small HFS-private header that includes shared on-disk/common definitions and defines `struct hfs_readdir_data`.

Key structure:
- `struct hfs_readdir_data` stores list linkage, owning `struct file *`, and last catalog key for an active directory enumeration.

Dependencies and integration:
- Used by `dir.c` and `catalog.c` to adjust open directory iterators when catalog entries are deleted before their current position.

Risk notes:
- The structure is protected by `HFS_I(dir)->open_dir_lock`; callers must preserve that locking discipline.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/hfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/hfs_fs.h -->
# File Research: sources/os/linux/linux/fs/hfs/hfs_fs.h

Purpose: Main classic HFS internal header defining in-core inode/superblock state, flags, helpers, time conversion, and module-wide function prototypes.

Key structures and helpers:
- `struct hfs_inode_info` stores open count, flags, catalog key, resource fork link, extent cache, allocation sizing, physical size, and embedded VFS inode.
- `struct hfs_sb_info` stores MDB buffers, bitmap, catalog/extents trees, counts, mount options, NLS tables, dirty flags, and delayed MDB work.
- `HFS_I()` and `HFS_SB()` convert generic VFS objects to HFS-private data.
- Time helpers convert between Mac epoch timestamps and Linux `timespec64`, using global timezone adjustment.
- `sb_bread512()` reads a 512-byte-sector address through the current block size and returns the sector data pointer.

Dependencies and integration:
- Declares APIs for bitmap, catalog, extents, inode, MDB, partition, string, translation, and superblock code.
- Includes Linux buffer/page/cache, FS, workqueue, NLS-facing support via dependent files.

Risk notes:
- Time conversion intentionally preserves historical HFS/Linux behavior, including global timezone effects.
- Many filesystem counters are stored as atomics in memory but written as 32-bit on-disk values, so overflow checks matter.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/hfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/inode.c -->
# File Research: sources/os/linux/linux/fs/hfs/inode.c

Purpose: Implements classic HFS inode lifecycle, address-space operations, file operations, fork read/write state, resource fork lookup, setattr, fsync, and file attribute reporting.

Key functions:
- `hfs_read_folio()`, `hfs_write_begin()`, `hfs_bmap()`, `hfs_direct_IO()`, and `hfs_writepages()` connect VFS/page-cache I/O to `hfs_get_block()`.
- `hfs_release_folio()` evicts cached B-tree nodes when their pages are released and no node refs remain.
- `hfs_new_inode()` initializes a newly allocated file or directory inode and updates filesystem counts.
- `hfs_delete_inode()` decrements counts and truncates deleted regular files.
- `hfs_inode_read_fork()` and `hfs_inode_write_fork()` translate catalog/MDB fork extents and sizes to in-memory fields.
- `hfs_iget()` uses `iget5_locked()` with catalog record identity checks.
- `hfs_write_inode()` writes updated catalog records, B-tree headers, and fork extents.
- `hfs_file_lookup()` exposes the resource fork through a synthetic `rsrc` child.
- `hfs_inode_setattr()` enforces HFS permission/ownership limitations and handles truncation.
- `hfs_file_fsync()` flushes inode, delayed MDB work, and block device.
- `hfs_fileattr_get()` reports casefold behavior.

Dependencies and integration:
- Uses catalog, extent, MDB, and B-tree helpers throughout.
- Exports `hfs_aops` and `hfs_btree_aops` for regular files and special B-tree files.
- File and inode operation tables are local, while directory operation tables come from `dir.c`.

Risk notes:
- Resource fork inodes are synthetic and share catalog backing with the main inode; lifecycle coupling via `rsrc_inode` must stay balanced.
- `hfs_file_release()` truncates on final close, so allocation cleanup can be deferred.
- Setattr accepts only limited mode changes and fixed mount uid/gid semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/mdb.c -->
# File Research: sources/os/linux/linux/fs/hfs/mdb.c

Purpose: Reads, validates, updates, and releases the classic HFS Master Directory Block, allocation bitmap, alternate MDB, and B-tree roots.

Key functions:
- `hfs_get_last_session()` handles CD-ROM multisession/session mount selection.
- `is_hfs_cnid_counts_valid()` checks next CNID, file count, and folder count fit in 32-bit on-disk fields.
- `hfs_mdb_get()` locates the HFS MDB, optionally via partition map, sets block size, reads volume metadata/bitmap, opens extents/catalog B-trees, and marks unsafe volumes read-only.
- `hfs_mdb_commit()` writes dirty MDB counters, alternate MDB fork metadata, and allocation bitmap changes.
- `hfs_mdb_close()` marks a writable volume cleanly unmounted.
- `hfs_mdb_put()` closes B-trees, releases MDB buffers, unloads NLS tables, and frees the bitmap.

Dependencies and integration:
- Uses `hfs_part_find()`, `hfs_btree_open()`, and `hfs_inode_write_fork()`.
- Dirty flags are set by allocation/catalog/inode code and flushed by `super.c`.

Risk notes:
- Mount is forced read-only if counts overflow, the volume was not cleanly unmounted, or it is marked locked.
- Partial initialization failures rely on caller cleanup through `hfs_mdb_put()`, so null-safe release behavior is important.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/mdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/part_tbl.c -->
# File Research: sources/os/linux/linux/fs/hfs/part_tbl.c

Purpose: Parses old and new Macintosh partition maps to find the selected HFS partition start and size.

Key functions:
- `hfs_part_find()` reads the partition map block, detects old or new signatures, scans entries, and updates `part_start`/`part_size` when a matching HFS partition is found.

Dependencies and integration:
- Uses `sb_bread512()` from `hfs_fs.h`.
- Called by `hfs_mdb_get()` when the raw MDB is not found at the current start sector.
- Honors `HFS_SB(sb)->part` when the user selected a partition number.

Risk notes:
- Old-style support scans a fixed 42-entry table and matches `TFS1`.
- New-style support follows contiguous map blocks and matches `Apple_HFS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/part_tbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/string.c -->
# File Research: sources/os/linux/linux/fs/hfs/string.c

Purpose: Implements classic HFS case-insensitive Macintosh filename hashing, ordering, and dentry comparison.

Key functions:
- `hfs_hash_dentry()` hashes names through the ARDI-derived `caseorder` table and truncates to `HFS_NAMELEN`.
- `hfs_strcmp()` compares two byte strings in Macintosh lexical/casefold order.
- `hfs_compare_dentry()` tests dentry name equality under the same casefold order.

Dependencies and integration:
- Used by catalog key comparison and dentry operations in `sysdep.c`.
- Functions are exported for KUnit under `EXPORT_SYMBOL_IF_KUNIT`.

Risk notes:
- The table is byte-oriented Mac Roman behavior, not Unicode normalization.
- `hfs_compare_dentry()` treats long lookup names through `HFS_NAMELEN` truncation semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/string_test.c -->
# File Research: sources/os/linux/linux/fs/hfs/string_test.c

Purpose: KUnit coverage for HFS filename comparison, hashing, and dentry equality.

Key tests:
- `hfs_strcmp_test()` covers equal strings, unequal strings, length ordering, case-insensitive equality, special characters, and single-character cases.
- `hfs_hash_dentry_test()` verifies hash success, case-insensitive same hashes, and different-name hash differences.
- `hfs_compare_dentry_test()` checks exact, case-insensitive, mismatched, length-mismatched, empty, and name-length-boundary comparisons.

Dependencies and integration:
- Requires KUnit and imports `EXPORTED_FOR_KUNIT_TESTING`.
- Tests exported symbols from `string.c`.

Risk notes:
- These tests assert intended behavior at a high level but do not exhaust the 256-entry Mac case-order table.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/string_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/super.c -->
# File Research: sources/os/linux/linux/fs/hfs/super.c

Purpose: Implements classic HFS filesystem registration, mount context parsing, superblock operations, delayed MDB flushing, root inode setup, and inode cache management.

Key functions:
- `hfs_sync_fs()` validates counters and commits MDB state.
- `hfs_put_super()` cancels delayed work, closes MDB, and releases resources.
- `flush_mdb()` is the delayed work handler for MDB commits.
- `hfs_mark_mdb_dirty()` schedules delayed MDB writeback.
- `hfs_statfs()` reports block/free counts based on allocation blocks.
- `hfs_reconfigure()` handles remount and refuses unsafe read-write transitions.
- `hfs_show_options()` prints non-default mount options.
- `hfs_parse_param()` handles uid/gid/umask/type/creator/partition/session/NLS/quiet options.
- `hfs_fill_super()` initializes HFS state, reads MDB, opens catalog, finds root, sets dentry operations, and creates root dentry.
- Module init/exit create/destroy the HFS inode slab and register/unregister the filesystem.

Dependencies and integration:
- Uses FS context API, `hfs_mdb_get()`, catalog lookup, inode creation, and xattr handlers.
- Sets `SB_NODIRATIME` and `FS_REQUIRES_DEV`.

Risk notes:
- Remount read-write is blocked for unclean or locked volumes.
- Mount option parsing rejects repeated NLS changes and non-4-byte type/creator strings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/sysdep.c -->
# File Research: sources/os/linux/linux/fs/hfs/sysdep.c

Purpose: Defines HFS dentry operations and revalidation behavior.

Key functions:
- `hfs_revalidate_dentry()` rejects RCU lookup, accepts negative dentries, and adjusts cached inode times if the system timezone offset changed.
- `hfs_dentry_operations` wires revalidation, casefold hash, and casefold compare callbacks.

Dependencies and integration:
- Uses `hfs_hash_dentry()` and `hfs_compare_dentry()` from `string.c`.
- Uses `HFS_I(inode)->tz_secondswest` to track per-inode timezone adjustment.

Risk notes:
- Time adjustment depends on global `sys_tz`, preserving legacy HFS local-time semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/sysdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfs/trans.c -->
# File Research: sources/os/linux/linux/fs/hfs/trans.c

Purpose: Converts classic HFS Pascal-style Mac names to Linux names and Linux names back to Mac on-disk names, with optional NLS translation.

Key functions:
- `hfs_mac2asc()` converts `struct hfs_name` to an output byte string, maps `/` to `:`, and optionally translates disk charset to I/O charset.
- `hfs_asc2mac()` converts a Linux `qstr` to an HFS name, maps `:` to `/`, optionally translates I/O charset to disk charset, truncates to `HFS_NAMELEN`, and zero-pads the on-disk name field.

Dependencies and integration:
- Used by catalog key/thread construction and directory enumeration.
- Depends on `HFS_SB(sb)->nls_disk` and `nls_io`.

Risk notes:
- Conversion failures substitute `?` except for output-space exhaustion.
- Returned names are not null-terminated; callers must use explicit lengths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfs/trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/Kconfig -->
# File Research: sources/os/linux/linux/fs/hfsplus/Kconfig

Purpose: Declares kernel configuration options for HFS+ filesystem support and HFS+ KUnit tests.

Key options:
- `HFSPLUS_FS` is a tristate depending on block devices, selecting buffer heads, NLS, UTF-8 NLS, and legacy direct I/O.
- `HFSPLUS_KUNIT_TEST` builds HFS+ KUnit tests when HFS+ and KUnit are enabled, defaulting under `KUNIT_ALL_TESTS`.

Dependencies and integration:
- Controls compilation of the HFS+ object list in `Makefile`.

Risk notes:
- HFS+ support is described as read-write and includes Mac metadata plus Unix-style ownership/permissions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/Makefile -->
# File Research: sources/os/linux/linux/fs/hfsplus/Makefile

Purpose: Defines HFS+ build objects and optional KUnit test object.

Key content:
- Builds `hfsplus.o` from superblock, options, inode, ioctl, extents, catalog, directory, B-tree, Unicode, wrapper, bitmap, partition, attributes, and xattr sources.
- Builds `unicode_test.o` under `CONFIG_HFSPLUS_KUNIT_TEST`.

Dependencies and integration:
- Reflects the HFS+ implementation split; the files in this research group are the B-tree, catalog, directory, extents, bitmap, and attributes core.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/attributes.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/attributes.c

Purpose: Implements HFS+ attributes B-tree support for extended attributes, limited to inline data records.

Key functions:
- `hfsplus_create_attr_tree_cache()` and `hfsplus_destroy_attr_tree_cache()` manage a kmem cache for attribute entries.
- `hfsplus_attr_bin_cmp_key()` sorts attribute keys by CNID and Unicode attribute name.
- `hfsplus_attr_build_key()` converts xattr names to HFS+ Unicode attribute keys.
- `hfsplus_attr_build_record()` creates inline/fork/extents records, but only inline data is meaningfully supported.
- `hfsplus_find_attr()` searches by full key or first record by CNID.
- `hfsplus_attr_exists()` checks whether an attribute exists.
- `hfsplus_create_attr()`, `hfsplus_delete_attr()`, `hfsplus_delete_all_attrs()`, and `hfsplus_replace_attr()` mutate the attributes tree and mark relevant inodes dirty.

Dependencies and integration:
- Uses generic HFS+ B-tree find/record mutation APIs.
- Called by HFS+ xattr handlers and catalog deletion cleanup.
- Marks both the attributes tree inode and owning inode with `HFSPLUS_I_ATTR_DIRTY`.

Risk notes:
- Fork-data and extents attributes return unsupported behavior; Linux HFS+ only stores inline xattr data here.
- `hfsplus_delete_all_attrs()` repeatedly searches first-by-CNID after each deletion, relying on B-tree ordering and mutation stability.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/attributes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/bfind.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/bfind.c

Purpose: Implements HFS+ B-tree search cursor lifecycle, binary record search strategies, leaf traversal, record reading, and typed catalog record validation.

Key functions:
- `hfs_find_init()` allocates search/current key buffers and locks the B-tree mutex using the tree-specific subclass.
- `hfs_find_exit()` releases the current node, frees keys, and unlocks the tree.
- `hfs_find_1st_rec_by_cnid()` finds the first record matching a CNID in extents, catalog, or attributes trees.
- `hfs_find_rec_by_key()` compares full keys using the tree comparator.
- `__hfs_brec_find()` binary-searches one node and populates offsets/lengths.
- `hfs_brec_find()` descends root-to-leaf through index records, validating node height and type.
- `hfs_brec_read()` reads a record by key.
- `hfs_brec_goto()` moves forward/backward across leaf sibling chains.
- `hfsplus_brec_read_cat()` validates catalog record sizes based on type, including variable-length thread records.

Dependencies and integration:
- Shared by attributes, catalog, extents, and directory code.
- Uses `hfs_brec_keylen()`/`hfs_brec_lenoff()` from `brec.c` and B-node I/O from `bnode.c`.

Risk notes:
- `hfs_brec_find()` returns best-fit state even for `-ENOENT`, which insert callers depend on.
- Typed catalog validation is important defense against malformed on-disk records.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/bfind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/bitmap.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/bitmap.c

Purpose: Manages HFS+ allocation-file bitmap bits for block allocation and freeing.

Key functions:
- `hfsplus_block_allocate()` scans allocation bitmap pages from a goal offset, sets a contiguous run up to caller-supplied maximum, decreases `free_blocks`, and marks MDB dirty.
- `hfsplus_block_free()` clears a range of bits, increases `free_blocks`, and marks MDB dirty.

Dependencies and integration:
- Uses `HFSPLUS_SB(sb)->alloc_file->i_mapping` for bitmap pages.
- Called by extent growth/truncation/free paths in `extents.c`.
- Protected by `sbi->alloc_mutex`.

Risk notes:
- Allocation wraps are handled by callers, not inside this function.
- Freeing trusts the requested range after bounds check; it clears bits without verifying they were previously allocated.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/bnode.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/bnode.c

Purpose: Implements HFS+ B-tree node page I/O, intra-node copy/move/clear, node validation/loading, hash-cache management, reference counting, unlinking, and deletion cleanup.

Key functions:
- `hfs_bnode_read()`, `hfs_bnode_write()`, `hfs_bnode_clear()`, `hfs_bnode_copy()`, and `hfs_bnode_move()` operate across one or more page-cache pages with offset/length validation.
- `hfs_bnode_read_key()` reads fixed or variable-length keys, with special handling for attributes tree keys.
- `hfs_bnode_dump()` emits debug information about node headers and offsets.
- `hfs_bnode_unlink()` relinks siblings, updates tree leaf head/tail/root/depth, and marks the node deleted.
- `hfs_bnode_findhash()`, `hfs_bnode_unhash()`, `hfs_bnode_find()`, and `hfs_bnode_create()` maintain the node hash cache and load/create node pages.
- `hfs_bnode_put()` decrements refs, frees deleted nodes, zeroes nodes when required, and returns node IDs to the B-tree bitmap.
- `hfs_bnode_need_zeroout()` checks the volume attribute requesting unused catalog nodes be zeroed.

Dependencies and integration:
- Used by all HFS+ B-tree search and mutation code.
- Relies on validation helpers such as `is_bnode_offset_valid()` and `check_and_correct_requested_length()` from HFS+ headers/common code.
- Interacts with `hfs_bmap_free()` from `btree.c`.

Risk notes:
- Node validation checks type, height, record offsets, entry sizes, and key sizes, reducing malformed-tree exposure.
- Refcount/hash locking correctness is critical because B-tree pages may be reclaimed through address-space operations elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/bnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/brec.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/brec.c

Purpose: Implements HFS+ B-tree record insertion/removal, node splitting, parent-key updates, and root height growth.

Key functions:
- `hfs_brec_lenoff()` and `hfs_brec_keylen()` decode record offsets/lengths and validate HFS+ two-byte key lengths.
- `hfs_brec_insert()` inserts key+entry data, splits full nodes, updates leaf count, and inserts new index records.
- `hfs_brec_remove()` removes records, unlinks empty nodes, and updates parent keys.
- `hfs_bnode_split()` allocates a sibling, chooses a split point, copies records, and updates sibling headers.
- `hfs_brec_update_parent()` adjusts ancestor separator key sizes/content after first-key changes.
- `hfs_btree_inc_height()` creates a new root and indexes the previous root.

Dependencies and integration:
- Mirrors the classic HFS `brec.c` design but uses HFS+ two-byte key lengths and treats the attributes tree as variable-index-key-like.
- Called by catalog, attributes, and extents mutation code.

Risk notes:
- Includes extra protection against oversized record offsets and key lengths.
- Removal does not clear obsolete offset/data bytes as thoroughly as the classic HFS version; correctness relies on `num_recs` and offset table bounds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/brec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/btree.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/btree.c

Purpose: Opens, validates, writes, grows, allocates, and frees HFS+ B-tree nodes for extents, catalog, and attributes trees.

Key functions:
- `hfsplus_calc_btree_clump_size()` computes B-tree clump sizes from volume size, node size, block size, and tree type.
- `hfs_btree_open()` reads tree header data, validates max-key lengths/flags/node counts, selects comparators, and verifies map bit 0.
- `hfs_btree_close()` releases cached nodes and backing inode.
- `hfs_btree_write()` writes updated header counters.
- `hfs_bmap_reserve()` extends the B-tree file to reserve free nodes.
- `hfs_bmap_alloc()` scans header/map node bitmap records, sets a free bit, writes header metadata, and creates the node.
- `hfs_bmap_free()` clears a node allocation bit through validated map-record helpers.

Dependencies and integration:
- Uses `hfsplus_iget()` to load special B-tree inodes.
- Comparator selection depends on HFSX and catalog key type.
- Calls `hfsplus_file_extend()` from `extents.c` and zeroes new catalog nodes when volume attributes require it.

Risk notes:
- If header map bit 0 is invalid, the filesystem is forced read-only and fsck is recommended.
- Uses lockdep assertions to require tree mutex ownership for bitmap reserve/alloc/free.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/catalog.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/catalog.c

Purpose: Implements HFS+ catalog key comparison/building, file/folder/thread record construction, lookup by CNID, create/delete, rename, permissions encoding, and HFSX subfolder count maintenance.

Key functions:
- `hfsplus_cat_case_cmp_key()` and `hfsplus_cat_bin_cmp_key()` compare catalog keys by parent then Unicode name with casefold or binary semantics.
- `hfsplus_cat_build_key()` and `hfsplus_cat_build_key_with_cnid()` build regular and thread keys.
- `hfsplus_cat_set_perms()` serializes Linux inode flags, mode, owner, group, device, and nlink into HFS+ permissions.
- `hfsplus_cat_build_record()` initializes folder/file records, including symlink type/creator and hardlink metadata.
- `hfsplus_fill_cat_thread()` creates variable-length file/folder thread records.
- `hfsplus_find_cat()` resolves a CNID thread record then finds the real catalog record.
- `hfsplus_create_cat()` inserts thread and visible records and updates directory valence/subfolder counts.
- `hfsplus_delete_cat()` removes visible and thread records, frees resource forks, adjusts active readdir positions, deletes xattrs, and marks catalog/dir dirty.
- `hfsplus_rename_cat()` inserts the destination record, removes source record, rewrites the thread record, and updates source/destination metadata.

Dependencies and integration:
- Uses HFS+ Unicode conversion/comparison, B-tree search/mutation, extents fork freeing, and attributes deletion.
- Directory and inode operations call these functions for VFS namespace changes.

Risk notes:
- Data fork freeing remains disabled in catalog delete; resource fork freeing is active.
- Hardlink catalog records use hidden directory conventions that must align with `dir.c` link/unlink logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/catalog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/dir.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/dir.c

Purpose: Provides HFS+ directory VFS operations, including lookup, readdir, hardlinks, unlink/rmdir, symlink, mknod/create/mkdir, rename, and operation tables.

Key functions:
- `hfsplus_lookup()` finds a catalog record, follows HFS+ hardlink indirection through the hidden directory when needed, sets `d_fsdata` to the catalog CNID, and returns the inode.
- `hfsplus_readdir()` emits synthetic `.`/`..`, walks catalog records, converts Unicode names to userspace charset, hides the hidden directory, and records iterator state.
- `hfsplus_link()` creates HFS+ hardlinks by moving the original file into the hidden directory when needed and creating link catalog records.
- `hfsplus_unlink()` removes catalog records, handles open unlinked files by moving to hidden temp names, manages hardlink counts, and deletes hidden backing records when possible.
- `hfsplus_rmdir()` removes empty directories.
- `hfsplus_symlink()` creates symlink inodes, writes symlink contents, creates catalog record, and initializes security xattrs.
- `hfsplus_mknod()` handles regular/special/dir creation with catalog and security initialization.
- `hfsplus_rename()` supports `RENAME_NOREPLACE`, deletes existing destination, renames catalog entries, and writes affected inodes.

Dependencies and integration:
- Uses catalog operations, security/xattr initialization, inode creation/deletion, and `vh_mutex` for volume-header/count-sensitive mutations.
- Exposes `hfsplus_dir_inode_operations` and `hfsplus_dir_operations`.

Risk notes:
- Hardlink behavior is complex and depends on hidden directory state, `d_fsdata`, link IDs, and open-count handling.
- Directory iteration allocates a charset-sized buffer and validates record sizes before emission.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/extents.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/extents.c

Purpose: Implements HFS+ extent overflow handling, block mapping, fork freeing, file allocation growth, optional zeroout for B-tree nodes, and truncation.

Key functions:
- `hfsplus_ext_cmp_key()` compares extent keys by CNID, fork type, and start block.
- `hfsplus_ext_find_block()`, `hfsplus_ext_block_count()`, and `hfsplus_ext_lastblock()` interpret eight-entry HFS+ extent records.
- `hfsplus_ext_write_extent()` flushes dirty cached overflow extents under `extents_lock`.
- `hfsplus_get_block()` maps or allocates a file block, reading overflow extents as needed and marking dirty when cached extents are flushed.
- `hfsplus_free_fork()` frees inline and overflow extent records for a fork.
- `hfsplus_file_extend()` allocates allocation blocks, optionally zeroes them, appends to inline/cached extents, or creates a new overflow extent record.
- `hfsplus_file_truncate()` shrinks allocation, frees blocks, removes overflow records, and updates physical/fs block accounting.

Dependencies and integration:
- Uses allocation bitmap functions from `bitmap.c`.
- Called by inode/page-cache operations and by B-tree growth code.
- Marks allocation file and target inode dirty with HFS+ dirty-bit categories.

Risk notes:
- Extents tree file itself cannot be mapped through overflow extents in `hfsplus_get_block()`.
- Truncation deliberately unlocks the B-tree while freeing allocation bitmap blocks, then relocks with the correct subclass.
- Allocation-file size exhaustion returns ENOSPC rather than extending the allocation file dynamically.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/extents.c -->