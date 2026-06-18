# Group Research: group_762_linux_sources_os_linux_linux_fs_hfsplus_hfsplus_fs_h_sources_os_linu_46aba7f8edf1

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux/fs/hfsplus/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/hfsplus_fs.h -->
# File Research: sources/os/linux/linux/fs/hfsplus/hfsplus_fs.h

## Role

Central private header for the Linux HFS+ driver. It defines in-memory B-tree, superblock, inode, finder, and readdir state; mount/runtime flags; compatibility aliases; ioctl constants; cross-file function prototypes; and small inline helpers used throughout the HFS+ implementation.

## Key Definitions

- `struct hfs_btree`: in-memory HFS+ B-tree descriptor with backing inode, key comparator, root/leaf/free-node counters, node geometry, tree mutex, pages-per-node metadata, and a 256-bucket hash of cached `hfs_bnode` objects.
- `struct hfs_bnode`: cached B-tree node with tree pointer, node IDs/linkage, record count, node type/height, lock/error/new/dirty/deleted bits, wait queue, refcount, page offset, and flexible page array.
- `struct hfsplus_sb_info`: filesystem private superblock state derived from the on-disk volume header plus runtime state:
  - active and backup volume header buffers;
  - extents, catalog, and attributes B-trees;
  - allocation file and hidden directory inodes;
  - NLS table, partition/session layout, block offset, minimum I/O size, allocation geometry;
  - mutable `free_blocks`, `next_cnid`, file/folder counts guarded by `alloc_mutex` and `vh_mutex`;
  - creator/type defaults, umask/uid/gid overrides, mount flags, delayed sync work, and RCU release.
- `struct hfsplus_inode_info`: HFS+-private inode state for resource forks, extent caches, create date, hard-link ID, HFS+/BSD flags, subfolder count, open-directory tracking, physical size, and embedded VFS inode.
- `struct hfs_find_data`: B-tree search cursor carrying caller-provided keys plus located node, record number, key offset/length, and entry offset/length.
- `struct hfsplus_readdir_data`: directory iteration state linked through the inode-private open directory list.
- Runtime flags include backup-header write, nodecompose, force, HFSX, casefold, nobarrier, uid override, and gid override.
- Inode dirty flags distinguish catalog, extent, allocation-file, and attributes-tree metadata dirtiness.
- `HFSPLUS_IOC_BLESS` defines the HFS+-specific boot-blessing ioctl.

## Cross-File API Surface

The header exposes the driver’s internal subsystem contracts:

- Attributes: key comparison/building, lookup, create/delete/replace, delete-all, allocation/free of attribute entries, and cache lifecycle.
- Bitmap/allocation: allocation-block allocate/free.
- B-tree and B-node: tree open/close/write, B-tree bitmap reserve/alloc/free, node I/O, node hash lookup, node create/free/get/put, and node bounds helpers.
- B-record/B-find: record length/key helpers, insert/remove/read/goto, cursor init/exit, and record search strategies.
- Catalog: key comparison/building, permission serialization, catalog lookup/create/delete/rename.
- Extents: key comparison, extent writeback, block mapping, fork free, file extend, and file truncate.
- Inode/VFS: address-space ops, dentry ops, inode creation/deletion, fork read/write, catalog inode read/write, getattr, fsync, and file attributes.
- Options, partition map, superblock commit/dirty handling, Unicode conversion/comparison/hash, and wrapper block I/O.

## Inline Logic

- `HFSPLUS_SB()` and `HFSPLUS_I()` recover private superblock and inode structures.
- `hfsplus_mark_inode_dirty()` sets an HFS+-specific metadata dirty bit and marks the VFS inode dirty.
- `hfsplus_min_io_size()` returns the larger of probed minimum I/O size and the HFS+ sector size.
- `hfsplus_cat_thread_size()` computes variable-length catalog-thread record size.
- Time helpers convert between HFS+ 1904-based timestamps and Unix timestamps. The comment documents Linux’s unsigned-wrap behavior that maps low on-disk values into the 2040-2106 range.
- `hfsplus_btree_lock_class()` maps catalog/extents/attributes B-tree CNIDs to lockdep nested mutex subclasses and `BUG()`s for unexpected tree IDs.
- `is_bnode_offset_valid()` validates a B-node offset against node size and logs corrupt requests.
- `check_and_correct_requested_length()` clamps B-node read/write length at node bounds and logs the correction.

