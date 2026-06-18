# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog.c

## Purpose
Implements the GlusterFS `changelog` feature translator. It intercepts selected filesystem operations, records data/metadata/entry changes into changelog journals, dispatches live notification events, and coordinates snapshot barriers so geo-replication and glusterfind consumers see a consistent operation stream.

## Important APIs, types, and functions
The exported translator entry points are `init`, `fini`, `reconfigure`, `notify`, `mem_acct_init`, the `fops` table, and `cbks.release`. Entry fops include `changelog_mknod`, `mkdir`, `create`, `symlink`, `link`, `rename`, `unlink`, and `rmdir`; metadata fops include `{f,}setattr`, `{f,}setxattr`, `{f,}removexattr`, `{f,}xattrop`; data fops include `{f,}truncate` and `writev`. Callback pairs call `changelog_update()` on successful child completion. Helper routines configure operation mode, encoding, barrier timeout, helper threads, RPC notification, and option cleanup.

## Control flow
Each logged fop first checks whether changelog is active and whether the request is internal/rebalance/shard-excluded where applicable. It initializes a `changelog_local_t`, fills encoded changelog records with fop number, gfid, mode/uid/gid, or entry names, and either winds immediately or queues a call stub behind the changelog barrier. On callback success, it updates the log as `CHANGELOG_TYPE_DATA`, `METADATA`, `METADATA_XATTR`, or `ENTRY`, decrements barrier fop counters, and unwinds. Barrier `notify()` requests start or stop snapshot logging, flip `barrier_ext`, enable/disable queuing, wake rollover through a pipe, and drain queued operations.

## State and persistence behavior
Persistent output is the changelog directory tree, htime data, csnap logging, and per-slice changelog files written by the runtime backend selected from `cb_bootstrap`. Durable options are `changelog-dir`, `encoding`, `rollover-time`, `fsync-interval`, and delete-path capture. Runtime state lives in `changelog_priv_t`: active/rpc flags, current color, fop counters, queue, pthread condition variables, RPC service/listeners, rolling buffers, helper thread ids, htime fd, changelog fd, and event selection. Per-operation state is in `frame->local` and is cleaned through changelog unwind macros.

## Dependencies and integration points
Depends on Gluster xlator stack APIs, changelog runtime/encoder/RPC headers, call stubs, dictionaries, mem pools, pthreads, htime/csnap helpers, and RPC service cleanup. Integrates with geo-replication/glusterfind through journal files and with live consumers through `changelog_dispatch_event()`, open/create/release events, IPC event dispatch, and Unix-domain changelog RPC sockets. DHT special rename metadata and shard/tier internal markers influence what is recorded.

## Risks and test signals
High-risk areas are barrier races, counter/color ordering, queued stub allocation failure, helper thread cleanup, RPC listener teardown during parent-down, htime/csnap rollover, and option reconfigure while active. The source contains apparent duplicate tokens near `changelog_unlink` and `changelog_link` in this snapshot, which is a build-risk signal. Tests should exercise all logged fops with active/inactive changelog, internal fop suppression, DHT rename-as-unlink, delete-path capture, virtual `GF_XATTR_TRIGGER_SYNC`, barrier on/off/timeout, RPC notification enablement, reconfigure from inactive to active, and cleanup during parent down.
