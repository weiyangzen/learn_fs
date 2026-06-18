# sources/distributed-fs/ceph-client/fs/super.c

## Purpose
This is the VFS superblock core. It allocates, publishes, finds, reconfigures, freezes, thaws, synchronizes, and tears down `struct super_block` instances. It also provides common helpers for anonymous, nodev, single-instance, keyed, and block-device-backed mounts.

## Important APIs, Types, and Functions
Key exports include `sget_fc()`, `sget()`, `vfs_get_tree()`, `get_tree_nodev()`, `get_tree_single()`, `get_tree_keyed()`, `get_tree_bdev_flags()`, `get_tree_bdev()`, `deactivate_super()`, `deactivate_locked_super()`, `generic_shutdown_super()`, `reconfigure_super()`, `freeze_super()`, `thaw_super()`, `get_anon_bdev()`, `kill_anon_super()`, `kill_block_super()`, `super_setup_bdi()`, and `sb_init_dio_done_wq()`. Internal state is coordinated through global `super_blocks`, `sb_lock`, `s_umount`, `s_count`, `s_active`, `s_flags`, per-superblock shrinkers, LRUs, freeze counters, and optional block-device holder callbacks.

## Control Flow and State
Mount construction flows through `alloc_super()` then `sget_fc()` or `sget()`, which either reuses a matching live superblock or publishes a new nascent one on both the global list and filesystem-type list. `vfs_get_tree()` calls the filesystem `get_tree` operation, requires `fc->root`, then marks the superblock `SB_BORN` with release ordering so waiters can safely see initialized fields. Shutdown reverses this: active references drain through `deactivate_locked_super()`, filesystem `kill_sb()` runs, `generic_shutdown_super()` evicts dentries/inodes and calls `put_super`, and waiters are notified through `SB_DYING`/`SB_DEAD`.

Freeze control is staged by `freeze_super()`: block normal writers, block page faults, sync, block internal filesystem writers, invoke `->freeze_fs`, record holder counts/owner, and leave the filesystem in `SB_FREEZE_COMPLETE`. `thaw_super()` validates holder/owner rules and unwinds the staged rwsems and optional `->unfreeze_fs`.

## Persistence, Dependencies, and Integration
The file sits between mount API/fs_context, block layer holder operations, writeback, shrinkers, fsnotify, fscrypt, security hooks, cgroup writeback, and filesystem-specific `super_operations`. Block-backed mounts open and claim the source bdev, reject frozen/read-only-incompatible devices, set block size and BDI, and register `fs_holder_ops` for block-device death, sync, freeze, and thaw.

## Risks and Test Signals
Risk centers on lifecycle races: nascent superblocks visible before `SB_BORN`, reuse during shutdown, freeze nesting ownership, bdev surprise removal, and deadlocks between shrinker, `s_umount`, `sb_lock`, and block-device locks. Strong signals are mount/reconfigure/unmount stress, filesystem freeze/thaw with nested userspace/kernel holders, bdev removal tests, lockdep, KASAN/RCU checks, sync-after-unmount assertions, and filesystem xfstests that exercise remount RO/RW and `syncfs`.
