# subset-b-005671 Research

Grouped research for the HFS and HFS+ source files listed in work item `subset-b-005671`. Each section preserves the source path in its title and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/brec.c -->
# sources/distributed-fs/ceph-client/fs/hfs/brec.c

Purpose: implements classic HFS B-tree record mutation: record length/key length discovery, insert, remove, node split, parent-key maintenance, and root-height growth. It is the low-level mutator used by catalog and extent trees after `bfind.c` has positioned an `hfs_find_data`.

Important APIs and control flow: `hfs_brec_lenoff()` decodes the trailing record-offset table and returns record span. `hfs_brec_keylen()` handles leaf/index key sizing, including fixed index keys and variable/big-key trees. `hfs_brec_insert()` calculates the aligned key plus payload size, splits the node if the record will not fit, shifts offsets/data, writes key and entry, updates `leaf_count`, then inserts a new index record for split nodes and grows the root with `hfs_btree_inc_height()` when needed. `hfs_brec_remove()` removes the selected record, collapses the payload area and offset table, unlinks empty nodes, and recursively removes parent index records. `hfs_brec_update_parent()` repairs separator keys up the tree when the first key in a child changes.

State and persistence: all structural changes are written through `hfs_bnode_*()` helpers into mapped btree inode pages and mark the relevant pages/inodes dirty. Tree-wide state affected here includes `root`, `depth`, `leaf_head`, `leaf_tail`, and `leaf_count`. New nodes are allocated from the btree bitmap by `hfs_bmap_alloc()`; deleted empty nodes are unlinked and later freed through the bnode lifecycle.

Dependencies and integration: depends on `btree.h`, `hfs_bnode_*`, `__hfs_brec_find()`, and btree bitmap allocation. Catalog operations (`hfs_cat_create/delete/move`) and extent writes (`hfs_ext_write_extent`) rely on this file for all on-disk record updates.

Risks and test signals: node splits and parent-key rewrites are corruption-sensitive. The code has panic-style assumptions for impossible split states and limited rollback after partially successful multi-record catalog operations. Useful tests are fsck-backed create/delete/rename workloads that force leaf and index splits, plus fault injection around `hfs_bmap_alloc()` and bnode read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/brec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/btree.c -->
# sources/distributed-fs/ceph-client/fs/hfs/btree.c

Purpose: opens, validates, writes, reserves, allocates, and frees nodes in classic HFS catalog and extents B-trees. It bridges MDB fork metadata into in-memory `struct hfs_btree` state and manages the tree node allocation bitmap.

Important APIs and control flow: `hfs_btree_open()` allocates `struct hfs_btree`, creates/loads the special btree inode for `HFS_EXT_CNID` or `HFS_CAT_CNID`, reads the header node from disk, validates power-of-two node size, node count, and max key length, then configures node geometry. `hfs_btree_close()` releases cached bnodes and the btree inode. `hfs_btree_write()` writes mutable header fields (`root`, leaf links/count, node/free counts, attributes, depth) to node 0. `hfs_bmap_reserve()` extends the btree file by calling `hfs_extend_file()` until enough free nodes exist. `hfs_bmap_alloc()` scans header/map-node bitmap records for a clear bit, sets it, decrements `free_nodes`, and creates the corresponding bnode. `hfs_bmap_free()` clears the bit and increments `free_nodes`.

State and persistence: this file persists btree header records, btree bitmap bits, btree inode size/bytes, and dirty inode state. Growing a btree updates the special btree inode's allocated block counts and `tree->node_count`. Bitmap changes dirty individual pages and the btree inode so writeback can flush them.

Dependencies and integration: depends on `hfs_inode_read_fork()`, `hfs_ext_find_block()`, `hfs_extend_file()`, bnode cache helpers, and the MDB fields loaded by `mdb.c`. It is used by `brec.c` for node allocation and by mount setup for opening catalog/extents trees.

Risks and test signals: header reading manually copies block data into folio 0, so block-size and offset mistakes can corrupt all later tree parsing. Bitmap map-node growth has a `panic("FIXME!!!")` when no free nodes remain in one path. Tests should mount crafted images with bad max key lengths, non-power-of-two node sizes, full btree maps, and forced catalog/extents growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/btree.h -->
# sources/distributed-fs/ceph-client/fs/hfs/btree.h

Purpose: declares the classic HFS in-memory btree model and the shared btree/bnode/search APIs used across catalog, extent, inode, and mount code.

Important types and APIs: `btree_keycmp` abstracts key ordering for catalog versus extents. `struct hfs_btree` stores superblock, backing inode, comparator, CNID, root/leaf topology, node/free counts, attributes, node size geometry, a tree mutex, and a hash table of cached bnodes. `struct hfs_bnode` stores sibling/parent links, node id, type, height, reference count, flags, page offset, and backing pages. `struct hfs_find_data` carries search and found keys, current node, record index, and key/entry offsets/lengths. The header declares btree open/write/reserve/allocation helpers, bnode read/write/move/cache helpers, record insert/remove helpers, and find/goto/read helpers.

State and persistence: the header itself has no persistence behavior, but its fields mirror persistent btree headers, node descriptors, record offset tables, and btree bitmap records. The `tree_lock` is the main serialization point for btree searches and mutations. `HFS_BNODE_NEW`, `HFS_BNODE_DELETED`, and `HFS_BNODE_ERROR` coordinate cache lifecycle and delayed node freeing.

Dependencies and integration: includes `hfs_fs.h`, which supplies HFS on-disk structures, superblock/inode state, and conversion macros. It is the contract between `btree.c`, `bnode.c`, `bfind.c`, `brec.c`, `catalog.c`, and `extent.c`.

