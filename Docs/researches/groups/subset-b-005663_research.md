# Research Report: subset-b-005663

Grouped research for the FAT filesystem implementation and generic `fcntl.c` in `sources/distributed-fs/ceph-client`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/cache.c -->
# sources/distributed-fs/ceph-client/fs/fat/cache.c

## Purpose
`cache.c` implements per-inode cluster-chain lookup caching and logical-to-physical block mapping for FAT files. FAT stores file extents as linked lists of cluster numbers in the FAT table, so random access otherwise requires walking from the first cluster. This file keeps a small LRU of contiguous logical file cluster to disk cluster runs and provides the mapping path used by buffered IO, direct IO, directory iteration, and `bmap`.

## Important APIs, Types, and Functions
- `struct fat_cache` is an in-memory cache record for one contiguous run: file cluster `fcluster`, disk cluster `dcluster`, and `nr_contig`.
- `struct fat_cache_id` is a temporary lookup/build accumulator tagged with `cache_valid_id` so stale walkers do not install entries after invalidation.
- `fat_cache_init()` / `fat_cache_destroy()` create and destroy the `fat_cache` slab.
- `fat_cache_lookup()`, `fat_cache_merge()`, `fat_cache_add()`, and `fat_cache_inval_inode()` manage the per-inode LRU under `MSDOS_I(inode)->cache_lru_lock`.
- `fat_get_cluster()` walks the FAT chain to resolve a logical cluster and updates the cache with contiguous runs.
- `fat_get_mapped_cluster()` and `fat_bmap()` translate VFS sectors to physical block numbers and mapped block counts.

## Control Flow
Lookup starts in `fat_bmap()`. FAT12/16 root directories are a special fixed-area case and map directly from `sbi->dir_start`; all other files call `fat_get_mapped_cluster()` after EOF bounds are checked. `fat_get_mapped_cluster()` computes the logical cluster and sector offset, calls `fat_bmap_cluster()`, then returns the physical sector from `fat_clus_to_blknr()`.

`fat_get_cluster()` validates the inode start cluster, handles cluster zero immediately, attempts an LRU lookup, and then iterates FAT entries through `fat_ent_read()`. It stops on the requested cluster, EOF, free-entry corruption, read error, or a chain-loop guard based on `s_maxbytes`. During iteration, `cache_contiguous()` detects whether the next disk cluster extends the current run; otherwise `cache_init()` starts a new run. The final run is installed with `fat_cache_add()`.

## State and Persistence
The cache itself is volatile per-inode state. Persistent state is not written here except indirectly through dependencies that read FAT entries. `cache_valid_id` is incremented during invalidation so a walker that observed old state cannot repopulate invalid entries. `fat_bmap()` consults `i_size`, `i_blocks`, and `MSDOS_I(inode)->mmu_private` to avoid mapping beyond logical EOF unless allocation is in progress.

## Dependencies and Integration Points
This file depends on FAT entry access from `fatent.c`, geometry and helpers from `fat.h`, corruption reporting from `misc.c`, and inode fields initialized in `inode.c`. It is called by address-space operations in `inode.c`, directory readers in `dir.c`, truncation paths in `file.c`, and export/rebuild logic that scans directories.

## Risks and Edge Cases
Corrupt chains can present invalid start clusters, free entries inside a file, EOF before the requested cluster, or loops; this file reports those as FAT filesystem errors and usually returns `-EIO`. The cache is intentionally tiny (`FAT_MAX_CACHE` 8), so workloads with many seeks still walk the FAT. Correct locking is important: LRU mutation is spinlocked, while FAT table serialization is handled lower in `fatent.c`.

## Test Signals
There is no direct KUnit suite for this cache. Strong signals come from filesystem IO tests that exercise sparse extension, truncate, directory traversal, `bmap`, fallocate keep-size, and corruption images with broken cluster chains. Cache invalidation should be covered by truncate and unlink/rmdir cases because those free clusters while readers may later remap the inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/dir.c -->
# sources/distributed-fs/ceph-client/fs/fat/dir.c

## Purpose
`dir.c` implements FAT directory entry iteration, VFAT long-name parsing, short-name display conversion, directory ioctls, directory emptiness/scanning helpers, and low-level slot insertion/removal. It is the shared directory engine used by both `msdos` and `vfat` namei layers.

## Important APIs, Types, and Functions
- `fat_get_entry()` and `fat__get_entry()` walk directory entries by logical byte offset, using `fat_bmap()` and block reads.
- `fat_parse_long()` reconstructs VFAT long names from `ATTR_EXT` slots, validates ordering and alias checksums, and falls back cleanly on malformed slot chains.
- `fat_parse_short()` converts 8.3 entries into visible names using mount shortname policy and NLS conversion.
- `fat_search_long()`, `fat_scan()`, and `fat_scan_logstart()` locate entries by long/short name or start cluster and fill `struct fat_slot_info`.
- `__fat_readdir()` backs normal readdir and legacy `VFAT_IOCTL_READDIR_*` ioctls.
- `fat_dir_empty()`, `fat_subdirs()`, and `fat_get_dotdot_entry()` provide namei and NFS helper logic.
- `fat_add_entries()`, `fat_alloc_new_dir()`, and `fat_remove_entries()` mutate directory slots.

