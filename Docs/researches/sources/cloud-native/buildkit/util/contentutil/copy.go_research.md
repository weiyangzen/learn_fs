# sources/cloud-native/buildkit/util/contentutil/copy.go

## Purpose
Recursive OCI content copier. It copies a descriptor and its children/referrers from a provider to an ingester using containerd image handlers.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `CopyInfo, CopyOption, WithReferrers, Copy, localFetcher, Fetch, rc, Read, Seek, CopyChain, copyChain, annotateDistributionSourceHandler`.

## Control Flow, State, And Persistence
Copy wraps a local provider as a fetcher; CopyChain uses a visited SyncMap to avoid duplicate descriptors, dispatches handlers for children and optional referrers, and annotates distribution-source labels from the source provider.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/errdefs, github.com/moby/buildkit/util/bkmaps, github.com/moby/buildkit/util/resolver/limited, github.com/moby/buildkit/util/resolver/retryhandler, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are graph traversal cycles, handler compatibility, and missing referrers support. copy_test.go validates basic copy behavior.
