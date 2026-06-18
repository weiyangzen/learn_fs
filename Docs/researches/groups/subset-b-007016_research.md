# Research: subset-b-007016

This grouped report covers Venus volume reintegration, repair, resolution, callbacks, the client modify log, and the `vproc` process abstraction. Each file section is bounded by reconciliation markers and preserves the source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_cml.cc -->
# sources/distributed-fs/coda/coda-src/venus/vol_cml.cc

## Purpose

`vol_cml.cc` implements Venus' Client Modify Log (CML), the persistent per-volume log of disconnected or write-back mutations. It records file and directory operations as `cmlent` records, optimizes away redundant operations, prepares log entries for reintegration RPCs, commits successful reintegrations into cached `fsobj` version state, aborts failed work, and checkpoints unreintegrated mutations to user-visible archive and `.cml` files.

The file is central to Coda's optimistic replication path. `reintvol` logging methods create CML entries while disconnected or write-back caching; `vol_reintegrate.cc` uses the CML prelude, packing, COP1 RPC, commit, and abort paths; `vol_repair.cc` uses the same log to localize or prune conflict entries.

## Important APIs, Types, and Functions

`ClientModifyLog` stores a persistent `rec_dlist` of `cmlent` objects plus transient/accounting fields such as `owner`, `entries`, high-water counters, byte counts, `cancelFrozenEntries`, and cancellation stats. `ResetTransient`, `Clear`, `_bytes`, `IncGetStats`, `print`, and `ResetHighWater` maintain these counters and reconstruct transient state after recovery.

`cmlent` is the persistent mutation record. Its discriminated union stores opcode-specific state for store, utimes, chown, chmod, create, remove, link, rename, mkdir, rmdir, symlink, and repair entries. It also carries a persistent `ViceStoreId sid`, operation time/user, `CmlFlags`, and transient bindings to affected `fsobj` instances.

Logging entry points are the `reintvol::Log*` methods. `LogStore`, `LogUtimes`, `LogChown`, and `LogChmod` perform last-writer or redundant-operation cancellation. Directory and name operations such as `LogRemove`, `LogRmdir`, and `LogRename` add identity-cancellation logic for create/remove pairs and target overwrite cases. `LogRepair` records disconnected repair mutations.

Reintegration preparation is split across `GetReintegrateable`, `GetFatHead`, `IncReallocFids`, `IncThread`, `IncPack`, `cmlent::realloc`, `cmlent::thread`, `cmlent::pack`, and `OutOfOrder`. COP1 network replay is handled by `ClientModifyLog::COP1` for replicated volumes and `COP1_NR` for non-replicated volumes.

Commit and failure APIs include `IncCommit`, `cmlent::commit`, `IncAbort`, `cmlent::abort`, `MarkFailedMLE`, `MarkCommittedMLE`, `HandleFailedMLE`, `CancelPending`, `ClearPending`, and `CancelStores`.

Partial store reintegration is exposed through `cmlent::HaveReintegrationHandle`, `GetReintegrationHandle`, `ValidateReintegrationHandle`, `WriteReintegrationHandle`, `CloseReintegrationHandle`, `DoneSending`, and `ClearReintegrationHandle`.

Persistence and user-safety helpers include `CheckPoint`, `cmlent::checkpoint`, `writeops`, `RecoverPathName`, `PathAltered`, `BackupOldFile`, `CheckPointMLEs`, `PurgeMLEs`, and `LastMLETime`.

## Control Flow

Creation starts in a `reintvol::Log*` method, normally inside an RVMLIB transaction. The method may scan the CML in commit or abort order, cancel older entries, and then allocate a new persistent `cmlent`. The constructor appends or prepends the record, copies RPC strings, initializes opcode-specific fields, generates a store id, resets transient version fields, attaches fid bindings, and updates log byte/count statistics.

Reintegration begins by freezing eligible records. `GetReintegrateable` walks in commit order, rejects records that are too young, not ready, blocked by store backfetch policy, or beyond the reintegration time budget, then freezes each record and assigns a transient negative reintegration tid. `GetFatHead` is the special path for a large store at the CML head; it freezes only that entry and drives partial reintegration.

