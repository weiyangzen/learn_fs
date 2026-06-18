# sources/control-plane/rook/pkg/operator/ceph/file/health.go

## Purpose
This file implements the periodic CephFS mirroring status checker used by the `CephFilesystem` controller when mirroring is enabled. It updates CR status with mirror daemon health, snapshot schedule status, or error text.

## Important APIs, Types, and Functions
`mirrorChecker` stores Rook context, interval, controller-runtime client, cluster info, namespaced name, filesystem spec pointer, and filesystem name. `newMirrorChecker` constructs the checker and applies `Spec.StatusCheck.Mirror.Interval` when set. `checkMirroring` runs one immediate check and then loops on `time.After(interval)` until its context is canceled. `checkMirroringHealth` calls `cephclient.GetFSMirrorDaemonStatus` and, when snapshot schedules are enabled, `cephclient.GetSnapshotScheduleStatus`, then calls `updateStatusMirroring`.

## Control Flow, State, and Persistence
The checker is launched as a goroutine by the reconciler. It writes status through Kubernetes API updates rather than persisting local state. On any Ceph status error, it records nil mirror/schedule status plus the error message. On success, it stores the current mirror status and schedule status with an empty error. Cancellation is driven by the controller's per-filesystem context map when the CR is deleted or not found.

## Dependencies and Integration Points
The checker integrates with Ceph mirror daemon status commands, snapshot schedule status commands, `CephFilesystem` status updates, controller-runtime client access, and the CR's mirroring/status-check fields. It depends on `updateStatusMirroring` defined elsewhere in the package.

## Risks
The loop uses `time.After` each iteration, so a canceled context is only observed immediately if it wins the select; otherwise timers are short-lived but repeated. The checker captures `fsSpec` at creation time, so schedule enablement and interval changes may not be picked up until the checker is restarted. Errors cause status updates both inside `checkMirroringHealth` and again in the caller path, which can duplicate status writes.

## Test Signals
Useful signals are interval override behavior, immediate first check, cancellation shutdown, status updates on mirror daemon errors, schedule status inclusion only when schedules are enabled, and stable behavior when Ceph commands fail repeatedly.
