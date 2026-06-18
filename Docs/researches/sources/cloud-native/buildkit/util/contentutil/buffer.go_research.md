# sources/cloud-native/buildkit/util/contentutil/buffer.go

## Purpose
In-memory content store implementing provider, ingester, ingest manager, and manager subsets for tests and transient content.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `Buffer, NewBuffer, buffer, Info, Update, Walk, Delete, Writer, Status, ListStatuses, Abort, ReaderAt, ...`.

## Control Flow, State, And Persistence
NewBuffer maintains mutex-protected digest-to-bytes, content.Info, and ref-lock maps. Writers buffer bytes, validate size/digest on Commit, add content info, support Truncate(0), ReaderAt, Info, and label Update. Walk/Delete/status are mostly no-ops.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are memory-only storage, incomplete content.Manager methods, and ref lock bookkeeping. buffer_test.go covers write/read, ReaderAt, digest/size errors, and labels.
