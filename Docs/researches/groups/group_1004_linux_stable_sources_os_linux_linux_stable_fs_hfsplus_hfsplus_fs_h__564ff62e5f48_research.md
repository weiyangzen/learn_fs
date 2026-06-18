# Group Research: group_1004_linux_stable_sources_os_linux_linux_stable_fs_hfsplus_hfsplus_fs_h__564ff62e5f48

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable/fs/hfsplus/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_fs.h

## Role

Central private header for the Linux HFS+ driver. It defines in-memory B-tree, superblock, inode, finder, and readdir state; mount/runtime flags; compatibility aliases; ioctl constants; cross-file function prototypes; and small inline helpers used by nearly every HFS+ implementation file.

## Key Definitions

- `struct hfs_btree`: in-memory representation of an HFS+ B-tree, including backing inode, key comparator, root/leaf/free-node counters, node sizing, tree mutex, pages-per-node metadata, and a hash table of cached `hfs_bnode` objects.
- `struct hfs_bnode`: in-memory B-tree node with tree pointer, linkage fields, record count, node type/height, flags, wait queue, refcount, page offset, and flexible page array.
- `struct hfsplus_sb_info`: filesystem private superblock state derived from the on-disk volume header plus runtime state:
  - volume header buffers and backup header buffers;
  - extents/catalog/attributes B-trees;
  - allocation file and hidden directory inodes;
  - NLS table;
  - partition/session/block layout;
  - immutable allocation geometry;
  - mutable `free_blocks`, `next_cnid`, file/folder counts;
  - mount flags and delayed sync work state.
- `struct hfsplus_inode_info`: private inode state for resource forks, extent caches, create date, link id, BSD user flags, subfolder count, open directory tracking, physical size, and embedded VFS inode.
- `struct hfs_find_data`: B-tree search cursor carrying caller-owned keys plus located node, record number, key offset/length, and entry offset/length.
- `struct hfsplus_readdir_data`: open-directory iteration state linked into inode-private open-dir tracking.
- Runtime flags include backup-header write, nodecompose, force, HFSX, casefold, nobarrier, uid override, and gid override.
- Inode flags include resource fork, catalog dirty, extents dirty, allocation dirty, and attributes dirty.
- `HFSPLUS_IOC_BLESS` defines the HFS+-specific boot-blessing ioctl.

## Cross-File API Surface

The header exposes the driver’s internal subsystem contracts:

- Attributes: key comparison/building, lookup, create/delete/replace, delete-all, cache lifecycle.
- Bitmap/allocation: block allocate/free.
- B-tree and B-node: open/close/write, bitmap reserve/alloc/free, node I/O, hash lookup, create/free/get/put.
- B-record/B-find: record insert/remove/read/goto and search routines.
- Catalog: key comparison/building, permissions serialization, catalog lookup/create/delete/rename.
- Extents: key comparison, extent writeback, block mapping, fork free, file extend/truncate.
- Inode/VFS: address-space ops, dentry ops, inode creation/deletion, fork read/write, catalog inode read/write, getattr/fsync/fileattr.
- Options, partition map, superblock, Unicode conversion/comparison/hash, and wrapper block I/O.

## Inline Logic

- `HFSPLUS_SB()` and `HFSPLUS_I()` retrieve private superblock and inode structures.
- `hfsplus_mark_inode_dirty()` sets a specific metadata dirty bit and marks the VFS inode dirty.
- `hfsplus_min_io_size()` returns the larger of the probed minimum I/O size and HFS+ sector size.
- Time helpers convert between HFS+ 1904-based timestamps and Unix timestamps. The comment documents the Linux behavior of treating low on-disk values as future 2040-2106 values due to unsigned 32-bit wrap behavior.
- `hfsplus_btree_lock_class()` maps catalog/extents/attributes B-tree CNIDs to lockdep nested mutex subclasses and `BUG()`s for unexpected tree IDs.
- `is_bnode_offset_valid()` validates a requested B-node offset against node size and logs invalid requests.
- `check_and_correct_requested_length()` clamps B-node read/write lengths that would cross node bounds and logs the correction.

## Dependencies

