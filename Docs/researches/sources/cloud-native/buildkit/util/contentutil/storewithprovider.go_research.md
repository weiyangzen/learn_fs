# sources/cloud-native/buildkit/util/contentutil/storewithprovider.go

## Purpose
Decorator that lets a content.Store fall back to another provider for reads.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `NewStoreWithProvider, storeWithProvider, ReaderAt`.

## Control Flow, State, And Persistence
ReaderAt first tries the store and falls back to the provider only when content is missing; all other store behavior is inherited by embedding.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is masking missing local content with external provider access. No local test.
