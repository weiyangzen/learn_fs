# Group Research: group_804_linux_sources_os_linux_linux_fs_ntfs_super_c_sources_os_linux_linux__d571c82aa294

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/super.c -->
# File Research: sources/os/linux/linux/fs/ntfs/super.c

Read coverage: complete file, 2786 lines.

This is the legacy `ntfs` filesystem driver's superblock and module lifecycle implementation. It owns mount option parsing, filesystem context allocation, boot sector validation, metadata bootstrap, VFS super operations, free-space accounting, dirty-volume handling, shutdown, and module cache/workqueue setup.

Key entry points and exports:
- `ntfs_parse_param()` parses fs_context options such as `uid`, `gid`, masks, NLS/charset, `errors=`, `show_sys_files`, case-sensitivity toggles, sparse/preallocation behavior, hidden-file behavior, Windows-name checking, ACLs, discard, and remount-sensitive `mft_zone_multiplier`.
- `ntfs_reconfigure()` handles remount transitions, especially read-only to read-write safety checks against volume errors, dirty flags, chkdsk-modified flags, unsupported volume flags, logfile emptying, and quota state.
- `ntfs_handle_error()`, `ntfs_set_volume_flags()`, `ntfs_clear_volume_flags()`, and `ntfs_write_volume_label()` provide shared volume-state mutation helpers.
- `ntfs_fill_super()` is the core mount path. It reads and validates the NTFS boot sector, derives sector/cluster/MFT/index sizes, initializes allocator zones, loads `$MFT`, creates or references the global upcase table, loads system metadata files, creates the root dentry, computes free MFT records, and queues background free-cluster precomputation.
- `ntfs_put_super()`, `ntfs_sync_fs()`, `ntfs_force_shutdown()`, and `ntfs_statfs()` implement VFS superblock behavior.
- `init_ntfs_fs()` / `exit_ntfs_fs()` create and destroy slab caches, the workqueue, optional debug sysctls, and register/unregister filesystem type `"ntfs"`.

Core control flow:
- Boot validation starts in `is_boot_sector_ntfs()` and `read_ntfs_boot_sector()`, then `parse_ntfs_boot_sector()` enforces supported sector, cluster, MFT-record, index-record, cluster-count, and mirror-LCN constraints.
- `load_system_files()` is the metadata bootstrap hub. It loads/checks `$MFTMirr`, `$MFT/$BITMAP`, `$UpCase`, `$AttrDef`, `$Bitmap`, `$Volume`, `$LogFile`, root directory, hibernation status, and NTFS 3.x metadata such as `$Secure`, `$Extend`, and `$Quota`.
- The driver is conservative around write mounts: dirty/unsupported flags, hibernation, logfile failures, mirror mismatch, and quota problems can force read-only mode and set `NVolErrors()`.
- Free-space accounting is split between MFT record bitmap scanning and cluster bitmap scanning. Cluster scanning is done lazily in `precalc_free_clusters()` on `ntfs_wq`; waiters use `NVolFreeClusterKnown`.

Integration points:
- Uses kernel fs_context API, `get_tree_bdev()`, block device helpers, folios/page cache, slab caches, lockdep classes, NLS tables, xattr handlers, export ops, inode operations from sibling NTFS files, and the `volume.h` `ntfs_volume` state structure.
- Interacts with NTFS system files through inode and attribute helpers such as `ntfs_iget()`, `ntfs_attr_iget()`, `ntfs_attr_lookup()`, `ntfs_empty_logfile()`, `ntfs_mark_quotas_out_of_date()`, `ntfs_read_inode_mount()`, and MFT record mapping helpers.

Risks and invariants:
- Mount bootstrap uses many goto cleanup paths; ownership of system inodes, upcase references, NLS tables, and `lcn_empty_bits_per_page` is the main correctness risk.
- Write enablement depends on volume flags, hibernation detection, and logfile state; mistakes here risk Windows/NTFS consistency.
- `check_mft_mirror()` compares mirror records and runlists and must keep folio mappings balanced on all error paths.
- Free-cluster users can wait on `free_waitq`; initialization order and `NVolFreeClusterKnown` transitions are important for avoiding hangs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/sysctl.c -->
# File Research: sources/os/linux/linux/fs/ntfs/sysctl.c