Includes Linux filesystem, mutex, buffer-head, block-device, and fs-context headers plus `hfsplus_raw.h`. It relies on on-disk HFS+ types and constants supplied through Linux HFS common raw definitions.

## Research Notes

This header is the driver’s main coupling point: most implementation files depend on its structures, flags, and prototypes. The inline B-node bounds helpers are notable because they centralize defensive behavior for corrupted on-disk B-tree offsets/lengths. The header also makes the metadata dirty-bit model explicit: individual metadata files are normal inodes, but dirtiness is tracked with HFS+-specific bits so sync/fsync can flush the correct B-tree or allocation file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_raw.h -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_raw.h

## Role

Thin raw-format include wrapper for HFS+ on-disk structure definitions.

## Contents

- SPDX GPL-2.0 license header.
- Historical comment identifying the file as the HFS+ raw on-disk format header and noting that the format information came from Apple Technote #1150.
- Include guard `_LINUX_HFSPLUS_RAW_H`.
- Includes:
  - `<linux/types.h>`
  - `<linux/hfs_common.h>`

## Research Notes

This file no longer declares raw HFS+ structures directly. Instead, it delegates to common Linux HFS/HFS+ definitions in `linux/hfs_common.h`. Local HFS+ source files include this header to maintain the traditional internal include name while sharing raw structure definitions from the common header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_raw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/inode.c

## Role

Implements HFS+ inode handling and regular-file VFS operations. It connects Linux page-cache/block-mapping helpers to HFS+ extent mapping, manages file open/release semantics, serializes/deserializes HFS+ catalog file/folder records, handles inode attributes, and participates in metadata sync.

## Address-Space and Dentry Operations

- `hfsplus_read_folio()` uses `block_read_full_folio()` with `hfsplus_get_block`.
- `hfsplus_write_begin()` uses `cont_write_begin()` and tracks `HFSPLUS_I(mapping->host)->phys_size`; on failure it calls `hfsplus_write_failed()`.
- `hfsplus_write_failed()` truncates page cache and HFS+ file allocation back to inode size if a failed extending write allocated beyond EOF.
- `hfsplus_bmap()` delegates to `generic_block_bmap()`.
- `hfsplus_direct_IO()` uses `blockdev_direct_IO()` and trims newly instantiated blocks after failed extending writes.
- `hfsplus_writepages()` delegates to `mpage_writepages()`.
- `hfsplus_btree_aops` adds `release_folio = hfsplus_release_folio` for metadata B-tree inodes.
- `hfsplus_aops` is the regular file/symlink mapping ops table.
- `hfsplus_dentry_operations` wires HFS+ Unicode-aware dentry hash and compare functions.

## B-tree Folio Release

`hfsplus_release_folio()` maps the metadata inode number to extents/catalog/attributes B-tree, then checks cached B-nodes that correspond to the folio:

- For node sizes at least page size, it maps one folio to one B-node index.
- For node sizes smaller than a page, it scans all B-node indices within that page.
- It refuses release if a cached node still has a nonzero refcount.
- If safe, it unhashes and frees cached nodes, then tries to free buffers.

This protects B-tree node cache consistency while allowing memory reclaim.

## Permission and Attribute Handling

- `hfsplus_get_perms()` validates catalog permission modes against expected directory/file types, applies mount UID/GID overrides, synthesizes default modes using mount umask when on-disk mode is absent, copies BSD user flags, and maps HFS+ immutable/append root flags to Linux `S_IMMUTABLE` and `S_APPEND`.
- `hfsplus_getattr()` adds `STATX_BTIME`, append/immutable/nodump attributes, and then calls `generic_fillattr()`.
- `hfsplus_fileattr_get()` maps Linux file attribute flags from inode state plus HFS+ nodump user flag.
- `hfsplus_fileattr_set()` rejects FS_XFLAG-style attributes and unsupported flags, maps immutable/append to inode flags, updates nodump in HFS+ user flags, updates ctime, and marks the inode dirty.

## File Operations

`hfsplus_file_operations` provides generic llseek/read/write/mmap/splice operations with HFS+-specific fsync/open/release/ioctl.

