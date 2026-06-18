# sources/cloud-native/buildkit/util/db/boltutil/db.go

## Purpose
Thin bbolt opener implementing BuildKit util/db.DB. It wraps bolt.Open and returns the database through the local interface type.

## Important APIs, Types, And Functions
Package: `boltutil`. Build tags: `none`. Key declarations observed in the file: `Open`.

## Control Flow, State, And Persistence
No additional state or control flow beyond propagating open errors.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/db, go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is direct bbolt open failure. SafeOpen adds recovery behavior in the sibling file.
