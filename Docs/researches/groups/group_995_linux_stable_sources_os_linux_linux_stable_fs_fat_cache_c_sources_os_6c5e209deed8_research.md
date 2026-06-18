# Group Research: group_995_linux_stable_sources_os_linux_linux_stable_fs_fat_cache_c_sources_os_6c5e209deed8

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/cache.c

This file implements FAT inode cluster-chain caching and logical-to-physical block mapping.

Key responsibilities:
- Maintains a small per-inode LRU cache of contiguous cluster-chain runs, capped by `FAT_MAX_CACHE`.
- Initializes and destroys the slab cache for `struct fat_cache`.
- Invalidates cached cluster runs when cluster chains are changed.
- Walks FAT chains through `fat_ent_read()` when a requested file cluster is not cached.
- Converts file-relative sectors into physical block numbers for page cache, direct I/O, bmap, and directory access.

Important functions:
- `fat_cache_init()` / `fat_cache_destroy()` create and destroy the global `fat_cache` kmem cache.
- `fat_cache_lookup()` finds the best cached run at or before the requested file cluster and returns the mapped disk cluster.
- `fat_cache_add()` merges or inserts a new cluster run, replacing the LRU entry when the cache is full.
- `fat_cache_inval_inode()` removes all per-inode cache entries and advances `cache_valid_id` so stale in-flight cache additions are ignored.
- `fat_get_cluster()` resolves a file cluster index to a disk cluster by starting from `i_start`, using cache hits when possible, detecting loops and invalid/free entries, and adding contiguous runs back to the cache.
- `fat_get_mapped_cluster()` maps a sector to a physical block and reports how many contiguous sectors are available.
- `fat_bmap()` handles FAT12/16 fixed root-directory mapping and normal cluster-chain mapping, with EOF checks that differ for allocation and bmap callers.

State and locking:
- Per-inode cache state lives in `struct msdos_inode_info`: `cache_lru`, `nr_caches`, and `cache_valid_id`.
- Cache list operations are protected by `cache_lru_lock`.
- Cluster-chain reads depend on `fatent.c` FAT entry access.
- `mmu_private` is consulted only on allocation paths and assumes the caller holds the inode lock.

Failure behavior:
- Invalid start clusters, free entries inside chains, cluster-chain loops, and requests beyond EOF are reported through FAT error helpers and generally return `-EIO`.
- Allocation failure for a cache object only drops the optimization; it does not fail the block lookup.

Research relevance:
- This is the core FAT block-mapping helper below regular file I/O, directory reads, truncation, and allocation. Correct cache invalidation is critical because FAT cluster chains can be rewritten by truncate, free, and rename/unlink paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/dir.c

This file implements shared directory handling for FAT-family filesystems, including directory entry iteration, short/long filename parsing, lookup helpers, ioctl readdir variants, entry removal, and entry allocation.

Key responsibilities:
- Walk directory entries with block mapping through `fat_bmap()`.
- Parse VFAT long-name slots and DOS 8.3 entries.
- Convert on-disk names through NLS or UTF-8 rules.
- Implement `iterate_shared` and legacy VFAT readdir ioctls.
- Search directories by name or starting cluster.
- Allocate and initialize directory clusters.
- Add or remove directory entry slots, including multi-slot long names.

Important functions:
- `fat_get_entry()` and `fat__get_entry()` iterate 32-byte directory entries, reading mapped blocks and issuing cluster readahead.
- `fat_parse_long()` reconstructs VFAT long filenames from ordered `ATTR_EXT` slots and validates slot count, checksum, ordering, EOF, volume, and deleted/free states.
- `fat_parse_short()` converts 8.3 entries to display names, respecting hidden-dot behavior, case flags, shortname display policy, and NLS conversion.
- `fat_search_long()` searches by short or long name and returns a `fat_slot_info` describing the matched slot range and on-disk inode position.
- `__fat_readdir()` emits directory entries, fakes root `.` and `..`, handles long/short name selection, and supports ioctl callbacks that return both names.
- `fat_dir_ioctl()` and compat variants implement `VFAT_IOCTL_READDIR_SHORT` and `VFAT_IOCTL_READDIR_BOTH`.
- `fat_scan()` and `fat_scan_logstart()` find entries by formatted 8.3 name or first cluster.
- `fat_dir_empty()` and `fat_subdirs()` scan for directory emptiness and subdirectory counts.
- `fat_alloc_new_dir()` allocates a cluster and initializes `.` and `..`.
- `fat_add_entries()` finds free slots or allocates new clusters, writes long-name slots before the short entry, and returns the final short-entry location.
- `fat_remove_entries()` marks the short entry first as deleted, then removes any preceding long-name slots.

