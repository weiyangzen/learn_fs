# Group Research: group_977_linux_stable_sources_os_linux_linux_stable_fs_exec_c_sources_os_linu_e534f7cd161b

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exec.c -->
# File Research: sources/os/linux/linux-stable/fs/exec.c

This file is the Linux stable core implementation of `execve()`/`execveat()`. It owns binary-format registration and dispatch, executable opening, argument/environment staging, new-mm construction, credential transition, and the point-of-no-return phase where the current task becomes the new program image.

Key elements:
- Maintains the global `formats` list protected by `binfmt_lock`; `__register_binfmt()` and `unregister_binfmt()` add/remove `struct linux_binfmt` handlers.
- `do_open_execat()` opens an executable with `__FMODE_EXEC`, follows or rejects symlinks according to flags, enforces `noexec`, requires regular files, and denies writes while the executable is active.
- `bprm_mm_init()`, `copy_strings()`, `copy_string_kernel()`, `bprm_stack_limits()`, and `setup_arg_pages()` create and populate the new process stack, enforcing argument limits and stack rlimit derived bounds.
- `search_binary_handler()` probes registered binfmt loaders after `prepare_binprm()` and `security_bprm_check()`. `exec_binprm()` handles interpreter recursion and emits audit/ptrace/proc connector events after success.
- `begin_new_exec()` is the central commit path: computes creds, de-threads, cancels io_uring work, unshares file tables/sighand, installs the new mm, closes close-on-exec descriptors, applies dumpability, commits credentials, and optionally passes an execfd to an interpreter.
- Syscall front ends `execve`, `execveat`, compat variants, and `kernel_execve()` converge on `do_execveat_common()`/`bprm_execve()`.

Important dependencies and contracts:
- Relies on binfmt loaders to call back into `begin_new_exec()` and later `setup_new_exec()`/`finalize_exec()`.
- Security hooks are staged carefully: `security_bprm_creds_for_exec()`, `security_bprm_check()`, `security_bprm_creds_from_file()`, and commit hooks see different phases of the exec.
- `bprm->point_of_no_return` changes failure semantics: failures after this point trigger fatal signal behavior rather than returning normally to old userspace.
- `cred_guard_mutex` and `exec_update_lock` protect ptrace/credential/mm visibility during the transition.
- `AT_EXECVE_CHECK` is supported as a pre-exec check path that stops after credential-preparation security checks without parsing/loading the binary.

Failure/edge behavior:
- Enforces `MAX_ARG_STRINGS`, `MAX_ARG_STRLEN`, pointer-array stack accounting, and NULL-argv normalization by injecting an empty argv[0].
- Detects interpreter loops with a depth limit.
- Handles multithreaded exec by killing other threads and, if needed, adopting the old leader’s TGID.
- `suid_dumpable` sysctl is registered under `fs` when sysctl support is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/exfat/Kconfig

This Kconfig file declares the Linux exFAT filesystem configuration options.

Key elements:
- `EXFAT_FS` is a tristate option named “exFAT filesystem support”.
- It selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, matching the implementation’s use of buffer-head based metadata I/O, charset conversion, and legacy direct I/O hooks.
- Help text states the module name is `exfat` and positions the filesystem for SD cards and USB storage.
- `EXFAT_DEFAULT_IOCHARSET` is a string option defaulting to `utf8`, dependent on `EXFAT_FS`.

Important behavior:
- The default charset setting controls the default user-visible filename conversion path between mount/user encoding and exFAT’s UTF-16 on-disk names.
- Runtime mount option `iocharset` can override this default.

Dependencies:
- Directly paired with `fs/exfat/Makefile`, which builds `exfat.o` only when `CONFIG_EXFAT_FS` is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/exfat/Makefile

This Makefile wires the exFAT filesystem into the kernel build.

Key elements:
- Builds `exfat.o` when `CONFIG_EXFAT_FS` is enabled.
- `exfat-y` is composed from:
  - `inode.o`
  - `namei.o`
  - `dir.o`
  - `super.o`
  - `fatent.o`
  - `cache.o`
  - `nls.o`
  - `misc.o`
  - `file.o`
  - `balloc.o`

Important dependency meaning:
- The file list reflects the subsystem split: inode/address-space mapping, VFS name operations, directory entry handling, superblock/mount support, FAT and bitmap allocation, cluster cache, Unicode/NLS conversion, utility routines, regular file operations, and allocation bitmap management.

