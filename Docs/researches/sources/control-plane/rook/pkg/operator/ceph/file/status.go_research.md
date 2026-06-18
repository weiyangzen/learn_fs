<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/status.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/status.go

## Purpose
This file centralizes CephFilesystem status updates and mirroring/snapshot-schedule status projection. It keeps CR status synchronized with reconcile phase, info maps, CephX state, mirror health, and snapshot schedule checks.

## Important APIs and control flow
`(*ReconcileCephFilesystem).updateStatus` retries on conflicts, fetches the `CephFilesystem`, initializes status, sets `Phase`, `Info`, optional `ObservedGeneration`, and optional daemon CephX status, then writes status through `reporting.UpdateStatus`. Missing resources are treated as deletion races. `(*mirrorChecker).updateStatusMirroring` fetches the filesystem and replaces status with `toCustomResourceStatus`. `toCustomResourceStatus` builds mirroring and snapshot schedule status structs, stamps `LastChecked` when input lists are non-empty, preserves prior `LastChanged` when possible, always stores error/details text, and preserves phase/info from the current status.

## State and persistence
All state is persisted in the `CephFilesystem.status` subresource. CephX status is nested under `Status.Cephx.Daemon`. Mirroring and snapshot schedule details include timestamps formatted in UTC RFC3339. No external Ceph state is modified.

## Dependencies and integration points
The file depends on controller-runtime clients, Kubernetes conflict retry helpers, Rook reporting status updates, `k8sutil.ObservedGenerationNotAvailable`, and logging helpers. The mirror checker path is an integration point for asynchronous CephFS mirroring inspection.

## Risks and test signals
`toCustomResourceStatus` assumes `currentStatus` is non-nil when preserving `Phase` and `Info`; callers initialize it before use. The function assigns `mirrorStatusSpec.LastChanged` from either previous mirroring status or previous snapshot status, which makes last-change semantics easy to regress. No direct tests for this file appear in the subset, so timestamp preservation and details propagation rely on broader controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/status.go -->