Before COP1, `IncReallocFids` replaces local fids created offline with server-allocated fids, translating all references in both CML and FSDB. `IncThread` records each affected object's predecessor store id and threads version vectors through the CML in commit order. `IncPack` sizes and fills an RPC buffer using the generated `pack_CML_*_request` helpers.

`COP1` builds a SMARTFTP descriptor for the packed buffer, piggybacks COP2 data when configured, sends `ViceReintegrate` either through a replicated multi-RPC path or an older single-primary path, collates return codes, handles `EALREADY`, marks failed entries by server-provided index, updates volume callback state, clears COP2 entries, and purges stale directories reported by servers. `COP1_NR` performs the same basic flow with a single non-replicated connection.

On success, `IncCommit` iterates the tid's records and calls `cmlent::commit`. Commit updates affected `fsobj` version vectors, submits resolve work for replicated objects when needed, adds COP2 entries, and deletes each committed CML entry. On retryable or unknown outcomes, entries stay frozen or pending as appropriate. On non-retryable failures, the CML is checkpointed, pending cancellations are resolved, failed entries are converted to repair state, and affected objects are purged or localized by later repair logic.

Checkpointing locks the CML against concurrent mutators, writes an archive containing the latest file data for last stores, created directories, and symlinks, and writes a `.cml` operation listing with recovered path names. Path recovery walks backward through remove/rmdir/rename records to reconstruct names even after local mutations changed the current tree.

## State and Persistence Behavior

`ClientModifyLog` and `cmlent` are RVMLIB persistent objects. Code that mutates durable fields uses `Recov_BeginTrans`, `Recov_EndTrans`, and `RVMLIB_REC_OBJECT`; many entry points document whether they require or exclude transactions.

Persistent fields include the list links, CML owner/count/bytes, CML flags, store ids, operation data, strings, and store reintegration handles. Transient fields include fid binding lists, dependency lists, temporary reintegration tids, version-vector staging fields, failure/committed marks, and runtime counters rebuilt by `ResetTransient`.

Freezing is a critical persistence boundary. A frozen store creates a shadow copy through `fsobj::MakeShadow` so the data being reintegrated is stable while the user may continue mutating the file. `Thaw` removes the shadow. Cancellation of frozen entries is deferred through `flags.cancellation_pending` unless `cancelFrozenEntries` is set for repair pruning.

Partial reintegration persists `ViceReintHandle`, offset, primary host, and host index in the store CML entry. This allows Venus to resume a large store after timeouts or server changes, while validating the remote handle before continuing.

Checkpoint output is external persistence outside RVM. The code writes to a user spool directory, renames previous checkpoint artifacts to `.old`, uses mode `0600`, and deletes incomplete files on error.

## Dependencies and Integration Points

This file depends on RPC2, SFTP/SMARTFTP, multi-RPC marshalling, Vice CML packing helpers, the persistent RVMLIB layer, `FSDB`, `fsobj`, `venusvol.h`, `mgrp`, `comm`, `worker`, `mariner`, and archive helpers.

It integrates with `vol_reintegrate.cc` for scheduling and high-level reintegration policy, `vol_repair.cc` for local/global conflict repair and CML pruning, `vol_resolve.cc` through `ResSubmit` during commit, `vol_vcb.cc` through VCB update and stale directory invalidation, and `vproc.cc` through VFS retry and volume-entry discipline.

Server RPCs used here include `ViceReintegrate`, `ViceOpenReintHandle`, `ViceQueryReintHandle`, `ViceSendReintFragment`, and `ViceCloseReintHandle`.

## Risks and Edge Cases

The CML is highly stateful and relies on strict transaction boundaries. Calling a transaction-required method outside a transaction, or yielding while a transaction is active, can corrupt persistent state or trigger debug assertions.

Cancellation logic is subtle. Identity cancellation must not delete frozen entries that may already be visible at the server. The `cancellation_pending` path exists to defer those changes until the outcome is known.