Scope note:
- `super.c` is built here but is outside this group; the files in this group depend on its mount-time initialization of `struct exfat_sb_info`, root inode setup, options, volume flags, and teardown paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/balloc.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/balloc.c

This file manages the exFAT allocation bitmap: loading it from disk, testing/setting/clearing bits, finding free clusters, counting used clusters, and implementing FITRIM discard over free extents.

Key elements:
- Uses endian-aware word access helpers for 32-bit and 64-bit `BITS_PER_LONG`.
- `exfat_allocate_bitmap()` validates the bitmap dentry, computes expected bitmap size from `EXFAT_DATA_CLUSTER_COUNT()`, reads all bitmap sectors with readahead, and checks that the bitmap’s own clusters are allocated.
- `exfat_load_bitmap()` scans the root directory for the primary allocation bitmap entry with flag `0x0`.
- `exfat_set_bitmap()`, `exfat_clear_bitmap()`, and `exfat_test_bitmap()` manipulate little-endian allocation bits in `sbi->vol_amap`.
- `exfat_find_free_bitmap()` searches from a cluster hint and wraps to the beginning when reaching the end.
- `exfat_count_used_clusters()` counts set bits in the loaded allocation bitmap.
- `exfat_trim_fs()` translates an `fstrim_range` into cluster ranges, scans free clusters, and issues `sb_issue_discard()` for contiguous free runs at least `minlen`.

Important dependencies:
- Depends on `exfat_get_dentry()`, `exfat_get_entry_type()`, `exfat_get_next_cluster()`, and `exfat_blk_readahead()` for root directory scanning and bitmap I/O.
- `fatent.c` allocation/free code calls these bitmap helpers under `sbi->bitmap_lock`.
- Uses `exfat_cluster_to_sector()` and bitmap offset macros from `exfat_fs.h`.

Failure/edge behavior:
- Invalid cluster IDs are rejected before bitmap access.
- A bitmap smaller than required is fatal; a larger bitmap is tolerated.
- `exfat_clear_bitmap()` returns error if clearing an already-free bit.
- `exfat_test_bitmap()` returns true if `vol_amap` is absent, which avoids false failure before bitmap loading but means callers must ensure mount-time initialization happened.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/cache.c

This file implements a small per-inode cluster mapping cache for FAT-chain lookup acceleration.

Key elements:
- Defines `struct exfat_cache`, holding a file-cluster start, disk-cluster start, and contiguous cluster count.
- Maintains up to `EXFAT_MAX_CACHE` entries per inode in `ei->cache_lru`, protected by `ei->cache_lru_lock`.
- `exfat_cache_init()` creates a slab cache for cache entries; `exfat_cache_shutdown()` destroys it.
- `exfat_cache_lookup()` finds a cache entry covering or preceding the requested file cluster range and returns the scan boundary before a later cache.
- `exfat_cache_add()` merges by file-cluster start, allocates a new cache entry when below the limit, or reuses the LRU tail when full.
- `exfat_cache_inval_inode()` drops all cached extents and bumps `cache_valid_id` so racing additions from stale traversals are ignored.
- `exfat_get_cluster()` maps a logical file cluster to a disk cluster, using the cache when possible and walking FAT entries with `exfat_ent_get()` when necessary.

Important dependencies:
- Used by `inode.c` through `exfat_map_cluster()`/`exfat_get_block()` for block mapping on fragmented files.
- Invalidated by `file.c` truncation and inode eviction when cluster chains change.
- For `ALLOC_NO_FAT_CHAIN` files, higher layers often bypass FAT walking; this cache mainly benefits `ALLOC_FAT_CHAIN`.

Failure/edge behavior:
- Detects invalid `start_clu == EXFAT_FREE_CLUSTER` as filesystem corruption.
- Handles EOF by returning `*count = 0`.
- Maintains `last_dclus` so append paths can link newly allocated FAT chains correctly.
- Cache entries store contiguous FAT extents, not arbitrary sparse mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/dir.c

This file owns exFAT directory entry parsing, directory iteration, directory entry-set caching, name-entry initialization, checksum maintenance, empty-slot discovery validation, and volume-label directory entries.

