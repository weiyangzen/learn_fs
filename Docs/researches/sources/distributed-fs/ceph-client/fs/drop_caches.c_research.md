# sources/distributed-fs/ceph-client/fs/drop_caches.c

## Purpose
`drop_caches.c` implements the `/proc/sys/vm/drop_caches` sysctl. It lets privileged users request pagecache and/or slab reclaim for testing and operations.

## Important APIs, Types, And Functions
The file defines global `sysctl_drop_caches`, `drop_pagecache_sb()`, `drop_caches_sysctl_handler()`, the `drop_caches_table`, and initcall `init_vm_drop_caches_sysctls()`.

## Control Flow
Writing the sysctl is parsed by `proc_dointvec_minmax()` with allowed values 1 through 4. Bit 1 drains LRU additions, iterates all superblocks, and invalidates inode mappings through `drop_pagecache_sb()`. Bit 2 calls `drop_slab()`. Bit 4 suppresses future informational logging. Successful pagecache/slab drops increment `DROP_PAGECACHE` and `DROP_SLAB` VM events.

`drop_pagecache_sb()` scans each superblock inode list under `s_inode_list_lock`, skips freeing/new inodes and empty mappings unless rescheduling is needed, takes an inode reference before dropping the list lock, invalidates mapping pages, drops the previous inode reference, calls `cond_resched()`, and resumes the scan.

## State And Persistence
The sysctl integer and static `stfu` flag are in-memory kernel state. Cache contents are not persistent; writing this sysctl intentionally discards reclaimable cache state.

## Dependencies And Integration Points
It integrates with sysctl registration, VFS superblock/inode lists, pagecache invalidation, slab reclaim, scheduler rescheduling, VM event counters, and filesystem initcalls.

## Risks
Dropping caches can cause large performance disruption and lock contention while scanning inode lists. The code avoids unusual inode states and holds references carefully, but it still depends on VFS locking correctness. The log suppression bit changes future observability.

## Test Signals
Manual sysctl writes with values 1, 2, 3, and 4 should update VM counters and logs as expected. Stress tests should verify no inode reference leaks or lockdep issues while filesystems are active.
