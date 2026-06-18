<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/timestamp.go -->
# sources/cloud-native/containerd/pkg/protobuf/timestamp.go

## Purpose
Wraps protobuf timestamp conversion for containerd callers during migration away from older protobuf APIs.

## Important APIs, Types, And Functions
ToTimestamp calls timestamppb.New; FromTimestamp calls AsTime.

## Control Flow
Simple pass-through conversions between time.Time and *timestamppb.Timestamp.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim delete responses and event envelopes that need protobuf timestamps.

## Risks And Edge Cases
FromTimestamp assumes non-nil input; nil would panic via method call. Callers should validate optional timestamp fields.

## Test Signals
Covered indirectly wherever timestamp fields are serialized or read.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/timestamp.go -->