Risks and test signals: incorrect assumptions about `max_key_len`, `node_size_shift`, or record offsets affect all users. Static analysis should verify callers hold the tree mutex around find/mutate sequences and release `hfs_find_data` through `hfs_find_exit()`. Runtime tests should stress bnode cache release under memory pressure and concurrent directory operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/catalog.c -->
# sources/distributed-fs/ceph-client/fs/hfs/catalog.c

Purpose: implements classic HFS catalog B-tree key construction, record/thread creation, lookup-by-CNID, create/delete/move operations, and next-CNID correction after deletion.

Important APIs and control flow: `hfs_cat_build_key()` creates parent/name or CNID/thread keys after converting Linux names to Mac names. `hfs_cat_build_record()` builds file/folder records, while `hfs_cat_build_thread()` creates thread records used to resolve CNID to parent/name. `hfs_cat_create()` reserves btree nodes, inserts the thread record keyed by CNID, inserts the visible directory record keyed by parent/name, and rolls back the thread if visible insertion fails. `hfs_cat_find_brec()` reads a thread record and then searches for the visible record. `hfs_cat_delete()` removes the visible record, frees the resource fork for files, adjusts active readdir positions, removes the thread, decrements directory size, and corrects `next_id`. `hfs_cat_move()` copies the old visible record to a new parent/name, removes the old record, and rebuilds the thread.

State and persistence: catalog records, thread records, directory valence (`i_size`), root/file/folder counters indirectly, and `next_id` are modified. Updates dirty directory inodes and btree pages. CNID counts live in `hfs_sb_info` atomics and are eventually flushed to the MDB.

Dependencies and integration: uses `btree.h` search/mutation primitives, `hfs_asc2mac()`/`hfs_strcmp()` name handling, `hfs_free_fork()` extent cleanup, and open-directory state from `hfs.h`. VFS directory operations in `dir.c` are thin wrappers around these APIs.

Risks and test signals: multi-record catalog updates are not transactional, so interrupted rename/create/delete can leave orphaned thread or visible records. `hfs_correct_next_unused_CNID()` scans leaf nodes backward and depends on valid bnode offsets. Tests should cover create rollback, delete of files with resource forks, rename across directories, CNID wrap/corruption handling, and active `readdir()` during deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/catalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/hfs/dir.c

Purpose: provides VFS directory operations for classic HFS: lookup, iteration, create, mkdir, unlink/rmdir, rename, and release cleanup for active directory reads.

Important APIs and control flow: `hfs_lookup()` searches the catalog by parent/name and instantiates the inode with `hfs_iget()`. `hfs_readdir()` emits synthetic `.` and `..`, then walks catalog leaf records using `hfs_brec_goto()`, converts Mac names to Linux names, emits directory/file entries, and saves the last key in `file->private_data` when the caller stops mid-stream. `hfs_dir_release()` removes that saved readdir state. `hfs_create()` and `hfs_mkdir()` allocate a new inode and insert catalog records, cleaning up the inode on failure. `hfs_remove()` handles both unlink and rmdir, rejects nonempty directories, validates CNID counters, deletes catalog records, clears nlink, and invokes inode deletion. `hfs_rename()` implements only normal and `RENAME_NOREPLACE`, removes an existing destination first, then calls `hfs_cat_move()`.

State and persistence: directory size is catalog valence plus synthetic entries. New and removed entries update catalog tree pages, inode link counts, inode timestamps, and MDB counters via inode/catalog helpers. Active readdir cursors are linked in `HFS_I(dir)->open_dir_list` and adjusted during deletion to avoid skipped or duplicated entries.

Dependencies and integration: integrates VFS `file_operations`/`inode_operations` with `catalog.c`, `inode.c`, `string.c`, and `trans.c`. Dentry hashing/comparison is installed by `super.c`.

Risks and test signals: destination removal before rename means failures after removal are visible to users. Directory iteration trusts catalog ordering and parent checks to detect corruption. Tests should cover interrupted readdir with concurrent unlink, nonempty rmdir, rename replacement, oversized names, and CNID count read-only/corruption paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/extent.c -->
# sources/distributed-fs/ceph-client/fs/hfs/extent.c

Purpose: manages classic HFS file extent mapping, extent overflow tree records, allocation bitmap interactions, block mapping, file growth, fork freeing, and truncation.

Important APIs and control flow: `hfs_ext_keycmp()` orders extent records by file id, fork type, and allocation block. `hfs_ext_find_block()` maps a logical allocation-block offset through the three extents in a record. `hfs_ext_write_extent()` flushes cached dirty/new overflow extents to the extents tree. `hfs_ext_read_extent()` fills the inode's cached overflow extent record if a block is outside the first extents. `hfs_get_block()` maps VFS block numbers to disk sectors, optionally extending the file by one allocation clump. `hfs_extend_file()` chooses an allocation goal from the last extent, searches/marks the volume bitmap, appends to first or cached extents when possible, or creates a new overflow record. `hfs_free_fork()` and `hfs_file_truncate()` release allocation blocks and remove obsolete overflow records.

State and persistence: mutates `HFS_I(inode)` extent fields (`first_extents`, `cached_extents`, block counts, dirty/new flags), volume bitmap bits, free block counts, file physical/logical sizes, inode bytes, and MDB dirty flags. Btree overflow extent records are persisted through `brec.c`; bitmap and MDB fields flush through `mdb.c`.

Dependencies and integration: depends on `hfs_vbm_search_free()`/`hfs_clear_vbm_bits()`, btree find/record helpers, `hfs_write_begin()`, and inode writeback. It services all page cache and direct I/O block mapping via `hfs_aops`.

