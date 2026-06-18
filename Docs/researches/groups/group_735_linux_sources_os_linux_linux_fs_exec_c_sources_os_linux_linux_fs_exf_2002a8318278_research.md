# Group Research: group_735_linux_sources_os_linux_linux_fs_exec_c_sources_os_linux_linux_fs_exf_2002a8318278

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exec.c -->
# File Research: sources/os/linux/linux/fs/exec.c

## Purpose
Implements Linux process image replacement for `execve`, `execveat`, and kernel-driven `kernel_execve`. It owns binary-format dispatch, argument/environment staging, credential preparation and commitment, address-space replacement, thread-group collapse, close-on-exec handling, and exec-related sysctl wiring.

## Main Interfaces
- Exported helpers: `__register_binfmt`, `unregister_binfmt`, `open_exec`, `copy_string_kernel`, `setup_arg_pages`, `begin_new_exec`, `would_dump`, `setup_new_exec`, `finalize_exec`, `remove_arg_zero`, `set_binfmt`.
- Syscalls: `execve`, `execveat`, plus compat variants under `CONFIG_COMPAT`.
- Sysctl: `/proc/sys/fs/suid_dumpable` when `CONFIG_SYSCTL`.

## Key Data Flow
`do_execveat_common()` opens the target with execute intent, creates `linux_binprm`, counts and copies argv/envp backward onto the nascent stack, enforces stack/argument limits, and calls `bprm_execve()`. `bprm_execve()` prepares credentials, checks unsafe exec states, invokes LSM hooks, and runs `exec_binprm()`. `exec_binprm()` repeatedly calls binary format loaders through `search_binary_handler()` to support interpreter chains.

The point of no return is `begin_new_exec()`: credentials are finalized from the actual executable, other threads are killed via `de_thread()`, files and signal handlers are unshared/reset, the new `mm_struct` replaces the old one, dumpability and `comm` are updated, credentials are committed, and optional execfd handoff is installed. `setup_new_exec()` later drops exec locks and releases the old mm.

## Dependencies
Tightly coupled to VFS path/open code, LSM hooks, binfmt modules, mm/VMA setup, signal/thread-group internals, credentials/user namespaces, audit, ptrace, proc connector, perf, rseq, io_uring, coredump policy, and architecture-specific stack/start-thread behavior.

## Notable Invariants And Risks
- After `bprm->point_of_no_return`, failures must kill the task rather than return to old userspace.
- `cred_guard_mutex` and `exec_update_lock` ordering is central to ptrace, credentials, and mm replacement safety.
- argv/envp accounting temporarily charges pages to the old mm for OOM behavior.
- setuid/setgid handling is guarded by mount flags, `no_new_privs`, idmapped mounts, namespace mappings, and LSM hooks.
- Binary-handler recursion is bounded to prevent interpreter loops.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/Kconfig -->
# File Research: sources/os/linux/linux/fs/exfat/Kconfig

## Purpose
Defines kernel configuration entries for the exFAT filesystem driver.

## Main Interfaces
- `EXFAT_FS`: tristate option enabling built-in or module support for exFAT.
- `EXFAT_DEFAULT_IOCHARSET`: default charset used for converting between user-visible filenames and exFAT UTF-16 names.

