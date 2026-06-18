# subset-b-005672 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_fs.h -->
# sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_fs.h

## Purpose
`hfsplus_fs.h` is the central private interface for the HFS+ filesystem driver. It ties the Linux VFS-facing code to HFS+ on-disk structures from `hfsplus_raw.h`/`hfs_common.h`, declares the in-memory superblock, inode, B-tree, and search-state types, exposes cross-file function prototypes, and defines helper macros for dirty metadata, timestamp conversion, B-tree locking, and bounded B-node access.

## Important APIs, types, and functions
The main runtime types are `struct hfsplus_sb_info`, `struct hfsplus_inode_info`, `struct hfs_btree`, `struct hfs_bnode`, `struct hfs_find_data`, and `struct hfsplus_readdir_data`. `HFSPLUS_SB()` and `HFSPLUS_I()` recover private state from VFS objects. B-tree state includes catalog/extents/attributes tree identifiers, root/leaf/node counters, node size geometry, hash-cache state, and `tree_lock`; B-node state tracks record count, type, height, links, lock/error/new/dirty/deleted flags, refcount, and backing pages.

The header publishes the filesystem's internal API surface: attribute-tree functions, bitmap alloc/free, B-tree open/write/reserve/allocation, B-node read/write/copy/move/hash/refcount helpers, B-record search/insert/remove helpers, catalog compare/build/create/delete/rename helpers, extent mapping/truncation, inode read/write/fsync/fileattr helpers, mount option parsing/showing, partition-map probing, superblock commit, Unicode conversion/hash/compare helpers, and wrapper I/O helpers.

Inline helpers include `hfsplus_mark_inode_dirty()`, `hfsplus_min_io_size()`, `hfsplus_cat_thread_size()`, HFS+ timestamp conversions, `hfsplus_btree_lock_class()`, `is_bnode_offset_valid()`, and `check_and_correct_requested_length()`.

## Control flow
Most implementation files include this header and communicate through its structures. Mount setup fills `hfsplus_sb_info`, opens B-trees, and creates metadata inodes. VFS inode operations use `hfsplus_inode_info` to cache first and recently-used extents, resource-fork links, creation time, BSD flags, open-directory state, and physical size. B-tree code moves through `hfs_find_data`: callers provide a search key, find code binds a tree/B-node and record offsets, and record helpers read or update entries.

Dirtying is split by metadata domain. `hfsplus_mark_inode_dirty()` sets a domain bit on the inode private flags and then calls `mark_inode_dirty()`. Later writeback/fsync paths inspect the catalog, extents, allocation, and attributes dirty bits to decide which metadata inodes and trees must be flushed.

## State and persistence behavior
The header separates mutable superblock state by lock: allocation counters use `alloc_mutex`; volume-header counters such as `next_cnid`, `file_count`, and `folder_count` use `vh_mutex`; delayed sync work is protected by `work_lock`. Inode extent allocation state is protected by `extents_lock`; some inode flags are atomic bitops; `open_dir_list` has its own spinlock. Persistent state represented here includes the volume header, backup volume header, allocation bitmap, catalog/extents/attributes B-trees, fork extents, BSD file flags, CNIDs, and HFS+ timestamps.

Timestamp conversion intentionally maps 1904-based HFS+ timestamps to Linux time by subtracting `HFSPLUS_UTC_OFFSET` in unsigned 32-bit space, matching the driver's historic 1970-2106 behavior.

## Dependencies and integration points
The file depends on Linux VFS, buffer heads, block devices, fs context parsing, mutex/spinlock/list/RCU infrastructure, NLS tables, and HFS+ wire-format definitions. It is the integration point for `super.c`, `inode.c`, `catalog.c`, `extents.c`, `btree.c`, `bnode.c`, `bfind.c`, `brec.c`, `bitmap.c`, `attributes.c`, `unicode.c`, `options.c`, `ioctl.c`, `part_tbl.c`, and `wrapper.c`.