State and integration:
- Uses `struct fat_slot_info` as the common handoff between lookup/namei code and mutation code.
- Uses `sbi->s_lock` for serialized readdir/namei paths.
- Updates directory times, inode version, metadata buffer tracking, and synchronous-directory writes where required.
- Calls into `fat_alloc_clusters()`, `fat_chain_add()`, `fat_free_clusters()`, `fat_sync_inode()`, and FAT time helpers.

Failure behavior:
- Directory read failures are rate-limited and skipped when possible during iteration.
- Corrupt entries or invalid long-name slot chains are ignored for lookup/readdir unless memory or I/O errors occur.
- Entry allocation carefully rolls back newly written free slots when later cluster allocation or chain extension fails.

Research relevance:
- This is the shared namespace storage layer used by both `msdos` and `vfat`; it defines how Linux interprets, scans, creates, and deletes FAT directory records.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/fat.h -->
# File Research: sources/os/linux/linux-stable/fs/fat/fat.h

This header defines the private FAT filesystem ABI shared across the FAT core, directory code, namei implementations, NFS export code, tests, and module setup.

Key data structures:
- `struct fat_mount_options` stores mount behavior: ownership, masks, codepage/iocharset, timestamp offset, shortname policy, error policy, NFS mode, and feature flags such as `flush`, `discard`, `rodir`, `utf8`, and `unicode_xlate`.
- `struct msdos_sb_info` is the in-core superblock: geometry, FAT layout, root directory layout, FSINFO state, locks, free-cluster cache, NLS tables, inode/dir hash tables, FAT entry operations, and dirty-state tracking.
- `struct msdos_inode_info` extends VFS inode state with cluster-cache LRU state, first/logical cluster, on-disk directory-entry position, truncate lock, creation time, and metadata buffer tracking.
- `struct fat_slot_info` describes a matched or inserted directory entry range.
- `struct fat_entry` represents a FAT table entry cursor, including variant-specific entry pointers and buffer_heads.

Important inline helpers:
- `MSDOS_SB()` and `MSDOS_I()` convert VFS objects to FAT-private state.
- `is_fat12()`, `is_fat16()`, `is_fat32()`, and `max_fat()` classify FAT variants.
- `fat_mode_can_hold_ro()`, `fat_make_mode()`, `fat_make_attrs()`, and `fat_save_attrs()` translate between DOS attribute bits and Unix mode semantics.
- `fat_checksum()` computes the VFAT long-name alias checksum.
- `fat_clus_to_blknr()`, `fat_get_blknr_offset()`, `fat_get_start()`, and `fat_set_start()` encode/decode on-disk locations and cluster numbers.
- `fat16_towchar()` and `fatwchar_to16()` handle endian-safe UTF-16 slot conversion.
- `fatent_init()`, `fatent_set_entry()`, `fatent_brelse()`, and `fat_valid_entry()` manage FAT entry cursors.

Exported interfaces:
- Declares cross-file functions for cluster caching, directory scanning/mutation, FAT entry access/allocation/free/trim, regular file operations, inode/superblock lifecycle, error reporting, time conversion, NFS export operations, and buffer synchronization.

Research relevance:
- This file is the central contract for the FAT implementation. It shows which state is global per superblock, which is per inode, and which helpers form the boundaries between cache, directory, allocation, file, inode, and namespace layers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/fat_test.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/fat_test.c

This file contains KUnit coverage for FAT checksum and timestamp conversion behavior.

