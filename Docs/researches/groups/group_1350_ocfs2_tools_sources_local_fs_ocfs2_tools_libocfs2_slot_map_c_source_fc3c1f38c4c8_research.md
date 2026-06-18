# Group Research: group_1350_ocfs2_tools_sources_local_fs_ocfs2_tools_libocfs2_slot_map_c_source_fc3c1f38c4c8

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/ocfs2-tools`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/slot_map.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/slot_map.c

Implements OCFS2 slot-map reading, writing, conversion, and formatting for the userspace library. It supports both legacy 16-bit slot maps and extended slot maps selected by `ocfs2_uses_extended_slot_map()`.

Key responsibilities:
- Byte-swaps legacy and extended slot-map structures on big-endian hosts.
- Reads the `SLOT_MAP_SYSTEM_INODE` through `ocfs2_lookup_system_inode()` and `ocfs2_read_whole_file()`.
- Writes slot maps through cached inode file writes.
- Converts raw on-disk maps into `struct ocfs2_slot_map_data`, a normalized in-memory representation.
- Formats/resizes the slot-map system file to match `s_max_slots`.

Important functions:
- `ocfs2_read_slot_map()` / `ocfs2_read_slot_map_extended()`: public typed wrappers over the common reader.
- `ocfs2_write_slot_map()` / `ocfs2_write_slot_map_extended()`: public typed wrappers over the common writer.
- `ocfs2_load_slot_map()` / `ocfs2_store_slot_map()`: normalized load/store API.
- `ocfs2_format_slot_map()`: validates the system inode, resizes allocation if needed, and writes an empty map.

Dependencies:
- `ocfs2_lookup_system_inode`, `ocfs2_read_whole_file`, `ocfs2_file_write`, cached inode APIs.
- `ocfs2_extend_allocation()` and `ocfs2_truncate()` for slot-map sizing.

Research notes:
- `ocfs2_size_slot_map()` deliberately sets `i_size` to the full allocation, not just bytes needed.
- Legacy maps reject `s_max_slots > OCFS2_MAX_SLOTS`; extended maps allow larger node numbers.
- The writer accepts either full-block byte count or logical map size as a successful write result because `ocfs2_file_write()` may report only `i_size`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/slot_map.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/sysfile.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/sysfile.c

Small helper for resolving OCFS2 system inode names to inode block numbers.

Key function:
- `ocfs2_lookup_system_inode(fs, type, slot_num, blkno)`

Behavior:
- Allocates a filename buffer sized for `OCFS2_MAX_FILENAME_LEN + 1`.
- Builds the system inode name with `ocfs2_sprintf_system_inode_name()`.
- Looks it up in `fs->fs_sysdir_blkno` using `ocfs2_lookup()`.
- Frees the temporary buffer before returning.

Dependencies:
- `ocfs2_malloc0`, `ocfs2_free`, `ocfs2_sprintf_system_inode_name`, `ocfs2_lookup`.

Research notes:
- This is a central lookup primitive used by slot maps, mkfs finalization, and other system-file operations.
- It assumes `fs->fs_sysdir_blkno` is already known and valid.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/truncate.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/truncate.c

Implements userspace OCFS2 truncate operations for regular file data, inline data, xattr value trees, xattr index trees, and indexed directory trees.

Key responsibilities:
- Walks extent trees depth-first and removes extents beyond a requested new size.
- Frees ordinary clusters or decreases refcounts for refcounted extents.
- Zeroes the tail inside a still-allocated cluster after truncation.
- Handles inline data and fast symlink truncation.
- Clears DIO orphan state by forcing truncation to current inode size.

Important functions:
- `truncate_iterate()`: extent iterator callback that trims records, deletes empty extent blocks, and frees clusters.
- `ocfs2_zero_tail_for_truncate()`: zeroes bytes after `new_i_size` inside the remaining cluster, performing COW first if refcounted.
- `ocfs2_zero_tail_and_truncate()`: public helper for trimming extents and zeroing the tail.
- `ocfs2_truncate_inline()`: truncates inline-data files and fast symlinks.
- `ocfs2_truncate_full()` / `ocfs2_truncate()`: public truncate API.
- `ocfs2_xattr_value_truncate()`, `ocfs2_xattr_tree_truncate()`, `ocfs2_dir_indexed_tree_truncate()`: truncate specialized metadata extent trees.

Dependencies:
- Extent iteration APIs, `ocfs2_free_clusters`, `ocfs2_decrease_refcount`, `ocfs2_refcount_cow`.
- Cached inode APIs and `ocfs2_write_cached_inode`.
- `ocfs2_extent_map_get_blocks` for locating physical blocks.

Research notes:
- Truncating into an internal extent block may require rereading the block to determine whether it became empty.
- If truncation reaches zero clusters, inode tree depth is reset to zero.
- Refcount tree is detached when a refcounted file is truncated to zero.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/unix_io.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/unix_io.c

Provides the Unix/Linux-backed `io_channel` implementation for libocfs2. It wraps file descriptor I/O, optional direct I/O, optional block caching, libaio vector reads, and I/O statistics.

Key responsibilities:
- Opens devices/files with `open64()`, normally using `O_DIRECT` unless buffered mode is requested.
- Reads/writes blocks via `pread64()` and `pwrite64()`.
- Provides libaio vector reads through `io_submit()` / `io_getevents()`.
- Maintains an optional cache using an rbtree for lookup and an LRU list for eviction.
- Supports shared caches across channels and optional `mlock()` pinning.
- Exposes stats for bytes read/written and cache hits/misses/inserts/removes.

Important functions:
- `io_open()` / `io_close()`: lifecycle for `io_channel`.
- `io_read_block()` / `io_write_block()`: normal block I/O with cache participation if enabled.
- `io_read_block_nocache()` / `io_write_block_nocache()`: avoid inserting new cache entries while updating existing ones.
- `io_vec_read_blocks()`: asynchronous vector read path.
- `io_init_cache()`, `io_init_cache_size()`, `io_destroy_cache()`, `io_share_cache()`.
- `io_validate_o_direct()`: probes viable block size for direct I/O.

Dependencies:
- POSIX/Linux I/O APIs, `libaio`, `linux/fs.h` for `BLKROGET`.
- `ocfs2/kernel-rbtree.h`, kernel-style list helpers, libocfs2 allocation wrappers.

Research notes:
- Negative `count` means byte count rather than block count in low-level read/write helpers.
- Cache correctness assumes cached blocks match disk contents; writes update cache after completed I/O.
- The direct-I/O validation loop tries block sizes from current size up to `OCFS2_MAX_BLOCKSIZE`.
- Includes a legacy Linux 2.4 block-device file-size-limit workaround.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/unix_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/unlink.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/unlink.c

Implements directory entry removal for OCFS2 userspace operations, supporting both classic directory blocks and indexed directories.

Key responsibilities:
- Removes a matching directory entry by name and/or inode.
- For classic directories, iterates entries and clears the inode field.
- For indexed directories, updates the data leaf, free-list metadata, dx leaf or inline dx entries, root count, and inode.

Important functions:
- `unlink_proc()`: classic directory iterator callback.
- `ocfs2_unlink_el()`: extent-list directory unlink path.
- `__ocfs2_delete_entry()`: merges a deleted entry into the previous record where possible.
- `ocfs2_unlink_dx()`: indexed-directory unlink path.
- `ocfs2_unlink()`: public API that checks RW mode and dispatches based on directory features.

Dependencies:
- Directory iteration, indexed directory search/write APIs.
- `ocfs2_read_inode`, `ocfs2_read_dx_root`, `ocfs2_dx_dir_search`, `ocfs2_write_dir_block`, `ocfs2_write_dx_leaf`, `ocfs2_write_dx_root`.

Research notes:
- Indexed unlink requires a non-null name and uses dx lookup results.
- The dx path updates `db_free_rec_len` and may add the leaf to the root free-list.
- The classic path reports `OCFS2_ET_DIR_NO_SPACE` when no matching entry was found, inherited from ext2fs-style behavior.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/unlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/xattr.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/xattr.c

Implements extended attribute hashing, byte-order conversion, block/bucket read-write helpers, and xattr iteration for OCFS2.

Key responsibilities:
- Hashes volume UUID and xattr names.
- Computes bucket/block layout values.
- Swaps xattr headers, entries, block headers, value roots, tree roots, and nested extent lists.
- Reads and writes xattr blocks with metadata ECC validation/computation.
- Reads and writes xattr buckets, including bucket ECC.
- Locates indexed xattr records by name hash.
- Iterates inline inode xattrs, external xattr blocks, and indexed xattr buckets.

Important functions:
- `ocfs2_xattr_uuid_hash()` / `ocfs2_xattr_name_hash()`.
- `ocfs2_swap_xattrs_to_cpu()` / `ocfs2_swap_xattrs_from_cpu()`.
- `ocfs2_read_xattr_block()` / `ocfs2_write_xattr_block()`.
- `ocfs2_read_xattr_bucket()` / `ocfs2_write_xattr_bucket()`.
- `ocfs2_xattr_get_rec()`: finds the extent record covering a name hash in an indexed xattr tree.
- `ocfs2_xattr_iterate()`: public iterator over all xattr storage locations.

Dependencies:
- Byteorder helpers, metadata ECC helpers, extent-list swap and search APIs.
- `ocfs2_tree_find_leaf`, `ocfs2_read_blocks`, `io_write_block`.

Research notes:
- Xattr swap handling is complex because headers may live in inode tails, xattr blocks, or 4K buckets independent of filesystem block size.
- The implementation uses a fake `ocfs2_filesys` with `fs_blocksize = objsize` for swap-barrier checks.
- Iteration stops on `OCFS2_XATTR_ABORT` or `OCFS2_XATTR_ERROR`; callers that mutate xattrs must restart.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/libtools-internal/Makefile

Builds the internal helper library `libtools-internal.a`.

Key contents:
- Includes top-level `Preamble.make` and `Postamble.make`.
- Builds `verbose.c`, `progress.c`, `utils.c`, and `scandisk.c`.
- Adds `-fPIC` to `CFLAGS`.
- Defines `VERSION` for compiled code.
- Supports optional debug executables for files containing `DEBUG_EXE`.

Build outputs:
- Uninstalled static library: `libtools-internal.a`.
- Optional debug programs named `debug_<file>` when `OCFS2_DEBUG_EXE` is set.

Research notes:
- This is a private library for shared ocfs2-tools CLI behavior.
- Debug executable discovery is dynamic via `awk` over `$(CFILES)`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/libtools-internal.h -->
# File Research: sources/local-fs/ocfs2-tools/libtools-internal/libtools-internal.h

Small private header exposing internal cross-module hooks for verbosity, interaction, and progress handling.

Declarations:
- `tools_verbosity()`
- `tools_is_interactive()`
- `tools_progress_clear()`
- `tools_progress_restore()`

Research notes:
- Public tool APIs are in headers under `include/tools-internal`; this header exposes internals needed between implementation files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/libtools-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/progress.c -->
# File Research: sources/local-fs/ocfs2-tools/libtools-internal/progress.c

Implements terminal-aware progress display for ocfs2-tools.

Key responsibilities:
- Maintains a global list of active progress records, allowing nested progress displays.
- Renders either percentages for bounded work or spinner characters for unbounded work.
- Adapts output width using `COLUMNS`, shrinking long names to short names and then truncated names.
- Uses carriage return on terminals and newline on non-tty output.
- Provides clear/restore hooks so normal log output does not corrupt the progress line.

Important functions:
- `tools_progress_enable()` / `tools_progress_disable()` / `tools_progress_enabled()`.
- `tools_progress_start(long_name, short_name, count)`.
- `tools_progress_step(prog, step)`.
- `tools_progress_stop(prog)`.
- Internal rendering helpers: `progress_compute()`, `progress_printf()`, `truncate_printf()`.

Dependencies:
- Kernel-style list API.
- `isatty`, `gettimeofday`, environment variable `COLUMNS`.

Research notes:
- Updates are throttled to roughly 1/8 second and skipped if displayed percentage is unchanged.
- When disabled, callers get a static fake `disabled_prog`, so step/stop calls are harmless.
- Progress output is integrated with `verbose.c` via `tools_progress_clear()` and `tools_progress_restore()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/progress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/scandisk.c -->
# File Research: sources/local-fs/ocfs2-tools/libtools-internal/scandisk.c

