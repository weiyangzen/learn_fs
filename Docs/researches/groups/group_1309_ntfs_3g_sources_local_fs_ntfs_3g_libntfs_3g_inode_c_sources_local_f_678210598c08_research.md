# Group Research: group_1309_ntfs_3g_sources_local_fs_ntfs_3g_libntfs_3g_inode_c_sources_local_f_678210598c08

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/ntfs-3g`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/inode.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/inode.c

## Purpose
Implements NTFS inode lifecycle, dirty tracking, MFT record open/close, extent inode attachment, inode writeback, attribute-list creation, MFT-record space reclamation, timestamp helpers, and `$BadClus:$Bad` detection.

## Main Interfaces
- `ntfs_inode_base()` returns the base inode for extent inodes.
- `ntfs_inode_mark_dirty()` marks an inode and its base inode dirty.
- `ntfs_inode_allocate()` allocates an initialized in-memory inode shell.
- `ntfs_inode_open()` opens an MFT record, optionally through the nidata cache.
- `ntfs_inode_close()` syncs and either caches or releases an inode.
- `ntfs_inode_real_close()` performs actual close/release and closes extent inodes.
- `ntfs_extent_inode_open()` opens and attaches an extent MFT record to a base inode.
- `ntfs_inode_attach_all_extents()` walks an attribute list and attaches all referenced extents.
- `ntfs_inode_sync()` writes standard information, filename index state, attrlist data, and MFT records.
- `ntfs_inode_close_in_dir()` syncs while reusing an already-open parent directory inode.
- `ntfs_inode_add_attrlist()` creates and populates `$ATTRIBUTE_LIST`.
- `ntfs_inode_free_space()` moves eligible attributes out of the base record to free MFT-record space.
- `ntfs_inode_update_times()`, `ntfs_inode_get_times()`, and `ntfs_inode_set_times()` maintain NTFS timestamps.
- `ntfs_inode_badclus_bad()` identifies `$BadClus:$Bad`.

## Control Flow and State
Opening reads and validates the MFT record through `ntfs_file_record_read()`, extracts `$STANDARD_INFORMATION`, loads optional `$ATTRIBUTE_LIST`, and derives unnamed `$DATA` size state. Closing first syncs dirty metadata, then closes attached extents or disconnects an extent from its base inode before release. Cache-enabled builds avoid full release for non-system reusable inode data.

Sync ordering is deliberate: standard information, filename index entries, attrlist attribute contents, current MFT record, then dirty extent records. Filename sync updates parent directory `$I30` index entries and propagates file size, attributes, timestamps, and reparse tags.

## Integration Points
Depends heavily on `attrib.c`, `attrlist.c`, `mft.c`, `index.c`, `dir.c`, `lcnalloc.c`, `cache.c`, `ntfstime.c`, and `xattrs.h`. It is central glue between on-disk MFT records and higher-level file/directory operations.

## Risks and Invariants
- Reopening an inode is explicitly warned against because stale cache entries can be reused.
- Extent inode handling must avoid duplicate attachments and stale sequence references.
- `$MFT` extent lookup has special anti-recursion checks because malformed MFT extent placement can become unreadable.
- Rollback in `ntfs_inode_add_attrlist()` attempts to restore moved attributes, but failed rollback is logged as possible corruption.
- Timestamp setters mark `TimesSet` to avoid close-time lower-precision overwrite.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/ioctl.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/ioctl.c

## Purpose
Implements NTFS-3G ioctl dispatch, currently centered on Linux `FITRIM` support when both `FITRIM` and `BLKDISCARD` are available.

## Main Interfaces
- `ntfs_ioctl()` dispatches supported ioctls and returns negative errno-style failures.
- `fstrim()` scans the volume bitmap and issues discard requests for free cluster ranges.
- `fstrim_clusters()` sends `BLKDISCARD` to the backing block device.
- `fstrim_limits()` reads discard alignment, granularity, and max-byte limits from `/sys/dev/block`.
- `read_line()` and `read_u64()` read sysfs numeric attributes.
- `align_up()` and `align_down()` align cluster ranges to device discard granularity.

## Control Flow
`ntfs_ioctl()` accepts `FITRIM`, validates inode/data, calls `fstrim()`, and writes actual trimmed byte count back to `struct fstrim_range.len`. `fstrim()` rejects non-default start/length/minlen options, requires a block device, reads discard limits, syncs the device, scans `$BITMAP` in 4096-byte chunks, finds contiguous free cluster runs, granularity-aligns them, caps requests by `discard_max_bytes`, then issues discard.

## Integration Points
Uses `ntfs_attr_pread()` on `vol->lcnbmp_na`, `ntfs_bit_get()` bitmap helpers, `ntfs_device_sync()`, device `d_ops->ioctl`, and NTFS volume cluster sizing.

## Risks and Invariants
- FITRIM only supports full-volume trim with default offset/length and `minlen <= cluster_size`.
- Non-block-device backing stores return `-EOPNOTSUPP`.
- Sysfs probing treats missing discard files as “discard unavailable,” not fatal.
- Count calculation reads whole bitmap bytes; correctness depends on cluster count and bitmap sizing consistency.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/lcnalloc.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/lcnalloc.c

## Purpose
Provides cluster allocation and deallocation over the volume LCN bitmap, respecting NTFS MFT-zone reservation and reducing fragmentation through zone cursors and run coalescing.

## Main Interfaces
- `ntfs_cluster_alloc()` allocates clusters and returns a runlist.
- `ntfs_cluster_free_from_rl()` frees all non-sparse runs in a runlist.
- `ntfs_cluster_free_basic()` frees a single LCN/count range.
- `ntfs_cluster_free()` frees clusters from an attribute runlist starting at a VCN.
- Internal helpers maintain zone cursors, full-zone state, bitmap writeback, and empty-run discovery.

## Control Flow
The allocator scans `$BITMAP` in 4096-byte buffers. It starts either from a caller hint or from the relevant zone cursor. It searches zones in passes: current point to zone end, then zone start to current point, then switches among MFT, data1, and data2 zones. Free bits are set in memory, contiguous LCNs are coalesced into runlist entries, bitmap chunks are written back, volume free-cluster counters are updated, and zone cursors advance with a skip distance.

On error, the partial runlist is terminated, dumped for debugging, freed through `ntfs_cluster_free_from_rl()`, and discarded.

## Integration Points
Uses `$BITMAP` through `vol->lcnbmp_na`, bitmap helpers, runlist helpers, `ntfs_attr_pread/pwrite`, and volume fields such as `mft_zone_start`, `mft_zone_end`, `data*_zone_pos`, `mft_zone_pos`, `full_zones`, and free-cluster counters.

## Risks and Invariants
- Partial allocation rollback relies on the runlist being validly terminated.
- Free counters are adjusted optimistically and checked against `nr_clusters`.
- `ntfs_cluster_free()` contains FIXME notes for rollback gaps if freeing later runs fails.
- The allocator marks full zones and later clears those marks when a cluster in that zone is freed.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/lcnalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.pc.in -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.pc.in

## Purpose
Pkg-config template for the `libntfs-3g` library.

## Contents
Defines substituted install variables:
- `prefix`
- `exec_prefix`
- `libdir`
- `includedir`

Exports:
- `Name: libntfs-3g`
- `Description: NTFS-3G Read/Write Driver Library`
- `Version: @PACKAGE_VERSION@`
- `Cflags: -I${includedir}`
- `Libs: @LIBFUSE_LITE_LIBS@ -L${libdir} -lntfs-3g`

## Integration Points
Consumed by build/install tooling to generate a `.pc` file for downstream compilation and linking.

## Risks
Correctness depends on configure-time substitution of package version, include/lib directories, and optional FUSE-lite libraries.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.script.so.in -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.script.so.in

## Purpose
Linker script template for locating the actual `libntfs-3g.so`.

## Contents
Contains:
- `@OUTPUT_FORMAT@`
- `GROUP ( @rootlibdir@/libntfs-3g.so  )`

## Integration Points
Used by the build/install process to emit a linker script that redirects linking to the library in `rootlibdir`.

## Risks
Depends entirely on correct configure-time substitution of output format and root library directory.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.script.so.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/logfile.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/logfile.c

## Purpose
Validates and optionally clears NTFS `$LogFile`, enough to decide whether the volume journal indicates clean shutdown. It checks restart pages and restart areas, not full log replay.

## Main Interfaces
- `ntfs_check_logfile()` validates `$LogFile` and returns the most recent valid restart page.
- `ntfs_is_logfile_clean()` checks clean-shutdown state from the restart area.
- `ntfs_empty_logfile()` overwrites a clean non-resident `$LogFile` with `0xff` bytes and marks it empty.
- Internal validators check restart page headers, restart areas, log client arrays, and load/deprotect restart pages.

## Control Flow
`ntfs_check_logfile()` caps size, verifies minimum size, scans candidate restart page positions, reads the first NTFS block, accepts `RSTR` or `CHKD` pages, validates header/area/client lists, loads and MST-deprotects the full page, and chooses the page with the newer LSN. Empty logfiles set the volume empty flag and pass.

`ntfs_is_logfile_clean()` treats an already-empty logfile as clean; otherwise it requires valid restart magic and either no active clients or `RESTART_VOLUME_IS_CLEAN`.

## Integration Points
Uses `ntfs_attr_pread/pwrite`, MST fixups from `mst.c`, logfile layout structures, and volume flags such as `NVolLogFileEmpty`.

## Risks and Invariants
- Version support is limited to `$LogFile` 1.1 and 2.0, with 2.0 still treated carefully.
- Chkdsk-modified restart pages may lack update sequence arrays.
- The implementation is intentionally conservative and may classify some idle unclean shutdowns as dirty.
- `ntfs_empty_logfile()` requires a prior clean check and rejects resident `$LogFile`.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/logfile.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/logging.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/logging.c

## Purpose
Centralized logging framework for NTFS-3G library/tools, with configurable levels, style flags, and output handlers.

## Main Interfaces
- `ntfs_log_get_levels()`, `ntfs_log_set_levels()`, `ntfs_log_clear_levels()`.
- `ntfs_log_get_flags()`, `ntfs_log_set_flags()`, `ntfs_log_clear_flags()`.
- `ntfs_log_set_handler()` installs the active handler.
- `ntfs_log_redirect()` is the central varargs dispatcher used by logging macros.
- Handlers: `ntfs_log_handler_syslog()`, `ntfs_log_handler_fprintf()`, `ntfs_log_handler_null()`, `ntfs_log_handler_stdout()`, `ntfs_log_handler_outerr()`, `ntfs_log_handler_stderr()`.
- `ntfs_log_early_error()` logs before normal redirection.
- `ntfs_log_parse_option()` handles `--log-*` options.

## Control Flow
A static `ntfs_log` struct holds enabled levels, style flags, and handler. `ntfs_log_redirect()` preserves caller `errno`, filters disabled levels, invokes the handler, and restores `errno`. The fprintf handler applies optional filename, line, function, prefix, perror text, and debug indentation.

## Integration Points
Used throughout libntfs-3g via logging macros. Syslog integration is conditional on `HAVE_SYSLOG_H`.

## Risks and Invariants
- `errno` preservation is a key invariant.
- Non-debug syslog suppresses `ENOSPC` perror spam.
- Default handler is null in non-debug builds, outerr in debug builds.
- `ntfs_log_parse_option()` only recognizes debug, verbose, quiet, and trace options.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/logging.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/mft.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/mft.c

## Purpose
Implements low-level MFT record IO, validation, layout/formatting, MFT bitmap growth, MFT data growth, MFT record allocation/freeing, and update sequence number adjustment.

## Main Interfaces
- `ntfs_mft_records_read()` and `ntfs_mft_records_write()` read/write MST-protected MFT records.
- `ntfs_mft_record_check()` validates MFT record structure and attribute ordering/sizes.
- `ntfs_file_record_read()` reads, validates, and sequence-checks a FILE record.
- `ntfs_mft_record_layout()` initializes an empty record in memory.
- `ntfs_mft_record_format()` writes a freshly laid-out record.
- `ntfs_mft_record_alloc()` allocates a base or extent MFT record.
- `ntfs_mft_record_free()` marks an MFT record free and clears its bitmap bit.
- `ntfs_mft_usn_dec()` decrements a record update sequence number.
- Internal helpers grow `$MFT/$BITMAP`, grow `$MFT/$DATA`, and initialize newly exposed records.

## Control Flow
MFT reads refuse records beyond initialized `$MFT/$DATA`, use `ntfs_attr_mst_pread()`, and leave records deprotected. Writes protect records, update `$MFT`, and mirror affected low-numbered records to `$MFTMirr`.

Allocation first searches `$MFT/$BITMAP` after reserved records or near a base inode for extents. If no free bit exists, it extends bitmap allocation/initialized size, extends `$MFT/$DATA`, formats newly initialized records, marks the chosen bit, reads and reformats the old record while preserving sequence/USN when possible, sets `MFT_RECORD_IN_USE`, creates an `ntfs_inode`, and attaches it for extent allocations. Errors attempt to undo bitmap bits, cluster allocations, runlists, mapping pairs, and attribute sizes.

Freeing clears in-use flag, increments sequence number, syncs the inode, clears the bitmap bit, then closes/releases the inode; rollback restores bitmap bit and old sequence on failure.

## Integration Points
Core dependencies include `attrib.c`, `bitmap.c`, `lcnalloc.c`, `runlist.c`, `inode.c`, and MST-protected attribute IO. The file manipulates `vol->mft_na`, `vol->mftbmp_na`, `vol->mftmirr_na`, `vol->free_mft_records`, and `vol->mft_data_pos`.

## Risks and Invariants
- Records 0-23 are reserved; normal allocation starts at `RESERVED_MFT_RECORDS` 64 in this code.
- MFT extents have special placement rules to avoid circular dependency where extents are needed to find themselves.
- Several failure paths log “Leaving inconsistent metadata. Run chkdsk.” if rollback cannot fully restore on-disk state.
- `$MFTMirr` write failure is logged as needing chkdsk.
- `ntfs_mft_rec_init()` appears to return `-1` even after updating sizes; it is only used in the special `$MFT` extent path and warrants scrutiny.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/mft.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/misc.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/misc.c

## Purpose
Small allocation wrapper module that logs allocation failures consistently.

## Main Interfaces
- `ntfs_calloc(size)` calls `calloc(1, size)` and logs failure.
- `ntfs_malloc(size)` calls `malloc(size)` and logs failure.
- `ntfs_realloc(ptr, size)` calls `realloc()` and logs failure.
- `ntfs_free(p)` wraps `free()`.

## Integration Points
Used across libntfs-3g for allocation with logging through `logging.c`.

## Risks
Wrappers do not alter allocation semantics. `ntfs_realloc()` returns `NULL` on failure and leaves original pointer ownership with the caller, matching standard `realloc()`.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/mst.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/mst.c

## Purpose
Implements NTFS multi-sector transfer fixup handling for protected records such as MFT records and logfile pages.

## Main Interfaces
- `ntfs_mst_post_read_fixup_warn()` validates and deprotects a record after read, optionally warning.
- `ntfs_mst_post_read_fixup()` calls the warning variant with warnings enabled.
- `ntfs_mst_pre_write_fixup()` applies update sequence protection before write.
- `ntfs_mst_post_write_fixup()` restores original sector tails in memory after write protection.
- Internal `is_valid_record()` validates size, USA offset/count, and sector alignment.

## Control Flow
Post-read validation checks the USA header, compares each protected sector tail to the update sequence number, marks the record `BAAD` on incomplete transfer, and restores saved sector tails from the USA array. Pre-write increments the USN cyclically, stores original sector tails in the USA, and writes the USN into each tail.

## Integration Points
Used by MFT and logfile attribute IO. Depends on NTFS layout definitions and logging.

## Risks and Invariants
- Record size must be an NTFS block-size multiple.
- USA must fit before the last word in the first sector.
- USN skips `0` and `0xffff`.
- `ntfs_mst_post_write_fixup()` assumes a successful preceding pre-write fixup and performs no validation.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/mst.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/object_id.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/object_id.c

## Purpose
Implements NTFS object ID extended attribute handling and `$Extend/$ObjId:$O` index maintenance.

## Main Interfaces
- `ntfs_get_ntfs_object_id()` reads object ID xattr data, merging index-stored birth/domain GUIDs when available.
- `ntfs_set_ntfs_object_id()` creates/replaces object ID data and index entry.
- `ntfs_remove_ntfs_object_id()` removes object ID attribute and index entry.
- `ntfs_delete_object_id_index()` removes only the index entry for an existing attribute.
- Internal helpers open `$ObjId`, add/remove/update index entries, merge index data, and create a dummy attribute.

## Control Flow
The on-file `$OBJECT_ID` attribute stores only the object GUID. The `$ObjId` index stores GUID key to file reference plus birth volume/object/domain GUIDs. Setting first opens `$Extend/$ObjId`, checks uniqueness unless the existing entry belongs to the same inode, adds the attribute if allowed by xattr flags, removes any old index entry, truncates/writes the GUID attribute, and inserts the full index entry.

Removal removes the index first, then removes the attribute; if attribute removal fails after index removal, it attempts to restore the index and logs possible corruption.

## Integration Points
Uses `ntfs_inode_open()`, `ntfs_inode_lookup_by_mbsname()`, `ntfs_index_ctx_get()`, `ntfs_index_lookup()`, `ntfs_ie_add()`, `ntfs_index_rm()`, attribute read/write/truncate/remove helpers, and xattr flag semantics.

## Risks and Invariants
- GUID indexing uses Windows-compatible little-endian comparison semantics.
- NTFS version must be at least 3 for adding object ID attributes.
- Partial failure can leave object ID/index inconsistency; code attempts repair and logs possible corruption.
- `ntfs_get_ntfs_object_id()` treats unexpected attribute sizes as unsupported.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/object_id.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/realpath.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/realpath.c

## Purpose
Provides device-path canonicalization, with Linux-specific repair for device-mapper paths.

## Main Interfaces
- `ntfs_realpath()` fallback is provided only when system `realpath()` is unavailable.
- `ntfs_realpath_canonicalize()` canonicalizes a path and maps `/dev/dm-N` back to `/dev/mapper/<name>` on Linux.
- Internal `canonicalize_dm_name()` reads `/sys/block/<dm>/dm/name`.

## Control Flow
Canonicalization first resolves the path normally. On Linux, if the basename matches `dm-<digits>`, it reads the device-mapper name from sysfs and returns `/dev/mapper/<name>` instead.

## Integration Points
Used around mount/device path reporting to avoid canonicalizing mapper devices into paths that are difficult to unmount.

## Risks
The fallback `ntfs_realpath()` copies into `PATH_MAX` bytes but writes `resolved_path[PATH_MAX]`, so callers must provide at least `PATH_MAX + 1` bytes. Linux mapper repair depends on sysfs availability.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/realpath.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/reparse.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/reparse.c

## Purpose
Handles NTFS reparse points, including junctions, Windows symlinks, WSL symlinks/special files, raw reparse xattrs, and `$Extend/$Reparse:$R` index maintenance.

## Main Interfaces
- `ntfs_make_symlink()` converts supported reparse point data into a Linux symlink target.
- `ntfs_possible_symlink()` checks whether reparse data might describe a link.
- `ntfs_get_ntfs_reparse_data()`, `ntfs_set_ntfs_reparse_data()`, `ntfs_remove_ntfs_reparse_data()` expose raw reparse data through xattr-style APIs.
- `ntfs_delete_reparse_index()` removes the reparse index entry.
- `ntfs_reparse_check_wsl()` validates WSL special file tags.
- `ntfs_reparse_set_wsl_symlink()` and `ntfs_reparse_set_wsl_not_symlink()` create WSL reparse data.
- `ntfs_get_reparse_point()` returns validated reparse data.

## Control Flow
Validation checks reparse header sizing, Microsoft vs non-Microsoft header length rules, tag-specific payload bounds, directory requirement for mount points, WSL symlink type, and WSL special-file flags. Link conversion distinguishes junction/full paths (`\??\`, `\\?\Volume{}`), absolute paths (`\` or `X:\`), relative paths, and WSL symlinks. Same-volume targets are resolved through directory indexes with case correction; unresolved drive/volume targets are mapped through `/.NTFS-3G/` stubs.

Setting raw reparse data validates the payload, opens `$Extend/$Reparse`, creates the unnamed `$REPARSE_POINT` attribute if needed, sets `FILE_ATTR_REPARSE_POINT`, writes the data, and inserts/updates the index entry. Removal removes the index first, removes the attribute, clears the file attribute flag, and marks filename index data dirty.

## Integration Points
Depends on inode, directory, index, attribute, volume, xattr, and EA helpers. It opens `$Extend/$Reparse`, uses `$R` index entries keyed by reparse tag plus file ID, and coordinates with filename sync through `NInoFileNameSetDirty()` when reparse flags/tags change.

## Risks and Invariants
- Link target resolution intentionally stops before dereferencing nested reparse points.
- Relative symlink resolution has a hard safety limit of 32 path components.
- Several structures use packed on-disk data and comments warn about alignment-sensitive processors.
- Raw set warns that EA compatibility is no longer checked because Windows 10 requires otherwise, which may affect older Windows versions.
- Failed index restore/removal paths can leave inconsistency and are logged as possible corruption.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/reparse.c -->