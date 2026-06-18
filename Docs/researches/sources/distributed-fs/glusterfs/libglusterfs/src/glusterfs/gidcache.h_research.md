# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gidcache.h

## Purpose
Defines a fixed-size auxiliary group-ID cache keyed by identifiers for uid/gid resolution, reducing repeated group lookup cost in busy systems.

## APIs, Types, and Functions
The cache is 4-way associative with 256 buckets, for `AUX_GID_CACHE_SIZE` of 1024 entries. `gid_list_t` stores lookup id, uid, gid, group count, allocated gid list, and expiration deadline. `gid_cache_t` stores a lock, max age, bucket count, and the fixed entry array. APIs are `gid_cache_init()`, `gid_cache_reconf()`, `gid_cache_lookup()`, `gid_cache_release()`, and `gid_cache_add()`.

## Control Flow, State, and Persistence
The cache is in-memory and time-bounded. Lookups search a bucket set under lock, return a const `gid_list_t`, and require `gid_cache_release()` by callers. Reconfiguration changes maximum age. Adds replace or populate entries and set deadlines.

## Dependencies and Integration
Depends on `glusterfs.h`, `locking.h`, `gid_t`, and `time_t`. It integrates with credential resolution, FUSE/server request authentication, and `cmd_args_t` gid timeout configuration.

## Risks and Test Signals
Risks include stale group membership until deadline, fixed-size collision pressure, ownership of `gl_list`, caller failure to release, and races during reconfiguration. Test signals include hit/miss/expiry tests, collision replacement tests, reconf timeout tests, concurrent lookup/add stress, and credential-auth integration checks.