- `hfsplus_file_open()` redirects resource-fork opens to the main resource inode for open-count tracking and rejects non-largefile opens of files larger than `MAX_NON_LFS`.
- `hfsplus_file_release()` decrements the open count; when it reaches zero, it truncates allocation and, if the inode is dead, deletes the catalog entry from the hidden directory and deletes the inode.
- `hfsplus_setattr()` handles size changes with direct-I/O wait, contiguous expansion for grows, truncate for shrinks, timestamp updates, and generic attribute copying.
- `hfsplus_file_fsync()` writes data, syncs inode metadata to catalog/extents/attributes/allocation metadata files, prepares and commits the volume header, and issues a block-device flush unless `nobarrier` is set.

## Inode Lifecycle

- `hfsplus_new_inode()` allocates a VFS inode, assigns `next_cnid`, initializes ownership, timestamps, extent cache, open-dir state, resource-fork pointer, size/accounting fields, and operation tables based on mode. It increments file/folder counts, inserts into inode hash, marks dirty, and marks the volume header dirty.
- `hfsplus_delete_inode()` decrements file/folder counts, truncates regular files and symlinks when appropriate, and marks the volume header dirty.
- `hfsplus_inode_read_fork()` copies first extents from an on-disk fork, counts blocks in the first extent record, resets cached extents, sets allocation blocks, physical size, VFS size, `i_blocks`, and clump size.
- `hfsplus_inode_write_fork()` writes first extents, logical size, and allocated block count back into an on-disk fork.

## Catalog Record Serialization

- `hfsplus_cat_read_inode()` reads a catalog record from a B-tree cursor:
  - For `HFSPLUS_FOLDER`, validates entry length, reads folder record, applies permissions, sets link count, sets directory size to `2 + valence`, converts timestamps, stores create date and subfolder count, and installs directory ops.
  - For `HFSPLUS_FILE`, validates entry length, reads file record, chooses data/resource fork, applies permissions, sets regular/symlink/special operation tables, handles hard-link count stored in `permissions.dev`, initializes device special inodes, and converts timestamps.
  - Unexpected record types return `-EIO`.
- `hfsplus_cat_write_inode()` locates the main catalog record, skips unlinked main inodes, then writes updated folder or file metadata:
  - Directories: permissions, access/content/attribute dates, valence, optional subfolder count.
  - Resource fork inodes: resource fork fields only.
  - Regular file/symlink/special: data fork, permissions, file locked flag derived from immutable bits, timestamps.
  - It writes the catalog B-tree and sets catalog dirty bits on both catalog tree inode and target inode.

## Dependencies

Uses block/page-cache helpers, credential/idmap helpers, file attributes, HFS+ xattr declarations, extents, catalog, B-tree, and Unicode dentry callbacks.

## Research Notes

This file is the bridge between HFS+ catalog/fork metadata and Linux inode semantics. The most important behavior is that file data, extents, catalog records, allocation bitmap state, and volume header state are synchronized through separate metadata inodes and HFS+-specific dirty bits. Resource forks are treated specially: many operations redirect accounting or serialization to the main inode/resource relationship rather than treating the resource fork as an independent user-visible inode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/ioctl.c

## Role

Implements HFS+-specific ioctl handling. The only supported ioctl is boot “blessing”.

## Key Functions

- `hfsplus_ioctl_bless(struct file *file, int __user *user_flags)`
  - Requires `CAP_SYS_ADMIN`.
  - Uses the file dentry and inode to access the HFS+ superblock private state and active/backup volume headers.
  - Gets the catalog node ID from `dentry->d_fsdata`.
  - Under `sbi->vh_mutex`, updates `finder_info` in both primary and backup volume headers:
    - `finder_info[0]`: parent directory containing the bootable system.
    - `finder_info[1]`: bootloader CNID, using dentry filesystem data so hard links can bless the hard-link file ID rather than the indirect inode.
    - `finder_info[5]`: OS X system folder, set to the same parent directory value.
  - The `user_flags` pointer is accepted by signature but not read.
- `hfsplus_ioctl(struct file *file, unsigned int cmd, unsigned long arg)`
  - Dispatches `HFSPLUS_IOC_BLESS`.
  - Returns `-ENOTTY` for unsupported ioctl commands.

## Dependencies

Uses capability checks, VFS dentry/inode helpers, user pointer types, and HFS+ volume header state from `hfsplus_fs.h`.

