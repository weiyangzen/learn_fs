# Group Research: group_1003_linux_stable_sources_os_linux_linux_stable_fs_hfs_brec_c_sources_os_bebcba58e5de

Scope: `Docs/research_subset_a.md`. This grouped report covers the listed Linux stable classic HFS and HFS+ files under `sources/os/linux/linux-stable/fs/`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/brec.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/brec.c

## Scope

Implements classic HFS B-tree record mutation: record length/key-length discovery, leaf/index record insertion, record removal, node splitting, parent-key propagation, and tree-height growth.

## APIs And Behavior

- `hfs_brec_lenoff()` reads the record-offset table at the end of a bnode and returns record length plus start offset.
- `hfs_brec_keylen()` calculates keyed-record key length for leaf/index nodes, handling fixed index keys, variable index keys, and big-key validation against `tree->max_key_len`.
- `hfs_brec_insert()` inserts a key plus caller-supplied payload at `fd->record + 1`, splits the node if needed, updates leaf counts, shifts record offsets/data, and recursively inserts new child pointers into parent index nodes.
- `hfs_brec_remove()` removes the current record, compacts node data, unlinks empty nodes, removes parent index entries, and updates parent keys when the first key in a node changes.
- `hfs_bnode_split()` allocates a bmap node, divides records around the midpoint while accounting for the pending insert, rewrites sibling links, and updates `leaf_tail` when splitting the tail.
- `hfs_brec_update_parent()` replaces parent separator keys and may split index nodes if the replacement key grows.
- `hfs_btree_inc_height()` creates a new root node, turns an empty tree into a leaf tree, or creates an index root pointing at the old root.

## State And Dependencies

The file mutates `struct hfs_btree` root/depth/leaf counters, `struct hfs_bnode` sibling/parent/height/record metadata, and the on-disk node descriptor and record-offset table. It depends on `bnode.c` primitives, `bfind.c` search state, `btree.c` bmap allocation, and dirtying the B-tree inode when persistent tree metadata changes.

## Risks And Invariants

Record offsets grow upward from the node descriptor while record-offset slots grow downward from the end of the node; all insert/remove/split paths depend on preserving this layout exactly. Parent update paths temporarily reuse `fd->search_key` and `fd->bnode`, so reference ownership and restoration are subtle. If a split still cannot make room, the insert path panics, reflecting an assumed pre-reservation invariant.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/brec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/btree.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/btree.c

## Scope

Opens, closes, writes, grows, and allocates/free nodes for classic HFS catalog and extents B-trees.

## APIs And Behavior

- `hfs_btree_open()` allocates an in-memory `hfs_btree`, creates/initializes the special CNID inode, reads the on-disk header node into page cache, validates node size/count and max key length, and installs `hfs_btree_aops`.
- `hfs_btree_close()` releases all cached bnodes, warns about nonzero bnode refs, drops the tree inode, and frees the tree.
- `hfs_btree_write()` updates the header record fields for root, leaf count/head/tail, node count/free count, attributes, and depth.
- `hfs_bmap_reserve()` extends the tree file until enough free B-tree nodes exist, then updates inode sizes and tree node counts.
- `hfs_bmap_alloc()` scans the header/map-node bitmap for a free node bit, marks it allocated, creates map nodes when needed, decrements `free_nodes`, and returns a zeroed bnode via `hfs_bnode_create()`.
- `hfs_bmap_free()` locates the map bit for a node, clears it, and increments `free_nodes`.

## State And Dependencies

This file bridges the HFS MDB fork records to in-memory B-tree metadata. It depends on `hfs_inode_read_fork()`, `hfs_ext_find_block()`, special CNIDs `HFS_EXT_CNID` and `HFS_CAT_CNID`, page-cache helpers, block reads, and bnode primitives.

## Risks And Invariants

Tree header validation is limited but important: node size must be a power of two, node count nonzero, and max key length must match the requested tree type. Bmap allocation assumes `hfs_bmap_reserve()` has made enough nodes available. Map-node creation still contains panic/FIXME behavior if `free_nodes` is unexpectedly zero.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/btree.h -->
# File Research: sources/os/linux/linux-stable/fs/hfs/btree.h

## Scope

Declares the classic HFS B-tree in-memory structures, find cursor, node flags, lock class enum, and cross-file B-tree APIs.

## Key Structures

- `struct hfs_btree` stores the superblock, special tree inode, key comparator, root/leaf/node/free counts, attributes, node sizing, tree mutex, page count per bnode, hash lock, and bnode hash table.
- `struct hfs_bnode` stores tree linkage, sibling/parent IDs, node type/height, record count, hash linkage, state flags, waitqueue, refcount, page offset, and backing pages.
- `struct hfs_find_data` is the shared cursor used by search and mutation paths: active/search keys, tree, current bnode, record index, and key/entry offsets and lengths.

