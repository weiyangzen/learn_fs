# Group Research: group_265_btrfs_progs_sources_local_fs_btrfs_progs_check_qgroup_verify_c_sourc_b5203d1e094b

Scope: `Docs/research_subset_a.md`; source tree: `sources/local-fs/btrfs-progs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/qgroup-verify.c -->
# File Research: sources/local-fs/btrfs-progs/check/qgroup-verify.c

## Purpose
Implements quota-group verification, reporting, extent-root ownership tracing, and qgroup repair for `btrfs check`. It reconstructs expected qgroup referenced/exclusive counts from extent references and compares them with quota-tree `BTRFS_QGROUP_INFO_KEY` records.

## Main Data Model
- `struct qgroup_count` stores one qgroup id, whether its subvolume exists, on-disk counts, recomputed counts, parent/child qgroup relation lists, and a `bad_list` entry for repair.
- `counts` is a global rb-tree of `qgroup_count` records plus qgroup status flags: rescan, inconsistency, simple-quota mode, enable generation, and scan progress.
- `struct ref` stores one extent reference keyed by `(bytenr, parent, root)` in `by_bytenr`; full refs use `root`, shared refs use `parent`.
- `tree_blocks` is a ulist of interior tree blocks that need implied reference expansion for classic qgroups.

## Control Flow
- `qgroup_verify_all()` is the main verifier. It loads quota-tree qgroups and relations, scans all block groups' extent items, accounts extents, records bad qgroups, and returns `0`, positive inconsistency, or negative fatal error.
- `load_quota_info()` does two quota-tree passes: first reads status and qgroup info items, then reads relation items and links child qgroups to parent qgroups.
- `scan_extents()` walks extent-tree leaves over each block group range. It records inline refs, keyed refs, metadata item sizes, and interior tree blocks.
- Classic qgroups use `map_implied_refs()` and `account_all_refs()`: shared refs are recursively resolved to filesystem roots, then `account_one_extent()` propagates usage through qgroup parent relations.
- Simple quota mode bypasses classic backref resolution in `simple_quota_account_extent()` and accounts eligible extents directly to their owner root if the extent generation is not older than qgroup enable generation.

## Repair and Reporting
- `report_qgroups()` prints per-qgroup recomputed versus on-disk referenced/exclusive differences, with special messaging when rescan or inconsistency status makes differences expected.
- `repair_qgroups()` updates qgroup info items for all entries queued on `bad_qgroups`, then repairs the qgroup status item last so it gets the newest transaction id.
- `repair_qgroup_info()` writes recomputed referenced/exclusive and compressed counts into the quota tree.
- `repair_qgroup_status()` clears rescan/inconsistent state and preserves simple-quota status when applicable.

## Notable Behavior and Edge Cases
- Full refs are sorted before shared refs for a bytenr, which supports root resolution by walking a bytenr group from the leftmost node.
- Tree reloc self-reference loops are special-cased as `BTRFS_TREE_RELOC_OBJECTID` and skipped for qgroup contribution.
- `qgroup_seq` avoids clearing every qgroup refcount between extent-accounting rounds.
- `print_extent_state()` is a diagnostic path that prints extents and all roots referencing a chosen subvolume without updating qgroup counters.
- Global qgroup/ref state is intentionally retained until reporting, but `free_tree_blocks()` and `free_ref_tree()` clean transient scan state after each verification/debug pass.

## Dependencies
Uses btrfs core accessors, disk IO, transactions, ulist, extent IO, tree checker, rb-tree helpers, `check/repair.h`, and the public declarations in `check/qgroup-verify.h`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/qgroup-verify.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/qgroup-verify.h -->
# File Research: sources/local-fs/btrfs-progs/check/qgroup-verify.h

## Purpose
Declares the qgroup verification API used by the btrfs check code.

## API
- `qgroup_verify_all(struct btrfs_fs_info *info)` verifies all quota-group accounting for a filesystem.
- `report_qgroups(int all)` prints qgroup accounting differences after verification.
- `repair_qgroups(struct btrfs_fs_info *info, int *repaired, bool silent)` writes repaired qgroup info/status items.
- `print_extent_state(struct btrfs_fs_info *info, u64 subvol)` prints extent ownership state for one subvolume.
- `free_qgroup_counts()` frees retained qgroup count records.
- `qgroup_set_item_count_ptr(u64 *item_count_ptr)` installs an optional progress/item counter.

## Dependencies
Includes `kerncompat.h`, `stdbool.h`, and forward-declares `struct btrfs_fs_info`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/qgroup-verify.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/repair.c -->
# File Research: sources/local-fs/btrfs-progs/check/repair.c

## Purpose
Provides shared repair helpers for `btrfs check`, including unsafe key updates, corrupt extent-root block tracking, used-block reconstruction, block accounting fixup, orphan device-extent removal, and tree-checker repair integration.

## Main Functions
- `btrfs_fixup_low_keys()` updates ancestor node separator keys after modifying a low-level key, stopping once the changed slot is not zero.
- `btrfs_set_item_key_unsafe()` rewrites a leaf item key and fixes low keys upward; it is explicitly intended for fsck repair paths.
- `btrfs_add_corrupt_extent_record()` records corrupt extent-tree blocks in `fs_info->corrupt_blocks` using a cache extent keyed by start/length plus first key and level.
- `btrfs_mark_used_tree_blocks()` traverses chunk, root, and block-group trees to mark tree blocks as used or pin them.
- `btrfs_mark_used_blocks()` populates an extent_io_tree from extent roots and the remap tree.
- `btrfs_fix_block_accounting()` rebuilds block-group `used` and `space_info->bytes_used` from actual used extents, updates dirty block groups, and rewrites super `bytes_used`.
- `btrfs_remove_dev_extent()` deletes one dev-extent item, subtracts its length from the device's bytes-used counter, updates the device item, and commits.
- `btrfs_check_block_for_repair()` runs leaf/node tree checker logic and records corrupt extent-tree blocks for repair handling.

## Traversal Details
`traverse_tree_blocks()` recursively walks tree nodes. For level-1 non-root nodes, it can mark children directly without reading leaves, while root tree traversal follows root items into other tree roots. Already marked ranges are skipped to avoid loops on damaged filesystems.

## Error Handling
Errors are returned as negative errno-style values for internal helpers and nonzero repair failures. Transaction paths abort on mutation failures and commit on success. Device extent removal reports missing devices, search failure, deletion failure, underflow-like `bytes_used` cases, and commit errors.

## Dependencies
Uses ctree accessors, transactions, extent IO trees, disk IO, volumes, extent cache, messages, and tree checker internals.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/repair.h -->
# File Research: sources/local-fs/btrfs-progs/check/repair.h

## Purpose
Declares repair-mode globals, corrupt-block records, and repair helper functions used by btrfs check.

## Exposed Types and Globals
- `extern int opt_check_repair` indicates repair mode.
- `struct btrfs_corrupt_block` combines a `cache_extent`, first key, and level for corrupt tree-block tracking.

## API
Declares corrupt extent recording, block accounting rebuild, tree/used block marking, orphan dev-extent removal, block checking for repair, unsafe item-key update, and low-key fixup.

## Dependencies
Includes `tree-checker.h`, `btrfs_tree.h`, and `common/extent-cache.h`, with forward declarations for btrfs transaction, fs info, paths, roots, extent IO trees, and extent buffers.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/repair.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/balance.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/balance.c

## Purpose
Implements the `btrfs balance` command group: start, pause, cancel, resume, status, and hidden legacy full-balance behavior.

## Parsing and Validation
- `parse_one_filter()` handles balance filters: `profiles`, `usage`, `devid`, `drange`, `vrange`, `convert`, `soft`, `limit`, and `stripes`.
- `parse_filters()` splits comma-separated filter strings for data/system/metadata scopes.
- Duplicate filters produce warnings; invalid profiles, ranges, usage percentages, missing arguments, and unsupported filter combinations fail early.
- `drange` requires `devid`, and `soft` requires a matching `convert`.

## Balance Execution
- `cmd_balance_start()` builds `struct btrfs_ioctl_balance_args`, applies type flags, mirrors metadata filters to system chunks unless system is explicitly forced, and invokes `do_balance()`.
- `do_balance()` opens the mount directory, checks exclusive-operation state, calls `BTRFS_IOC_BALANCE_V2`, and falls back to old `BTRFS_IOC_BALANCE` only if no filters require v2.
- Background mode double-forks, detaches, redirects stdio to `/dev/null`, and then runs the balance.

## Safety Behavior
- Full unfiltered balance warns and delays unless `--full-balance` is used.
- Conversion with missing devices warns because new chunks could target failed devices.
- RAID5/6 conversion warns and delays unless `--force` is used.
- Explicit system-chunk balancing is refused unless forced.

## Other Commands
- `pause` and `cancel` call `BTRFS_IOC_BALANCE_CTL`.
- `resume` calls `BTRFS_IOC_BALANCE_V2` with `BTRFS_BALANCE_RESUME`.
- `status` calls `BTRFS_IOC_BALANCE_PROGRESS`, prints running/paused state and progress, and optionally dumps ioctl arguments.

## Registration
Defines the `balance` command group with start, pause, cancel, resume, status, and hidden `--full-balance`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/balance.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/commands.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/commands.h

## Purpose
Defines the internal command registration ABI for btrfs-progs CLI command handlers.

## Core Types
- `struct cmd_struct` stores token, callback, usage string array, optional subgroup, and flags.
- `struct cmd_group` stores group usage, group info text, and a null-terminated array of command pointers.

## Flags
Command flags include hidden commands, aliases, text/json output support, and global dry-run support. `CMD_FORMAT_MASK` covers output format flags.

## Macros
- `DEFINE_COMMAND()` creates a `cmd_struct_<name>` with explicit fields.
- `DEFINE_SIMPLE_COMMAND()` follows the `cmd_<name>` and `cmd_<name>_usage` naming convention.
- `DEFINE_COMMAND_WITH_FLAGS()` adds command-specific flags such as JSON support.
- `DEFINE_GROUP_COMMAND()` and `DEFINE_GROUP_COMMAND_TOKEN()` register command groups handled by `handle_command_group()`.

## Declared Commands
Declares top-level and inspect/filesystem helper commands, including `filesystem`, `filesystem_du`, `filesystem_usage`, `balance`, `device`, `inspect_dump_super`, `inspect_dump_tree`, and `inspect_tree_stats`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/commands.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/device.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/device.c

## Purpose
Implements `btrfs device` subcommands for adding/removing devices, scanning/forgetting devices, readiness checks, IO stats, per-device usage, and the replace alias.

## Device Mutation Commands
- `cmd_device_add()` validates target devices, checks exclusive-operation state, rejects host-managed zoned devices for non-zoned filesystems, prepares devices with optional discard, canonicalizes paths, and calls `BTRFS_IOC_ADD_DEV`.
- `_cmd_device_remove()` backs both `remove` and `delete`; it supports device paths, numeric devids, `missing`, and `cancel`, uses `BTRFS_IOC_RM_DEV_V2`, and falls back to legacy `BTRFS_IOC_RM_DEV` only when compatible.
- Multiple removals warn and delay unless `--force` is used.

## Scan and Ready
- `btrfs_forget_devices()` calls `/dev/btrfs-control` with `BTRFS_IOC_FORGET_DEV`.
- `cmd_device_scan()` scans all devices, specified block devices, or forgets stale/specified devices.
- `cmd_device_ready()` canonicalizes a block device and calls `BTRFS_IOC_DEVICES_READY` through `/dev/btrfs-control`.

## Device Stats
- `cmd_device_stats()` supports mounted ioctl reads and `--offline` reads from the dev tree.
- Online mode opens the mount and calls `BTRFS_IOC_GET_DEV_STATS`, optionally with reset.
- Offline mode opens ctree state and uses `get_device_stats_offline()` to read `BTRFS_DEV_STATS_OBJECTID` persistent items.
- Output supports plain text, JSON, and tabular `-T`; `--check` returns bit `64` if any counter is nonzero.

## Device Usage
- `_cmd_device_usage()` loads chunk/device info via `load_chunk_and_device_info()` and prints per-device sizes plus chunk allocation details using helpers from `filesystem-usage.c`.

## Registration
Registers add, delete alias, remove, replace alias, scan, ready, stats, and usage under the `device` group.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/device.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem-du.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/filesystem-du.c

## Purpose
Implements `btrfs filesystem du`, a recursive FIEMAP-based disk usage summarizer that reports total, exclusive, and set-shared bytes.

## Data Structures
- `struct shared_extent` is an interval-tree node for physical shared extents.
- `seen_inodes` is an rb-tree of `(inode, subvol)` pairs to avoid double-counting hardlinks.
- `struct du_dir_ctxt` stores aggregate directory totals, directory stream, and a top-level shared-extent tree.

## Accounting Flow
- `du_calc_file_space()` issues repeated `FS_IOC_FIEMAP` calls, skips unknown/delalloc/inline extents, sums total bytes, and records `FIEMAP_EXTENT_SHARED` ranges.
- `du_add_file()` stats and opens a path, resolves the root id for hardlink tracking, recurses into directories, and prints one row unless summary mode suppresses non-top-level rows.
- `du_walk_dir()` iterates regular files and directories under a directory fd and accumulates totals.
- For top-level directories, `count_shared_bytes()` merges overlapping shared physical intervals so shared bytes are counted once per argument set.

## CLI Behavior
Supports `-s/--summarize` and unit options. It warns on very old kernels where `FIEMAP_EXTENT_SHARED` is unavailable. Hardlink detection is reset for each command-line argument.

## Notable Edge Cases
Inline extents are skipped because they do not consume separate data space. Unknown and delalloc extents are skipped because final allocation is not known. Empty subvolume directory inode `2` is treated specially because it has no related tree.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem-du.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem-usage.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/filesystem-usage.c

## Purpose
Implements `btrfs filesystem usage` and shared chunk/device accounting helpers used by `btrfs device usage`.

## Chunk and Space Loading
- `load_chunk_info()` uses tree-search ioctl on the chunk tree and groups chunks by `(type, devid, num_stripes)` through `add_info_to_list()`.
- `load_space_info()` calls `BTRFS_IOC_SPACE_INFO` twice: first to get count, then to fetch and sort all space entries.
- `load_device_info()` calls `BTRFS_IOC_FS_INFO` and `device_get_info()` over device ids, skips seed devices when detectable, and records device size, filesystem-occupied size, and path/missing state.
- `load_chunk_and_device_info()` combines chunk and device loading and degrades with warnings on permission-limited chunk or FS info access.

## Accounting Logic
- `calc_chunk_size()` converts grouped chunk size to per-device allocation size, handling parity/sub-stripes and special RAID1/DUP cases.
- `get_raid56_space_info()` estimates raw chunk and used bytes for RAID5/6 using logical usage ratios and parity counts.
- `print_filesystem_usage_overall()` computes raw total size, allocated, used, unallocated, missing, slack, estimated free, minimum free, data/metadata ratios, global reserve, multiple profiles, and zoned unusable/zone size values.

## Output Modes
- Linear output prints each block-group type/profile with size, used percentage, per-device allocations, and unallocated device space.
- Tabular output builds a matrix of devices versus space-info columns, plus unallocated, total, slack, total, and used rows.
- `print_device_chunks()` and `print_device_sizes()` expose per-device output for `device usage`.

## Notable Edge Cases
RAID56 free/unallocated estimates are marked unreliable if chunk info is unavailable. Seed devices are filtered by fsid comparison through sysfs or direct superblock reads. Missing devices have zero `device_size`, contributing to missing totals.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem-usage.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem-usage.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/filesystem-usage.h

## Purpose
Declares the shared device/chunk usage data model and helper API for filesystem and device usage commands.

## Types
- `struct device_info` stores devid, path, block-device size, and filesystem-occupied size.
- `struct chunk_info` stores grouped chunk type, size, devid, and number of stripes. Grouping is by `(type, devid, num_stripes)`.

## API
- `load_chunk_and_device_info()` populates arrays of `chunk_info` and `device_info`.
- `print_device_chunks()` and `print_device_sizes()` print device-level allocation details.
- `dev_to_fsid()` reads a device superblock and extracts fsid.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem-usage.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/filesystem.c

## Purpose
Implements the `btrfs filesystem` command group: `df`, `show`, `sync`, `defragment`, legacy `balance` alias, `resize`, `label`, `mkswapfile`, `commit-stats`, plus group registration for `du` and `usage`.

## Filesystem Space Display
- `cmd_filesystem_df()` opens a mount, calls `get_df()`, and prints text or JSON. Text mode also reads sysfs allocation files per block-group type.
- `print_df_text()` and `print_df_json()` include zone-unusable data when available.

## Filesystem Discovery
- `cmd_filesystem_show()` searches mounted filesystems, blkid-scanned devices, direct regular-file images, UUIDs, labels, devices, or mountpoints.
- Mounted scan uses `/proc/self/mounts`, `get_fs_info()`, `get_label_*()`, and `get_df()`.
- Unmounted scan copies the global scanned fs-device list, builds seed/sprout mappings by opening ctrees partially, and prints deduplicated fsids.
- `seen_fsid_hash` prevents duplicate output for filesystems mounted multiple times.

## Sync and Label
- `cmd_filesystem_sync()` delegates to `btrfs_util_fs_sync()`.
- `cmd_filesystem_label()` gets or sets labels through common label helpers.

## Defragment
- `cmd_filesystem_defrag()` parses recursive mode, compression type/level, no-compress, flush, byte range, target extent size, and step size.
- Defrag uses `BTRFS_IOC_DEFRAG_RANGE`; optional step mode repeatedly submits smaller ranges and starts IO after each step.
- Recursive directory defrag uses `nftw()` and skips crossing mounts/physical symlinks.
- The code warns when directories are passed without recursive mode because kernel directory defrag does not walk files.

## Resize
- `parse_resize_args()` handles `cancel`, optional `devid:`, `max`, absolute sizes, and +/- size deltas.
- Mounted resize validates device ids and new size, checks exclusive-operation state unless canceling, then calls `BTRFS_IOC_RESIZE`.
- `offline_resize()` supports unmounted single-device growth/max resize through direct ctree write, device item update, super total update, and regular-file truncation when applicable. Offline shrinking and multi-device filesystems are rejected.

## Swapfile and Commit Stats
- `cmd_filesystem_mkswapfile()` creates a new 0600 file, sets NOCOW, fallocates aligned size, and writes a v2 swap signature with UUID.
- `cmd_filesystem_commit_stats()` reads `commit_stats` from sysfs, maps known keys to user-facing labels, prints UUID when available, and can reset max commit duration with `-z/--reset`.

## Registration
The command group includes `df`, `du`, `show`, `commit-stats`, `sync`, `defragment`, hidden `balance` alias, `resize`, `label`, `usage`, and `mkswapfile`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/filesystem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect-dump-super.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/inspect-dump-super.c

## Purpose
Implements `btrfs inspect-internal dump-super`, which reads and prints one or more superblock copies from devices or filesystem image files.

## Core Logic
- `load_and_dump_sb()` stats the input, avoids reading beyond the end for block/regular files, reads the superblock at a requested bytenr, validates magic unless forced, and delegates formatting to `btrfs_print_superblock()`.
- `cmd_inspect_dump_super()` parses `--full`, `--all`, `--super`, `--force`, and `--bytenr`, plus deprecated `-i` and legacy `-s <bytenr>` behavior.

## CLI Behavior
`--all` iterates all standard superblock mirror offsets. A specific `--super` mirror or `--bytenr` clears all-mode. Multiple devices are processed sequentially.

## Error Handling
Reports open/stat/read failures, short reads, bad magic without force, and invalid mirror indexes. Short devices that have no later superblock copy can silently skip that copy.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect-dump-super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect-dump-tree.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/inspect-dump-tree.c

## Purpose
Implements `btrfs inspect-internal dump-tree`, a textual tree dumper for devices/images with options to dump selected trees, extents, roots, UUID tree, backup roots, or explicit tree blocks.

## Opening Strategy
The command opens ctree state with partial mode, no block groups, and skipped leaf item checks. This intentionally favors diagnostic visibility on damaged filesystems over strict validation.

## Explicit Block Dumping
- `dump_add_tree_block()` records each requested `--block` bytenr in a cache tree and rejects duplicates.
- `dump_print_tree_blocks()` checks sector alignment and verifies the logical address belongs to metadata before reading and printing each block.
- `--follow` can recursively print children of requested blocks.

## Tree Dumping Flow
- Without explicit blocks, it prints root/chunk/log root summaries or full trees depending on filters.
- It handles special roots not necessarily found through ordinary root items, such as root, chunk, log, and block-group trees.
- It scans root items from the tree root and log root tree, names known root object ids, applies filters for extent/device/uuid/tree-id modes, and prints either short root lines or full `btrfs_print_tree()` output.
- `--extents` uses `print_extents()` to recursively descend tree nodes and print leaves containing extent information.
- `--backups` prints superblock backup root slots via `print_old_roots()`.

## Options
Supports extent-only, device-only, roots-only, backup roots, UUID-only, one or more blocks, one tree id/name, device scan disabling, BFS/DFS traversal, hiding names, and checksum display modes.

## Notable Edge Cases
Child level mismatches in `print_extents()` are treated as corruption warnings and stop that branch. Explicit block mode requires only chunk-root availability and does not need full root setup.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect-dump-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect-tree-stats.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/inspect-tree-stats.c

## Purpose
Implements `btrfs inspect-internal tree-stats`, which computes size, layout, seek, clustering, inline data, fanout, and read-time statistics for selected Btrfs trees.

## Data Structures
- `struct root_stats` accumulates total nodes/bytes, inline bytes, seek counts and lengths, cluster counts/sizes, bytenr spread, per-level node counts, and an rb-tree histogram of seek distances.
- `struct seek` stores one seek distance bucket and count.

## Traversal
- `calc_root_size()` reads a root by key, initializes stats from the root node, times traversal, prints stats, and frees the seek histogram.
- `walk_nodes()` recursively reads child blocks, counts nodes per level, tracks physical distance between adjacent child blocks, classifies forward/backward seeks, and groups contiguous node clusters.
- `walk_leaf()` counts leaf nodes/bytes and optionally sums inline file-extent payload sizes.

## Output
Prints raw or human-readable totals for tree size, inline data, seeks, average/max seek length, optional histogram, clusters, disk spread, read time, levels, node counts, and average fanout per non-leaf level.

## CLI Behavior
Supports unit options, `-b` for raw bytes, `-t TREEID` for one tree, and `-v` which increments a file-local verbosity counter but is not otherwise used. Without `-t`, it reports root, extent, checksum, and fs trees.

## Safety Note
Warns when the target is mounted because this command accesses block devices directly and can produce inaccurate results or errors if the filesystem changes during traversal.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/inspect-tree-stats.c -->