Implements Linux block-device discovery and classification for internal tooling.

Key responsibilities:
- Maintains a cached linked list of devices keyed by major/minor.
- Scans `/sys/block`, `/proc/partitions`, `/dev`, `/proc/mdstat`, and `/proc/devices`.
- Associates multiple paths with each device.
- Marks sysfs attributes such as removable, holders, slaves, and disk-like status.
- Marks device-mapper, mdraid, and powerpath devices.
- Allows callers to run a custom filter over the discovered list.

Important functions:
- `scan_for_dev(devlisthead, timeout, filter, filter_args)`: public scanner/cache entry point.
- `free_dev_list()`: public cleanup.
- `scansysfs()`: recursive `/sys/block` scanner.
- `scanprocpart()`: parses `/proc/partitions`.
- `lsdev()`: recursive `/dev` scanner for block devices and symlinks to block devices.
- `scanmdstat()`, `scanmapper()`, `scanpower()`: classify stacking technologies.

Dependencies:
- Linux procfs/sysfs conventions.
- `sys/sysmacros.h` major/minor helpers.
- Internal `tools-internal/scandisk.h`.

Research notes:
- Cache expiration is based on `cache_timestamp` and `cache_timeout`; nonpositive timeout means no expiration.
- Device discovery is tolerant of missing sources, but aborts on allocation failures.
- The debug executable demonstrates filtering for top-level disks with `/dev/sd*` or `/dev/mapper/*` paths.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/scandisk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/utils.c -->
# File Research: sources/local-fs/ocfs2-tools/libtools-internal/utils.c

