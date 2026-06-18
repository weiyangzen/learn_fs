# sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store.go

## Purpose

`tarantool/tarantool_store.go` implements a Tarantool-backed filer metadata store behind the `tarantool` build tag. It was read as a complete 324-line file.

## Important APIs, Types, and Functions

`TarantoolStore` owns a `pool.ConnectionPool`. It registers as `tarantool`, initializes pool instances, implements no-op transactions, entry CRUD, folder child deletion, directory listing, and `Shutdown`. Constants include `tarantoolSpaceName = "filer_metadata"`.

## Control Flow

Initialization parses comma-separated addresses, timeout, and reconnect settings, creates pool instances, connects, and pings. Inserts encode metadata, optional-gzip it, compute an absolute TTL epoch, and perform a CRUD upsert. Finds use CRUD get with read/replica preferences. Listing and folder deletion call Tarantool stored functions.

## State and Persistence Behavior

Metadata persists in Tarantool space `filer_metadata` with fields including directory, name, TTL, and data. Directory indexing/deletion behavior relies on Tarantool-side schema/functions.

## Dependencies and Integration Points

Depends on `go-tarantool/v2`, `crud`, `pool`, SeaweedFS filer serialization, and `filer_pb.ErrNotFound`.

## Risks and Edge Cases

Correctness depends on external Tarantool schema and stored functions being installed. Type assertions on returned rows can fail at runtime. Transactions are no-ops in Go.

## Test Signals

`tarantool_store_test.go` gates the generic store suite behind `RUN_TARANTOOL_TESTS=1`.
