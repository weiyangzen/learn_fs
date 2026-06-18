# Research: sources/distributed-fs/coda/coda-src/venus/venusvol.cc

## Purpose

`venusvol.cc` implements the Venus volume database and the core runtime behavior of `volent`, `reintvol`, `volrep`, and `repvol`. It is the main bridge between recovered volume metadata in RVM, live RPC connectivity, file-system object cache membership, modify-log ownership, reintegration/resolution scheduling, fid allocation, and user-visible volume status. The file turns communication events and VFS/CFS entry/exit calls into a controlled volume state machine with the states `Reachable`, `Unreachable`, and `Resolving`.

## Important APIs, Types, and Functions

- `VolInit()` and `VolInitPost()` restore or create the recovered `VDB`, reset transient fields, validate CML allocation counts, install local fake root/repair volumes, start the volume daemon, and later release the temporary references held during fsobj initialization.
- `VOL_HashFN()` hashes `Volid` keys by realm plus volume id for both recovered hash tables.
- `vdb::Find`, `vdb::Get`, `vdb::Create`, and `vdb::Put` implement lookup-by-id, lookup-by-name through `ViceGetVolumeInfo`, creation/reconfiguration of `volrep` and `repvol`, and reference release.
- `volent::Enter`, `volent::Exit`, `volent::TakeTransition`, `volent::Wait`, `volent::Signal`, `volent::Lock`, and `volent::UnLock` implement volume admission, state transitions, daemon wakeups, and pgid-scoped shared/exclusive volume locking.
- `volrep::DownMember`, `volrep::UpMember`, `repvol::DownMember`, and `repvol::UpMember` translate server connectivity changes into volume transition and demotion flags.
- `reintvol::SyncCache`, `reintvol::WriteDisconnect`, and `reintvol::ReportVolState` integrate CML reintegration configuration and state reporting.
- `volrep::GetConn`, `reintvol::GetConn`, and `repvol::GetMgrp` select direct server connections or VSG multicast groups, optionally flushing pending COP2 data for piggybacking.
- `reintvol::AllocFid`, `repvol::AllocFid`, `reintvol::GenerateLocalFid`, and `volent::GenerateFakeFid` allocate persistent or local/disconnected fids.
- `volent::GetVolStat` and `volent::SetVolStat` expose volume status locally or through single-server/multi-server Vice RPCs.
- Iterator classes at the end of the file provide reference-safe scans over recovered hash tables.

## Control Flow

Startup begins in `VolInit()`. If metadata is being initialized, it creates a new recovered `vdb`; otherwise it resets the recovered database's transient hash behavior. It scans all `volrep` and `repvol` entries, resets transient state, temporarily holds each volume until fsobjs are reset, checks that found CML entries match `AllocatedMLEs`, creates or reinstalls the local `CodaRoot` and `Repair` fake volumes, updates `rootfid`, flushes/truncates recovery state, and initializes the volume daemon.

Volume discovery flows through `vdb::Get`. A numeric id is resolved first by hash lookup and then by stringified volume id through the realm's admin connection. Name lookup splits `name@realm`, fetches a realm root volume name for cross-realm empty mount names, optionally derives a path from a mount fsobj, calls `ViceGetVolumeInfo`, handles timeout by returning an already known volume if possible, renames stale name mappings to fake volume-id names, and delegates to `Create`. `Create` either updates an existing name/VSG mapping or constructs `volrep`/`repvol` objects under recovery transactions.

The core request path enters `volent::Enter()`. It first handles pending demotion by clearing callbacks and demoting every fsobj in `fso_list`. It then takes pending transitions while no mutators, observers, or resolvers are active. If enabled, it may validate or fetch a volume callback/version stamp. Mutating entry waits for exclusive pgid locks, resolution, CML write locks, or pending transitions; for read/write volumes it also enforces one CML owner uid except for the ASR uid. Observing entry waits for resolution and pending transitions. Resolving entry is replicated-volume-only and waits for all active use plus shared locks to drain before taking the exclusive pgid lock.

`Exit()` reverses the admission accounting, releases the CML read lock for mutators, clears CML ownership when the last mutator leaves and the log is empty, reports volume state, and either takes a pending transition or signals waiters. `TakeTransition()` computes the next state from AVSG size and pending resolution list count. Reachable read/write volumes may synchronously or asynchronously trigger reintegration; resolving replicated volumes invoke `Resolve`; unreachable and reachable states signal sleepers.