## Control Flow
Directory reads use `fat_get_entry()` as a fast path when the next entry is still in the same buffer; otherwise `fat__get_entry()` maps the next directory block, optionally readaheads an entire cluster, and reads the block. `__fat_readdir()` serializes on `sbi->s_lock`, emits synthetic root `.` and `..`, filters free/deleted/volume entries, optionally reconstructs long names, and emits either the long name or the short name to the VFS `dir_context`.

Search uses similar parsing but compares the requested name against both the short display form and reconstructed VFAT long name. On a match, `fat_slot_info` records the starting slot offset, slot count, short entry pointer, buffer head, and encoded `i_pos`.

Mutation is staged for crash tolerance. `fat_remove_entries()` marks the short slot deleted first, then removes preceding long slots. `fat_add_entries()` first searches for enough free contiguous slots, writes long slots before the short slot, and if no space exists allocates one or two new clusters, initializes them with the new entries, appends the cluster chain, and updates directory size.

## State and Persistence
Persistent directory state is a sequence of 32-byte `struct msdos_dir_entry` and `struct msdos_dir_slot` records. Dirty buffers are tracked through `MSDOS_I(dir)->i_metadata_bhs` using metadata-buffer helpers, then synchronously flushed for `IS_DIRSYNC(dir)`. Directory ctime/mtime are truncated via `fat_truncate_time()`, i_version is bumped on removals and additions where needed by callers, and cluster allocation changes are delegated to `fatent.c` and `misc.c`.

## Dependencies and Integration Points
`dir.c` depends on block mapping from `cache.c`, cluster allocation and FAT entry writes from `fatent.c` / `misc.c`, timestamp conversion from `misc.c`, inode lookup/build from `inode.c`, and VFS directory APIs. `namei_msdos.c` and `namei_vfat.c` call the exported scan/add/remove helpers. `nfs.c` uses dotdot and logstart scanning when reconnecting exported directories.

## Risks and Edge Cases
Malformed long-name slot chains are common on damaged media; this code must distinguish invalid records from EOF and from a short entry that is not part of a long name. Slot insertion spans block and cluster boundaries, so rollback through `__fat_remove_entries()` matters after partial writes. FAT12/16 root directories cannot grow; FAT32 and subdirectories can. Legacy directory ioctls copy two records to userspace and must preserve EOF behavior expected by old programs.

