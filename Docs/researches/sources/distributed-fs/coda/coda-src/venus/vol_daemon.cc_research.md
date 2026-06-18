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
