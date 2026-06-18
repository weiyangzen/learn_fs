# Group Research: group_753_linux_sources_os_linux_linux_fs_fat_cache_c_sources_os_linux_linux_f_387687195dab

Scope verified against `Docs/research_subset_a.md`: this group is within `sources/os/linux/linux`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/cache.c -->
# File Research: sources/os/linux/linux/fs/fat/cache.c

## Purpose
Implements FAT per-inode cluster-chain lookup caching and block mapping. It speeds translation from file-relative cluster/block positions to on-disk clusters/sectors while handling FAT chain corruption, EOF, truncation races, and FAT12/16 fixed root directory mapping.

## Main Responsibilities
- Maintains a small per-inode LRU cache of contiguous cluster-chain runs, capped by `FAT_MAX_CACHE`.
- Resolves a file cluster index to an on-disk cluster via `fat_get_cluster()`.
- Maps logical sectors to physical sectors for buffered I/O and `bmap()`.
- Invalidates cached cluster mappings when the FAT chain changes.

## Key Interfaces
- `fat_cache_init()` / `fat_cache_destroy()`: create and destroy the slab cache for `struct fat_cache`.
- `fat_cache_inval_inode()`: drops all cached cluster-chain records for one inode and bumps `cache_valid_id`.
- `fat_get_cluster()`: walks the FAT chain from `MSDOS_I(inode)->i_start` or from a cache hit to find a requested cluster.
- `fat_get_mapped_cluster()`: converts a sector into FAT cluster plus intra-cluster offset and returns a physical block span.
- `fat_bmap()`: public mapping helper used by FAT address-space and directory code.

## Important Behavior
`fat_get_cluster()` treats `cluster == 0` as the inode start cluster and returns `FAT_ENT_EOF` if the requested cluster is past EOF. It detects invalid start clusters, free entries in chains, and probable loops using `s_maxbytes >> cluster_bits` as a traversal limit.

The cache records file cluster, disk cluster, and contiguous length. `fat_cache_lookup()` can return either an exact containing run or the nearest prior run, allowing traversal to resume partway through a chain. `fat_cache_add()` rejects stale lookups by comparing `fat_cache_id.id` against the inode `cache_valid_id`.

`fat_bmap()` has a special branch for the fixed FAT12/FAT16 root directory, whose data is not cluster-chain-backed. For normal files it checks EOF differently for live I/O versus `bmap()` callers.

## Dependencies
Uses `struct msdos_inode_info` cache fields from `fat.h`, FAT entry readers from `fatent.c`, and error reporting from `misc.c`.

## Research Notes
The cache is correctness-sensitive around chain mutation. The code deliberately invalidates cache entries on truncation/free paths rather than trying to update existing LRU entries. The dummy cache id path in `fat_get_cluster()` avoids adding a bogus cache when no useful prior mapping was found.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/dir.c -->
# File Research: sources/os/linux/linux/fs/fat/dir.c

## Purpose
Implements FAT directory traversal, name parsing, directory-entry search, readdir/ioctl readdir, directory entry allocation/removal, and new-directory initialization.

## Main Responsibilities
- Reads directory entries through `fat_get_entry()` and physical mappings from `fat_bmap()`.
- Parses short 8.3 names and VFAT long-name slot chains.
- Implements `iterate_shared` via `fat_readdir()`.
- Supports legacy VFAT directory ioctls returning short or short+long names.
- Searches directories by name, short name, or starting cluster.
- Adds/removes directory entry slot sequences.
- Allocates and zeroes clusters for new directories or directory growth.

## Key Interfaces
- `fat_search_long()`: searches a directory by display/input name, comparing both short and long names.
- `fat_dir_empty()`: checks that a directory contains no entries other than `.` and `..`.
- `fat_subdirs()`: counts subdirectories for link-count setup.
- `fat_scan()` / `fat_scan_logstart()`: find a short-name entry or entry with a given starting cluster.
- `fat_get_dotdot_entry()`: locates `..` in a directory.
- `fat_alloc_new_dir()`: allocates a cluster and writes `.` / `..`.
- `fat_add_entries()`: writes one or more short/VFAT slots into free directory space or extends the directory.
- `fat_remove_entries()`: marks a short entry and its long-name slots deleted.
- `fat_dir_operations`: file operations for directories.