Risks and test signals: HFS uses 16-bit allocation-block indexes here, making overflow/corruption checks important. Truncate has comments noting limited error handling. Tests should force extents beyond the first three, noncontiguous allocation, ENOSPC during extension, partial truncate across first and overflow extents, and resource fork cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/extent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/hfs.h -->
# sources/distributed-fs/ceph-client/fs/hfs/hfs.h

Purpose: small classic HFS private header that includes common HFS on-disk definitions and declares `struct hfs_readdir_data`, the per-open-directory cursor state used to keep directory iteration coherent during catalog mutations.

Important types and APIs: `struct hfs_readdir_data` stores a list node, owning `struct file *`, and the last catalog key seen by `readdir()`. It has no functions of its own; it is allocated in `hfs_readdir()`, linked under `HFS_I(dir)->open_dir_lock`, consulted in `hfs_cat_delete()` to decrement `f_pos` for affected readers, and freed in `hfs_dir_release()`.

State and persistence: the structure is in-memory only. It does not persist to disk, but it protects the user-visible stream position while persistent catalog records are removed from the underlying B-tree.

Dependencies and integration: includes `<linux/hfs_common.h>` for shared HFS/HFS+ raw definitions such as catalog keys and constants. It is included by `hfs_fs.h`, making the readdir state available to directory and catalog code.

Risks and test signals: because the state stores a catalog key copied from a mutable B-tree position, correctness depends on catalog comparator stability and locking between directory iteration and deletion. Tests should run `readdir()` while deleting and renaming entries in the same directory and validate no stale list entries remain after file release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/hfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/hfs_fs.h -->
# sources/distributed-fs/ceph-client/fs/hfs/hfs_fs.h

Purpose: central private header for classic HFS. It defines HFS-specific inode and superblock state, dirty flags, helper macros, timestamp conversions, the 512-byte read macro, and cross-file function prototypes.

Important types and APIs: `struct hfs_inode_info` extends VFS inodes with open count, flags, catalog key, resource-fork inode linkage, extent lock, first/cached extents, allocation/physical sizes, and open-directory cursor list. `struct hfs_sb_info` stores MDB buffers, primary/alternate MDB pointers, in-memory volume bitmap, catalog/extents trees, atomic file/folder/CNID counters, allocation geometry, mount options, NLS tables, bitmap lock, delayed MDB work, and dirty flags. Mac/Unix timestamp conversion helpers apply the HFS 1904 epoch and system timezone behavior. `HFS_I()` and `HFS_SB()` are the main accessors used throughout the filesystem.

State and persistence: header fields mirror the MDB, volume bitmap, catalog records, extent records, and btree fork metadata. Dirty flags `HFS_FLG_BITMAP_DIRTY`, `HFS_FLG_MDB_DIRTY`, and `HFS_FLG_ALT_MDB_DIRTY` coordinate delayed and sync-time persistence. Inode flags track resource forks and cached overflow extents.

Dependencies and integration: includes Linux VFS, buffer, mutex, workqueue, endian, and uaccess headers plus `hfs.h`. It declares APIs from bitmap, catalog, extent, inode, MDB, partition, string, translation, xattr, and super modules.

Risks and test signals: this header encodes global invariants: counter widths must stay within `u32`, allocation block geometry must match MDB values, and timestamp conversions depend on global timezone. Tests should exercise remount/sync dirty flags, timezone dentry revalidation, resource forks, and special CNID inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/hfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/hfs/inode.c

Purpose: implements classic HFS inode lifecycle, file address-space operations, fork metadata import/export, inode writeback to catalog records, resource-fork pseudo-directory lookup, file open/release, setattr, and fsync.

Important APIs and control flow: `hfs_aops` and `hfs_btree_aops` wire page cache operations to `hfs_get_block()`, with btree folio release checking cached bnode references. `hfs_write_begin()` uses `cont_write_begin()` and truncates failed extension writes. `hfs_new_inode()` allocates CNIDs, initializes mode/owner/timestamps, updates file/folder/root counts, and marks MDB dirty. `hfs_delete_inode()` decrements counters and truncates unlinked regular files. `hfs_inode_read_fork()` and `hfs_inode_write_fork()` translate catalog/MDB fork fields into in-memory extent state and back. `hfs_iget()` uses `iget5_locked()` with catalog records. `hfs_write_inode()` flushes dirty extents, special btree headers, or catalog file/folder records. `hfs_file_lookup()` exposes a file's resource fork under a synthetic `rsrc` child. `hfs_inode_setattr()` restricts uid/gid/mode changes to HFS-supported semantics and truncates on size changes. `hfs_file_fsync()` writes inode/catalog state, flushes delayed MDB work, then syncs the block device.

State and persistence: inode writeback updates catalog records for times, directory valence, file lock bit, and fork extents/sizes. Special extents/catalog btree inodes update btree headers. Resource-fork inodes share the main catalog record and hold cross references.

Dependencies and integration: integrates VFS address-space/file/inode operations with `extent.c`, `catalog.c`, `mdb.c`, `super.c`, and xattr listing. It depends on Linux page cache, direct I/O, mpage writeback, and credential APIs.

Risks and test signals: resource fork handling uses fake hashed inodes and shared catalog state. Counter updates occur before catalog insertion can fail, relying on cleanup paths. Tests should cover resource fork reads/writes, direct I/O extension failure, writeback of btree inodes, mode mapping, truncate-on-last-close, and fsync persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/mdb.c -->
# sources/distributed-fs/ceph-client/fs/hfs/mdb.c

Purpose: reads, validates, updates, and releases the classic HFS Master Directory Block (MDB), alternate MDB, volume bitmap, catalog tree, and extents tree.