## API Surface

The header exposes B-tree open/close/write and bmap allocation, low-level bnode read/write/copy/move/refcount routines, B-tree record insertion/removal, and search/read/goto helpers from `bfind.c`.

## Risks And Invariants

The header makes the locking model visible: callers generally enter through `hfs_find_init()` and hold `tree_lock` while using `hfs_find_data`. Bnodes are refcounted and hash-cached, so any path storing `fd->bnode` must pair with `hfs_find_exit()` or explicit `hfs_bnode_put()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/catalog.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/catalog.c

## Scope

Implements classic HFS catalog B-tree key creation, record/thread creation, lookup-by-CNID, create/delete/move operations, and catalog key comparison.

## APIs And Behavior

- `hfs_cat_build_key()` builds a catalog key from parent CNID and optional name, converting Linux names to Mac names.
- `hfs_cat_create()` creates both the thread record keyed by new CNID and the visible directory/file record keyed by parent/name, with pre-reservation for B-tree splits and rollback of the thread record on failure.
- `hfs_cat_keycmp()` orders records by parent ID then Macintosh lexical order via `hfs_strcmp()`.
- `hfs_cat_find_brec()` resolves a CNID through its thread record, validates thread type/name length, reconstructs the parent/name key, and finds the visible catalog record.
- `hfs_cat_delete()` deletes the visible record, frees resource forks for files, adjusts open readdir positions, removes the thread record when present, updates parent size/mtime, and corrects `next_id`.
- `hfs_cat_move()` implements rename by inserting a destination visible record, removing the source record, then replacing the thread record with one pointing at the new parent/name.

## State And Dependencies

This file updates directory `i_size`, timestamps, catalog B-tree records, MDB counters indirectly through inode deletion paths, and open directory iteration cursors. It depends on B-tree search/mutation, string conversion, extent freeing for resource forks, and `HFS_SB(sb)->next_id`.

## Risks And Invariants

Catalog entries are paired with thread records; create/move/delete must keep the two in sync. `hfs_correct_next_unused_CNID()` scans backward from the leaf tail after deletion to repair the allocator's next CNID, and treats malformed leaf ordering/key lengths as corruption. Readdir position adjustment is protected only against release by `open_dir_lock` and relies on the VFS directory lock for catalog deletion exclusion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/catalog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/dir.c

## Scope

Provides classic HFS directory VFS operations: lookup, readdir, create, mkdir, unlink/rmdir, rename, directory release, and operation tables.

## APIs And Behavior

- `hfs_lookup()` searches the catalog by parent/name and instantiates an inode with `hfs_iget()`.
- `hfs_readdir()` emits synthetic `.` and `..`, resolves the folder thread for the parent ID, then walks catalog records under the current directory CNID, converting Mac names to Linux names.
- `hfs_create()` and `hfs_mkdir()` allocate a new inode, create catalog records, instantiate the dentry, and roll back inode state on catalog failure.
- `hfs_remove()` enforces directory emptiness, rejects operations if CNID counters are out of range, deletes catalog records, clears link count, and truncates/deletes the inode.
- `hfs_rename()` supports only `RENAME_NOREPLACE`, removes any existing destination, moves catalog records, and updates the moved inode's cached catalog key.

## State And Dependencies

Directory offsets use `inode->i_size` with two synthetic entries included. The file depends on catalog helpers, inode creation/deletion/truncation, dcache splice helpers, and per-inode open directory readdir tracking.

## Risks And Invariants

`hfs_readdir()` requires catalog records to stay grouped by parent CNID; walking past that boundary is treated as `-EIO`. HFS has no hardlinks, so unlink and rmdir both clear the target link count after the directory-specific emptiness check. Rename first deletes any target entry, so partial failures after target removal can be externally visible.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/extent.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/extent.c

## Scope

Manages classic HFS extent records, overflow extent cache writeback/read, block mapping, file extension, fork freeing, and truncation.

## APIs And Behavior

- `hfs_ext_keycmp()` orders extents by CNID, fork type, then allocation block number.
- `hfs_ext_find_block()` maps a fork-relative allocation-block offset through a three-entry extent record.
- `hfs_ext_write_extent()` writes dirty cached overflow extents, inserting new overflow records or overwriting existing ones.
- `hfs_get_block()` maps VFS logical blocks to physical disk sectors and allocates blocks for extending writes.
- `hfs_extend_file()` finds free allocation blocks, appends them to first extents or cached overflow extents, or creates a new overflow record when the current extent record is full.
- `hfs_free_fork()` frees first and overflow extents for a data/resource fork and removes overflow records.
- `hfs_file_truncate()` grows sparse page-cache state when `i_size` exceeds physical size, or frees extents and overflow records when shrinking.

## State And Dependencies

Per-inode extent state includes first extents, cached overflow extents, first/cached block counts, allocation block count, physical size, filesystem block count, and dirty/new extent flags. The file depends on the volume bitmap, extents B-tree, block mapper, page-cache write helpers, MDB dirtying, and allocation block geometry from `HFS_SB`.

## Risks And Invariants

The cached overflow record must be flushed before replacing it. Allocation and truncation require `extents_lock` to serialize cached extent state. Shrink paths free blocks while removing overflow records, but error handling is limited and comments note missing propagation for `hfs_file_truncate()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/hfs.h -->
# File Research: sources/os/linux/linux-stable/fs/hfs/hfs.h

