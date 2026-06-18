## sources/distributed-fs/lizardfs/src/mount/symlinkcache.h

Purpose: declares the symlink cache API.

Important APIs: `symlink_cache_insert(inode, path)`, `symlink_cache_search(inode, &path)` returning int hit/miss, `symlink_cache_init(cache_time = 3600)`, and `symlink_cache_term`.

State and integration: the returned `path` points to cache-owned memory; the cache is global and must be initialized before use.

Risks and tests: lifetime of returned path is not encoded in the API. Tests should copy the result immediately and verify behavior before/after termination.