Important APIs and control flow: `hfs_get_last_session()` chooses a CD-ROM/session starting sector or whole-device default. `is_hfs_cnid_counts_valid()` checks `next_id`, file count, and folder count against `U32_MAX`. `hfs_mdb_get()` sets block size, locates the HFS MDB directly or via partition map, validates allocation block size, loads geometry/counters/root counts, optionally loads alternate MDB, reads the volume bitmap into memory, opens extents and catalog btrees, and marks writable mounts as unclean/inconsistent. `hfs_mdb_commit()` writes dirty MDB counters/times, writes alternate MDB after special btree fork growth, and flushes dirty bitmap bytes back to disk. `hfs_mdb_close()` marks the volume clean on unmount, and `hfs_mdb_put()` closes btrees, releases buffers, unloads NLS tables, and frees the bitmap.

State and persistence: owns primary and alternate MDB buffer_heads, `hfs_sb_info` geometry/counters/free blocks, in-memory volume bitmap, unmount/lock/inconsistent attributes, write count, and btree handles. Dirty flags control which portions are copied back.

Dependencies and integration: depends on block-device helpers, CD-ROM multisession APIs, partition parsing in `part_tbl.c`, btree open/close, and fork write helpers. `super.c` calls these from mount, sync, delayed work, and unmount paths.

Risks and test signals: mount can continue read-only after suspicious counters or unclean/locked attributes. Bitmap allocation is fixed-size 8192 bytes, matching classic HFS limits. Tests should use images with partition maps, alternate MDB missing, unclean flags, corrupt counters, unusual block sizes, dirty bitmap writes, and read-only remounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/mdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/part_tbl.c -->
# sources/distributed-fs/ceph-client/fs/hfs/part_tbl.c

Purpose: parses old and new Macintosh partition maps to locate the selected HFS partition when the MDB is not found at the current device/session offset.

Important APIs and control flow: `struct new_pmap` models an Apple partition map entry with signature, map count, physical start/count, name, and type. `struct old_pmap` models the older fixed array of 42 entries. `hfs_part_find()` reads the first partition-map block with `sb_bread512()`, switches on old (`HFS_OLD_PMAP_MAGIC`) or new (`HFS_NEW_PMAP_MAGIC`) signatures, scans entries for HFS/TFS1 or `Apple_HFS`, applies the mount option selected partition index when present, and updates `part_start`/`part_size`.

State and persistence: this file is read-only. It mutates only caller-owned sector offsets used by `hfs_mdb_get()` to reread the MDB and compute filesystem geometry.

Dependencies and integration: depends on `hfs_fs.h` constants and `HFS_SB(sb)->part`. It is called from `mdb.c` during mount discovery after an initial direct MDB check fails.

Risks and test signals: old-map parsing can return the last matching entry rather than breaking, while new-map parsing stops at the first match. The code assumes 512-byte partition-map blocks and limited structural validation. Tests should cover explicit `part=` selection, invalid signatures, truncated maps, multiple HFS entries, and loop/CD images with both direct and partitioned layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/part_tbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/string.c -->
# sources/distributed-fs/ceph-client/fs/hfs/string.c

Purpose: implements classic HFS filename hashing and comparison using Macintosh lexical case ordering.

Important APIs and control flow: the file-local `caseorder[256]` table folds case and imposes Mac ordering. `hfs_hash_dentry()` caps names at `HFS_NAMELEN`, hashes each byte through `caseorder`, and stores the dentry hash. `hfs_strcmp()` compares two Mac-encoded names byte-by-byte through `caseorder`, returning the ordering difference or length difference. `hfs_compare_dentry()` implements dcache equality, enforcing HFS name length behavior and comparing folded bytes. The functions are exported for KUnit visibility.

State and persistence: no on-disk state is written. The comparison order determines catalog B-tree key ordering and dentry cache behavior, so it indirectly controls persistent catalog record placement and lookup correctness.

Dependencies and integration: used by `hfs_cat_keycmp()` and installed as dentry operations through `hfs_dentry_operations` in `sysdep.c`. Name conversion to/from disk encoding is handled separately in `trans.c`.

Risks and test signals: any mismatch between hashing and comparison can cause negative dentry aliasing or lookup misses. Truncation at `HFS_NAMELEN` is a compatibility edge. Tests should include case-equivalent names, punctuation/space ordering, high-bit Mac characters, exactly/over-limit lengths, and catalog lookup order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/string_test.c -->
# sources/distributed-fs/ceph-client/fs/hfs/string_test.c

Purpose: KUnit coverage for classic HFS string comparison, dentry hashing, and dentry comparison.

Important APIs and control flow: `hfs_strcmp_test()` checks equality, inequality, length ordering, case-insensitive behavior, special filename strings, and one-character boundaries. `hfs_hash_dentry_test()` builds three `qstr` values, hashes them, expects case variants to hash equally, and expects a different name to hash differently. `hfs_compare_dentry_test()` checks exact, case-insensitive, different-name, different-length, empty-string, and `HFS_NAMELEN` boundary comparisons. The suite is registered as `hfs_string` and imports the KUnit export namespace.

State and persistence: no filesystem state is persisted. The tests exercise pure functions that affect dentry-cache lookup and catalog key comparison.

Dependencies and integration: depends on KUnit, `linux/dcache.h`, and exported symbols from `string.c` via `EXPORT_SYMBOL_IF_KUNIT`. Build integration depends on the corresponding kernel config/Makefile entries outside this file.

Risks and test signals: the tests are valuable smoke coverage but mostly ASCII-focused; they do not exhaust the Mac `caseorder` table, high-bit characters, or all punctuation ordering that the catalog tree relies on. Additional tests should assert hash/compare consistency for overlong names and Mac-encoded bytes above 0x7f.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/string_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/super.c -->
# sources/distributed-fs/ceph-client/fs/hfs/super.c