## Dependencies
Selecting `EXFAT_FS` pulls in `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, matching the implementation’s use of buffer heads, kernel NLS tables, and legacy direct I/O paths.

## Behavior Notes
The help text identifies exFAT as common for SD cards and USB storage. If built as a module, the module name is `exfat`. The default iocharset is `utf8`, but mounts can override it with the `iocharset` option.

## Risks
Configuration directly controls availability of the full `fs/exfat` object set. Charset defaults affect filename interpretation and compatibility, especially when users do not provide an explicit mount option.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/Makefile -->
# File Research: sources/os/linux/linux/fs/exfat/Makefile

## Purpose
Builds the Linux exFAT filesystem object when `CONFIG_EXFAT_FS` is enabled.

## Main Interfaces
- `obj-$(CONFIG_EXFAT_FS) += exfat.o`
- `exfat-y` composes `exfat.o` from `inode.o`, `namei.o`, `dir.o`, `super.o`, `fatent.o`, `cache.o`, `nls.o`, `misc.o`, `file.o`, and `balloc.o`.

## Dependencies
The Makefile reveals the driver’s internal layering: superblock/mount logic in `super.o`; inode/page-cache mapping in `inode.o`; namespace operations in `namei.o`; directory entry handling in `dir.o`; allocation bitmap and FAT chain management in `balloc.o` and `fatent.o`; cluster cache in `cache.o`; charset/upcase support in `nls.o`; shared helpers in `misc.o`; and regular file operations in `file.o`.

## Risks
Any new exFAT implementation file must be added here to participate in the monolithic `exfat.o` module.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/balloc.c -->
# File Research: sources/os/linux/linux/fs/exfat/balloc.c

## Purpose
Manages the exFAT allocation bitmap: loading it from disk, querying and mutating cluster allocation bits, counting used clusters, finding free clusters, and issuing discard ranges for FITRIM.

## Main Interfaces
- `exfat_load_bitmap`, `exfat_free_bitmap`
- `exfat_set_bitmap`, `exfat_clear_bitmap`, `exfat_test_bitmap`
- `exfat_find_free_bitmap`, `exfat_count_used_clusters`
- `exfat_trim_fs`

## Key Data Flow
`exfat_load_bitmap()` scans root directory entries for the primary allocation bitmap entry, then `exfat_allocate_bitmap()` validates the advertised bitmap size, allocates `sbi->vol_amap`, reads all bitmap sectors, and verifies that clusters backing the bitmap itself are marked allocated. Set/clear/test functions translate cluster numbers through `CLUSTER_TO_BITMAP_ENT()` and sector/bit macros from `exfat_fs.h`.

`exfat_find_free_bitmap()` searches little-endian machine-word chunks, wraps at the end of the bitmap, and returns `EXFAT_EOF_CLUSTER` on exhaustion. `exfat_trim_fs()` walks free-cluster runs in the requested byte range and calls `sb_issue_discard()` for runs meeting `minlen`.

## Dependencies
Uses `struct exfat_sb_info` bitmap fields, root directory entry scanning via `exfat_get_dentry()`, endian-aware bitmap helpers, block readahead, buffer heads, and block-device discard APIs.

## Notable Invariants And Risks
- Bitmap size smaller than required is treated as I/O corruption.
- `exfat_clear_bitmap()` rejects clearing an already-free bit.
- `exfat_test_bitmap()` returns true if the bitmap is not loaded, allowing some callers to proceed during early mount/setup paths.
- Correct locking is expected around allocation/free callers; trim takes `bitmap_lock` itself.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/cache.c -->
# File Research: sources/os/linux/linux/fs/exfat/cache.c

## Purpose
Provides a small per-inode LRU cache for translating file-relative cluster offsets to disk clusters, mainly accelerating FAT-chain traversal for fragmented files.

## Main Interfaces
- `exfat_cache_init`, `exfat_cache_shutdown`
- `exfat_cache_inval_inode`
- `exfat_get_cluster`

## Key Data Flow
The file defines `struct exfat_cache` ranges with file cluster, disk cluster, and contiguous count. `exfat_get_cluster()` starts from `ei->start_clu`, consults cached ranges with `exfat_cache_lookup()`, walks FAT entries as needed with `exfat_ent_get()`, detects contiguous disk extents, and adds/merges cache entries with `exfat_cache_add()`.

The cache is capped at `EXFAT_MAX_CACHE` entries per inode. When full, it reuses the least-recently-used entry. Cache invalidation frees all entries and bumps `ei->cache_valid_id` so stale in-flight cache descriptions are ignored.

## Dependencies
Depends on inode-private fields in `struct exfat_inode_info`, FAT entry reads from `fatent.c`, and spinlock-protected LRU lists.

## Notable Invariants And Risks
- `EXFAT_FREE_CLUSTER` as a file start is treated as filesystem corruption.
- No-FAT-chain files generally bypass deep FAT walking elsewhere; this cache mainly helps FAT-chain mode.
- Invalidation is intentionally coarse; callers must invalidate on truncation or chain mutation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/dir.c -->
# File Research: sources/os/linux/linux/fs/exfat/dir.c

## Purpose
Implements directory entry parsing, directory iteration, entry-set caching/writing, directory-entry checksums, free-slot validation, name matching support, subdirectory counting, and volume-label read/write.

## Main Interfaces
- File ops: `exfat_dir_operations`
- Entry helpers: `exfat_get_entry_type`, `exfat_get_dentry`, `exfat_get_dentry_set`, `exfat_get_empty_dentry_set`, `exfat_put_dentry_set`
- Mutation helpers: `exfat_init_dir_entry`, `exfat_init_ext_entry`, `exfat_remove_entries`, `exfat_update_dir_chksum`
- Search/count helpers: `exfat_find_dir_entry`, `exfat_count_dir_entries`
- Volume label: `exfat_read_volume_label`, `exfat_write_volume_label`

## Key Data Flow
Directory records are handled as entry sets: file entry, stream extension, then one or more filename entries, optionally followed by secondary entries. `exfat_readdir()` walks a directory chain, extracts UTF-16 name pieces, converts them through NLS/UTF-8 helpers, and emits VFS directory entries outside `s_lock`.

`__exfat_get_dentry_set()` loads all sectors covering an entry set into buffer heads, using inline storage for common cases and dynamic allocation if needed. `exfat_get_dentry_set()` validates the expected file/stream/name/secondary sequence. Modified entry sets are flushed by `exfat_put_dentry_set()`.

`exfat_find_dir_entry()` scans dentries with name-hash prefiltering, UTF-16 case-insensitive comparison, hint updates, empty-slot hints, rewind support, and loop guards.

## Dependencies
Uses allocation/FAT chain traversal, NLS conversion, checksum helpers, buffer heads, inode hint fields, and the global exFAT superblock lock.

## Notable Invariants And Risks
- Entry-set validation protects against malformed secondary-entry ordering.
- Deleting an entry also frees allocatable benign-secondary clusters.
- Directory iteration must drop `s_lock` before `dir_emit()`.
- Volume-label lookup reuses root empty-entry hints when no label exists.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/exfat_fs.h -->
# File Research: sources/os/linux/linux/fs/exfat/exfat_fs.h

## Purpose
Central private header for the Linux exFAT driver. It defines in-memory structures, type constants, conversion macros, mount options, inode/superblock private state, inline helpers, and cross-file prototypes.

## Main Contents
- Logical dentry type constants such as `TYPE_FILE`, `TYPE_DIR`, `TYPE_STREAM`, `TYPE_EXTEND`, bitmap/upcase/volume/vendor types.
- Size and conversion macros for clusters, blocks, dentries, FAT entries, and allocation bitmap offsets.
- Core structures: `exfat_uni_name`, `exfat_chain`, `exfat_hint`, `exfat_hint_femp`, `exfat_entry_set_cache`, `exfat_dir_entry`, `exfat_mount_options`, `exfat_sb_info`, `exfat_inode_info`.
- Inline helpers: `EXFAT_SB`, `EXFAT_I`, forced-shutdown test, mode/attribute conversion, cluster/sector conversion, cluster validity, ondisk-size calculation, `exfat_cluster_walk`, and `exfat_chain_advance`.
- Prototypes for super, FAT/bitmap, file, namei, cache, dir, inode, NLS, and misc modules.

## Integration Role
This header is the contract tying all exFAT `.c` files together. It exposes shared locking state (`s_lock`, `bitmap_lock`), allocation state (`vol_amap`, `used_clusters`, `clu_srch_ptr`), directory/inode hints, and file-operation declarations.

## Notable Invariants And Risks
- `ALLOC_NO_FAT_CHAIN` means cluster traversal is arithmetic; `ALLOC_FAT_CHAIN` means FAT lookup.
- Directory entry sets are bounded by `ES_MAX_ENTRY_NUM` and cached across up to `DIR_CACHE_SIZE` sectors.
- Mode/attribute conversion is mount-option dependent and intentionally limited by exFAT metadata capabilities.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/exfat_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/exfat_raw.h -->
# File Research: sources/os/linux/linux/fs/exfat/exfat_raw.h

## Purpose
Defines exFAT on-disk constants and packed structures used to interpret boot sectors and directory entries.

## Main Contents
- Signatures and identifiers: boot signatures, `"EXFAT   "` filesystem name.
- Cluster sentinels: free, EOF, bad, reserved/first cluster, maximum cluster count.
- Allocation flags: `ALLOC_POSSIBLE`, `ALLOC_FAT_CHAIN`, `ALLOC_NO_FAT_CHAIN`.
- Dentry type byte values: unused, deleted, bitmap, upcase, volume, file, stream, name, ACL/vendor entries.
- File attributes: readonly, hidden, system, volume, subdir, archive.
- On-disk sizes: 32-byte dentries, 15 UTF-16 code units per filename dentry, 11-code-unit volume labels.
- Packed structs: `boot_sector` and union-based `exfat_dentry`.
- Timestamp bounds and timezone-valid bit.

## Integration Role
All parser and writer code in `dir.c`, `super.c`, `fatent.c`, `balloc.c`, `inode.c`, and `nls.c` relies on these exact packed layouts and constants to avoid ABI drift from the exFAT disk format.

## Notable Invariants And Risks
- The union in `struct exfat_dentry` overlays many entry forms on one 32-byte record.
- Endianness conversion is required for all multibyte on-disk fields.
- Incorrect changes here would corrupt disk-format interpretation globally.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/exfat_raw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/fatent.c -->
# File Research: sources/os/linux/linux/fs/exfat/fatent.c

## Purpose
Implements FAT entry access, FAT mirroring, cluster-chain construction, cluster allocation/freeing, cluster zeroing, chain counting, and block readahead for FAT/bitmap-heavy paths.

## Main Interfaces
- `exfat_ent_get`, `exfat_ent_set`
- `exfat_blk_readahead`
- `exfat_chain_cont_cluster`
- `exfat_free_cluster`, `exfat_alloc_cluster`
- `exfat_find_last_cluster`, `exfat_zeroed_cluster`, `exfat_count_num_clusters`

## Key Data Flow
FAT entry reads and writes translate cluster numbers into FAT sectors and byte offsets. Reads validate content, remap reserved values above bad-cluster to EOF, and reject free/bad/invalid references. Writes optionally cache a buffer head and mirror changes to FAT2 when present.

`exfat_alloc_cluster()` uses the allocation bitmap to find free clusters, sets bits, initializes FAT entries when needed, and preserves `ALLOC_NO_FAT_CHAIN` only while allocation remains physically contiguous. If allocation wraps or becomes non-contiguous, it materializes FAT links with `exfat_chain_cont_cluster()` and switches to `ALLOC_FAT_CHAIN`.

`__exfat_free_cluster()` clears bitmap bits for no-FAT or FAT-chain allocations, optionally discards contiguous freed runs, updates `used_clusters`, and includes loop protection.

## Dependencies
Depends on bitmap helpers from `balloc.c`, buffer-head writes from `misc.c`, cluster conversion macros, block-device discard/sync APIs, and `bitmap_lock`.

## Notable Invariants And Risks
- FAT2 mirroring must stay consistent with FAT1.
- Partial allocation failure rolls back through `__exfat_free_cluster()`.
- Looping FAT chains trigger recovery behavior or filesystem errors.
- Directory-sync inodes influence bitmap/FAT flush timing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/fatent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/file.c -->
# File Research: sources/os/linux/linux/fs/exfat/file.c

## Purpose
Implements regular-file VFS operations, file resizing/truncation policy, fallocate, attribute/stat handling, ioctls, fsync, valid-data-length maintenance, mmap write handling, and read/write/splice dispatch.

## Main Interfaces
- File ops: `exfat_file_operations`
- Inode ops: `exfat_file_inode_operations`
- Exported helpers: `__exfat_truncate`, `exfat_truncate`, `exfat_setattr`, `exfat_getattr`, `exfat_fileattr_get`, `exfat_file_fsync`, `exfat_ioctl`, `exfat_compat_ioctl`

## Key Data Flow
`exfat_cont_expand()` grows allocation without extending valid data length, supporting `FALLOC_FL_ALLOCATE_RANGE` and expanding truncate. `__exfat_truncate()` updates directory metadata before freeing clusters to reduce crash windows where freed clusters remain referenced.

`exfat_setattr()` enforces exFAT’s limited ownership/mode model, handles growth via allocation, zeroes partial truncate blocks, updates inode state, and calls `exfat_truncate()`. Read/write paths reject forced shutdown, maintain valid size, zero gaps before writes beyond VDL, validate direct-I/O alignment, and use generic buffered/direct I/O helpers.

Ioctls expose FAT-style attribute get/set, shutdown, FITRIM, and filesystem label get/set.

## Dependencies
Depends on inode/block mapping in `inode.c`, cluster allocation/free in `fatent.c`, volume-label functions in `dir.c`, NLS conversion, security hooks, block-device flush/discard, and VFS generic file helpers.

## Notable Invariants And Risks
- `valid_size` and `i_size` intentionally differ; unwritten allocated ranges must read as zero.
- Attribute updates must respect root-directory restrictions and capability checks for system attributes.
- `fsync` flushes file state, the block device, and cache.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/inode.c -->
# File Research: sources/os/linux/linux/fs/exfat/inode.c

## Purpose
Implements exFAT inode writeback, logical-to-physical block mapping, address-space operations, direct I/O integration, inode hash lookup, inode construction, and eviction.

## Main Interfaces
- `__exfat_write_inode`, `exfat_write_inode`, `exfat_sync_inode`
- `exfat_build_inode`, `exfat_hash_inode`, `exfat_unhash_inode`, `exfat_iget`
- `exfat_evict_inode`, `exfat_block_truncate_page`

## Key Data Flow
`__exfat_write_inode()` writes VFS inode state back into the file and stream directory entries: attributes, create/modify/access times, size, valid size, allocation flags, start cluster, and checksum. Root and deleted entries are skipped.

`exfat_map_cluster()` maps a file cluster offset to a disk cluster, allocating clusters when requested. It handles no-FAT arithmetic mapping, FAT-chain cached mapping, new allocation, FAT-chain conversion, and hint updates. `exfat_get_block()` turns this into block mappings for buffered I/O, direct I/O, bmap, readahead, and writeback, carefully treating unwritten space beyond valid size.

The file also defines address-space operations using mpage/block helpers, direct I/O, and truncate locking. Inode hashing maps exFAT directory position (`i_pos`) to in-memory inode reuse.

## Dependencies
Uses directory entry-set helpers, allocation/FAT/cache code, misc timestamp/checksum helpers, VFS inode/page-cache APIs, and `s_lock`/`truncate_lock`.

## Notable Invariants And Risks
- `valid_size` controls zero-fill behavior for unwritten allocated blocks.
- Truncation must serialize with bmap/direct mapping through `truncate_lock`.
- Inode identity is based on directory-entry position, not a native on-disk inode number.
- Evicting unlinked inodes truncates/free clusters under `s_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/misc.c -->
# File Research: sources/os/linux/linux/fs/exfat/misc.c

