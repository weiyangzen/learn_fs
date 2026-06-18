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
