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