## Test Signals
Useful test coverage includes VFAT long-name lookup/readdir, deleted slot reuse, directory growth at 512-byte cluster boundaries, sync-directory mounts, root directory limits on FAT12/16, hidden/dots display on msdos, and corruption cases with broken long-name checksums. NFS reconnect tests also exercise `fat_scan_logstart()` and `fat_get_dotdot_entry()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/fat.h -->
# sources/distributed-fs/ceph-client/fs/fat/fat.h

## Purpose
`fat.h` is the private header for the FAT core, msdos, vfat, and NFS export code. It defines mount options, in-core superblock and inode state, slot lookup structures, FAT-entry abstractions, inline helpers for mode/attribute/cluster conversion, and cross-file function declarations.

## Important APIs, Types, and Functions
- `struct fat_mount_options` captures parsed mount policy: uid/gid, masks, codepage, iocharset, timestamp offset, shortname behavior, error policy, NFS mode, UTF-8/unicode escape behavior, discard, flush, and FAT-specific flags.
- `struct msdos_sb_info` is the FAT superblock state: layout geometry, FAT table location, root directory info, FSINFO counters, locks, NLS tables, inode and directory hashes, special FAT/FSINFO inodes, and dirty-state tracking.
- `struct msdos_inode_info` extends VFS inodes with cluster cache, FAT chain start, on-disk directory-entry position, hash nodes, truncate lock, creation time, and metadata-buffer tracking.
- `struct fat_slot_info` describes a located directory entry and its VFAT slot span.
- Inline helpers include `MSDOS_SB()`, `MSDOS_I()`, `is_fat12/16/32()`, `fat_make_mode()`, `fat_make_attrs()`, `fat_checksum()`, `fat_clus_to_blknr()`, `fat_get_start()`, and `fat_set_start()`.
- The header declares the exported functions implemented in `cache.c`, `dir.c`, `fatent.c`, `file.c`, `inode.c`, `misc.c`, and `nfs.c`.

## Control Flow
The header is not executable control flow, but it defines the contracts that connect mount parsing, block mapping, directory entry mutation, FAT entry access, and VFS operations. Callers use `fat_get_start()` and `fat_set_start()` to handle FAT32 high cluster bits transparently, and use `fat_make_mode()` / `fat_make_attrs()` to translate between FAT attributes and Linux permission bits.

## State and Persistence
The central persistent bridge is `i_pos`, an encoded directory-entry location, and `i_start` / `i_logstart`, the first cluster for file data. `msdos_sb_info` mirrors persistent boot-sector and FSINFO fields such as FAT layout, root cluster, volume ID, free cluster counts, and dirty state. `msdos_inode_info::i_metadata_bhs` groups metadata buffers that need fsync.

## Dependencies and Integration Points
This header depends on Linux VFS, buffer-head, NLS, hash, ratelimit, msdos on-disk structures, and fs_context parser APIs. It is included by all FAT implementation files in this subset and is the main integration surface between the common FAT core and the msdos/vfat filesystem modules.

## Risks and Edge Cases
Inline helpers encode subtle semantics. `fat_mode_can_hold_ro()` treats directory read-only differently based on `rodir`; changing it affects chmod and attribute ioctls. `fat_i_pos_read()` needs locking on 32-bit systems because `loff_t` is not atomically readable. FAT12/16/32 maximum cluster handling and FAT32 high cluster bits are centralized here, so mistakes propagate widely.

## Test Signals
Compile coverage across FAT, msdos, vfat, and NFS export modules is important because this header defines shared structures. KUnit coverage in `fat_test.c` directly validates `fat_checksum()` and timestamp helpers declared here. Broader mount, chmod, getattr, NFS export, and long-name tests validate the structure contracts indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/fat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/fat_test.c -->
# sources/distributed-fs/ceph-client/fs/fat/fat_test.c

## Purpose
`fat_test.c` is a KUnit suite for small deterministic FAT helpers, mainly short-name checksum and timestamp conversion/truncation behavior. It gives direct regression coverage for date range clamping, timezone offsets, leap-year handling, VFAT centisecond fields, and FAT atime granularity.

## Important APIs, Types, and Functions
- `fat_checksum_test()` validates the VFAT alias checksum helper for representative 8.3 names.
- `struct fat_timestamp_testcase`, `struct fat_unix2fat_clamp_testcase`, and `struct fat_truncate_atime_testcase` define parameterized time cases.
- `fat_test_set_time_offset()` initializes a fake `msdos_sb_info` with controlled timestamp offset policy.
- `fat_time_fat2unix_test()`, `fat_time_unix2fat_test()`, `fat_time_unix2fat_clamp_test()`, `fat_time_unix2fat_no_csec_test()`, and `fat_truncate_atime_test()` exercise exported helpers from `misc.c`.
- `kunit_test_suites(&fat_test_suite)` registers the suite as `fat_test`.

## Control Flow
The suite builds static parameter arrays, exposes them through `KUNIT_ARRAY_PARAM`, and runs each helper against one testcase at a time. Each test prepares a fake superblock info object, calls the conversion function, and checks exact seconds, nanoseconds, date, time, or centisecond outputs.

## State and Persistence
No filesystem state is persisted. The tests intentionally avoid mounting a FAT image and instead isolate pure conversion logic using in-memory `msdos_sb_info` values. This makes the suite fast and deterministic but limits coverage to helper-level behavior.

## Dependencies and Integration Points
The tests include `fat.h` and rely on `fat_time_fat2unix()`, `fat_time_unix2fat()`, and `fat_truncate_atime()` being exported for test access. The covered helpers are used by inode fill/writeback, directory creation, setattr, and timestamp update paths throughout the FAT implementation.

## Risks and Edge Cases
The test data targets high-risk time semantics: earliest FAT date, latest FAT date, 2100 non-leap behavior, timezone offsets that cross FAT range boundaries, odd-second VFAT resolution, 10 ms centiseconds, and atime truncation to local midnight. Gaps remain around directory slot parsing, cluster allocation, cache invalidation, mount parsing, and NLS name conversion.

## Test Signals
A passing `fat_test` suite strongly signals that timestamp helper regressions are unlikely. It does not prove on-disk writeback correctness; integration tests should still mount FAT/VFAT images and check that timestamps survive create, setattr, fsync, remount, and timezone option changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/fat_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/fatent.c -->
# sources/distributed-fs/ceph-client/fs/fat/fatent.c

## Purpose
`fatent.c` implements low-level FAT table entry access for FAT12, FAT16, and FAT32, plus cluster allocation, cluster freeing, free-space counting, and discard/trim support. It is the persistence engine for file cluster chains.

## Important APIs, Types, and Functions
- `struct fatent_operations` abstracts FAT variant behavior: entry block calculation, pointer setup, buffer reads, get/put, and next-entry iteration.
- FAT12-specific access uses `fat12_entry_lock` because 12-bit entries can straddle bytes and block boundaries.
- `fat_ent_access_init()` selects `fat12_ops`, `fat16_ops`, or `fat32_ops` and initializes `sbi->fat_lock`.
- `fat_ent_read()` reads a specific FAT entry, reusing buffers where possible.
- `fat_ent_write()` writes one entry, optionally syncs buffers, and mirrors changes to backup FATs.
- `fat_alloc_clusters()` scans for free entries, builds an EOF-terminated chain, updates free-space accounting, and mirrors dirty FAT buffers.
- `fat_free_clusters()` walks a chain, marks entries free, optionally issues discard, and updates FSINFO state.
- `fat_count_free_clusters()` and `fat_trim_fs()` perform full FAT scans with readahead.

## Control Flow
All modifying cluster operations take `sbi->fat_lock`. Entry reads compute the FAT sector and byte offset, then either update the current `fat_entry` pointer if the same buffer still contains the entry or read new buffer heads. Writes call the variant `ent_put()` function, sync if requested, then copy dirty FAT sectors to all mirrored FAT tables.

Allocation starts near `sbi->prev_free + 1`, wraps at `max_cluster`, and scans until enough `FAT_ENT_FREE` entries are found or the table is exhausted. Each found entry is immediately marked EOF, and the previous allocated entry is pointed to the new entry to form a chain. On error after partial allocation, the new chain is freed.

Freeing starts at a caller-supplied cluster, reads the next link, optionally batches discard for contiguous data clusters, marks the current FAT entry free, batches dirty buffer heads, mirrors and syncs as required, and stops at EOF. Counting and trim use sequential FAT block readahead to reduce scan cost.

## State and Persistence
Persistent state is the FAT table and its mirrors. Volatile superblock state includes `prev_free`, `free_clusters`, and `free_clus_valid`; when changed for FAT32, `mark_fsinfo_dirty()` marks the FSINFO inode for later writeback. FAT12/16/32 EOF marker encodings are normalized to `FAT_ENT_EOF` on read and translated back on write.

## Dependencies and Integration Points
This file depends on `fat.h`, buffer-head IO, block discard APIs, scheduler signal/resched checks, and metadata buffer tracking. It is used by `cache.c` for chain reads, `misc.c` for appending chains, `file.c` and `inode.c` for truncate/allocation, `dir.c` for directory growth, and `fat_generic_ioctl(FITRIM)` for discard.

## Risks and Edge Cases
FAT12 entries crossing block boundaries require two buffer heads and careful locking. Mirrored FAT updates can fail after the primary FAT was changed, causing possible on-disk inconsistency. The allocation scan is linear and can be expensive on fragmented or nearly full volumes. Free-space counters may be stale and are corrected by full scans. Discard failures of `-EOPNOTSUPP` are tolerated during trim.

## Test Signals
Useful tests mount FAT12/16/32 images, allocate and truncate files across cluster boundaries, verify mirrored FATs, run fsck after simulated sync failures, exercise fallocate rollback, and run `fstrim` with minlen and range boundaries. Corruption tests should cover free entries inside chains and bad FAT variants selected during mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/fatent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/file.c -->
# sources/distributed-fs/ceph-client/fs/fat/file.c

## Purpose
`file.c` provides regular-file VFS operations and common FAT ioctls, plus truncate, fallocate, getattr, setattr, fsync, and close-time flush behavior. It translates Linux file operations into FAT's limited attribute and cluster-chain model.

## Important APIs, Types, and Functions
- `fat_generic_ioctl()` dispatches attribute get/set, volume ID, and `FITRIM`.
- `fat_ioctl_set_attributes()` maps FAT attributes to Linux mode changes and enforces immutable/security checks.
- `fat_file_fsync()` syncs file data and metadata buffers, then flushes the block device.
- `fat_fallocate()` supports regular-file preallocation, with `FALLOC_FL_KEEP_SIZE` allocating clusters without growing i_size.
- `fat_truncate_blocks()` and internal `fat_free()` free cluster chains after a target offset.
- `fat_getattr()` returns FAT-specific block size, optional stable NFS inode number, and VFAT birth time.
- `fat_setattr()` handles chmod/chown-like restrictions, size changes, FAT timestamp truncation, and dirtying.

## Control Flow
Ioctls first validate userspace access and permissions, then use shared helpers. Attribute setting calls `mnt_want_write_file()`, locks the inode, sanitizes disallowed FAT bits, runs LSM `security_inode_setattr()`, calls `fat_setattr()`, sends fsnotify, and updates `S_IMMUTABLE` if configured.

Fallocate locks the inode, rejects unsupported flags and non-regular files, and either allocates additional clusters up to the requested keep-size reservation or expands the file via `fat_cont_expand()`. Truncation invalidates the cluster cache, writes the new start/EOF state before freeing tail clusters, updates timestamps and archive bit, and then frees the old chain through `fat_free_clusters()`.

`fat_setattr()` is careful with expansion: if the requested size grows, it zero-fills/allocates through `fat_cont_expand()` before normal setattr copy. On shrink, it truncates the partial tail block, updates i_size, and frees trailing clusters under `truncate_lock`.

## State and Persistence
This file mutates `i_mode`, FAT attribute bits, `i_start`, `i_logstart`, `i_blocks`, `mmu_private`, timestamps, and on-disk directory entries through inode writeback. Directory entry metadata is written by `fat_sync_inode()` or normal dirty inode writeback; cluster table changes are delegated to `fatent.c`. `fat_file_release()` optionally starts writeback for `flush` mounts.

## Dependencies and Integration Points
It integrates with VFS file operations, LSM hooks, fsnotify, block discard, address-space writeback in `inode.c`, FAT entry allocation/freeing, timestamp helpers, metadata-buffer helpers, and mount options in `msdos_sb_info`. Directory file operations in `dir.c` reuse `fat_generic_ioctl()` and `fat_file_fsync()`.

## Risks and Edge Cases
FAT cannot represent arbitrary Unix mode changes, ownership changes, or sparse holes. `quiet` may hide permission errors for compatibility. The archive bit and read-only bit are encoded through FAT attributes, not normal Unix metadata. Fallocate keep-size must release unused EOF blocks on eviction. Shrink/extend races are guarded by inode locks and `truncate_lock`, and direct IO write extension falls back to buffered IO in `inode.c`.

## Test Signals
Strong tests include chmod/chown behavior under masks and `quiet`, FAT attribute ioctls, immutable system files, truncate/grow/shrink across clusters, fallocate keep-size and eviction, fsync durability, `FITRIM`, volume ID ioctl, and `STATX_BTIME` on VFAT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/inode.c -->
# sources/distributed-fs/ceph-client/fs/fat/inode.c

## Purpose
`inode.c` is the FAT core mount, inode, address-space, writeback, option parsing, and module lifecycle implementation. It reads the boot sector/BPB, builds in-core superblock geometry, initializes NLS and special inodes, maps file IO to cluster allocation, and writes inode metadata back into directory entries.

## Important APIs, Types, and Functions
- `fat_add_cluster()`, `__fat_get_block()`, and `fat_get_block()` bridge pagecache block mapping to FAT cluster allocation.
- `fat_aops` defines FAT address-space behavior for read, readahead, writepages, write_begin/end, direct IO, bmap, and migration.
- `fat_attach()`, `fat_detach()`, and `fat_iget()` maintain the directory-entry-position inode hash; directory hash support backs NFS reconnect.
- `fat_fill_inode()`, `fat_build_inode()`, and `fat_read_root()` construct VFS inodes from on-disk directory entries or root geometry.
- `fat_write_inode()` / `__fat_write_inode()` persist inode size, attributes, start cluster, and timestamps to the directory entry.
- `fat_parse_param()`, `fat_init_fs_context()`, `fat_free_fc()`, and `fat_reconfigure()` manage mount options.
- `fat_fill_super()` performs full mount setup and validation.

## Control Flow
Mount begins with `fat_init_fs_context()` defaults in the msdos/vfat module, option parsing through `fat_parse_param()`, and block-device mounting through `fat_fill_super()`. `fat_fill_super()` allocates `msdos_sb_info`, sets VFS superblock operations, reads the boot sector, validates the BPB or optional DOS 1.x defaults, computes FAT/root/data layout, detects FAT type, loads NLS tables, creates the FAT and FSINFO pseudo-inodes, reads the root inode, attaches hashes, and marks the volume dirty.

File IO mapping starts in `fat_get_block()`. If an existing mapping is found, it returns a mapped buffer. For writes at `mmu_private`, it allocates a new cluster when needed, advances `mmu_private`, remaps, marks new buffers, and reports corruption if mapping still fails. Write failures truncate pagecache and free blocks beyond i_size.

Inode writeback reads the directory entry block from `i_pos`, verifies under `inode_hash_lock` that the inode still owns that position, then writes size, attrs, start cluster, mtime/date, and VFAT atime/crtime fields. If the inode was detached by unlink/rename, writeback returns without touching stale media.

## State and Persistence
Persistent state includes the boot-sector dirty bit, BPB-derived layout, FSINFO counters, FAT table through dependencies, root and directory entries, and file data clusters. In-core state includes inode caches, two hash tables, mount options, NLS tables, `free_clusters`, `prev_free`, special inodes, and metadata buffer ledgers. `fat_set_state()` marks the volume dirty on mount/remount writable and clean on unmount/remount read-only when appropriate.

## Dependencies and Integration Points
This file ties together nearly every FAT subsystem: `cache.c` for mapping, `fatent.c` for FAT access, `dir.c` for root/subdir sizing and link counts, `file.c` for inode operations, `misc.c` for timestamps/errors, and `nfs.c` export operations. It uses VFS fs_context, superblock, address-space, inode cache, mpage, direct IO, buffer-head, block-device, NLS, random generation, and idmapped mount APIs.

## Risks and Edge Cases
Mount validation must reject malformed BPBs while tolerating real-world oddities such as zero geometry fields and optional DOS 1.x floppy defaults. FAT32 FSINFO may be invalid or stale. Inode identity is complex because `i_ino` is synthetic while persistence is tied to `i_pos`; rename/unlink races are handled by detach/attach and writeback revalidation. Cluster allocation during write has to keep `mmu_private`, `i_blocks`, and FAT chains consistent. NFS `nostale_ro` forces read-only because stable handles are based on directory-entry positions.

## Test Signals
Mount tests should cover FAT12/16/32 images, invalid BPBs, DOS 1.x floppy mode, NLS failures, dirty-bit behavior, FSINFO counters, mount options, remount read-only/read-write, and NFS option behavior. IO tests should cover buffered writes, direct IO fallback, truncate after failed writes, bmap, inode writeback after rename/unlink, eviction of fallocated blocks, and fsck clean unmount state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/misc.c -->
# sources/distributed-fs/ceph-client/fs/fat/misc.c

## Purpose
`misc.c` provides common FAT utility behavior: filesystem error handling, printk wrappers, FAT32 FSINFO cluster counter flushing, appending allocated cluster chains to inodes, FAT timestamp conversion/truncation, inode timestamp update policy, and synchronous buffer-head write helpers.

## Important APIs, Types, and Functions
- `__fat_fs_error()` implements the `errors=` mount policy: continue, panic, or remount read-only.
- `_fat_msg()` is the underlying FAT message printer used by indexed `fat_msg()` macros.
- `fat_clusters_flush()` writes `free_clusters` and `prev_free` to FAT32 FSINFO.
- `fat_chain_add()` appends a newly allocated cluster chain to an inode and updates `i_start`, `i_logstart`, and `i_blocks`.
- `fat_time_fat2unix()` and `fat_time_unix2fat()` convert between FAT date/time fields and `timespec64`.
- `fat_truncate_atime()`, `fat_truncate_time()`, and `fat_update_time()` enforce FAT timestamp granularity.
- `fat_sync_bhs()` writes and waits for an array of buffer heads.

## Control Flow
Error reporting prints conditionally based on ratelimit/report flags, then either panics or flips `SB_RDONLY` for remount-read-only policy. `fat_clusters_flush()` reads the FSINFO sector, validates signatures, updates counters if known, and marks the buffer dirty.

`fat_chain_add()` locates the current EOF cluster if the inode already has a chain, writes the previous EOF entry to point at the new chain, or initializes an empty inode start cluster. It verifies `i_blocks` matches the computed append position, invalidates the cluster cache on mismatch, and then increments block count.

Timestamp conversion decodes/encodes FAT bitfields with timezone offset handling. `fat_time_unix2fat()` clamps before 1980 to the earliest FAT date and after 2107 to the latest FAT date. `fat_truncate_time()` skips the root inode, truncates atime to local midnight, and keeps ctime equal to mtime at two-second resolution.

## State and Persistence
This file mutates superblock read-only state on serious errors, FAT32 FSINFO sectors, inode chain starts, `i_blocks`, inode timestamps, and dirty flags. It does not allocate clusters itself; it connects already allocated chains to inodes and relies on `fatent.c` for FAT entry writes.

## Dependencies and Integration Points
It depends on `fat.h`, VFS inode dirtying, buffer-head IO, ratelimit state, timezone globals, and metadata sync helpers. It is used by mount/unmount, file creation, directory growth, write paths, setattr, fsync, and KUnit tests.

## Risks and Edge Cases
Time conversion is historically fragile because FAT stores local time, has a 1980-2107 date range, two-second mtime resolution, 24-hour atime resolution, and VFAT centiseconds. `fat_chain_add()` must avoid exposing a cluster chain without corresponding inode metadata under synchronous directory semantics. FSINFO signatures may be invalid; the code warns but does not fail the flush.

## Test Signals
`fat_test.c` directly covers checksum and timestamp conversion/truncation. Integration tests should verify `errors=panic/remount-ro/continue`, FAT32 FSINFO update after allocation/free, directory creation with sync options, and timestamp persistence across create, write, setattr, and remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/namei_msdos.c -->
# sources/distributed-fs/ceph-client/fs/fat/namei_msdos.c

## Purpose
`namei_msdos.c` implements the `msdos` filesystem variant: strict 8.3 name formatting, dentry hashing/comparison for formatted names, and VFS directory inode operations for create, lookup, unlink, mkdir, rmdir, and rename. It layers single-slot names on top of common FAT directory and inode helpers.

## Important APIs, Types, and Functions
- `msdos_format_name()` validates and converts user names into 11-byte FAT 8.3 names based on `check=`, `dotsOK`, and `nocase`.
- `msdos_find()` formats a user name, calls `fat_scan()`, and applies hidden-file dot semantics.
- `msdos_hash()` and `msdos_cmp()` ensure dentries compare in formatted-name space when possible.
- `msdos_add_entry()` builds one `msdos_dir_entry` and calls `fat_add_entries()`.
- `msdos_create()`, `msdos_mkdir()`, `msdos_unlink()`, `msdos_rmdir()`, and `msdos_rename()` implement the VFS operations.
- `msdos_init_fs_context()` registers msdos-specific fs_context operations and defaults.

## Control Flow
Lookup takes `sbi->s_lock`, formats the requested name, scans the directory, and builds or reuses a FAT inode by `sinfo.i_pos`. Create and mkdir format the target, reject formatted-name conflicts including dot-hidden aliases, create directory slots, build inodes, instantiate dentries, and flush if requested.

Remove operations check emptiness for rmdir, locate the slot, mark directory entries deleted, drop link counts, detach the inode from FAT hashes, and flush. Rename formats old/new names, handles hidden-dot attribute-only transitions, optionally validates replacement directories are empty, creates the destination entry if needed, moves `i_pos` by detach/attach, updates `..` for cross-directory directory moves, removes old slots, adjusts link counts, and has rollback/error paths that report corruption if on-disk recovery fails.

## State and Persistence
Persistent state is a single 8.3 directory entry per object. Hidden dotfiles are represented as `ATTR_HIDDEN` plus no leading dot in the formatted name when `dotsOK` is enabled. Rename changes directory entry location and possibly attributes, so inode hash state must be updated with `fat_detach()` / `fat_attach()`. Directory timestamps and link counts are updated through common helpers.

## Dependencies and Integration Points
This file uses `fat_scan()`, `fat_add_entries()`, `fat_remove_entries()`, `fat_alloc_new_dir()`, `fat_dir_empty()`, `fat_get_dotdot_entry()`, `fat_build_inode()`, `fat_flush_inodes()`, and shared attribute/getattr/setattr helpers. It registers a `file_system_type` named `msdos` that delegates mount setup to `fat_fill_super()`.

## Risks and Edge Cases
Name validation depends on relaxed/normal/strict modes and must preserve DOS 0xE5/0x05 first-character semantics. Dot-hidden behavior can create conflicts between `foo` and `.foo`. Rename has multiple partial-persistence windows: new entry creation, inode position update, dotdot update, and old entry removal. FAT has no hard links, so link count repair and detach semantics are critical.

## Test Signals
Tests should cover 8.3 validation under all `check=` modes, `dotsOK`, case/no-case behavior, hidden attribute transitions, create/mkdir/unlink/rmdir, cross-directory rename, replacement of empty directories, rollback after injected IO failure, and mount registration/options for `msdos`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/namei_msdos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/namei_vfat.c -->
# sources/distributed-fs/ceph-client/fs/fat/namei_vfat.c

## Purpose
`namei_vfat.c` implements the VFAT filesystem variant with long filename support, short alias generation, case-sensitive or case-insensitive dentry operations, and full VFS namespace operations including `RENAME_EXCHANGE`. It builds long-name slot arrays and delegates physical directory mutation to `dir.c`.

## Important APIs, Types, and Functions
- `vfat_revalidate()` and `vfat_revalidate_ci()` invalidate negative dentries when parent i_version changes or create/rename intent requires a case-accurate lookup.
- `vfat_hash()`, `vfat_hashi()`, `vfat_cmp()`, and `vfat_cmpi()` implement trailing-dot stripping and optional case folding.
- `xlate_to_uni()` converts user names to UTF-16 using UTF-8, NLS, or `:xxxx` unicode escape sequences.
- `vfat_create_shortname()` derives a unique 8.3 alias, including Win95/WinNT case rules and numeric/randomized tails.
- `vfat_build_slots()` creates VFAT long-name slots plus the final short entry.
- `vfat_add_entry()` allocates the slot array and calls `fat_add_entries()`.
- `vfat_lookup()`, create/unlink/mkdir/rmdir, `vfat_rename()`, and `vfat_rename_exchange()` implement VFS namespace behavior.

## Control Flow
Lookup strips trailing dots, searches both long and short names through `fat_search_long()`, builds the inode from the located short entry, and handles alias dentries when the same inode was previously reached by an 8.3 alias or long name. Negative dentries remember the parent i_version so new aliases can invalidate them.

Creation converts the user name to UTF-16, rejects bad characters and trailing spaces, builds a unique short alias, optionally emits long-name slots with checksum and order markers, writes slots, increments parent i_version, builds the inode, and instantiates the dentry. Mkdir first allocates and initializes a directory cluster, then writes the VFAT entry.

Normal rename creates or reuses the destination slot, detaches any replaced inode, moves the old inode's `i_pos`, syncs it, updates `..` when crossing directories, removes old slots, updates metadata, and rolls back on failure. `RENAME_EXCHANGE` swaps `i_pos` between two existing inodes, updates both `..` entries when needed, fixes link counts when exactly one side is a directory crossing parents, and attempts rollback if any sync fails.

## State and Persistence
VFAT persistent names are a sequence of one or more `ATTR_EXT` slots followed by an 8.3 alias entry. The alias checksum connects the long-name slots to the short entry. In-core dentry state stores parent i_version in `d_fsdata` for negative dentry validation. Rename and exchange persist by changing which on-disk slot each inode's metadata writes to, not by rewriting the whole source name in place.

## Dependencies and Integration Points
The file uses NLS tables from mount setup, common FAT directory slot functions, inode build/detach/attach/sync helpers, timestamp helpers, and VFS dentry/namei operations. It registers the `vfat` filesystem type and delegates common mount parsing/fill to `fat_parse_param()` and `fat_fill_super()`.

## Risks and Edge Cases
Short alias generation is performance-sensitive and collision-prone in large directories; it tries `~1` through `~9`, then jiffies-derived hex tails. Unicode conversion can fail on invalid UTF-8/NLS sequences or names longer than `FAT_LFN_LEN`. Case-insensitive positive dentries cannot always support case-only renames. Rename/exchange has corruption risk if dotdot or inode-position sync fails after partial state changes.

## Test Signals
Tests should cover UTF-8 and non-UTF-8 mounts, unicode escape mode, bad-character rejection, trailing dot stripping, trailing space rejection, short alias collisions, `nonumtail`, Win95/WinNT shortname policies, long readdir/lookup by alias and long name, negative dentry invalidation, cross-directory rename, directory replacement, and `RENAME_EXCHANGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/namei_vfat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/nfs.c -->
# sources/distributed-fs/ceph-client/fs/fat/nfs.c