## Purpose
Provides shared exFAT helpers for filesystem error policy, timestamp conversion, atime truncation, checksums, buffer-head dirty/sync handling, and simple chain initialization/copy.

## Main Interfaces
- `__exfat_fs_error`
- `exfat_get_entry_time`, `exfat_set_entry_time`
- `exfat_truncate_atime`, `exfat_truncate_inode_atime`
- `exfat_calc_chksum16`, `exfat_calc_chksum32`
- `exfat_update_bh`, `exfat_update_bhs`
- `exfat_chain_set`, `exfat_chain_dup`

## Key Data Flow
`__exfat_fs_error()` reports corruption/inconsistency and applies the mount `errors=` policy: continue, panic, or remount read-only. Timestamp conversion maps exFAT date/time/centisecond/timezone fields to `timespec64` and back. Access time is rounded down to exFAT’s two-second granularity.

Checksum helpers implement the exFAT rolling checksum variants, skipping specified fields for directory-entry and boot-sector checksum modes. Buffer helpers mark buffer heads uptodate/dirty and optionally synchronously write/wait for them.

## Dependencies
Used throughout dir, inode, super, FAT, bitmap, and file code. Depends on mount options in `exfat_sb_info`, buffer-head APIs, kernel time helpers, and raw checksum type constants.