## Important Behavior
`fat_parse_long()` validates VFAT slot ordering, slot count, checksum, and associated short entry. If checksum validation fails, it still allows the short name but clears `nr_slots`, preventing the long name from being used.

`fat_parse_short()` handles 8.3 decoding, hidden-dot presentation for msdos mounts, case display flags, NLS conversion, UTF-8 conversion through `fat_uni_to_x8()`, and the special 0x05/0xE5 deleted-entry convention.

`__fat_readdir()` serializes directory reads with `sbi->s_lock`, fakes `.` and `..` for root, handles invalid offsets, skips volume/free/deleted entries, and emits stable inode numbers by trying `fat_iget()` for existing inodes or falling back to `iunique()`.

`fat_add_entries()` is staged for consistency: it first fills existing free slots if possible, syncs long slots before short slots for dirsync, then allocates and chains new clusters only if needed. On failure after partial insertion it removes any slots it just wrote.

## Dependencies
Depends on `cache.c` for `fat_bmap()`, `fatent.c`/`misc.c` for cluster allocation and time conversion, `inode.c` for `fat_iget()` and inode build/sync helpers, and `fat.h` structures/constants.

## Research Notes
Ordering matters: deletion marks the short entry first, making the file invisible before long-name cleanup. Creation writes long-name slots before the short entry, so incomplete creation is less likely to expose a valid file. Directory cluster zeroing uses buffer locking to avoid races with userspace reads through the block device.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/fat.h -->
# File Research: sources/os/linux/linux/fs/fat/fat.h

## Purpose
Central private header for Linux FAT, msdos, and vfat implementation. It defines mount options, in-memory superblock and inode state, FAT entry abstractions, inline conversion helpers, and cross-file function declarations.

## Main Data Structures
- `struct fat_mount_options`: parsed mount policy such as uid/gid, masks, charset/codepage, shortname behavior, error policy, NFS mode, timestamp offset, flush/discard, VFAT options, and DOS compatibility flags.
- `struct msdos_sb_info`: in-core FAT superblock state including geometry, FAT layout, root directory layout, FSINFO state, locks, NLS tables, inode/dir hash tables, FAT operations, and mount options.
- `struct msdos_inode_info`: FAT-specific inode state including cluster-cache LRU, allocated size `mmu_private`, start/logical start clusters, attributes, on-disk directory-entry position, hash nodes, truncate lock, birth time, metadata buffer tracking, and embedded VFS inode.
- `struct fat_slot_info`: result container for directory entry searches and additions.
- `struct fat_entry`: abstraction for a FAT12/16/32 entry and its backing buffer heads.

## Key Inline Helpers
- `MSDOS_SB()` and `MSDOS_I()` cast VFS objects to FAT-specific state.
- `is_fat12()`, `is_fat16()`, `is_fat32()`, `max_fat()` classify FAT variant.
- `fat_make_mode()`, `fat_make_attrs()`, `fat_save_attrs()`, `fat_mode_can_hold_ro()` translate between DOS attributes and Unix mode bits.
- `fat_checksum()` computes VFAT long-name checksum over the 8.3 alias.
- `fat_clus_to_blknr()`, `fat_get_blknr_offset()`, `fat_get_start()`, `fat_set_start()` translate FAT directory and cluster fields.
- `fatent_init()`, `fatent_set_entry()`, `fatent_brelse()`, `fat_valid_entry()` manage FAT entry cursors.

## Exported Internal API
Declares the internal interfaces implemented by `cache.c`, `dir.c`, `fatent.c`, `file.c`, `inode.c`, `misc.c`, and `nfs.c`.

