# sources/distributed-fs/ceph/src/client/Client.h

## Purpose
`Client.h` declares the main libcephfs client object, its public POSIX-like API, the lower-level ll_* API, metadata request/session/capability machinery, directory read state, client lifecycle state machines, and fscrypt-aware read/write helpers. It is the central integration point between callers, MDS metadata operations, OSD object IO, local metadata cache objects, snapshot realms, delegation state, and admin/perf interfaces.

## Important APIs, Types, and Functions
The public `Client` API mirrors filesystem syscalls: mount/unmount, path traversal, directory iteration, file open/read/write/fsync/fallocate/locks, xattrs, snapshots, stat/statx, layout queries, quota/auth checks, and MDS/OSD map exposure. The ll_* family exposes inode/file-handle oriented operations for FUSE and low-level users. `dir_result_t` stores readdir cursor state, cached entries, hash/frag ordering, and fdopendir linkage. `SubvolumeMetricTracker` maps inodes to subvolume IDs and aggregates IO metrics. `MDSCommandOp` extends `CommandOp` with MDS targeting. Nested context classes coordinate async read/write completion, nonblocking fsync, encrypted write read-modify-write, and finisher locking. `StandaloneClient` owns objecter setup around the base client.

## Control Flow
External operations enter through public wrappers, acquire lifecycle `RWRef` state checks, resolve paths through `walk`/`path_walk`, build `MetaRequest` instances for MDS operations, and update local cache/capability state from replies. File IO flows through `Fh` and `Inode` capability checks, `Filer`/`ObjectCacher`, `ObjecterWriteback`, and completion contexts. Directory iteration advances a `dir_result_t` across fragments, local cache, and MDS readdir requests. Mount/init and unmount/shutdown are serialized through `initialize_state` and `mount_state`, then drain sessions, requests, caps, finishers, and cache entries.

## State and Persistence Behavior
The header declares most in-memory client state: root/cwd refs, inode and fd maps, fake inode maps, MDS sessions, outstanding metadata requests, cap flush tids, snap realm map, metrics counters, timers, finishers, fscrypt object, pool permission cache, reclaim state, and dentry/cap/open metrics. Persistence is external: metadata and capabilities are authoritative on MDS, data lives in OSD objects, while this class holds transient cache, leases, dirty cap queues, writeback state, and request replay/reclaim bookkeeping. The `client_lock` protects most client/cache state; `timer_lock` protects timers, and `command_lock` protects MDS admin commands.

## Dependencies and Integration Points
This file depends on Ceph common utilities, messenger dispatch, mon/objecter/filer/object cacher, MDS message/types, low-level CephFS types, and client cache model classes (`Inode`, `Dentry`, `Dir`, `Fh`, `MetaRequest`, `MetaSession`, `SnapRealm`). Linux builds integrate `FSCrypt`. Admin socket commands, perf counters, FUSE callbacks, interrupt/remount callbacks, capability renewal, MDS map/session handling, and OSD map full-flag handling all converge here.

## Risks and Edge Cases
The class has high concurrency risk: lifecycle state, client_lock, timer_lock, finishers, callbacks, and async contexts must agree on ownership and completion order. Cache/cap code risks use-after-free if refs are not balanced across dentries, inodes, Fhs, snap realms, and requests. Readdir offsets encode frag/hash state and can regress if ordering assumptions change. Encrypted writes require block-aligned RMW and may need read caps during write. Unmount/reclaim paths must drain unsafe requests and release caps without losing dirty metadata. Fake inode mapping is sensitive on 32-bit ino_t clients.

## Test Signals
Useful coverage includes mount/unmount races with active IO, ll_* lifecycle refusal during mounting/unmounting, readdir cache and hash-order seeks, MDS failover/reconnect and unsafe request replay, cap grant/revoke/flush/snap flush, objecter writeback errors reflected through `Fh::async_err`, fscrypt reads/writes and name wrapping, callback invalidation paths, delegation timeout behavior, and admin/perf dump stability.
