# sources/cloud-native/containerd/api/events/container.pb.go

## Purpose
This generated file provides Go protobuf types and descriptors for container lifecycle event messages defined in `events/container.proto`.

## Important APIs, Types, And Functions
It defines `ContainerCreate`, `ContainerUpdate`, `ContainerDelete`, nested `ContainerCreate_Runtime`, getters for each field, `ProtoReflect`, deprecated `Descriptor` methods, `File_events_container_proto`, raw descriptor data, message info arrays, dependency indexes, and `file_events_container_proto_init`.

Fields include create `ID`, `Image`, and runtime name/options (`google.protobuf.Any`); update `ID`, `Image`, `Labels`, and `SnapshotKey`; delete `ID`.

## Control Flow
Generated methods reset messages, return string/proto reflection forms, expose nil-safe getters, compress raw descriptors once, and build the file descriptor during package init.

## State And Persistence
State is in-memory protobuf descriptor metadata, guarded raw descriptor compression, and per-message protoimpl state/size/unknown fields. There is no disk persistence.

## Dependencies And Integration Points
It depends on `google.golang.org/protobuf`, `anypb`, and a blank import of `github.com/containerd/containerd/api/types` for custom options. Event publishers/consumers in containerd use these types for typed event payloads.

## Risks
Manual edits would be overwritten by `make protos`. API compatibility is controlled by field numbers and proto definitions; changing or reusing numbers can break clients. `Any` runtime options require registered typeurl handling for consumers.

## Test Signals
Generated-code freshness via `make protos`/git diff, `go -C api test ./...`, Buf breaking checks, and event serialization/deserialization tests are relevant.
