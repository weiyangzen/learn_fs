# Group Research: group_1046_linux_stable_sources_os_linux_linux_stable_fs_ntfs_super_c_sources__a89a7264c118

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`. All files listed in the work item were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/super.c

This is the legacy `fs/ntfs` driver superblock, mount, system-file bootstrap, free-space accounting, and module lifecycle implementation. It owns `struct file_system_type ntfs_fs_type`, the `super_operations`, fs-context option parsing, the mount-time load of core NTFS metadata files, and unmount/sync/shutdown behavior.

Main responsibilities:
- Defines mount parameters for ownership, masks, NLS/charset, error policy, system/hidden file visibility, case sensitivity, sparse/discard behavior, ACLs, MFT zone multiplier, preallocation size, and Windows-name checking.
- Implements `ntfs_reconfigure()` with conservative read-write remount checks: existing volume errors, dirty/unsupported flags, chkdsk modification flags, logfile clearing, and quota-out-of-date marking can force failure or read-only behavior.
- Validates and parses the NTFS boot sector, deriving sector size, cluster size, MFT/index record sizes, volume cluster count, `$MFT` and `$MFTMirr` LCNs, mirror size, serial number, and sparse compression unit.
- Loads critical NTFS metadata in mount order: `$MFT`, `$MFTMirr`, `$MFT/$BITMAP`, `$UpCase`, `$AttrDef`, `$Bitmap`, `$Volume`, `$LogFile`, root, `$Secure`, `$Extend`, and optional `$Quota/$Q`.
- Compares `$MFT` and `$MFTMirr`, checks logfile state, detects Windows hibernation through `hiberfil.sys`, and handles dirty/unsupported volume flags.
- Maintains volume flags and label writes through resident `$Volume` attributes.
- Tracks free clusters and free MFT records by scanning `$Bitmap` and `$MFT/$BITMAP`; cluster scanning is queued on `ntfs-bg-io` after mount.
- Implements unmount cleanup, dirty-bit clearing on clean writable unmount, inode commits, block flushes, shutdown via `FS_IOC_SHUTDOWN`, `statfs`, module cache creation/destruction, sysctl registration, and filesystem registration.

Important functions and data:
- `ntfs_parse_param()` maps fs_context parameters to `struct ntfs_volume` fields and `NVol*` flags.
- `ntfs_handle_error()` applies `errors=panic|remount-ro|continue`, including writeback shutdown tracking for `-ENODEV`.
- `ntfs_write_volume_flags()`, `ntfs_set_volume_flags()`, `ntfs_clear_volume_flags()`, and `ntfs_write_volume_label()` update `$Volume` metadata.
- `is_boot_sector_ntfs()`, `read_ntfs_boot_sector()`, and `parse_ntfs_boot_sector()` form the boot-sector validation path.
- `ntfs_setup_allocators()` initializes MFT/data allocation zones based on `mft_zone_multiplier`.
- `load_system_files()` is the main metadata bootstrap routine and centralizes fallback-to-read-only decisions for damaged or unsafe volumes.
- `get_nr_free_clusters()`, `ntfs_available_clusters_count()`, and `__get_nr_free_mft_records()` populate allocation statistics used by `statfs` and allocation decisions.
- `ntfs_fill_super()` is the mount entry point used by `get_tree_bdev()`.
- Global caches: `ntfs_name_cache`, `ntfs_inode_cache`, `ntfs_big_inode_cache`, `ntfs_attr_ctx_cache`, and `ntfs_index_ctx_cache`.

Notable implementation details:
- Uses a global default `$UpCase` table with `ntfs_nr_upcase_users` under `ntfs_lock`; volumes use their own `$UpCase` unless it matches the generated default.
- Temporarily disables lockdep during NTFS mount bootstrap because metadata inode loading has exceptional locking order.
- Uses separate lock classes for system-file inodes such as `$MFTMirr`, `$Bitmap`, and `$MFT/$BITMAP`.
- `lcn_empty_bits_per_page` caches empty-bit counts for `$Bitmap` pages, complementing the atomic `free_clusters` and `dirty_clusters` counters.
- The mount path sets `s_time_gran = 100`, matching NTFS 100 ns timestamps, and enables idmapped mounts with `FS_ALLOW_IDMAP`.

Research notes:
- The file has been updated for read-write support and modern fs_context APIs, while still retaining legacy NTFS driver naming and metadata assumptions.
- Safety policy is strongly Windows-aware: dirty, chkdsk-modified, hibernated, unsupported-flag, or logfile-error states usually prevent writable operation.
- This file is the primary integration point between NTFS on-disk metadata validation and Linux VFS lifecycle semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/sysctl.c

This file provides optional sysctl support for the legacy `fs/ntfs` driver debug flag.

Main responsibilities:
- Compiles only when `DEBUG` is defined; the actual sysctl registration compiles only with `CONFIG_SYSCTL`.
- Defines a single sysctl table entry, `fs/ntfs/ntfs-debug`, backed by the global `debug_msgs` integer from `debug.h`.
- Provides `ntfs_sysctl(int add)` to register or unregister the table during module init/exit.

Important functions and data:
- `ntfs_sysctls[]` contains the `procname`, data pointer, size, permissions `0644`, and `proc_dointvec` handler.
- `sysctls_root_table` stores the registration handle returned by `register_sysctl()`.
- `ntfs_sysctl(1)` registers under `fs/ntfs`; `ntfs_sysctl(0)` unregisters and clears the handle.

Research notes:
- In non-debug builds this file contributes no code; callers rely on the inline no-op in `sysctl.h`.
- The sysctl is strictly a debug-message control and has no mount or metadata behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/sysctl.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/sysctl.h

This header declares or stubs the legacy NTFS debug sysctl registration function.

Main responsibilities:
- Provides the include guard `_LINUX_NTFS_SYSCTL_H`.
- Declares `int ntfs_sysctl(int add);` only for `DEBUG && CONFIG_SYSCTL`.
- Provides an inline no-op `ntfs_sysctl()` returning success for all other builds.

Research notes:
- This lets `super.c` call `ntfs_sysctl(1)` and `ntfs_sysctl(0)` unconditionally in module init/exit.
- The stub preserves identical control flow in production configurations without requiring extra preprocessor branches in the caller.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/time.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/time.h

This header implements inline conversion between Linux `timespec64` UTC timestamps and NTFS little-endian timestamp values.

Main responsibilities:
- Defines `NTFS_TIME_OFFSET`, the seconds between the NTFS epoch, January 1, 1601 UTC, and the Unix epoch, January 1, 1970 UTC.
- Converts Linux time to NTFS 100 ns units with `utc2ntfs()`.
- Gets current coarse realtime and converts it with `get_current_ntfs_time()`.
- Converts little-endian NTFS timestamps back to `struct timespec64` with `ntfs2utc()`.

Important functions:
- `utc2ntfs()` adds the epoch offset, multiplies seconds by 10,000,000, adds `tv_nsec / 100`, and returns `cpu_to_le64()`.
- `ntfs2utc()` subtracts the offset in 100 ns units, uses `div_s64_rem()` to split seconds and remainder, and converts the remainder to nanoseconds.

Research notes:
- The file is header-only for cheap use in inode and metadata timestamp paths.
- All on-disk NTFS values are represented as little-endian `__le64`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/unistr.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/unistr.c

This file implements legacy NTFS Unicode string comparison, collation, duplication, and conversion between mounted NLS encoding and NTFS little-endian UTF-16 strings.

Main responsibilities:
- Compares NTFS UTF-16 names case-sensitively or case-insensitively using the volume `$UpCase` table.
- Collates filename attributes for index ordering and rejects invalid Windows filename characters during collation.
- Converts user/NLS strings into little-endian UTF-16 for NTFS names and labels.
- Converts UTF-16 names back to NLS/UTF-8 for presentation.
- Duplicates bounded UTF-16 strings safely.

Important functions and data:
- `legal_ansi_char_array[]` marks low ASCII characters invalid or special for collation.
- `ntfs_are_names_equal()` and `ntfs_names_are_equal()` are equality helpers; the latter treats zero-length equal names explicitly.
- `ntfs_collate_names()` compares two names and can return a caller-specified error value if `name1` contains invalid `"`, `*`, `<`, `>`, or `?` characters.
- `ntfs_ucsncmp()` and `ntfs_ucsncasecmp()` are endian-aware UTF-16 comparison primitives.
- `ntfs_file_compare_values()` compares `FILE_NAME` attribute values using NTFS collation.
- `ntfs_nlstoucs()` allocates and fills an NTFS UTF-16 output string, using UTF-8 conversion when `vol->nls_utf8` is set or the mounted NLS table otherwise.
- `ntfs_ucstonls()` converts UTF-16 to UTF-8/NLS, allocating or growing the output buffer when allowed.
- `ntfs_ucsndup()` duplicates up to `maxlen` UTF-16 characters and always terminates.

