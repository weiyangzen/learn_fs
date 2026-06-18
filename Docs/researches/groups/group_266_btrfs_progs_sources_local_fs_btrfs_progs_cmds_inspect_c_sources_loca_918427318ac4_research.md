# Group Research: group_266_btrfs_progs_sources_local_fs_btrfs_progs_cmds_inspect_c_sources_loca_918427318ac4

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/btrfs-progs`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/inspect.c

## Purpose

Implements the `btrfs inspect-internal` command group. This file exposes developer/admin inspection helpers for resolving inode and logical addresses, mapping subvolume IDs, computing minimum device shrink sizes, enumerating chunks, and checking swapfile physical offsets.

## Commands Implemented

- `inode-resolve`: maps an inode number to filesystem paths using `BTRFS_IOC_INO_PATHS`.
- `logical-resolve`: maps a logical address to inode/root/offset triples or resolved paths using `BTRFS_IOC_LOGICAL_INO` / `BTRFS_IOC_LOGICAL_INO_V2`.
- `subvolid-resolve`: resolves a subvolume ID to a path with `btrfs_subvolid_resolve`.
- `rootid`: returns the containing subvolume tree ID for a path via `lookup_path_rootid`.
- `min-dev-size`: estimates the minimum shrinkable size for a device by reading device extents and modeling relocation scratch space.
- `list-chunks`: lists physical/logical chunk mappings and usage, with multi-key sorting and unit formatting.
- `map-swapfile`: verifies a file is suitable as a Btrfs swapfile and maps its first physical block/resume offset.

## Key Helpers and Data Structures

- `__ino_to_path_fd()` wraps inode-to-path ioctl results and prints each returned path.
- `struct dev_extent_elem` stores device extent/hole ranges for minimum device size estimation.
- `adjust_dev_min_size()` accounts for extents beyond the provisional minimum size, usable holes, superblock mirror locations, relocation scratch space, and possible system chunk allocation.
- `struct list_chunks_entry` records one stripe/chunk row: device ID, physical start, logical start, length, flags, usage, and numbering.
- `print_list_chunks()` builds a table with columns for device, physical/logical numbering, type/profile, offsets, length, and usage.
- `read_chunk_tree()`, `find_chunk()`, and `map_physical_start()` support swapfile mapping by reconstructing chunk-to-stripe layout and file extent placement.

## External Interfaces

The file depends heavily on kernel Btrfs ioctls and tree-search helpers:

- `BTRFS_IOC_INO_PATHS`
- `BTRFS_IOC_LOGICAL_INO`
- `BTRFS_IOC_LOGICAL_INO_V2`
- `BTRFS_IOC_TREE_SEARCH`
- `BTRFS_IOC_INO_LOOKUP`
- `FS_IOC_GETFLAGS`

It also uses shared btrfs-progs helpers for mount parsing, subvolume ID resolution, path/root lookup, unit formatting, table output, sorting, and open handling.

## Important Behavior

- `logical-resolve` switches to the v2 ioctl when the buffer exceeds 64 KiB or when `--ignore-offsets` is requested.
- `logical-resolve` attempts to map resolved root IDs back to currently mounted subvolumes; if a referenced subvolume is not mounted, it reports that path resolution cannot continue for that inode.
- `min-dev-size` is intentionally conservative because relocation can require temporary scratch space and may allocate a system chunk.
- `list-chunks` computes logical numbering per device and physical numbering after sorting by device and physical offset.
- `map-swapfile` rejects non-regular files, non-Btrfs files, non-NOCOW files, compressed files, holes, inline extents, encrypted/encoded extents, unsupported block group profiles, and files spanning multiple devices.

## Notes

This file is a read-only inspection and validation surface except for opening files/directories and querying kernel state. It is central to low-level diagnostics and exposes details that normal user-facing commands hide.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/property.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/property.c

## Purpose

Implements the `btrfs property` command group for getting, setting, and listing supported properties on Btrfs objects.

## Commands Implemented

- `property get [-t type] <object> [name]`
- `property set [-f] [-t type] <object> <name> <value>`
- `property list [-t type] <object>`

Supported object types are device, filesystem/root, subvolume, and inode.

## Property Handlers

The `prop_handlers[]` table defines the supported properties:

- `ro`: read-only status of a subvolume.
- `label`: filesystem label for a device or filesystem root.
- `compression`: per-inode compression xattr.

## Key Helpers

- `subvolume_clear_received_uuid()` clears received-subvolume metadata through `BTRFS_IOC_SET_RECEIVED_SUBVOL`.
- `prop_read_only()` reads or changes subvolume read-only state via libbtrfsutil.
- `prop_label()` delegates label get/set to filesystem utility helpers.
- `prop_compression()` gets/sets `btrfs.compression` xattr on a path.
- `autodetect_object_types()` determines applicable object types from stat data, Btrfs fsid checks, block-device checks, subvolume inode number, and root detection.
- `check_is_root()` compares fsids between an object and its parent to decide whether a path is a filesystem root boundary.
- `setget_prop()` validates property existence, object compatibility, ambiguity, and read-only status before dispatching to a handler.
- `parse_args()` centralizes parsing of `-t` and `-f`, object/name/value positions, and type autodetection.

## Important Behavior

- Setting `ro=false` on a received read-only subvolume is blocked if `received_uuid` is set unless `-f` is used.
- With `-f`, `ro=false` also attempts to clear `received_uuid`, because leaving it set can break incremental send semantics.
- Read-write subvolumes with `received_uuid` set produce a warning.
- Missing compression xattrs are treated as an absent property rather than a hard error.
- Object type autodetection can produce multiple compatible types; if the selected property matches more than one, the user must provide `-t`.

## External Interfaces

Uses libbtrfsutil for subvolume read-only and info operations, xattr syscalls for compression, and filesystem label helpers for label get/set.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/property.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/props.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/props.h

## Purpose

Declares the property object model and handler interface used by `property.c`.

## Main Definitions

- `enum prop_object_type`
  - `prop_object_dev`
  - `prop_object_root`
  - `prop_object_subvol`
  - `prop_object_inode`

- `prop_handler_t`
  - Function pointer type for property handlers.
  - Receives object type, object path, property name, optional value, and force flag.

- `struct prop_handler`
  - `name`: property name.
  - `desc`: human-readable description.
  - `read_only`: whether the property can be set.
  - `types`: bitmask of supported object types.
  - `handler`: implementation callback.

## Exported Symbol

- `extern const struct prop_handler prop_handlers[];`

## Role in the Codebase

This header keeps the property dispatch table and object-type bitmask contract shared and explicit. The implementation is in `property.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/props.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/qgroup.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/qgroup.c

