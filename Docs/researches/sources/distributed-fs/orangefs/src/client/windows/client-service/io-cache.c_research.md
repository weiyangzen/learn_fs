# sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.c

## Purpose
`io-cache.c` implements a small qhash-backed cache from Dokany file contexts to OrangeFS object refs so read/write callbacks can avoid repeated path lookup.

## Important APIs, Types, And Functions
The file defines external globals `io_cache` and `io_cache_mutex`, and implements `io_cache_compare`, `io_cache_add`, `io_cache_remove`, and `io_cache_get`. Entries are `struct io_cache_entry` from `io-cache.h`, containing context, `PVFS_object_ref`, IO type, and update flag.

## Control Flow
`io_cache_add` searches for an existing context. If present, it updates `io_type` when needed and returns. On miss, it allocates and initializes an entry and inserts it into `io_cache`. `io_cache_get` searches by context, copies the object ref/type/update flag into caller outputs, and returns `IO_CACHE_HIT` or `IO_CACHE_MISS`. `io_cache_remove` removes and frees the entry.

## State And Persistence
State is entirely in-memory and scoped to the service process. Entries should correspond to active Dokany contexts. Persistent filesystem data is not stored here; the cache only accelerates lookup.

## Dependencies And Integration Points
It depends on `gen-locks`, `gossip`, `client-service.h`, `io-cache.h`, OrangeFS types, and quickhash. `dokany-interface.c` uses this cache in `PVFS_Dokan_read_file` and `PVFS_Dokan_write_file`.

## Risks And Test Signals
The search and insert/remove operations are mutex-protected, but `io_cache_add` mutates an existing entry after releasing the mutex, and `io_cache_get` copies after releasing the mutex. That can race with remove or another update under heavy concurrent IO. There is no automatic removal shown in `PVFS_Dokan_close_file`, so lifetime depends on callers remembering to remove entries; otherwise stale object refs may accumulate. IO tests and multi-threaded file creation provide some signal but do not directly verify cache correctness or races.