## Scope

Small classic HFS header that includes common on-disk declarations and defines directory iteration private state.

## Data Structure

`struct hfs_readdir_data` links an open directory stream into the owning inode's `open_dir_list`, stores the associated `struct file`, and records the last catalog key used for readdir position adjustment during deletion.

## Dependencies And Risks

This structure is used by `dir.c` and `catalog.c` under `open_dir_lock`. Its correctness depends on release removing entries from the list and catalog deletion adjusting `f_pos` when a removed key precedes an active iterator.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/hfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/hfs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/hfs/hfs_fs.h

## Scope

Primary classic HFS filesystem header. Defines in-memory inode/superblock state, flags, public helper prototypes, time conversion helpers, dirtying helpers, and 512-byte-sector block-read macro.

## Key Structures

- `struct hfs_inode_info` stores open count, flags, timezone offset, catalog key, open directory iterator list, resource-fork inode pointer, extent lock/cache, fork sizes, and embedded VFS inode.
- `struct hfs_sb_info` stores primary/alternate MDB buffers, allocation bitmap, extents/catalog B-trees, file/folder/CNID counters, allocation geometry, mount defaults, NLS tables, bitmap/MDB dirty state, delayed work state, and partition/session options.

## API Surface

The header exposes bitmap, catalog, directory, extent, inode, xattr, MDB, partition, string, translation, and superblock dirtying APIs. It also defines `HFS_I()`/`HFS_SB()` accessors, HFS timestamp conversion between Mac and Unix epochs with timezone adjustment, and `sb_bread512()` for sector-granular reads on larger block devices.

## Risks And Invariants

The timestamp model intentionally maps pre-1970 on-disk values into the 2040-2106 range to match historical 64-bit Linux behavior. Superblock dirty flags distinguish MDB, alternate MDB, and bitmap writes. Resource forks use a paired inode pointer and `HFS_FLG_RSRC`, so main/resource inode lifetime must stay synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/hfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/inode.c

## Scope

Implements classic HFS inode lifecycle, address-space operations, fork read/write, inode writeback, resource-fork lookup, setattr/truncate, fsync, and file operation tables.

## APIs And Behavior

- Address-space methods map buffered/direct I/O through `hfs_get_block()`, clean up failed extending writes, and release cached bnodes from B-tree pages when possible.
- `hfs_new_inode()` allocates a VFS inode, assigns a CNID from `next_id`, initializes mode/ownership/extent state, updates file/folder/root counters, and marks the MDB dirty.
- `hfs_delete_inode()` decrements counters and truncates regular files with no links.
- `hfs_inode_read_fork()` and `hfs_inode_write_fork()` translate between on-disk fork extent/size fields and in-memory extent/size state.
- `hfs_iget()` uses `iget5_locked()` with catalog record matching to load files or directories.
- `hfs_write_inode()` flushes dirty extents, writes B-tree headers for special tree inodes, and updates catalog file/folder records for normal and resource-fork inodes.
- `hfs_file_lookup()` exposes the resource fork as a synthetic `rsrc` child inode of regular file inodes.
- `hfs_inode_setattr()` restricts uid/gid/mode changes to HFS' model and performs size changes through `hfs_file_truncate()`.
- `hfs_file_fsync()` writes data, writes the inode/MDB, flushes delayed MDB work, and syncs the block device.

## State And Dependencies

This file ties VFS inode/page-cache operations to catalog and extent metadata. It depends on catalog lookup keys, extent allocation/truncation, MDB dirty delayed work, xattrs, generic file helpers, and the B-tree special inodes.

## Risks And Invariants

HFS permissions are coarse: file write bits are all-on or all-off and directories cannot meaningfully change mode beyond the mount mask. Resource fork inodes are fake-hashed and share catalog records with their main inode, so writeback routes through `main_inode`. B-tree page release must not free a referenced bnode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/mdb.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/mdb.c

## Scope

Reads, validates, opens, commits, closes, and releases the classic HFS Master Directory Block (MDB), alternate MDB, allocation bitmap, and core B-trees.

## APIs And Behavior

