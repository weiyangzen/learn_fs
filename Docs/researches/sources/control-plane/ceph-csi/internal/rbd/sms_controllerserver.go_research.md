<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver.go

## Purpose
`sms_controllerserver.go` implements CSI Snapshot Metadata Service streaming RPCs for RBD snapshots: allocated metadata for one snapshot and delta metadata between two snapshots.

## Important APIs, Types, And Functions
Key functions are `normalizeMaxResults`, `validateMetadataAllocatedReq`, `ControllerServer.GetMetadataAllocated`, `validateMetadataDeltaReq`, and `ControllerServer.GetMetadataDelta`. `defaultMaxResults` caps streamed batch size at 128.

## Control Flow
Both RPCs first check `features.SupportsRBDSnapDiffByID`, validate IDs, secrets, starting offset, and max results, then create a manager with request secrets. `GetMetadataAllocated` resolves one snapshot and streams `ProcessMetadata` with no base snapshot. `GetMetadataDelta` resolves base and target snapshots and streams `ProcessMetadata` against the target with the base snapshot. Both reject starting offsets beyond the target volume size and wrap each sent batch in CSI response messages with variable-length block metadata and capacity.

## State And Persistence
The server does not write persistent state. It opens manager/snapshot resources and streams responses over gRPC. It depends on snapshot size and RBD diff iteration state from `snap_diff.go`.

## Dependencies And Integration Points
It depends on CSI snapshot metadata service protobufs, go gRPC status codes, feature probing, `NewManager`, RBD snapshot resolution, and `rbdSnapshot.ProcessMetadata`.

## Risks
The feature probe is runtime-gated and returns `Unimplemented` when unavailable. `maxResults` is capped internally, which can surprise callers requesting larger batches but protects memory. Secrets are mandatory. Starting offset is checked before LUKS header padding is applied in `ProcessMetadata`, so encrypted snapshots rely on downstream adjustment. Snapshot resolution errors are mapped to `NotFound` only for `ErrImageNotFound`.

## Test Signals
`sms_controllerserver_test.go` covers validation and max-results normalization. It does not test streaming RPCs, feature-gate failures, manager interactions, snapshot lookup, or send failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver.go -->
