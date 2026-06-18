# sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.c

## Purpose
Implements a TTL-based authorization cache for NFS file handles. It records that a host has been authorized for a file handle and keeps the matched `export_item` so later NFS operations can avoid reparsing or rewalking exports and netgroups until the entry expires.

## APIs, Types, and Functions
Public functions are `auth_cache_init()`, `cache_nfs_fh()`, `is_nfs_fh_cached()`, `is_nfs_fh_cached_and_writeable()`, and `auth_cache_purge()`. Internal pieces include `enum auth_cache_lookup_results`, `struct auth_cache_entry`, `make_hashkey()`, `auth_cache_entry_init()`, `auth_cache_entry_free()`, `auth_cache_add()`, `_auth_cache_expired()`, `auth_cache_get()`, `auth_cache_lookup()`, and `auth_cache_entry_purge()`.

## Control Flow, State, and Persistence
`make_hashkey()` builds a key from file-handle `exportid`, `mountid`, and host address. `cache_nfs_fh()` first looks up the entry, then creates a refcounted `auth_cache_entry`, timestamps it with `gf_time()`, takes a reference to the authorized `export_item`, wraps it in a `data_t`, and inserts it under the cache lock. `auth_cache_lookup()` generates the same key, calls `auth_cache_get()`, returns the cached timestamp and `opts->rw` flag on hit, and releases the entry reference. Expired entries are removed from the dict. `auth_cache_purge()` swaps in a new dict under lock, then walks and releases entries from the old dict. State is in `struct auth_cache`: a lock, dict, TTL seconds, and per-entry references to export options.

## Dependencies and Integration
Depends on Gluster `dict_t`, locks, refcount helpers, `data_t`, UUID formatting, `gf_time()`, NFSv3 file-handle layout, export parsing structures, and NFS logging. It integrates with mount authorization and NFS FOP authorization checks that cache successful host/file-handle decisions.

## Risks and Test Signals
Risks include the file's own FIXME around dangerous `entry_data` use, manual `GF_FREE(lookup_res)` on expiry instead of normal refcount release, potential stale authorization until TTL expiry after exports changes, host string normalization mismatches, and lock/refcount interaction during purge and lookup. Test signals include cache hit/miss/expiry cases, writeable versus read-only export checks, purge while lookups are active, exports reload invalidation behavior, and sanitizer or valgrind runs around expired-entry removal.
