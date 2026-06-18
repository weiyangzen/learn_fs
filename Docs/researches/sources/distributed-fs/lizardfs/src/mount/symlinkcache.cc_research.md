## sources/distributed-fs/lizardfs/src/mount/symlinkcache.cc

Purpose: implements a fixed-size in-memory symlink target cache keyed by inode.

Important APIs/state: `symlink_cache_init` allocates 6257 hash buckets, each with 16 slots; four multiplicative hash functions probe up to 64 candidate slots. `symlink_cache_insert` updates an existing inode or replaces the oldest candidate slot. `symlink_cache_search` checks expiration, returns cached path pointer on hit, and updates stats. `symlink_cache_term` frees paths and bucket storage.

Control flow: insertion and search are protected by `slcachelock`. Entries store inode, timestamp, and `strdup` path. `kCacheTimeInSeconds` controls expiry. Stats counters track inserts, hits, misses, and live links.

Dependencies and integration: used by symlink read path elsewhere in mount code; exports counters under `symlink_cache`.

Risks: returned path pointer is unlocked before return and can be invalidated by later cache mutation, so callers must copy or consume carefully. `symlink_cache_init` does not check malloc failure before `memset`. Expired entry accounting decrements link count on search cleanup only.

Test signals: insert/search hit, replacement policy, expiration, duplicate update, stats counters, and termination after many allocated paths.
