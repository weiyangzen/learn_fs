# sources/cloud-native/buildkit/util/contentutil/cache_test.go

## Purpose
Unit tests for contentutil cache.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `stubProvider, newStubProvider, ReaderAt, FetchReferrers, add, addReferrer, buf, Close, newBuf, stubManifest, TestReferrersProviderBuffer, TestReferrersProviderRefsBuffer, ...`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/containerd/v2/plugins/content/local, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.