Notable implementation details:
- All routines assume strings are stored as little-endian Unicode.
- `ntfs_nlstoucs()` uses `ntfs_name_cache` for normal NTFS maximum-length names and `kvmalloc()` for larger caller-provided limits such as volume labels.
- Conversion failures distinguish invalid character sequences from too-long names where possible.

Research notes:
- This file is used by directory lookup, index collation, volume label handling, and any code converting Linux-visible names to NTFS on-disk names.
- Correct use depends on the volume `upcase` table initialized in `super.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/unistr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/upcase.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/upcase.c

This file generates the legacy NTFS default Unicode uppercase mapping table in little-endian form.

Main responsibilities:
- Allocates a `default_upcase_len` entry `__le16` table.
- Initializes each character to identity mapping.
- Applies compact range and word override tables to produce NTFS uppercase mappings.

Important data:
- `uc_run_table` stores contiguous ranges with a constant additive delta.
- `uc_dup_table` stores alternating pairs where the odd/lowercase entry maps to the previous entry.
- `uc_word_table` stores individual codepoint overrides.

Important function:
- `generate_default_upcase()` returns a freshly allocated table or `NULL` on allocation failure.

Research notes:
- The generated table is shared by volumes in `super.c` when their on-disk `$UpCase` matches the default.
- The table is little-endian because NTFS strings and upcase entries are little-endian on disk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/upcase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/volume.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/volume.h

This header defines the legacy NTFS in-memory volume structure and related volume-flag and accounting helpers.

Main responsibilities:
- Declares `struct ntfs_volume`, the central superblock-private state used by `fs/ntfs`.
- Defines bit positions for mount/volume behavior flags and emits inline `NVol*`, `NVolSet*`, and `NVolClear*` helpers.
- Provides inline helpers for free cluster, free MFT record, LCN bitmap, and dirty-cluster reservation accounting.
- Declares `ntfs_available_clusters_count()` and `get_nr_free_clusters()` implemented in `super.c`.

Important fields in `struct ntfs_volume`:
- VFS/mount state: `sb`, `flags`, `uid`, `gid`, permission masks, `on_errors`, `wb_err`, `nls_map`, and `nls_utf8`.
- Geometry: sector, cluster, MFT record, and index record sizes plus masks and shifts.
- Volume layout: cluster count, `$MFT` and `$MFTMirr` LCNs, mirror size, serial number, MFT/data allocation zone positions.
- Metadata inodes: `$MFT`, `$MFT/$BITMAP`, `$MFTMirr`, `$LogFile`, `$Bitmap`, `$Volume`, root, `$Secure`, `$Extend`, `$Quota`, and `$Quota/$Q`.
- Metadata tables: `$UpCase`, `$AttrDef`, volume flags/version, and volume label.
- Allocation accounting: `free_waitq`, `free_clusters`, `free_mft_records`, `dirty_clusters`, sparse compression unit, `lcn_empty_bits_per_page`, and background `precalc_work`.

Volume flags:
- Include errors, system-file visibility, case sensitivity, logfile empty, quota state, USN journal state, read-only, compression, known free-cluster count, shutdown, system-file immutability, hidden/dot-file policies, Windows-name checking, discard, and sparse disabling.

Research notes:
- The inline free-cluster helpers wait until `NVolFreeClusterKnown()` is set; this couples allocation accounting to the background scan started by `super.c`.
- `dirty_clusters` tracks reserved or delayed allocation pressure separately from committed free-cluster counts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/volume.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/Kconfig

This file defines Linux Kconfig options for the newer `ntfs3` driver.

Main responsibilities:
- Defines `NTFS3_FS`, a tristate read-write NTFS filesystem driver option.
- Ensures `ntfs3` does not conflict with built-in legacy `NTFS_FS` by depending on `!NTFS_FS || m`.
- Selects required kernel features: `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`.
- Exposes optional 64-bit cluster support through `NTFS3_64BIT_CLUSTER`.
- Exposes optional Windows 10 external compression support through `NTFS3_LZX_XPRESS`.
- Exposes POSIX ACL support through `NTFS3_FS_POSIX_ACL`, selecting `FS_POSIX_ACL`.

Research notes:
- The main help text describes read/write support, journal replay, sparse/compressed file support, mount type `ntfs3`, and module name `ntfs3`.
- `NTFS3_64BIT_CLUSTER` is explicitly documented as not Windows-compatible for such volumes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/Makefile

This Makefile builds the `ntfs3` filesystem module or built-in object and configures warning coverage for the driver.

Main responsibilities:
- Adds a subset of W=1 style warnings and suppresses selected `-Wextra` warnings that are noisy for this codebase.
- Builds `ntfs3.o` when `CONFIG_NTFS3_FS` is enabled.
- Lists core object files for attributes, attribute lists, bitmaps, directories, records, files, journal/log handling, inodes, index logic, compression, namei, runlists, superblock, upcase, and xattrs.
- Adds external compression library objects when `CONFIG_NTFS3_LZX_XPRESS` is enabled.

Research notes:
- The prompt listed 56 lines, while the checked-out file contains 55 lines.
- The object list shows that the files in this group are foundational components of the broader ntfs3 driver, not standalone code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/attrib.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/attrib.c

This is the ntfs3 attribute storage engine. It manages resident and nonresident attribute sizing, cluster allocation/deallocation, runlist packing and loading, delayed allocation, sparse and compressed data mapping, WOF frame offset lookup, hole punching, range insertion/collapse, and forced conversion to nonresident storage.

Main responsibilities:
- Computes preallocation clumps and allocates clusters into `runs_tree` instances using volume free-space search.
- Deallocates run ranges, optionally issuing trim and removing delayed-allocation reservations.
- Converts resident attributes into nonresident attributes, preserving data through page cache or direct run writes.
- Resizes attributes through `attr_set_size_ex()`, handling resident growth/shrink, nonresident extension/truncation, delayed allocation, sparse/compressed files, MFT-specific allocation, preallocation, multi-segment attributes, and attribute-list creation/expansion.
- Resolves data blocks for read/write paths, including resident data, cached real runs, delayed allocation placeholders, sparse holes, compressed frames, and EOF.
- Allocates real clusters for sparse/compressed holes and updates packed runs and `total_size`.
- Reads WOF LZX/XPRESS frame offset tables when configured.
- Detects compressed frames by inspecting data and sparse runs within an NTFS compression unit.
- Rewrites compressed/sparse frame allocation with `attr_allocate_frame()`.
- Implements fallocate-like range operations: collapse range, punch hole, insert range, and force nonresident.

Important functions:
- `attr_load_runs()` and `attr_load_runs_vcn()` unpack on-disk run arrays into in-memory run trees.
- `run_deallocate_ex()` frees physical cluster ranges and keeps delayed allocation accounting synchronized.
- `attr_allocate_clusters()` wraps free-space search, run insertion, optional zeroout, partial allocation return, and rollback.
- `attr_make_nonresident()` removes a resident attribute record and reinserts it as nonresident with allocated runs.
- `attr_set_size_ex()` is the central resize routine for both `$DATA` and other attributes.
- `attr_data_get_block()` and `attr_data_get_block_locked()` serve mapping requests and allocate sparse/compressed holes when requested.
- `attr_load_runs_range()` ensures a byte range has run mappings loaded.
- `attr_wof_frame_info()` reads compressed WOF frame offset metadata for external compression.
- `attr_is_frame_compressed()` distinguishes uncompressed, sparse, and compressed NTFS compression frames.
- `attr_allocate_frame()` updates physical allocation for a compressed frame and maintains `total_size`.
- `attr_collapse_range()`, `attr_punch_hole()`, and `attr_insert_range()` mutate file layout for aligned ranges.
- `attr_force_nonresident()` converts default data to nonresident form.

Notable implementation details:
- Delayed allocation is represented with `ni->file.run_da` and `DELALLOC_LCN`; it is disabled for MFT, compressed/external attributes, and selected no-delalloc callers.
- Sparse and compressed attributes use `total_size` as physical allocation accounting distinct from logical `data_size` and `alloc_size`.
- Run packing with `mi_pack_runs()` can force creation of `$ATTRIBUTE_LIST` and additional nonresident attribute segments when one MFT record cannot hold the runlist.
- Many multi-step mutating paths have partial rollback; if rollback is impossible or metadata becomes inconsistent, the inode is marked bad with `_ntfs_bad_inode()`.
- Compressed/sparse range operations enforce cluster or compression-frame alignment and can return ntfs3-specific alignment errors.

Research notes:
- This file is one of the highest-risk ntfs3 metadata mutation points because it ties allocator state, runlists, MFT record layout, attribute-list entries, inode size, and VFS dirtying together.
- Several comments identify complexity and TODOs around merging allocation/resize paths, which aligns with the overlapping responsibilities of `attr_set_size_ex()`, `attr_data_get_block_locked()`, and `attr_allocate_frame()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/attrib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/attrlist.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/attrlist.c

