# sources/distributed-fs/ceph-client/fs/btrfs/fs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/fs.h` is a central Btrfs filesystem state header. It defines block-size and extent-size constants, format feature support masks, mount option bits, filesystem runtime flags, exclusive operation types, major runtime structures such as `struct btrfs_fs_info`, `struct btrfs_free_cluster`, discard/device-replace/commit/delayed-root state, and inline helpers for metadata sizing, generation accessors, mount options, shutdown, and test-only behavior. The file was read as a complete 1238-line header.

## Important APIs, Types, and Functions

Important constants include `BTRFS_MIN_BLOCKSIZE`, `BTRFS_MAX_BLOCKSIZE`, `BTRFS_MAX_EXTENT_SIZE`, `BTRFS_MAX_TRIM_LENGTH`, `BTRFS_SUPER_INFO_OFFSET`, `BTRFS_SUPER_INFO_SIZE`, `BTRFS_DIRTY_METADATA_THRESH`, feature support/safe-set masks, `BTRFS_DEFAULT_COMMIT_INTERVAL`, and `BTRFS_DEFAULT_MAX_INLINE`. It defines runtime filesystem state enums (`BTRFS_FS_STATE_*`), `fs_info->flags` bits such as `BTRFS_FS_CREATING_FREE_SPACE_TREE`, `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`, `BTRFS_FS_CLEANUP_SPACE_CACHE_V1`, and mount option bits such as `BTRFS_MOUNT_SPACE_CACHE`, `BTRFS_MOUNT_FREE_SPACE_TREE`, `BTRFS_MOUNT_DISCARD_SYNC`, and `BTRFS_MOUNT_DISCARD_ASYNC`.

Major structures are `struct btrfs_dev_replace`, `struct btrfs_free_cluster`, `struct btrfs_discard_ctl`, `enum btrfs_exclusive_operation`, `struct btrfs_commit_stats`, `struct btrfs_delayed_root`, and the large `struct btrfs_fs_info`. Inline/function declarations include folio/inode/fs_info conversion helpers, `btrfs_alloc_write_mask`, `btrfs_min_folio_size`, generation and root-drop accessors, checksum leaf calculation, metadata reservation calculators, zoned-mode detection, max-extent counting, blocks-per-folio calculation, exclusive operation APIs, checksum APIs, feature flag APIs/macros, mount-option macros, cleaner/sleep checks, shutdown forcing, ordered-folio flag aliases, and sanity-test-only exports.

## Control Flow

This header mostly defines data and inline helpers. Typical control flow shaped by it starts at mount: supported feature masks validate superblock flags, mount options populate `fs_info->mount_opt`, block sizes and checksum fields are cached, and `struct btrfs_fs_info` owns roots, locks, counters, workers, reservations, block groups, discard control, quota state, zoned state, and error state. Runtime code then uses `btrfs_test_opt()` and flag bits to branch into feature-specific behavior such as free-space tree loading, cache v1 cleanup, async discard, zoned allocation, qgroups, relocation, and tree-mod-log use.

The inline generation accessors centralize `READ_ONCE`/`WRITE_ONCE` use for transaction generation fields. Metadata reservation helpers compute worst-case node COW costs for insertion and modification. Shutdown helper `btrfs_force_shutdown()` writes `fs_error`, sets emergency shutdown once, logs a critical message, and reports filesystem shutdown. Mount option and feature macros wrap raw bit operations so call sites can use symbolic feature names.

## State and Persistence Behavior

`struct btrfs_fs_info` is the in-memory root of mounted filesystem state. It holds persistent-format mirrors such as `super_copy`, `super_for_commit`, feature bits, checksum type/size, block sizes, generation counters, roots, block-group cache tree, mapping tree, global roots, free chunk space, reservations, transaction pointers, workqueues, device replacement state, discard control, quotas, tree-mod-log state, zoned state, commit stats, and error/shutdown flags. Some fields are persisted indirectly through superblock or btree commits; many are runtime-only synchronization and accounting fields.

The header documents lock expectations for several fields: generation under transaction locking, `last_trans_committed` through accessors, feature flags under `super_lock`, block-group cache under `block_group_cache_lock`, mapping tree under `mapping_tree_lock`, delayed roots under their lock, and exclusive operations under `super_lock`. Mount and feature masks encode on-disk compatibility rules and determine which unknown feature combinations can be mounted.

## Dependencies and Integration Points

The header depends on crypto, block device, memory sizing, time, atomics, percpu counters, completion, lockdep, spinlocks, mutexes, rwsems, lists, pagemap, radix tree, workqueues, wait queues, scheduler, rbtrees, xxhash, filesystem error reporting, Btrfs uapi tree definitions, and local headers `extent-io-tree.h`, `async-thread.h`, `block-rsv.h`, and `messages.h`. Nearly every Btrfs subsystem integrates with it: transactions, roots, extent allocation, free-space cache/tree, scrub, balance, relocation, qgroups, device replacement, discard, zoned mode, compression, delayed refs/items, tree log, sysfs, and tests.

## Risks and Edge Cases

Because this is a central shared contract, field layout and semantic changes have broad blast radius. Feature support masks must stay synchronized with mount validation and btrfs-progs expectations. Mount-option bits must be reflected in option display/parsing code. Locking comments are important; bypassing accessors or using fields under the wrong lock can introduce races. Some values differ under `CONFIG_BTRFS_DEBUG`, `CONFIG_BTRFS_EXPERIMENTAL`, `CONFIG_BLK_DEV_ZONED`, 32-bit builds, and sanity-test builds. `btrfs_force_shutdown()` intentionally marks an emergency shutdown without remounting read-only, so callers must understand how thaw and RO/RW paths diverge.

## Test Signals

Signals include broad Btrfs compile coverage across config matrices, mount tests for feature masks and mount options, lockdep coverage for fs_info locks and exclusive operations, checksum and block-size tests through `fs.c`, zoned and non-zoned allocation tests, free-space tree/cache feature toggles, sysfs feature-change updates, emergency shutdown behavior, and sanity-test builds that exercise `EXPORT_FOR_TESTS` branches.
