# sources/cloud-native/buildkit/util/db/boltutil/safe_open.go

## Purpose
Resilient bbolt opener for disposable BuildKit databases. It recovers from open panics/errors by backing up a non-empty database and creating a new one.

## Important APIs, Types, And Functions
Package: `boltutil`. Build tags: `none`. Key declarations observed in the file: `SafeOpen, fallbackOpen, fileHasContent`.

## Control Flow, State, And Persistence
SafeOpen defers panic-to-error conversion, checks fileHasContent on failure, calls fallbackOpen to rename the corrupt file with identity.NewID and reopen.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/identity, github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/db, github.com/pkg/errors, go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is intentional data loss after corruption and backup rename failure. No local test in this subset.