Read coverage: complete file, 54 lines.

This file implements optional debug sysctl registration for the NTFS driver, compiled only when both `DEBUG` and `CONFIG_SYSCTL` are enabled.

Key logic:
- Defines a single sysctl table entry under `fs/ntfs` named `ntfs-debug`.
- The sysctl exposes the global `debug_msgs` integer through `proc_dointvec` with mode `0644`.
- `ntfs_sysctl(int add)` registers the table when `add` is true and unregisters it when false.
- Registration failure returns `-ENOMEM`; removal clears the saved `ctl_table_header *`.

Integration:
- Called from `super.c` module init/exit.
- Includes `debug.h`, where `debug_msgs` is declared/used by the NTFS debug infrastructure.

Risk:
- Only active in debug builds with sysctl support. Normal builds use the inline no-op from `sysctl.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/sysctl.h -->
# File Research: sources/os/linux/linux/fs/ntfs/sysctl.h

Read coverage: complete file, 26 lines.

This header declares or stubs the NTFS debug sysctl hook.

Key logic:
- If `DEBUG && CONFIG_SYSCTL`, declares `int ntfs_sysctl(int add);`.
- Otherwise provides an inline `ntfs_sysctl()` that always returns success.

Integration:
- Lets `super.c` call `ntfs_sysctl(1)` and `ntfs_sysctl(0)` unconditionally without scattering preprocessor conditionals.
- Keeps non-debug and non-sysctl builds free of runtime behavior.

Risk:
- Minimal. The stub intentionally ignores `add`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/time.h -->
# File Research: sources/os/linux/linux/fs/ntfs/time.h

Read coverage: complete file, 87 lines.

This header provides inline conversion helpers between Linux `timespec64` UTC timestamps and NTFS timestamps.

Key definitions:
- `NTFS_TIME_OFFSET` is the seconds offset between 1601-01-01 UTC and 1970-01-01 UTC.
- `utc2ntfs()` converts seconds/nanoseconds to 100 ns NTFS ticks and returns little-endian `__le64`.
- `get_current_ntfs_time()` uses `ktime_get_coarse_real_ts64()` then `utc2ntfs()`.
- `ntfs2utc()` converts little-endian NTFS ticks back to `struct timespec64` using `div_s64_rem()`.

Integration:
- Used anywhere the NTFS driver must read/write on-disk NTFS time fields.
- Handles endian conversion at the conversion boundary.

Risks:
- Negative NTFS-to-Unix conversions rely on signed division/remainder behavior. Callers should expect `tv_nsec` derived from a signed remainder for pre-1970 times.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/unistr.c -->
# File Research: sources/os/linux/linux/fs/ntfs/unistr.c

Read coverage: complete file, 477 lines.

This file implements Unicode and NLS string handling for the legacy NTFS driver. All NTFS strings are treated as little-endian UTF-16.

Key functions:
- `ntfs_are_names_equal()` and `ntfs_names_are_equal()` compare UTF-16 names, optionally case-insensitive via an upcase table.
- `ntfs_collate_names()` implements NTFS filename collation with invalid-character detection for `"`, `*`, `<`, `>`, and `?`.
- `ntfs_ucsncmp()` / `ntfs_ucsncasecmp()` compare little-endian Unicode strings with or without upcasing.
- `ntfs_file_compare_values()` adapts filename attributes to collation.
- `ntfs_nlstoucs()` converts mount-NLS or UTF-8 input names into little-endian UTF-16, allocating from `ntfs_name_cache` for normal names or `kvmalloc()` for longer requested limits.
- `ntfs_ucstonls()` converts UTF-16 names back to the mounted NLS/UTF-8 encoding, allocating/growing output when needed.
- `ntfs_ucsndup()` duplicates bounded UTF-16 strings.

Integration:
- Depends on `struct ntfs_volume` NLS settings, `ntfs_name_cache`, UTF conversion helpers, and the volume upcase table.
- Used by path lookup, directory indexing/collation, label handling, and filename conversion between VFS byte strings and NTFS UTF-16.