## Notable Invariants And Risks
- Error policy can mutate the superblock into read-only state.
- `exfat_set_entry_time()` records UTC offset as valid zero offset.
- Directory-entry checksum skips the checksum field itself.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/namei.c -->
# File Research: sources/os/linux/linux/fs/exfat/namei.c

## Purpose
Implements exFAT namespace operations: dentry hashing/comparison/revalidation, empty-slot search and directory expansion, path/name normalization, lookup, create, unlink, mkdir, rmdir, rename, and move/replace semantics.

## Main Interfaces
- Dentry ops: `exfat_dentry_ops`, `exfat_utf8_dentry_ops`
- Directory inode ops: `exfat_dir_inode_operations`
- Shared helper: `exfat_find_empty_entry`

## Key Data Flow
Dentry operations compute case-insensitive hashes and comparisons using either mounted NLS tables or UTF-8 decoding plus the exFAT upcase table. Negative dentries are versioned against parent `i_version` and dropped for create/rename targets.

Creation flows through `exfat_add_entry()`: resolve VFS name to UTF-16, calculate needed dentry count, find or allocate an empty entry set, optionally allocate a new directory cluster, initialize file/stream/name entries, flush them, and return `exfat_dir_entry` metadata for inode construction.

Lookup calls `exfat_find()` to resolve names using directory hints, read entry metadata, validate sizes/start clusters, count subdirectories for directories, and build/reuse inodes. Unlink/rmdir mark entry sets deleted, update parent timestamps/versions, unhash target inodes, and set dentry version data. Rename either rewrites in-place if the new name fits or allocates/moves entry sets, handles target replacement, frees replaced directory clusters, and updates inode hashes/link counts.