Fid allocation first consumes preallocated ranges. If no range is available and the volume can create local fids, `GenerateLocalFid()` is used. Forced allocation on reachable volumes performs `ViceAllocFids` for non-replicated volumes or `OldViceAllocFids` through a chosen primary host for replicated volumes, persists the returned range, and consumes the first fid. Replicated forced allocation also flushes COP2 first because fid allocation is sent to one replica, not the whole VSG.

Status operations branch on local/unreachable/local-only versus connected. Local status fabricates a `VolumeStatus` from local volume fields and CML statistics. Replicated connected status marshals per-server arguments, calls `MRPC_MakeMulti`, collates with the `mgrpent`, chooses a dominant host result, and rewrites the returned vid/name to the replicated view. Non-replicated status calls the single-server Vice RPC. `SetVolStat` additionally creates a store id, supports COP2 piggybacking, collates the COP1 update set, clears piggybacked COP2 on success, and queues or sends COP2.

## State and Persistence Behavior

The database, volume entries, volume names, CMLs, fid ranges, `FidUnique`, and VSG membership pointers are recovered objects managed with `rvmlib_rec_malloc`, `RVMLIB_REC_OBJECT`, and `Recov_BeginTrans`/`Recov_EndTrans`. Transient fields include state, wait counters, active user counters, locks, callback status, server pointers, VSG objects, resolution and COP2 lists, fso lists, and per-run reintegration counters. Dirty shutdown discards unused preallocated fid ranges to avoid reusing fids that may have reached a server before a crash.

Reference counts are runtime-only and protect recovered volume objects from deletion while fsobjs, iterators, VSG parents, or startup initialization still reference them. Deletion is refused while CML entries or resolution/COP2 lists remain. The iterators hold the next returned volume and release the previous one as iteration advances, which is important because hash-table entries are recovered objects whose lifetime is tied to reference counts.

Volume state flags are deliberately split between persistent-ish policy/configuration and transient event flags. Communication events set `transition_pending`, `demotion_pending`, and replica `available`; `Enter`/`Exit` or the volume daemon consume those flags at stable points. CML ownership is stored in the `ClientModifyLog` and cleared only when no mutator, no log records, and no reintegration remain.

## Dependencies and Integration Points

This file depends on RPC2/Vice interfaces, RVM recovery helpers, `Realm` and `REALMDB`, server and connection management, VSG and `mgrpent` multi-RPC handling, fsobj cache objects, callback/version-vector code, mariner logging, volume daemon wakeups, and local fake volume definitions. It calls into `vol_reintegrate.cc` through `::Reintegrate`, `vol_resolve.cc` through `::Resolve`, CML methods for statistics and ownership, and `vol_COP2.cc` through `FlushCOP2`, `ClearCOP2`, and `COP2`. It is also invoked by VFS/CFS code for volume entry and by communication code for server up/down events.

## Risks and Edge Cases

- The volume admission protocol has many shared counters (`mutator_count`, `observer_count`, `resolver_count`, `shrd_count`, `excl_count`, `waiter_count`) and depends on every caller pairing `Enter` and `Exit` with the same mode. A missed exit can stall transitions and reintegration.
- `volent::Enter()` casts read/write volumes to `reintvol` and some mutating-exit code casts to `repvol` before checking `IsReadWrite`; this relies on layout and read/write-volume type discipline.
- VSG reconfiguration updates replica pointers and calls `Reconfigure()` while preserving refs. A missed `Put` or `hold` can leak or prematurely delete volume objects.
- `vdb::Get` handles timeouts by returning stale local mappings, which is necessary for disconnected use but can hide namespace changes until reconnection succeeds.
- `SetStagingServer()` creates local staging volume ids from a static counter and fakes a callback connection id; this is intentionally special-case behavior and can surprise code expecting normal server/realm semantics.
- COP2 flushing before single-replica fid allocation is best-effort; failure is ignored because fid allocation correctness does not depend on COP2, but stale COP2 queues can still affect later consistency signaling.
- Local/unreachable `GetVolStat` has no authoritative quota or server message data and returns fabricated in-service/blessed fields.

## Test Signals

Useful tests and runtime checks should cover startup recovery after clean and dirty shutdown, CML allocation-count mismatches, cross-realm root volume lookup, volume-name remapping after VLDB changes, disconnected `vdb::Get` fallback, server up/down transitions, demotion of cached fsobjs, mutator ownership contention across uids, ASR entry while a user owns the CML, synchronous reintegration through `SyncCache`, forced and local fid allocation, replicated and non-replicated `GetVolStat`/`SetVolStat`, VSG reconfiguration, staging server selection, iterator reference handling, and deletion refusal when CML/resolution/COP2 state remains. Existing `CODA_ASSERT`, `CHOKE`, `VOL_ASSERT`, log messages, and mariner state reports are major diagnostic signals.
