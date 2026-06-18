# sources/distributed-fs/openafs/src/afs/afs_osidnlc.c

## Purpose
`afs_osidnlc.c` implements the OSI directory name lookup cache, an in-memory name-to-vcache cache for frequently accessed directory entries. It avoids repeated disk-cache directory scans for short names.

## Important APIs, types, and functions
Global state includes `afs_xdnlc`, `dnlcstats`, `ncfreelist`, fixed `nameCache[NCSIZE]`, `nameHash[NHSIZE]`, `afs_usednlc`, and debug trace arrays. Public functions are `osi_dnlc_enter`, `osi_dnlc_lookup`, `osi_dnlc_remove`, `osi_dnlc_purgedp`, `osi_dnlc_purgevp`, `osi_dnlc_purge`, `osi_dnlc_purgevol`, `osi_dnlc_init`, and `osi_dnlc_shutdown`. Internal helpers are `GetMeAnEntry`, `InsertEntry`, and `RemoveEntry`.

## Control flow
`osi_dnlc_init` initializes the lock, stats, hash table, fixed cache array, and freelist. `osi_dnlc_enter` hashes a short name, rejects names too long for `AFSNCNAMESIZE`, verifies the directory vcache is statted and still at the directory data version used for lookup, de-duplicates an existing entry if present, otherwise obtains an entry from the freelist or scavenges the oldest entry from a hash bucket, fills `dirp`, `vp`, key, and name, and inserts it at the bucket head.

`osi_dnlc_lookup` hashes the name, searches the bucket under DNLC and vcache read locks, rejects initializing/dead vcaches, obtains a vnode/vcache reference with Darwin or generic APIs, removes entries that fail to ref, and returns the held vcache. Remove and purge functions null matching entries first and opportunistically unlink them under a nonblocking write lock, falling back to eventual scavenging when busy.

## State and persistence behavior
The cache is fixed-size and volatile. Each `struct nc` stores key, circular hash links, directory vcache, target vcache, and short name. Stats count enters, lookups, misses, removes, purge types, cycles, and lookup races.

## Dependencies and integration points
It depends on vcache locks (`afs_xvcache`), vcache state flags, vnode reference APIs, Darwin name cache purge calls, AFS locks, and `afs_osidnlc.h`. Lookup, directory update, callback invalidation, and volume purge paths use it to cache or invalidate name mappings.

## Risks and edge cases
Long names are not cached. Hash buckets are circular lists; cycle detection warns, increments stats, and purges the whole cache. Nonblocking removal can leave invalidated entries in buckets with null pointers until scavenged. Entry validity depends on matching the directory data version at insertion, so stale directory data should not be cached. Linux disables this cache by default in this file.

## Test signals
Test enter/lookup hit/miss behavior, long-name rejection, duplicate update, stale directory version rejection, ref-acquisition failure removal, purgedp/purgevp/purgevol invalidation, full-cache scavenging, cycle recovery, and Darwin cache-purge integration.
