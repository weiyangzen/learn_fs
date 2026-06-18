# Group Research: group_267_btrfs_progs_sources_local_fs_btrfs_progs_cmds_rescue_chunk_recover_c_4a22ed700a56

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/btrfs-progs`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue-chunk-recover.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/rescue-chunk-recover.c

## Purpose

Implements `btrfs rescue chunk-recover` backend. It reconstructs a damaged chunk tree by scanning all devices for valid Btrfs tree blocks, extracting surviving chunk/block-group/device-extent metadata, deriving missing chunk records, validating reconstructed mappings against filesystem metadata, and finally rewriting the chunk tree, system chunk array, and missing block-group items.

## Main API

- `int btrfs_recover_chunk_tree(const char *path, int yes)` is the exported rescue entry point declared in `cmds/rescue.h`.
- Internal state is centered on `struct recover_control`, which owns recovered metadata caches, device set, checksum/super geometry, and chunk classification lists:
  - `chunk`, `bg`, `devext`, `eb_cache`
  - `good_chunks`, `bad_chunks`, `rebuild_chunks`, `unrepaired_chunks`
  - `rc_lock` for multithreaded scan insertion

## Control Flow

1. `recover_prepare()` opens the input device, reads a recovery-mode superblock, rejects seed devices, records sectorsize/nodesize/generation/checksum details, and scans all filesystem devices.
2. `scan_devices()` starts one pthread per device. `scan_one_device()` walks the device at node-size intervals, skips superblock bytenrs, verifies fsid and tree-block checksum, records newest matching tree blocks, and extracts metadata leaf items from extent/dev/chunk trees.
3. `check_chunks()` reconciles chunk, block-group, and device-extent records into good/bad/rebuild lists. If orphan block groups or device extents remain, `btrfs_recover_chunks()` creates synthetic chunk records from block groups and orphan device extents.
4. Stripe recovery uses metadata location for ordered metadata RAID chunks and checksum-guided matching for data RAID chunks.
5. `open_ctree_with_broken_chunk()` builds an in-memory mapping tree from recovered good/rebuild chunk records so normal metadata can be read.
6. Metadata cross-checks run through `check_all_chunks_by_metadata()` and `btrfs_rebuild_ordered_data_chunk_stripes()`.
7. After confirmation, a write transaction removes old system chunk extent items, rebuilds the chunk root, inserts device and chunk items, rebuilds the system array, and inserts missing block-group items.

## Notable Algorithms

- Newer duplicate records replace older generation records during scan insertion.
- `btrfs_rebuild_ordered_meta_chunk_stripes()` maps tree-block logical addresses to expected stripe indexes to recover stripe order for stripey metadata chunks.
- `rebuild_raid_data_chunk_stripes()` attempts to identify data stripe ordering by comparing checksum tree entries against candidate device extents.
- `validate_rebuild_chunks()` rejects rebuilt chunks that overlap already-good chunks.

## Dependencies

Uses btrfs-progs shared libraries for tree access, transactions, volume mapping, chunk/block-group/device-extent record creation, checksum validation, extent buffers, and cache trees. It also reuses `check_chunks()` and shared block-group/device extent structures from checker code.

## Risks And Edge Cases

- The final repair phase uses `BUG_ON()` after transaction start for several failures, so unexpected write-side errors can abort rather than unwind cleanly.
- `check_one_csum()` contains `UASSERT(0)` and initializes `csum_size` to zero before comparing checksums; this is suspicious because RAID data stripe recovery calls it.
- `calculate_bg_used()` tests `BTRFS_EXTENT_DATA_KEY` while walking the extent tree, where extent items are expected as `BTRFS_EXTENT_ITEM_KEY` or `BTRFS_METADATA_ITEM_KEY`; this can undercount block-group used bytes.
- The recovery scan is raw-device and sector/node stepping based; false negatives are possible if metadata is not aligned as expected or only older generations remain.
- RAID56 data stripe order recovery has explicit limitations for parity-based inference.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue-chunk-recover.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue-fix-data-checksum.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/rescue-fix-data-checksum.c

## Purpose

Implements `btrfs rescue fix-data-checksum`, a specialized offline tool that scans checksum items, verifies all mirrors for each checksummed data sector, reports logical blocks with checksum/read failures, resolves affected filenames, and optionally updates checksum items from a selected mirror.

## Main API

- `int btrfs_recover_fix_data_checksum(const char *path, enum btrfs_fix_data_checksum_mode mode, unsigned int mirror)`
- Modes come from `cmds/rescue.h`:
  - readonly report only
  - interactive prompt per corrupted logical block
  - noninteractive checksum update from a selected mirror

## Control Flow

1. Checks mount status and refuses mounted filesystems.
2. Opens the ctree with `OPEN_CTREE_WRITES`.
3. Rejects running replace or balance operations.
4. Gets the checksum root and walks all `BTRFS_EXTENT_CSUM_KEY` items.
5. For each checksummed sector, `verify_one_data_block()` reads every mirror and compares computed checksum with the csum item bytes.
6. Corrupted logical blocks are accumulated in global `corrupted_blocks`.
7. `report_corrupted_blocks()` prints affected logical bytenrs, failed mirror numbers, paths resolved through backrefs, and applies the selected repair action.
8. `update_csum_item()` starts a transaction, reads the chosen mirror, recomputes the checksum, overwrites the csum item, and commits.

## State

- `struct corrupted_block` records logical bytenr, mirror count, and a bitmap of failed mirrors.
- `corrupted_blocks` is a global list freed at command exit.
- `global_repair_mode` is assigned but not used later in this file.

## Dependencies

Uses checksum root helpers, data mirror reads, inode backref/path resolution, transaction helpers, mount-status checks, and shared rescue mode declarations.

## Risks And Edge Cases

- In `add_corrupted_block()`, the duplicate-last-entry path calls `set_bit(mirror, ...)`, while the new-entry path uses `set_bit(mirror - 1, ...)`; this looks like an off-by-one bug for repeated corruption records.
- `verify_one_data_block()` continues to checksum `buf` after `read_data_from_disk()` fails, so a failed read can be followed by a checksum comparison against stale or undefined data.
- `iterate_one_csum_item()` allocates `buf` but never uses it.
- `update_csum_item()` has an error format typo: `"failed to find csum item for logical %llu: $m"`.
- Updating checksum items is dangerous when the selected mirror is itself stale or corrupt; the tool trusts the user or requested mirror.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue-fix-data-checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue-super-recover.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/rescue-super-recover.c

## Purpose

Implements `btrfs rescue super-recover` backend. It scans all devices and superblock mirror locations, classifies valid current-generation superblocks as good and invalid/outdated ones as bad, then rewrites all superblock copies from a good copy after user confirmation.

## Main API

- `int btrfs_recover_superblocks(const char *dname, int yes)`

## Control Flow

1. Opens the provided device and scans filesystem devices in recovery mode.
2. `read_fs_supers()` iterates all devices and calls `read_dev_supers()` for each super mirror offset.
3. Valid superblocks are added to `good_supers`; corrupted readable locations go to `bad_supers`.
4. Valid superblocks older than the maximum observed generation are moved to `bad_supers`.
5. If no bad supers exist, reports no recovery needed.
6. Otherwise asks for confirmation unless `yes` is set.
7. Opens the ctree from the first good superblock using `OPEN_CTREE_RECOVER_SUPER | OPEN_CTREE_WRITES`.
8. Resets `super_bytenr` to the primary super offset and calls `write_all_supers()`.

## State

- `struct btrfs_recover_superblock` owns the scanned device set, good/bad lists, and maximum generation.
- `struct super_block_record` stores device name, superblock copy, and bytenr.

## Dependencies

Uses device scanning, superblock reads, list helpers, super writers, and normal ctree open/close paths.

## Risks And Edge Cases

- The implementation assumes at least one good superblock remains if bad superblocks exist; it takes the first good record before rewriting.
- Recovery rewrites all superblock mirrors and can destroy non-Btrfs data if pointed at the wrong device; the command-level wrapper also checks mount status.
- Return codes are user-facing status values rather than plain negative errno.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue-super-recover.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/rescue.c

## Purpose

Defines the `btrfs rescue` command group and command-line frontends for specific offline repair/rescue operations.

## Commands

- `chunk-recover`: validates unmounted device, parses `-y/-v`, calls `btrfs_recover_chunk_tree()`.
- `super-recover`: validates unmounted device, parses `-y/-v`, calls `btrfs_recover_superblocks()`.
- `zero-log`: opens partial writable ctree and clears superblock log root fields.
- `fix-device-size`: opens partial writable ctree and calls `btrfs_fix_device_and_super_size()`.
- `fix-data-checksum`: parses readonly/interactive/mirror modes and calls `btrfs_recover_fix_data_checksum()`.
- `create-control-device`: creates `/dev/btrfs-control` with major/minor `10:234`.
- `clear-uuid-tree`: deletes the UUID tree so the kernel can rebuild it.
- `clear-ino-cache`: removes deprecated inode-cache items.
- `clear-space-cache`: removes v1 or v2 free-space cache.

## Control Flow

Each destructive filesystem operation checks mount status before opening, generally refuses mounted filesystems, and opens the ctree with write flags appropriate to the operation. Several commands also reject running replace/balance through `has_running_replace_or_balance()`.

## Dependencies

Connects command framework macros, help text, open-utils, clear-cache helpers, transaction APIs, and exported rescue backends from `cmds/rescue.h`.

## Risks And Edge Cases

- Return value normalization varies: some functions return `!!ret`, while `super-recover` preserves its documented status codes.
- `clear_uuid_tree()` manually detaches and frees a root after deleting its items and root item; transaction abort/commit handling is explicit but complex.
- `zero-log`, cache clearing, UUID tree clearing, and chunk/super recovery are offline destructive repair operations; correctness relies on mount checks and user confirmation in lower-level backends where applicable.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/rescue.h

## Purpose

Small shared header for rescue command backends.

## API

Defines `enum btrfs_fix_data_checksum_mode`:

- `BTRFS_FIX_DATA_CSUMS_READONLY`
- `BTRFS_FIX_DATA_CSUMS_INTERACTIVE`
- `BTRFS_FIX_DATA_CSUMS_UPDATE_CSUM_ITEM`
- `BTRFS_FIX_DATA_CSUMS_LAST`

Declares:

- `btrfs_recover_superblocks()`
- `btrfs_recover_chunk_tree()`
- `btrfs_recover_fix_data_checksum()`

## Dependencies And Role

Used by `rescue.c`, `rescue-super-recover.c`, `rescue-chunk-recover.c`, and `rescue-fix-data-checksum.c` to share backend entry points without exposing implementation details.

## Risks

No internal logic. ABI risk is limited to changing enum values or function signatures used across rescue translation units.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/rescue.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/restore.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/restore.c

## Purpose

Implements `btrfs restore`, an offline best-effort file recovery command for damaged unmounted filesystems. It opens trees in partial/read-only style, walks directory and extent metadata manually, and copies files, directories, symlinks, metadata, xattrs, snapshots, or matching paths into an output directory.

## Main Features

- Supports zlib, optional LZO, and optional ZSTD decompression.
- Can restore metadata, symlinks, snapshots, and xattrs.
- Can list roots, choose backup super, tree bytenr, fs root bytenr, or root objectid.
- Supports dry-run, overwrite, ignore-errors, regex path filtering, and first-directory discovery.

## Control Flow

1. `cmd_restore()` parses options, refuses mounted filesystems, and opens the filesystem through `open_fs()`.
2. `open_fs()` tries backup superblocks and uses partial/no-block-group/transid-mismatch flags to tolerate damage.
3. For restore mode, `search_dir()` recursively scans `BTRFS_DIR_INDEX_KEY` items from a root directory.
4. Regular files are opened and copied through `copy_file()`.
5. `copy_file()` walks `BTRFS_EXTENT_DATA_KEY` items and dispatches inline extents to `copy_one_inline()` and regular extents to `copy_one_extent()`.
6. Direct extents are read from mirrors via `read_data_from_disk()`, retrying mirrors on read/decompression failure.
7. Directory metadata and xattrs are applied after child traversal.
8. Symlinks are restored through `copy_symlink()` when requested.

## State

Global buffers and flags carry current path/output state and selected restore behavior:

- `fs_name`, `path_name`, `symlink_target`
- `get_snaps`, `restore_metadata`, `restore_symlinks`, `ignore_errors`, `overwrite`, `get_xattrs`, `dry_run`

## Dependencies

Uses btrfs-progs disk/tree/extent/file item APIs, compression libraries, path utilities, xattr/syscall APIs, regex, and shared open/mount checks.

## Risks And Edge Cases

- It intentionally tolerates damaged metadata and manually walks leaves, so output may be partial and errors may be skipped with `-i`.
- `copy_one_inline()` reads inline data into a fixed 4096-byte stack buffer; correctness depends on inline item size staying within that buffer.
- `copy_one_extent()` allocates buffers based on on-disk extent sizes, which can be large or corrupt.
- `overwrite_ok()` takes a `path` parameter but calls `fstatat()` on global `path_name`; current callers pass the same value, but the API is misleading.
- Recursive path construction uses fixed `PATH_MAX` buffers and rejects overflow through `path_cat_out()`/length checks.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/restore.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/scrub.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/scrub.c

## Purpose

Implements the `btrfs scrub` command group: start, resume, cancel, status, and per-device throughput limit management. It wraps kernel scrub ioctls, maintains persistent scrub status files, exposes live progress through a Unix socket, and formats per-device or filesystem-wide reports.

## Commands

- `scrub start`: starts scrub, optionally foreground/background, read-only, raw/per-device output, ioprio, force, and throughput limit.
- `scrub resume`: resumes canceled/interrupted scrub from recorded `last_physical`.
- `scrub cancel`: issues `BTRFS_IOC_SCRUB_CANCEL`.
- `scrub status`: reads live socket or persisted status file and prints progress/history.
- `scrub limit`: shows or writes `devinfo/<devid>/scrub_speed_max` sysfs limits.

## Core Data Structures

- `struct scrub_progress`: per-device ioctl args, fd, status, old/new limits, ioprio, mutex, and resume pointer.
- `struct scrub_file_record`: persisted status for one fsid/devid.
- `struct scrub_progress_cycle`: progress-thread context for periodic ioctl polling, socket service, and status writes.
- `struct scrub_fs_stat`: aggregate filesystem stats for summary output.

## Control Flow

1. `scrub_start()` opens the mount, gets filesystem/device info, reads prior status, checks whether scrub is already running, and prepares per-device progress records.
2. It optionally creates a progress socket and initial status file.
3. In background mode it forks; the child starts per-device scrub threads and one progress thread.
4. `scrub_one_dev()` calls `BTRFS_IOC_SCRUB`; `scrub_progress_cycle()` polls `BTRFS_IOC_SCRUB_PROGRESS`, writes status, and serves socket clients.
5. On completion it restores device limits, joins threads, records final status, prints summaries if requested, and returns special statuses for no resume or uncorrectable errors.

## Status File Format

- Stored under `/var/lib/btrfs/scrub.status.<fsid>`.
- Versioned with `scrub status:1`.
- Parser `scrub_read_file()` is a state machine that reads fsid/devid and key-value progress/stat fields.
- Writer `scrub_write_file()` serializes the same fields through helper macros.

## Dependencies

Uses Btrfs scrub ioctls, fs/device info helpers, sysfs utilities, units formatting, string tables, pthreads, signals, Unix sockets, flocked status files, and UUID utilities.

## Risks And Edge Cases

- The status parser is hand-written and stateful; malformed files are skipped/reported, but parser complexity is high.
- Thread cancellation is asynchronous in the progress thread, requiring careful mutex and file-write cancellation protection.
- Background mode relies on status files and socket cleanup; stale sockets are detected and unlinked when connection is refused.
- `scrub_write_file()` contains a suspicious call sequence around writing the devid: after `scrub_writev()` it calls `scrub_write_buf(fd, buf, ret)`, where `ret` is not clearly the formatted byte count at that point.
- Limit handling writes sysfs values before scrub and attempts to restore old values later; failures are warnings, so limits can remain changed if reset fails.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/send.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/send.c

## Purpose

Implements `btrfs send`, producing a send stream for one or more read-only subvolumes through the kernel `BTRFS_IOC_SEND` ioctl. Handles full sends, incremental sends, clone sources, multi-subvolume stream framing, output files, no-data mode, and protocol version/compressed-data negotiation.

## Main Data Structure

`struct btrfs_send` tracks:

- send pipe fd and output fd
- mount fd
- clone source root IDs
- mount root path
- requested and supported protocol version

## Control Flow

1. `cmd_send()` parses options and output destination.
2. It resolves clone sources and parent subvolumes, ensuring they are read-only.
3. It verifies all target subvolumes are on the same Btrfs mount and read-only.
4. It detects kernel-supported send stream version via sysfs.
5. `--compressed-data` enforces protocol version >= 2 or auto-selects v2 if no protocol was explicitly requested.
6. For each target subvolume, `do_send()` opens it, creates a pipe, starts `read_sent_data()` to splice kernel stream data to output, and calls `BTRFS_IOC_SEND`.
7. Multi-subvolume `-e` mode omits stream headers/end commands as needed.

## Parent/Clone Logic

- `get_root_id()` resolves root id from path.
- `get_parent()` follows parent UUID metadata.
- `find_good_parent()` chooses a clone source matching the real parent lineage and closest creation transaction.
- Parent root id is also added as a clone source for explicit `-p`.

## Dependencies

Uses send-utils for subvolume UUID searches, path mount resolution helpers, sysfs feature probing, pthreads, splice/pipe/fcntl, and Btrfs ioctl definitions.

## Risks And Edge Cases

- `read_sent_data()` calls `exit(-ret)` from the helper thread on splice errors, terminating the whole process rather than returning cleanly.
- Clone source selection depends on UUID metadata and creation transactions; missing/stale metadata produces parent determination failures.
- `--proto 0` requests kernel default/highest behavior through versioned ioctl fields, while local validation only rejects some unsupported combinations.
- Output to a terminal is refused to avoid binary stream corruption.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/send.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/subvolume-list.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/subvolume-list.c

## Purpose

Implements `btrfs subvolume list`, collecting subvolume/snapshot root metadata through tree-search ioctls, resolving paths, applying filters/sorters, and printing default/table/raw/JSON layouts.

## Main Data Structures

- `struct root_info`: one root/subvolume record with root id, refs, generation, creation generation/time, flags, UUIDs, name, path, full path, and deleted marker.
- `struct btrfs_list_filter_set`: dynamic array of predicates.
- `struct btrfs_list_comparer_set`: dynamic array of sort comparers.
- Two rbtrees are used:
  - lookup tree keyed by root id
  - sorted output tree keyed by configured comparers plus root id fallback

## Control Flow

1. `cmd_subvolume_list()` parses field, filter, sort, and layout options.
2. Opens the path and resolves the current top root id.
3. `list_subvol_search()` searches the root tree for `ROOT_ITEM` and `ROOT_BACKREF` items, adding/updating `root_info` records.
4. `lookup_ino_path()` asks the kernel to resolve each root reference directory path.
5. `resolve_root()` walks parent root references to assemble full paths.
6. Deleted or unresolved roots are marked with `DELETED`; top-level gets `TOPLEVEL`.
7. Filters are applied, then records are inserted into the sorted rbtree.
8. Output is printed in default, table, raw, or JSON form.

## Filters And Sorting

Filters include root id, snapshots only, readonly flags, generation comparisons, creation generation comparisons, top-id equality, full-path display adjustment, parent UUID, and deleted-only mode.

Sort keys include root id, generation, creation generation, and path, each optionally ascending or descending.

## Dependencies

Uses Btrfs tree-search and inode-lookup ioctls, rbtrees, UUID formatting/comparison, command formatting helpers, and subvolume command definitions.

## Risks And Edge Cases

- Several allocation failures call `exit(1)` instead of returning errors.
- `filter_by_parent()` stores a UUID pointer through a `u64` data field cast, which is pointer-size dependent and not type-safe.
- Path reconstruction depends on root backrefs and inode lookup; deleted or missing parents become `DELETED`.
- `comp_entry_with_path()` assumes `full_path` is populated before sorting by path; this is satisfied by current `filter_and_sort_subvol()` ordering.
- The top-level subvolume is collected but skipped in normal printing.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/subvolume-list.c -->