Risks:
- Error handling must release the right allocator family: slab cache for normal NTFS names and `kvfree()` for larger buffers.
- Name length limits are enforced at conversion time; callers must pass correct maximum lengths for filenames versus labels.
- Collation only validates invalid characters in `name1`, matching its documented contract.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/unistr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/upcase.c -->
# File Research: sources/os/linux/linux/fs/ntfs/upcase.c

Read coverage: complete file, 70 lines.

This file generates the legacy NTFS driver's default Unicode upcase table.

Key logic:
- `generate_default_upcase()` allocates `default_upcase_len` little-endian UTF-16 entries with `kvcalloc()`.
- Initializes identity mapping for all entries.
- Applies three compact tables:
  - range/add mappings for broad lowercase-to-uppercase spans,
  - duplicate alternating pairs where odd entries map to previous entries,
  - explicit word mappings for individual code points.
- Returns the generated table or `NULL` on allocation failure.

Integration:
- Called by `super.c` to create a global default upcase table under `ntfs_lock`.
- Volume `$UpCase` tables are compared with this generated table and may share it by reference.

Risk:
- The table is fixed and partial to NTFS expectations; correctness depends on matching Windows/NTFS upcase semantics used by on-disk indexes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/upcase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/volume.h -->
# File Research: sources/os/linux/linux/fs/ntfs/volume.h

Read coverage: complete file, 296 lines.

This header defines the legacy NTFS in-memory volume/superblock structure and inline helpers for volume flags and counters.

Key contents:
- `struct ntfs_volume` stores VFS superblock linkage, mount ownership/mask options, error policy, sector/cluster/MFT/index geometry, volume serial/version/flags/label, upcase and attrdef tables, allocator cursors/zones, system inode references, NLS state, free-space counters, dirty delayed-allocation accounting, a waitqueue, background work item, and preallocation size.
- Defines `NTFS_VOL_UID` and `NTFS_VOL_GID`.
- Enumerates `NV_*` state bits, including errors, visibility toggles, case sensitivity, logfile/quota flags, read-only/shutdown, compression, free-cluster-known, immutability, Windows-name checking, discard, and sparse disabling.
- Macro `DEFINE_NVOL_BIT_OPS()` emits `NVol*`, `NVolSet*`, and `NVolClear*` inline helpers for all flags.
- Inline counter helpers update free clusters, free MFT records, LCN empty-bit page counts, and dirty-cluster reservations.
- Declares `ntfs_available_clusters_count()` and `get_nr_free_clusters()`.

Integration:
- Central state carrier used across legacy NTFS mount, inode, allocation, directory, and metadata code.
- Counter helpers coordinate with `super.c` free-space precomputation via `NVolFreeClusterKnown` and `free_waitq`.

Risks:
- Many fields have cross-file ownership. Cleanup order in `super.c` must match this structure.
- Helpers that wait for `NVolFreeClusterKnown` can block if the background scan never completes.
- Atomic counters track approximations under concurrent allocation and delayed allocation; callers must respect the established locks around bitmap operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/volume.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/Kconfig -->
# File Research: sources/os/linux/linux/fs/ntfs3/Kconfig

Read coverage: complete file, 49 lines.

This Kconfig file defines build-time options for the newer Paragon `ntfs3` driver.