## Research Notes
This header is the coupling point for the FAT subsystem. It captures the main invariants: cluster numbers start at `FAT_START_ENT`, FAT32 start clusters use high and low directory-entry fields, `mmu_private` requires inode locking on allocation paths, and `i_pos` needs special care on 32-bit systems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/fat_test.c -->
# File Research: sources/os/linux/linux/fs/fat/fat_test.c

## Purpose
KUnit tests for FAT helper behavior, focused on short-name checksum and FAT timestamp conversions/truncation.

## Test Coverage
- `fat_checksum_test()` validates checksum values for representative 8.3 names.
- Parameterized `fat_time_fat2unix_test()` validates FAT date/time/centisecond to Unix `timespec64`.
- Parameterized `fat_time_unix2fat_test()` validates Unix to FAT conversion.
- `fat_time_unix2fat_clamp_test()` validates clamping before 1980 and after 2107, including timezone shifts.
- `fat_time_unix2fat_no_csec_test()` checks conversion when the centisecond output pointer is `NULL`.
- `fat_truncate_atime_test()` validates FAT atime truncation to local-day granularity.

## Important Cases
The tests include earliest and latest FAT dates, leap years including 2000 and non-leap 2100, odd-second VFAT centisecond behavior, 10 ms centisecond precision, and timezone offsets that cross date boundaries.

## Dependencies
Exercises exported helpers from `misc.c` and inline `fat_checksum()` from `fat.h`. Uses a zeroed fake `msdos_sb_info` with only timestamp offset fields populated.

## Research Notes
The test file documents the intended FAT timestamp range and timezone semantics. It does not cover directory, cluster, allocation, or mount behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/fat_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/fatent.c -->
# File Research: sources/os/linux/linux/fs/fat/fatent.c

## Purpose
Implements low-level FAT table entry access, mutation, free-space allocation, cluster freeing, free-space counting, and trim/discard support for FAT12, FAT16, and FAT32.

## Main Responsibilities
- Provides variant-specific FAT entry operations through `struct fatent_operations`.
- Reads/writes FAT entries, including FAT12 entries that can straddle block boundaries.
- Mirrors primary FAT changes to backup FATs.
- Allocates clusters and links them into chains.
- Frees cluster chains, optionally issuing discard.
- Counts free clusters and updates FAT32 FSINFO state.
- Implements `FITRIM` cluster scanning.

## Key Interfaces
- `fat_ent_access_init()`: selects FAT12/16/32 operations and initializes `fat_lock`.
- `fat_ent_read()` / `fat_ent_write()`: public read/write operations for one FAT entry.
- `fat_alloc_clusters()`: finds free entries, marks them EOF, links multiple allocated clusters, mirrors writes, updates free counts.
- `fat_free_clusters()`: walks a chain, marks entries free, mirrors writes, batches buffer syncing, and optionally discards freed extents.
- `fat_count_free_clusters()`: sequentially scans FAT entries with readahead.
- `fat_trim_fs()`: trims free cluster runs within a requested byte range.

## Important Behavior
FAT12 access uses a global `fat12_entry_lock` around nibble-level read/write because one entry shares bytes with neighbors. FAT16 and FAT32 are aligned pointer accesses, with FAT32 preserving the high reserved nibble on writes.

`fat_alloc_clusters()` holds `sbi->fat_lock` while scanning and modifying free entries. It starts near `prev_free + 1`, wraps at `max_cluster`, updates `prev_free`, decrements `free_clusters` when valid, and rolls back by freeing already allocated clusters if a later sync/mirror error happens.

`fat_free_clusters()` treats encountering a free entry inside a chain as corruption. It updates `free_clusters`, marks FSINFO dirty, and batches mirrored buffer writes to avoid excessive I/O.

`fat_trim_fs()` converts a byte range into cluster indices, scans for free runs meeting `minlen`, handles fatal signals, and temporarily drops `fat_lock` around rescheduling after releasing held FAT buffers.

