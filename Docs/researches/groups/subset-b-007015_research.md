# Research Group: subset-b-007015

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusvol.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusvol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusvol.h -->
# Research: sources/distributed-fs/coda/coda-src/venus/venusvol.h

## Purpose

`venusvol.h` declares the Venus volume abstraction and its related persistent and transient data structures. It defines the recovered volume database, client modify log, modify-log entries, read/write reintegration base volume, non-replicated replicas, replicated volumes, COP2 queue entries, resolution queue entries, iterators, global knobs, and the public entry points used by Venus startup, VFS/CFS operations, communication events, reintegration, resolution, repair, and callbacks.

## Important APIs, Types, and Functions

- Constants and flags include `VDB`, magic numbers, CML/MLE limits, `UNSET_TID`, reintegration default sentinel values, `VM_MUTATING`, `VM_OBSERVING`, `VM_RESOLVING`, `VM_NDELAY`, and `NO_ASR`.
- `cmlstats` accumulates counts and byte sizes for store and non-store CML records, including cancelled records.
- `ClientModifyLog` is a persistent per-volume log of disconnected/partitioned mutations. It exposes optimization, COP1 packing, reintegration, cancellation, checkpoint, repair, statistics, and fid-binding APIs.
- `CmlFlags` stores per-CML-entry repair/freeze/failure/commit/prepend state.
- `cmlent` is the persistent record for one logged mutation. Its union covers store, truncate, utimes, chown, chmod, create, remove, link, rename, mkdir, rmdir, symlink, and repair operations, with fids, names, lengths, modes, version vectors, and partial-reintegration handles.
- `cml_iterator` iterates CML entries in commit or abort order and can filter by fid or start after a prelude entry.
- `vdb` owns recovered hash tables for replicated volumes and replicas plus the MLE free list. Its public API provides lookup, reference release, communication event propagation, write-disconnect configuration, cache synchronization, CML statistics, callback breaks, transition processing, printing, and cache listing.
- `VolFlags` packs replicated/readonly/available state, transition/demotion flags, ASR flags, reintegration/repair/resolve flags, callback/reintegration conflict hints, and authentication hints.
- `FidRange` tracks preallocated fid ranges by vnode, unique, stride, and count.
- `volent` is the common base class for all volume entries, with synchronization/admission, status, utility, fake-fid, fake-object, printing, and cache-list APIs.
- `reintvol` extends `volent` with fid ranges, a `ClientModifyLog`, CML lock, reintegration limits/counters, callback state, VVV stamp, reintegration APIs, ASR APIs, fid allocation, connection selection, mutation logging, CML repair operations, and callback validation.
- `volrep` represents one server-hosted volume replica with host/server state and read-only/read-write-replica metadata.
- `repvol` represents a replicated volume composed of up to `VSG_MEMBERS` `volrep`s, a VSG manager, optional read-only staging replica, resolution list, COP2 list, allocation/repair/resolution/COP2/callback APIs, and multi-RPC collation helpers.
- Iterator classes scan recovered volume hash tables by type.
- `cop2ent` and `resent` define queue elements for deferred COP2 update propagation and pending resolution requests.

## Control Flow Exposed by the Header

The header describes a layered flow. Venus startup calls `VolInit()` and `VolInitPost()` to restore the volume database. VFS operations call `volent::Enter()` with a mode and uid, perform fsobj/CFS work, and call `Exit()`. CFS and reintegration code use `reintvol::GetConn()`, `repvol::GetMgrp()`, the `Collate_*` helpers, and the `Log*` methods. Reintegration packs records through `ClientModifyLog::COP1()` or incremental repair methods, commits or aborts entries, may allocate server fids, and then uses COP2 routines on `repvol` to distribute update sets. Communication code calls `vdb::DownEvent()` and `vdb::UpEvent()`, which lead to per-volume transitions. Resolution code queues `resent` objects with `ResSubmit()` and drains them through `Resolve()` and `ResAwait()`.

The class hierarchy also encodes which behavior is valid on which volume. `volent` covers common entry/status/cache functionality; `reintvol` is the read/write-capable layer with CML and reintegration; `volrep` is a concrete non-replicated or replica volume; `repvol` is a concrete replicated volume with VSG, resolution, and COP2 semantics.

## State and Persistence Behavior

Several declarations are explicitly marked persistent. `ClientModifyLog`, `cmlent`, `vdb`, `volent` subobjects, volume names, fid ranges, CML entries, CML flags, version vectors, and recovered hash/list links are stored in RVM and require transactions for mutation. Members annotated with `/*T*/` are transient and must be rebuilt after restart, such as owner-derived counters, locks, active-user counts, fso lists, server pointers, VSG handles, callback status, resolution/COP2 lists, and reintegration counters. The method annotations (`REQUIRES_TRANSACTION`, `EXCLUDES_TRANSACTION`, `TRANSACTION_OPTIONAL`) document important transaction boundaries.

