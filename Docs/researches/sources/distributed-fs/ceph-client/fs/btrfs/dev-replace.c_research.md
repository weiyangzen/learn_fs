# sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.c

## Purpose

`dev-replace.c` implements Btrfs online device replacement. It copies existing extents from a source device to a target device using scrub infrastructure while new writes are duplicated to both source and target through the block mapping path. When copying finishes, it atomically updates in-memory chunk mappings and on-disk device replace state so the target assumes the source device identity and the old source is removed from active filesystem metadata.

## Important APIs, Types, and Functions

Mount/state APIs are `btrfs_init_dev_replace()` and `btrfs_run_dev_replace()`. User-facing control APIs are `btrfs_dev_replace_by_ioctl()`, `btrfs_dev_replace_status()`, `btrfs_dev_replace_cancel()`, `btrfs_dev_replace_suspend_for_unmount()`, and `btrfs_resume_dev_replace_async()`. Runtime helpers include `btrfs_init_dev_replace_tgtdev()`, `mark_block_group_to_copy()`, `btrfs_finish_block_group_to_copy()`, `btrfs_dev_replace_start()`, `btrfs_dev_replace_finishing()`, `btrfs_dev_replace_kthread()`, `btrfs_dev_replace_is_ongoing()`, `btrfs_bio_counter_sub()`, and `btrfs_bio_counter_inc_blocked()`.

Important finishing helpers include `btrfs_set_target_alloc_state()`, which copies chunk allocation state from source to target, and `btrfs_dev_replace_update_device_in_mapping_tree()`, which rewrites chunk-map stripes from source device pointers to target device pointers.

## Control Flow

Mount initialization reads the `BTRFS_DEV_REPLACE_KEY` item from the device root, validates item size, restores state, source/target devices, cursors, timestamps, and error counters, and rejects inconsistent cases such as a replace target without a valid active item unless degraded semantics allow cancellation.

Starting replacement resolves the source device, rejects active swapfile and seed filesystem cases, commits outstanding transactions to refresh committed sizes, opens and validates the target block device, checks zone type and capacity, adds a replacement target device with devid `BTRFS_DEV_REPLACE_DEVID`, optionally marks zoned block groups as `TO_COPY`, sets `replace_state` to started under `dev_replace->rwsem`, adds sysfs state, waits for ordered roots, commits the device replace item, and calls `btrfs_scrub_dev()` to copy source extents. Finishing then handles success or scrub error.

Finishing serializes against cancel/unmount, flushes all delalloc/ordered I/O, repeatedly commits transactions until the source has no post-commit device updates, locks the device list and chunk mutex, marks replace finished or canceled, updates mapping-tree stripes and target allocation state on success, swaps devids and UUIDs, moves allocation list membership, blocks new bios while removing the old source, updates sysfs, scratches old superblocks if writable, commits superblocks, and frees the old source device.

Cancel either asks scrub to cancel an active replacement and lets finishing clean up, or directly cancels suspended replacements by updating state, committing, and destroying the target. Resume turns suspended state back to started and launches `btrfs-devrepl` if no other exclusive operation is active. The bio counter blocks new bios during source/target removal and wakes waiters when safe.

## State and Persistence Behavior

Persistent state is the device replace item in the device tree, written by `btrfs_run_dev_replace()` during transaction commit. It stores source devid, read-from-source mode, replace state, start/stop times, write/read error counters, and copy cursors. In-memory state lives in `fs_info->dev_replace`: rwsem-protected source/target pointers, state, cursors, scrub progress, error counters, writeback flag, finishing/cancel mutex, replacement task, waitqueue, and per-cpu bio counter.

Replacement also mutates durable device identity by swapping devid/UUID fields and writing superblocks. The scrub copy covers committed extents while write duplication covers new writes after start. Zoned filesystems additionally keep block groups read-only until all source stripes are copied.

## Dependencies and Integration Points

This file integrates with the ioctl layer, device tree items, transaction commit, block device opening, volume/device list management, sysfs, scrub, async kthreads, exclusive-operation tracking, chunk mapping tree, block-group runtime flags, zoned device checks, ordered extent flushing, superblock writing, device stats, and the bio mapping path that duplicates writes during replacement.

## Risks and Edge Cases

The start/finish sequence has many cross-lock constraints: device list mutex, chunk mutex, mapping tree lock, dev_replace rwsem, and finish/cancel mutex must prevent new chunks, bios, or superblock writes from seeing half-swapped devices. Missing source/target devices during mount require degraded handling. Target validation must reject too-small devices, in-filesystem devices, zone mismatches, seed filesystems, and active swapfile sources. Scrub errors route to cancel cleanup; errors while updating target allocation state must destroy the target safely. Progress calculation divides by source size/1000 and assumes a valid nonzero source size while active.

## Test Signals

Validation should cover successful online replacement, cancel during active scrub, cancel of suspended replacement, resume after unmount/remount, missing source/target in degraded and non-degraded mounts, target too small/in filesystem/zone mismatch, scrub error cleanup, write duplication during replacement, direct/metadata writes while finishing, sysfs device replacement, superblock scratching, zoned `TO_COPY` block group handling, and bio counter blocking during device removal.