Key elements:
- `exfat_readdir()` scans directory clusters, recognizes file/dir primary entries, gathers UTF-16 long names from secondary name entries, converts them to the mount charset, and advances `ctx->pos`.
- `exfat_iterate()` implements VFS directory iteration, emits dot entries, manages name buffers, and avoids holding `s_lock` across `dir_emit()`.
- `exfat_get_entry_type()` maps raw exFAT dentry type bytes to internal `TYPE_*` flags.
- `exfat_init_dir_entry()`, `exfat_init_ext_entry()`, and helpers create primary file, stream-extension, and filename entries.
- `exfat_update_dir_chksum()` computes and stores the entry-set checksum, skipping checksum bytes for the primary entry.
- `exfat_get_dentry()` maps a directory entry index to sector/offset, validates cluster allocation, reads the buffer, and returns an in-buffer pointer.
- `exfat_get_dentry_set()` reads a multi-entry set into `struct exfat_entry_set_cache`, including entries spanning sectors, and validates stream/name/secondary ordering.
- `exfat_get_empty_dentry_set()` validates a candidate empty range, tolerating deleted entries after unused entries for compatibility but detecting used-after-unused corruption.
- `exfat_find_dir_entry()` performs case-insensitive name lookup using stream name hash, filename entries, hints, and loop guards.
- `exfat_read_volume_label()` and `exfat_write_volume_label()` handle the root volume-label entry.

Important dependencies:
- Name conversion and comparison come from `nls.c`.
- Cluster walking and FAT/bitmap validation come from `fatent.c`/`balloc.c`.
- Namei create/rename/delete paths use entry-set creation, removal, and empty-slot search support here.
- Inode writeback uses `exfat_get_dentry_set_by_ei()` and checksum update to persist metadata.

Failure/edge behavior:
- Protects against deleted dentry access through `DIR_DELETED`.
- Caps directory scanning by `MAX_EXFAT_DENTRIES` and cluster-count loop guards.
- Frees clusters referenced by benign secondary entries when removing entry sets if those entries declare allocated data.
- `exfat_find_dir_entry()` updates parent hints both for next lookup and for future empty-entry allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/exfat_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/exfat/exfat_fs.h

This is the central internal header for the exFAT driver. It defines in-memory filesystem structures, internal type constants, conversion macros, inline helpers, and cross-file function prototypes.

Key elements:
- Defines internal `TYPE_*` values for raw dentry categories, plus entry-set constants such as `ES_IDX_FILE`, `ES_IDX_STREAM`, and `ES_IDX_FIRST_FILENAME`.
- Provides byte/cluster/block/dentry conversion macros, FAT entry offset macros, allocation bitmap offset macros, and entry-set size limits.
- Defines `struct exfat_mount_options`, including uid/gid masks, charset options, error behavior, discard, timezone behavior, trailing-dot handling, and zero-size directory support.
- Defines `struct exfat_sb_info`, which stores geometry, FAT/data starts, root directory cluster, bitmap buffers, upcase table, used cluster count, locks, NLS table, inode hash table, and options.
- Defines `struct exfat_inode_info`, extending VFS inode state with exFAT directory location, entry index, raw attributes, start cluster, allocation flags, lookup/allocation hints, cluster cache state, on-disk position, valid size, and truncate lock.
- Provides inline helpers for `EXFAT_SB()`, `EXFAT_I()`, forced shutdown checks, mode/attribute conversion, cluster/sector conversion, cluster validity, and chain walking/advancing.

Important dependencies:
- Included by every exFAT implementation file in this group.
- Raw on-disk layout comes from `exfat_raw.h`.
- Prototypes expose the module boundaries between allocation, FAT, file operations, name operations, cache, directory, inode, NLS, and misc utilities.

Critical contracts:
- `ALLOC_NO_FAT_CHAIN` means clusters are physically contiguous and can be walked arithmetically; `ALLOC_FAT_CHAIN` requires FAT lookup.
- `valid_size` is tracked separately from logical `i_size` to preserve exFAT valid-data-length semantics.
- `s_lock` serializes broad filesystem metadata operations; `bitmap_lock` serializes bitmap allocation/free; inode `truncate_lock` protects bmap against truncate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/exfat_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/exfat_raw.h -->
# File Research: sources/os/linux/linux-stable/fs/exfat/exfat_raw.h

This header defines exFAT on-disk constants and packed raw structures.