## Dependencies
Uses geometry and operations from `msdos_sb_info`, buffer-head I/O, block discard helpers, metadata buffer tracking, and logging/sync helpers from `misc.c`.

## Research Notes
This file is the serialization center for FAT table mutations. The public callers rely on `fat_lock` for FAT entry consistency, while higher layers separately protect inode size/chain state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/fatent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/file.c -->
# File Research: sources/os/linux/linux/fs/fat/file.c

## Purpose
Implements regular-file operations, FAT ioctls, fsync, fallocate, truncation, getattr/setattr, and file attribute reporting.

## Main Responsibilities
- Handles FAT-specific ioctls for DOS attributes, volume id, and trim.
- Defines `fat_file_operations` and `fat_file_inode_operations`.
- Implements FAT fsync over file metadata, FAT metadata, and block-device flush.
- Supports preallocation through `fallocate`.
- Frees cluster chains on truncate.
- Translates VFS setattr/getattr into FAT semantics.

## Key Interfaces
- `fat_generic_ioctl()`: dispatches FAT attribute, volume id, and `FITRIM` commands.
- `fat_file_fsync()`: syncs file metadata buffers, FAT metadata buffers, then flushes block device.
- `fat_truncate_blocks()`: frees clusters after a target offset and adjusts `mmu_private`.
- `fat_fileattr_get()`: reports immutable and casefold/case-preserving flags.
- `fat_getattr()`: fills `kstat`, reports cluster block size, optional NFS `i_pos` ino, and VFAT birth time.
- `fat_setattr()`: applies mode/uid/gid/size/time changes under FAT restrictions.

## Important Behavior
`fat_ioctl_set_attributes()` masks off invalid bits, prevents changing volume/dir bits, applies the read-only attribute through chmod-like mode changes, enforces `sys_immutable`, calls LSM setattr checks, then updates FAT attributes.

`fat_fallocate()` supports only normal extension and `FALLOC_FL_KEEP_SIZE`. KEEP_SIZE allocates clusters without zeroing if the requested range exceeds current on-disk allocation; non-KEEP_SIZE delegates to expanding truncate via `fat_cont_expand()`.

`fat_free()` invalidates the cluster cache before chain changes, writes inode size/start-cluster changes first, writes EOF at the kept cluster if truncating partially, updates `i_blocks`, and frees the remaining chain.

`fat_setattr()` preserves old FAT behavior for quiet failures, rejects uid/gid changes away from mounted uid/gid, sanitizes modes to all-or-none writable semantics, zeroes partial truncate pages, and truncates FAT timestamps manually rather than relying on generic setattr copying.

## Dependencies
Uses cluster allocation/free from `fatent.c` and `misc.c`, mapping/truncation from `inode.c`, and attribute helpers from `fat.h`.

## Research Notes
FAT has no native Unix ownership/mode model, so this file enforces mount-option-derived invariants instead of direct metadata persistence. `mmu_private` is central to avoiding writes into unallocated holes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/inode.c -->
# File Research: sources/os/linux/linux/fs/fat/inode.c

## Purpose
Core FAT filesystem implementation: address-space mapping, inode lifecycle, inode hashing, mount option parsing, superblock reading, root/inode construction, writeback, statfs, module initialization, and shared FAT mount context setup.

## Main Responsibilities
- Maps file blocks to FAT clusters for buffered, direct, and bmap I/O.
- Implements FAT address-space operations.
- Maintains inode caches keyed by on-disk directory entry position and directory start cluster.
- Builds VFS inodes from FAT directory entries.
- Reads and validates the BIOS Parameter Block and optional DOS 1.x defaults.
- Fills the superblock, loads NLS tables, creates root/FAT/FSINFO inodes.
- Parses and displays FAT/msdos/vfat mount options.
- Writes inode metadata back to directory entries.
- Initializes/destroys FAT inode and cluster-cache slabs.

