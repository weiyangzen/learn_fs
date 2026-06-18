# sources/cloud-native/buildkit/util/contentutil/fetcher.go

## Purpose
Adapter from remotes.Fetcher to content.Provider plus referrers support. It converts streaming fetches into ReaderAt-capable objects.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `ReferrersProvider, FromFetcher, fetchedProvider, ReaderAt, FetchReferrers, readerAt, ReadAt, Size`.

## Control Flow, State, And Persistence
ReaderAt fetches a stream, reads it fully into memory, and returns a readerAt wrapper with Size and Close. FetchReferrers delegates to fetchers implementing remotes.ReferrersFetcher.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are memory use for large blobs and slow fetch behavior. fetcher_test.go covers normal and slow fetch cases.
