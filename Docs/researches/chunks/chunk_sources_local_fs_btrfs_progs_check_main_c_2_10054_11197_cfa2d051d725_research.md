# Chunk Research: sources/local-fs/btrfs-progs/check/main.c lines 10054-11197

## Scope

This report covers `sources/local-fs/btrfs-progs/check/main.c` lines 10054-11197 for subset A (`Docs/research_subset_a.md`). The chunk starts in `load_log_root()` after adjacent setup at line 10045 and then covers log-tree checking, root-item repair support, critical-root validation, the `btrfs check` usage text, the full `cmd_check()` command dispatcher, final cleanup/reporting, and `DEFINE_SIMPLE_COMMAND(check, "check")`. It does not create or update the merged per-file report.

## Public And Internal APIs Covered

- `load_log_root()` finishes loading a per-subvolume log root from a root item in the log root tree by reading the root item, constructing a `btrfs_tree_parent_check`, reading the tree block, and validating the loaded node level against the root item level.
- `check_log()` walks `gfs_info->log_root_tree` for `BTRFS_TREE_LOG_OBJECTID` root items whose offsets are filesystem root objectids, loads each temporary log root, and passes it to `check_log_root()` from the preceding chunk.
- `free_roots_info_cache()`, `build_roots_info_cache()`, `maybe_repair_root_item()`, and `repair_root_items()` implement the early root-item sanity/repair pass that detects historical stale root item bytenr/generation/level values by comparing root-tree root items against extent-tree tree-block references.
- `check_global_roots_uptodate()` verifies all global roots are readable and that each global-root generation has extent, checksum, and, when enabled, free-space-tree roots.
- `check_early_critical_roots()` validates that the tree, device, and chunk roots are uptodate before any checker stage relies on them.
- `cmd_check_usage[]` defines user-facing `btrfs check` options for superblock/root selection, operation modes, repair, checksum verification, quota report, subvolume extent reporting, progress, and deprecated space-cache clearing.
- `cmd_check()` is the command entry point: it parses CLI options, opens the filesystem, gates dangerous modes, coordinates optional one-shot operations, runs the eight main checker stages, performs deferred repair cleanups, prints summary counters, and tears down state.
- `DEFINE_SIMPLE_COMMAND(check, "check")` registers this command with the btrfs-progs command framework.

## Control Flow And Behavior