Options:
- `NTFS3_FS`: tristate NTFS read-write filesystem support for filesystem type/module `ntfs3`; selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`; depends on the legacy `NTFS_FS` not being built-in unless `ntfs3` is modular.
- `NTFS3_64BIT_CLUSTER`: optional 64-bit cluster support on 64-bit builds; warns that Windows cannot mount such volumes and recommends `N`.
- `NTFS3_LZX_XPRESS`: enables reading Windows 10 external compression formats xpress4k/xpress8k/xpress16k/lzx; recommends `Y`.
- `NTFS3_FS_POSIX_ACL`: enables Linux-only POSIX ACL support and selects `FS_POSIX_ACL`; recommends `N` if unsure.

Integration:
- Controls compilation paths in `Makefile` and conditional code such as WOF/LZX/XPRESS support.

Risk:
- Feature toggles change on-disk interoperability, especially 64-bit clusters and Linux-only ACLs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/Makefile -->
# File Research: sources/os/linux/linux/fs/ntfs3/Makefile

Read coverage: complete file, 56 lines.

This Makefile builds the `ntfs3` kernel module or built-in object set.

Key contents:
- Adds a subset of `W=1` warnings plus compiler-option-guarded warning flags.
- Suppresses selected `-Wextra` warnings that are noisy for this codebase.
- Builds `ntfs3.o` when `CONFIG_NTFS3_FS` is enabled.
- Core object list includes attribute, bitmap, directory, log, inode, index, runlist, superblock, upcase, xattr, compression, and namei/file support objects.
- Adds `lib/decompress_common.o`, `lib/lzx_decompress.o`, and `lib/xpress_decompress.o` when `CONFIG_NTFS3_LZX_XPRESS` is enabled.

Integration:
- Mirrors Kconfig feature selection.
- Sets stricter local warning policy than many kernel subdirectories.

Risk:
- Warning flags may expose compiler-version-specific issues; guarded flags reduce but do not eliminate portability concerns.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/attrib.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/attrib.c

Read coverage: complete file, 2776 lines.

This is the ntfs3 attribute allocation and mutation engine. It manipulates resident/nonresident attributes, runlists, delayed allocation, sparse/compressed data, WOF compression metadata, file size changes, and fallocate-style range operations.

Key functions:
- `attr_load_runs()` and `attr_load_runs_vcn()` unpack nonresident mapping pairs into run trees.
- `run_deallocate_ex()` frees physical clusters from run ranges, optionally trims and reconciles delayed-allocation runs.
- `attr_allocate_clusters()` finds free clusters, inserts runlist entries, handles preallocation, MFT-zone allocation, zeroout requests, delayed-allocation removal, and rollback on failure.
- `attr_make_nonresident()` converts a resident attribute into a nonresident one, copying existing data into allocated clusters or page cache and restoring metadata on failure.
- `attr_set_size_ex()` is the central resize path for resident/nonresident attributes. It handles growth, shrink, preallocation, delayed allocation, sparse/compressed attributes, multi-segment attributes, attribute-list creation/expansion, MFT special cases, size/valid-size/alloc-size updates, and rollback paths.
- `attr_data_get_block()` / `_locked()` map VCN to LCN, allocate sparse holes on demand, return special LCN values for resident, EOF, delayed, sparse, and compressed cases, and manage compressed-frame-aligned allocation.
- `attr_data_write_resident()` writes a dirty folio back into a resident `$DATA` attribute.
- `attr_load_runs_range()` ensures runlist coverage for byte ranges.
- `attr_wof_frame_info()` under `CONFIG_NTFS3_LZX_XPRESS` reads WOF compressed frame offset tables from resident or nonresident WOF data.
- `attr_is_frame_compressed()` detects whether an NTFS compression frame has sparse tail clusters.
- `attr_allocate_frame()` adjusts physical clusters for an LZNT compressed frame and updates total allocated size.
- `attr_collapse_range()`, `attr_punch_hole()`, and `attr_insert_range()` implement aligned range removal, sparse hole punching, and hole insertion for extended attributes.
- `attr_force_nonresident()` forces the default data attribute out of resident form.

Integration:
- Heavily depends on ntfs3 runlist, bitmap, MFT-record, attribute-list, inode, delayed-allocation, and compression helpers.
- Called from file I/O, fallocate, compression, inode growth/truncation, and metadata maintenance paths.
- Coordinates VFS inode size/bytes, `ni->i_valid`, parent duplicate-info update flags, and dirty inode/MFT state.

Risks and invariants:
- Most operations mutate both runlists and packed on-disk mapping pairs; rollback paths are critical.
- Attribute-list layout can change mid-operation, so many paths re-find base attributes after insertion or expansion.
- Delayed allocation and real allocation coexist; callers must hold `ni->file.run_lock` and `ni_lock()` as documented by each path.
- Sparse/compressed files require frame alignment and special total-size accounting.
- Several unrecoverable deep failures mark the inode bad because reconstructing prior multi-segment state is too complex.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/attrib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/attrlist.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/attrlist.c

Read coverage: complete file, 428 lines.

This file manages ntfs3 in-memory and on-disk attribute lists, used when one MFT record cannot hold all attribute records for an inode.

Key functions:
- `al_destroy()` frees the attribute-list run and entry buffer and clears dirty/size state.
- `ntfs_load_attr_list()` loads `ATTR_LIST` from resident data or from nonresident runs using `run_unpack_ex()` and `ntfs_read_run_nb()`.
- `al_enumerate()` safely iterates list entries, checking size, bounds, and name storage.
- `al_find_le()` and `al_find_ex()` locate list entries by type, name, and optional VCN, respecting NTFS sort order.
- `al_add_le()` inserts a sorted list entry, grows backing storage, updates the on-disk `ATTR_LIST` size via `attr_set_size_ex()`, and writes nonresident lists immediately.
- `al_remove_le()` removes an entry and marks the list dirty.
- `al_update()` writes dirty list contents back to resident or nonresident storage and marks the owning MFT record dirty.

Integration:
- Used by `attrib.c`, inode record splitting, and multi-segment attribute handling.
- Depends on name comparison, runlist, attribute size, and MFT helpers.

Risks:
- Entry validation and sorted insertion are essential; corrupt sizes or offsets can otherwise walk outside the allocated list.
- `al_add_le()` mutates memory before resizing storage and must undo insertion correctly on failure.
- Dirty nonresident lists require explicit writeback to keep list entries and attribute segments synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/attrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/bitfunc.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/bitfunc.c

Read coverage: complete file, 128 lines.

This file provides optimized bit-range predicates over little-endian bitmap memory.

Key functions:
- `are_bits_clear(lmap, bit, nbits)` returns true if all bits in `[bit, bit + nbits)` are zero.
- `are_bits_set(lmap, bit, nbits)` returns true if all bits in `[bit, bit + nbits)` are one.
- Both handle unaligned starting bits, byte-alignment cleanup, native `size_t` chunks, trailing bytes, and final partial bits.

Integration:
- Used by ntfs3 bitmap window code to validate free/used cluster ranges from on-disk bitmap buffers.
- Depends on `MINUS_ONE_T` from ntfs3 headers for full-word comparison.

Risks:
- Reads native `size_t *` from byte buffers after manual alignment. The alignment code is central to avoiding unaligned access issues.
- Endianness is safe for all-zeros/all-ones checks but these helpers are not general bit-order scanners.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/bitfunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/bitmap.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/bitmap.c

Read coverage: complete file, 1564 lines.

This file implements ntfs3 bitmap-window management for cluster/MFT allocation. It maintains per-window free-bit counts and two red-black trees of free extents: one ordered by start and one by length.

Key functions:
- `ntfs3_init_bitmap()` / `ntfs3_exit_bitmap()` create and destroy the `e_node` cache.
- `wnd_init()` initializes a `wnd_bitmap`, allocates per-window free counters, and scans the bitmap.
- `wnd_rescan()` reads bitmap windows from disk, populates free-bit counts, tracks total zeroes, and builds cached free extents, with support for an excluded allocation zone.
- `wnd_close()` frees counters, runlist storage, and extent tree nodes.
- `wnd_add_free_ext()` and `wnd_remove_free_ext()` maintain free-extent trees when bits are freed/allocated, merging/splitting extents and capping cached extents at `NTFS_MAX_WND_EXTENTS`.
- `wnd_set_free()`, `wnd_set_used()`, and `wnd_set_used_safe()` modify on-disk bitmap buffers and update cached counters/extents.
- `wnd_is_free()` and `wnd_is_used()` test ranges using extent caches first and falling back to bitmap reads.
- `wnd_find()` finds free space by hint, biggest extent, or bitmap scan, respecting `BITMAP_FIND_FULL`, `BITMAP_FIND_MARK_AS_USED`, and the reserved zone.
- `wnd_extend()` grows a bitmap, clears new bits, resizes counters, and adds the new free extent.
- `wnd_zone_set()` reserves or releases a zone by removing/adding it from cached free extents.
- `ntfs_trim_fs()` implements fstrim over free bitmap ranges.
- `ntfs_bitmap_set_le()`, `ntfs_bitmap_clear_le()`, and `ntfs_bitmap_weight_le()` are endian-aware bitmap primitives.

Integration:
- Used by allocation paths in `attrib.c` and broader ntfs3 cluster/MFT bitmap management.
- Maps bitmap VBOs through runlists to LBOs with `wnd_map()`, reads buffers with `ntfs_bread()`, and updates kernel buffer state.
- Calls discard/trim helpers for freed ranges and fstrim.

Risks and invariants:
- Tree cache can become approximate (`uptodated = -1`) when extent limits or allocation failures occur; scanning fallback must remain correct.
- `wnd_find()` has complex wraparound, zone exclusion, and partial-allocation behavior.
- All bitmap mutations must keep `free_bits`, `total_zeroes`, and extent trees synchronized with dirty buffer updates.
- Callers are expected to use `wnd->rw_lock`; several functions assume higher-level locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/debug.h -->
# File Research: sources/os/linux/linux/fs/ntfs3/debug.h

Read coverage: complete file, 55 lines.

This header defines ntfs3 debug/logging helpers.

Key contents:
- Declares `struct super_block` and `struct inode`.
- Defines pointer arithmetic helpers `Add2Ptr()` and `PtrOffset()` if not already defined.
- If `CONFIG_PRINTK` is enabled, declares `ntfs_printk()` and `ntfs_inode_printk()` with printf format checking.
- Otherwise provides empty inline stubs.
- Defines logging macros: `ntfs_err`, `ntfs_warn`, `ntfs_info`, `ntfs_notice`, `ntfs_inode_err`, and `ntfs_inode_warn`.

Integration:
- Included across ntfs3 source files for diagnostics and pointer helpers.
- Centralizes message severity prefixes.

Risk:
- `Add2Ptr()` / `PtrOffset()` are raw pointer arithmetic helpers used extensively for on-disk structure parsing; callers must validate bounds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/dir.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/dir.c

Read coverage: complete file, 679 lines.

This file implements ntfs3 directory name conversion, lookup helper behavior, directory iteration, emptiness/count checks, and directory file operations.

Key functions:
- `ntfs_utf16_to_nls()` converts little-endian UTF-16 NTFS names to the mount NLS encoding or UTF-8, replacing unconvertible characters with `_` and logging the first conversion failure.
- `_utf8s_to_utf16s()` and `put_utf16()` convert UTF-8 to UTF-16 with explicit output-limit handling and surrogate-pair support.
- `ntfs_nls_to_utf16()` converts VFS byte names to UTF-16 for NTFS creation/lookup, using mount NLS or UTF-8.
- `dir_search_u()` searches a directory index for a UTF-16 name and returns an inode from the found reference.
- `ntfs_dir_emit()` filters directory entries, converts names, determines `d_type`, skips DOS aliases, root/self/meta/hidden entries as configured, and emits to `dir_context`.
- `ntfs_read_hdr()` walks one NTFS index header and emits entries while validating entry sizes and key sizes.
- `ntfs_readdir()` implements `iterate_shared`, emits dot entries, loads subrecords if needed, enumerates root index entries then index allocation buffers, and handles directories modified during readdir by rewinding to a stable internal position.
- `ntfs_dir_count()` counts child directories/files and supports emptiness checks.
- `dir_is_empty()` wraps `ntfs_dir_count()`.
- `ntfs_dir_operations` wires directory file operations: llseek, generic directory read, iterate, fsync, open, ioctl, compat ioctl, and lease handling.

Integration:
- Depends on ntfs3 index lookup/enumeration, MFT inode loading, NLS conversion, directory index metadata, and file operation helpers.
- Directory enumeration uses `indx_find`, `indx_get_root`, `indx_used_bit`, `indx_read_ra`, and `ntfs_iget5()`.

Risks:
- Directory parsing must validate index entry bounds carefully to avoid corrupt-directory walks.
- `ntfs_readdir()` intentionally uses non-sorted enumeration to avoid loops in corrupted name trees.
- Name conversion can truncate output when buffers are too small; current emit buffer is `PATH_MAX` and guarded by static assertions.
- `d_type` is partly inferred from duplicated directory information and may require opening the inode for more accurate extended-data cases.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/dir.c -->