Covered behavior:
- `fat_checksum()` is tested against known 8.3 aliases without extension, with a three-letter extension, and with a one-letter extension.
- `fat_time_fat2unix()` and `fat_time_unix2fat()` are tested across FAT date range limits, leap years, UTC offsets, odd seconds, and centisecond precision.
- `fat_time_unix2fat()` clamp behavior is tested below 1980 and above 2107, including timezone offsets that push otherwise-valid UTC values out of FAT range.
- `fat_time_unix2fat()` is also tested with a `NULL` centisecond pointer.
- `fat_truncate_atime()` is tested for FAT’s local-day access-time truncation behavior under UTC and offset timezones.

Important structures:
- `fat_timestamp_testcase` stores bidirectional timestamp conversion cases.
- `fat_unix2fat_clamp_testcase` stores out-of-range conversion clamp cases.
- `fat_truncate_atime_testcase` stores expected local-midnight truncation cases.

Important functions:
- `fat_test_set_time_offset()` builds a minimal fake `msdos_sb_info` with `tz_set` and `time_offset`.
- Parameterized KUnit tests use `KUNIT_ARRAY_PARAM()` for timestamp, clamp, and atime truncation cases.
- `fat_test_suite` registers all test cases under the `fat_test` suite.

Research relevance:
- This file documents expected FAT timestamp semantics, especially the tricky 1980-2107 range, 2-second mtime granularity, 10ms creation-time centiseconds, and local-time access-date truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/fat_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/fatent.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/fatent.c

This file implements raw FAT table entry access for FAT12, FAT16, and FAT32, plus cluster allocation, cluster freeing, free-space counting, and discard trimming.

Key responsibilities:
- Abstract FAT12/16/32 entry layout behind `struct fatent_operations`.
- Read and write FAT entries, including mirrored FAT copies.
- Allocate new cluster chains.
- Free cluster chains and optionally issue discard.
- Count free clusters with FAT-table readahead.
- Implement `FITRIM` cluster-range trimming.

Important functions:
- `fat_ent_access_init()` selects FAT12, FAT16, or FAT32 operations and initializes `sbi->fat_lock`.
- `fat_ent_read()` validates an entry, maps it to a FAT sector/offset, reuses buffer_heads when possible, and returns the decoded next cluster or EOF.
- `fat_ent_write()` updates an entry, optionally syncs modified buffers, and mirrors changes to backup FATs.
- FAT12 helpers handle 12-bit packed entries that can straddle block boundaries, protected by `fat12_entry_lock`.
- `fat_alloc_clusters()` scans from `prev_free`, links allocated entries into a chain, updates free-cluster accounting, mirrors changes, and rolls back partial allocation on error.
- `fat_free_clusters()` walks a cluster chain, marks entries free, batches dirty buffers, updates FSINFO counters, and optionally discards contiguous freed cluster ranges.
- `fat_count_free_clusters()` scans the FAT with readahead and updates `sbi->free_clusters`.
- `fat_trim_fs()` converts a byte `fstrim_range` into cluster indexes, scans for free extents meeting `minlen`, issues discard, and reports trimmed bytes.

State and locking:
- All FAT table mutation and free-space scans are serialized with `sbi->fat_lock`.
- FSINFO updates are marked dirty via the synthetic `fsinfo_inode`.
- Modified FAT buffers are tracked with `mmb_mark_buffer_dirty()` against `sbi->fat_inode`.

Failure behavior:
- Invalid FAT entry access is reported and returns `-EIO`.
- Read failures are rate-limited.
- Allocation sets `free_clusters = 0` when no space is found.
- `fat_trim_fs()` tolerates `-EOPNOTSUPP` from discard as non-fatal for individual trim attempts.

Research relevance:
- This is the allocator and low-level FAT table engine. Most correctness risks involve FAT12 packed-entry handling, mirrored FAT consistency, free-space accounting, and avoiding partial-chain leaks on allocation failures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/fatent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/file.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/file.c

This file implements regular-file VFS operations and generic FAT ioctls.

Key responsibilities:
- Handle FAT attribute ioctls, volume ID query, and `FITRIM`.
- Define regular file operations and inode operations.
- Implement file release flushing, fsync, fallocate, truncate, getattr, and setattr.
- Enforce FAT mode and timestamp semantics.