## Dependencies

Includes Linux filesystem, mutex, buffer-head, block-device, and fs-context headers plus `hfsplus_raw.h`. It relies on common on-disk HFS/HFS+ definitions from `linux/hfs_common.h` via `hfsplus_raw.h`.

## Research Notes

This header is the HFS+ driver’s main coupling point. Most implementation files depend on its structure layouts, dirty-bit model, and prototypes. The inline B-node bounds helpers are security-relevant defensive code because corrupted on-disk B-tree offsets and lengths are checked centrally before node I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/hfsplus_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/hfsplus_raw.h -->
# File Research: sources/os/linux/linux/fs/hfsplus/hfsplus_raw.h

## Role

Thin raw-format include wrapper for HFS+ on-disk structure definitions.

## Contents

- SPDX GPL-2.0 license header.
- Historical comment identifying the file as the HFS+ raw on-disk format header and noting Apple Technote #1150 as the source for format information.
- Include guard `_LINUX_HFSPLUS_RAW_H`.
- Includes:
  - `<linux/types.h>`
  - `<linux/hfs_common.h>`

## Research Notes

This file no longer declares raw HFS+ structures directly. It preserves the traditional internal include name while delegating actual raw format definitions to the common Linux HFS/HFS+ header.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/hfsplus_raw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/inode.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/inode.c

## Role

Implements HFS+ inode handling and regular-file VFS operations. It connects Linux page-cache/block-mapping helpers to HFS+ extent mapping, manages file open/release semantics, serializes and deserializes catalog file/folder records, maps HFS+ permissions and user flags to Linux inode/file attributes, and participates in metadata sync.

## Address-Space and Dentry Operations

- `hfsplus_read_folio()` uses `block_read_full_folio()` with `hfsplus_get_block`.
- `hfsplus_write_begin()` uses `cont_write_begin()` and tracks `HFSPLUS_I(mapping->host)->phys_size`; failed extending writes call `hfsplus_write_failed()`.
- `hfsplus_write_failed()` truncates page cache and HFS+ file allocation back to `i_size` if a failed write allocated beyond EOF.
- `hfsplus_bmap()` delegates to `generic_block_bmap()`.
- `hfsplus_direct_IO()` delegates to `blockdev_direct_IO()` and trims blocks after failed extending direct writes.
- `hfsplus_writepages()` delegates to `mpage_writepages()`.
- `hfsplus_btree_aops` is used by metadata B-tree inodes and adds `release_folio = hfsplus_release_folio`.
- `hfsplus_aops` is used by regular file and symlink data mappings.
- `hfsplus_dentry_operations` wires Unicode-aware HFS+ dentry hash and compare functions.

## B-tree Folio Release

`hfsplus_release_folio()` maps metadata inode numbers to the corresponding extents, catalog, or attributes tree. It then checks cached B-nodes associated with the folio:

- for node sizes at least page size, it maps one folio to one B-node index;
- for node sizes smaller than a page, it scans all node indices inside the page;
- it refuses release if a cached node still has a nonzero refcount;
- if safe, it unhashes and frees cached nodes, then calls `try_to_free_buffers()`.

This protects B-tree cache consistency during memory reclaim.

## Permission and Attribute Handling

- `hfsplus_get_perms()` validates catalog permission modes against directory/file expectations, applies mount UID/GID overrides, synthesizes default modes with mount umask when on-disk mode is absent, copies BSD user flags, and maps HFS+ immutable/append root flags to Linux `S_IMMUTABLE` and `S_APPEND`.
- `hfsplus_getattr()` adds `STATX_BTIME`, append/immutable/nodump attributes, and then calls `generic_fillattr()`.
- `hfsplus_fileattr_get()` reports immutable, append, nodump, and, in this `linux` tree, `FS_CASEFOLD_FL` when the superblock has `HFSPLUS_SB_CASEFOLD` set.
- `hfsplus_fileattr_set()` rejects FS_XFLAG-style attributes and unsupported flags, maps immutable/append to inode flags, updates HFS+ nodump user flags, updates ctime, and marks the inode dirty. It accepts `FS_CASEFOLD_FL` as a no-op only when the mounted volume is already casefolded, so read-modify-write tools such as `chattr` can round-trip attributes without trying to change a mount-time HFS+ property.

