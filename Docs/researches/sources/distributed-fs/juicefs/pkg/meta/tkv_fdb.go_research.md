# sources/distributed-fs/juicefs/pkg/meta/tkv_fdb.go

## Purpose
`tkv_fdb.go` adapts FoundationDB to the generic transactional KV metadata layer behind the `fdb` build tag.

## Important APIs, Types, and Functions
Key types are `fdbTxn` and `fdbClient`. `newFdbClient` sets API version 630, opens the configured cluster file/path, applies a query `prefix` through `withPrefix`, and registers `drivers["fdb"]`. Transaction methods map to FoundationDB `Get`, parallel `gets`, range scans, `Set`, `AppendIfFits`, atomic `Add` counters, and `Clear`.

## Control Flow and State
`fdbClient.txn` wraps the closure in FoundationDB `Transact`, relying on FDB's built-in retry loop. Top-level `scan` uses repeated snapshot read transactions with a large range limit and advances by appending a zero byte to the last key when a page is full. `reset` clears the prefix range. `id` combines the FDB read version with an atomic client-local sequence to generate changelog ids.

## State and Persistence Behavior
Metadata is persisted in FoundationDB under the selected prefix plus `0xFD`. Atomic counter increments use FDB's little-endian add semantics over the same encoding as `packCounter`. `close` is a no-op, so lifecycle is owned by the FDB binding/database handle.

## Dependencies and Integration Points
It depends on `github.com/apple/foundationdb/bindings/go/src/fdb`, build tags, URL parsing, and `prefixClient`. It integrates with `newKVMeta("fdb", ...)`, generic KV operations, changelog generation, and FDB-specific tests.

## Risks and Test Signals
Risks include build-tag drift, API version incompatibility, `AppendIfFits` not matching arbitrary append semantics for large values, scan pagination gaps, and `shouldRetry` returning false because retries are delegated to FDB. Tests in `tkv_fdb_test.go` call `testMeta` and `testTKV` against a local FoundationDB cluster.
