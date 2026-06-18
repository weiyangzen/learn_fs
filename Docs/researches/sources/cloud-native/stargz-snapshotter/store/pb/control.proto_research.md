<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.proto -->
# sources/cloud-native/stargz-snapshotter/store/pb/control.proto

## Purpose
Defines the protobuf schema for stargz store control messages.

## Important APIs, Types, And Functions
- Uses `syntax = "proto3"`.
- Package is `containerd_stargz_grpc`.
- `go_package` points to `github.com/containerd/stargz-snapshotter/store/pb`.
- Declares an empty `InfoRequest` message.

## Control Flow
No control flow; this is schema data consumed by protoc.

## State And Persistence
No state. Wire compatibility is determined by message and field definitions.

## Dependencies And Integration Points
Drives `control.pb.go` generation and any gRPC/control-plane code that imports the store pb package.

## Risks And Edge Cases
`InfoRequest` is empty, so future fields must use compatible proto3 numbering. Package/name changes would break generated Go imports and wire compatibility.

## Test Signals
Regenerating `control.pb.go` and compiling downstream users validates the schema.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.proto -->
