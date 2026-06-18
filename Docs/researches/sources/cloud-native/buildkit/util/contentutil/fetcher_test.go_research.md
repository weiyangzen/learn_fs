# sources/cloud-native/buildkit/util/contentutil/fetcher_test.go

## Purpose
Unit tests for contentutil fetcher.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `TestFetcher, TestSlowFetch, dummySlowFetcher, Fetch, newSlowBuffer, slowBuffer, Seek, Read, Close`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.