## Risks and test signals
Risks include stale or incorrectly scoped dirty bits, inconsistent lock ordering across catalog/extents/attributes trees, B-node offset correction hiding corruption, timestamp wrap surprises, resource-fork/main-inode confusion, and prototypes drifting from implementation behavior. Test signals should include mount/write/fsync/unmount cycles, concurrent metadata updates, B-tree node-size variants, corrupted B-node offsets, HFSX casefold mounts, resource fork operations, attribute-tree creation/failure paths, and timestamp edge cases around 1970 and 2106.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_raw.h -->
# sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_raw.h

## Purpose
`hfsplus_raw.h` is a compatibility wrapper for on-disk HFS+ structure definitions. In this tree it does not define the raw structures directly; it includes `<linux/types.h>` and `<linux/hfs_common.h>`, where the shared HFS/HFS+ constants, CNIDs, volume header, fork, catalog, attribute, extent, Unicode, and permission structures live.

## Important APIs, types, and functions
The header exports no functions and declares no local types beyond its include guard. Its effective API is the set of raw HFS+ types made available through `linux/hfs_common.h`, such as `struct hfsplus_vh`, `struct hfsplus_fork_raw`, catalog entries, attribute keys, extent records, Unicode strings, and constants used throughout the HFS+ driver.

## Control flow
There is no executable control flow. The file is included by `hfsplus_fs.h`, `inode.c`, and `unicode.c` so those files can refer to raw on-disk objects without each including the common header directly.

## State and persistence behavior
The file itself has no state, but it is part of the persistence ABI boundary. Any raw structures transitively included through it describe big-endian on-disk HFS+ metadata and must remain compatible with disk images and Apple Technote 1150 semantics.

## Dependencies and integration points
It depends on Linux fixed-width types and `linux/hfs_common.h`. It integrates the HFS+ driver with common HFS/HFS+ definitions shared outside this local directory.

## Risks and test signals
Risks are mostly indirect: include path changes, raw-structure drift in `hfs_common.h`, or assumptions in implementation files that this header itself owns definitions. Test signals are compile coverage for all HFS+ objects, mount/read of representative HFS+ images, and static checks that raw structures still match expected endian/layout contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/inode.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/inode.c

## Purpose
`inode.c` implements HFS+ inode, file, address-space, attribute, and fork handling. It bridges generic VFS file I/O and metadata operations to HFS+ extent mapping, catalog records, resource forks, metadata B-tree writeback, file flags, size changes, and explicit filesystem synchronization.

## Important APIs, types, and functions
Exported objects are `hfsplus_aops`, `hfsplus_btree_aops`, and `hfsplus_dentry_operations`. Exported functions include `hfsplus_write_begin`, `hfsplus_new_inode`, `hfsplus_delete_inode`, `hfsplus_inode_read_fork`, `hfsplus_inode_write_fork`, `hfsplus_cat_read_inode`, `hfsplus_cat_write_inode`, `hfsplus_getattr`, `hfsplus_file_fsync`, `hfsplus_fileattr_get`, and `hfsplus_fileattr_set`.

Key internal helpers are `hfsplus_read_folio`, `hfsplus_write_failed`, `hfsplus_bmap`, `hfsplus_release_folio`, `hfsplus_direct_IO`, `hfsplus_writepages`, `hfsplus_get_perms`, `hfsplus_file_open`, `hfsplus_file_release`, and `hfsplus_setattr`. The file operation table uses generic llseek/read/write/mmap/splice helpers, `hfsplus_file_fsync`, open/release tracking, and `hfsplus_ioctl`.

## Control flow
Buffered writes enter `hfsplus_write_begin()`, call `cont_write_begin()` with `hfsplus_get_block`, and truncate partially instantiated blocks through `hfsplus_write_failed()` on error. Direct I/O uses `blockdev_direct_IO()` and also trims blocks beyond `i_size` after failed extending writes. Writeback uses `mpage_writepages()`. B-tree metadata mappings use a special `release_folio` path that evicts unreferenced B-node hash entries before freeing buffers.