Partial reintegration can leave persisted server handles and offsets. Bad handles are cleared and retried, but timeouts intentionally preserve state because the original server may later become reachable.

FID translation after local creation must update every CML reference and the FSDB atomically. A missed reference causes later packing, path recovery, or commit to refer to stale local fids.

The file contains several fixed-size path buffers and `sprintf` calls. Path reconstruction and checkpoint names depend on `MAXPATHLEN` assumptions and are risk points for malformed or unexpectedly long names.

Iterator behavior is fragile because records may delete themselves during cancellation, abort, or commit. Several loops advance the iterator before destructive calls; new changes must preserve that pattern.

## Test Signals

Useful tests would exercise disconnected create/remove identity cancellation, repeated chmod/chown/store cancellation, frozen-store cancellation after success and failure, local fid reallocation and translation across rename/link records, replicated and non-replicated COP1 success, `EALREADY`, retry, timeout, and semantic failure paths, large-store partial reintegration resume, CML checkpoint archive generation, and recovery-time `ResetTransient` reconstruction.

Runtime signals include `MarinerLog` reintegration lines, CML printouts, cancellation stats, `RecordsCommitted`, `RecordsCancelled`, `RecordsAborted`, `FidsRealloced`, stale directory purge logs, and checkpoint success/failure messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_cml.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_daemon.cc -->
# sources/distributed-fs/coda/coda-src/venus/vol_daemon.cc

## Purpose

`vol_daemon.cc` implements the Venus volume daemon. It is a periodic `vproc` that nudges volume state forward, reclaims idle volume resources, flushes delayed COP2 messages, checkpoints active CMLs, and triggers trickle reintegration for ready volumes. It is the background scheduler that keeps volume-level maintenance from depending solely on foreground VFS calls.

## Important APIs, Types, and Functions

`VOLD_Init` creates a `vproc` named `VolDaemon` with type `VPT_VolDaemon`.

`VolDaemon` registers with the daemon scheduler through `RegisterDaemon`, waits on `voldaemon_sync`, and runs periodic tasks at fixed intervals: transition checks every tick, `GetDown` every five minutes, COP2 flush every five seconds, CML checkpoint every ten minutes, and trickle reintegration every ten seconds.

`vdb::GetDown` scans replicated volumes and volume replicas looking for entries with only the database reference left. The current implementation logs reclaimable entries rather than actually destroying them in the shown code.

`vdb::FlushCOP2` iterates replicated volumes, enters each in non-blocking observing mode, and calls `repvol::FlushCOP2(COP2Window)` until the operation no longer returns `ERETRY`.

`vdb::TakeTransition` enters and exits every non-local replicated volume and volume replica in non-blocking observing mode. This intentionally causes `volent::Enter`/`Exit` state-machine side effects to run.

`vdb::CheckPoint` scans `reintvol` instances and checkpoints non-empty CMLs whose last modification falls within the checkpoint interval, unless local repair state is unresolved or the CML lock is busy.

`TrickleReintegrate` scans `reintvol` instances, enters each in non-blocking observing mode, calls `ReadyToReintegrate`, and dispatches `::Reintegrate` when possible.

## Control Flow

The daemon starts by yielding once so the newly created `vproc` has valid members, registers its wakeup interval, initializes last-run timestamps, and then loops forever. Each wakeup performs transition, resource, COP2, checkpoint, and reintegration tasks if their intervals have expired.

All maintenance work uses non-blocking volume entry where possible. This avoids wedging the daemon behind a volume already held by foreground work. For reintegration, `TrickleReintegrate` only dispatches an asynchronous reintegrator after the readiness predicate succeeds while the daemon has observing access.

Checkpointing has additional guards. It skips volumes containing unrepaired local subtrees, checks the last CML entry time, refuses to boost the CML lock if it is busy, and then calls `CheckPointMLEs` under observing entry.

## State and Persistence Behavior