## Dependencies
Uses `dir.c` entry-set helpers, `nls.c` conversion/upcase helpers, allocation helpers, inode construction/hash helpers, VFS dentry/inode APIs, and global `s_lock`.

## Notable Invariants And Risks
- Trailing-dot behavior is mount-option dependent; creation can reject names ending in dots when `keep_last_dots` is enabled.
- exFAT has no native Unix hard links; inode identity follows directory-entry position.
- Rename replacement must handle empty target directories and link-count updates carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/nls.c -->
# File Research: sources/os/linux/linux/fs/exfat/nls.c

## Purpose
Implements filename character conversion, case folding through the exFAT upcase table, name hashing support, and loading of on-disk or default upcase tables.

## Main Interfaces
- `exfat_toupper`
- `exfat_uniname_ncmp`
- `exfat_utf16_to_nls`
- `exfat_nls_to_utf16`
- `exfat_create_upcase_table`
- `exfat_free_upcase_table`

## Key Data Flow
The file includes the compressed recommended default upcase table and expands it into a 65,536-entry table. `exfat_create_upcase_table()` scans root directory entries for an upcase-table entry, loads it from disk, verifies its checksum, and falls back to the default table for non-I/O validation failures.

Name conversion has two modes. UTF-8 mode uses kernel UTF-8/UTF-16 helpers and computes name hashes from uppercased UTF-16 code units. Non-UTF-8 mode uses the mounted NLS table, converting between byte strings and UCS-2. Invalid half-width characters and control characters mark conversion as lossy; create paths reject lossy names while lookup can tolerate them for compatibility. UTF-16 surrogate pairs above U+FFFF are converted to replacement characters in NLS output because kernel NLS is UCS-2 oriented.

## Dependencies
Uses raw directory-entry types, checksum helpers, `exfat_get_dentry()`, FAT cluster traversal, buffer heads, kernel NLS, and UTF conversion APIs.

## Notable Invariants And Risks
- exFAT lookup is case-insensitive through the upcase table.
- Name hashes are computed over uppercased UTF-16 data.
- On-disk upcase table checksum mismatch causes fallback only for non-I/O errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/nls.c -->