## File Operations

`hfsplus_file_operations` provides generic llseek/read/write/mmap/splice operations plus HFS+-specific fsync/open/release/ioctl.

- `hfsplus_file_open()` redirects resource-fork opens to the main resource inode for open-count tracking and rejects non-largefile opens for files larger than `MAX_NON_LFS`.
- `hfsplus_file_release()` decrements the open count; when it reaches zero, it truncates allocation and, for dead inodes, deletes the catalog entry from the hidden directory and deletes the inode.
- `hfsplus_setattr()` handles size changes with direct-I/O wait, contiguous expansion for grows, truncate for shrinks, timestamp updates, generic attribute copying, and inode dirtiness.
- `hfsplus_file_fsync()` writes data, syncs inode metadata to catalog/extents/attributes/allocation metadata files, prepares and commits the volume header, and issues a block-device flush unless `nobarrier` is set.

## Inode Lifecycle

- `hfsplus_new_inode()` allocates a VFS inode, assigns `next_cnid`, initializes owner/timestamps/extent cache/open-dir state/resource-fork pointer/accounting fields, selects operations based on mode, increments file/folder counts, inserts into the inode hash, marks dirty, and marks the volume header dirty.
- `hfsplus_delete_inode()` decrements file/folder counts, truncates regular files and symlinks when appropriate, and marks the volume header dirty.
- `hfsplus_inode_read_fork()` copies first extents from an on-disk fork, counts blocks in the first extent record, resets cached extents, sets allocation blocks, physical size, VFS size, `i_blocks` accounting, and clump size.
- `hfsplus_inode_write_fork()` writes first extents, logical size, and allocated block count back into an on-disk fork.

## Catalog Record Serialization

- `hfsplus_cat_read_inode()` reads a catalog record from a B-tree cursor:
  - `HFSPLUS_FOLDER`: validates entry length, reads folder record, applies permissions, sets link count, sets directory size to `2 + valence`, converts timestamps, stores create date and optional subfolder count, and installs directory ops.
  - `HFSPLUS_FILE`: validates entry length, reads file record, chooses data or resource fork, applies permissions, sets regular/symlink/special operation tables, handles hard-link count stored in `permissions.dev`, initializes special inodes, and converts timestamps.
  - unexpected record types return `-EIO`.
- `hfsplus_cat_write_inode()` locates the main catalog record, skips unlinked main inodes, and writes updated folder/file metadata:
  - directories: permissions, access/content/attribute dates, valence, optional subfolder count;
  - resource fork inodes: resource fork fields only;
  - regular file/symlink/special: data fork, permissions, file locked flag derived from immutable bits, timestamps.
  - it writes the catalog B-tree and marks catalog dirty bits on both catalog-tree inode and target inode.

## Dependencies

Uses block/page-cache helpers, direct-I/O helpers, credential/idmap helpers, file-attribute APIs, HFS+ xattr declarations, extents, catalog, B-tree, and Unicode dentry callbacks.

## Research Notes

This file is the bridge between HFS+ catalog/fork metadata and Linux inode semantics. File data, extents, catalog records, allocation bitmap state, and volume header state are synchronized through separate metadata inodes plus HFS+-specific dirty bits. Resource forks are not treated as fully independent user-visible files; open counts and serialization route through the main inode/resource relationship.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/ioctl.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/ioctl.c

## Role

Implements HFS+-specific ioctl handling. The only supported ioctl is boot “blessing”.

## Key Functions

- `hfsplus_ioctl_bless(struct file *file, int __user *user_flags)`
  - Requires `CAP_SYS_ADMIN`.
  - Uses the file dentry and inode to reach the HFS+ superblock private state and active/backup volume headers.
  - Reads the bootloader CNID from `dentry->d_fsdata`.
  - Under `sbi->vh_mutex`, updates `finder_info` in both primary and backup volume headers:
    - `finder_info[0]`: parent directory containing the bootable system;
    - `finder_info[1]`: bootloader CNID, using dentry filesystem data so hard links bless the hard-link file ID rather than the indirect inode;
    - `finder_info[5]`: OS X system folder, set to the same parent directory value.
  - The `user_flags` pointer is accepted by signature but not read.
