# sources/distributed-fs/ceph/src/mds/Locker.h

## Purpose

`Locker.h` declares the CephFS MDS `Locker` class and its public contract for metadata lock coordination, client capability management, lock caching, scatter/file lock evaluation, local locks, file max-size sharing, and client leases. It is the interface used by request execution, MDCache, migration/recovery code, and message dispatch to coordinate distributed metadata consistency.

## Important APIs, Types, and Functions

The header forward declares major collaborators (`MDSRank`, `MDCache`, `CInode`, `CDentry`, `CDir`, `SimpleLock`, `ScatterLock`, `LocalLockC`, `Capability`, sessions, cap and lease messages) and defines mempool-aware aliases for inode and xattr data. `Locker(MDSRank*, MDCache*)` binds the locker to one MDS rank and its cache.

Public APIs group into message dispatch (`dispatch`, `handle_lock`, `tick`), acquisition/drop (`acquire_locks`, `try_rdlock_snap_layout`, `cancel_locking`, `drop_locks`, `drop_non_rdlocks`, `handle_locks_for_early_reply`, `drop_lock`), remote cleanup (`request_drop_remote_locks`, `request_drop_non_rdlocks`, `request_drop_locks`), lock cache (`create_lock_cache`, `find_and_attach_lock_cache`, invalidate/eval/put helpers), evaluation (`eval_gather`, `eval`, `eval_any`, `try_eval`, `eval_cap_gather`, `eval_scatter_gathers`), lock primitives, cap handling, local locks, file lock handling, file IO caps/max-size, and lease handling.

Protected APIs declare the implementation-only state-machine handlers: sending `MLock`, `_drop_locks`, simple/scatter/file handlers, client-cap internals, local lock finishers, `file_update_finish`, xattr decoding, and quiesce failure handling. Private friend classes are completion contexts used by asynchronous journal, waiter, and retry callbacks.

## Control Flow and Data Flow

Callers build lock operation vectors and pass them to `acquire_locks`; on success, the mutation owns lock references and auth pins until a drop helper releases them. Callers that receive messages invoke `dispatch`, which routes to the protected message-specific handlers implemented in `Locker.cc`. Periodic MDS ticks invoke `tick`, allowing scatter and cap queues to make progress.

Capability data flows through `issue_new_caps`, `issue_caps`, cap release/update handlers, stale-cap helpers, and max-size helpers. Lock state data flows through `eval_any` and the primitive lock functions, with `eval_any` choosing gather evaluation for unstable locks and normal evaluation for stable auth locks.

## State and Persistence Behavior

The header exposes state containers owned by `Locker`: `updated_scatterlocks`, `updated_filelocks`, global and per-client `revoking_caps` lists, and `need_snapflush_inodes`. These are in-memory queues that drive later lock writeback, cap revocation warnings, and snapflush retries. Durable changes are performed by methods declared here but implemented through journal events in `Locker.cc`.

The class stores raw pointers to `MDSRank` and `MDCache`; the `Locker` lifetime is tied to the MDS rank. Friend context classes use these pointers to resume operations after waiters or log commits.

## Dependencies and Integration Points

`Locker.h` depends on Ceph common types, mempool allocation, `mdstypes`, `Mutation`, and `SimpleLock`. It integrates with the MDS message layer, request retry contexts, MDCache object waiters, lock state machines, journal callbacks, session/capability state, and client reply lease encoding.

The interface is intentionally broad because the locker sits at the convergence of metadata mutation, distributed lock state, client cap protocol, and journal persistence. MDCache can call `scatter_nudge`, cap paths can call lock evaluation, and request paths can use lock-cache helpers to elide repeated lock acquisition.

## Risks and Edge Cases

Because the header exposes many methods that mutate lock/cap state, callers must understand which functions require auth, stable locks, held auth pins, or active MDS state. `acquire_locks` can mutate the provided lock vector by adding quiesce/version locks. The local lock APIs only apply to `LocalLockC` lock types such as version and quiesce locks. `eval_any` silently does nothing for stable non-auth locks, so callers expecting replica-side state changes must send/request through the message path.

The public state lists are intrusive lists; objects must remove their list items before destruction. Misuse of `drop_non_rdlocks` versus `drop_locks` can preserve rdlocks that intentionally gate later snap/layout operations.

## Test Signals

Header-level validation is compile coverage across MDS modules that include `Locker.h`. Behavioral coverage should exercise all declared public families through request locking, cap issue/release, scatter writeback, stale cap handling, max-size updates, and lease issue/revoke. API regression tests should verify that quiesce/version locks and lock-cache helpers remain available to request code and that friend callback classes can reach private completion methods.