- Log checking starts by searching the log root tree for key `{ TREE_LOG_OBJECTID, ROOT_ITEM_KEY, 0 }`. It advances leaf-by-leaf until keys move past the log-root item range. For each fs-root log item it zeroes a stack `struct btrfs_root`, calls `load_log_root()`, checks the loaded root through `check_log_root()`, and frees `tmp_root.node`.
- `load_log_root()` assumes the caller's path points at the log root item. It copies the on-disk root item into `tmp_root->root_item`, sets `tmp_root->root_key`, reads the root node using owner/transid/level parent checks, and returns `-EIO` if the actual tree-block header level disagrees with the root item.
- `build_roots_info_cache()` scans the extent tree from the first extent item, increments the shared progress item counter, filters to tree-block extent or metadata items, derives the block level, and accepts only first inline refs of type `BTRFS_TREE_BLOCK_REF_KEY`. It records, per root id, the highest-level candidate root node by bytenr/generation and counts how many nodes exist at that level.
- `maybe_repair_root_item()` looks up the root id in `roots_info_cache`, rejects missing extent evidence or ambiguous top-level nodes, reads the current root item, and compares bytenr, level, and generation. In read-only checking it reports mismatch and returns `1`; in repair mode it can rewrite those fields in the leaf. It refuses to downgrade from a newer root-item generation to an older found root node.
- `repair_root_items()` first skips filesystems with `EXTENT_TREE_V2`, then builds the extent-derived root cache and scans `gfs_info->tree_root` for root items beginning at `BTRFS_FIRST_FREE_OBJECTID`. It uses a two-pass-per-leaf strategy: first scan read-only to decide whether a transaction is needed, then restart at the bad key with a transaction only for leaves that need writes. Each transaction is committed before moving to the next leaf/key range.
- Command parsing mutates global checker state: `--repair`, `--init-csum-tree`, and `--init-extent-tree` enable repair writes; `--check-data-csum` enables data checksum verification; `--mode` switches original vs lowmem checking; `--progress` initializes task reporting; `--force` bypasses mount-status blocking and drops exclusive open.
- Before opening the filesystem, `cmd_check()` checks argument count, handles the `--readonly` plus repair incompatibility, and imposes a 10-second repair warning delay unless `--force` is present. It then checks mount status, sets `OPEN_CTREE_PARTIAL` for repair, and opens `gfs_info` via `open_ctree_fs_info()`.
- After opening, repair mode refuses to proceed while device replace or balance is running. The command prints the filesystem UUID, validates critical roots, handles deprecated `--clear-space-cache`, optionally clears the tree log after user confirmation, and handles early-exit report modes (`--qgroup-report` and `--subvol-extents`).
- `--init-extent-tree` and `--init-csum-tree` run inside a transaction before normal checking. Extent-tree rebuild marks `gfs_info->rebuilding_extent_tree`; checksum-tree rebuild reinitializes checksum global roots and refills checksums, optionally after extent-tree rebuild, then commits before proceeding.
- The normal checker sequence is ordered as log, root items, extents/chunks, free-space tree/cache, fs roots, checksums, root refs, and qgroups. Progress mode wraps each stage with `task_start()` / `task_stop()` using `g_task_ctx.tp`; non-progress mode prints `[1/8]` through `[8/8]` messages.
- Some errors are fatal to later stages and branch to `out` or `close_out`, while others accumulate in `err` and continue. Fs-root and root-ref failures stop later structural checks; checksum errors are reported but intentionally non-fatal so the checker can continue.
- After root/ref/csum checks, repair mode processes `gfs_info->recow_ebs` through `recow_extent_buffer()` to fix transid errors, then drains `delete_items`, deleting bad items only in repair mode and freeing all queued records. Quota verification and possible qgroup repair run last when quotas are enabled.
- The final `out` block prints aggregate space/accounting counters, frees qgroup counts and root records, closes the ctree, deinitializes progress state, and returns the boolean-ish accumulated `err`.

## State And Data Structures

- `gfs_info` is the central filesystem handle. This chunk reads and mutates `tree_root`, `dev_root`, `chunk_root`, `fs_root`, `log_root_tree`, `global_roots_tree`, `nr_global_roots`, `super_copy`, `quota_enabled`, `recow_ebs`, and `rebuilding_extent_tree`.
- `roots_info_cache` is a process-global `struct cache_tree *` keyed by root id. Entries are `struct root_item_info` from `check/mode-original.h`, containing root level, number of highest-level nodes, root bytenr, generation, and embedded `cache_extent`.
- `root_cache` is a stack `struct cache_tree` passed across log, fs-root, and root-ref checks, then freed with `free_root_recs_tree()`.
- Command-local mode state includes selected superblock bytenr, selected tree/chunk root bytenrs, subvolume id for `--subvol-extents`, booleans for readonly, qgroup report, force, and init-csum-tree, plus `clear_space_cache` and qgroup repair counters.
- Process-wide checker flags and counters used here include `opt_check_repair`, `init_extent_tree`, `check_data_csum`, `check_mode`, `is_free_space_tree`, `no_holes`, `found_free_ino_cache`, `delete_items`, and the summary counters `bytes_used`, `total_csum_bytes`, `total_btree_bytes`, `total_fs_tree_bytes`, `total_extent_tree_bytes`, `btree_space_waste`, `data_bytes_allocated`, and `data_bytes_referenced`.
- `g_task_ctx` bridges progress reporting and item-count accounting. This chunk initializes it for progress mode and passes its `item_count` pointer to qgroup verification so qgroup scanning contributes to shared progress.

## Dependencies