## Purpose
`nfs.c` implements FAT export operations for NFS. It provides normal export support based on VFS inode numbers and a `nostale_ro` mode that encodes stable directory-entry positions into file handles and can rebuild disconnected inodes.

## Important APIs, Types, and Functions
- `struct fat_fid` is the on-wire file handle layout for `nostale_ro`: inode generation, child `i_pos`, and optional parent `i_pos` and generation.
- `fat_dget()` looks up cached directory inodes by start cluster in `sbi->dir_hashtable`.
- `fat_ilookup()` chooses `fat_iget()` by `i_pos` for nostale mode or `ilookup()` by inode number for normal mode.
- `__fat_nfs_get_inode()` validates generation and, in nostale mode, can read the directory entry and build an inode if it is not already cached.
- `fat_encode_fh_nostale()`, `fat_fh_to_dentry_nostale()`, and `fat_fh_to_parent_nostale()` encode/decode stable handles.
- `fat_rebuild_parent()` and `fat_get_parent()` reconnect exported directories using `..` entries and logstart scans.
- `fat_export_ops` and `fat_export_ops_nostale` are the exported operation tables.

## Control Flow
Normal export delegates encoding and decoding mostly to generic helpers using 32-bit inode numbers. Nostale export encodes `i_pos` and generation into `fat_fid`; decode reconstructs `i_pos`, looks for an existing inode by directory-entry position, and if absent reads the directory entry block, rejects free/deleted entries, and calls `fat_build_inode()`.

