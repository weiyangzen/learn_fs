# sources/cloud-native/buildkit/util/db/transactor.go

## Purpose
Transaction interface for bbolt-backed utility databases. It defines View and Update methods accepting *bolt.Tx callbacks.

## Important APIs, Types, And Functions
Package: `db`. Build tags: `none`. Key declarations observed in the file: `Transactor`.

## Control Flow, State, And Persistence
No state or implementation; concrete bolt.DB satisfies it.

## Dependencies And Integration Points
Important dependencies/imports: `go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is bbolt-specific type leakage through the interface. No tests.
