# sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.h

## Purpose
`io-cache.h` declares the in-memory Dokany-context-to-OrangeFS-object cache used by the Windows client service read/write path.

## Important APIs, Types, And Functions
It defines result constants `IO_CACHE_HIT` and `IO_CACHE_MISS`, update constants `IO_CACHE_NO_UPDATE` and `IO_CACHE_UPDATE`, and `struct io_cache_entry` with quickhash linkage, `ULONG64 context`, `PVFS_object_ref object_ref`, `enum PVFS_io_type io_type`, and `update_flag`. It declares compare/add/remove/get functions.

## Control Flow
Callers add a context after resolving a path and performing successful IO, retrieve it on later IO, and remove it when the context is no longer valid. The header does not define initialization; the service initializes the qhash and mutex in `service-main.c`.

## State And Persistence
The declared structure is process-local cache state only. It persists for service lifetime or until explicit removal, not across restarts.

## Dependencies And Integration Points
It includes Windows, OrangeFS, and `quickhash.h`. It is consumed by `io-cache.c`, initialized by `service-main.c`, and used by `dokany-interface.c`.

## Risks And Test Signals
The cache key is a Dokany context id, so context uniqueness and cleanup are critical. There is no generation counter or mount id in the key. Tests that stress read/write performance can reveal functional misses but not subtle stale-entry races.