The daemon itself keeps only transient timestamps and the global wakeup byte `voldaemon_sync`. The persistent effects come from the routines it invokes: COP2 entries may be sent and cleared, CML checkpoint archives may be written, and volume state transitions may demote, validate, resolve, or reintegrate state through `Enter`/`Exit`.

`vdb::GetDown` wraps its scans in a recovery transaction, but in this implementation the body only logs reclaimable volume entries. `vdb::CheckPoint` delegates durable CML archive persistence to `ClientModifyLog::CheckPoint`.

## Dependencies and Integration Points

This file depends on `venus.private.h`, `venusrecov.h`, `venusvol.h`, `vproc.h`, and `local.h`. It integrates with the volume database iterators, `volent::Enter`/`Exit`, the COP2 subsystem in `repvol`, CML checkpointing in `vol_cml.cc`, and reintegration dispatch in `vol_reintegrate.cc`.

The daemon is also part of the global daemon scheduler through `RegisterDaemon` and is woken via the `voldaemon_sync` address.

## Risks and Edge Cases

Because `FlushCOP2` uses `continue` when a volume is not replicated inside an inner infinite loop, it assumes the iterator only produces replicated `repvol` objects. A future iterator change could turn that into a spin.

`TakeTransition` relies on side effects of volume enter/exit, so behavior is indirect and can be easy to break if `Enter`/`Exit` semantics change.

Checkpoint selection uses `lmTime > curr_time - VolCheckPointInterval`, meaning it checkpoints recently changed CMLs on interval ticks rather than old inactive ones. That matches the comment but is worth preserving intentionally.

All daemon operations are opportunistic. Non-blocking entry failures silently defer maintenance until a later tick, so tests should account for eventual rather than immediate progress.

## Test Signals

Useful tests or runtime checks include daemon wakeup sequencing, transition-pending volumes being touched, COP2 queues being flushed after `COP2CheckInterval`, checkpoint files appearing for eligible CMLs but not for unrepaired CMLs or busy locks, and `TrickleReintegrate` dispatching only when `ReadyToReintegrate` is true.

Instrumentation signals are `LOG(100)` daemon messages, Mariner reintegration output, checkpoint `eprint` messages, and volume state reports emitted by lower layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_daemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_reintegrate.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_reintegrate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_repair.cc -->
# sources/distributed-fs/coda/coda-src/venus/vol_repair.cc

## Purpose

`vol_repair.cc` implements Venus repair of inconsistent replicated objects. It supports connected server/server repair through `ViceRepair`, local/global repair cleanup against the CML, disconnected file repair by creating a local repaired object and logging a `CML_Repair_OP`, and ASR permission/running-state controls.

The code bridges user-supplied repair files, cached fake conflict objects, server replica state, and CML mutation pruning. It is both a user-visible repair path and a reintegration conflict recovery component.

## Important APIs, Types, and Functions

`repvol::Repair` is the public dispatcher. It rejects unreachable or resolving volumes, then currently always calls `ConnectedRepair` for non-ASR-issued repair requests.

`GetRepairF` is a helper that recognizes repair file strings of the form `@volume.vnode.unique@realm`, resolves them to cached `fsobj` file data, and returns either a file object or no special handling for ordinary filesystem paths.

`repvol::ConnectedRepair` verifies the target is fake or marked to be repaired, flushes COP2, builds a `ViceStatus` from a repair `fsobj` or path, parses directory fixfiles through `repair_getdfile`, calls `ViceRepair` with multi-RPC, collates results, prunes local CML entries for local directory repairs, sends COP2, purges fake objects, and submits async resolve for repaired directories.

`repvol::DisconnectedRepair` supports disconnected file repair only. It verifies conflict state and parent write access, builds a template version vector from replicas, creates a local repaired `fsobj`, logs a repair CML entry, and calls `LocalRepair` to install file contents in the cache.

`repvol::LocalRepair` fills an `fsobj` from a `ViceStatus`, matriculates it, attaches parent fid state, creates a cache container file, copies repair contents, validates length, and marks the object dirty.

