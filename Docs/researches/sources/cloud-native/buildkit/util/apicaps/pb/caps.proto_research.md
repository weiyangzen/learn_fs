# sources/cloud-native/buildkit/util/apicaps/pb/caps.proto

## Purpose
Protocol schema for API capability advertisements. APICap is the wire format exchanged between clients and services to describe support, disablement, and alternatives.

## Important APIs, Types, And Functions
Package: `moby`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
Fields are scalar and backward-compatible when appended. No control flow in the proto itself; generated code and apicaps.CapList consume it.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are field semantic drift, especially Deprecated and DisabledAlternative. caps.go and caps_test.go are the behavior consumers.
