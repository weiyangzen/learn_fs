<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver_test.go

## Purpose
`sms_controllerserver_test.go` validates request validation and max-results normalization for Snapshot Metadata Service controller methods.

## Important APIs, Types, And Functions
Tests are `Test_validateMetadataAllocatedReq`, `Test_validateMetadataDeltaReq`, and `Test_normalizeMaxResults`.

## Control Flow
The tests use table-driven CSI request objects to check valid input, missing IDs, negative starting offsets, negative max results, empty secrets, zero max defaulting, over-limit capping, and in-limit preservation.

## State And Persistence
All state is in memory. No RBD or gRPC stream is created.

## Dependencies And Integration Points
The file depends on CSI protobuf request types and package constants. It guards the input contract before snapshot manager and diff code run.

## Risks
It does not assert exact gRPC status codes for validation errors, only error presence. It does not cover nil request handling, feature-gate behavior, or the streaming methods.

## Test Signals
Good signal for basic request guards and batch-size cap; weak signal for end-to-end metadata streaming.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver_test.go -->