- `hfs_get_last_session()` resolves multisession CD-ROM starts or an explicit session option.
- `is_hfs_cnid_counts_valid()` validates next CNID, file count, and folder count against 32-bit HFS limits.
- `hfs_mdb_get()` sets device block size, finds the MDB directly or through Mac partition maps, validates allocation block size, loads primary and alternate MDBs, loads the volume bitmap, opens extents/catalog B-trees, and forces read-only on corrupt counts, dirty unmount, or locked volume attributes.
- `hfs_mdb_commit()` writes dirty MDB counters/timestamps, optionally syncs the alternate MDB when tree fork extents change, and writes dirty volume bitmap blocks.
- `hfs_mdb_close()` marks a writable volume cleanly unmounted.
- `hfs_mdb_put()` closes B-trees, releases buffers, unloads NLS tables, and frees the bitmap.

## State And Dependencies

This file initializes most `hfs_sb_info` runtime state: allocation geometry, counters, root counts, B-tree pointers, bitmap memory, NLS lifetime, and dirty flags. It depends on `hfs_part_find()`, `hfs_btree_open()`, `hfs_inode_write_fork()`, and block-buffer IO.

## Risks And Invariants

Mount can leave the filesystem read-only based on on-disk state but still complete successfully. Bitmap allocation is fixed at 8192 bytes, matching classic HFS bitmap limits. Commit locks the primary MDB buffer while updating MDB fields and bitmap dirty state, so callers should not hold conflicting buffer locks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/mdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/part_tbl.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/part_tbl.c

## Scope

Parses old and new Macintosh partition maps to locate an HFS partition inside a block device.

## APIs And Behavior

`hfs_part_find()` reads the partition map block at the current candidate start, distinguishes old and new partition map signatures, scans entries for either old `TFS1` IDs or new `Apple_HFS` partition types, honors the mount `part` option, and updates `part_start` and `part_size` on success.

## State And Dependencies

The function uses `sb_bread512()` for sector-sized reads regardless of filesystem block size and reads `HFS_SB(sb)->part` to select a specific partition index or the first matching partition.

## Risks And Invariants

The new partition map loop trusts `pmMapBlkCnt` as the number of map blocks to scan but stops if subsequent signatures are invalid. Old-map scanning does not break on match, so later matching entries can overwrite earlier matches unless a specific `part` was requested.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/part_tbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/string.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/string.c

## Scope

Implements classic HFS case-insensitive Macintosh filename hashing, ordering, and dentry comparison.

## APIs And Behavior

- `caseorder[256]` defines HFS case-folded lexical ordering for Macintosh character bytes.
- `hfs_hash_dentry()` hashes up to `HFS_NAMELEN` bytes using `caseorder`.
- `hfs_strcmp()` compares two byte strings by HFS lexical order, falling back to length difference.
- `hfs_compare_dentry()` checks dentry-name equality under the same case-folded ordering and HFS name-length truncation rules.

## State And Dependencies

Exports are visible to KUnit through `EXPORT_SYMBOL_IF_KUNIT`. The functions are used by catalog key comparison and dentry operations.

## Risks And Invariants

The comparison is byte-table based, not Unicode normalization. Names at or above `HFS_NAMELEN` are truncated for hashing/comparison in ways that must match catalog key construction and VFS dentry behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/string_test.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/string_test.c

## Scope

KUnit tests for classic HFS string comparison, hashing, and dentry comparison.

## Tests Covered

- `hfs_strcmp_test()` checks equal/unequal strings, length ordering, case-insensitive equality, special-character differences, and one-byte boundaries.
- `hfs_hash_dentry_test()` checks successful hashing and verifies case-insensitive names hash equally.
- `hfs_compare_dentry_test()` checks exact/case-insensitive equality, length mismatches, empty strings, and an `HFS_NAMELEN` boundary case.

## Dependencies And Risks

The tests import the KUnit-exported string helpers and use minimal dummy dentries. The coverage is useful for basic behavior but does not validate the full Macintosh `caseorder` table, non-ASCII Mac encodings, or catalog ordering edge cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/string_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/super.c

## Scope

Registers the classic HFS filesystem and implements fs-context option parsing, mount, remount, statfs, sync, delayed MDB flushing, superblock teardown, and inode-cache lifecycle.

## APIs And Behavior

- `hfs_sync_fs()` validates counters and commits the MDB.
- `hfs_put_super()` cancels delayed MDB work, marks the MDB clean, and releases MDB resources.
- `hfs_mark_mdb_dirty()` queues delayed MDB writeback on `system_long_wq` unless read-only.
- `hfs_statfs()` reports allocation-block based capacity/free counts and maximum name length.
- `hfs_reconfigure()` handles read-only/read-write transitions while refusing write access to unclean or locked volumes.
- `hfs_show_options()` emits non-default mount options.
- `hfs_parse_param()` parses uid/gid, umasks, partition/session selection, file type/creator, quiet mode, codepage, and iocharset.
- `hfs_fill_super()` initializes `hfs_sb_info`, reads the MDB, finds the root catalog record by `HFS_ROOT_CNID`, loads the root inode, and installs dentry operations.
- Module init/exit creates/destroys the inode slab and registers/unregisters `hfs`.