Opening a file rejects non-largefile callers for oversized files and increments `opencnt` on the main inode, not the resource-fork proxy. Release decrements `opencnt`; the last close truncates allocation to logical size and, for dead inodes, removes the hidden-directory catalog entry and calls `hfsplus_delete_inode()`.

`hfsplus_setattr()` validates attributes, serializes direct I/O before size changes, expands sparse ranges when growing, truncates page cache and HFS+ extents when shrinking, updates times, copies attributes, and marks the inode dirty. `hfsplus_getattr()` reports birth time and append/immutable/nodump attributes.

New inode allocation consumes `sbi->next_cnid`, initializes private extent/resource-fork/open-dir state, selects directory/file/symlink/special operation tables, adjusts file/folder counters, inserts the inode hash, marks the inode dirty, and marks the volume header dirty. Deletion decrements counters and truncates regular or symlink fork storage when the last link is gone.

Catalog read loads either folder or file catalog records, validates record length and type, maps HFS+ permissions to Linux uid/gid/mode/flags, initializes times and fork state, and selects VFS operations. Catalog write locates the catalog record by CNID, updates permissions/times/valence/subfolder count or data/resource fork fields, writes the B-tree, and marks catalog dirty bits.

`hfsplus_file_fsync()` waits dirty file data, locks the inode, syncs inode metadata into catalog/extents, explicitly writes dirty catalog/extents/attributes/allocation metadata inodes, prepares and commits the volume header, and issues a block-device flush unless `nobarrier` is set.

## State and persistence behavior
Persistent inode state lives mainly in catalog records and fork records, with overflow extents in the extents B-tree and allocation state in the allocation file. The driver has no journal in this path; consistency depends on ordered writeback, dirty bits, volume-header commits, and optional cache flushes. File/folder counters and `next_cnid` are mutable superblock state. Fork state is cached in `hfsplus_inode_info` and written back with endian conversion.

Resource forks are represented by inodes with `HFSPLUS_I_RSRC` set and a back pointer to the main inode. File flags map between HFS+ permission flags and Linux `S_IMMUTABLE`, `S_APPEND`, and `FS_NODUMP_FL`.

## Dependencies and integration points
This file depends on Linux page cache, mpage, direct I/O, generic setattr/getattr/fileattr helpers, block mapping, VFS operation tables, xattrs, catalog and extent code, B-tree/B-node helpers, volume-header commit code, and `ioctl.c`. It also integrates with `unicode.c` through `hfsplus_dentry_operations`.

## Risks and test signals
Risks include resource-fork lifetime bugs, catalog record length/type validation gaps, dirty-bit loss causing metadata not to reach disk, truncate/extend races with direct I/O, B-node cache eviction while referenced, non-journaled ordering windows, incorrect link counts for hard links encoded in `permissions.dev`, and inconsistent file flag propagation. Test signals include buffered/direct extending writes with injected errors, truncate and last-close truncation, fsync after catalog/extent/attribute/allocation changes, resource-fork open/release/eviction, hard-link catalog entries, special files, immutable/append/nodump fileattr round trips, corrupted catalog records, and `nobarrier` vs barrier flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/ioctl.c

## Purpose
`ioctl.c` implements the HFS+-specific ioctl surface. The only local command is `HFSPLUS_IOC_BLESS`, which updates volume-header Finder metadata so platform firmware can locate the bootable system folder and bootloader.

## Important APIs, types, and functions
The public entry point is `hfsplus_ioctl(struct file *file, unsigned int cmd, unsigned long arg)`. The only helper is `hfsplus_ioctl_bless()`. The command code is declared in `hfsplus_fs.h` as `_IO('h', 0x80)`.

## Control flow
`hfsplus_ioctl()` switches on the command and dispatches `HFSPLUS_IOC_BLESS`; unknown commands return `-ENOTTY`. Blessing first requires `CAP_SYS_ADMIN`. It then locks `sbi->vh_mutex`, updates both primary and backup volume-header `finder_info` fields, and unlocks. `finder_info[0]` and `[5]` receive the parent directory inode, and `finder_info[1]` receives the CNID stored in `dentry->d_fsdata` so hard-link boot files use the hard-link file ID rather than the indirect inode.