This file manages ntfs3 `$ATTRIBUTE_LIST` data for inodes whose attributes span multiple MFT records or segments.

Main responsibilities:
- Loads resident or nonresident attribute-list contents into `ni->attr_list`.
- Enumerates and validates variable-sized `ATTR_LIST_ENTRY` records.
- Finds entries by attribute type, name, and VCN.
- Inserts new list entries in NTFS sorted order.
- Removes list entries and marks the list dirty.
- Persists dirty attribute-list content back to resident data or nonresident runs.

Important functions:
- `al_destroy()` frees the list run and entry buffer and resets dirty/size state.
- `ntfs_load_attr_list()` handles resident copy or nonresident run unpack plus read into a kvmalloc buffer.
- `al_enumerate()` validates bounds, size, and name offset before returning the next entry.
- `al_find_le()` and `al_find_ex()` locate the matching or preceding list entry for a VCN.
- `al_add_le()` grows the in-memory list, inserts a sorted entry, resizes `$ATTRIBUTE_LIST` through `attr_set_size_ex()`, and writes nonresident list data if needed.
- `al_remove_le()` removes an entry by memmove after validating it belongs to the current list.
- `al_update()` shrinks or writes the backing `$ATTRIBUTE_LIST` attribute and clears the dirty flag.

Research notes:
- The code assumes list entries are sorted by type, name, and VCN; lookup and insertion depend on that invariant.
- Nonresident list loading comments estimate worst-case memory at about 16 MiB for extremely fragmented 1 TiB files with 4 KiB clusters.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/attrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/bitfunc.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/bitfunc.c