ASR control methods are `reintvol::EnableASR`, `DisableASR`, `AllowASR`, `DisallowASR`, `lock_asr`, `unlock_asr`, and `asr_pgid`.

## Control Flow

Connected repair starts by returning per-replica volume ids in `RWVols`, fetching the target status, and accepting only inconsistent fake objects or local/global to-be-repaired objects. It flushes COP2 because `ViceRepair` does not piggyback COP2. It optionally resolves the repair file to a cache object, generates a store id, acquires an mgroup, and computes a template version vector from the accessible replica objects.

The repair status is built from either cached repair data or `stat(2)` on the repair file. The code opens the repair data, creates a SMARTFTP descriptor, and, for directory repairs, parses the fixfile. When the fixfile includes the local replica, it precomputes fids and link counts for entries that may need corresponding CML pruning.

The server operation is a multi-RPC `ViceRepair`. `Collate_COP1` computes the update set and repair-level return code. The code then maps individual server return codes back to the `RWVols` order. On success or synchronous resolve, it may prune local CML mutations by replaying repair commands into `LogRemove`, `LogRmdir`, `LogChmod`, `LogChown`, `LogUtimes`, or `LogRename` with `cancelFreezes(1)` so frozen CML entries can be thawed and cancelled when safe.

For local/global file repair, successful connected repair discards local mutation state and clears all `to_be_repaired` flags. For all successful connected repairs, the code sends a final COP2, releases resources, purges the fake conflict object if this was not a local fake, and submits a resolve for directories.

Disconnected repair rejects directories, verifies the target is inconsistent, checks parent write access, builds a repair status, kills the fake conflict object if possible, creates a real FSDB object at the repaired fid, logs `LogRepair` with prepend, and copies repair data into the local container. The eventual reintegration of that CML repair entry causes the server-side `ViceRepair` and clears inconsistency remotely.

## State and Persistence Behavior

Connected repair mostly changes server state and cache state. It generates a persistent store id for COP2 finalization, may append or cancel CML entries inside recovery transactions, clears fake object flags before killing conflict placeholders, and can clear CML repair flags.

Disconnected repair persists a local dirty object and a repair CML record. `LocalRepair` mutates durable `fsobj` fields and creates cache container data inside an RVM transaction controlled by the caller.

ASR flags are transient volume flags. `allow_asrinvocation` is user permission, `enable_asrinvocation` is volume-service gating, `asr_running` serializes ASR execution, and `pgid` records the process group allowed to keep operating while ASR is active.

## Dependencies and Integration Points

The file depends on RPC2, Vice interfaces, `inconsist.h`, `copyfile.h`, `prs.h`, `repio.h`, `FSDB`, `fsobj`, `mgrp`, `mariner`, `worker`, `realmdb`, and volume/CML APIs.

It integrates with `vol_cml.cc` by logging repair entries, pruning CML operations, and clearing repair flags; with `vol_reintegrate.cc` through ASR gating and local/global conflict recovery; with `vol_resolve.cc` by submitting resolves after directory repair; and with COP2 and multi-RPC collation in the replicated volume layer.

## Risks and Edge Cases

Connected repair assumes the target object remains meaningful after the initial status get. Fake object purging and local CML pruning must be ordered carefully so users do not see stale conflict state.

Directory fixfile pruning is complex. It depends on parsing the local replica section, looking up names before the server call, preserving link counts, and then converting repair commands into CML operations. Lookup failures or unexpected opcodes can leave server repair successful but local CML cleanup incomplete.

`ConnectedRepair` currently always selected by `Repair` means disconnected repair is unreachable through that dispatcher unless the placeholder predicate is changed.

`LocalRepair` uses assertions around file opens and copy operations. In production builds or unusual environments, bad repair paths or container-file failures can become hard failures rather than graceful error propagation.

ASR flags are simple bit fields without internal locking in this file. Correctness depends on volume entry discipline and the broader Venus single-process LWP model.

## Test Signals