## State and persistence behavior
The ioctl mutates in-memory primary and backup volume headers. Persistence is deferred to the normal superblock commit/sync path; this function does not call `hfsplus_mark_mdb_dirty()` or write the volume header itself. The state is protected by `vh_mutex`.

## Dependencies and integration points
It depends on VFS file/dentry/inode state, Linux capability checks, user ioctl dispatch, HFS+ private superblock state, and the volume-header commit logic in `super.c`. It is wired into regular-file operations through `hfsplus_file_operations.unlocked_ioctl`.

## Risks and test signals
Risks include blessing changes not being persisted until a later sync, stale or absent `d_fsdata` for hard links, allowing the ioctl on unsuitable inode types, and missing readonly/error checks in the ioctl itself. Test signals include permission checks, blessing normal files and hard links, fsync/sync/unmount persistence of Finder info, readonly mount behavior, and unknown ioctl return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/options.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/options.c

## Purpose
`options.c` owns HFS+ mount option defaults, fs_context parsing, and option display. It converts user parameters into `hfsplus_sb_info` fields and controls behavior such as default creator/type codes, uid/gid/umask overrides, partition/session selection, NLS charset, Unicode decomposition, write barriers, and forced writable mounts.

## Important APIs, types, and functions
The public functions are `hfsplus_fill_defaults()`, `hfsplus_parse_param()`, and `hfsplus_show_options()`. `hfs_param_spec[]` defines accepted parameters: `creator`, `type`, `umask`, `uid`, `gid`, `part`, `session`, `nls`, `decompose`/`nodecompose`, `barrier`/`nobarrier`, and `force`.

## Control flow
Mount initialization calls `hfsplus_fill_defaults()` to set creator/type to `????`, derive umask/uid/gid from the current task, and set partition/session to `-1`. `hfsplus_parse_param()` ignores every option except `force` during remount/reconfigure. For normal mount parsing it calls `fs_parse()` and updates the private superblock: creator/type must be exactly four bytes, uid/gid set corresponding override bits, `nls` loads a charset exactly once, negated `decompose` sets `HFSPLUS_SB_NODECOMPOSE`, negated `barrier` sets `HFSPLUS_SB_NOBARRIER`, and `force` sets `HFSPLUS_SB_FORCE`.

`hfsplus_show_options()` emits non-default creator/type values, always shows umask/uid/gid, conditionally shows part/session/nls, and prints `nodecompose` and `nobarrier` flags.

## State and persistence behavior
These options are runtime mount state, not on-disk metadata. They influence later persistence indirectly: uid/gid/umask affect mode ownership mapping for files without explicit metadata, `nodecompose` changes filename normalization behavior, `nobarrier` suppresses cache flushes, `part` and `session` choose the block range to mount, and `force` can allow write access despite journal/lock warnings in `super.c`.

## Dependencies and integration points
The file depends on the fs_context/fs_parser API, NLS loading, current credentials, seq_file option output, and superblock private flags. `super.c` installs it as the context parser and uses the parsed state during mount and reconfigure.

## Risks and test signals
Risks include treating four-byte creator/type values as host-endian integers, leaking or double-changing NLS tables, remount users expecting options other than `force` to change, `nobarrier` weakening write ordering, and force-mounted journaled HFS+ images being damaged. Test signals include valid/invalid creator/type lengths, uid/gid/umask display, NLS load failure, repeated nls option rejection, `decompose`/`nodecompose` and `barrier`/`nobarrier` polarity, remount with force, and partition/session selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/part_tbl.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/part_tbl.c

## Purpose
`part_tbl.c` parses legacy and Apple partition maps to locate an HFS/HFS+ partition within a block device. It is used when the filesystem is mounted from a whole disk image or media with Mac partition metadata rather than a raw HFS+ volume.