Important functions:
- `fat_generic_ioctl()` dispatches `FAT_IOCTL_GET_ATTRIBUTES`, `FAT_IOCTL_SET_ATTRIBUTES`, `FAT_IOCTL_GET_VOLUME_ID`, and `FITRIM`.
- `fat_ioctl_set_attributes()` validates immutable/system behavior, maps DOS attributes to Unix mode changes, calls security hooks and `fat_setattr()`, updates immutable flags, saves attributes, and dirties the inode.
- `fat_file_release()` performs extra flushing when the `flush` mount option is enabled.
- `fat_file_fsync()` syncs file metadata buffers, FAT metadata buffers, and flushes the block device.
- `fat_fallocate()` supports preallocation with optional `FALLOC_FL_KEEP_SIZE`; unsupported flags and directories return `-EOPNOTSUPP`.
- `fat_free()` truncates cluster chains, updates EOF in FAT when keeping a prefix, invalidates cluster cache, and frees the remaining chain.
- `fat_truncate_blocks()` adjusts `mmu_private`, frees clusters past the requested offset, and flushes if configured.
- `fat_getattr()` fills stat data, exposes cluster size, maps NFS no-stale inode numbers to `i_pos`, and reports VFAT birth time.
- `fat_setattr()` handles permission checks, quiet-mode compatibility, size expansion before truncate, size shrinking with block tail zeroing, FAT timestamp truncation, and final inode dirtying.

Operations:
- `fat_file_operations` wires generic read/write/mmap/splice operations to FAT-specific ioctl, fsync, release, and fallocate.
- `fat_file_inode_operations` wires setattr/getattr/update_time.

Failure behavior:
- Attribute changes reject illegal `ATTR_VOLUME`/`ATTR_DIR` mutations, root attribute changes, and unauthorized system immutable changes.
- FAT mode sanitization quietly drops invalid chmod requests in historical compatibility cases.
- Truncate and fallocate paths are careful to avoid holes inconsistent with FAT allocation.

Research relevance:
- This is the regular-file policy layer above block mapping and FAT allocation. It translates Linux file operations into FAT’s no-holes, attribute-byte, coarse-timestamp model.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/inode.c

This file implements the core FAT superblock, inode, address-space, mount-option, and module lifecycle logic.

Key responsibilities:
- Map file blocks for buffered I/O, direct I/O, writeback, bmap, and truncation.
- Manage FAT-private inode caches keyed by directory-entry position.
- Build VFS inodes from on-disk directory entries.
- Serialize inode metadata back to FAT directory entries.
- Parse mount options for both `msdos` and `vfat`.
- Read and validate boot-sector BPB data, including optional DOS 1.x floppy defaults.
- Fill the superblock, root inode, synthetic FAT/FSINFO inodes, NLS tables, export operations, and filesystem geometry.
- Manage FAT inode slab cache and module init/exit.

Important I/O functions:
- `fat_add_cluster()` allocates one cluster and appends it to an inode chain.
- `__fat_get_block()` maps or allocates a block, using `mmu_private` to prevent hole creation and adding clusters at cluster boundaries.
- `fat_write_begin()` / `fat_write_end()` integrate FAT allocation with buffered writes and set archive/time metadata.
- `fat_direct_IO()` allows direct reads/writes only when writes do not need to extend `mmu_private`; otherwise it falls back to buffered I/O.
- `_fat_bmap()` protects bmap against truncation with `truncate_lock`.
- `fat_block_truncate_page()` zeroes partial blocks before truncation.

Important inode functions:
- `fat_attach()` and `fat_detach()` maintain the on-disk-position hash and optional directory-start-cluster hash for NFS.
- `fat_iget()` finds an inode by on-disk directory-entry position.
- `fat_fill_inode()` converts a `msdos_dir_entry` into VFS inode mode, operations, size, blocks, timestamps, attributes, and cluster starts.
- `fat_build_inode()` creates or reuses an inode for a directory entry and attaches it to FAT hashes.
- `fat_evict_inode()` frees clusters for unlinked files, trims unused fallocated EOF blocks, invalidates metadata buffers, clears cluster cache, and detaches hashes.
- `__fat_write_inode()` updates the backing directory entry with size, attributes, start cluster, mtime, and VFAT atime/ctime fields.