## Research Notes

The ioctl updates in-memory volume headers only. Persistence depends on the normal dirty/sync path that commits volume headers. The design deliberately handles hard links by using catalog/dentry-specific CNID state instead of `inode->i_ino`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/options.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/options.c

## Role

Mount option defaults, parsing, and display for the HFS+ filesystem.

## Supported Options

The parser accepts:

- `creator=<4 chars>`
- `type=<4 chars>`
- `umask=<octal>`
- `uid=<u32>`
- `gid=<u32>`
- `part=<u32>`
- `session=<u32>`
- `nls=<charset>`
- `decompose` / negated form via `fsparam_flag_no`
- `barrier` / negated form via `fsparam_flag_no`
- `force`

## Key Functions

- `hfsplus_fill_defaults(struct hfsplus_sb_info *opts)`
  - Sets creator/type to default `'????'`.
  - Uses current process umask, uid, and gid.
  - Sets partition and session to `-1`.
- `hfsplus_parse_param(struct fs_context *fc, struct fs_parameter *param)`
  - During reconfigure, ignores every option except `force`.
  - Uses `fs_parse()` with `hfs_param_spec`.
  - Validates `creator` and `type` are exactly four characters, then copies raw bytes into 32-bit fields.
  - Sets mount UID/GID and corresponding override flags.
  - Stores partition/session selectors.
  - Loads NLS table once; refuses changing NLS after it is already set.
  - Handles `decompose` negation by setting `HFSPLUS_SB_NODECOMPOSE`; non-negated clears it.
  - Handles `barrier` negation by setting `HFSPLUS_SB_NOBARRIER`; non-negated clears it.
  - Sets `HFSPLUS_SB_FORCE` for `force`.
- `hfsplus_show_options(struct seq_file *seq, struct dentry *root)`
  - Emits non-default creator/type, always emits umask/uid/gid, emits optional part/session/nls, and displays `nodecompose`/`nobarrier` when those flags are set.

## Dependencies

Uses Linux fs-context/fs-parser, NLS loading, seq-file display helpers, mount/user namespace ID display, and HFS+ private superblock state.

## Research Notes

The option model maps positive user-facing `decompose` to clearing the internal `NODECOMPOSE` flag. The internal flag means “do not decompose” in Unicode paths, so code often computes `decompose = !NODECOMPOSE`. `nobarrier` suppresses block-device flushes in fsync/sync paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/options.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/part_tbl.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/part_tbl.c

## Role

Parses classic Mac partition maps to locate an HFS/HFS+ partition start and size.

## On-Disk Structures

- `struct new_pmap`: Apple Partition Map entry with signature, map block count, physical partition start/count, partition name, and partition type.
- `struct old_pmap`: old partition map with signature and up to 42 entries containing start, size, and filesystem ID.

## Constants

- Block offsets:
  - driver descriptor block 0
  - first partition map block 1
  - MDB block 2
- Magic values:
  - driver descriptor `"ER"`
  - old partition map `"TS"`
  - new partition map `"PM"`
  - HFS MDB `"BD"`
  - MFS MDB

## Key Functions

- `hfs_parse_old_pmap()`
  - Scans 42 old map entries.
  - Selects entries with nonzero start/size and FSID `"TFS1"`.
  - Honors requested `sbi->part` if set.
  - Adds the selected entry start to `*part_start` and stores entry size in `*part_size`.
- `hfs_parse_new_pmap()`
  - Uses `pmMapBlkCnt` to walk Apple Partition Map entries.
  - Selects partition type `"Apple_HFS"`.
  - Honors requested `sbi->part`.
  - Advances through entries in the current I/O buffer, submitting additional reads when it crosses `hfsplus_min_io_size(sb)`.
  - Returns `-ENOENT` if no matching entry exists.
- `hfs_part_find()`
  - Allocates a minimum-I/O-size buffer.
  - Reads block `*part_start + HFS_PMAP_BLK`.
  - Dispatches by first 16-bit signature to old or new parser.
  - Frees the buffer and returns parser status.

## Dependencies

Uses `hfsplus_submit_bio()` for raw block reads, `hfsplus_min_io_size()` for safe buffer sizing, and mount option `sbi->part` as the partition selector.