- `hfsplus_ioctl(struct file *file, unsigned int cmd, unsigned long arg)`
  - Dispatches `HFSPLUS_IOC_BLESS`.
  - Returns `-ENOTTY` for unsupported ioctl commands.

## Dependencies

Uses capability checks, VFS dentry/inode helpers, user pointer types, and HFS+ volume header state from `hfsplus_fs.h`.

## Research Notes

The ioctl updates in-memory volume header copies only. Persistence depends on normal HFS+ superblock commit/sync paths writing the primary and backup headers later.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/options.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/options.c

## Role

Parses, initializes, and displays HFS+ mount options through the Linux `fs_context` parser interface.

## Supported Parameters

The `hfs_param_spec[]` table accepts:

- string options: `creator`, `type`, `nls`;
- numeric options: octal `umask`, `uid`, `gid`, `part`, `session`;
- negatable flags: `decompose` / `nodecompose`, `barrier` / `nobarrier`;
- flag: `force`.

`creator` and `type` must be exactly four bytes and default to `HFSPLUS_DEF_CR_TYPE` (`'????'`).

## Key Functions

- `hfsplus_fill_defaults(struct hfsplus_sb_info *opts)`
  - Sets default creator/type, current umask, current UID/GID, and `part = session = -1`.
  - Returns immediately for a null options pointer.
- `hfsplus_parse_param(struct fs_context *fc, struct fs_parameter *param)`
  - During reconfigure/remount, ignores all options except `force`.
  - Uses `fs_parse()` against `hfs_param_spec`.
  - Validates fixed-length creator/type strings.
  - Stores uid/gid values and sets `HFSPLUS_SB_UID` / `HFSPLUS_SB_GID`.
  - Loads `nls` once and rejects attempts to change an already loaded NLS mapping.
  - Handles `nodecompose` via negated `decompose`; negated `decompose` sets `HFSPLUS_SB_NODECOMPOSE`, while plain `decompose` clears it.
  - Handles `nobarrier` via negated `barrier`; negated `barrier` sets `HFSPLUS_SB_NOBARRIER`, while plain `barrier` clears it.
  - Sets `HFSPLUS_SB_FORCE` for `force`.
- `hfsplus_show_options(struct seq_file *seq, struct dentry *root)`
  - Emits non-default creator/type, umask/uid/gid, partition/session, loaded NLS charset, `nodecompose`, and `nobarrier`.

## Dependencies

Uses Linux `fs_parser`, `fs_context`, NLS loading, seq-file option display, current credentials/umask helpers, and HFS+ superblock flags.

## Research Notes

Option parsing feeds directly into mount-time behavior in `super.c` and Unicode behavior in `unicode.c`. `force` is intentionally the only effective remount option; other parsed mount fields are immutable for an existing mount.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/options.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/part_tbl.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/part_tbl.c

## Role

Parses legacy and new-style Macintosh partition maps to locate an HFS/HFS+ partition within a block device.

## On-Disk Structures and Constants

- Block offsets:
  - `HFS_DD_BLK`: driver descriptor block.
  - `HFS_PMAP_BLK`: first partition map block.
  - `HFS_MDB_BLK`: HFS MDB block within a partition.
- Magic values:
  - `HFS_DRVR_DESC_MAGIC` (`"ER"`), `HFS_OLD_PMAP_MAGIC` (`"TS"`), `HFS_NEW_PMAP_MAGIC` (`"PM"`), HFS MDB (`"BD"`), and MFS MDB.
- `struct new_pmap`: packed new-style partition map entry with signature, map count, physical start/count, partition name, and partition type.
- `struct old_pmap`: packed old-style partition map with a signature and 42 entries containing start, size, and filesystem ID.

## Key Functions

- `hfs_parse_old_pmap()`
  - Scans 42 old-map entries.
  - Accepts entries with nonzero start/size, filesystem ID `"TFS1"`, and matching `sbi->part` if a specific partition was requested.
  - Adds the partition start to the caller-provided base and writes the partition size.
  - Returns `-ENOENT` when no matching partition exists.
- `hfs_parse_new_pmap()`
  - Uses `pmMapBlkCnt` as the map size.
  - Scans contiguous 512-byte map entries looking for `pmPartType == "Apple_HFS"` and optional matching partition index.
  - Reads additional map sectors through `hfsplus_submit_bio()` when the scan steps beyond the current minimum-I/O buffer.
  - Returns `-ENOENT` if no matching HFS partition is found or the signature chain stops.