Important mount/superblock functions:
- `fat_parse_param()` handles shared, msdos-specific, and vfat-specific mount options.
- `fat_init_fs_context()` initializes default mount options.
- `fat_read_bpb()` validates normal FAT BPB fields.
- `fat_read_static_bpb()` supplies defaults for recognized DOS 1.x floppy images when requested.
- `fat_fill_super()` allocates `msdos_sb_info`, applies options, reads BPB/FSINFO, computes FAT layout and cluster counts, loads NLS tables, creates synthetic/root inodes, chooses export operations, marks the volume dirty, and installs the root dentry.
- `fat_put_super()` clears dirty state and releases synthetic inodes and NLS resources.
- `fat_statfs()` reports free space, counting clusters on demand.

State and locking:
- `s_lock` serializes high-level FAT operations.
- `inode_hash_lock` protects `i_pos` attachment and write_inode races.
- `dir_hash_lock` supports NFS parent reconstruction.
- `truncate_lock` protects bmap against truncate.
- `nfs_build_inode_lock` serializes inode construction in no-stale NFS mode.

Failure behavior:
- Invalid BPB geometry, unsupported logical sector size, missing codepage/iocharset, bad root inode creation, or invalid cluster counts fail mount.
- Dirty volumes produce warnings but remain mountable.
- Writeback retries when inode `i_pos` changes during rename.

Research relevance:
- This is the central FAT core. It connects mount-time geometry discovery, VFS inode lifecycle, data I/O, metadata serialization, option parsing, and module-global cache setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/misc.c

This file provides shared FAT helpers for error handling, logging, FSINFO flushing, cluster-chain extension, timestamp conversion, timestamp truncation, and buffer synchronization.

Key responsibilities:
- Apply mount-option-driven behavior for filesystem errors.
- Print FAT-prefixed kernel messages.
- Flush FAT32 FSINFO free-cluster and next-cluster hints.
- Append clusters to an inode chain.
- Convert FAT date/time fields to and from Unix `timespec64`.
- Apply FAT timestamp granularity rules.
- Synchronously write buffer_head arrays.

Important functions:
- `__fat_fs_error()` reports corruption-like filesystem errors and either continues, panics, or remounts read-only based on `errors=`.
- `_fat_msg()` emits FAT-prefixed printk messages.
- `fat_clusters_flush()` writes `free_clusters` and `prev_free` to the FAT32 FSINFO sector when valid.
- `fat_chain_add()` appends a newly allocated cluster chain to an inode, updates start cluster for empty files, validates expected block count, and updates `i_blocks`.
- `fat_time_fat2unix()` converts FAT date/time/centiseconds into Unix time with timezone offset handling.
- `fat_time_unix2fat()` converts Unix time into FAT fields, clamping outside the supported 1980-2107 range.
- `fat_truncate_atime()` truncates access time to local-day granularity.
- `fat_truncate_time()` applies FAT atime and ctime/mtime granularity; root inode timestamps remain zero.
- `fat_update_time()` is the VFS update-time hook.
- `fat_sync_bhs()` writes and waits for a list of dirty buffers.

State and integration:
- Timestamp conversion honors `tz_set` and `time_offset`, otherwise uses system timezone minutes west.
- `fat_chain_add()` relies on `fat_get_cluster()`, `fat_ent_read()`, and `fat_ent_write()` from the cache/FAT-entry layers.
- FSINFO flushing is triggered through the synthetic FSINFO inode write path.

Failure behavior:
- Invalid FSINFO signatures are logged but do not hard-fail flushing.
- Cluster count mismatch during append reports a filesystem error and invalidates the inode cluster cache.
- Buffer sync returns `-EIO` if any written buffer is not uptodate.

Research relevance:
- This is the shared utility layer where FAT’s unusual error policy, timezone-dependent timestamps, and append-chain bookkeeping are centralized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/namei_msdos.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/namei_msdos.c