Provides small string trimming helpers.

Functions:
- `tools_strchomp(char *str)`: removes trailing whitespace in place.
- `tools_strchug(char *str)`: removes leading whitespace in place by `memmove()`.

Dependencies:
- Standard C string and ctype APIs.
- `tools-internal/utils.h`.

Research notes:
- Both functions return the original buffer pointer.
- The file includes a `DEBUG_EXE` self-test for trimming behavior.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/verbose.c -->
# File Research: sources/local-fs/ocfs2-tools/libtools-internal/verbose.c

Implements shared verbose/error/interactive output behavior for ocfs2-tools.

Key responsibilities:
- Tracks program basename, verbosity level, and interactive mode.
- Wraps normal output so active progress displays are cleared and restored.
- Can suppress `com_err()` output when quiet mode drives verbosity below normal.
- Provides yes/no prompting with optional preset answers.
- Prints tool version using compiled `VERSION`.

Important functions:
- `tools_setup_argv0()`, `tools_progname()`.
- `tools_verbose()`, `tools_quiet()`, `tools_verbosity()`.
- `verbosef()`, `errorf()`, `tcom_err()`.
- `tools_interactive()`, `tools_interactive_yes()`, `tools_interactive_no()`, `tools_interact()`, `tools_interact_critical()`.
- `tools_version()`.