## Key Interfaces
- `fat_add_cluster()`: allocates and appends one cluster.
- `fat_block_truncate_page()`: zeroes partial block tail on truncate.
- `fat_attach()` / `fat_detach()` / `fat_iget()`: manage on-disk-position inode hash.
- `fat_fill_inode()` / `fat_build_inode()`: populate or create VFS inodes from directory entries.
- `fat_sync_inode()`: writes one FAT inode synchronously.
- `fat_reconfigure()`: remount handling and dirty-state changes.
- `fat_parse_param()`: shared parser for core, msdos, and vfat mount options.
- `fat_fill_super()`: full FAT mount path.
- `fat_flush_inodes()`: optional flush behavior for mounts with `flush`.
- `fat_init_fs_context()` / `fat_free_fc()`: shared fs_context allocation and defaults.

## Important Behavior
The block mapping path uses `__fat_get_block()`. If the block already maps, it returns the physical block span. If creating and the block equals `mmu_private`, it allocates a cluster when needed, advances `mmu_private`, remaps, marks the buffer new, and detects corrupt file size/chain states.

`fat_direct_IO()` rejects direct writes that would extend beyond `mmu_private`, forcing buffered writes so holes can be zero-filled and allocation state updated correctly.

Inode identity is deliberately independent of disk position. `i_ino` is generated, while `i_pos` points to the directory entry and is used by FAT’s own hash. NFS nostale mode uses `i_pos` file handles and a directory hash by logical start cluster.

`fat_fill_inode()` distinguishes directory versus regular file setup, calculates directory size by walking to EOF, sets link count from subdirectory count, applies `showexec`, `sys_immutable`, attributes, timestamps, birth time, and rounded block count.

`fat_fill_super()` validates BPB fields, handles logical sector size changes, discovers FAT12/16/32 geometry, reads FAT32 FSINFO, validates cluster count, initializes locks/hash tables/FAT operations, loads NLS codepages, creates internal inodes, builds root, warns for discard without support, and marks the volume dirty on mount.

## Mount Options
Core options include uid/gid, umask/dmask/fmask, allow_utime, codepage, usefree, nocase, quiet, showexec, sys_immutable, flush, timezone/time_offset, errors policy, discard, NFS mode, and DOS 1.x floppy fallback. VFAT adds iocharset, shortname policy, utf8, unicode escaping, numtail, and rodir. MSDOS adds dots/dotsOK.

## Dependencies
This file is the hub for all FAT subsystem files. It calls directory helpers, FAT entry operations, cache/block mapping helpers, timestamp/error helpers, and exposes common functionality to msdos/vfat modules.

## Research Notes
The mount path has many compatibility accommodations: optional DOS 1.x static BPB, permissive first-FAT-entry media validation, FSINFO trust only with `usefree`, UTF-8 warnings, and read-only enforcement for `nfs=nostale_ro`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/misc.c -->
# File Research: sources/os/linux/linux/fs/fat/misc.c

## Purpose
Shared FAT utility implementation for error handling, FSINFO flushing, chain append, timestamp conversion/truncation, inode time updates, and buffer-head syncing.

## Main Responsibilities
- Implements FAT error policy: continue, panic, or remount read-only.
- Prints FAT-prefixed kernel messages.
- Flushes FAT32 free-cluster/next-cluster FSINFO fields.
- Appends newly allocated clusters to inode chains.
- Converts between FAT date/time fields and Unix `timespec64`.
- Applies FAT timestamp granularity rules.
- Syncs arrays of dirty buffer heads.

## Key Interfaces
- `__fat_fs_error()`: central filesystem corruption/error handler.
- `_fat_msg()`: FAT message printer used by `fat_msg()`.
- `fat_clusters_flush()`: writes FAT32 FSINFO free cluster hints.
- `fat_chain_add()`: links new clusters to an inode chain and updates block count.
- `fat_time_fat2unix()` / `fat_time_unix2fat()`: FAT/Unix timestamp conversion.
- `fat_truncate_atime()`: truncates atime to local midnight.
- `fat_truncate_time()` / `fat_update_time()`: applies FAT time granularity to inodes.
- `fat_sync_bhs()`: writes and waits for buffer-head arrays.

