# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.h

## Purpose

`cm_volume.h` defines the Windows cache manager volume object contract. It declares the in-memory structures, flags, hash macros, and APIs used by cache-manager lookup, server selection, refresh, validation, status notification, and RO callback renewal code.

## Important APIs, Types, and Functions

`cm_vol_state_t` represents one RW, RO, or backup volume variant. It carries the volume ID, root parent fid, server-ref list, `enum volstatus`, per-state flags, and hash-chain metadata. `cm_volume_t` is the owning volume group object with LRU/all/name queues, cell binding, base name, three `vol[]` states, per-volume RW lock, reset/update/noexist/DFS/mixed flags, interlocked reference count, RO callback metadata, last VLDB update time, and cached RO size. The header exposes lookup APIs (`cm_FindVolumeByName()`, `cm_FindVolumeByID()`, `cm_FindVolumeByFID()`, `cm_GetVolumeByFID()`), lifecycle APIs, refresh/status APIs, hash/LRU helpers, and state/type helpers.

## Control Flow

Callers generally find or create a held `cm_volume_t`, optionally causing a VLDB refresh unless `CM_GETVOL_FLAG_NO_RESET` is set. Server-selection code calls `cm_GetVolServers()` or `cm_ChecksumVolumeServerList()` and later frees returned server lists. Daemon and error paths use `cm_RefreshVolumes()`, `cm_ForceUpdateVolume()`, `cm_CheckOfflineVolumes()`, and `cm_UpdateVolumeStatus()` to mark cached entries stale or recompute availability.

## State and Persistence Behavior

The declared fields are stored in the cache manager's shared `cm_data` arena and can survive process restart depending on cache-file mode. The magic number and validation API support sanity checking that persisted pointers still point into expected arenas. Flags split between per-volume metadata (`CM_VOLUMEFLAG_*`) and queue/hash membership (`CM_VOLUME_QFLAG_*`) so object lifetime and refresh state can be tracked separately.

## Dependencies and Integration Points

The header depends on `opr/jhash.h`, fid, cell, server, user, and request types from the cache manager, plus `enum volstatus` and RW/RO/BK constants from surrounding OpenAFS headers. It is consumed by volume, scache, callback, server-list, pioctl, and diagnostic paths.

## Risks and Edge Cases

Hash macros rely on `cm_data.volumeHashTableSize` being initialized and power/size-compatible with the ID mask expression. Lock annotations in comments matter: `serversp` belongs with `cm_serverLock`, `vol[]` and `flags` with the volume RW lock, and queue/hash metadata with `cm_volumeLock`. Any future field change must preserve restart validation and interlocked reference-count assumptions.

## Test Signals

Compile-time tests should catch prototype drift. Runtime tests should exercise all public lookup modes, per-type state selection by ID/name/type, hash insertion/removal, LRU movement/removal, replicated flag reporting, status transitions, and validation after cache reuse or restart.