This file implements the `msdos` filesystem namespace operations using strict DOS 8.3 directory entries without VFAT long-name slots.

Key responsibilities:
- Format user names into 8.3 on-disk names.
- Provide dentry hash/compare operations based on formatted DOS names.
- Implement lookup, create, mkdir, unlink, rmdir, and rename.
- Handle `dotsOK` hidden-file behavior for non-VFAT mounts.
- Register the `msdos` filesystem type and fs_context operations.

Important functions:
- `msdos_format_name()` validates and converts names into 11-byte DOS format, rejecting invalid characters based on `check=` policy, uppercasing when required, handling extensions, spaces, leading dots, and the special first-byte `0xE5` to `0x05` mapping.
- `msdos_find()` formats a user name, scans the directory with `fat_scan()`, and applies hidden-dot conflict rules.
- `msdos_hash()` and `msdos_cmp()` make dcache operations compare by normalized DOS 8.3 form when possible.
- `msdos_lookup()` finds an entry under `s_lock` and builds or splices the inode.
- `msdos_add_entry()` builds one short directory entry with timestamps, attributes, hidden flag, start cluster, and size.
- `msdos_create()` rejects conflicts such as `foo` versus `.foo`, adds an entry, builds an inode, and instantiates the dentry.
- `msdos_mkdir()` allocates and initializes a new directory cluster, adds the parent entry, increments parent link count, and builds the child inode.
- `msdos_unlink()` and `msdos_rmdir()` remove entries, clear link counts, detach FAT inode hashes, and flush when needed.
- `do_msdos_rename()` handles replacement, cross-directory directory moves, `..` updates, hidden-attribute changes for dot aliases, link-count adjustments, and rollback on sync failure.
- `msdos_rename()` validates flags, formats old/new names, computes hidden-dot state, and delegates to `do_msdos_rename()`.

Operations and registration:
- `msdos_dir_inode_operations` wires VFS namespace operations to shared FAT setattr/getattr/update_time.
- `setup()` installs msdos directory ops and dentry ops and sets `SB_NOATIME`.
- The module registers `msdos_fs_type` with `fat_fill_super()` and `fat_parse_param(..., false)`.

Failure behavior:
- Invalid names generally map to `-EINVAL` or lookup `-ENOENT`.
- Rename rollback attempts to restore inode attachments, dotdot entries, and target entries; serious partial failures are reported as filesystem corruption.

Research relevance:
- This is the short-name-only namespace personality for FAT. It shows how the common FAT directory layer is adapted to legacy DOS naming rules.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/namei_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/namei_vfat.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/namei_vfat.c

This file implements the `vfat` namespace layer, including long filenames, short-alias generation, case-insensitive dentries, and extended rename behavior.

Key responsibilities:
- Provide case-sensitive or case-insensitive dentry hashing/comparison depending on mount options.
- Revalidate negative dentries when directory versions change because new long names can create matching 8.3 aliases.
- Convert user names to UTF-16 long-name slots.
- Generate unique 8.3 aliases.
- Build multi-slot VFAT directory entries.
- Implement lookup, create, mkdir, unlink, rmdir, normal rename, and `RENAME_EXCHANGE`.
- Register the `vfat` filesystem type and fs_context operations.

