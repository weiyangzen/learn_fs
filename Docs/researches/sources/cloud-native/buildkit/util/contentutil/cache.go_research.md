# sources/cloud-native/buildkit/util/contentutil/cache.go

## Purpose
Caching wrapper for a ReferrersProvider. It fetches blobs/referrers once into a local content buffer/store and adds GC labels to keep cached dependencies reachable.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `ReferrersProviderWithBuffer, _, ReferrersProviderBuffer, ReaderAt, FetchReferrers, SetGCLabels, filterRefs, addName, readArtifactType`.

## Control Flow, State, And Persistence
ReaderAt opens a writer by digest ref, resets resumed offsets, copies source ReaderAt into cache, commits, records blob descriptors, and avoids poisoning later attempts on abort. FetchReferrers caches filtered referrers and names; SetGCLabels writes content and referrer GC references.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are partial ingest cleanup, label collisions, artifact-type filtering, and concurrent cache maps. cache_test.go covers blob caching, referrer caching, canceled reads, resumed offsets, and GC labels.
