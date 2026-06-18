# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.c

## Purpose

`cm_volume.c` implements the Windows OpenAFS cache manager's volume table. It maps volume names and IDs to cached `cm_volume_t` objects, refreshes location data from VLDB servers, tracks RW/RO/backup server lists and availability state, recycles volume objects through an LRU, validates persisted cache metadata, and drives status notifications for volume online/offline/busy/down transitions.

## Important APIs, Types, and Functions

The main public entry points are `cm_InitVolume()`, `cm_ShutdownVolume()`, `cm_FindVolumeByName()`, `cm_FindVolumeByID()`, `cm_FindVolumeByFID()`, `cm_GetVolumeByFID()`, `cm_GetVolServers()`, `cm_ForceUpdateVolume()`, `cm_RefreshVolumes()`, `cm_CheckOfflineVolumes()`, `cm_UpdateVolumeStatus()`, `cm_VolumeRenewROCallbacks()`, hash/LRU helpers, and volume-state lookup helpers. `cm_UpdateVolumeLocation()` is the central refresh routine. It calls `VL_GetEntryByNameU`, then falls back to `N` and old `O` VLDB forms, expands UUID/multihomed server entries through `cm_GetAddrsU()`, installs file-server refs, and updates all three per-volume states.

## Control Flow

Lookup first searches global name or ID hash tables under `cm_volumeLock`. If a name lookup misses and creation is allowed, it either allocates a new slot from `cm_data.volumeBaseAddress` or recycles an unreferenced LRU object after removing it from name and ID hashes. The candidate is initialized, reference-counted, made visible in the name hash, then refreshed under the per-volume write lock unless `CM_GETVOL_FLAG_NO_RESET` suppresses it.

Refresh is serialized with `CM_VOLUMEFLAG_UPDATING_VL`; contending threads sleep on `volp->flags` and reuse the completed result. The code avoids repeated VLDB storms with 60-second retry throttling and a 10-minute negative-cache window for nonexistent volumes. Successful VLDB data is normalized to the base volume name, inserted into RW/RO/BK ID hashes, converted to server-ref lists, randomized for replicated RO access, and mapped to `vl_online` or `vl_alldown`. Failure maps no-such-volume into `CM_VOLUMEFLAG_NOEXIST`; other failures mark all variants down.

Offline checks run from daemon context over the LRU. They reset busy/offline server-ref states, optionally force a VLDB refresh, issue `RXAFS_GetVolumeStatus()` against a root fid, cache RO size when available, and move volume state back online when a server reports an online volume. Status recalculation counts server refs as down, busy, offline, deleted, or usable and emits notifications on transitions.

## State and Persistence Behavior

Volume objects live in `cm_data` shared cache memory and are revalidated on restart with pointer range and magic checks. Persistent-ish fields include the all-volume list, hash chains, LRU queue, base name, cell pointer, per-type IDs, dotdot fids, flags, callback metadata, and RO size. Server-ref lists are live references into the server table and are freed/rebuilt on every successful VLDB refresh. The file does not persist VLDB state itself; it caches remote volume-location state and invalidates it by flags, lifetime, VNOVOL/VMOVED force-refresh, mixed RO-release polling, and shutdown.

## Dependencies and Integration Points

The module depends on cache-manager globals in `cm_data`, `cm_cell_t`, `cm_serverRef_t`, `cm_server_t`, Rx/VLDB RPCs, multihomed address resolution, server ranking/randomization, `cm_Analyze()` retry logic, callback/scache APIs, Windows synchronization and interlocked operations, and volume-status notification hooks. File operations consume it through `cm_GetServerList()`, `cm_ConnFromVolume()`, mount-root generation changes, and VNOVOL/VMOVED handling.

## Risks and Edge Cases

Concurrency is delicate: global hash/LRU state and per-volume state use different locks, and `cm_UpdateVolumeLocation()` intentionally drops the volume lock during RPCs. Recycling must remove every old hash and server-list reference before exposing a reused object. Numeric volume names, `.readonly` fallback, renamed volumes looked up by ID, linked cells, fake freelance root volumes, old VLDB opcodes, UUID mismatch logging, mixed RO releases, all-deleted refs, and negative-cache throttling are all special cases. There is a suspicious `if (code = 0)` assignment in the offline status path that would suppress the status RPC block.

## Test Signals

Good tests include name and ID lookup, LRU recycling under max-volume pressure, restart validation, concurrent refresh waiters, VLDB U/N/O fallback, multihomed UUID expansion, `.readonly` lookup when the base name is absent, rename recovery by ID, linked-cell fallback, RO replica randomization, server-rank change reorder, negative-cache expiration, mixed RO-release refresh every five minutes, VNOVOL/VMOVED forced refresh, offline/busy/down transitions, RO callback renewal, and shutdown notification/reset behavior.
