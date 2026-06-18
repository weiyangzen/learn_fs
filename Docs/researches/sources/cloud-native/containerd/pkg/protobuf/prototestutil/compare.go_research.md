<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/prototestutil/compare.go -->
# sources/cloud-native/containerd/pkg/protobuf/prototestutil/compare.go

## Purpose
Provides a cmp.Option for tests to compare protobuf messages by semantic proto equality rather than Go struct field equality.

## Important APIs, Types, And Functions
Compare filters values where both sides implement proto.Message and compares them with proto.Equal.

## Control Flow
go-cmp invokes the filter for candidate values and the comparer performs type assertions before calling proto.Equal.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Integrates tests using github.com/google/go-cmp/cmp with google.golang.org/protobuf/proto.

## Risks And Edge Cases
The comparer only applies when both values are proto.Message; mixed or wrapped values fall back to other cmp behavior.

## Test Signals
No direct test here; intended as shared test infrastructure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/prototestutil/compare.go -->