Dependencies:
- `com_err` hooks.
- `tools-internal/progress.h` and private `libtools-internal.h`.

Research notes:
- `tools_interact()` auto-approves if interactive mode is disabled.
- `tools_interact_critical()` always asks, intended for high-risk confirmations.
- Output target can be switched to stdout via `VL_FLAG_STDOUT`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libtools-internal/verbose.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/listuuid/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/listuuid/Makefile

Builds the `listuuid` utility.

Key contents:
- Includes top-level build pre/postamble.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, `uuid`, and `aio`.
- Adds optional `-ldlm_lt` when fsdlm support is enabled.

Build output:
- Uninstalled program: `listuuid`.

Research notes:
- The Makefile does not include `LIBO2CB_LIBS` in the final `$(LINK)` command despite declaring deps/libs; `listuuid.c` itself mainly uses libocfs2 and OCFS1 compatibility helpers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/listuuid/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/listuuid/listuuid.c -->
# File Research: sources/local-fs/ocfs2-tools/listuuid/listuuid.c

Implements a utility that lists OCFS/OCFS2 UUIDs and labels for devices.

Key responsibilities:
- Parses `/proc/partitions` to build candidate `/dev/<name>` entries.
- Optionally checks a single user-provided device.
- Opens each device as OCFS2 using `ocfs2_open()`.
- Detects OCFS1 via `OCFS2_ET_OCFS_REV`.
- Reads OCFS2 label/UUID from the superblock or OCFS1 label/UUID via compatibility helper.
- Prints a table with device, major/minor, filesystem type, UUID, and label.