Key elements:
- Defines boot signatures, filesystem name string, max filename length, volume flags, special cluster values, reserved cluster numbering, and maximum cluster count.
- Defines raw directory entry type bytes such as `EXFAT_FILE`, `EXFAT_STREAM`, `EXFAT_NAME`, `EXFAT_BITMAP`, `EXFAT_UPCASE`, and volume/vendor entries.
- Provides classification macros for critical/benign primary and secondary entries.
- Defines checksum modes `CS_DIR_ENTRY`, `CS_BOOT_SECTOR`, and `CS_DEFAULT`.
- Defines file attribute bits and writable mask `EXFAT_ATTR_RWMASK`.
- Defines boot sector layout in packed `struct boot_sector`.
- Defines packed `struct exfat_dentry` union covering file primary, stream extension, name, bitmap, upcase, volume label, vendor, and generic secondary entries.
- Defines timestamp range constants and timezone-valid flag.

Important dependencies:
- `dir.c`, `inode.c`, `namei.c`, `balloc.c`, `fatent.c`, and `nls.c` interpret and write these raw fields using little-endian conversions.
- `exfat_fs.h` builds internal helper types and logic on top of these raw constants.

Critical contracts:
- Directory entries are exactly 32 bytes.
- File names are stored as 15 UTF-16 code units per name secondary entry.
- Cluster 0 and 1 are reserved; data cluster numbering starts at 2.
- The stream extension contains allocation flags, valid size, start cluster, and logical size, which drives block mapping and writeback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/exfat_raw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/fatent.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/fatent.c

This file manages FAT entry I/O, mirrored FAT updates, readahead, cluster-chain construction, allocation, freeing, discard, zeroing, and cluster counting.

Key elements:
- `exfat_ent_get()` validates FAT entry location/content, reads the FAT sector, returns the next cluster, and maps reserved high values to EOF.
- `exfat_ent_set()` writes a FAT entry; lower helper `__exfat_ent_set()` supports cached buffer-head reuse.
- `exfat_mirror_bh()` mirrors FAT sector updates to FAT2 when a second FAT exists.
- `exfat_blk_readahead()` issues block readahead in plugged batches.
- `exfat_chain_cont_cluster()` writes a contiguous FAT chain ending in `EXFAT_EOF_CLUSTER`.
- `exfat_free_cluster()` clears bitmap bits for either contiguous no-FAT chains or FAT chains, optionally issues discard, updates `used_clusters`, and detects loop-like chains.
- `exfat_find_last_cluster()` locates and validates the last cluster of a chain.
- `exfat_zeroed_cluster()` zeroes every block in a newly allocated directory cluster.
- `exfat_alloc_cluster()` finds free bitmap bits, marks them allocated, writes FAT entries when needed, converts no-FAT chains to FAT chains when allocation is no longer contiguous, and updates `clu_srch_ptr`/`used_clusters`.
- `exfat_count_num_clusters()` counts a chain’s length with loop detection.

Important dependencies:
- Uses bitmap helpers from `balloc.c`.
- Used by `inode.c` block mapping, `file.c` truncation/expansion, `namei.c` directory growth, and `dir.c` chain traversal.
- Uses `exfat_update_bh()` from `misc.c` and geometry helpers from `exfat_fs.h`.

Failure/edge behavior:
- Invalid FAT access is reported through rate-limited filesystem errors.
- Allocation rollback calls internal free on partially allocated chains.
- If contiguous allocation fails while `ALLOC_NO_FAT_CHAIN` was expected, it materializes a FAT chain and switches flags.
- Discard unsupported errors disable the discard mount option.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/fatent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/file.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/file.c

This file implements regular-file VFS operations, attribute ioctls, fitrim/label/shutdown ioctls, fallocate, truncate/expand behavior, valid-size extension, mmap write handling, and fsync.

Key elements:
- `exfat_cont_expand()` grows a file by allocating clusters, linking them to the existing chain, updating `i_size`, `i_blocks`, times, and dirty state without increasing `valid_size`.
- `exfat_fallocate()` supports only `FALLOC_FL_ALLOCATE_RANGE`, implemented as expansion without zeroing newly allocated clusters because exFAT tracks valid data length.
- `__exfat_truncate()` adjusts FAT/bitmap state after shrink or zero-length truncation, writes directory metadata before freeing clusters, invalidates cluster cache, resets hints, and frees the removed chain.
- `exfat_setattr()` handles size expansion/shrink, ownership/mode restrictions derived from mount options, timestamp permission relaxation via `allow_utime`, and atime truncation.
- Attribute ioctls map FAT/exFAT attributes to Unix mode and restrict system attribute changes to `CAP_LINUX_IMMUTABLE`.
- `FITRIM`, forced shutdown, and filesystem label ioctls dispatch to allocation, shutdown, and volume-label helpers.
- `exfat_file_write_iter()` ensures holes between `valid_size` and write position are zeroed before writes.
- `exfat_extend_valid_size()` writes zeroed buffers up to a new valid-size boundary.
- `exfat_page_mkwrite()` extends valid size for mmap writes before allowing page dirtying.
- `exfat_file_fsync()` flushes file data, block device state, and cache flush.

