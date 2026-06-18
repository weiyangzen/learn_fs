# sources/cloud-native/buildkit/util/contentutil/pusher.go

## Purpose
Adapter from remotes.Pusher to content.Ingester. It exposes content.Writer handles backed by remote push streams.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `FromPusher, pushingIngester, Writer, writer, Status, Commit, Close`.

## Control Flow, State, And Persistence
Writer resolves descriptor/ref options, asks the pusher for a writer, tracks offset/status, validates expected digest on Commit, and closes remote resources.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are streaming push failures and limited local status semantics. No direct local test in this subset.
