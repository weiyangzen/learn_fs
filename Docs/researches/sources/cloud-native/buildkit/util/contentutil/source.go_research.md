# sources/cloud-native/buildkit/util/contentutil/source.go

## Purpose
Checks whether content.Info labels indicate a descriptor came from a registry source reference.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `HasSource`.

## Control Flow, State, And Persistence
HasSource normalizes a reference spec and compares it against containerd distribution source labels for matching host/repository information.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/pkg/reference`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are label format drift and reference normalization. source_test.go validates positive/negative source detection.