## Important APIs, types, and functions
The public entry point is `hfs_part_find(struct super_block *sb, sector_t *part_start, sector_t *part_size)`. Internal parsers are `hfs_parse_old_pmap()` and `hfs_parse_new_pmap()`. Local packed structures describe old partition-map entries and new Apple partition-map blocks. Important magic values include `HFS_OLD_PMAP_MAGIC` (`TS`), `HFS_NEW_PMAP_MAGIC` (`PM`), and `Apple_HFS` partition type matching.

## Control flow
`hfs_part_find()` allocates a buffer sized to `hfsplus_min_io_size()`, reads partition-map block 1 relative to the current `part_start` through `hfsplus_submit_bio()`, dispatches by the first big-endian signature, and frees the buffer on every path.

The old-map parser scans up to 42 embedded entries, looking for nonzero start/size, filesystem id `TFS1`, and either the requested partition index or any partition. The new-map parser reads the `pmMapBlkCnt` count, walks contiguous 512-byte partition entries, selects entries whose type starts with `Apple_HFS` and whose index matches `sbi->part` if set, and rereads the next media block when the current minimum-I/O buffer has been exhausted.

## State and persistence behavior
The code only reads disk partition metadata. On success it mutates the caller-provided `part_start` by adding the selected partition start and stores the selected partition size in sectors/512-byte blocks. It does not persist anything.

## Dependencies and integration points
It depends on HFS+ wrapper block I/O, superblock private mount option `part`, minimum I/O sizing, endian helpers, and slab allocation. It is normally reached from wrapper/superblock discovery before the volume header is interpreted.

## Risks and test signals
Risks include trusting `pmMapBlkCnt` from disk, off-by-one partition indices, partial-buffer pointer arithmetic across minimum I/O boundaries, weak partition-type string matching, and old-map support being limited to 42 entries and `TFS1`. Test signals include old and new Apple partition maps, requested `part=` success/failure, maps larger than one minimum-I/O block, malformed signatures/counts, I/O errors while walking entries, and raw volumes with no partition map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/part_tbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/super.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/super.c

## Purpose
`super.c` implements HFS+ filesystem registration, fs_context setup, mount-time superblock initialization, metadata inode loading, volume-header commit/sync/unmount, inode-cache lifecycle, statfs, remount policy, and superblock teardown. It is the top-level coordinator for converting a block device with an HFS+ volume header into a live VFS superblock.

## Important APIs, types, and functions
Public functions are `hfsplus_iget()`, `hfsplus_mark_mdb_dirty()`, `hfsplus_prepare_volume_header_for_commit()`, and `hfsplus_commit_superblock()`. Important internal functions include `hfsplus_system_read_inode()`, `hfsplus_system_write_inode()`, `hfsplus_write_inode()`, `hfsplus_evict_inode()`, `hfsplus_sync_fs()`, `delayed_sync_fs()`, `hfsplus_put_super()`, `hfsplus_statfs()`, `hfsplus_reconfigure()`, `hfsplus_get_hidden_dir_entry()`, `hfsplus_fill_super()`, `hfsplus_alloc_inode()`, `hfsplus_free_inode()`, `hfsplus_get_tree()`, `hfsplus_free_fc()`, `hfsplus_init_fs_context()`, `hfsplus_kill_super()`, `hfsplus_init_once()`, `init_hfsplus_fs()`, and `exit_hfsplus_fs()`.

The file defines `hfsplus_sops`, `hfsplus_context_ops`, and `hfsplus_fs_type`, plus the `hfsplus_icache` slab.

## Control flow
Module initialization creates the inode cache, creates the attribute-entry cache, and registers the `hfsplus` filesystem type. New mount contexts allocate `hfsplus_sb_info`, fill defaults for normal mounts, and install parse/get_tree/reconfigure/free callbacks. `get_tree_bdev()` calls `hfsplus_fill_super()`.

Mount setup initializes locks and delayed sync work, loads an NLS table, temporarily switches to UTF-8 to locate the hidden directory, reads the wrapper/volume header, validates HFS+ version and size limits, sets `s_op` and max file size, enforces readonly policy for unclean, softlocked, or journaled volumes unless force permits, opens extents/catalog/optional attributes B-trees, loads the allocation file and root inode, installs dentry operations, finds or creates the hidden directory for deleted open files, prepares and syncs the volume header when writable, restores the requested NLS table, and unwinds resources on errors.