Purpose: implements classic HFS filesystem registration, mount context/options, superblock operations, delayed MDB flushing, statfs, remount validation, and inode cache lifecycle.

Important APIs and control flow: `hfs_sync_fs()` validates CNID counters and commits the MDB. `hfs_put_super()` cancels delayed work, marks the MDB clean, and releases MDB resources. `flush_mdb()` is delayed work that clears `work_queued` and commits dirty MDB/bitmap state. `hfs_mark_mdb_dirty()` schedules that work for writable mounts. `hfs_statfs()` reports block/free counts derived from allocation blocks and `fs_div`. `hfs_parse_param()` handles uid/gid, umasks, partition/session, creator/type, quiet, codepage, and iocharset. `hfs_fill_super()` initializes defaults/locks, calls `hfs_mdb_get()`, reads the root catalog record, instantiates root inode/dentry, and installs dentry ops. Module init creates the inode slab and registers `hfs`; exit unregisters and destroys the slab.

State and persistence: superblock fields, mount options, inode cache, delayed MDB work state, dirty MDB commits, and root dentry setup are managed here. Remount to read-write is refused if the MDB is not clean or is locked.

Dependencies and integration: integrates with Linux `fs_context`, block-device mount helpers, NLS, VFS super operations, `mdb.c`, `catalog.c`, `inode.c`, xattr handlers, and dentry operations.

Risks and test signals: mount failure paths call `hfs_mdb_put()` even after partial setup, so resource initialization order matters. Delayed MDB work is a persistence window. Tests should cover mount option parsing, failed NLS loads, read-only remount rules, statfs values, delayed dirty commit, and unmount after partial mount failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/sysdep.c -->
# sources/distributed-fs/ceph-client/fs/hfs/sysdep.c

Purpose: provides HFS dentry operations and timezone revalidation behavior needed because classic HFS timestamps are stored relative to local-time conventions.

Important APIs and control flow: `hfs_revalidate_dentry()` rejects RCU lookup with `-ECHILD`, returns valid for negative dentries, and for positive dentries adjusts ctime/atime/mtime by the difference between current `sys_tz.tz_minuteswest` and the inode's stored `tz_secondswest`. `hfs_dentry_operations` wires this revalidator together with `hfs_hash_dentry()` and `hfs_compare_dentry()`.

State and persistence: only in-memory inode timestamps and `HFS_I(inode)->tz_secondswest` are adjusted during dentry revalidation. No disk write is performed directly, but adjusted times could later be written through inode writeback if the inode becomes dirty through other paths.

Dependencies and integration: depends on Linux namei/dcache APIs and `hfs_fs.h`. `super.c` installs `hfs_dentry_operations` as default dentry operations after mounting the root.

Risks and test signals: global timezone changes can shift visible timestamps during lookup, and RCU walk fallback is required. Tests should simulate timezone changes, verify repeated revalidation does not double-adjust, and cover hash/compare consistency under dcache lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/sysdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/trans.c -->
# sources/distributed-fs/ceph-client/fs/hfs/trans.c

Purpose: converts names between Linux-visible byte strings and classic HFS Mac-encoded Pascal strings, including the HFS path separator rule.

Important APIs and control flow: `hfs_mac2asc()` converts an on-disk `struct hfs_name` to a Linux filename buffer, capping source length at `HFS_NAMELEN`, using optional disk and I/O NLS tables when configured, replacing on-disk `/` with Linux-visible `:`, and returning the produced byte length. `hfs_asc2mac()` converts a Linux `qstr` into an on-disk HFS name, optionally translating through NLS tables, replacing Linux-visible `:` with on-disk `/`, truncating to `HFS_NAMELEN`, storing the Pascal length, and zero-filling the remaining name bytes.

State and persistence: the conversion itself is pure with respect to global filesystem state, but its output is persisted in catalog keys and thread records. NLS table choices from mount options determine the byte representation on disk.

Dependencies and integration: used by catalog key/thread construction and directory iteration. Depends on `HFS_SB(sb)->nls_disk` and `nls_io`, and Linux NLS conversion callbacks.

Risks and test signals: conversion failures substitute `?` except for name-too-long termination paths, so distinct Unicode names can collide. Separator mapping is compatibility-sensitive. Tests should include NLS-enabled mounts, invalid byte sequences, names containing `:` and `/`, max-length truncation, and round-trip uniqueness assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfs/trans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/Kconfig -->
# sources/distributed-fs/ceph-client/fs/hfsplus/Kconfig

Purpose: declares kernel configuration options for the HFS+ filesystem and its KUnit tests.

Important options: `HFSPLUS_FS` is a tristate block filesystem option for Apple Extended HFS support. It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, `NLS_UTF8`, and `LEGACY_DIRECT_IO`, matching the implementation's use of block buffers, charset conversion, UTF-8 handling, and direct I/O helpers. Help text documents HFS+ as MacOS 8-era extended HFS with data forks, creator codes, ownership, and permissions. `HFSPLUS_KUNIT_TEST` builds HFS+ KUnit tests when `HFSPLUS_FS` and `KUNIT` are enabled, defaulting under `KUNIT_ALL_TESTS`.

State and persistence: no runtime state is managed here. The selected config controls whether the HFS+ module and tests are built into the kernel or as modules.

Dependencies and integration: paired with `Makefile`, which builds `hfsplus.o` from the implementation files and `unicode_test.o` for test config. The selected dependencies correspond to headers and APIs used by files in this subset, especially `bitmap.c`, `inode.c`, `unicode.c`, and the btree code.

Risks and test signals: missing selected dependencies would surface as build failures. Config tests should verify `HFSPLUS_FS=m/y` builds the full object list and `HFSPLUS_KUNIT_TEST` pulls in only test code when KUnit is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/Makefile -->
# sources/distributed-fs/ceph-client/fs/hfsplus/Makefile