The CML is central persistence. It stores owner, entry counts, high-water metrics, byte counts, cancellation policy, cancelled statistics, and a recovered list of `cmlent` records. Each `cmlent` stores the operation identity, affected fids/names/version vectors, local repair metadata, and transient dependency/fid-binding lists that can be rebuilt. `FidRange` and `FidUnique` persist fid allocation progress so disconnected and preallocated fids remain unique across restarts, except when implementation code discards unused preallocated ranges after a dirty shutdown.

## Dependencies and Integration Points

The header pulls in RPC2, Vice, callback and directory interfaces, utility list/hash containers, volume definitions, communication state, recovery APIs, realm database, private Venus globals, and VSG support. It exposes integration hooks for `vol_daemon.cc`, `vol_reintegrate.cc`, `vol_resolve.cc`, `vol_cml.cc`, repair code, fsobj code, user and vproc code, callback fetch handling, and local-realm fake volumes. The macro `VOL_ASSERT` integrates volume dumps with fatal assertions, and `PRINT_*` macros standardize diagnostics across implementation files.

## Risks and Edge Cases

- The header exposes many friend relationships, so invariants are spread across CML, fsobj, repair, reintegration, and volume implementation files rather than being encapsulated in one class.
- Persistent and transient fields are interleaved. Missing a transient reset after recovery or incorrectly wrapping a persistent mutation in a transaction can corrupt recovered state.
- Bit-packed `VolFlags` and `CmlFlags` are compact but make compatibility and initialization errors subtle.
- `cmlent` uses a large discriminated union keyed by `opcode`; every pack, print, commit, cancel, repair, and fid-translation path must keep the opcode-specific fields in sync.
- Multiple `GetConn` overloads, `Collate_*` variants, and volume type predicates must be used consistently to avoid treating a non-replicated volume as a replicated one or vice versa.
- Constants such as `COP2SIZE`, `VSG_MEMBERS`, and CML limits define buffer and batching contracts shared with implementation files; changing them has cross-file effects.

## Test Signals

Header-level validation should focus on compile coverage of all class declarations and friend users, transaction annotation consistency, recovered layout compatibility, CML record construction for every opcode, iterator behavior for all volume categories, ASR and repair flag transitions, `VolFlags` initialization, and cross-file callers of `Log*`, `COP2`, `Resolve`, `GetVolStat`, `AllocFid`, and `GetMgrp`. Runtime diagnostics include `VOL_ASSERT`, CML print/list output, volume print output, and counters for MLEs, callbacks, CML bytes, and reintegration outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusvol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_COP2.cc -->
# Research: sources/distributed-fs/coda/coda-src/venus/vol_COP2.cc

## Purpose

`vol_COP2.cc` implements the Venus COP2 facility for replicated volumes. After a mutating COP1 operation produces a `ViceStoreId` and `ViceVersionVector` update set, this code distributes that update set to the AVSG. It supports immediate synchronous COP2 RPCs, deferred asynchronous RPCs from the volume daemon, and piggybacked COP2 data on later worker RPCs. Update propagation is intentionally idempotent, and multiple pending update sets can be batched into one `RPC2_CountedBS` buffer.

## Important APIs, Types, and Functions

- `COP2EntrySize` is the serialized size of one `ViceStoreId` plus one `ViceVersionVector`.
- `repvol::COP2(mgrpent *, RPC2_CountedBS *)` sends an already packed buffer to all VSG members through `MRPC_MakeMulti(ViceCOP2_OP)` and clears matching queued entries on success.
- `repvol::COP2(mgrpent *, ViceStoreId *, ViceVersionVector *, int donotpiggy)` either queues the entry for piggybacking or packs and sends a one-entry buffer immediately.
- `repvol::FlushCOP2(time_t window)` is the volume-daemon/direct-flush path. It sends oldest entries when they are old enough, filling buffers with younger entries as capacity allows.
- `repvol::FlushCOP2(mgrpent *, RPC2_CountedBS *)` is the piggyback preparation path. It directly sends all but the final buffer-full and copies the remaining entries into the caller's piggyback buffer.
- `repvol::GetCOP2()` serializes pending entries in FIFO order without removing them.
- `repvol::FindCOP2()` locates a queued entry by store id.
- `repvol::AddCOP2()` appends a new queue entry.
- `repvol::ClearCOP2(RPC2_CountedBS *)` parses a sent buffer, removes matching queued entries, deletes them, and resets the buffer length.
- `repvol::ClearCOP2()` drains the whole queue.
- `cop2ent` stores one pending `sid`, `updateset`, and enqueue time and has a small free-list-backed allocator.

## Control Flow

When a mutating replicated operation finishes COP1, callers invoke the single-entry `COP2` overload. If piggybacking is enabled and the caller did not force direct sending, `AddCOP2()` appends a `cop2ent` and returns success. Otherwise the method serializes the store id with `htonsid`, serializes the update vector with `htonvv`, and delegates to the buffer-sending `COP2` overload.