- `hfs_part_find()`
  - Allocates a `hfsplus_min_io_size()` buffer.
  - Reads the first partition-map block at `*part_start + HFS_PMAP_BLK`.
  - Dispatches to old or new map parsing by 16-bit signature.
  - Frees the buffer and returns parser status.

## Dependencies

Uses `kmalloc/kfree`, HFS+ wrapper bio reads, endian helpers, minimum I/O sizing from `hfsplus_fs.h`, and `sbi->part` selection.

## Research Notes

The parser mutates `*part_start` by adding the selected partition’s physical start. Callers must pass a base sector and expect in-place update to the selected HFS/HFS+ partition. The code recognizes HFS partitions by legacy Mac partition maps rather than Linux partition infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/part_tbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/super.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/super.c

## Role

Implements HFS+ superblock lifecycle, filesystem registration, mount/open of metadata objects, root creation, volume header commit/sync, statfs, remount/reconfigure checks, inode cache management, and teardown.

## Inode Loading and Writeback

- `hfsplus_system_read_inode()` reads system-file forks from the active volume header:
  - extents and catalog files get `hfsplus_btree_aops`;
  - allocation file gets `hfsplus_aops`;
  - startup and attributes files are read from their volume-header fork fields;
  - system inodes receive dummy `S_IFREG` mode so VFS open checks see a valid file type.
- `hfsplus_iget()` initializes HFS+ inode-private fields for new inodes, then either:
  - looks up user/root CNIDs in the catalog B-tree and calls `hfsplus_cat_read_inode()`, or
  - reads special system inodes from volume-header forks.
- `hfsplus_system_write_inode()` writes system inode fork state back to the volume header, marks the backup header dirty when sizes change, and writes associated B-trees under the correct nested lock class.
- `hfsplus_write_inode()` writes dirty extents first, then serializes user/root inodes to the catalog or system inodes to the volume header.
- `hfsplus_evict_inode()` truncates final pages, clears the VFS inode, and unlinks resource-fork inode relationships.

## Superblock Commit and Sync

- `hfsplus_commit_superblock()`
  - Under `vh_mutex` and `alloc_mutex`, copies `free_blocks`, `next_cnid`, `folder_count`, and `file_count` into the active volume header.
  - If `HFSPLUS_SB_WRITEBACKUP` is set, copies active header contents to the backup header and writes both primary and backup headers.
  - Uses `hfsplus_submit_bio()` to write the primary header at `part_start + HFSPLUS_VOLHEAD_SECTOR` and backup header at `part_start + sect_count - 2`.
- `hfsplus_sync_fs()`
  - For synchronous syncs, explicitly writes catalog, extents, optional attributes, and allocation-file mappings.
  - Commits the superblock and issues `blkdev_issue_flush()` unless `HFSPLUS_SB_NOBARRIER` is set.
- `delayed_sync_fs()` runs queued delayed superblock sync work and reports errors.
- `hfsplus_mark_mdb_dirty()` queues delayed sync work for writable mounts, using `dirty_writeback_interval * 10`.
- `hfsplus_prepare_volume_header_for_commit()` updates mount version, modify date, write count, clears the clean-unmount bit, and sets the inconsistent bit before commit.

## Mount and Root Setup

`hfsplus_fill_super()` performs mount setup:

- initializes allocation/header locks, delayed work, and work lock;
- loads default NLS, falling back from UTF-8 to default NLS when needed;
- temporarily switches to UTF-8 to locate the hidden directory;
- reads the HFS+ wrapper/volume header via `hfsplus_read_wrapper()`;
- validates volume version and caches total/free blocks, next CNID, file/folder counts, and data/resource clump blocks;
- checks filesystem size against sector and page-index limits;
- installs `hfsplus_sops` and `MAX_LFS_FILESIZE`;
- forces read-only for unclean, soft-locked, or journaled volumes unless allowed by `force` rules;
- opens extents and catalog B-trees, optionally opens the attributes B-tree, installs xattr handlers, and loads the allocation file inode;
- loads root inode, sets default HFS+ dentry ops, and creates `sb->s_root`;
- finds or creates the hidden directory used for hard-link/private file handling;
- on writable mounts, prepares/commits the volume header and initializes security on a newly created hidden directory when supported;
- unwinds all allocated/opened resources on failure.

