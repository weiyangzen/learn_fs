# sources/cloud-native/buildkit/util/db/db.go

## Purpose
Database interface contract used by BuildKit utilities. DB combines io.Closer with the Transactor interface.

## Important APIs, Types, And Functions
Package: `db`. Build tags: `none`. Key declarations observed in the file: `DB`.

## Control Flow, State, And Persistence
No control flow. It abstracts bbolt so callers depend on View/Update/Close rather than concrete bolt.DB.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is interface drift with transaction users. No tests.
