# Chunk Research: sources/local-fs/btrfs-progs/check/main.c lines 1-10053

## Scope And Position

This chunk covers almost all of `btrfs check`'s original-mode implementation in `sources/local-fs/btrfs-progs/check/main.c`: global state, inode/root checks, extent/chunk/device verification, repair helpers, and the beginning of log-tree loading. The range ends at line 10053 inside `load_log_root()`, so log-tree orchestration and CLI command handling continue in the next chunk.

## APIs And Entry Points

Visible non-static APIs include `free_chunk_cache_tree()`, `insert_block_group_record()`, `free_block_group_tree()`, `insert_device_extent_record()`, `free_device_extent_tree()`, `btrfs_new_chunk_record()`, `btrfs_new_block_group_record()`, `btrfs_new_device_extent_record()`, and `check_chunks()`.

Main internal entry points are `do_check_fs_roots()`, `do_check_chunks_and_extents()`, `check_csums()`, and `check_log_root()`.

## Control Flow

The chunk implements original-mode fs-root walking through `check_fs_roots()` and `check_fs_root()`. It builds inode/root caches while manually walking B-trees with `walk_down_tree()` and `walk_up_tree()`, processes inode, dir, xattr, file extent, and root-ref items, and reconciles records after shared-node merging.

Inode repair is gated by `opt_check_repair`. `check_inode_recs()` stages backref deletion/addition before final inode validation, while `try_repair_inode()` applies repairs for bad dir hashes, invalid imode/generation, missing inode items, discounted extents, wrong isize/nbytes, orphan items, nlinks, inline ram_bytes, and unaligned extent records.

Extent checking scans tree blocks via `run_next_block()`, builds `extent_record` objects, parses extent-tree items, records data/tree backrefs, validates full-backref state, and later reconciles all remaining extent records in `check_extent_refs()`. Repair paths can delete/recreate extent refs, fix full-backref flags, repair generations, prune corrupt blocks, and restart with `-EAGAIN`.

Chunk/device verification builds `chunk_record`, `block_group_record`, `device_extent_record`, and `device_record` views, then cross-checks chunks against block groups and dev extents, device `bytes_used` against dev extents, super/device sizing, and dev extent overlap/bounds.

Checksum validation scans csum roots, detects csum overlap/oversized items, optionally verifies data against all mirrors, and checks csum ranges against extent records. `check_log_root()` verifies logged regular extents have checksums in the log or main checksum root.

## State And Dependencies

Key mutable state includes `gfs_info`, global accounting counters, `duplicate_extents`, `delete_items`, `no_holes`, `is_free_space_tree`, `init_extent_tree`, `check_data_csum`, and `roots_info_cache`.

The chunk depends heavily on btrfs-progs shared tree, disk, transaction, accessor, extent-cache, rbtree/list, repair, and lowmem-mode APIs. It mutates `gfs_info->corrupt_blocks`, `fsck_extent_cache`, `excluded_extents`, and `free_extent_hook` during repair.

## Risks And Edge Cases

Repairs are destructive: they can delete items, recreate refs, punch holes, reset roots, prune corrupt blocks, and rebuild extent/block-group accounting.

Notable risks visible in this chunk:
- `try_to_fix_bad_block()` appears to check `IS_ERR(root)` instead of `IS_ERR(search_root)`.
- `record_unaligned_extent_rec()` duplicates the same existing-record scan.
- `process_extent_item()` reports corrupt inline refs but still returns `0`.
- `check_extent_refs()` appears to assign `err = cur_err` per record rather than accumulating all errors.
- Multiple corruption paths use `BUG_ON()` or `abort()`, so malformed filesystems can terminate the checker.
- Full-backref inference relies on root objectid ordering and has an explicit FIXME.
- The chunk boundary cuts `load_log_root()` before it reads and validates the log root item.

## Cross-Chunk References

The next chunk must complete `load_log_root()`, `check_log()`, roots-info cache handling, root item repair, global-root freshness checks, early critical root checks, command usage, and `cmd_check()`.

This chunk also calls lowmem implementations from other files: `check_fs_roots_lowmem()` and `check_chunks_and_extents_lowmem()`.

## Summary

Lines 1-10053 implement the original-mode core of `btrfs check`: walking filesystem roots, collecting inode/root/extent/chunk/device facts, validating cross-references, and applying repair strategies. The core pattern is to build temporary reconciliation caches from independent metadata views, free records that agree, report or repair records that remain, and restart scans after repairs invalidate cached state.