## State And Dependencies

The file owns `hfs_inode_cachep` and the `file_system_type`. It depends on `hfs_mdb_get/put/commit`, catalog lookup, root inode loading, xattr handlers, NLS option loading, and block-device mount helpers.

## Risks And Invariants

Remount ignores fs-specific option changes and only handles read-only state. Error cleanup after failed `hfs_mdb_get()` calls `hfs_mdb_put()`, so MDB teardown must tolerate partially initialized superblock state. Dirty MDB writeback is delayed and separately flushed by fsync.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/sysdep.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/sysdep.c

## Scope

Defines classic HFS dentry operations and timezone revalidation behavior.

## APIs And Behavior

`hfs_revalidate_dentry()` rejects RCU lookup with `-ECHILD`, accepts negative dentries, and adjusts cached inode atime/mtime/ctime if the global timezone offset changed since inode load. `hfs_dentry_operations` wires this revalidation with HFS-specific hash and compare functions.

## State And Dependencies

The file depends on `sys_tz`, per-inode `tz_secondswest`, and string helpers from `string.c`.

## Risks And Invariants

Timestamp adjustment mutates inode timestamps during dentry revalidation to preserve HFS local-time semantics. RCU path walk cannot perform this work, so RCU lookup must fall back.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/sysdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/trans.c -->
# File Research: sources/os/linux/linux-stable/fs/hfs/trans.c

## Scope

Converts classic HFS names between on-disk Macintosh Pascal strings and Linux filename byte strings, with optional NLS transcoding.

## APIs And Behavior

- `hfs_mac2asc()` converts an HFS name to an output filename buffer, caps source length at `HFS_NAMELEN`, maps `/` to `:`, optionally transcodes disk NLS to Unicode then IO NLS, and returns output byte length.
- `hfs_asc2mac()` converts a Linux `qstr` to an HFS name, maps `:` to `/`, optionally transcodes through IO/disk NLS tables, caps output to `HFS_NAMELEN`, stores length, and zero-fills the remaining name buffer.

## State And Dependencies

Uses `HFS_SB(sb)->nls_disk` and `nls_io` from mount options. The converted names feed catalog key creation and readdir output.

## Risks And Invariants