## Research Notes

This parser mutates the caller’s `part_start` by adding the selected partition’s physical start. It treats partition map entries as 512-byte sectors even when the read buffer is larger. New-style maps are limited by the map block count, while old-style maps are fixed at 42 entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/part_tbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/super.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/super.c

## Role

Filesystem registration, mount/fill-super logic, superblock operations, metadata inode loading/writing, volume header commit, sync/remount behavior, and module init/exit for the Linux HFS+ driver.

## Metadata Inode Loading and Writing

- `hfsplus_system_read_inode()` initializes special system inodes from volume-header fork records:
  - extents overflow file
  - catalog file
  - allocation file
  - startup file
  - attributes file
  - B-tree system files get `hfsplus_btree_aops`; allocation gets `hfsplus_aops`.
  - Assigns dummy `S_IFREG` mode so VFS open checks see a valid file type.
- `hfsplus_iget()`
  - Uses `iget_locked()`.
  - Initializes all HFS+ private inode fields on new inodes.
  - Loads user/root catalog inodes through catalog lookup/read.
  - Loads system inodes through `hfsplus_system_read_inode()`.
  - Calls `iget_failed()` on errors.
- `hfsplus_system_write_inode()`
  - Maps system inode CNIDs back to volume-header fork fields.
  - If total size changed, sets backup-header write and marks MDB dirty.
  - Writes fork data and, for B-tree inodes, writes the B-tree under nested tree lock.
- `hfsplus_write_inode()`
  - Flushes dirty extent state first.
  - Dispatches user/root inodes to catalog writeback and system inodes to volume-header fork writeback.
- `hfsplus_evict_inode()`
  - Truncates final pages, clears inode, and handles resource-fork backpointer/iput cleanup.

## Volume Header Commit and Sync

- `hfsplus_prepare_volume_header_for_commit()`
  - Sets Linux HFS+ mount version.
  - Updates modify date.
  - Increments write count.
  - Clears clean-unmounted bit and sets inconsistent bit before write activity.
- `hfsplus_commit_superblock()`
  - Under `vh_mutex` and `alloc_mutex`, writes mutable counters into the primary volume header.
  - Copies primary header to backup header if `HFSPLUS_SB_WRITEBACKUP` was set.
  - Writes primary volume header sector and optionally backup volume header sector through `hfsplus_submit_bio()`.
- `hfsplus_sync_fs()`
  - For wait syncs, explicitly writes catalog, extents, optional attributes, and allocation file mappings.
  - Commits the superblock.
  - Issues block-device flush unless `HFSPLUS_SB_NOBARRIER` is set.
- `hfsplus_mark_mdb_dirty()`
  - Skips read-only mounts.
  - Queues delayed sync work once, using `dirty_writeback_interval * 10`.
- `delayed_sync_fs()`
  - Clears queued state and runs `hfsplus_sync_fs()`.

## Unmount, Statfs, and Reconfigure

- `hfsplus_put_super()`
  - Cancels delayed sync work.
  - On writable mounts, sets modify date, marks clean unmounted, clears inconsistent, and syncs.
  - Drops allocation and hidden directory inodes, closes B-trees, frees volume header buffers.
- `hfsplus_statfs()` fills HFS+ statfs data from allocation counters and block geometry.
- `hfsplus_reconfigure()`
  - Syncs before changing read-only state.
  - Refuses read-write remount if not cleanly unmounted, soft-locked, or journaled unless `force` permits the latter checks according to mount logic.

## Mount Path

`hfsplus_fill_super()` performs the full mount:

1. Initializes locks and delayed work.
2. Loads requested/default NLS; temporarily switches to UTF-8 to find/create the hidden directory.
3. Reads wrapper/volume header with `hfsplus_read_wrapper()`.
4. Validates HFS+ version and copies volume header counters/geometric fields.
5. Checks filesystem size against sector and page-index limits.
6. Sets superblock operations and maximum file size.
7. Applies safety read-only policy for unclean, soft-locked, and journaled volumes unless force permits.
8. Opens extents and catalog B-trees.
9. Opens attributes B-tree if the attributes fork has blocks and sets xattr handlers.
10. Loads allocation file inode.
11. Loads root inode and builds root dentry.
12. Looks up the hidden directory under root.
13. On writable mounts, prepares/commits volume header and creates the hidden directory if absent, including security xattr initialization.
14. Restores the originally requested NLS table.

