# sources/cloud-native/containerd/api/events/content.pb.go

## Purpose
This generated file provides Go protobuf types and descriptors for content lifecycle events.

## Important APIs, Types, And Functions
It defines `ContentCreate` with `Digest` and `Size`, `ContentDelete` with `Digest`, nil-safe getters, proto reflection methods, raw descriptor data, message info arrays, and `file_events_content_proto_init`.

## Control Flow
Generated control flow mirrors normal protoc-gen-go output: reset/store message info, string conversion, reflection, descriptor compression once, and descriptor build during init.

## State And Persistence
State is in-memory protobuf message and descriptor metadata. The file persists generated API code.

## Dependencies And Integration Points
It depends on `google.golang.org/protobuf` and a blank import of containerd API types for options. Content service event producers and consumers use these messages.

## Risks
Manual edits are overwritten. `Size` is int64 in proto but not exposed by generated fieldpath helper, so filterability is limited unless generator behavior changes.

## Test Signals
`make protos`, `go -C api test ./...`, Buf breaking checks, and content event serialization tests validate it.
