# sources/control-plane/external-snapshotter/pkg/sidecar-controller/csi_handler.go

## Purpose
This file defines the `Handler` abstraction and CSI-backed implementation used by the sidecar controller to create, delete, and poll individual snapshots and volume group snapshots. It translates Kubernetes `VolumeSnapshotContent` and `VolumeGroupSnapshotContent` objects into CSI snapshotter and group snapshotter method calls, adds operation timeouts, validates required references and handles, and generates deterministic CSI snapshot names from object UIDs.

## Important APIs, Types, And Functions
- `Handler` declares `CreateSnapshot`, `DeleteSnapshot`, `GetSnapshotStatus`, `CreateGroupSnapshot`, `GetGroupSnapshotStatus`, and `DeleteGroupSnapshot`.
- `csiHandler` stores a `snapshotter.Snapshotter`, a `group_snapshotter.GroupSnapshotter`, operation timeout, and name prefix/UUID truncation settings for snapshots and group snapshots.
- `NewCSIHandler` wires the concrete handler and returns it as `Handler`.
- `CreateSnapshot` validates `VolumeSnapshotRef.UID` and source `VolumeHandle`, generates the CSI snapshot name with `makeSnapshotName`, and calls `snapshotter.CreateSnapshot`.
- `DeleteSnapshot` and `GetSnapshotStatus` select the snapshot handle from status first, then static source handle, and wrap missing-handle or CSI errors with content context.
- `makeSnapshotName` returns `prefix-uid` when truncation is `-1`, otherwise removes dashes and slices the UID to the configured length.
- `CreateGroupSnapshot`, `DeleteGroupSnapshot`, and `GetGroupSnapshotStatus` mirror the individual snapshot paths for group snapshot content, using group handles and required per-snapshot IDs.
- `makeGroupSnapshotName` implements group snapshot name generation with the handler's configured prefix and truncation.

## Control Flow
Every public method creates a `context.WithTimeout` from `handler.timeout` and defers cancellation. Create paths validate binding and source fields before name generation and CSI dispatch. Delete and status paths resolve handles from current status when available, fall back to spec source handles for static/pre-provisioned objects, and fail fast if required IDs are missing. Group delete and status require a non-empty `snapshotIDs` list before calling the group snapshotter because CSI group snapshot operations need the member snapshot handles.

## State And Persistence Behavior
The handler itself is stateless after construction except for its configured dependencies and naming parameters. It does not patch Kubernetes objects or persist results. Returned driver names, snapshot IDs, timestamps, sizes, readiness flags, and group snapshot IDs are persisted by higher-level controller code. Name generation is deterministic for a given prefix, UID, and truncation length, except it can panic if truncation length exceeds the dash-stripped UID length because slicing is unchecked.

## Dependencies And Integration Points
The file integrates with CSI protobuf types, external-snapshotter CRD APIs, `snapshotter.Snapshotter`, `group_snapshotter.GroupSnapshotter`, Go `context`, and controller code that owns Kubernetes object reconciliation. Error strings include content names and are consumed by tests and status/event paths in sidecar controller code.

## Risks And Edge Cases
- `makeSnapshotName` and `makeGroupSnapshotName` slice the dash-stripped UID without bounds checks. Invalid or short UIDs plus a positive configured UUID length can panic.
- Group delete/status require `snapshotIDs`; callers must correctly derive them from dynamic status or static spec handles.
- Handle resolution prefers status over spec. That is appropriate for dynamically provisioned objects, but stale status would override static spec data.
- The handler does not verify the CSI driver name returned by create operations; higher layers consume the returned value.
- A nil snapshotter or group snapshotter will panic if the corresponding method is called.

## Test Signals
`csi_handler_test.go` directly covers group snapshot methods, including missing UIDs, empty volume handles, missing group handles, empty snapshot ID lists, status/spec handle fallback, driver errors, and `-1` truncation behavior. Individual snapshot handler paths are indirectly covered by sidecar controller tests through the fake snapshotter.