## Super Operations and Reconfigure

- `hfsplus_sops` wires inode allocation/free, writeback, eviction, put_super, sync, statfs, and show_options.
- `hfsplus_put_super()` cancels delayed sync, marks writable volumes cleanly unmounted and not inconsistent, syncs, drops metadata inodes/B-trees, frees header buffers, and leaves `sbi` for RCU-delayed free.
- `hfsplus_statfs()` reports HFS+ magic, block size/count/free count, a synthetic file count, free CNIDs, fsid, and maximum name length.
- `hfsplus_reconfigure()` syncs before remount and blocks read-write transition for unclean, locked, or journaled volumes unless `force` permits the journaled/locked checks.

## Module and Cache Lifecycle

- `hfsplus_init_fs_context()` allocates and initializes `hfsplus_sb_info`, fills defaults for initial mounts, and installs `hfsplus_context_ops`.
- `hfsplus_get_tree()` mounts via `get_tree_bdev()`.
- `hfsplus_free_fc()` frees unmounted context state.
- `hfsplus_kill_super()` calls `kill_block_super()` and schedules `sbi` for RCU-delayed cleanup.
- `init_hfsplus_fs()` creates the inode cache, creates the attributes-tree cache, and registers the filesystem.
- `exit_hfsplus_fs()` unregisters the filesystem, waits for RCU, destroys the attributes cache, and destroys the inode cache.

## Dependencies

Uses Linux module/init, VFS, block-device, page-cache, fs_context, NLS, slab, xattr, HFS+ B-tree/catalog/extent/allocation helpers, and wrapper volume-header I/O.

## Research Notes

This file coordinates the filesystem-wide dirty state: special metadata files are ordinary inodes for writeback, but HFS+ must explicitly write the B-tree/allocation mappings and commit the volume header to keep on-disk state consistent. The mount path is conservative for journaled or unclean volumes because this driver does not replay HFS+ journals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/tables.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/tables.c

## Role

Provides static Unicode lookup tables used by `unicode.c` for HFS+ name comparison, case folding, decomposition, and composition.

## Exported Data

- `u16 hfsplus_case_fold_table[]` (starts at line 15)
  - Case folding table from Apple Technote #1150.
  - Layout is a 256-entry high-byte table followed by 256-entry subtables.
  - A high-byte entry of zero means no case mapping or ignorable characters for that block.
  - Ignorable characters map to zero.
  - Used by `case_fold()` in `unicode.c`, then by case-insensitive catalog comparison, dentry hashing, and dentry comparison.
- `u16 hfsplus_decompose_table[]` (starts at line 411)
  - Multi-level decomposition lookup table for non-Hangul Unicode characters.
  - Encodes top-level and nested table offsets followed by decomposition sequences.
  - Used by `hfsplus_decompose_nonhangul()` in `unicode.c`.
- `u16 hfsplus_compose_table[]` (starts at line 1072)
  - Composition lookup table for recomposing decomposed HFS+ Unicode sequences when presenting names through Linux.
  - Includes a base table of combining marks, nested lookup records, a Hangul marker (`0xffff`), and many direct composed-codepoint leaves.
  - Used by `hfsplus_compose_lookup()` and `hfsplus_uni2asc()`.

## Integration

The file includes only `hfsplus_fs.h`, which declares the arrays as externs for other HFS+ files. There is no executable code in this file; all behavior is in `unicode.c`.

## Research Notes

These tables are part of HFS+ on-disk compatibility rather than generic modern Unicode normalization. Changes here would affect catalog ordering, case-insensitive lookup behavior, dentry hash stability, and Linux-visible filename conversion. Because HFS+ normalization historically follows Apple’s fixed Unicode behavior, these tables should be treated as format data, not tunable locale policy.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/unicode.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/unicode.c

## Role

Implements HFS+ Unicode string comparison, case folding, Linux/HFS+ filename character compatibility conversions, Unicode composition/decomposition, conversion between HFS+ Unicode names and Linux byte strings through NLS, and dentry hash/compare hooks.

## Case-Sensitive and Case-Insensitive Comparison

