# sources/distributed-fs/ceph-client/fs/cachefiles/interface.c

## Purpose
`interface.c` implements the FS-Cache cache-ops interface for CacheFiles cookies. It allocates backing objects, maps FS-Cache cookies to local files, handles resize/invalidation/withdrawal, and exposes the `cachefiles_cache_ops` vtable to FS-Cache.

## Important APIs, Types, and Functions
Important functions include `cachefiles_alloc_object`, `cachefiles_see_object`, `cachefiles_grab_object`, `cachefiles_put_object`, `cachefiles_adjust_size`, `cachefiles_lookup_cookie`, `cachefiles_shorten_object`, `cachefiles_resize_cookie`, `cachefiles_commit_object`, `cachefiles_clean_up_object`, `cachefiles_withdraw_cookie`, and `cachefiles_invalidate_cookie`. The exported integration object is `const struct fscache_cache_ops cachefiles_cache_ops`.

## Control Flow
Lookup allocates a `cachefiles_object`, optionally initializes on-demand metadata, cooks the cookie key into a backing filename, stores the object in `cookie->cache_priv`, enters cache credentials, and calls `cachefiles_look_up_object`. Successful lookup links the object to the cache list and adjusts backing file size to a direct-I/O block multiple. Resize shrinks by truncating and zeroing DIO padding, while growth only updates the cookie size. Withdrawal removes the object from active lists, sends on-demand close/cleanup, commits xattrs or deletes retired objects, unmarks the inode, drops the file, clears `cookie->cache_priv`, and releases the object reference. Invalidation swaps in a new tmpfile, marks content absent, resumes FS-Cache invalidation, then buries the old file if needed.

## State and Persistence Behavior
Runtime state is `struct cachefiles_object`: cookie, volume, active-list link, backing `struct file`, cooked name, debug ID, refcount, content state, tmpfile flag, and optional on-demand state. Persistent state is updated through backing file truncation, xattr writes, tmpfile linking, and old object removal. Cookie flags such as `FSCACHE_COOKIE_LOCAL_WRITE`, `NEEDS_UPDATE`, `RETIRED`, `NO_DATA_TO_READ`, and `HAVE_DATA` drive persistence decisions.

## Dependencies and Integration Points
This file is the FS-Cache entry point into CacheFiles. It depends on object-name cooking, VFS namei helpers, xattr coherency helpers, netfs operation begin/end from `io.c`, on-demand helpers, volume state, and fscache reference/access APIs.

## Risks and Edge Cases
Object reference counts and `cookie->cache_priv` lifetime are critical. Failed lookup leaves an allocated object attached until FS-Cache drops its access count. Invalidation must atomically swap the file under `object->lock` so new I/O targets the tmpfile. Size adjustment must preserve DIO alignment without accidentally exposing padding as real object data. Xattr update failure can leave stale or dirty cache objects.

## Test Signals
Test lookup of new, existing, stale, and weird objects; object size shrink/grow paths; invalidation while I/O is active; retired cookie deletion; local-write xattr commits; failed tmpfile creation; and reference leak detection through tracepoints and slab/KASAN.