Important dependencies:
- Uses `fatent.c` allocation/free/chain logic and `inode.c` writeback/block mapping.
- Uses `dir.c` volume label helpers and `nls.c` conversion for label ioctl paths.
- Uses `misc.c` timestamp truncation and buffer update utilities.

Failure/edge behavior:
- Most public operations reject work after forced shutdown.
- Direct I/O write alignment must satisfy inode block size or device logical block size.
- Truncation writes directory entry metadata before freeing clusters to reduce power-failure dangling-reference risk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/inode.c

This file implements inode writeback, logical-to-physical block mapping, address-space operations, direct I/O handling, inode hash lookup by on-disk position, inode construction, and eviction.

Key elements:
- `__exfat_write_inode()` persists a non-root inode’s file and stream entries: attributes, create/modify/access times, logical size, valid size, allocation flags, start cluster, and directory checksum.
- `exfat_map_cluster()` maps or allocates clusters for a logical cluster offset, handling no-FAT contiguous chains, FAT chains, chain extension, and conversion to FAT-chain representation when appended allocation is not contiguous.
- `exfat_get_block()` maps filesystem blocks for buffered I/O, direct I/O, bmap, and writeback. It handles `valid_size` carefully so unwritten regions read as zero and partially valid blocks are read/zero-filled as needed.
- Address-space operations include mpage read/readahead/writepages, block write begin/end, direct I/O, bmap under `truncate_lock`, and buffer migration.
- `exfat_direct_IO()` updates `valid_size` for writes and zeroes unwritten tail data for reads crossing valid size.
- `exfat_hash_inode()`, `exfat_unhash_inode()`, and `exfat_iget()` maintain a per-superblock hash keyed by encoded directory location.
- `exfat_fill_inode()` initializes VFS inode fields from `struct exfat_dir_entry`, choosing directory vs file operations and setting timestamps, generation, nlink, mapping ops, size, and blocks.
- `exfat_build_inode()` reuses existing hashed inodes or creates and hashes a new inode.
- `exfat_evict_inode()` truncates data for unlinked inodes, clears pages, invalidates cluster cache, and unhashes the inode.

Important dependencies:
- Block mapping calls cluster cache (`cache.c`), FAT/bitmap allocation (`fatent.c`/`balloc.c`), and directory writeback (`dir.c`).
- File operations in `file.c` depend on `exfat_block_truncate_page()` and writeback behavior here.

Failure/edge behavior:
- Detects broken FAT chains when logical size exceeds allocated clusters.
- Maintains separate `i_size`, `i_blocks`, and `ei->valid_size`, which is central to exFAT correctness.
- Root inode is not written through normal directory-entry writeback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/misc.c

This file contains shared utility routines for filesystem error handling, timestamp conversion, checksum computation, buffer-head update/sync, and simple chain initialization.

Key elements:
- `__exfat_fs_error()` reports corruption/inconsistency and applies the mount `errors=` policy: continue, panic, or remount read-only.
- Timestamp helpers convert between exFAT date/time fields and Unix `timespec64`.
- Timezone handling uses either recorded exFAT timezone offsets, system timezone mode, or mount `time_offset`.
- `exfat_truncate_atime()` and `exfat_truncate_inode_atime()` enforce exFAT access-time granularity.
- `exfat_calc_chksum16()` computes directory-entry checksums, skipping primary checksum bytes when requested.
- `exfat_calc_chksum32()` computes boot/upcase checksums, skipping boot-sector mutable fields for boot checksum mode.
- `exfat_update_bh()` marks one buffer uptodate/dirty and optionally synchronously writes it.
- `exfat_update_bhs()` marks and optionally synchronously writes multiple buffers, waiting and returning `-EIO` if any sync write fails.
- `exfat_chain_set()` and `exfat_chain_dup()` initialize/copy `struct exfat_chain`.

Important dependencies:
- Directory, inode, FAT, bitmap, and name code all call these helpers.
- Error handling is used to escalate metadata corruption consistently.
- Timestamp helpers are used in inode writeback, lookup, create, mkdir, setattr, and volume metadata paths.