This file implements two low-level bitmap predicates for ntfs3.

Main responsibilities:
- Checks whether every bit in `[bit, bit + nbits)` is clear.
- Checks whether every bit in `[bit, bit + nbits)` is set.
- Handles unaligned bit offsets and then scans byte/word-aligned regions efficiently.

Important functions and data:
- `fill_mask[]` and `zero_mask[]` provide first-N-bit and after-N-bit masks for partial bytes.
- `are_bits_clear()` returns true only if the selected range contains no set bits.
- `are_bits_set()` returns true only if the selected range contains all set bits.
- `BITS_IN_SIZE_T` lets the implementation scan native word chunks after alignment.

Research notes:
- These helpers are used by the ntfs3 bitmap allocator to verify free/used ranges in on-disk bitmap buffers.
- The code treats zero-length ranges as true in the initial partial-byte cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/bitfunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/bitmap.c

This file implements ntfs3 bitmap-window management for cluster and MFT allocation bitmaps. It keeps cached free-space extents in red-black trees while retaining the ability to rescan on-disk bitmap blocks.

Main responsibilities:
- Initializes and destroys a slab cache for free-extent nodes.
- Builds two extent trees for free ranges: one sorted by start, one sorted by length.
- Rescans on-disk bitmap data to initialize or rebuild cached free extents and per-window free counts.
- Marks bitmap ranges free or used and updates buffer heads, per-window counters, total zero counts, and cached extents.
- Safely marks only actually-free bits as used for repair/reconciliation scenarios.
- Checks whether ranges are free or used, using trees when possible and bitmap buffers otherwise.
- Finds allocatable free ranges with hint support, full-or-partial semantics, zone exclusion, largest-extent fallback, optional mark-as-used, and bitmap scanning fallback.
- Extends a bitmap, used for `$MFT` bitmap growth.
- Temporarily excludes a zone from allocation with `wnd_zone_set()`.
- Implements filesystem trim by scanning free bitmap ranges and calling discard.
- Provides little-endian bitmap set, clear, and weight helpers.

