# sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.h

## Purpose
Declares the NFS authorization cache interface and cache container type.

## APIs, Types, and Functions
`struct auth_cache` contains `gf_lock_t lock`, `dict_t *cache_dict`, and `time_t ttl_sec`. The public API is `auth_cache_init()`, `cache_nfs_fh()`, `is_nfs_fh_cached_and_writeable()`, `is_nfs_fh_cached()`, and `auth_cache_purge()`.

## Control Flow, State, and Persistence
The header has no executable flow. It defines the state shared by cache implementation and users: an in-memory dictionary protected by a Gluster lock and governed by TTL. No on-disk persistence is implied.

## Dependencies and Integration
Depends on `nfs-mem-types.h`, `exports.h`, `<glusterfs/dict.h>`, and `nfs3.h`. It integrates with NFS server authorization paths that use `struct nfs3_fh`, host addresses, and parsed `struct export_item` objects.

## Risks and Test Signals
Risks include callers treating cache checks as authoritative after export configuration changes, passing unstable `host_addr` formatting, or using the cache without periodic purge/reload. Test signals are compile coverage for all cache users, write-permission checks through `is_nfs_fh_cached_and_writeable()`, and reload paths invoking `auth_cache_purge()`.
