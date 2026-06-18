# sources/distributed-fs/ceph-client/fs/cachefiles/daemon.c

## Purpose
`daemon.c` implements the `/dev/cachefiles` control interface used by cachefilesd. It parses configuration/control commands, exposes cache state to userspace, handles polling, binds/unbinds caches, and coordinates daemon lifetime.

## Important APIs, Types, and Functions
It exports `cachefiles_daemon_fops`, `cachefiles_flush_reqs`, `cachefiles_get_unbind_pincount`, and `cachefiles_put_unbind_pincount`. The file operations are open, release, read, write, poll, and noop llseek. Command handlers include `bind`, `dir`, `tag`, `secctx`, `frun`, `fcull`, `fstop`, `brun`, `bcull`, `bstop`, `cull`, `debug`, `inuse`, plus on-demand `copen` and `restore` when configured.

## Control Flow
Open requires `CAP_SYS_ADMIN`, enforces a single open instance with `cachefiles_open`, allocates and initializes `struct cachefiles_cache`, sets default culling thresholds, initializes xarrays and lists, and attaches it to `file->private_data`. Writes copy one command from userspace, reject embedded NULs and oversized input, split command and arguments, serialize through `daemon_mutex`, and dispatch to the command table unless `CACHEFILES_DEAD` is set. Reads report either ordinary culling/threshold/release state or on-demand requests. Poll reports readable state changes or on-demand work and writable culling state. Release marks the cache dead, flushes on-demand requests if necessary, drops the daemon pointer, and decrements the unbind pin count, which eventually calls unbind and frees the cache.

## State and Persistence Behavior
Daemon-set state includes root directory, tag, optional security context ID, threshold percentages, ready/dead/culling/on-demand flags, request xarrays, and unbind pin count. `bind` persists by creating/opening cache directories and registering the cache. `cull` persists by unlinking or moving backing objects into the graveyard. Read drains `f_released` and `b_released` counters.

## Dependencies and Integration Points
The daemon interface connects userspace cachefilesd to `cache.c`, `namei.c`, `security.c`, `ondemand.c`, and FS-Cache. It uses Linux capability checks, copy-from-user/copy-to-user, poll waitqueues, current working directory for `cull`/`inuse`, LSM security helpers, and VFS path operations under CacheFiles credentials.

## Risks and Edge Cases
Single-open and unbind pinning prevent use-after-free while anonymous on-demand fds exist. Command parsing must reject malformed thresholds and second `dir`, `tag`, or `secctx` commands. The threshold invariant is `stop < cull < run < 100` for both files and blocks. `cachefiles_flush_reqs` relies on memory ordering with request enqueue to avoid orphaned on-demand requests during daemon death.

## Test Signals
Exercise command parser errors, duplicate open, non-admin open, bind without `dir`, bad threshold ranges, on-demand and non-on-demand poll/read behavior, release during active requests, `cull` and `inuse` with invalid cwd or names containing `/`, and daemon restart/recovery paths.