Important functions and data:
- `struct e_node` stores one free extent in both start and count trees.
- `NTFS_MAX_WND_EXTENTS` caps cached extents at 32K; if exceeded, the cache keeps larger extents and marks exactness degraded.
- `wnd_scan()` scans a bitmap buffer window for a free run and tracks the best fragment.
- `wnd_add_free_ext()` merges adjacent free extents and inserts or replaces cached extent nodes.
- `wnd_remove_free_ext()` removes or splits cached extents after allocation.
- `wnd_rescan()` walks bitmap runs, reads mapped blocks, counts zero bits, and rebuilds extent metadata.
- `wnd_init()` allocates `free_bits`, computes window count and final-window bits, and performs the initial rescan.
- `wnd_set_free()` and `wnd_set_used()` mutate on-disk bitmap buffers and cached state.
- `wnd_find()` is the allocator-facing free-space search routine.
- `wnd_extend()` grows the bitmap and zeroes new bits.
- `ntfs_trim_fs()` implements `FITRIM`-style discard over free clusters.
- `ntfs_bitmap_set_le()`, `ntfs_bitmap_clear_le()`, and `ntfs_bitmap_weight_le()` operate on little-endian bitmap words.

Notable implementation details:
- `wnd->free_bits[iw]` caches the number of free bits per bitmap block/window.
- `wnd->uptodated` tracks whether extent trees are exact, empty, or degraded.
- The zone `[zone_bit, zone_end)` is removed from free extents and skipped by allocation searches.
- Readahead is used during full rescans of mapped bitmap storage.

