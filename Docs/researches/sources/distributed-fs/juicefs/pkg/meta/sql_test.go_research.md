# sources/distributed-fs/juicefs/pkg/meta/sql_test.go

## Purpose

`sql_test.go` contains focused tests for SQL metadata backend construction, backend-specific DSN behavior, and SQLite chunk-reference correctness around batch clone and chunk deletion. It also invokes the shared `testMeta` suite for SQLite, MySQL, and PostgreSQL when those databases are available.

## Important APIs, Types, And Functions

`TestSQLiteClient` creates a temporary SQLite metadata database and runs `testMeta`. `TestSQLiteBatchUpdateChunkRefs` sets up source and destination directories, writes two slices to a source file, clones that file through `BatchClone`, verifies `chunk_ref` counts increase from 1 to 2, deletes the cloned chunk, and verifies counts decrease to 1 without triggering deletion callbacks. `sqlSliceRefCount` is a helper that reads a `sliceRef` row and validates its stored size.

`TestMySQLClient` and `TestPostgreSQLClient` instantiate SQL metadata backends for external databases and run `testMeta`; comments mark them as mutate tests. `TestPostgreSQLClientWithSearchPath` checks the one-schema `search_path` guard. `TestRecoveryMysqlPwd` validates MySQL password recovery cases. `TestGetCustomConfig` checks extraction and deletion of custom URL query parameters.

## Control Flow

The SQLite chunk-ref test initializes metadata, creates directories and a file, allocates two slices, writes both slices into the same chunk, checks initial reference counts, collects directory entries, invokes `BatchClone`, checks cloned file lookup and doubled refs, installs an `OnMsg(DeleteSlice)` callback that fails the test if deletion is attempted, calls `deleteChunk` on the clone, and finally verifies refs are decremented but still present.

## State And Persistence Behavior

The tests directly inspect `chunk_ref` rows for correctness, which is important because SQL clone/copy/delete operations rely on reference counts to decide when object slices can be physically deleted. The DSN tests verify that custom query parameters are consumed before the remaining DSN is passed to drivers.

## Dependencies And Integration Points

The file depends on test helpers such as `testConfig`, `testFormat`, `testMeta`, `Background`, and the public `Meta` methods. It also calls internal `dbMeta` methods (`Reset`, `Init`, `deleteChunk`, `getBase().BatchClone`) because the tests are in package `meta`.

## Risks And Edge Cases

External MySQL/PostgreSQL tests require local services and can mutate databases, making them environment-dependent. The SQLite chunk-ref test covers batch clone but not `CopyFileRange`, compaction, delayed slice cleanup, hardlink clone semantics, or failure retries. `TestPostgreSQLClientWithSearchPath` calls `err.Error()` without guarding nil, relying on the constructor to fail.

## Test Signals

The strongest signal is `TestSQLiteBatchUpdateChunkRefs`, which targets a previously risky persistence invariant: cloned chunks must increment `chunk_ref` and deleting a clone must not delete still-referenced slices. Shared `testMeta` invocations provide broad behavioral coverage when databases are configured.