Error paths unwind hidden dir/root/allocation inode/B-trees/header buffers/NLS state.

## Filesystem Registration and Cache Lifecycle

- Defines `hfsplus_sops`.
- Allocates HFS+ inode cache with `kmem_cache_create()`.
- Initializes attributes tree cache.
- Registers `file_system_type` named `"hfsplus"` with block-device requirement and fs-context operations.
- `hfsplus_kill_super()` calls `kill_block_super()` then defers private superblock free through RCU.
- Exit unregisters filesystem, runs `rcu_barrier()`, destroys attribute cache, and destroys inode cache.

## Dependencies

Uses VFS block filesystem mount helpers, NLS, slab caches, delayed work, B-tree/catalog/allocation/xattr subsystems, wrapper block I/O, and HFS+ volume header structures.

## Research Notes

This file defines the driver’s safety posture: unclean, soft-locked, and journaled volumes are kept read-only unless permitted by `force` where applicable. It also explains why metadata inodes are explicitly written during sync: flusher writeback alone can redirty metadata and miss the latest state. The hidden directory is a Linux-driver implementation detail used for special HFS+ bookkeeping, and mount temporarily forces UTF-8 to find it consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/tables.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/tables.c

## Role

Static Unicode lookup data used by HFS+ filename comparison, case folding, decomposition, and composition. The tables are consumed by `unicode.c`.

## Exported Tables

- `u16 hfsplus_case_fold_table[]`
  - Starts at line 15.
  - Comment says the Unicode case folding table is taken from Apple Technote #1150.
  - Layout:
    - 256-entry high-byte table.
    - Followed by 256-entry subtables for high-byte ranges that have case mappings or ignorable characters.
    - High-byte table value `0` means no mapping/ignorable entries for that high byte.
    - Ignorable characters map to zero.
  - Used by `case_fold()` in `unicode.c`.
- `u16 hfsplus_decompose_table[]`
  - Starts at line 411.
  - Multi-level nibble-indexed decomposition lookup table.
  - Contains base table, per-range pointer tables, and packed decomposition entries.
  - Encodes decomposition lengths in low bits of offsets and points into the trailing decomposed-character data.
  - Used by `hfsplus_decompose_nonhangul()` in `unicode.c`.
- `u16 hfsplus_compose_table[]`
  - Starts at line 1072 and runs to EOF.
  - Trie-like composition table used to convert decomposed sequences back to precomposed Unicode where HFS+ display/export behavior wants composition.
  - Begins with a base table keyed by combining marks and includes a Hangul marker entry.
  - Contains many nested continuation tables for multi-codepoint compositions.
  - Ends with explicit composed results for longer Greek and other multi-mark sequences.
  - Used by `hfsplus_compose_lookup()` and `hfsplus_uni2asc()`.

## Data Coverage

The tables cover:

- ASCII and Latin case mappings.
- Greek, Cyrillic, Armenian, Georgian, fullwidth forms, and other case-folding blocks.
- Canonical decompositions for Latin accented forms, Greek polytonic forms, Indic scripts, Hebrew presentation forms, Japanese voiced/semi-voiced kana, Tibetan combinations, and many multi-mark Latin/Greek sequences.
- Composition support for single and chained combining marks, including Hangul composition marker support handled algorithmically in `unicode.c`.

## Dependencies

Includes only `hfsplus_fs.h`, which declares the external arrays for other HFS+ files.

## Research Notes

This file is generated/static data rather than executable logic. Correctness depends on the lookup formats matching the algorithms in `unicode.c`:

- `case_fold(c)` indexes high byte then low byte.
- `hfsplus_decompose_nonhangul()` walks four 4-bit levels and interprets packed offset/length values.
- `hfsplus_compose_lookup()` binary-searches child tables containing `(codepoint, offset)` pairs.