Parent lookup reads the child's `..` entry. If the parent directory is in the directory hash, it returns that inode. In nostale mode, if the parent is not cached, `fat_rebuild_parent()` reads the parent cluster, builds a temporary grandparent from `..`, scans it for the parent's start cluster, and builds the real parent inode.

## State and Persistence
Normal NFS handles are vulnerable because FAT inode numbers are synthetic and can be stale after eviction/remount. Nostale mode persists identity through directory-entry position (`i_pos`) and generation, so `fat_fill_super()` forces read-only when `nfs=nostale_ro`. Directory hash state is populated by `fat_attach()` for directories when NFS support is enabled.

## Dependencies and Integration Points
This file depends on exportfs generic helpers, inode hash/dir hash maintenance from `inode.c`, directory scanning from `dir.c`, cluster start helpers from `fat.h`, and `fat_build_inode()`. Mount option handling in `inode.c` selects the export operation table.

## Risks and Edge Cases
`i_pos` handles become invalid if directory entries move, which is why nostale mode is read-only. Rebuild depends on valid `.` and `..` entries and unique start clusters; corrupted directories or double-linked directories can break reconnect. Normal mode can return stale file handles under mutation and is explicitly documented by the mount option name.

## Test Signals
NFS export tests should cover normal `stale_rw` behavior, `nostale_ro` forcing read-only, file handle encode/decode after inode eviction, parent reconnect for disconnected directories, generation mismatch rejection, deleted-entry rejection, and corrupted dotdot entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/nfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fcntl.c -->
# sources/distributed-fs/ceph-client/fs/fcntl.c