Useful tests include repair of a fake file and fake directory, repair-file-by-fid parsing, ordinary path repair with file, directory, and symlink status, COP2 flush failure, per-replica return-code collation, directory fixfile pruning for remove/rmdir/chmod/chown/utimes/rename, local/global file repair clearing repair flags, disconnected file repair and later reintegration, access denial through parent rights, and ASR allow/enable/running state transitions.

Runtime signals include `MarinerLog("store::Repair")`, `ViceRepair` multi-RPC stats, per-replica `ReturnCodes`, fake-object purge logs, CML pruning logs, and `DisconnectedRepair` length-mismatch or access messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_repair.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_resolve.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_resolve.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_vcb.cc -->
# sources/distributed-fs/coda/coda-src/venus/vol_vcb.cc

## Purpose

`vol_vcb.cc` implements volume callback (VCB) management. VCBs let Venus validate or invalidate cached state at volume granularity using server-maintained version stamps. The file handles callback breaks, fetching initial volume version stamps, piggyback validation of multiple volumes, collation of callback status from replicated servers, cached-object validation before acquiring a volume stamp, and the simple policy for deciding when a callback is worth requesting.

## Important APIs, Types, and Functions

Global state includes `vcbbreaks`, a count of broken volume callbacks, and `VCBEnabled`, the default policy toggle.

`vdb::CallBackBreak` maps a kernel/server callback-break `Volid` to a volume and invokes `reintvol::CallBackBreak`.

`reintvol::GetVolAttr` is the main validation/fetch routine. If `VVV` is null, it validates cached FSOs, calls `ViceGetVolVS`, and records returned version stamps and callback status. If `VVV` is present, it batches validation of volumes on the same VSG or host through `ViceValidateVols`.

`reintvol::UpdateVCBInfo` handles the single-server/non-replicated callback result path.

`repvol::CollateVCB` handles replicated callback collation, requiring every participating server to return `CallBackSet` before preserving the callback.

`reintvol::ValidateFSOs` walks cached fsobjs in the volume and refetches status/data for invalid objects before a volume stamp is fetched.

`reintvol::PackVS` serializes version stamps into an RPC counted byte string.

`reintvol::CallBackBreak`, `ClearCallBack`, `SetCallBack`, and `WantCallBack` maintain callback state and policy.

## Control Flow

A callback break enters through `vdb::CallBackBreak`. The volume is looked up, `CallBackBreak` clears `VCBStatus` and persistent `VVV` if a callback was set, and the global break count increments only when a callback was actually broken.

`GetVolAttr` first gets a connection and, for replicated volumes, an mgroup. It records the current `cbbreaks` count so it can avoid installing callback state if a concurrent callback break occurred during the RPC.

When the local volume version vector is null, `GetVolAttr` calls `ValidateFSOs` first. This ensures any cached file state is valid before Venus asks servers for a volume-level version stamp that will summarize that state. It then calls `ViceGetVolVS`, collates the non-mutating result, and updates VCB info if no callback break raced.

When the version vector is non-null, `GetVolAttr` builds a batch of up to `MAX_PIGGY_VALIDATIONS` eligible volumes: reachable, wanting a callback, non-null VVV, and on the same VSG for replicated volumes or same host for non-replicated volumes. It serializes all version stamps, calls `ViceValidateVols`, collates results, and then applies per-volume flags. Valid callback results set callbacks and promote directory access rights for `ANYUSER_UID` and the current uid. Valid no-callback results clear callbacks. Invalid results clear callbacks and reset `VVV`.

`ValidateFSOs` iterates the volume's `fso_list`, skips dying or already-valid objects, holds the next object while calling `FSDB->Get` on the current one, and purges kernel state on `EINCONS`.

## State and Persistence Behavior

`VCBStatus`, `VCBHits`, and some policy counters are transient, while `VVV` is a persistent volume version vector. Updates to `VVV` are wrapped in RVMLIB transactions.

A valid callback means Venus can trust `VVV` until a callback break. A callback break clears both the transient callback status and the persistent version vector so later accesses must validate or refetch.

`GetVolAttr` installs callback state only if `cbbreaks` has not changed since the RPC started. This avoids accepting stale callback promises after a concurrent break.

