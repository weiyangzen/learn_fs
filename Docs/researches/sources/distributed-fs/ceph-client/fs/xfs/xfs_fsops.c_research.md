# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.c

## Purpose
`xfs_fsops.c` implements filesystem-level operations: data/log growfs entry points, reserved block pool resizing, user-triggered shutdown, forced shutdown reporting, and per-AG/realtime metadata reservation setup and teardown.

## Important APIs, types, and functions
Public functions are `xfs_growfs_data`, `xfs_growfs_log`, `xfs_reserve_blocks`, `xfs_fs_goingdown`, `xfs_do_force_shutdown`, `xfs_fs_reserve_ag_blocks`, and `xfs_fs_unreserve_ag_blocks`. Internal helpers initialize new AG headers, perform data grow/shrink transaction work, reject unsupported log grow/move requests, and update `imaxpct`.

## Control flow
Data grow requires `CAP_SYS_ADMIN`, takes `m_growlock`, rejects internal-rt data size changes, optionally updates `imaxpct`, then grows or experimentally shrinks data blocks. Grow validates block count and device reachability, checks realtime geometry, computes AG deltas, initializes new perag structures, allocates a grow transaction, writes new AG headers non-transactionally before logging sb changes, extends or shrinks the last AG, updates superblock counters transactionally, commits synchronously, updates mount-side derived limits, reserves AG metadata blocks, recomputes rt btree maxlevels, updates secondary superblocks, and bumps mount generation. Log grow is permission/lock protected but returns `-ENOSYS` for actual movement/resizing. `xfs_reserve_blocks` changes per-counter reserve totals under `m_sb_lock`, moving unused reserves back or partially filling from free counters. Shutdown ioctls map user flags to log/device shutdown variants; `xfs_do_force_shutdown` atomically marks shutdown, shuts down the log, reports alerts, fserror, and healthmon events.

## State and persistence
Growfs persists superblock AG count, data block count, free block count, imaxpct, new AG headers, and secondary superblocks. Runtime state includes perag arrays, max inode count, low-space thresholds, allocation set-aside, mount generation, reserve pool counters, shutdown flags, and metadata reserve pools. Forced shutdown prevents further persistent writes after the first successful state transition.

## Dependencies and integration points
This file integrates ioctl dispatch, superblock validation/logging, AG header initialization, perag lifecycle, grow/shrink helpers, transaction reservations, allocation reservations, realtime geometry and btree sizing, block-device freeze/thaw, log shutdown, fserror, health monitor, and admin capability checks.

## Risks and test signals
Risks include partial grow after non-transactional header writes, unsupported shrink edge cases, secondary superblock update failures after live size change, reserve counter TOCTOU near ENOSPC, shutdown races, and metadata reservation failures forcing shutdown. Test signals include grow by extending last AG and adding new AGs, no-op grow, invalid block counts, internal realtime rejection, imaxpct-only updates, reserve increase/decrease under concurrent allocation, goingdown flag variants, repeated forced shutdown calls, AG reservation ENOSPC versus hard errors, and recovery after crash during growfs.