## Purpose
`fcntl.c` implements the Linux `fcntl` and compat `fcntl` syscalls, file flag changes, file ownership for SIGIO/SIGURG, write-life hints, descriptor duplication queries, leases/delegations dispatch, pipe/memfd fcntls, and fasync registration/signal delivery. It is generic VFS/syscall infrastructure used by all filesystems and device drivers.

## Important APIs, Types, and Functions
- `setfl()` applies `F_SETFL` changes for append, nonblocking, direct IO, noatime, and fasync flags.
- `file_f_owner_allocate()`, `__f_setown()`, `f_setown()`, `f_getown()`, `f_setown_ex()`, and `f_getown_ex()` manage `struct fown_struct`.
- `do_fcntl()` dispatches most native fcntl commands.
- `SYSCALL_DEFINE3(fcntl)` and 32-bit `fcntl64` perform fd lookup, `FMODE_PATH` restrictions, LSM checks, and dispatch.
- Compat helpers translate `struct flock` layouts and command values.
- `send_sigio()`, `send_sigurg()`, `fasync_helper()`, `fasync_insert_entry()`, `fasync_remove_entry()`, and `kill_fasync()` implement asynchronous notification.
- `fcntl_init()` creates the `fasync_cache` and validates open flag bit uniqueness.

## Control Flow
The syscall path obtains the file from the fd table, rejects most commands on `FMODE_PATH`, calls `security_file_fcntl()`, then dispatches. `do_fcntl()` handles descriptor flags, file flags, file locks, owner/signal configuration, leases, dnotify, pipe sizing, memfd seals, write-life hints, delegations, and created/dup queries.