Important functions:
- `ocfs2_partition_list()`
- `ocfs2_detect()`
- `ocfs2_print_uuids()`
- `read_options()`
- `main()`

Dependencies:
- `/proc/partitions`.
- `uuid_unparse`.
- `ocfs2_open`, `ocfs2_close`, `ocfs2_get_ocfs1_label`.

Research notes:
- `-a` sets `all_devices`, but the variable is not used by the detection logic in this file.
- If no device argument is supplied, it scans all partitions from `/proc/partitions`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/listuuid/listuuid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/Makefile

Builds and installs the `mkfs.ocfs2` formatter.

Key contents:
- Installs program under `$(root_sbindir)`.
- Builds from `mkfs.c` and `check.c`.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, `uuid`, and `aio`.
- Adds optional cluster stack libraries: `-lcmap` and/or `-ldlm_lt`.
- Builds man page `mkfs.ocfs2.8` from `.in` source.

Research notes:
- This target is tightly coupled to OCFS2 cluster libraries because formatting safety checks may query active cluster state and DLM.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/check.c -->
# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/check.c

Implements pre-format safety checks and cluster-information resolution for `mkfs.ocfs2`.

Key responsibilities:
- Determines active cluster stack information through o2cb.
- Reads existing on-disk cluster information if the target already has OCFS2 metadata.
- Merges user-provided, active-cluster, and on-disk cluster values.
- Rejects incompatible cluster configurations unless forced.
- Checks whether the device is mounted or busy.
- For existing OCFS2 volumes, tries to initialize DLM and lock the cluster before overwriting.

Important functions:
- `is_classic_stack()`
- `cluster_fill()`
- `ocfs2_fill_cluster_information()`
- `ocfs2_check_volume()`

Dependencies:
- `o2cb_init`, `o2cb_running_cluster_desc`, `o2cb_setup_stack`.
- `ocfs2_open`, `ocfs2_check_if_mounted`, `ocfs2_initialize_dlm`, `ocfs2_lock_down_cluster`.

Research notes:
- `--force` bypasses several safety gates but prints explicit warnings.
- Global heartbeat requires the classic `o2cb` stack and cluster information.
- Local mount skips cluster-information filling.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/check.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.c -->
# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.c

Main implementation of the OCFS2 filesystem formatter.

Key responsibilities:
- Parses command-line options for block size, cluster size, features, node slots, UUID, label, journal options, mount mode, cluster stack/name, heartbeat, discard, dry-run, force, and fs type.
- Computes default block/cluster/journal sizes and node slots.
- Opens the target device with direct I/O.
- Optionally discards device blocks.
- Clears both ends of the volume to remove stale metadata.
- Manually constructs initial OCFS2 superblock, root directory, system directory, system inodes, global bitmap, and allocator group.
- Writes all initial metadata with correct byte order and metadata ECC when enabled.
- Reopens the new filesystem with libocfs2 to finish higher-level structures: backup superblocks, journals, extent allocator growth, slot map, quotas, indexed directories, and `lost+found`.