## Purpose

Implements the `btrfs qgroup` command group and the reusable `btrfs_qgroup_query()` helper. It manages quota group creation, deletion, relation changes, listing, filtering, sorting, limits, and stale qgroup cleanup.

## Commands Implemented

- `qgroup assign [--rescan|--no-rescan] <src> <dst> <path>`
- `qgroup remove [--rescan|--no-rescan] <src> <dst> <path>`
- `qgroup create <qgroupid> <path>`
- `qgroup destroy <qgroupid> <path>`
- `qgroup show [options] <path>`
- `qgroup limit [-c] [-e] <size>|none [<qgroupid>] <path>`
- `qgroup clear-stale <path>`

## Core Data Structures

- `struct btrfs_qgroup`
  - In-memory representation of a qgroup.
  - Stores qgroup ID, optional path, stale marker, info item, limit item, parent qgroups, and member qgroups.
  - Embedded rb nodes support lookup, sorted output, and parent traversal.

- `struct btrfs_qgroup_list`
  - Bidirectional relationship entry connecting child and parent qgroups.

- `struct qgroup_lookup`
  - Holds qgroup status flags and rb-tree root for qgroup lookup.

- `struct btrfs_qgroup_filter_set`
  - Dynamic list of filters used by `qgroup show`.

- `struct btrfs_qgroup_comparer_set`
  - Dynamic list of comparers used for multi-key sorting.

## Query and Graph Construction

- `__qgroups_search()` walks the quota tree using the tree-search ioctl and consumes:
  - `BTRFS_QGROUP_STATUS_KEY`
  - `BTRFS_QGROUP_INFO_KEY`
  - `BTRFS_QGROUP_LIMIT_KEY`
  - `BTRFS_QGROUP_RELATION_KEY`

- `get_or_add_qgroup()` creates graph nodes and, for level-0 qgroups, attempts to resolve the corresponding subvolume path and stale status through libbtrfsutil.

- `update_qgroup_info()`, `update_qgroup_limit()`, and `update_qgroup_relation()` populate qgroup accounting, limit, and parent/child data.

- `btrfs_qgroup_query()` searches for one qgroup and fills `struct btrfs_qgroup_stats`; this is declared in `qgroup.h`.

## Output Behavior

`qgroup show` supports classic table output and JSON output.

Table columns include:

- qgroup ID
- referenced bytes
- exclusive bytes
- max referenced limit
- max exclusive limit
- parent qgroups
- child qgroups
- path

