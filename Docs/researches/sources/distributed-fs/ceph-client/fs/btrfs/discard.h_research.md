# sources/distributed-fs/ceph-client/fs/btrfs/discard.h

## Purpose
`discard.h` declares the async discard interface used by Btrfs block-group, free-space, mount, remount, and transaction code. It also centralizes the default maximum discard size and the two size filters used by the implementation.

## Important APIs, types, and functions
The header forward-declares `struct btrfs_fs_info`, `struct btrfs_discard_ctl`, and `struct btrfs_block_group`. Constants include `BTRFS_ASYNC_DISCARD_DEFAULT_MAX_SIZE`, `BTRFS_ASYNC_DISCARD_MAX_FILTER`, and `BTRFS_ASYNC_DISCARD_MIN_FILTER`. The exported functions cover list/filter updates (`btrfs_discard_check_filter`), work management (`btrfs_discard_cancel_work`, `btrfs_discard_queue_work`, `btrfs_discard_schedule_work`), accounting (`btrfs_discard_calc_delay`, `btrfs_discard_update_discardable`), and lifecycle (`btrfs_discard_punt_unused_bgs_list`, `btrfs_discard_resume`, `btrfs_discard_stop`, `btrfs_discard_init`, `btrfs_discard_cleanup`).

## Control flow
Callers initialize the discard controller during `btrfs_fs_info` setup, resume it after a writable mount is ready, queue block groups as free space changes, recalculate delays after discardable accounting changes, and stop/cleanup the delayed work during remount or unmount. The header intentionally hides list mechanics and state-machine details inside `discard.c`.

## State and persistence
The header itself holds no state. Its API operates on `fs_info->discard_ctl` and block-group runtime fields. The associated state is volatile and reconstructed at mount, while actual trim effects are external device side effects.

## Dependencies and integration points
It includes Linux integer/size types and is included by Btrfs components that need to enqueue discard work or manage discard lifecycle. The function signatures expose only Btrfs core structures, keeping free-space cache and workqueue details private to the implementation file.

## Risks and test signals
The main API risk is lifecycle ordering: callers must not queue work before initialization, must stop/cancel work before freeing block groups or workqueues, and must hold the free-space cache lock where `btrfs_discard_update_discardable` expects it. Test signals are compile coverage from block-group/free-space/disk-io users, async discard mount/remount/unmount tests, and fault-injection around workqueue creation and cancellation.