Failure/edge behavior:
- `EXFAT_ERRORS_RO` mutates `sb->s_flags` to read-only when corruption is reported.
- `exfat_set_entry_time()` writes timezone-valid with zero offset, effectively storing UTC-equivalent timestamps.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/namei.c

This file implements exFAT VFS directory inode operations and dentry operations: lookup, create, unlink, mkdir, rmdir, rename, case-insensitive hashing/comparison, empty-entry allocation, and pathname-to-UTF16 resolution.

Key elements:
- Dentry operations provide case-insensitive hashing/comparison using either NLS tables or UTF-8 decoding, with optional trailing-dot stripping controlled by mount options.
- `exfat_d_revalidate()` validates negative dentries using parent inode version and drops negative creation targets to avoid stale aliases.
- `exfat_search_empty_slot()` and `exfat_find_empty_entry()` find or allocate contiguous directory-entry slots, using `hint_femp` and growing directories by allocating and zeroing clusters.
- `__exfat_resolve_path()` strips trailing periods unless configured otherwise, enforces length limits, converts input names to UTF-16, and rejects lossy/invalid names on creation.
- `exfat_add_entry()` creates a file or directory entry set, allocating initial directory storage unless zero-size directories are enabled.
- `exfat_find()` resolves a child name, reads its entry set, validates size/start cluster/valid size, converts timestamps, and counts subdirectories for directory nlink.
- `exfat_lookup()` builds or reuses inodes by on-disk position and handles alias dentries.
- `exfat_unlink()` and `exfat_rmdir()` mark entry sets deleted, update parent/child metadata, unhash inodes, and set dentry versions.
- Rename support is split into same-directory rename, cross-directory move, and replacement handling. It rewrites entry sets when the new name needs more entries, deletes overwritten targets, frees replaced directory clusters, rehashes moved inodes, and updates nlink counts.
- Exposes `exfat_dir_inode_operations`.

Important dependencies:
- Uses directory entry-set APIs from `dir.c`, name conversion/upcase from `nls.c`, allocation from `fatent.c`, inode construction/hash from `inode.c`, and metadata utilities from `misc.c`.

Failure/edge behavior:
- Rejects unsupported rename flags except `RENAME_NOREPLACE`.
- Checks target directories are empty before replacement/removal.
- Guards against operations on entries whose `ei->dir.dir` is `DIR_DELETED`.
- Directory growth updates `i_size`, `valid_size`, `i_blocks`, and allocation flags immediately.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/nls.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/nls.c

This file implements exFAT Unicode/NLS conversion, case folding through the upcase table, filename hash computation support, and upcase-table loading.

Key elements:
- Contains the compressed default exFAT upcase table `uni_def_upcase`, read fully and summarized here as static data implementing the recommended exFAT uppercase mapping.
- `bad_uni_chars` lists disallowed half-width ASCII filename characters for Windows compatibility.
- `exfat_convert_char_to_ucs2()` and `exfat_convert_ucs2_to_char()` bridge kernel NLS conversion and lossy replacement with `_`.
- `exfat_toupper()` maps UCS-2 values through `sbi->vol_utbl`, returning the original code point if no mapping exists.
- `exfat_uniname_ncmp()` compares UTF-16 names case-insensitively using the upcase table.
- UTF-8 paths use `utf8s_to_utf16s()`/`utf16s_to_utf8s()` when the mount is in UTF-8 mode.
- Non-UTF8 paths use NLS table conversion to/from UCS-2. UTF-16 surrogate pairs above U+FFFF are represented as `_` when converting to legacy NLS because kernel NLS is UCS-2 oriented.
- `exfat_nls_to_utf16()` computes `name_len` and the exFAT stream `name_hash` over uppercased UTF-16 bytes.
- `exfat_create_upcase_table()` scans the root directory for the upcase table entry, loads and validates it with checksum, and falls back to the default table for non-I/O validation failures.
- `exfat_free_upcase_table()` releases the table.

Important dependencies:
- Dentry hash/compare in `namei.c`, lookup matching in `dir.c`, label ioctls in `file.c`, and volume mount setup all depend on these routines.
- Checksum helpers come from `misc.c`; raw upcase dentry layout comes from `exfat_raw.h`.

Failure/edge behavior:
- Conversion failures mark names lossy and replace characters with `_`; creation rejects lossy names while lookup is more permissive for compatibility.
- Names longer than `MAX_NAME_LENGTH` return `-ENAMETOOLONG`.
- Upcase-table checksum mismatch causes fallback to the default table unless the failure was an I/O error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/nls.c -->