Purpose: defines the build composition for the HFS+ filesystem object and HFS+ KUnit test object.

Important build rules: `obj-$(CONFIG_HFSPLUS_FS) += hfsplus.o` makes the filesystem build conditional on the config option. `hfsplus-objs` aggregates the module from super/options/inode/ioctl/extents/catalog/dir/btree/bnode/brec/bfind/tables/unicode/wrapper/bitmap/part_tbl/attributes/xattr and xattr namespace handlers. `obj-$(CONFIG_HFSPLUS_KUNIT_TEST) += unicode_test.o` builds tests separately.

State and persistence: no runtime state. The object list determines which source files are linked into the filesystem implementation and therefore which APIs are available across translation units.

Dependencies and integration: this subset covers many of the listed core objects: attributes, bfind, bitmap, bnode, brec, btree, catalog, dir, and extents. Other linked files provide superblock setup, options, raw definitions, Unicode conversion, wrapper/MDB handling, inode writeback, ioctl, and xattr glue.

Risks and test signals: build ordering is not explicit, so missing prototypes or config guards show up at compile/link time. Since `attributes.o` and xattr handlers are always included with HFS+, attribute-tree absence must be handled at runtime, as `attributes.c` does. Build tests should cover builtin, module, and KUnit-enabled variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/attributes.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/attributes.c

Purpose: implements HFS+ attribute-tree support for extended attributes, limited to inline data records. It handles key creation, lookup, existence checks, create, delete, delete-all, and replace.

Important APIs and control flow: `hfsplus_create_attr_tree_cache()`/`destroy` manage a slab cache for temporary `hfsplus_attr_entry` records. `hfsplus_attr_bin_cmp_key()` orders attributes by CNID then Unicode attribute name. `hfsplus_attr_build_key()` converts xattr names to HFS+ Unicode xattr keys and computes variable key length. `hfsplus_attr_build_record()` supports `HFSPLUS_ATTR_INLINE_DATA`, rejects oversized inline values with `-E2BIG`, and treats fork/extents records as unsupported placeholders. `hfsplus_find_attr()` searches either an exact name or first record for a CNID. `hfsplus_create_attr()` reserves btree space and inserts an inline record. `__hfsplus_delete_attr()` validates CNID and record type before removal. `hfsplus_delete_all_attrs()` loops over first-by-CNID records. `hfsplus_replace_attr()` deletes then recreates.

State and persistence: mutates the attributes btree and marks both the attributes-tree inode and target inode with `HFSPLUS_I_ATTR_DIRTY`. Attribute data is persisted inline in btree leaf records; non-inline attribute forks are not supported.

Dependencies and integration: uses HFS+ btree search/mutation helpers, Unicode conversion, xattr constants from `xattr.h`, and raw HFS+ attribute structures. VFS xattr handlers call these helpers indirectly.

Risks and test signals: replace is delete-then-create without transaction rollback. Delete-all relies on repeated first-by-CNID searches after each removal. Tests should cover absent attribute tree, exact and first-by-CNID lookup, max inline data size, unsupported fork/extents records, replace failure after delete, and Unicode xattr names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/bfind.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/bfind.c

Purpose: implements HFS+ btree search cursors, binary search strategies, record reads, record-relative movement, and catalog record size validation.

Important APIs and control flow: `hfs_find_init()` allocates paired search/current key buffers sized from `tree->max_key_len`, records the tree, and locks the tree mutex with a tree-specific lock class. `hfs_find_exit()` drops the current bnode, frees keys, and unlocks. `hfs_find_1st_rec_by_cnid()` is a strategy for locating the first record with a matching CNID in extents, catalog, or attributes trees. `hfs_find_rec_by_key()` is exact comparator-based search. `__hfs_brec_find()` performs binary search within one bnode and fills offsets/lengths. `hfs_brec_find()` traverses root-to-leaf through index records, validating node type/height. `hfs_brec_read()` combines find and payload copy. `hfs_brec_goto()` moves forward/backward across linked leaf nodes. `hfsplus_brec_read_cat()` reads a catalog entry and validates exact record size based on type, including variable thread size.

State and persistence: no direct writes. It establishes in-memory cursor state used by mutators and readers. The tree mutex serializes concurrent operations while a cursor is active.

Dependencies and integration: depends on bnode read helpers, tree comparators configured by `btree.c`, and HFS+ raw catalog structures. Catalog, extents, attributes, directory, and inode code all build keys then use this search layer.

Risks and test signals: bad key lengths or malformed record offsets propagate as `-EINVAL`/`-EIO`; caller cleanup must always invoke `hfs_find_exit()`. Tests should cover malformed catalog thread sizes, movement across leaf boundaries, first-by-CNID searches with multiple attrs, and invalid index height/type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/bfind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/bitmap.c

Purpose: manages the HFS+ allocation bitmap stored in the allocation file, allocating and freeing allocation blocks.

Important APIs and control flow: `hfsplus_block_allocate()` locks `alloc_mutex`, reads bitmap pages from `sbi->alloc_file`, scans from an offset for the first zero bit, sets contiguous zero bits up to `*max`, handles page boundaries, dirties modified pages, subtracts allocated count from `free_blocks`, marks the MDB dirty, and returns the starting block or `size` when full/error. `hfsplus_block_free()` validates range, locks the bitmap, clears the requested bit range across pages, dirties pages, adds the count back to `free_blocks`, and marks the MDB dirty.

State and persistence: mutates allocation file pages, `HFSPLUS_SB(sb)->free_blocks`, and MDB dirty state. The bitmap is page-cache backed rather than an in-memory fixed array, so normal file writeback persists allocation changes.

