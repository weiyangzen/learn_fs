<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff.go -->
# sources/control-plane/ceph-csi/internal/rbd/snap_diff.go

## Purpose
`snap_diff.go` implements RBD snapshot diff streaming for the CSI Snapshot Metadata Service. It uses librbd `DiffIterateByID` to report allocated or changed byte ranges in batches, with support for encrypted-volume LUKS header offset correction.

## Important APIs, Types, And Functions
The central method is `rbdSnapshot.ProcessMetadata`. Supporting helpers are `handleDiffIterateError` and `createDiffIterateByIDCB`.

## Control Flow
`ProcessMetadata` opens the snapshot image, resolves the target snapshot ID via `getRBDSnapID`, sets the image to that snapshot, optionally converts and resolves the base snapshot ID, reads LUKS header padding metadata, shifts the requested starting offset by that padding, and returns early if beyond volume size. It creates a callback that appends `csi.BlockMetadata`, flushes when `maxResults` is reached, then calls `image.DiffIterateByID`. After iteration, remaining blocks are sent.

## State And Persistence
No persistent state is written. Runtime state includes the open RBD image, snapshot selection, local `changedBlocks` batch slice, and callback return codes. The reported offsets subtract LUKS header padding so callers see user-data offsets.

## Dependencies And Integration Points
It depends on go-ceph RBD `DiffIterateByID`, CSI block metadata, gRPC codes used as callback status integers, RBD snapshot conversion from `snapshot.go`, encryption metadata helpers, and snapshot metadata controller methods in `sms_controllerserver.go`.

## Risks
`createDiffIterateByIDCB` subtracts `luksHeaderPadding` from an unsigned offset; if librbd reports an offset below the padding, it underflows before conversion to `int64`. `maxResults` must be positive or every callback will flush immediately because `len < maxResults` is false; controller validation permits zero only after normalization. Error-code handling depends on errors implementing the local `ErrorCode` interface. A send failure is surfaced through callback code `Unknown`, then wrapped.

## Test Signals
`snap_diff_test.go` covers callback batching, LUKS offset adjustment, cancellation, send errors, remainder handling, no-block behavior, and `handleDiffIterateError` mappings. It does not exercise real RBD diff iteration, snapshot ID lookup, LUKS metadata read, or base-snapshot delta setup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff.go -->
