# sources/control-plane/longhorn-engine/pkg/replica/restore.go

Purpose: tracks replica-side restore progress and mutable status for backup restore operations.

Important APIs/types/functions: `RestoreStatus` stores replica address, progress, error, backup URL, state, target temp file, final snapshot disk name, last/current backup IDs, and a one-shot stop channel. `NewRestore` initializes in-progress status. `StartNewRestore` resets fields for a new restore and optionally clears last restored. `OpenVolumeDev` recreates the destination file. `UpdateRestoreStatus`, `FinishRestore`, `Revert`, `DeepCopy`, `Stop`, and `GetStopChan` manage state.

Control flow: restore starts in progress at zero. Status updates set progress and append/prepend errors, transitioning to error on non-nil error. Finish marks complete only if not already errored. Revert restores a previous snapshot of status when a failed restore did not modify files. Stop closes the channel once.

State and persistence: status is in-memory. `OpenVolumeDev` creates/removes a file path used as restore data target; durable rename/finalization occurs in sync-agent code outside this file.

Dependencies and integration points: used by sync-agent restore RPC implementation and sync task status reporting. Depends on logrus and Cockroach errors for file cleanup errors.

Risks: `DeepCopy` omits `replicaAddress`, `stopChan`, and `stopOnce`, which is fine for status revert but not a full clone. `OpenVolumeDev` logs "WithError(err)" when `err` is nil after successful stat. Error concatenation order can be surprising. No persistence means process restart loses in-progress status unless reconstructed elsewhere.

Test signals: no direct tests in this subset. Restore behavior is indirectly exercised by sync-agent restore tests if present elsewhere.