Important top-level flow:
- `main()` sets signal handlers, initializes error tables, parses state, checks target safety, opens device, fills defaults, prints format plan, writes initial metadata, writes superblock, then calls `finish_normal_format()` unless formatting a heartbeat-only device.
- `finish_normal_format()` uses libocfs2 to finish filesystem initialization after the base image is readable.

Important functions:
- `get_state()`: option parsing and feature reconciliation.
- `fill_defaults()`: determines sizes, volume geometry, slot count, journal size, allocator reserve.
- `initialize_bitmap()` / `initialize_alloc_group()`: construct initial allocation metadata.
- `alloc_from_bitmap()` / `alloc_from_group()` / `alloc_inode()`: early allocator primitives.
- `add_entry_to_directory()`: builds root/system/orphan directory entries.
- `format_superblock()`: writes primary superblock dinode and feature fields.
- `format_file()`: writes system-file dinodes.
- `write_bitmap_data()`, `write_group_data()`, `write_directory_data()`.
- `format_journals()`, `format_slotmap()`, `format_backup_super()`.
- `index_system_dirs()`, `create_lost_found_dir()`.
- `mkfs_compute_meta_ecc()`: computes block checksums when metaecc is enabled.

Dependencies:
- libocfs2 feature parsing, metadata, directory, quota, journal, allocator, and slot-map APIs.
- libo2cb/libo2dlm safety checks via `check.c`.
- Linux direct I/O, `BLKDISCARD`, `/dev/urandom`.

Research notes:
- Initial filesystem creation is mostly manual because libocfs2 needs a readable filesystem before higher-level APIs can run.
- Feature flags are merged from feature level, explicit feature list, mount mode, cluster options, and heartbeat-device mode.
- Backup-super feature is cleared before primary superblock write, then set later by `format_backup_super()` after actual backup superblocks are written.
- `clear_both_ends()` is used both before formatting and as a failure cleanup path to reduce risk of leaving recognizable partial metadata.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.h -->
# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.h

Defines shared state, constants, and internal data structures for `mkfs.ocfs2`.

Key contents:
- Mount modes: local vs cluster.
- Formatting constants for reserved blocks, clear size, default OCFS2 policy values, block discard step.
- `SystemFileInfo`: static description of OCFS2 system files.
- `AllocGroup`: in-memory allocation group descriptor plus chain accounting.
- `SystemFileDiskRecord`: planned on-disk inode/extent/allocation metadata for a system file.
- `AllocBitmap`: global bitmap/group construction state.
- `DirData`: temporary directory buffer plus linked disk record.
- `State`: full formatter state from CLI, feature flags, geometry, cluster settings, allocator state, and filesystem type.

Declared functions:
- `is_classic_stack`
- `cluster_fill`
- `ocfs2_fill_cluster_information`
- `ocfs2_check_volume`

Dependencies:
- Standard C/POSIX headers.
- `uuid/uuid.h`, `ocfs2/ocfs2.h`, `ocfs2/bitops.h`, OCFS1 compatibility header.

Research notes:
- This header is local to `mkfs.ocfs2`; it exposes the contract between `mkfs.c` and `check.c`.
- `State` is the central object that carries parsed user intent and computed filesystem geometry through the formatter.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.ocfs2.8.in

Manual page template for `mkfs.ocfs2`.

Key contents:
- Synopsis and purpose of creating OCFS2 filesystems.
- Documents options for block size, cluster size, force, journal options, label, mount mode, node slots, filesystem type, feature sets, cluster stack/name, global heartbeat, discard, dry-run, quiet, UUID, verbose, version, and explicit block count.
- Explains feature levels: `max-compat`, `default`, `max-features`.
- Lists individual features and their semantics.
- Provides feature compatibility table by kernel/tool version.
- Provides feature bit-value table for debugging unsupported-feature mount failures.

