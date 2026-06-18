# sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store_test.go

## Purpose

`foundationdb_store_test.go` exercises and benchmarks the FoundationDB filer store. It is guarded by the same `foundationdb` build tag and skips tests when no local FoundationDB cluster file is available, making it an integration-test suite rather than a pure unit suite.

## Important APIs, Types, and Functions

The tests cover `Initialize`, `initialize`, `GetName`, `genKey`, `extractFileName`, `FindEntry`, `KvGet`, transaction lifecycle methods, `InsertEntry`, `DeleteFolderChildren`, and `ListDirectoryEntries`. Helpers include `getTestClusterFile`, `createBenchmarkStore`, `createBenchmarkStoreWithBatching`, `getTestStore`, and `containsString`.

## Control Flow

Config tests create Viper-backed configuration values, initialize a store, and assert default/custom fields or expected parse failures. Key tests initialize a real store and check tuple key creation for root, nested, spaces, and Unicode paths. Error handling checks missing entry/KV lookups and transaction operations without an active context. Benchmarks pre-create or repeatedly write entries and compare direct commit mode with batched mode, including parallel insert workloads.

The large delete test creates hundreds of entries, then verifies `DeleteFolderChildren` outside a transaction, inside a transaction that is rolled back, and across nested directories. The expected behavior documents the implementation contract: deletions survive the outer rollback because the operation manages its own transactions.

## State and Persistence Behavior

Tests write real metadata and KV state into the configured FoundationDB cluster under the configured directory prefix. Many paths include timestamps to avoid collisions. Benchmark helpers create stores with configurable batching state and a `benchmark` prefix. No cleanup of the entire FDB directory layer is performed, so repeated benchmark runs can leave data unless the backing cluster is reset externally.

## Dependencies and Integration Points

The file depends on an operational FoundationDB service and `FDB_CLUSTER_FILE` or `/var/fdb/config/fdb.cluster`. It integrates with Go's testing/benchmark framework, SeaweedFS filer entry types, and FDB's actual transaction semantics.

## Risks and Edge Cases

Because most tests skip on missing FDB, CI without FoundationDB will not validate this backend. Tests that initialize the same directory prefix can interact with existing data if the cluster is shared. The custom `containsString` wrapper is simple but less idiomatic than `strings.Contains`. The large-delete test intentionally asserts non-atomic behavior, which is important because future refactors may otherwise try to make it transactional and reintroduce FDB transaction-limit failures.

## Test Signals

Strong signals are successful initialization against a real cluster, correct not-found errors, transaction state errors, key unpacking for Unicode and spaces, no entries remaining after large deletes, and benchmark deltas between batching modes under serial and parallel insertion.
