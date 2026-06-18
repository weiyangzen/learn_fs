# sources/distributed-fs/lizardfs/src/mount/lizard_client.cc

## Purpose
This is the central mount-side filesystem client implementation. It translates higher-level FUSE-facing `LizardClient` calls into master RPCs, chunkserver read/write cache operations, special inode handling, ACL/xattr conversion, directory-entry caching, credential registration, I/O limiting, advisory locking, statistics, and subsystem initialization/termination.

## Important APIs, Types, And Functions
Global state includes `gGroupCache`, `gDirEntryCache`, readdir sessions, cache timeouts, `keep_cache`, `use_rwlock`, `gDirectIo`, lock request counters, stats counters, and `acl_cache`. `updateGroups()` compresses secondary group vectors into master-registered group ids; `masterDisconnectedCallback()` resets group and dir caches and marks readdir sessions restarted. Attribute helpers convert protocol `Attributes` into `stat`, build mode/attribute strings, and map `RequestException` to system errors. Core filesystem APIs include `statfs`, `access`, `lookup`, `getattr`, `setattr`, `mknod`, `unlink`, `undel`, `mkdir`, `rmdir`, `symlink`, `readlink`, `rename`, `link`, `opendir`, `readdir`, `readreserved`, `readtrash`, `create`, `open`, `release`, `read`, `write`, `flush`, `fsync`, xattrs, locks, snapshot/goal/chunk queries, `fs_init`, and `fs_term`.

## Control Flow
Metadata operations validate special names/inodes, name lengths, permissions, and then call `fs_*` master RPCs using `RETRY_ON_ERROR_WITH_UPDATED_CREDENTIALS` so missing group registrations trigger credential upload and one retry. Directory reads first consult `DirEntryCache`, then fetch batches from the master, insert sequences and end markers, and repair offsets when the master restarts by searching for the last-read inode. Open/create allocate `finfo` objects with read or write pipeline state. Reads enforce local and global I/O limits, switch write descriptors to read mode by flushing pending data, align to block boundaries, and call `read_data()`. Writes enforce the same limiters, switch read descriptors to write mode, call `write_data()`, and invalidate inode cache entries. Flush/fsync drain pending writes; release closes lock state and file info.

## State And Persistence
This file owns most mount-process state: credential group cache, directory cache, ACL cache, special tweak variables, file-handle `finfo` objects, read/write cache handles, readdir sessions, lock usage flags, and stats counters. Durable filesystem effects occur through master RPCs and chunkserver write pipelines; local state is cache/control state and is reset or invalidated on mutations and reconnects.

## Dependencies And Integration Points
It integrates with `mastercomm`, `masterproxy`, `readdata`, `writedata`, `special_inode`, `direntry_cache`, `acl_cache`, ACL converters, rich ACL and optional OS X ACL converters, symlink cache, oplog/stats, I/O limiters, tweaks, protocol serializers, and chunkserver metadata. It is called by `mfs_fuse.cc` for normal FUSE requests and by administrative code for snapshot/goal/chunk queries.

## Risks And Test Signals
Risks include wide global mutable state, manual `finfo` allocation/destruction, multi-lock ordering around file reads/writes/flushes, cache invalidation gaps after mutations, master restart handling in readdir, xattr/ACL conversion failures, lock send/recv threading constraints, and mixed LizardFS-status vs errno inputs in a few admin error paths. Test signals include FUSE operation tests, ACL/xattr tests, read/write cache tests, limiter tests, direntry-cache restart scenarios, file-lock interrupt tests, and integration tests against a master/chunkserver cluster.