Important functions:
- `vfat_revalidate()` and `vfat_revalidate_ci()` validate negative dentries against parent inode version, with stricter dropping for case-insensitive create/rename targets.
- `vfat_hash()` / `vfat_hashi()` and `vfat_cmp()` / `vfat_cmpi()` implement trailing-dot-stripped dcache behavior, optionally case-insensitive through NLS lowercasing.
- `vfat_is_used_badchars()` rejects invalid Unicode names and trailing spaces.
- `to_shortname_char()` maps Unicode chars into short-name bytes, replacing unsupported or disallowed alias chars with `_` and tracking case properties.
- `vfat_create_shortname()` decides whether a long name can be represented as a short entry only, whether an LFN must be stored without a numeric tail, or whether `~n`/randomized aliases are needed to avoid collisions.
- `xlate_to_uni()` converts input names from UTF-8 or configured NLS, including `:hhhh` unicode escape decoding when enabled, and pads the UTF-16 name to 13-char slot boundaries.
- `vfat_build_slots()` builds long-name slots with checksum plus the final short alias entry.
- `vfat_add_entry()` strips trailing dots, allocates slot memory, builds slots, calls `fat_add_entries()`, and updates parent metadata.
- `vfat_lookup()` searches by long or short name, builds inodes, and handles alias dentries for long-name versus 8.3 lookups.
- `vfat_create()`, `vfat_mkdir()`, `vfat_unlink()`, and `vfat_rmdir()` are namespace mutations built around shared FAT directory helpers.
- `vfat_rename()` handles normal rename and replacement, including cross-directory `..` updates and rollback.
- `vfat_rename_exchange()` swaps two existing entries by exchanging inode `i_pos` attachments and updating `..` entries/link counts for cross-directory directory exchanges.
- `vfat_rename2()` accepts `RENAME_NOREPLACE` and `RENAME_EXCHANGE`.

Operations and registration:
- `vfat_dir_inode_operations` wires VFS namespace operations to shared FAT setattr/getattr/update_time.
- `setup()` installs vfat dir ops and selects case-insensitive dentry ops unless `check=strict`.
- The module registers `vfat_fs_type` with `fat_fill_super()` and `fat_parse_param(..., true)`.

Failure behavior:
- Invalid long names return `-EINVAL`; too-long converted names return `-ENAMETOOLONG`.
- Alias collision generation probes existing short names and falls back to jiffies-derived aliases after `~1` through `~9`.
- Rename rollback restores inode positions and dotdot entries where possible, and reports filesystem corruption if recovery fails.

Research relevance:
- This file is the Windows-compatible FAT namespace personality. It contains the highest-complexity name handling in the FAT implementation: Unicode conversion, short alias policy, negative-dentry coherency, and atomic-ish rename/exchange logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/namei_vfat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/nfs.c -->
# File Research: sources/os/linux/linux-stable/fs/fat/nfs.c

This file implements NFS export support for FAT, including a normal stale-capable mode and a read-only no-stale mode based on stable directory-entry positions.

Key responsibilities:
- Encode and decode FAT file handles.
- Reconstruct inodes from either VFS inode numbers or FAT directory-entry positions.
- Find parent directories for disconnected dentries.
- Support a special `nfs=nostale_ro` mode that forces read-only export and uses `i_pos`-based handles.

Important data:
- `struct fat_fid` stores generation, child `i_pos`, and optional parent `i_pos` plus parent generation.
- `FAT_FID_SIZE_WITHOUT_PARENT` and `FAT_FID_SIZE_WITH_PARENT` define file-handle lengths.

Important functions:
- `fat_dget()` finds a cached directory inode by logical start cluster through `dir_hashtable`.
- `fat_ilookup()` chooses `fat_iget(i_pos)` in no-stale mode or normal `ilookup()` in stale-capable mode.
- `__fat_nfs_get_inode()` validates generation and, in no-stale mode, can read the directory-entry block and rebuild an inode if the entry is not free.
- `fat_encode_fh_nostale()` encodes child and optional parent directory-entry positions into the file handle.
- `fat_fh_to_dentry()` and `fat_fh_to_parent()` delegate normal handles to generic export helpers.
- `fat_fh_to_dentry_nostale()` and `fat_fh_to_parent_nostale()` decode `fat_fid` and obtain aliases from rebuilt inodes.
- `fat_rebuild_parent()` reconstructs a parent by reading a child directory’s `.` and `..` entries, using a cached or dummy grandparent to scan for the matching cluster.
- `fat_get_parent()` reads `..`, tries `fat_dget()`, and falls back to parent rebuild in no-stale mode.

Export operations:
- `fat_export_ops` uses generic inode-number file handles and can become stale after FAT rename/delete behavior.
- `fat_export_ops_nostale` uses custom `i_pos` handles and parent reconstruction, intended for read-only export.

Failure behavior:
- File handles with insufficient length or unknown type return `NULL`.
- If a no-stale decoded directory entry is free, no inode is built.
- Parent reconstruction depends on readable directory clusters and may fail if required cached/dummy traversal cannot be constructed.