## Important Behavior
`__fat_fs_error()` only logs if the caller requested reporting, then follows the mount `errors=` policy. The default remount-read-only path sets `SB_RDONLY` and logs the transition.

`fat_chain_add()` locates the current EOF, writes the previous last cluster to point at the new cluster, or sets `i_start/i_logstart` for an empty file. It checks expected file-cluster count against `i_blocks`, invalidating the FAT cluster cache on mismatch.

Timestamp conversion honors either explicit `time_offset`/`tz=UTC` mount options or the kernel timezone fallback. FAT dates are clamped to 1980-01-01 through 2107-12-31. mtime/ctime are truncated to 2-second granularity, while atime is truncated to day granularity.

## Dependencies
Uses FAT entry read/write, inode sync, cache invalidation, and metadata state from `fat.h`.

## Research Notes
This file encodes much of FAT’s externally visible compatibility behavior, especially timestamps. KUnit coverage in `fat_test.c` targets these timestamp helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/namei_msdos.c -->
# File Research: sources/os/linux/linux/fs/fat/namei_msdos.c

## Purpose
Implements the `msdos` filesystem namespace layer: 8.3-only name formatting, lookup, create, mkdir, unlink, rmdir, rename, dentry hashing/comparison, mount registration, and fs_context hooks.

## Main Responsibilities
- Converts user names to strict/normal/relaxed MS-DOS 8.3 names.
- Handles `dotsOK` hidden-file dot presentation.
- Provides msdos dentry hash/compare operations based on formatted 8.3 names.
- Implements directory inode operations for creation, deletion, lookup, and rename.
- Registers the `msdos` filesystem type.

## Key Interfaces
- `msdos_format_name()`: validates and formats user names into 11-byte 8.3 form.
- `msdos_find()`: formats a name and scans the directory.
- `msdos_lookup()`: finds and builds an inode, then splices aliases.
- `msdos_add_entry()`: writes a single short directory entry.
- `msdos_create()`, `msdos_mkdir()`, `msdos_unlink()`, `msdos_rmdir()`: namespace operations.
- `do_msdos_rename()` / `msdos_rename()`: rename implementation.
- `msdos_init_fs_context()`: initializes shared FAT context with `is_vfat=false`.

## Important Behavior
`msdos_format_name()` rejects invalid characters according to mount `check=` mode, uppercases lowercase unless `nocase`, handles leading dot names only with `dotsOK`, prohibits trailing spaces, and maps first-byte 0xE5 to 0x05.

`msdos_find()` applies the hidden attribute distinction for `dotsOK`: `.foo` and `foo` can map to the same 8.3 short name but are distinguished by `ATTR_HIDDEN`.

Create and mkdir explicitly reject conflicts between dot-hidden and non-hidden forms by scanning the formatted short name before insertion.

Rename is careful with directories: it updates `..` when moving across parents, adjusts link counts, detaches and reattaches inode hash positions, handles the special `foo` to `.foo` hidden-attribute-only rename, and tries rollback paths if inode or dotdot updates fail.

## Dependencies
Uses shared FAT directory, inode, time, sync, and attribute helpers. `setup()` installs `msdos_dir_inode_operations` and `msdos_dentry_operations`, then enables `SB_NOATIME`.

## Research Notes
The msdos namespace is short-name-only and lacks VFAT long-name slot management. Most complexity comes from legacy name validation and hidden-dot compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/namei_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/namei_vfat.c -->
# File Research: sources/os/linux/linux/fs/fat/namei_vfat.c

## Purpose
Implements the `vfat` namespace layer: long filename handling, short alias generation, case-sensitive/case-insensitive dentry behavior, lookup/create/delete/mkdir/rename including `RENAME_EXCHANGE`, and filesystem registration.