Any modification to table layout requires coordinated changes in `unicode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/unicode.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/unicode.c

## Role

Implements HFS+ Unicode string comparison, case folding, Unicode-to-local-NLS conversion, local-NLS-to-HFS+ Unicode conversion, canonical decomposition/composition, Linux/HFS+ filename character compatibility mapping, dentry hashing, and dentry comparison.

## Case-Sensitive and Case-Insensitive Comparisons

- `case_fold(u16 c)`
  - Uses `hfsplus_case_fold_table`.
  - Returns folded value, original value if no subtable exists, or zero for ignorable characters.
- `hfsplus_strcasecmp()`
  - Reads big-endian HFS+ Unicode string lengths.
  - Clamps invalid lengths above `HFSPLUS_MAX_STRLEN` and logs correction.
  - Case-folds each code unit, skipping ignorables mapped to zero.
  - Returns normal strcmp-style ordering.
- `hfsplus_strcmp()`
  - Case-sensitive 16-bit code-unit comparison.
  - Also clamps invalid lengths above `HFSPLUS_MAX_STRLEN`.
  - Orders by first differing code unit, then length.

These functions are exported to KUnit with `EXPORT_SYMBOL_IF_KUNIT`.

## Composition and Decomposition

- Hangul constants implement Unicode algorithmic Hangul composition/decomposition.
- `hfsplus_compose_lookup()`
  - Binary-searches composition table entries and returns a continuation table or result pointer.
- `hfsplus_decompose_nonhangul()`
  - Walks the nibble-indexed `hfsplus_decompose_table`.
  - Extracts decomposition size from low two bits of the final encoded offset.
- `hfsplus_try_decompose_hangul()`
  - Implements Unicode Annex #15 Hangul decomposition into L/V/T jamo.
- `decompose_unichar()`
  - Uses Hangul algorithm first, then table-based non-Hangul decomposition.

## HFS+/Linux Compatibility Mapping

HFS+ permits characters that Linux path components cannot represent directly:

- Mac-to-Linux conversion:
  - HFS+ NUL `0x0000` maps to Unicode `0x2400`.
  - HFS+ slash `/` maps to Linux colon `:`.
- Linux-to-Mac conversion:
  - Unicode `0x2400` maps back to NUL.
  - Linux colon `:` maps back to HFS+ slash `/`.
- Xattr names bypass these conversions (`HFS_XATTR_NAME`).

## Unicode to Local Name Conversion

- `hfsplus_uni2asc()`
  - Converts HFS+ Unicode strings to local NLS bytes.
  - Clamps source length to max name length.
  - Composes decomposed HFS+ sequences unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Handles Hangul composition.
  - Applies Mac-to-Linux compatibility mapping for regular names.
  - Uses `nls->uni2char()`, replacing unsupported characters with `?` except for `-ENAMETOOLONG`.
  - Returns output byte length through `len_p`.
- `hfsplus_uni2asc_str()` wraps regular filename conversion with `HFSPLUS_MAX_STRLEN`.
- `hfsplus_uni2asc_xattr_str()` wraps xattr-name conversion with `HFSPLUS_ATTR_MAX_STRLEN`.

## Local Name to HFS+ Unicode Conversion

- `asc2unichar()`
  - Uses `nls->char2uni()`.
  - Replaces conversion failures with `?`.
  - Applies Linux-to-Mac compatibility mapping.
- `hfsplus_asc2uni()`
  - Converts local bytes to HFS+ Unicode.
  - Decomposes characters unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Uses Hangul algorithm and decomposition table.
  - Stops at `max_unistr_len`, writes output length, and returns `-ENAMETOOLONG` if source bytes remain.

## Dentry Hash and Compare

- `hfsplus_hash_dentry()`
  - Converts a Linux qstr through NLS and compatibility mapping.
  - Optionally decomposes codepoints.
  - Optionally case-folds when `HFSPLUS_SB_CASEFOLD` is set.
  - Skips casefold-ignorable zero results.
  - Produces Linux dcache hash via `partial_name_hash()` / `end_name_hash()`.
- `hfsplus_compare_dentry()`
  - Converts both names through the same pipeline.
  - Maintains decomposition iterators for both sides.
  - Applies case folding and skips ignorable folded characters.
  - Returns strcmp-style ordering and length ordering.

## Dependencies

Uses NLS callbacks, KUnit visibility exports, HFS+ Unicode tables, mount flags, and Linux dentry string-hash helpers.

## Research Notes

The `HFSPLUS_SB_NODECOMPOSE` flag is inverted relative to a simple `decompose` boolean: when the bit is clear, conversion/hash/compare decompose or compose as needed; when the bit is set, nodecompose behavior preserves non-decomposed form. This file is also where HFS+’s colon/slash mismatch is normalized for Linux pathnames. Xattr names intentionally skip that mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/unicode_test.c -->
# File Research: sources/os/linux/linux-stable/fs/hfsplus/unicode_test.c

## Role

KUnit test suite for HFS+ Unicode string operations in `unicode.c`.

## Test Harness

- `struct test_mock_string_env`
  - Holds two `hfsplus_unistr` values plus an output/input buffer.
- `setup_mock_str_env()` / `free_mock_str_env()`
  - Allocate/free string test environment and buffer.
- `create_unistr()`
  - Builds a simple HFS+ Unicode string from ASCII bytes.
- `corrupt_unistr()`
  - Sets length to `U16_MAX` to exercise length-clamping behavior.
- `struct test_mock_sb`
  - Minimal mocked superblock, HFS+ superblock info, and NLS table.
- `setup_mock_sb()` / `free_mock_sb()`
  - Initializes mocked NLS and HFS+ flags.
- `test_uni2char()`
  - ASCII-only `uni2char` mock; non-ASCII becomes `?`, no space returns `-ENAMETOOLONG`.
- `test_char2uni()`
  - Single-byte `char2uni` mock.
- `setup_mock_dentry()` and `create_qstr()` support hash/compare tests.

## Covered Functions

The suite covers:

- `hfsplus_strcasecmp()`
- `hfsplus_strcmp()`
- `hfsplus_uni2asc_str()`
- `hfsplus_asc2uni()`
- `hfsplus_hash_dentry()`
- `hfsplus_compare_dentry()`

## Test Categories

- String comparison:
  - identical strings
  - case-insensitive equality
  - case-sensitive inequality
  - lexicographic ordering
  - different lengths
  - empty strings
  - single characters
  - maximum HFS+ length
  - corrupted overlarge lengths
  - special Unicode codepoints
  - embedded NUL code units
- Unicode-to-ASCII/NLS conversion:
  - basic ASCII conversion
  - empty and single-character strings
  - NUL and slash compatibility mapping
  - mixed special characters
  - insufficient/exact/zero output buffers
  - corrupted length correction
  - maximum length strings
  - non-ASCII fallback behavior through mocked NLS
- ASCII/NLS-to-Unicode conversion:
  - basic ASCII
  - explicit source length with embedded NUL tail ignored
  - colon-to-slash mapping
  - repeated special characters
  - max-length and over-length behavior
  - zero max length
  - printable ASCII and embedded NUL
  - nodecompose flag behavior for simple ASCII
- Dentry hashing:
  - nonzero hashes
  - identical strings produce identical hashes
  - casefold disabled/enabled behavior
  - colon/slash normalization
  - consistency and simple distribution checks
  - long names, printable ASCII, embedded NUL
- Dentry comparison:
  - identical strings
  - lexicographic ordering
  - empty/non-empty ordering
  - casefold disabled/enabled behavior
  - colon/slash normalization
  - length parameter behavior
  - nodecompose flag behavior for simple ASCII
  - long strings and end differences
  - embedded NUL
  - combined casefold/nodecompose flag states

## Suite Registration

- `hfsplus_unicode_test_cases[]` registers 27 KUnit cases.
- `hfsplus_unicode_test_suite` is named `"hfsplus_unicode"`.
- Uses `kunit_test_suite()`.
- Module metadata declares GPL license and imports `EXPORTED_FOR_KUNIT_TESTING`.

## Research Notes

The tests use simplified mock NLS behavior, so they validate control flow, flag behavior, buffer handling, and HFS+/Linux special-character mapping more than full real-world UTF-8 conversion. Several tests exercise corrupted length handling introduced in `unicode.c` by expecting clamping rather than crashes or out-of-bounds traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hfsplus/unicode_test.c -->