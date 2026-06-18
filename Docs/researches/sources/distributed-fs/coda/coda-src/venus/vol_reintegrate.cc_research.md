# sources/distributed-fs/coda/coda-src/venus/vol_reintegrate.cc

## Purpose

`vol_reintegrate.cc` implements Venus reintegration, the client-coordinated merge of locally logged mutations back to Coda servers after disconnected or weakly connected operation. It selects CML records that are ready, handles large-store partial reintegration, drives COP1 replay through `vol_cml.cc`, commits or preserves records depending on server outcomes, and launches ASR conflict handling when appropriate.

## Important APIs, Types, and Functions

`reintvol::Reintegrate` is the high-level volume reintegration routine. It disables ASRs, marks the volume reintegrating, enters the volume through `vproc::Begin_VFS`, locks the CML against checkpoint confusion, cancels open-for-write stores, loops over partial and normal reintegration work, then clears state and optionally launches ASR.

`reintvol::IncReintegrate` executes the main three-phase reintegration for one transient tid: late prelude (`IncReallocFids`, `IncThread`, `IncPack`), interlude (`COP1` or `COP1_NR`), and postlude (`IncCommit`, retry waiting, checkpoint and repair handling).

`reintvol::PartialReintegrate` handles a large store at the head of the log by obtaining or validating a server reintegration handle, sending data fragments within the time budget, and closing the handle with a packed CML replay once all data is sent.

`reintvol::ReadyToReintegrate` is the readiness predicate used by foreground transitions and `TrickleReintegrate`. It checks reachability, existing reintegration, non-empty CML, user token validity, ASR state, transition state, and the head CML entry's `ReintReady` result.

`cmlent::ReintReady` rejects repair-related entries, records containing local fids, transactional/IOT entries, and entries younger than the volume age limit.

The `reintegrator` class is a pooled `vproc` subclass. The free function `Reintegrate(reintvol *)` assigns a volume to an idle reintegrator or creates one.

## Control Flow

Normal asynchronous reintegration starts when `TrickleReintegrate` or a volume transition calls `Reintegrate(reintvol *)`. That dispatcher holds the volume, initializes a reintegrator's user context, marks it non-idle, and signals it. The reintegrator thread calls `reintvol::Reintegrate`.

Inside `reintvol::Reintegrate`, the routine first rechecks readiness, disables ASR invocation to prevent concurrent ASR-generated CML mutations, sets `flags.reintegrating`, and enters the volume as `CODA_REINTEGRATE`. It obtains a read lock on `CML_lock`, cancels stores for files still open for write, then loops while work succeeds and a full CML block may remain.

Each loop gets a new negative reintegration id. It first calls `PartialReintegrate` for a fat head store. If no partial work is needed (`ENOENT`), it asks the CML to mark reintegrateable entries up to the time and 100-record limits. If records were marked, `IncReintegrate` performs replay. The loop continues only when replay succeeds and `GetReintegrateable` indicated more work may be available.

`IncReintegrate` skips empty tids and unreachable volumes. It gathers CML stats, reallocates local fids, threads version vectors, packs the CML, chooses replicated or non-replicated COP1, and then handles results. Success and `EALREADY` commit entries. `ETIMEDOUT` preserves frozen uncertainty. `ERETRY` and `EWOULDBLOCK` cancel pending records when safe and sleep with bounded retry logic unless a transition is pending. Non-retryable failures checkpoint the CML, cancel pending entries, and mark failed records for repair.

After the main loop, `Reintegrate` clears reintegration and sync flags, clears the owner only if the CML is empty and no mutators remain, reports errors to `End_VFS` as `EINVAL` for failure accounting, reenables ASR, releases the CML lock, exits the volume, and tries to launch ASR if the failure was an incompatibility or inconsistency and policy allows it.

## State and Persistence Behavior

Most durable CML mutation happens in `vol_cml.cc`; this file controls transient volume flags and sequencing. `flags.reintegrating`, `flags.sync_reintegrate`, `cur_reint_tid`, retry counters in the current `vproc`, `flags.reint_conflict`, and `flags.unauthenticated` are transient state used for coordination and reporting.

The routine intentionally holds `CML_lock` in read mode during reintegration to prevent checkpoint iteration from racing with record cancellation, commit, or abort. It temporarily releases that lock around `CML.CheckPoint` because checkpointing boosts locking and the code avoids deadlock with mutator-held object locks.

Timeouts are treated conservatively. The code avoids cancelling pending records after `ETIMEDOUT` because the server may have committed even though the reply was lost. Retryable errors with known outcomes can cancel pending records.

## Dependencies and Integration Points

This file depends on `local.h`, `user.h`, `venus.private.h`, `venusvol.h`, and `vproc.h`. It integrates tightly with `ClientModifyLog` methods from `vol_cml.cc`, volume entry/retry behavior in `vproc.cc`, daemon dispatch in `vol_daemon.cc`, ASR controls in `vol_repair.cc`, and server RPC collation and VCB/COP2 behavior in other volume modules.

It uses user token validity through `realm->GetUser(CML.owner)`, Mariner progress logs, and `fsobj::LaunchASR` for local/global conflict automation.

## Risks and Edge Cases

The outcome distinction between timeout, retry, already-committed, and semantic failure is critical. Treating a timeout as safe-to-cancel could drop mutations that actually reached the server.

ASR coordination is conservative but fragile. `DisableASR` can return busy if an ASR is running; reintegration silently exits in that case. `EnableASR` must run on all exit paths after the flag was disabled.

The loop relies on negative tids and resets `cur_reint_tid` between attempts so log optimization can proceed. Incorrect tid reuse or stale tid values would cause commit or abort to affect the wrong records.

Large-store partial reintegration and normal reintegration must agree on `allow_backfetch` behavior. `GetReintegrateable` intentionally skips stores when backfetches are disabled so `PartialReintegrate` can handle them.

ASR launch after failure chooses the first to-be-repaired CML entry and then the first fid in that entry. This is pragmatic but may not represent every conflicted object in complex CMLs.

## Test Signals

Useful tests include readiness rejection for unreachable, unauthenticated, ASR-running, transition-pending, young, local-fid, and repair-marked cases; successful replicated and non-replicated reintegration; `EALREADY` commit; retry sleep bounds for `ERETRY` and `EWOULDBLOCK`; timeout preservation; non-retryable failure checkpointing and repair marking; partial store resume after bad handle and timeout; and ASR launch gating after `EINCONS` or `EINCOMPATIBLE`.

Runtime signals include `MarinerLog("reintegrate::...")`, `eprint("Reintegrate: ...")`, CML stats logs, retry counters in the `vproc`, and volume state reports before and after reintegration.