## Dependencies and Integration Points

This file depends on RPC2, Vice callback/status types, `comm`, `fso`, `mariner`, `mgrp`, `venuscb`, `venusvol`, `vproc`, and `worker`.

It integrates with server RPCs `ViceGetVolVS` and `ViceValidateVols`, cache validation through `FSDB->Get`, kernel purge through `k_Purge`, access-right promotion on directories, COP1/reintegration paths that call `CollateVCB` or `UpdateVCBInfo`, and callback-break downcalls through `vdb::CallBackBreak`.

## Risks and Edge Cases

The batching path serializes version stamps into a raw byte string. It depends on matching server expectations for stamp count and endian conversion. Replicated and non-replicated paths use different stamp counts and host arrays.

`ValidateFSOs` mutates and may remove objects while iterating `fso_list`, so it holds the next object before the fetch. This pattern must be preserved.

Callback collation is intentionally conservative. Any participating replicated server returning no callback clears the volume callback, and any zero stamp resets `VVV`.

`WantCallBack` uses a simple threshold: more than one cached fsobj and no current callback. That policy may be suboptimal for workloads with frequent mutations or partitions, but it is easy to reason about.

## Test Signals

Useful tests include callback break with and without an active callback, initial `ViceGetVolVS` fetch after validating stale FSOs, piggyback validation across same-VSG replicated volumes, same-host non-replicated volumes, callback-break race during RPC, mixed server callback statuses, invalid zero stamps, `ValidateFSOs` handling status-only and data invalidation, and `WantCallBack` threshold behavior.