Research notes:
- This file is the core ntfs3 free-space allocator cache; allocator correctness depends on keeping on-disk bitmaps, counters, and extent trees synchronized.
- When the extent cache is incomplete, searches can fall back to direct bitmap scanning.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/debug.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/debug.h

This header defines ntfs3 debug/logging support and common pointer arithmetic macros.

Main responsibilities:
- Defines `Add2Ptr(P, I)` and `PtrOffset(B, O)` if not already defined.
- Declares `ntfs_printk()` and `ntfs_inode_printk()` with printf format checking when `CONFIG_PRINTK` is enabled.
- Provides no-op inline versions when printk support is disabled.
- Defines log-level wrappers: `ntfs_err`, `ntfs_warn`, `ntfs_info`, `ntfs_notice`, `ntfs_inode_err`, and `ntfs_inode_warn`.

Research notes:
- The pointer helpers are heavily used throughout ntfs3 metadata parsing for packed on-disk records.
- Logging macros centralize superblock- and inode-context messages while preserving kernel log levels.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/dir.c

This file implements ntfs3 directory name conversion, lookup by Unicode name, readdir iteration, directory entry emission, and directory emptiness/count checks.

Main responsibilities:
- Converts NTFS little-endian UTF-16 names to mounted NLS or UTF-8 output.
- Converts incoming NLS/UTF-8 names to UTF-16 for NTFS directory operations and symlink creation.
- Searches directory indexes for a Unicode name and returns the referenced inode.
- Emits directory entries while filtering DOS aliases, non-home entries, metadata files, hidden files, root self-reference, and malformed names.
- Iterates directory index root and allocation blocks in an unsorted physical/index order.
- Handles directories modified during readdir by restarting from a low position when the directory version changed after end-of-directory.
- Counts directories/files and checks whether a directory is empty.
- Defines `ntfs_dir_operations`.

Important functions:
- `ntfs_utf16_to_nls()` converts UTF-16 to UTF-8 when no NLS table is configured, or uses `uni2char()` with replacement and warning on conversion failure.
- `_utf8s_to_utf16s()` is a local UTF-8 to UTF-16 converter that detects output exhaustion before writing beyond the maximum.
- `ntfs_nls_to_utf16()` converts user names to UTF-16 in requested endian form.
- `dir_search_u()` calls `indx_find()` and then `ntfs_iget5()` for the matching directory entry reference.
- `ntfs_dir_emit()` validates and filters a directory entry, converts the file name, determines `d_type`, and may open the inode for more accurate type when extended duplicated info is present.
- `ntfs_read_hdr()` walks one `INDEX_HDR`, validates entry sizes and key sizes, updates `ctx->pos`, and calls the emitter.
- `ntfs_readdir()` emits dots, reads the index root, iterates used index allocation bits with readahead, and normalizes end/error positions.
- `ntfs_dir_count()` walks root and index blocks to count non-DOS directory and file entries.
- `dir_is_empty()` wraps `ntfs_dir_count()`.

Notable implementation details:
- Readdir intentionally uses non-sorted enumeration to avoid infinite loops if the directory name tree is corrupted.
- `ctx->pos` uses the index-root area first, then index allocation positions offset by `sbi->record_size`.
- `file->private_data` stores `ni->dir.version` to detect mutation during a directory stream.
- The comments explicitly discuss POSIX-unspecified readdir/unlink behavior and why ntfs3 attempts rmdir-like behavior for callers that remove while iterating.

Research notes:
- Directory presentation is strongly governed by mount options such as `showmeta` and `nohidden`.
- Dentry type from duplicated NTFS filename information is treated as potentially unreliable; the code optionally opens the inode for a better type in selected cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/dir.c -->