- `case_fold(u16 c)`
  - Looks up a character through `hfsplus_case_fold_table`.
  - Returns folded character, original character when no subtable exists, or zero for ignorable characters.
- `hfsplus_strcasecmp()`
  - Compares `hfsplus_unistr` values after case folding.
  - Clamps corrupt lengths greater than `HFSPLUS_MAX_STRLEN` and logs correction.
  - Skips case-folded zero/ignorable characters.
  - Returns strcmp-like `-1`, `0`, or `1`.
- `hfsplus_strcmp()`
  - Compares `hfsplus_unistr` values as unsigned 16-bit code units.
  - Also clamps overlong lengths and logs correction.
  - Returns lexicographic order with length as tiebreaker.

The string comparison functions are exported under `EXPORT_SYMBOL_IF_KUNIT` for KUnit tests.

## Composition and Decomposition

- Hangul constants implement Unicode decomposition/composition ranges.
- `hfsplus_compose_lookup()` binary-searches nested composition records in `hfsplus_compose_table`.
- `hfsplus_decompose_nonhangul()` walks `hfsplus_decompose_table` levels by nibbles to find non-Hangul decomposition sequences.
- `hfsplus_try_decompose_hangul()` implements Unicode Annex #15 Hangul decomposition into L/V/T jamo.
- `decompose_unichar()` tries Hangul first, then non-Hangul table decomposition.

## Linux/HFS+ Character Compatibility

HFS+ permits characters that conflict with Linux path/string conventions:

- `hfsplus_mac2linux_compatibility_check()` maps HFS+ NUL to U+2400 and HFS+ slash (`/`) to Linux colon (`:`) for regular names. It bypasses this conversion for xattr names.
- `hfsplus_linux2mac_compatibility_check()` maps Linux U+2400 back to NUL and Linux colon back to HFS+ slash for regular names. It bypasses this conversion for xattr names.
- `asc2unichar()` converts one Linux byte sequence to a Unicode character through the mount NLS table, substitutes `?` on conversion failure, then applies Linux-to-HFS+ compatibility mapping.

## Name Conversion

- `hfsplus_uni2asc()`
  - Converts HFS+ Unicode names to Linux byte strings.
  - Uses the mount NLS `uni2char` callback.
  - Clamps overlong HFS+ string lengths to the supplied maximum.
  - Composes decomposed sequences unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Special-cases Hangul composition.
  - Converts HFS+ slash/NUL for regular names.
  - Returns `-ENAMETOOLONG` when the output buffer is too small; otherwise substitutes `?` for conversion failures.
- `hfsplus_uni2asc_str()` converts normal HFS+ strings with `HFSPLUS_MAX_STRLEN`.
- `hfsplus_uni2asc_xattr_str()` converts attribute strings with `HFSPLUS_ATTR_MAX_STRLEN` and xattr-name conversion rules.
- `hfsplus_asc2uni()`
  - Converts Linux byte strings to HFS+ Unicode strings through the mount NLS `char2uni` callback.
  - Decomposes characters unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Handles Hangul and table-driven non-Hangul decomposition.
  - Stops at `max_unistr_len` and returns `-ENAMETOOLONG` if input remains.

## Dentry Hooks

- `hfsplus_hash_dentry()`
  - Converts each byte sequence to Unicode, applies Linux-to-HFS+ compatibility mapping, optionally decomposes, optionally casefolds, skips ignorable folded characters, and feeds 16-bit values into Linux name hashing.
  - Writes the final hash into `str->hash`.
- `hfsplus_compare_dentry()`
  - Converts both names to Unicode streams, optionally decomposes and casefolds each side, skips ignorable folded characters, and returns lexicographic order.
  - Uses remaining byte lengths as the final tiebreaker.

Both dentry hooks are exported for KUnit visibility.

## Dependencies

Uses NLS conversion callbacks, Linux dentry/string hashing helpers, KUnit visibility export macros, HFS+ raw constants, and the three Unicode tables from `tables.c`.

## Research Notes

The Unicode implementation is central to correctness for catalog lookup and Linux dcache behavior. HFS+ filenames are stored in a historical decomposed form and may be case-sensitive or case-insensitive depending on volume flags. The `nodecompose` flag inverts the default conversion behavior: without it, Linux-facing conversion tries to compose decomposed names; with it, node names remain decomposed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/unicode_test.c -->
# File Research: sources/os/linux/linux/fs/hfsplus/unicode_test.c

