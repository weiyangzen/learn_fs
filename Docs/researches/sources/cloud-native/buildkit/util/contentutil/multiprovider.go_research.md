# sources/cloud-native/buildkit/util/contentutil/multiprovider.go

## Purpose
Content provider multiplexer with lazy provider registration. It routes descriptors to per-digest providers while falling back to a base provider.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `NewMultiProvider, MultiProvider, SnapshotLabels, ReaderAt, Info, Add, UnlazySession`.

## Control Flow, State, And Persistence
Add stores provider overrides, ReaderAt/Info select provider by digest, SnapshotLabels records indexed labels for descriptors, and UnlazySession exposes session groups from lazy providers.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/errdefs, github.com/moby/buildkit/session, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale provider maps and label/index assumptions. multiprovider_test.go covers routing and label snapshots.
