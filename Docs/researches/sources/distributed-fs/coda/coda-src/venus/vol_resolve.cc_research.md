# sources/distributed-fs/coda/coda-src/venus/vol_resolve.cc

## Purpose

`vol_resolve.cc` implements asynchronous and synchronous resolution of replicated-volume inconsistencies. It queues fids needing server-side resolve, dispatches pooled resolver `vproc`s, invokes `ViceResolve` on a chosen coordinator, demotes or kills affected cache objects based on results, and wakes foreground waiters.

## Important APIs, Types, and Functions

`repvol::Resolve` is the worker routine that enters the volume as `CODA_RESOLVE`, flushes COP2, drains `res_list`, sends `ViceResolve` for each queued fid, handles parent requeue on `VNOVNODE`, demotes cached objects, and signals or deletes `resent` entries.

`repvol::ResSubmit` adds a fid to the resolution queue, optionally returns a wait block for synchronous callers, and marks the volume transition pending for async work. It deduplicates existing queued fids and supports bounded requeue through a `resent **`.

`repvol::ResAwait` waits on a submitted `resent` until `HandleResult` fills the result, then releases the waiter's reference.

`resent` is the queued resolve entry. It stores the target `VenusFid`, result code, waiter refcount, and remaining requeue count.

The `resolver` class is a pooled `vproc` subclass. The free function `Resolve(volent *)` assigns a volume to an idle resolver or creates one.

## Control Flow

Callers submit resolve work with `ResSubmit`. If the fid belongs to a different volume, is the same as the failed requeue entry, or the requeue count is exhausted, the fid is converted to `NullFid`. Otherwise, `ResSubmit` finds or creates a `resent`, increments its waiter refcount for synchronous use, appends requeued work behind newly submitted work, sets `transition_pending` for async dispatch, and demotes the cached object if present.

`Resolve(volent *)` prepares a resolver vproc with the target volume and signals it. In `resolver::main`, the thread waits for assignment, asserts the volume is replicated, calls `repvol::Resolve`, increments its sequence number, and returns to the freelist or self-destructs if the freelist is full.

`repvol::Resolve` enters the volume in resolving mode and first checks whether another thread already resolved the volume. It flushes COP2 before resolving because `ViceResolve` does not carry piggybacked COP2. For each `resent`, it acquires an mgroup, selects a primary host as coordinator, gets an unauthenticated/ANYUSER connection, calls `ViceResolve`, collates the return code, and records RPC stats.

After each RPC, it demotes any cached object for the fid. If resolution fails with `VNOVNODE` and the object has a cached parent, it submits the parent for resolve and requeues the current entry behind it. Other failures are logged. `HandleResult` then either deletes the entry or signals waiters. On exit, any pending entries are completed with `ERETRY`, `transition_pending` is set, and `End_VFS` receives `EINVAL` for failure accounting if needed.

## State and Persistence Behavior

The queue (`res_list`) and `resent` objects are transient. Resolution changes persistent/cache state indirectly: `FlushCOP2` may finalize mutation commits, `fsobj::Demote` invalidates cached status/data assumptions, and `resent::HandleResult(EINCONS)` kills cached inconsistent objects inside an RVM transaction.

`transition_pending` is used to force the volume state machine to revisit state after resolve work. Foreground synchronous waiters block on the address of the `resent` and are released by `VprocSignal`.

## Dependencies and Integration Points

This file depends on `comm.h`, `fso.h`, `mariner.h`, `mgrp.h`, `venus.private.h`, `venusvol.h`, and `vproc.h`. It integrates with COP2 flushing, the volume state machine, `FSDB` cache demotion/kill, multi-server mgroup selection, and `vproc::End_VFS` synchronous resolve handling via `u.u_resblk`.

Resolve submissions are also triggered from CML commit in `vol_cml.cc` when reintegration leaves objects needing server-side resolution, and from repair after successful directory repair.

## Risks and Edge Cases

Requeue is bounded by `MAX_REQUEUE`; after exhaustion, the fid becomes `NullFid` and no new parent-first resolve is queued. This prevents infinite loops but may leave complex missing-child cases unresolved until a later trigger.

`ResSubmit` demotes `FSDB->Find(fid)` even when `fid` was rewritten to `NullFid`. The null lookup must remain harmless.

Synchronous waiters rely on `refcnt` discipline. `HandleResult` deletes entries with no waiters; `ResAwait` deletes after the last waiter observes the result. Any future sharing must preserve that ownership model.

`repvol::Resolve` picks a primary host as coordinator and uses `ANYUSER_UID`. Server-side policy must allow this resolve path, or errors will propagate as retry/failure.

## Test Signals

Useful tests include async submission deduplication, synchronous submit/await, successful `ViceResolve`, already-resolved volume exit, COP2 flush failure, `VNOVNODE` child-to-parent requeue, `EINCONS` cache kill, pending-entry release with `ERETRY` on early exit, resolver freelist reuse, and bounded requeue exhaustion.

Runtime signals include `MarinerLog("resolve::")`, `MarinerLog("store::Resolve")`, `repvol::Resolve` logs for each fid, object demotion/kill effects, and `ResAwait` return codes feeding VFS retries.
