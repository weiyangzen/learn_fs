<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.pb.go -->
# sources/cloud-native/stargz-snapshotter/store/pb/control.pb.go

## Purpose
Generated Go protobuf bindings for the stargz store control API.

## Important APIs, Types, And Functions
- Defines the `InfoRequest` message type for `github.com/containerd/stargz-snapshotter/store/pb`.
- Provides standard proto reflection, reset/string/proto message methods, raw descriptor data, exporter setup, and `File_store_pb_control_proto`.
- Generated metadata comes from `store/pb/control.proto`.

## Control Flow
Generated init functions build and register the protobuf file descriptor. Message methods delegate to `protoimpl` runtime helpers.

## State And Persistence
No application state is persisted. Package globals cache descriptor and message info metadata.

## Dependencies And Integration Points
Depends on `google.golang.org/protobuf` runtime. Consumers should import the generated package rather than manually parsing control proto payloads.

## Risks And Edge Cases
Manual edits will be overwritten by regeneration. Generated code must stay in sync with `control.proto` and the protoc/protoc-gen-go versions used by `generate.go`.

## Test Signals
Compilation and proto reflection for `InfoRequest` are the main signals; regeneration should produce a stable diff when the proto is unchanged.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/pb/control.pb.go -->
