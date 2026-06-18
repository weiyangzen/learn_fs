# sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.c` implements the debug-only Btrfs reference verification cache behind the `REF_VERIFY` mount option. It builds an in-memory shadow model of extent-tree references at mount time, then updates that model on delayed reference modifications to detect incorrect reference accounting, invalid drops/adds, stale reallocations, overlapping freed ranges, and extent-tree inconsistencies. The source was read as a complete 1025-line file.

## Important APIs, Types, and Functions

The public functions are `btrfs_build_ref_tree()`, `btrfs_ref_tree_mod()`, `btrfs_free_ref_cache()`, and `btrfs_free_ref_tree_range()`. Internal state is modeled with `struct block_entry` for each referenced bytenr, `struct ref_entry` for individual tree/data/shared refs, `struct root_entry` for per-root direct ref counts, and `struct ref_action` for historical modifications plus optional stack traces.

Core helpers include rb-tree comparators and insert/lookups for block, root, and ref entries; `add_tree_block()`, `add_shared_data_ref()`, and `add_extent_data_ref()` for loading on-disk refs; `process_extent_item()`, `process_leaf()`, `walk_down_tree()`, and `walk_up_tree()` for extent-tree traversal; `dump_ref_action()` and `dump_block_entry()` for diagnostic logging; and `free_block_entry()` for full cache teardown.

## Control Flow

At mount or enable time, `btrfs_build_ref_tree()` checks `REF_VERIFY`, obtains the extent root, read-locks the root node, and walks the extent tree manually. Leaf processing reads extent items, metadata items, inline refs, and separate ref key items, then inserts equivalent shadow records into `fs_info->block_tree`. The walker tracks the last extent bytenr/length/tree-block level so separate ref items can be associated with the correct extent item.

During normal delayed-ref processing, `btrfs_ref_tree_mod()` receives a `struct btrfs_ref`, converts it into a normalized `ref_entry`, records a `ref_action` with stack trace and action metadata, and updates the matching `block_entry` under `fs_info->ref_verify_lock`. Add-extent actions preallocate or reset the block entry and verify that reallocation is not happening while references remain. Add/drop ref actions update `ref_entry`, `root_entry`, and total block ref counts, with metadata refs restricted from duplicate adds. On any verification failure it dumps diagnostics, frees the ref cache, and clears `REF_VERIFY`.

Freeing paths include `btrfs_free_ref_cache()`, which drains the whole rb-tree, and `btrfs_free_ref_tree_range()`, which removes cached entries for a block group range while warning about overlapping cached extents.

## State and Persistence Behavior

All verifier state is in memory under `fs_info->block_tree` and protected by `fs_info->ref_verify_lock`. It mirrors persistent extent-tree reference records but does not write disk state. `block_entry` objects are intentionally retained with historical actions until unmount or range removal so reallocations can be checked against prior history. Stack traces are stored only when `CONFIG_STACKTRACE` is enabled.

If the verifier detects an inconsistency or cannot continue safely, it tears down the in-memory cache and disables the mount option. This makes the verifier fail closed with respect to debug checking while leaving the live filesystem path to continue without ref verification.

## Dependencies and Integration Points

The file depends on Btrfs extent-tree accessors, delayed-ref structures, root locking and extent buffer APIs, rb-tree helpers, spinlocks, mount options, stacktrace support, and logging. It is compiled only through the debug interface declared in `ref-verify.h`; non-debug builds use inline no-op stubs. Runtime integration occurs wherever delayed refs call `btrfs_ref_tree_mod()`, mount setup calls `btrfs_build_ref_tree()`, block-group cleanup calls `btrfs_free_ref_tree_range()`, and unmount/disable calls `btrfs_free_ref_cache()`.

## Risks and Edge Cases

The shadow model must exactly match the extent-tree representation. Inline refs and separate ref key items are easy to misassociate if `bytenr`, `num_bytes`, or tree-block level tracking is stale. Metadata and data refs have different uniqueness rules, and shared refs use parent-based identity rather than direct root identity. The code performs memory allocation before or around spinlock-protected updates; error paths must free partially built objects and unlock correctly.

Because failures disable `REF_VERIFY`, a false positive can remove useful debug coverage for the rest of the mount. Range freeing has special overlap diagnostics and must tolerate empty block groups. Manual tree walking must balance read locks and extent-buffer refs while allowing rescheduling during large cache frees.

## Test Signals

Test signals include debug-kernel mounts with `ref_verify`, fstests that stress snapshot create/delete, reflink, extent sharing, relocation, block-group removal, and delayed-ref churn, plus injected duplicate refs, invalid drops, and reallocation-with-live-ref scenarios. Logging from `dump_block_entry()` and `dump_ref_action()` is the main diagnostic output; stack traces are an additional signal when `CONFIG_STACKTRACE` is enabled.