`F_SETFL` goes through `setfl()`: it enforces append-only and noatime permissions, normalizes `O_NDELAY`, validates `O_DIRECT`, delegates filesystem/device-specific flag checks, updates fasync registration if requested, and finally updates `f_flags` under `filp->f_lock`.

Async notification stores target pid/pid_type and credentials in `fown_struct`. Signal delivery checks credentials and LSM permission, queues realtime signal info for configured signals, falls back to SIGIO, and supports process-group fanout. Fasync lists are protected by `fasync_lock`, per-file `f_lock`, per-entry `fa_lock`, and RCU for safe traversal during `kill_fasync()`.

## State and Persistence
State is in-memory kernel state: `file->f_flags`, `file->f_iocb_flags`, close-on-exec fd bits, `file->f_owner`, inode write-life hints, fasync lists, and lock/lease/delegation state owned by other subsystems. No filesystem media is directly persisted here, though write hints and locks affect later IO behavior.

## Dependencies and Integration Points
The file integrates with fdtable helpers, VFS file locking, leases, dnotify, pipefs, memfd, LSM hooks, pid namespaces, credentials, signals, RCU, slab caches, user copy helpers, and compat syscall ABI. Filesystems and drivers integrate by implementing `file_operations::check_flags` and `::fasync`, and by using `kill_fasync()` to notify listeners.

## Risks and Edge Cases
`F_GETOWN` can return negative process-group IDs and therefore uses `force_successful_syscall_return()`. Owner allocation is race-safe through `cmpxchg`. `O_APPEND` cannot be cleared on append-only files, and `O_NOATIME` requires ownership/capability. Compat lock structures need overflow fixups. FASYNC flag consistency with list membership is explicitly critical; broken drivers can cause missed or spurious SIGIO.

## Test Signals
Tests should cover all descriptor flag commands, `F_SETFL` permission failures, fasync registration/removal, SIGIO/SIGURG delivery to pid and process group owners, compat lock commands, OFD locks, pipe sizing, memfd seals, write-life hint permissions/validation, `FMODE_PATH` restrictions, and LSM denial paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fcntl.c -->