- Btrfs-progs core tree APIs: `btrfs_search_slot()`, `btrfs_next_leaf()`, `find_next_key()`, `btrfs_release_path()`, `read_tree_block()`, extent-buffer read/write helpers, root/item/key accessors, feature-flag accessors, and global-root rb-tree traversal.
- Transaction and repair APIs: `btrfs_start_transaction()`, `btrfs_commit_transaction()`, `reinit_extent_tree()`, `reinit_global_roots()`, `fill_csum_tree()`, `zero_log_tree()`, `recow_extent_buffer()`, `delete_bad_item()`, `repair_qgroups()`, and repair gating via `has_running_replace_or_balance()`.
- Checker stages defined earlier or in other check modules: `check_log_root()` from the previous chunk, `do_check_chunks_and_extents()`, `validate_free_space_cache()`, `do_check_fs_roots()`, `check_csums()`, `check_root_refs()`, `qgroup_verify_all()`, `report_qgroups()`, and `print_extent_state()`.
- Common command/runtime support: `getopt_long()`, `check_argc_exact()`, `usage_unknown_option()`, `arg_strtou64()`, mount detection through `check_mounted()`, open helpers through `open_ctree_fs_info()`, UUID formatting, task utils, warning/error messaging, and the simple-command registration macro.
- Compatibility with lowmem mode is explicit: extent checking delegates to `check_chunks_and_extents_lowmem()` inside `do_check_chunks_and_extents()` outside this chunk, and root-ref checking is skipped here when lowmem fs-root checking already handled it.

## Risks And Invariants

- Root-item repair must run before other repair code. The in-code comment explains that later backref or extent-tree repair can otherwise delete or rewrite evidence needed to repair stale root items, leaving the filesystem inconsistent.
- `roots_info_cache` relies on a root having exactly one highest-level tree block. Multiple nodes at the chosen level make the root item unrecoverable here, because there is no unambiguous replacement bytenr/generation/level.
- The extent scan assumes the first inline ref of a root extent is a `TREE_BLOCK_REF`; it guards against extent items without inline refs before dereferencing. Missing this boundary check would read beyond the leaf item.
- The transaction restart loop in `repair_root_items()` is intentionally conservative to avoid committing transactions for clean leaves and rotating backup roots unnecessarily. It must release paths before commits/restarts and preserve the next key when moving across leaves.
- `cmd_check()` mixes `ret` as a detailed errno-style status with `err` as the final command failure indicator. Several branches use `err |= !!ret`; a missed update can hide a detected error, while an early `return -EIO` in the checksum-tree refill path bypasses normal cleanup.
- Repair mode on a mounted or active filesystem is dangerous. The code blocks mounted filesystems unless `--force`, removes exclusive open under force, refuses running replace/balance, and warns before repair, but `--force --repair` can still proceed with substantial corruption risk.
- Clearing the tree log in repair mode is user-confirmed because any repair transaction would otherwise invalidate log replay expectations. Failure to zero the log is treated as fatal for repair startup.
- The `--init-extent-tree` path sets `OPEN_CTREE_NO_BLOCK_GROUPS` and `gfs_info->rebuilding_extent_tree`; later extent checking depends on that state to rebuild block-group items and cannot trust metadata free space while rebuilding.
- Stage ordering is part of correctness: critical roots precede all checks; log/root-item handling precedes extent/fs-root scans; free-space validation follows extent/chunk checks; root refs follow fs roots except in lowmem mode; deferred recow/delete-item repair happens after structural scans.
- `check_global_roots_uptodate()` expects counts equal to `gfs_info->nr_global_roots` for each global root class. A typo in its error string says "chritical", but the behavior is a hard `-EIO`.

## Cross-Chunk References

- The immediately preceding chunk defines `check_range_csummed()` and `check_log_root()`, which are the actual per-log-root validators called by `check_log()` in this chunk.
- Top-of-file state outside this chunk defines `gfs_info`, summary counters, `delete_items`, checker mode flags, `roots_info_cache`, progress printing helpers, and `parse_check_mode()`; `cmd_check()` depends on all of them.
- Earlier same-file functions implement the major checker stages invoked here: root-ref validation around line 3534, fs-root checking around line 4152, checksum checking around line 6268, extent/chunk checking around line 9379, `zero_log_tree()` around line 9867, and extent-tree reinitialization around line 9709.
- Header `check/mode-original.h` defines `struct root_item_info`; `check/mode-common.h` defines `g_task_ctx` and `enum task_position`; `check/qgroup-verify.c` stores the shared qgroup item-count pointer.
- This chunk is the final chunk of `main.c`: after `cmd_check()` returns, only `DEFINE_SIMPLE_COMMAND(check, "check")` remains, so no later same-file implementation needs to be merged for command dispatch.