Sorting supports:

- `qgroupid`
- `path`
- `rfer`
- `excl`
- `max_rfer`
- `max_excl`

Filters support:

- `-f`: qgroups directly impacting the given path.
- `-F`: all qgroups impacting the given path, including ancestral qgroups.

## Important Behavior

- Qgroup status warnings are printed when quotas are disabled, rescan is running, or accounting is inconsistent.
- `check_qgroup_sysfs_inconsistent()` supplements quota-tree status with sysfs because tree-search status can lag until transaction commit.
- `qgroup assign/remove` can schedule quota rescans when the kernel reports accounting became inconsistent.
- `qgroup limit` accepts `none` as an unlimited size and can limit either referenced or exclusive space.
- `qgroup clear-stale` syncs the filesystem, enumerates qgroups, and deletes stale level-0 qgroups whose subvolume root no longer exists.
- In simple quota mode, non-empty stale qgroups can represent required accounting placeholders and are not deleted.

## External Interfaces

Uses Btrfs quota ioctls:

- `BTRFS_IOC_QGROUP_ASSIGN`
- `BTRFS_IOC_QGROUP_CREATE`
- `BTRFS_IOC_QGROUP_LIMIT`
- quota tree search through shared tree-search helpers

Uses libbtrfsutil for subvolume path/info and filesystem sync, and sysfs helpers for inconsistent/mode status.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/qgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/qgroup.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/qgroup.h

## Purpose

Declares qgroup accounting structures and the query helper exported from `qgroup.c`.

## Main Definitions

- `struct btrfs_qgroup_info`
  - `generation`
  - `referenced`
  - `referenced_compressed`
  - `exclusive`
  - `exclusive_compressed`

- `struct btrfs_qgroup_stats`
  - `qgroupid`
  - `info`
  - `limit`

## Exported Function

- `int btrfs_qgroup_query(int fd, u64 qgroupid, struct btrfs_qgroup_stats *stats);`

## Role in the Codebase

Provides a small public interface for consumers that need to query one qgroup’s accounting and limits without using the full `qgroup show` command path.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/qgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/quota.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/quota.c

## Purpose

Implements the `btrfs quota` command group for enabling/disabling quota accounting, rescanning metadata, and reporting quota subsystem status.

## Commands Implemented

- `quota enable [-s|--simple] <path>`
- `quota disable <path>`
- `quota rescan [-s|-w|-W] <path>`
- `quota status [--is-enabled] <path>`

## Key Helpers

- `quota_ctl()` wraps `BTRFS_IOC_QUOTA_CTL`.
- `quota_is_enabled()` checks whether the filesystem has a qgroups sysfs directory.
- `describe_mode()` maps sysfs mode strings to user-facing descriptions.

## Important Behavior

- `quota enable --simple` uses `BTRFS_QUOTA_CTL_ENABLE_SIMPLE_QUOTA`; otherwise full qgroup accounting is enabled.
- `quota rescan -s` only reports current rescan status.
- `quota rescan -w` starts a rescan and waits for completion.
- `quota rescan -W` waits for an already-running rescan without starting one.
- `quota status --is-enabled` returns process status only and prints nothing.
- `quota status` reads sysfs files for mode, inconsistent state, quota override, drop-subtree threshold, and qgroup counts.
- For kernels without `qgroups/mode`, status assumes classic `qgroup` mode.

## External Interfaces

Uses:

- `BTRFS_IOC_QUOTA_CTL`
- `BTRFS_IOC_QUOTA_RESCAN`
- `BTRFS_IOC_QUOTA_RESCAN_STATUS`
- `BTRFS_IOC_QUOTA_RESCAN_WAIT`
- qgroup sysfs files under the filesystem fsid directory
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/receive-dump.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/receive-dump.c

## Purpose

Defines print-only send-stream callbacks used by `btrfs receive --dump`. It decodes send-stream operations into one textual line per operation without applying changes to the filesystem.

## Core Data Flow

The file exports `btrfs_print_send_ops`, a `struct btrfs_send_ops` callback table. Each callback formats one send-stream command.

## Key Helpers

- `PATH_CAT_OR_RET` validates and joins paths.
- `__print_dump()` centralizes output formatting:
  - operation title
  - escaped path
  - optional operation-specific fields
  - special path handling for subvolume/snapshot commands
- `PRINT_DUMP_SUBVOL`, `PRINT_DUMP`, and `PRINT_DUMP_NO_NEWLINE` wrap the print modes.
- `sprintf_timespec()` formats timestamps using local time and `%FT%T%z`.