Dependencies and integration: called by `extents.c` for file/fork growth and truncation/freeing. Depends on `read_mapping_page()`, page mapping/dirtying, allocation-file inode setup from mount code, and `hfsplus_mark_mdb_dirty()`.

Risks and test signals: allocation returns `size` on some read errors, which callers interpret like no space. Freeing does not verify bits were set before clearing, so double-free detection is weak at this layer. Tests should exercise partial-word start/end ranges, page-boundary allocations/frees, wraparound allocation fallback, ENOSPC, and corrupted/short allocation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/bnode.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/bnode.c

Purpose: provides HFS+ btree node cache management and byte-level operations for reading, writing, clearing, copying, moving, validating, unlinking, creating, and freeing bnodes.

Important APIs and control flow: `hfs_bnode_read/write/clear/copy/move()` operate across one or more pages, using shared bounds helpers (`is_bnode_offset_valid()`, `check_and_correct_requested_length()`) and dirtying changed pages. `hfs_bnode_read_key()` derives key length from node/tree attributes, with special handling for the attributes tree. `hfs_bnode_unlink()` updates sibling descriptors, adjusts leaf head/tail or root/depth, and marks a node deleted. `hfs_bnode_findhash()`, `__hfs_bnode_create()`, `hfs_bnode_find()`, and `hfs_bnode_create()` implement a hashed bnode cache with `HFS_BNODE_NEW` wait coordination and structural validation of descriptor type/height and record offset table. `hfs_bnode_put()` frees deleted nodes after last reference, optionally zeroing unused nodes. `hfs_bnode_need_zeroout()` checks the volume unused-node-fix attribute.

State and persistence: writes directly to btree inode pages, marks pages dirty, updates sibling/root/leaf metadata, and frees node bitmap bits through `hfs_bmap_free()`. Cached bnodes are in-memory but backed by page-cache pages.

Dependencies and integration: used by all HFS+ btree search and mutation files. Relies on HFS+ raw node descriptors, page cache, hash locking, and volume attributes.

Risks and test signals: bounds checks mitigate malformed images, but truncated reads can still alter caller behavior. Node cache reference correctness is critical under memory pressure. Tests should cover malformed record offsets, deleted node lifetime, zeroout-enabled frees, multi-page nodes, and concurrent lookup of the same new bnode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/bnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/brec.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/brec.c

Purpose: mutates individual HFS+ btree records: insert, remove, split, parent separator update, and height increase. It is the HFS+ counterpart to classic HFS `brec.c` with 16-bit key lengths and attribute-tree handling.

Important APIs and control flow: `hfs_brec_lenoff()` decodes record offsets. `hfs_brec_keylen()` validates record offset and key length against `tree->max_key_len`, using fixed index keys only when variable index keys are absent and the tree is not the attributes tree. `hfs_brec_insert()` inserts into the current leaf or creates a root if empty, splits full nodes, shifts offset/data regions, writes key/payload, increments leaf count, and recursively inserts index records for split nodes. `hfs_brec_remove()` removes records, unlinks empty nodes, recurses into parent records, and updates parent keys for first-record removals. `hfs_bnode_split()` splits approximately half the node into a newly allocated bnode, updates sibling descriptors and leaf tail. `hfs_brec_update_parent()` propagates new separator keys upward, splitting index nodes if needed. `hfs_btree_inc_height()` creates a new root and inserts the old root pointer.

State and persistence: changes btree page data, node descriptors, record offset tables, tree root/depth/leaf count, node links, and dirty state for the btree inode. New nodes come from the btree map; deleted nodes are flagged through bnode unlink.

Dependencies and integration: used by catalog, extents, and attributes code for all persistent btree record mutations. It depends on `bfind.c` strategies, `btree.c` node allocation, and bnode byte helpers.

Risks and test signals: split math is sensitive to descriptor size, record offset table size, and variable key lengths. Tests should force catalog, extents, and attributes splits; root growth; deletion to empty tree; attribute-tree fixed/variable index behavior; and malformed key length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/brec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/btree.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/btree.c

Purpose: opens, validates, writes, grows, allocates, and frees nodes for HFS+ extents, catalog, and attributes B-trees.

Important APIs and control flow: `hfsplus_calc_btree_clump_size()` derives clump sizes from volume size and tree type using Apple's table-derived heuristics. `hfs_btree_open()` loads the special file inode, reads header node 0, validates max key length/flags/node size/count, assigns the proper comparator, detects HFSX binary versus casefold catalog behavior, initializes geometry, and verifies bit 0 in the btree map, forcing read-only if corrupted. `hfs_btree_write()` persists mutable header fields. `hfs_bmap_reserve()` extends the btree file using `hfsplus_file_extend()`, optionally zeroing new nodes when required, and updates node counts. `hfs_bmap_alloc()` scans header/map-node map records for free node bits, sets one, writes the btree header, and creates a bnode. `hfs_bmap_free()` clears a map bit with validation and updates free counts/header.

State and persistence: owns in-memory `struct hfs_btree` state and persists header fields plus btree allocation bits. Growing btree special files updates their inode allocation/size state and dirties the special inode.

Dependencies and integration: depends on `hfsplus_iget()`, bnode helpers, extent-based file extension, volume flags, and comparators from `catalog.c`, `extents.c`, and `attributes.c`. Mount code opens these trees; btree mutators reserve/allocate/free nodes here.

Risks and test signals: map-record corruption causes read-only fallback, a critical safety behavior. Attribute tree has different key rules. Tests should cover malformed headers, map bit 0 clear, HFSX binary vs casefold comparator selection, btree growth ENOSPC, new map-node creation, and node free double-free detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/catalog.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/catalog.c