## Role

KUnit test suite for HFS+ Unicode string operations. It tests string comparison, Unicode-to-Linux conversion, Linux-to-Unicode conversion, dentry hashing, dentry comparison, special character mapping, buffer limits, corrupted lengths, and casefold/decomposition flag behavior.

## Test Fixtures and Helpers

- `struct test_mock_string_env` bundles two `hfsplus_unistr` values, a scratch buffer, and buffer size.
- `setup_mock_str_env()` and `free_mock_str_env()` allocate/free string test state.
- `create_unistr()` builds a simple big-endian HFS+ Unicode string from ASCII bytes.
- `corrupt_unistr()` sets length to `U16_MAX` to exercise defensive clamping.
- `struct test_mock_sb` embeds a mock `nls_table`, `hfsplus_sb_info`, and `super_block`.
- `setup_mock_sb()` initializes mock UTF-8 NLS state, attaches `sb.s_fs_info`, and clears `HFSPLUS_SB_NODECOMPOSE` and `HFSPLUS_SB_CASEFOLD`.
- `test_uni2char()` emits ASCII characters directly and `?` for non-ASCII.
- `test_char2uni()` converts one input byte to a Unicode code point.
- `setup_mock_dentry()` assigns the mock superblock to a static dentry.
- `create_qstr()` builds qstrs for hash/compare tests.

## Covered Behavior

- `hfsplus_strcasecmp_test()`
  - Identical strings, case-insensitive equality, ordering, prefix/length ordering, empty strings, single characters, maximum-length strings, mid-string differences, and corrupted overlong lengths.
- `hfsplus_strcmp_test()`
  - Case-sensitive equality/ordering, prefix/length ordering, empty strings, maximum-length strings, mid-string differences, and corrupted overlong lengths.
- `hfsplus_unicode_edge_cases_test()` and `hfsplus_unicode_boundary_test()`
  - Non-ASCII code units, embedded NUL code units, maximum length, last-character differences, zero-length strings, and single-character-vs-empty comparisons.
- `hfsplus_uni2asc_*` tests
  - Basic ASCII conversion, empty/single-character conversion, HFS+ NUL and slash mapping, mixed special characters, buffer-too-small handling, exact-size buffers, zero-length buffers, corrupted HFS+ lengths, maximum-length strings, and non-ASCII fallback behavior in the mock NLS table.
- `hfsplus_asc2uni_*` tests
  - Basic ASCII conversion, explicit lengths with embedded NULs, colon-to-slash mapping, multiple special characters, exact/excess/zero output limits, partial input lengths, printable ASCII, and decomposition flag behavior for simple ASCII.
- `hfsplus_hash_dentry_*` tests
  - Basic hashing, identical-string stability, empty/single-character hashing, casefold disabled/enabled behavior, colon/slash equivalence, decomposition flag behavior, consistency across repeated hashes, different-string hash differences, long names, printable punctuation, and embedded NULs.
- `hfsplus_compare_dentry_*` tests
  - Identical/different strings, empty-string ordering, casefold disabled/enabled behavior, colon/slash equivalence, length differences, decomposition flag behavior, long names, single-character differences, embedded NULs, printable punctuation, and combined casefold/decomposition flag behavior.

## Suite Registration

- `hfsplus_unicode_test_cases[]` registers 27 KUnit cases.
- `hfsplus_unicode_test_suite` names the suite `hfsplus_unicode`.
- `kunit_test_suite()` registers the suite.
- Module metadata describes the suite, uses GPL licensing, and imports the `EXPORTED_FOR_KUNIT_TESTING` namespace.

## Dependencies

Includes KUnit, NLS, dcache, stringhash, and `hfsplus_fs.h`. It depends on KUnit-visible exports from `unicode.c`.

## Research Notes

The tests are focused on algorithmic Unicode behavior with mock NLS callbacks rather than mounting real HFS+ media. They provide regression coverage for edge cases that can affect catalog lookup and dcache consistency: overlong HFS+ string lengths, casefold-dependent equality, colon/slash compatibility mapping, embedded NUL handling, and output length failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hfsplus/unicode_test.c -->