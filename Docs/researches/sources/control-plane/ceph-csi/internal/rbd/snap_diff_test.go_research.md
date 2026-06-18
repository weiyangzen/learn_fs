<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/snap_diff_test.go

## Purpose
`snap_diff_test.go` unit-tests the pure callback and error-handling parts of snapshot diff streaming.

## Important APIs, Types, And Functions
It defines `mockError` implementing `Error()` and `ErrorCode()`, `newMockError`, `Test_createDiffIterateByIDCB`, `Test_createDiffIterateByIDCB_errorAndEdgeCases`, and `Test_handleDiffIterateError`.

## Control Flow
The callback tests simulate librbd diff callbacks for single blocks, LUKS padding adjustment, max-result batching and slice reset, send errors, context cancellation, multiple batches with remainder, and zero-block cases. Error tests feed nil, OK, canceled, unknown/send failure, unrecognized code, and generic errors into `handleDiffIterateError`.

## State And Persistence
All state is in memory. The tests copy sent batches to avoid slice reuse hiding bugs.

## Dependencies And Integration Points
The tests depend on CSI `BlockMetadata` and gRPC `codes`, but do not require go-ceph or a live RBD image. They validate behavior used by `rbdSnapshot.ProcessMetadata`.

## Risks
The tests do not cover unsigned underflow when LUKS padding exceeds callback offset. They also do not cover actual `DiffIterateByID` integration, final remainder flushing by `ProcessMetadata`, or base snapshot ID handling.

## Test Signals
Strong signal for callback batching and error code translation; weak signal for backend diff behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff_test.go -->