`hfsplus_iget()` initializes private inode fields for new inodes, then reads user/root CNIDs from the catalog tree or system CNIDs from volume-header fork records. Writeback first writes dirty overflow extents, then writes either catalog records or system fork records. System B-tree inodes also force a B-tree header write under the nested tree lock.

`hfsplus_sync_fs()` explicitly writes catalog, extents, attributes, and allocation mappings, commits the volume header, and issues a cache flush unless barriers are disabled. `hfsplus_mark_mdb_dirty()` queues delayed sync work for dirty volume-header state. Unmount cancels delayed work, marks writable volumes unmounted and consistent, syncs, drops metadata inodes/B-trees/buffers, and later frees NLS and private superblock state via RCU from `kill_super`.

## State and persistence behavior
Persistent state is centered on the primary and backup volume headers plus metadata files referenced by the volume header. `hfsplus_prepare_volume_header_for_commit()` writes mount version, modify date, increments write count, clears `HFSPLUS_VOL_UNMNT`, and sets `HFSPLUS_VOL_INCNSTNT`; unmount reverses those consistency bits before syncing. `hfsplus_commit_superblock()` copies runtime counters into the volume header under `vh_mutex` and `alloc_mutex`, writes the primary header, and writes the backup header only when `HFSPLUS_SB_WRITEBACKUP` was set.

Because writable journaled HFS+ is not supported, this implementation relies on conservative readonly policy, explicit writeback, volume-header consistency flags, delayed syncing, and optional flush barriers. Error paths carefully drop loaded B-trees, inodes, headers, and NLS tables.

## Dependencies and integration points
The file integrates with Linux module and filesystem registration, block-device mounts, fs_context, VFS super operations, writeback, NLS, slab/RCU, catalog/extents/attributes/allocation implementations, xattr handlers, wrapper volume-header reading, security initialization for the hidden directory, and option parsing from `options.c`.

## Risks and test signals
Risks include write access to journaled or unclean volumes with `force`, incomplete error unwinding, delayed sync races during unmount, backup volume-header update conditions, lock ordering between `vh_mutex`, `alloc_mutex`, and B-tree locks, hidden-directory creation failures, temporary NLS switching side effects, and non-journaled consistency windows. Test signals include clean/unclean/softlocked/journaled mount policy, force mounts, remount readwrite checks, volume size overflow rejection, missing or malformed B-trees, hidden directory absent/present/wrong type, sync/unmount consistency flags, backup-header updates, statfs counters, inode cache lifecycle, and module init/exit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/tables.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/tables.c

## Purpose
`tables.c` contains the static Unicode mapping data used by HFS+ filename comparison, conversion, hashing, composition, and decomposition. The tables encode Apple's HFS+ case-folding behavior and normalization mappings, letting `unicode.c` implement HFS+ name semantics without dynamic Unicode database lookups.

## Important APIs, types, and functions
The exported data arrays are `hfsplus_case_fold_table[]`, `hfsplus_decompose_table[]`, and `hfsplus_compose_table[]`. There are no functions. `hfsplus_fs.h` declares the arrays for use by `unicode.c`.

`hfsplus_case_fold_table` starts with a 256-entry high-byte index and points to 256-entry subtables for blocks that have case mappings or ignorable characters; a zero high-byte entry means identity mapping for that block, and folded value zero means the character is ignorable. `hfsplus_decompose_table` is a trie-like table for non-Hangul decomposition. `hfsplus_compose_table` is a reverse lookup tree for composing decomposed sequences back to precomposed Unicode where HFS+ expects it.

## Control flow
There is no executable control flow in this file. Runtime lookup is driven by `unicode.c`: `case_fold()` indexes the case-fold table by high and low byte; `hfsplus_decompose_nonhangul()` walks the decomposition table by nibbles; and `hfsplus_compose_lookup()` binary-searches subranges in the compose table.