Research notes:
- The man page states that default feature level enables sparse, unwritten, inline-data, xattr, indexed-dirs, discontig-bg, refcount, extended-slotmap, and clusterinfo.
- It warns strongly against manually reusing UUIDs.
- The `--no-backup-super` option is documented as deprecated in favor of `--fs-features=nobackup-super`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.ocfs2.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mkinstalldirs -->
# File Research: sources/local-fs/ocfs2-tools/mkinstalldirs

Portable shell helper for creating installation directory hierarchies.

Key responsibilities:
- Parses `--help`, `--version`, and `-m MODE`.
- Uses `mkdir -p` or `mkdir -m MODE -p` when available.
- Falls back to manually creating each path component.
- Applies mode with `chmod` in fallback mode.
- Handles path components beginning with `-` by prefixing `./`.

Research notes:
- This is the standard Automake-era public-domain `mkinstalldirs` script.
- It reports commands as it runs them.
- It exits with accumulated error status from failed mkdir/chmod operations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mkinstalldirs -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/Makefile

Builds and installs the `mount.ocfs2` helper.

Key contents:
- Installs program under `$(root_sbindir)`.
- Core source files include `fstab.c`, `mntent.c`, `realpath.c`, `sundries.c`, `xmalloc.c`, and `opts.c`.
- Main source is `mount.ocfs2.c`.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, and `aio`.
- Adds optional cluster support libraries for fsdlm and cmap.
- Builds man page `mount.ocfs2.8`.

Research notes:
- This mount helper carries forked/util-linux-style mount support files with OCFS2-specific modifications.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.c

Implements mount table reading, lookup, locking, and update logic for `mount.ocfs2`, based on classic util-linux mount code with OCFS2 modifications.

Key responsibilities:
- Detects whether `/etc/mtab` exists, is a symlink, or is writable.
- Reads `/etc/mtab`, falling back to `/proc/mounts`.
- Stores mount entries in a doubly linked `mntentchn` list.
- Finds mount entries by device, directory, or `loop=` option.
- Checks whether a name appears exactly once in the mount table.
- Locks `/etc/mtab` safely using link-based lock creation plus `fcntl()`.
- Updates `/etc/mtab` by rewriting through a temporary file and renaming.

Important functions:
- `mtab_does_not_exist()`, `mtab_is_a_symlink()`, `mtab_is_writable()`.
- `mtab_head()`, `read_mounttable()`, `read_mntentchn()`.
- `getmntfile()`, `getmntdirbackward()`, `getmntdevbackward()`, `getmntoptfile()`.
- `is_mounted_once()`.
- `lock_mtab()`, `unlock_mtab()`, `update_mtab()`.

Disabled code:
- fstab reading and lookup functions are compiled out with `#if 0 /* OCFS2 modification */`.
- LABEL/UUID fstab resolution helpers are also disabled.

Dependencies:
- Local mount helper infrastructure: `mntent.h`, `sundries.h`, `xmalloc.h`, `paths.h`, `nls.h`.
- Mount path constants such as `MOUNTED`, `MOUNTED_LOCK`, and `MOUNTED_TEMP`.

Research notes:
- If `/etc/mtab` is missing or a symlink, `update_mtab()` returns without writing.
- Lock handling installs signal handlers to ensure lock cleanup.
- `update_mtab()` supports unmount removal, remount option update, and insertion of absent entries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.h

Header for mount table helper functions used by `mount.ocfs2`.

Key contents:
- Declares `struct mntentchn`, a doubly linked wrapper around `struct my_mntent`.
- Exposes mtab status, lookup, lock, unlock, and update functions.
- Disables fstab-specific lookup declarations with `#if 0 /* OCFS2 modification */`.

Public declarations:
- `mtab_is_writable`, `mtab_does_not_exist`, `mtab_is_a_symlink`.
- `is_mounted_once`.
- `mtab_head`, `getmntfile`, `getmntoptfile`, `getmntdirbackward`, `getmntdevbackward`.
- `lock_mtab`, `unlock_mtab`, `update_mtab`.

Research notes:
- The header intentionally narrows util-linux-style fstab support to the mtab behavior needed by OCFS2 mount tooling.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.h -->