Runtime signals include `vcbbreaks`, VVV debug prints, `MarinerLog("store::GetVolVS")`, `MarinerLog("store::ValidateVols")`, callback status logs, access-right promotion effects, and kernel purges on `EINCONS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vol_vcb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc.cc -->
# sources/distributed-fs/coda/coda-src/venus/vproc.cc

## Purpose

`vproc.cc` implements Venus' lightweight process abstraction on top of the Coda LWP and IOMGR libraries. It provides vproc creation, current-thread lookup through LWP rocks, wait/signal/sleep/yield wrappers with transaction-safety checks, retry backoff, volume-entry wrappers for VFS operations, process diagnostics, vnode attribute initialization, and fid-to-kernel-node conversion.

This abstraction underpins daemon threads, workers, reintegrators, resolvers, callback handlers, and foreground VFS call handling.

## Important APIs, Types, and Functions

`VprocInit` initializes the main vproc and retry schedule. `VprocPreamble` runs in each new LWP, finds the owning `vproc`, installs LWP rocks for the vproc and RVM thread data, then calls the vproc's virtual `main`.

`VprocSelf`, `FindVproc`, `vproc_iterator`, and the static `vproc::tbl` provide lookup and iteration.

`VprocWait`, `VprocMwait`, `VprocSignal`, `VprocSleep`, `VprocYield`, and `VprocSelect` wrap LWP/IOMGR primitives. In debug builds, they assert that the current thread is not inside an RVM transaction before context switching.

`VprocSetRetry`, `VprocRetryN`, and `VprocRetryBeta` configure bounded exponential retry sleeps.

The `vproc` constructor, `start_thread`, `main`, destructor, `GetStamp`, and `print` manage lifecycle, LWP startup synchronization, dispatch, diagnostic stamps, and stack reporting.

`vproc::Begin_VFS` resolves the target volume, maps VFS operations to volume modes, applies red/yellow resource-zone throttling, blocks non-ASR processes while ASR is running, and calls `volent::Enter`.

`vproc::End_VFS` exits the volume, handles synchronous resolve, decides whether errors should retry, sleeps for retry/would-block/timeout cases, updates VFS statistics, and releases the volume reference.

`va_init`, `VPROC_printvattr`, and `FidToNodeid` are utility functions for kernel/VFS attribute and node-id handling.

## Control Flow

At startup, `VprocInit` creates the `Main` vproc with a placeholder function. The first `start_thread` initializes LWP and IOMGR and immediately runs `VprocPreamble`; later `start_thread` calls create new LWPs with a startup lock so the new thread can map itself back to its `vproc` object before running `main`.

Derived classes such as reintegrator and resolver pass `NULL` to the base constructor and call `start_thread` after their constructors finish. This avoids virtual dispatch before derived initialization is complete.

For a VFS operation, the caller initializes user context and calls `Begin_VFS`. If no volume is already in context, it obtains one from `VDB`. The operation is mapped to `VM_MUTATING`, `VM_OBSERVING`, or `VM_RESOLVING` unless explicitly supplied. Mutating replicated operations may throttle in yellow/red cache pressure zones by waking the FSO daemon and sleeping until red-zone pressure drops. ASR process-group checks can reject unrelated callers with `EAGAIN`. Finally, `volent::Enter` performs state-machine locking.

`End_VFS` mirrors this. It may set `transition_pending` for synchronous reintegration after successful create/destroy-like mutations, exits the volume, handles `ESYNRESOLVE` by waiting on `ResAwait`, and then processes retryable errors. `ERETRY` uses the configured exponential schedule, `EWOULDBLOCK` uses bounded fixed waits, and `ETIMEDOUT` waits only for users configured to wait forever. It sets `*retryp` when the caller should retry the whole operation.

## State and Persistence Behavior

`vproc` objects are transient process structures, but each has `rvm_perthread_t rvm_data` installed as an LWP rock so RVMLIB can associate transactions with the current lightweight process. The wait/signal/sleep/yield wrappers are important persistence safety gates because they prevent context switches while an RVM transaction is active in debug builds.

`u` is the per-vproc user/VFS context. It stores current volume, uid, operation, volume mode, retry counters, resolve wait block, priority, process group, and timing fields.

The retry schedule is global process state allocated once by `VprocSetRetry`.

## Dependencies and Integration Points

This file depends on LWP, IOMGR, RVMLIB thread data, `local.h`, `user.h`, `venus.private.h`, `venusrecov.h`, `venusvol.h`, and `worker.h`.

It is used by nearly every other Venus subsystem. `vol_daemon.cc`, `vol_reintegrate.cc`, and `vol_resolve.cc` all define `vproc`-based daemons or pooled workers. Volume methods depend on `Begin_VFS` and `End_VFS` for consistent state transitions, retries, and statistics. FSDB pressure control integrates through `FSOD_ReclaimFSOs`, cache block counts, free MLE counts, and CML length thresholds.

## Risks and Edge Cases

Context switching inside RVM transactions is dangerous; the debug checks catch it, but non-debug builds rely on discipline. New code should avoid `VprocWait`, `VprocSleep`, `VprocYield`, or blocking I/O inside recovery transactions.

The startup handshake is delicate. Derived vproc classes must not let the base constructor start the thread before derived fields and virtual methods are ready.

`Begin_VFS` red-zone throttling can stall mutators indefinitely until reintegration or cache reclamation frees resources. This is intentional backpressure but can look like a hang if reintegration is also blocked by tokens or conflicts.

`End_VFS` converts `ERETRY` to `EWOULDBLOCK` if the caller did not provide a retry pointer. Callers must opt into retry loops explicitly.

ASR gating compares process groups. Incorrect pgid setup can either block the ASR itself or allow unrelated mutators during ASR.

## Test Signals

Useful tests include vproc creation and freelist users, `VprocSelf` lookup through rocks, retry beta calculation bounds, debug detection of waits in transactions, `Begin_VFS` mode mapping for representative CODA operations, red/yellow zone throttling, ASR pgid exclusion, `End_VFS` retry handling for `ERETRY`, `EWOULDBLOCK`, `ETIMEDOUT`, synchronous resolve handling for `ESYNRESOLVE`, and VFS statistic updates.

Runtime signals include `PrintVprocs`, per-vproc stamps from `GetStamp`, VFS stats counters, Mariner red/yellow zone messages, wait/retry `eprint` messages, and stack usage in `vproc::print`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc.cc -->