## State and persistence behavior
The arrays are immutable kernel data. They influence persistent namespace behavior because catalog key ordering, dentry hashing, and on-disk filename normalization depend on their exact values. Changing them can make existing names unreachable or alter collision behavior on casefolded HFSX volumes.

## Dependencies and integration points
The file depends only on `hfsplus_fs.h` for declarations and type availability. It is tightly coupled to the lookup algorithms in `unicode.c` and indirectly to catalog key comparison/building, dentry operations, and KUnit tests in `unicode_test.c`.

## Risks and test signals
Risks include table corruption, accidental regeneration from a different Unicode/HFS+ version, mismatch between compose/decompose lookup assumptions and table layout, ignorable-character handling changes, and large static data increasing review difficulty. Test signals include casefold vectors, decomposition/composition vectors including Hangul and multi-codepoint sequences, HFSX case-insensitive lookup on real disk images, dentry hash/compare consistency, and KUnit coverage for Unicode conversion paths. Static checks can also verify array bounds implied by offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/unicode.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/unicode.c

## Purpose
`unicode.c` implements HFS+ Unicode string comparison, case folding, filename conversion between HFS+ UTF-16-ish names and Linux/NLS byte strings, HFS+/Linux special-character compatibility mapping, decomposition/composition, dentry hashing, and dentry comparison. It is the main enforcement point for HFS+ and HFSX filename semantics.

## Important APIs, types, and functions
Public functions are `hfsplus_strcasecmp()`, `hfsplus_strcmp()`, `hfsplus_uni2asc_str()`, `hfsplus_uni2asc_xattr_str()`, `hfsplus_asc2uni()`, `hfsplus_hash_dentry()`, and `hfsplus_compare_dentry()`. Many are exported with `EXPORT_SYMBOL_IF_KUNIT` for unit testing.

Important internal helpers are `case_fold()`, `hfsplus_compose_lookup()`, `hfsplus_mac2linux_compatibility_check()`, `hfsplus_uni2asc()`, `hfsplus_linux2mac_compatibility_check()`, `asc2unichar()`, `hfsplus_decompose_nonhangul()`, `hfsplus_try_decompose_hangul()`, and `decompose_unichar()`.

## Control flow
Case-insensitive comparison clamps invalid lengths to `HFSPLUS_MAX_STRLEN`, folds each 16-bit character through `hfsplus_case_fold_table`, skips folded-zero ignorables, and compares folded values. Case-sensitive comparison clamps lengths and lexicographically compares raw big-endian 16-bit values.

HFS+ to Linux conversion (`hfsplus_uni2asc`) reads HFS+ Unicode characters, optionally composes decomposed sequences unless `HFSPLUS_SB_NODECOMPOSE` is set, handles Hangul algorithmic composition, maps HFS+ NUL to U+2400 and slash to colon for regular filenames, skips that compatibility mapping for xattr names, and emits bytes through the mounted NLS table. NLS conversion failures become `?` except `-ENAMETOOLONG`, which stops with an error and reports consumed length.

Linux to HFS+ conversion (`hfsplus_asc2uni`) repeatedly calls `char2uni`, maps U+2400 back to NUL and colon to slash for regular filenames, optionally decomposes non-Hangul characters through the table and Hangul syllables algorithmically, writes big-endian 16-bit output, and returns `-ENAMETOOLONG` if input remains after the maximum HFS+ name length is filled.

Dentry hashing and comparison both convert incoming byte names through NLS, optionally decompose, optionally case-fold, skip ignorable folded characters, and use Linux stringhash or lexicographic comparison over the resulting HFS+ semantic code units.

## State and persistence behavior
The file does not persist metadata directly, but it determines persistent namespace keys and lookup behavior. Superblock flags `HFSPLUS_SB_CASEFOLD` and `HFSPLUS_SB_NODECOMPOSE` alter hash, compare, and conversion semantics. The mounted NLS table affects byte encoding. Special-character mapping preserves HFS+ names containing slash or NUL while exposing Linux-compatible names.