The separator mapping is intentionally asymmetric for Linux legality versus HFS legality. Failed conversions substitute `?` except for output-space exhaustion, where conversion stops. Output is not NUL terminated by `hfs_mac2asc()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfs/trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/Kconfig

## Scope

Defines kernel configuration entries for HFS+ filesystem support and HFS+ KUnit tests.

## Configuration

- `HFSPLUS_FS` is a tristate block-device filesystem option. It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, `NLS_UTF8`, and `LEGACY_DIRECT_IO`.
- `HFSPLUS_KUNIT_TEST` builds HFS+ KUnit tests when `HFSPLUS_FS` and `KUNIT` are enabled, defaulting under `KUNIT_ALL_TESTS`.

## Risks And Invariants

The selected dependencies reflect implementation choices in this directory: buffer-head based block mapping, NLS/UTF-8 name conversion, and legacy direct I/O hooks. KUnit tests are explicitly development-only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/Makefile

## Scope

Builds the HFS+ module/object and optional HFS+ KUnit test object.

## Build Composition

`hfsplus.o` is composed from superblock/options/inode/ioctl/extents/catalog/dir/B-tree/unicode/wrapper/bitmap/partition/attribute/xattr sources. `unicode_test.o` is built when `CONFIG_HFSPLUS_KUNIT_TEST` is enabled.

## Dependencies And Risks

The object list shows the runtime subsystem boundaries: B-trees, catalog, allocation/extents, Unicode conversion, wrapper/partition probing, inode/superblock integration, and xattr families. Build failures in any listed component block the single `hfsplus` filesystem object.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/attributes.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/attributes.c

## Scope

Implements HFS+ attributes B-tree key comparison/building and inline extended-attribute create/find/delete/replace operations.

## APIs And Behavior

- `hfsplus_create_attr_tree_cache()` and `hfsplus_destroy_attr_tree_cache()` manage a slab for `hfsplus_attr_entry`.
- `hfsplus_attr_bin_cmp_key()` orders attributes by CNID then attribute Unicode name.
- `hfsplus_attr_build_key()` builds an attribute key from CNID and xattr name using HFS+ Unicode conversion.
- `hfsplus_find_attr()` searches exact attribute names or the first record for a CNID.
- `hfsplus_attr_exists()` probes for an attribute.
- `hfsplus_create_attr()` creates only inline-data attributes, rejecting oversized values with `-E2BIG`.
- `hfsplus_delete_attr()` deletes one inline attribute and rejects fork-data/extents attribute records as unsupported.
- `hfsplus_delete_all_attrs()` repeatedly finds and deletes all attributes for a CNID.
- `hfsplus_replace_attr()` deletes an existing attribute then creates the replacement record.

## State And Dependencies

The file depends on `HFSPLUS_SB(sb)->attr_tree`, B-tree search/mutation, HFS+ name conversion, xattr name type conversion, and inode/tree dirty flags `HFSPLUS_I_ATTR_DIRTY`.

## Risks And Invariants

Linux HFS+ supports Mac OS X style inline xattrs only; fork-data and extents records are recognized but not supported. Delete reads the current key into `fd->search_key` before removal to avoid B-tree corruption from stale cursor data. Replace is not transactional: deletion can succeed and creation can fail.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/attributes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/bfind.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/bfind.c

## Scope

Implements HFS+ B-tree search cursors, exact/CNID-first binary-search strategies, record reads, relative record movement, and catalog record size validation.

## APIs And Behavior

- `hfs_find_init()` allocates paired search/current key buffers and locks the tree mutex with a tree-specific lock class.
- `hfs_find_exit()` drops the current bnode, frees key memory, unlocks the tree, and clears the cursor tree pointer.
- `hfs_find_1st_rec_by_cnid()` searches for the first record matching a CNID across extents, catalog, or attributes trees.
- `hfs_find_rec_by_key()` performs exact key comparison using the tree comparator.
- `__hfs_brec_find()` binary-searches within one bnode and fills record/key/entry offsets and lengths.
- `hfs_brec_find()` descends root-to-leaf through index nodes, validating height/type consistency.
- `hfs_brec_read()` finds and reads an entry into a bounded caller buffer.
- `hfs_brec_goto()` walks forward/backward across leaf sibling links and updates cursor offsets.
- `hfsplus_brec_read_cat()` reads a catalog record and validates that its length matches the record type, including variable-size thread records.

## State And Dependencies

The file depends on B-tree key comparators, bnode read helpers, record length/key-length helpers, and lock-class selection. It is the shared cursor layer for catalog, extents, attributes, and directory iteration.

## Risks And Invariants

Search cursors own the tree mutex. Callers that copy `struct hfs_find_data` must avoid double-freeing the shared key buffer and must explicitly drop secondary bnodes, as seen in rename paths. Catalog record size validation is a corruption hardening point for variable-length thread records.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/bfind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/bitmap.c

## Scope

Manages allocation bitmap bits for HFS+ allocation blocks.

## APIs And Behavior

- `hfsplus_block_allocate()` scans the allocation file bitmap from a requested offset, finds a free bit, sets up to `*max` contiguous free bits, updates `*max` to the allocated length, decrements `free_blocks`, marks bitmap pages dirty, and marks the MDB dirty.
- `hfsplus_block_free()` clears a range of allocation bits, validates the range against `total_blocks`, increments `free_blocks`, marks pages/MDB dirty, and reports page read failures as `-EIO`.

## State And Dependencies

Uses `HFSPLUS_SB(sb)->alloc_file`, `alloc_mutex`, `total_blocks`, `free_blocks`, and page-cache reads of the allocation file. Bitmap bits are big-endian u32 words with high bit representing the first block in a word.

## Risks And Invariants

The allocator may allocate fewer blocks than requested and reports that through `*max`. It uses page-cache pages from the allocation file and marks them dirty, so allocation metadata writeback depends on normal inode writeback plus MDB dirtying. Freeing does not verify bits were previously set; it clears the requested range.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/bnode.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/bnode.c

## Scope

Implements HFS+ low-level B-tree node IO, memory movement, validation, hash-cache lookup, creation, refcounting, unlinking, and deletion cleanup.

## APIs And Behavior

- `hfs_bnode_read/write/clear/copy/move()` operate on bnode byte ranges across one or more page-cache pages, validate offsets/lengths, and mark modified pages dirty.
- `hfs_bnode_read_key()` reads variable or fixed-length keys, with attributes-tree special handling and maximum size validation.
- `hfs_bnode_dump()` emits debug details about node descriptors and record offsets.
- `hfs_bnode_unlink()` updates previous/next sibling links, leaf head/tail, root/depth for root deletion, and marks the node deleted.
- `hfs_bnode_findhash()` and `hfs_bnode_find()` implement cached bnode lookup and loading from the tree inode.
- `hfs_bnode_find()` validates node type/height, first offset, monotonic even record offsets, and key sizes for index/leaf records.
- `hfs_bnode_create()` creates a new zeroed bnode and clears the `NEW` flag after initialization.
- `hfs_bnode_put()` frees deleted nodes by unhashing, optionally zeroing contents, freeing the bmap bit, and releasing pages.
- `hfs_bnode_need_zeroout()` checks the volume unused-node-fix attribute for catalog-tree zeroing.

## State And Dependencies

This file owns the bnode hash/refcount/waitqueue protocol and depends on page cache, B-tree geometry, bmap free, node validation helpers, and volume header attributes.

## Risks And Invariants

Concurrent loads of the same node synchronize through `HFS_BNODE_NEW` and `lock_wq`. A malformed node causes `HFS_BNODE_ERROR` and `-EIO`. Deleted nodes are not physically freed until the last ref drops, and freeing requires the tree mutex because it clears the bmap bit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/bnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/brec.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/brec.c

## Scope

Implements HFS+ B-tree record insertion/removal, node splitting, parent key updates, and height growth.

## APIs And Behavior

- `hfs_brec_lenoff()` reads record length and offset from the bnode offset table.
- `hfs_brec_keylen()` returns fixed index key length for non-variable non-attribute index nodes, otherwise validates and returns the big-key length from the record itself.
- `hfs_brec_insert()` inserts `fd->search_key` plus entry payload, splits full nodes, updates leaf counts, shifts offsets/data, and recursively inserts index records for split nodes.
- `hfs_brec_remove()` removes the current record, unlinks empty nodes, removes parent index records, compacts data, and updates parent keys for first-record changes.
- `hfs_bnode_split()` allocates a new bnode, chooses a split point based on half-node data and record-offset table size, copies upper records, updates sibling descriptors, and handles tail updates.
- `hfs_brec_update_parent()` replaces parent separator keys, splitting index nodes if the new key is larger.
- `hfs_btree_inc_height()` creates a new root and installs the old root as an index child when needed.

## State And Dependencies

The file depends on HFS+ bnode primitives, `hfs_bmap_alloc()`, `hfs_brec_find()` strategy callbacks, tree dirtying, and attributes-tree special key semantics.

## Risks And Invariants

Unlike classic HFS, HFS+ keys use big-key 16-bit lengths and attributes-tree index keys are treated as variable even when tree flags differ. Split failure unlinks the newly allocated node before returning `-ENOSPC`. Cursor mutation and reference transfers mirror classic HFS and require careful `hfs_bnode_put()` pairing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/brec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/btree.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/btree.c

## Scope

Opens/closes/writes HFS+ B-trees, computes metadata-file clump sizes, manages B-tree node bitmap records, reserves/allocates/frees B-tree nodes, and validates map state.

## APIs And Behavior

- `hfsplus_calc_btree_clump_size()` computes default clump sizes for catalog, attributes, and extents trees based on volume size and node/block size.
- `hfs_btree_open()` loads a special-file inode, reads the header record, validates max key length, flags, node size/count, and installs the correct comparator for extents/catalog/attributes. It also checks bit 0 in the tree map and forces read-only on corruption.
- `hfs_btree_close()` releases cached nodes and the tree inode.
- `hfs_btree_write()` writes root, leaf, node count/free count, attributes, and depth back to the header node.
- `hfs_bmap_reserve()` extends the tree file until enough free nodes are available, optionally zeroing newly allocated bnodes for catalog unused-node fix.
- `hfs_bmap_alloc()` scans header/map-node bitmap records for a free node bit, creates new map nodes if needed, writes the header, and returns a new bnode.
- `hfs_bmap_free()` locates and clears a node bit through validated map-record access and updates free-node counts.

## State And Dependencies

This file depends on special CNID inodes via `hfsplus_iget()`, bnode loading/validation, extent-backed file extension, catalog/casefold flags, HFSX key type, and volume header attributes. It relies on `tree_lock` being held for bmap reserve/alloc/free.

## Risks And Invariants

Catalog trees require variable index keys; extents trees reject variable index keys; all HFS+ B-trees require big keys. Header/map-node bitmap access validates node type and record offsets before mapping pages. Detected map corruption forces the superblock read-only rather than failing mount outright.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/catalog.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/catalog.c

## Scope

Implements HFS+ catalog key comparison/building, catalog record/thread construction, permission serialization, CNID lookup, create/delete, rename, and HFSX subfolder count handling.

## APIs And Behavior

- `hfsplus_cat_case_cmp_key()` and `hfsplus_cat_bin_cmp_key()` order catalog keys by parent CNID then casefolded or binary Unicode comparison.
- `hfsplus_cat_build_key()` converts a Linux name to HFS+ Unicode and builds a parent/name key; `hfsplus_cat_build_key_with_cnid()` builds a thread key.
- `hfsplus_cat_set_perms()` serializes mode, uid/gid, immutable/append flags, link count, and device number into HFS+ permission fields.
- `hfsplus_cat_build_record()` creates file/folder catalog records, including HFSX folder count flags, symlink type/creator, hardlink metadata, and hidden-directory visibility flags.
- `hfsplus_find_cat()` resolves a CNID through a thread record, validates thread type/name length, reconstructs the parent/name key, and finds the visible record.
- `hfsplus_create_cat()` inserts thread and visible records with rollback and updates directory size/subfolder counts.
- `hfsplus_delete_cat()` deletes visible and thread records, frees resource forks, adjusts active readdir offsets, updates directory metadata, and deletes all xattrs for deleted files/folders.
- `hfsplus_rename_cat()` inserts a destination record, removes the old visible record, replaces the thread record, and dirties involved catalog inodes.

## State And Dependencies

The file depends on Unicode conversion, B-tree record operations, extents/resource-fork freeing, attributes deletion, hidden directory state, inode dirty flags, and HFSX volume flags.

## Risks And Invariants

Every file/folder should have a thread record; rename/delete must preserve or remove the pair consistently. Hardlinks are represented by catalog proxy records and hidden-directory backing records. HFSX subfolder counts are best-effort and decremented only if nonzero because older implementations may not maintain them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/catalog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/dir.c

## Scope

Provides HFS+ directory VFS operations: lookup, readdir, hardlink creation, unlink, rmdir, symlink, mknod/create/mkdir, rename, and directory operation tables.

## APIs And Behavior

- `hfsplus_lookup()` searches the catalog, resolves HFS+ hardlink proxy records through the hidden directory, stores catalog CNID in `d_fsdata`, and instantiates the target inode.
- `hfsplus_readdir()` emits `.`/`..`, walks catalog entries under a directory CNID, skips the hidden directory, converts Unicode names to mount charset, and emits file types from serialized modes.
- `hfsplus_link()` implements HFS+ hardlinks by moving the original file to the hidden directory if needed, creating catalog proxy records with new CNIDs, incrementing link count, and writing affected catalog records.
- `hfsplus_unlink()` handles open unlinked files by renaming them to hidden `temp*` records, deletes proxy and backing hidden records when link counts reach zero, and updates counts/dirty state.
- `hfsplus_rmdir()` enforces empty directories and deletes catalog records.
- `hfsplus_symlink()` writes the symlink body, creates catalog/security metadata, and instantiates the dentry.
- `hfsplus_mknod()` creates regular, directory, and special-file inodes, creates catalog records, initializes security xattrs, and writes catalog records.
- `hfsplus_rename()` supports only `RENAME_NOREPLACE`, removes existing destination entries, renames catalog records, transfers `d_fsdata`, and writes old/new dir and inode records.

## State And Dependencies

The file serializes namespace-changing operations with `vh_mutex`. It depends on catalog helpers, inode creation/deletion/writeback, hidden directory state, xattr security initialization, Unicode conversion, hardlink IDs, and open directory iterator tracking.

## Risks And Invariants

`d_fsdata` is semantically important because it stores the catalog CNID for proxy hardlink entries, which can differ from inode `i_ino`. Open-unlink handling relies on hidden temporary records and `S_DEAD`. Several operations write multiple catalog records after structural B-tree changes, so partial failure can leave work for fsck.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/extents.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/extents.c

## Scope

Manages HFS+ extents in catalog records and the extents overflow B-tree, including block mapping, file extension, fork freeing, extent cache writeback/read, and truncation.

## APIs And Behavior

- `hfsplus_ext_cmp_key()` orders extents by CNID, fork type, then starting allocation block.
- `hfsplus_ext_write_extent()` flushes dirty cached overflow extents, inserting new records or overwriting existing records.
- `hfsplus_get_block()` maps VFS logical blocks to physical sectors, extends the file for sequential writes, resolves first or cached overflow extents, and marks the inode dirty when allocation or extent-cache writeback occurs.
- `hfsplus_free_fork()` frees first extents and overflow extents for a fork, removing overflow B-tree records as it walks backward.
- `hfsplus_file_extend()` checks allocation-file capacity, chooses an allocation goal from the last extent, allocates blocks from the bitmap with wraparound, optionally zeroes blocks, appends to first/cached extents, or starts a new overflow extent record.
- `hfsplus_file_truncate()` extends page-cache state when growing beyond physical size or frees extents/overflow records and updates physical/fs block counts when shrinking.

## State And Dependencies

Per-inode state includes first/cached extents, cached start/count, first block count, allocation blocks, clump blocks, physical size, filesystem blocks, and `HFSPLUS_EXT_DIRTY/NEW` state. The file depends on allocation bitmap routines, extents B-tree cursors, file write helpers, superblock allocation geometry, and inode/tree dirty flags.

## Risks And Invariants

The extents overflow tree is itself extent-backed, so `hfsplus_get_block()` rejects overflow lookups for `HFSPLUS_EXT_CNID` beyond first extents to avoid recursion. Free/truncate paths unlock the B-tree mutex while freeing allocation bitmap blocks, then relock with the same nested class. Error handling in truncate is limited and comments note missing propagation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/extents.c -->