## Main Responsibilities
- Provides dentry hash/compare/revalidate logic for VFAT names.
- Converts user names to UTF-16 long-name slots.
- Generates unique 8.3 aliases for long names.
- Builds long-name slot chains plus short entries.
- Implements VFAT create, lookup, unlink, rmdir, mkdir, rename, and exchange.
- Registers the `vfat` filesystem type.

## Key Interfaces
- `vfat_hash()` / `vfat_hashi()`, `vfat_cmp()` / `vfat_cmpi()`: case-sensitive or case-insensitive dentry operations.
- `vfat_revalidate()` / `vfat_revalidate_ci()`: validates negative dentries using parent i_version.
- `vfat_create_shortname()`: creates unique 8.3 aliases and lower-case flags.
- `xlate_to_uni()`: converts input names to UTF-16, including `uni_xlate` escape decoding.
- `vfat_build_slots()`: builds long-name slots and final short entry.
- `vfat_add_entry()` / `vfat_find()`: shared add/search helpers.
- `vfat_lookup()`, `vfat_create()`, `vfat_mkdir()`, `vfat_unlink()`, `vfat_rmdir()`: namespace operations.
- `vfat_rename2()`: dispatches normal rename or exchange rename.

## Important Behavior
VFAT strips trailing dots from lookup/hash names. In case-insensitive mode, negative dentries are dropped for create/rename target intents so a newly specified case can be used. Negative dentries store the parent inode version to detect short-alias creation invalidating a previous negative lookup.

`vfat_create_shortname()` decides whether a name can be represented as a valid short name, whether a long-name slot is still required for case or multibyte preservation, and whether numeric tails are needed. It tries `~1` through `~9`, then uses jiffies-derived hexadecimal tails.

`vfat_build_slots()` converts to UTF-16, rejects bad characters/trailing space, creates an alias, emits long-name slots in reverse order with checksum when needed, then creates the short entry with VFAT creation/access/modify timestamps.

Rename detaches and reattaches inode `i_pos` mappings. Cross-directory directory renames update `..` and parent link counts. `RENAME_EXCHANGE` swaps two inode positions and updates both `..` entries when needed, with rollback attempts and corruption reporting on failures.

## Dependencies
Uses shared FAT directory entry allocation/search/removal, inode attach/detach/build/sync, timestamp helpers, NLS tables from mount setup, and dentry/VFS APIs.

## Research Notes
This file is where VFAT compatibility policy is most visible: trailing-dot semantics, casefold behavior, long-name checksum linkage, numeric-tail aliasing, and negative-dentry invalidation all protect the dual-name model of long names plus 8.3 aliases.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/namei_vfat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/nfs.c -->
# File Research: sources/os/linux/linux/fs/fat/nfs.c

## Purpose
Implements FAT export operations for NFS, including normal inode-number file handles and `nfs=nostale_ro` file handles based on on-disk directory-entry position.

## Main Responsibilities
- Encodes/decodes FAT-specific file handles.
- Looks up inodes by VFS inode number or by FAT `i_pos` depending on NFS mode.
- Rebuilds inodes from directory entries for nostale read-only export.
- Finds parent dentries for disconnected exported directories.
- Provides two export operation tables.

## Key Interfaces
- `fat_dget()`: finds a cached directory inode by logical start cluster.
- `fat_ilookup()` / `__fat_nfs_get_inode()`: retrieve or rebuild exported inodes.
- `fat_encode_fh_nostale()`: encodes generation and `i_pos`, optionally parent `i_pos`.
- `fat_fh_to_dentry()` / `fat_fh_to_parent()`: generic file-handle decode for stale-rw mode.
- `fat_fh_to_dentry_nostale()` / `fat_fh_to_parent_nostale()`: `i_pos`-based decode for nostale mode.
- `fat_get_parent()`: resolves parent via `..`, cache lookup, or rebuild.
- `fat_export_ops` / `fat_export_ops_nostale`: export tables selected at mount.

