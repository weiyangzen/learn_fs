<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/types/types.go -->
# sources/cloud-native/containerd/pkg/protobuf/types/types.go

## Purpose
Defines type aliases for common protobuf well-known types to ease imports during protobuf migration.

## Important APIs, Types, And Functions
Aliases Empty, Any, and FieldMask to emptypb.Empty, anypb.Any, and fieldmaskpb.FieldMask.

## Control Flow
No control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim runtime options and APIs that want stable containerd import paths.

## Risks And Edge Cases
Aliases expose exact upstream types, so upstream API changes propagate directly.

## Test Signals
Compile-time aliasing is the only needed signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/types/types.go -->
