# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-internal.c

## Purpose
Implements upcall cache-invalidation state management: per-inode client registries, xattr filtering, notification dispatch, and a reaper thread for expired client entries and destroyed inode contexts.

## Important APIs, Types, and Functions
- `is_upcall_enabled()` and `get_cache_invalidation_timeout()` read private options.
- `__upcall_inode_ctx_set()`, `__upcall_inode_ctx_get()`, and `upcall_inode_ctx_get()` attach `upcall_inode_ctx_t` to inodes and maintain a global list.
- `__add_upcall_client()` creates client entries with UID, access time, and expiry attribute.
- `upcall_cleanup_expired_clients()`, `__upcall_cleanup_inode_ctx_client_list()`, and `upcall_cleanup_inode_ctx()` clean client/inode state and send forget invalidations.
- `upcall_reaper_thread()` and `upcall_reaper_thread_init()` maintain background cleanup.
- `up_filter_xattr()`, `up_filter_unregd_xattr()`, `up_filter_afr_xattr()`, `up_compare_afr_xattr()`, and `up_invalidate_needed()` decide which xattr changes trigger notifications.
- `upcall_cache_invalidate()` is the central access/update/invalidation entry point.
- `upcall_client_cache_invalidate()` builds `gf_upcall`/`gf_upcall_cache_invalidation` payloads and calls `this->notify()`.
- `upcall_cache_forget()` sends `UP_FORGET` notifications during inode context cleanup.

## Control Flow
Most wrapped fop callbacks call `upcall_cache_invalidate()`. That function resolves a valid inode context, handles nameless lookup cases by finding a linked inode from returned stat, updates or adds the current client entry, and notifies other recently active clients unless the operation is only atime. Notifications are synchronous on the fop path through `this->notify(GF_EVENT_UPCALL, ...)`.

The reaper thread loops until `priv->fini`, scans `priv->inode_ctx_list`, removes expired clients, frees contexts marked `destroy`, sleeps for half the current timeout, then repeats. Inode forget calls `upcall_cleanup_inode_ctx()`, which deletes the inode ctx, sends forget notifications, cleans client entries, and marks the ctx for reaper destruction.

## State and Persistence
Runtime state is in `upcall_private_t`: timeout, global inode context list, lock, reaper thread id, registered xattr patterns, fini flag, enable flag, and init flag. Each inode context stores a GFID, a client list, its own mutex, and a destroy marker. Each client entry stores `client_uid`, last access time, and expire time. This is in-memory only and rebuilt as clients access files.

## Dependencies and Integration Points
Depends on GlusterFS inode ctx APIs, list macros, locks, thread helpers, `gf_upcall` structures, dict APIs, AFR xattr prefix handling, fnmatch-style registration matching, and `upcall.h` types. Integrates with the server/client notification path via `GF_EVENT_UPCALL` and `GF_UPCALL_CACHE_INVALIDATION`.

## Risks
- Notifications are sent from the I/O path, with comments noting async delivery would be preferable.
- Lock ordering spans inode locks, private list locks, and client-list mutexes; deadlocks or use-after-free are risks if lifecycle changes.
- Reaper sleeps `timeout / 2`; very small or zero timeout values could cause busy behavior.
- Xattr filtering mutates dictionaries copied into local state; callers must not share mutable dicts incorrectly.
- `this->notify` failure removes a client entry while iterating, so list-safe traversal is essential.

## Test Signals
Tests should cover client registration, same-client suppression, cross-client notification, timeout expiry, inode forget/UP_FORGET, xattr registration and filtering, AFR pending xattr comparison, nameless lookup linked-inode handling, reaper cleanup, and reconfigure timeout changes.