The buffer-sending `COP2` overload assumes a replicated volume and an existing `mgrpent`. It performs `MRPC_MakeMulti` with `ViceCOP2_OP`, collates via `Collate_COP2`, records multi-RPC stats, and calls `ClearCOP2(PiggyBS)` only when the multi-RPC succeeded. This means failed sends leave queue entries intact for future retry.

Daemon flushing starts at the head of `cop2_list`, which is maintained FIFO. If the list is empty or the oldest entry is younger than `window`, the flush returns. Otherwise it obtains an mgroup as `V_UID`, calls `GetCOP2()` to fill a local buffer up to `COP2SIZE`, sends it with `COP2`, releases the mgroup, and repeats from the list head until no eligible entries remain or a send/acquire error occurs. The code explicitly tolerates concurrent flushing: entries may disappear while `GetMgrp()` yields, so a zero-length buffer after mgroup acquisition is logged and stops the loop.

Piggyback flushing is used when a caller already has an mgroup for a normal VSG RPC. While the queued data exceeds one COP2 buffer, it sends full buffers directly. If the remaining queue fits in one buffer, it serializes those entries into the caller's `PiggyBS` so the caller can attach them to the normal RPC. The entries are not removed until the caller later calls `ClearCOP2()` after the piggybacked RPC succeeds.

## State and Persistence Behavior

`cop2_list` itself is a transient `dlist` owned by `repvol` and initialized in `repvol::ResetTransient()`. `cop2ent` objects are heap allocated, not RVM recovered. Pending COP2 updates therefore represent runtime delivery work rather than durable state in this file; durable mutation/reintegration state lives in the CML and is what can regenerate or require update propagation after recovery. Each entry records enqueue time through `Vtime()` for daemon window decisions.

`GetCOP2()` is non-destructive and network-byte-order serializing. `ClearCOP2()` is destructive only for entries whose store ids appear in the supplied buffer. This split is what makes direct-send retry and piggyback retry safe: the queue is cleared only after a successful RPC path calls back into clear logic. `ClearCOP2(void)` is used when a replicated volume is being destroyed and any remaining transient queue entries must be dropped.

The allocator keeps up to `MaxFreeCOP2ents` deleted entries on a process-local free list. Allocation zeroes memory only when obtaining fresh storage from `new char[len]`; reused entries are overwritten by the constructor fields that matter.

## Dependencies and Integration Points

The implementation depends on RPC2, Vice `ViceCOP2`, `mgrpent` multi-RPC connection state, `repvol::Collate_COP2()` from `venusvol.cc`, mariner/RPC statistics logging, `PIGGYCOP2`/COP mode globals from communication configuration, byte-order helpers from `nettohost.h`, and the `cop2ent`/`repvol` declarations in `venusvol.h`. Callers include connected CFS mutation paths, volume-status mutation, CML reintegration commit paths, repair code that forces non-piggybacked COP2, replicated fid allocation that best-effort flushes first, resolution/repair paths that require a clean COP2 queue, and `vol_daemon.cc` periodic flushing.

## Risks and Edge Cases

- The COP2 queue is transient. If callers assume queue persistence across process restart, update propagation can be lost unless higher-level CML/reintegration recovery recreates the need.
- `FlushCOP2(time_t window)` compares the oldest entry age and stops if it is younger than the window, so younger entries behind it are never sent alone. This preserves FIFO behavior but delays newer updates.
- `GetCOP2()` serializes from the list head each time without marking entries in flight. Concurrent flushers can send overlapping buffers, which is acceptable only because COP2 propagation is idempotent.
- `ClearCOP2()` silently ignores store ids that are no longer present. That matches concurrent/idempotent semantics but can hide unexpected duplicate or stale buffer contents.
- Buffer-size correctness depends on every packed buffer length being a multiple of `COP2EntrySize`; malformed buffers trigger `CHOKE`.
- The free-list allocator is not visibly locked in this file. It assumes Venus's scheduling/concurrency model is sufficient or that calls are serialized at a higher level.
- The debug print for `cop2ent` does not print the version vector contents even though logging in `GetCOP2()` does, limiting postmortem visibility from object dumps.

## Test Signals

Useful tests should exercise immediate COP2, piggyback queueing, daemon flushing with zero and nonzero windows, piggyback flushing when the queue is larger than `COP2SIZE`, successful clear after direct and piggybacked sends, failed sends leaving entries queued, malformed buffer length handling, duplicate/concurrent clear behavior, `FindCOP2` matching on both store-id fields, FIFO serialization order, free-list reuse bounds, and integration with callers that invoke `ClearCOP2(&PiggyBS)` after successful normal VSG RPCs. Runtime signals include `MULTI_RECORD_STATS(ViceCOP2_OP)`, mariner `store::COP2` logs, `LOG` lines for flush/no-entry cases, and fatal `CHOKE` paths for internal contract violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_COP2.cc -->