Purpose: implements HFS+ catalog key ordering/building, catalog record/thread creation, CNID lookup, directory subfolder counters, create, delete, and rename.

Important APIs and control flow: `hfsplus_cat_case_cmp_key()` and `hfsplus_cat_bin_cmp_key()` compare by parent CNID then Unicode name, using casefold or binary comparison. `hfsplus_cat_build_key()` converts Linux names to HFS+ Unicode keys; `hfsplus_cat_build_key_with_cnid()` builds thread keys. `hfsplus_cat_set_perms()` serializes Linux mode/uid/gid/flags/rdev/nlink into HFS+ permission records. `hfsplus_cat_build_record()` creates folder/file records, including special hardlink alias records. `hfsplus_fill_cat_thread()` creates variable-size thread records. `hfsplus_find_cat()` resolves CNID through a thread to the visible record. `hfsplus_create_cat()` inserts thread and visible record with rollback. `hfsplus_delete_cat()` removes visible and thread records, frees resource forks, adjusts readdir cursors, updates subfolder counts, and deletes xattrs. `hfsplus_rename_cat()` inserts destination visible record, removes source visible/thread records, and creates a new thread.

State and persistence: mutates catalog tree pages, directory `i_size`, HFSX subfolder counters, inode times, catalog-tree dirty flag, and directory inode dirty flags. File/folder records persist permissions, Finder info, fork metadata, and hardlink metadata.

Dependencies and integration: uses HFS+ btree search/mutation, Unicode conversion, extent fork cleanup, xattr deletion, inode dirty marking, and directory open cursor lists.

Risks and test signals: create/delete/rename are multi-record and not journaled. Hardlink alias semantics depend on hidden directory state. Tests should cover Unicode names, HFSX subfolder counters, hardlink records, rename across dirs, resource-fork delete, xattr delete-all, and rollback after failed second insert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/catalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/dir.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/dir.c

Purpose: provides HFS+ VFS directory operations, including lookup, readdir, hard links, unlink/rmdir, symlink, mknod/create/mkdir, rename, ioctl exposure, xattr listing, and file attribute operations.

Important APIs and control flow: `hfsplus_lookup()` searches the catalog by Unicode parent/name, resolves HFS+ hardlink alias records through the hidden directory (`iNode%d`), stores the visible CNID in `d_fsdata`, and instantiates the real inode. `hfsplus_readdir()` emits synthetic `.`/`..`, walks catalog records, converts Unicode names to Linux strings, hides the hidden directory, derives d_type from permissions, and stores active cursor state. `hfsplus_link()` converts the original file into a hidden inode record if needed, creates visible hardlink catalog records, increments nlink/file count, and writes affected catalog inodes. `hfsplus_unlink()` handles open-file temporary rename to hidden dir, visible alias deletion, nlink updates, hidden inode deletion when last link closes, and writeback. `hfsplus_rmdir()` checks emptiness and deletes folder records. `hfsplus_symlink()` and `hfsplus_mknod()` create new inodes, catalog records, optional security xattrs, instantiate dentries, and write back. `hfsplus_rename()` removes existing destination then calls catalog rename and writes involved inodes.

State and persistence: updates catalog tree, hidden-directory hardlink records, dentry `d_fsdata`, link counts, file counts, inode times, security xattrs, and dirty catalog/MDB state under `vh_mutex`.

Dependencies and integration: integrates `catalog.c`, `inode.c`, `attributes.c`/xattr security, Unicode conversion, random link id generation, and VFS operation tables.

Risks and test signals: hardlink conversion and open-unlink temporary renames are complex and non-transactional. Security xattr failure cleanup is best-effort. Tests should cover hardlink creation/deletion, open unlink, hidden dir hiding, symlink content persistence, device nodes, rename replacement, and active readdir with deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/extents.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/extents.c

Purpose: maps, allocates, frees, writes, reads, and truncates HFS+ file/fork extents across catalog-inline extents and the extents overflow tree.

Important APIs and control flow: `hfsplus_ext_cmp_key()` orders extents by CNID, fork type, and start block. `hfsplus_ext_build_key()` builds fixed extents-tree keys. `hfsplus_ext_find_block()` maps logical allocation offsets across eight extents. `hfsplus_ext_write_extent()` flushes cached dirty/new overflow records with the inode extent lock. `hfsplus_ext_read_extent()` loads a cached overflow record when a block lies outside the first extents. `hfsplus_get_block()` maps VFS logical blocks to disk sectors, extends on create, reads overflow extents when needed, and marks dirty if extension or dirty-cache write occurred. `hfsplus_free_fork()` frees first and overflow extents, temporarily dropping the tree lock around bitmap frees. `hfsplus_file_extend()` allocates from the allocation bitmap near the last extent, falls back to the beginning, optionally zeroes new blocks, appends to existing extents or starts a new overflow record, and marks allocation/inode dirty. `hfsplus_file_truncate()` expands through zero-length write or frees trailing extents and removes obsolete overflow records.

State and persistence: mutates inode fork extent state, overflow extent btree records, allocation bitmap pages, free block count, physical/logical block counters, inode bytes, and dirty flags on allocation file, extents tree, and target inode.

Dependencies and integration: depends on `bitmap.c`, btree find/mutation helpers, inode writeback, page cache block mapping, and HFS+ superblock geometry (`fs_shift`, `blockoffset`, allocation block size).

Risks and test signals: lock ordering is delicate because bitmap frees occur outside the extents tree lock. The extents overflow file itself cannot use overflow lookups in `hfsplus_get_block()`. Tests should cover fragmented files with more than eight extents, ENOSPC and wraparound allocation, zeroout failure, truncate across overflow records, resource fork free, and dirty-cache read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/extents.c -->