## Important Behavior
In `FAT_NFS_NOSTALE_RO`, file handles contain the on-disk directory-entry position instead of transient `i_ino`. If an inode is not cached, `__fat_nfs_get_inode()` reads the directory-entry block and rebuilds the inode unless the entry is free.

`fat_rebuild_parent()` reconstructs a missing parent by reading the child directory’s first cluster, extracting `.` and `..`, creating a temporary grandparent inode if needed, then scanning for the child start cluster.

## Dependencies
Relies on inode hash and directory hash maintenance from `inode.c`, directory scanning from `dir.c`, and FAT position helpers from `fat.h`.

## Research Notes
The nostale mode is forced read-only during mount in `fat_fill_super()`, which avoids handle instability from directory-entry relocation or reuse during writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fcntl.c -->
# File Research: sources/os/linux/linux/fs/fcntl.c

## Purpose
Implements Linux `fcntl` and `fcntl64` system call handling, file-owner management for async notifications, read/write lifetime hints, lease/delegation command dispatch, compat flock conversion, and fasync signal delivery infrastructure.

## Main Responsibilities
- Implements `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, dupfd commands, lock commands, owner/signal commands, leases, dnotify, pipe sizing, memfd seals, write hints, and delegations.
- Manages `struct fown_struct` allocation, ownership, credentials, pid references, and release.
- Sends `SIGIO`/custom async I/O signals and `SIGURG`.
- Maintains fasync lists used by drivers and lease code.
- Provides compat syscall handling for 32-bit userspace flock structures.

## Key Interfaces
- `setfl()`: validates and updates mutable file status flags.
- `file_f_owner_allocate()` / `file_f_owner_release()`: lifecycle for per-file owner state.
- `__f_setown()`, `f_setown()`, `f_delown()`, `f_getown()`: legacy owner APIs.
- `f_setown_ex()` / `f_getown_ex()`: extended owner APIs with PID/TGID/PGRP selection.
- `do_fcntl()`: central command dispatcher.
- `SYSCALL_DEFINE3(fcntl)` and `fcntl64`: syscall entry points.
- `do_compat_fcntl64()` and compat syscalls: compat lock structure handling.
- `send_sigio()` / `send_sigurg()`: notification delivery.
- `fasync_helper()`, `fasync_insert_entry()`, `fasync_remove_entry()`, `kill_fasync()`: fasync list management.
- `fcntl_init()`: initializes the fasync slab cache.

## Important Behavior
`setfl()` allows only `SETFL_MASK` bits to change, prevents clearing append on append-only writable files, restricts `O_NOATIME` to owner/capable callers, maps `O_NDELAY` to `O_NONBLOCK` where needed, validates `O_DIRECT`, and delegates filesystem-specific validation through `check_flags`.

File ownership stores pid, pid type, uid, and euid under `f_owner->lock`. Signals are permission-checked against saved owner credentials and LSM hooks before delivery.

`do_fcntl()` first handles generic fd/status commands, then locking via `fcntl_getlk`/`fcntl_setlk`, owner commands, leases, dnotify, pipe, memfd, write-hint, and delegation commands. `FMODE_PATH` descriptors are restricted to a small safe command set by `check_fcntl_cmd()`.

Compat handling converts `compat_flock` and `compat_flock64`, maps 64-bit lock commands, and guards overflow for 32-bit `struct flock` results.

Fasync list updates hold both `filp->f_lock` and global `fasync_lock`; removal uses RCU freeing. `kill_fasync()` traverses under RCU and sends signals through the file owner if present.

## Dependencies
Calls into VFS file table helpers, file locking, leases/delegations, dnotify, pipe, memfd, LSM hooks, pid namespaces, credentials, compat/uaccess helpers, and polling signal code.

## Research Notes
This file is not FAT-specific; it is generic VFS/syscall infrastructure included in the same research group. It interacts with FAT indirectly because FAT file and directory operations expose `.setlease = generic_setlease`, and all open FAT files are subject to these generic fcntl paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fcntl.c -->