## Dependencies and integration points
It depends on NLS tables, HFS+ Unicode mapping arrays from `tables.c`, superblock flags, Linux dentry stringhash helpers, catalog key creation/comparison through the declared API, and KUnit visibility exports. `inode.c` installs these functions into `hfsplus_dentry_operations`.

## Risks and test signals
Risks include casefold table bounds assumptions, invalid length correction reading padded or uninitialized entries, mismatched hash and compare normalization, NLS conversion lossy fallback causing name collisions, xattr names intentionally bypassing slash/NUL compatibility conversion, Hangul edge-case mistakes, and polarity confusion around `NODECOMPOSE`. Test signals include KUnit vectors, real HFS+/HFSX images with casefolded and decomposed names, slash/colon and NUL/U+2400 round trips, xattr name conversion, ENAMETOOLONG boundaries, non-ASCII NLS behavior, ignorable characters, and hash/compare equivalence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/unicode_test.c -->
# sources/distributed-fs/ceph-client/fs/hfsplus/unicode_test.c

## Purpose
`unicode_test.c` provides KUnit coverage for the HFS+ Unicode string, conversion, hash, and dentry-compare helpers. It exercises the exported-for-KUnit functions in `unicode.c` with mocked HFS+ strings, superblock private state, NLS callbacks, and dentry/qstr objects.

## Important APIs, types, and functions
The test suite is registered as `hfsplus_unicode`. Helpers include `struct test_mock_string_env`, `setup_mock_str_env()`, `free_mock_str_env()`, `create_unistr()`, `corrupt_unistr()`, `struct test_mock_sb`, `setup_mock_sb()`, `free_mock_sb()`, `test_uni2char()`, `test_char2uni()`, `check_unistr_content()`, `setup_mock_dentry()`, and `create_qstr()`.

The suite lists 27 test cases covering `hfsplus_strcasecmp`, `hfsplus_strcmp`, Unicode edge/boundary behavior, `uni2asc`, `asc2uni`, dentry hashing, dentry comparison, casefold flags, decomposition flags, special-character handling, long strings, embedded NULs, and combined flags. It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace.

## Control flow
Most tests allocate a small mock environment, populate HFS+ big-endian Unicode strings from ASCII fixtures, call the target helper, assert return values and output state, and free allocations. Conversion tests install simple mock NLS callbacks: `test_uni2char()` passes ASCII and maps non-ASCII to `?`; `test_char2uni()` maps one input byte to the same Unicode code point.

The hash/compare tests create a static mock dentry with a mock superblock, then toggle `HFSPLUS_SB_CASEFOLD` and `HFSPLUS_SB_NODECOMPOSE` to verify case sensitivity, case-insensitive equality, colon/slash normalization, long-name behavior, and deterministic hash output. The suite registration at the end supplies all cases to KUnit.

## State and persistence behavior
The tests do not touch disk or persistent filesystem state. They emulate the runtime state that affects Unicode behavior: `s_fs_info`, NLS callbacks, and HFS+ superblock flags. Memory is dynamically allocated and freed per test helper usage, with some static dentry state reset before hash/compare tests.

## Dependencies and integration points
It depends on KUnit, Linux NLS and dcache/stringhash headers, `hfsplus_fs.h`, and the KUnit-visible exports in `unicode.c`. It is a direct unit-test signal for table-driven Unicode behavior but does not mount HFS+ images or exercise catalog/B-tree integration.

## Risks and test signals
The test file's strengths are broad coverage of ASCII-oriented behavior, boundary lengths, corrupted HFS+ length fields, slash/colon mapping, embedded NULs, and flag combinations. Gaps include real UTF-8/NLS behavior, actual non-ASCII decomposition/composition vectors, Hangul syllable decomposition/composition, xattr-specific conversion, KASAN-style bounds checking for table offsets, and integration with catalog key ordering. Risks in the tests themselves include the mock NLS simplifying non-ASCII to `?`, possible polarity confusion in comments around `NODECOMPOSE`, and reliance on a static dentry object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hfsplus/unicode_test.c -->