## Operations Printed

Includes callbacks for:

- subvolume and snapshot creation
- file, directory, fifo, socket, node, and symlink creation
- rename, link, unlink, rmdir
- write and clone operations
- xattr set/remove
- truncate, chmod, chown, utimes
- update_extent
- encoded_write
- fallocate
- fileattr
- enable_verity

## Important Behavior

- Paths and arbitrary xattr data are printed using escaping helpers.
- Clone and rename output expands destination/source paths relative to current subvolume context.
- `enable_verity` prints metadata lengths and algorithm/block size, not the raw salt/signature.
- This file does not parse stream bytes itself; parsing is handled by `common/send-stream` and dispatched through callbacks.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/receive-dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/receive-dump.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/receive-dump.h

## Purpose

Declares the dump-mode receive context and callback table used by `receive.c`.

## Main Definitions

- `struct btrfs_dump_send_args`
  - `full_subvol_path[PATH_MAX]`
  - `root_path[PATH_MAX]`

These fields track path context while formatting stream operations.

## Exported Symbol

- `extern struct btrfs_send_ops btrfs_print_send_ops;`

## Role in the Codebase

Provides the bridge between `receive.c` command parsing and the print-only implementation in `receive-dump.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/receive-dump.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/receive.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/receive.c

## Purpose

Implements `btrfs receive`, including normal send-stream replay and `--dump` mode. It applies Btrfs send-stream operations to a destination filesystem, creates subvolumes/snapshots, writes data, clones extents, restores metadata, and finalizes received subvolumes.

## Main Context

`struct btrfs_receive` stores:

- mount and destination directory fds
- cached write fd/path
- root and destination path state
- current subvolume metadata
- chroot/end-command behavior
- forced decompression flag
- reusable zlib/zstd decompression state

## Command Options

- `-f FILE`: read stream from file instead of stdin.
- `-e`: honor end-command marker.
- `-C, --chroot`: chroot to destination.
- `-E, --max-errors`: maximum stream command errors.
- `-m ROOTMOUNT`: explicit root mount point.
- `--force-decompress`: always decompress encoded writes rather than using encoded I/O.
- `--dump`: print stream operations instead of replaying.
- `-q`, `-v`: quiet/verbose controls.

## Send-Stream Replay Operations

The `send_ops` callback table implements:

- subvolume and snapshot creation
- file, directory, fifo, socket, node, and symlink creation
- rename, hardlink, unlink, rmdir
- write and clone
- xattr set/remove
- truncate, chmod, chown, utimes
- update_extent no-op for no-file-data sends
- encoded_write with direct encoded I/O or decompression fallback
- fallocate
- fileattr no-op placeholder
- fs-verity enable when compiled with fsverity headers

## Key Helpers

- `finish_subvol()` sets received subvolume metadata with `BTRFS_IOC_SET_RECEIVED_SUBVOL` and makes the subvolume read-only.
- `process_subvol()` creates a new received subvolume and records received UUID/transid.
- `search_source_subvol()` finds source subvolumes by received UUID first, then regular UUID.
- `process_snapshot()` resolves parent subvolume, adjusts paths relative to the active root, and creates a snapshot with `BTRFS_IOC_SNAP_CREATE_V2`.
- `open_inode_for_write()` caches the current writable file fd across write-like operations.
- `process_clone()` resolves clone source subvolume/path and uses `BTRFS_IOC_CLONE_RANGE`.
- `process_encoded_write()` tries `BTRFS_IOC_ENCODED_WRITE`, falling back to userspace decompression for selected errors.
- `decompress_zlib()`, `decompress_zstd()`, and `decompress_lzo()` implement decompression backends when compiled in.
- `do_receive()` resolves destination/root mount context, optionally chroots, processes one or more streams, and finalizes subvolumes after each stream.

## Important Behavior

- Received subvolumes are made read-only immediately after stream completion.
- Snapshot parent lookup accepts both received UUID and normal UUID, improving compatibility with incremental streams.
- If receiving under a non-root mounted subvolume, source paths are adjusted so clone/snapshot sources remain reachable from the current mount context.
- Empty streams are rejected.
- `--dump` bypasses filesystem writes and delegates to `btrfs_print_send_ops`.
- `fileattr` is currently ignored because Btrfs inode flags cannot be directly applied as Linux `FS_IOC_SETFLAGS` flags without conversion and special handling.
- fs-verity support is compile-time dependent.

## External Interfaces

Uses Btrfs ioctls:

- `BTRFS_IOC_SET_RECEIVED_SUBVOL`
- `BTRFS_IOC_SUBVOL_GETFLAGS`
- `BTRFS_IOC_SUBVOL_SETFLAGS`
- `BTRFS_IOC_SUBVOL_CREATE`
- `BTRFS_IOC_SNAP_CREATE_V2`
- `BTRFS_IOC_CLONE_RANGE`
- `BTRFS_IOC_ENCODED_WRITE`

Also uses xattr syscalls, filesystem metadata syscalls, zlib/lzo/zstd libraries where enabled, and send-stream parsing from `common/send-stream`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/receive.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/reflink.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/reflink.c

## Purpose

Defines the `btrfs reflink` command group and a `reflink clone` subcommand intended for lightweight COW file copies/range cloning.

## Command Implemented

- `reflink clone [options] source target`

Documented options:

- `-s RANGESPEC`: range spec from source/same file semantics.
- `-t RANGESPEC`: range from target file, according to usage text.

Actual getopt string accepts `-r` and `-s`, not `-t`.

## Data Structures

- `struct reflink_range`
  - `from`
  - `length`
  - `to`
  - `same_file`
  - list node

## Key Helpers

- `parse_reflink_range()` parses `SRCOFF:LENGTH:DESTOFF`, accepting size suffixes through `arg_strtou64_with_suffix`.
- `reflink_apply_range()` is a stub returning `-EOPNOTSUPP`.

## Important Behavior and Status

This file appears incomplete:

- `reflink_apply_range()` does not perform cloning.
- `cmd_reflink_clone()` opens the source file but never opens the target file before checking `fd_target == -1`, so it always fails at target open validation.
- Usage text mentions `-t`, while getopt accepts `-r`.
- Range allocation and list cleanup are present, but successful reflink behavior is not implemented.

## Role in the Codebase

This is a command scaffold rather than a functional reflink implementation in the read version.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/replace.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/replace.c

## Purpose

Implements the `btrfs replace` command group for live device replacement: starting a replace operation, monitoring status, and canceling an active operation.

## Commands Implemented

- `replace start [-BfrK] [--enqueue] <srcdev>|<devid> <targetdev> <mount_point>`
- `replace status [-1] <mount_point>`
- `replace cancel <mount_point>`

## Key Helpers

- `replace_dev_result2string()` maps kernel replace result codes to user-readable strings.
- `dev_replace_sigint_handler()` cancels an active replace on SIGINT.
- `dev_replace_handle_sigint()` installs or restores SIGINT handling.
- `print_replace_status()` polls `BTRFS_IOCTL_DEV_REPLACE_CMD_STATUS` and prints progress or final state.
- `time2string()` formats kernel timestamps.
- `progress2string()` formats progress in tenths of a percent.

## Replace Start Flow

`cmd_replace_start()`:

1. Parses options:
   - `-B`: do not background.
   - `-r`: avoid reading from source if another good mirror exists.
   - `-f`: force target device use.
   - `--enqueue`: wait for another exclusive operation.
   - `-K, --nodiscard`: skip whole-device trim.
2. Opens the mounted filesystem.
3. Reads filesystem feature flags and detects zoned mode.
4. Checks exclusive-operation state.
5. Queries current replace status and rejects already-started replace.
6. Resolves source as either devid or block-device path.
7. Validates target device with mkfs safety checks.
8. Verifies target size is at least source size.
9. Opens and prepares the target device, with optional discard and zoned preparation.
10. Installs SIGINT cancel handler.
11. Backgrounds unless `-B` is set.
12. Starts replace through `BTRFS_IOC_DEV_REPLACE`.

## Status Behavior

`replace status` prints:

- running progress
- finished/canceled/suspended times
- write error count
- uncorrectable read error count

Without `-1`, it refreshes once per second until the operation reaches a terminal state.

## Cancel Behavior

`replace cancel` sends `BTRFS_IOCTL_DEV_REPLACE_CMD_CANCEL`. If no replace was started, it prints informational output and returns status `2`.

## External Interfaces

Uses:

- `BTRFS_IOC_GET_FEATURES`
- `BTRFS_IOC_DEV_REPLACE`
- filesystem exclusive-operation checks
- device size/probing/preparation helpers from common device and mkfs code

## Important Behavior

- Source may be specified as a device ID when the original source device is missing.
- Mounted target devices are protected by `test_dev_for_mkfs`.
- RAID5/6 unsupported-kernel cases are surfaced with a specific warning on `EOPNOTSUPP`.
- The start command may daemonize before issuing the start ioctl unless `-B` is used.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/replace.c -->