Research relevance:
- This file explains the FAT NFS tradeoff: normal exports are simpler but can go stale, while no-stale exports use on-disk directory positions and are restricted to read-only mounts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fcntl.c -->
# File Research: sources/os/linux/linux-stable/fs/fcntl.c

This file implements the Linux `fcntl` and `fcntl64` syscall core, file ownership for async notifications, fasync list management, signal delivery for async I/O, descriptor flag operations, lock command dispatch, leases/delegations, pipe sizing, memfd seals, and read/write lifetime hints.

Key responsibilities:
- Implement `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, descriptor duplication queries, and created-file queries.
- Dispatch POSIX/OFD lock commands to file-locking helpers.
- Manage `F_SETOWN`, `F_GETOWN`, `F_SETOWN_EX`, `F_GETOWN_EX`, `F_GETSIG`, and `F_SETSIG`.
- Expose owner UIDs for checkpoint/restore when configured.
- Handle leases, directory notifications, pipe size, memfd seals, write-life hints, and delegations.
- Provide native 32-bit, 64-bit, and compat syscall handling.
- Manage `fasync_struct` lists used by drivers and leases for async notification.

Important functions:
- `setfl()` validates and updates mutable file status flags: append-only restrictions, `O_NOATIME` permission, `O_NDELAY`/`O_NONBLOCK`, `O_DIRECT` capability, filesystem `check_flags`, and fasync transitions.
- `file_f_owner_allocate()` lazily allocates `struct fown_struct` with race-safe `cmpxchg`.
- `__f_setown()`, `f_setown()`, `f_delown()`, and `f_getown()` manage signal owner pid/type and credential snapshots.
- `f_setown_ex()` / `f_getown_ex()` handle typed owner selection for TID, PID, or process group.
- `rw_hint_valid()`, `fcntl_get_rw_hint()`, and `fcntl_set_rw_hint()` validate and get/set inode write lifetime hints.
- `f_dupfd_query()` reports whether another fd refers to the same `struct file`.
- `do_fcntl()` is the main command dispatcher for native fcntl.
- `check_fcntl_cmd()` allows a small safe subset for `FMODE_PATH` files.
- `SYSCALL_DEFINE3(fcntl)` and `SYSCALL_DEFINE3(fcntl64)` implement native syscall entry points.
- Compat helpers convert `compat_flock`/`compat_flock64`, fix overflow for old lock structures, and route compat syscalls through `do_compat_fcntl64()`.
- `send_sigio()` and `send_sigurg()` deliver async I/O and urgent-data signals to process, thread-group, or process-group owners after permission checks.
- `fasync_insert_entry()`, `fasync_remove_entry()`, `fasync_helper()`, and `kill_fasync()` maintain and use RCU-protected async notification lists.
- `fcntl_init()` validates open-flag bit uniqueness and creates the `fasync_cache`.

State and locking:
- `file->f_lock` protects mutable file flags during `F_SETFL` and fasync state changes.
- `fown_struct->lock` protects owner pid/type/credentials/signum.
- `fasync_lock` protects global fasync list modifications; individual entries also have `fa_lock`.
- RCU is used for pid/task lookup and fasync traversal.

Security and permission checks:
- `security_file_fcntl()` gates syscall commands.
- `inode_owner_or_capable()` gates `O_NOATIME` and write-life hint changes.
- `security_file_set_fowner()` records async owner security state.
- `security_file_send_sigiotask()` gates async signal delivery.

Failure behavior:
- Unsupported commands return `-EINVAL` from dispatch or `-ENOTTY` in lower helpers where appropriate.
- Bad fds return `-EBADF`.
- Invalid owners return `-ESRCH`; invalid signals return `-EINVAL`.
- User copy failures return `-EFAULT`.
- Compat lock results may return `-EOVERFLOW` if old ABI fields cannot represent the result.

Research relevance:
- This is the VFS syscall hub for file-descriptor control and async notification. It is not FAT-specific, but FAT file and directory operations expose `setlease` and ioctl behavior that eventually interact with this generic fcntl infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fcntl.c -->