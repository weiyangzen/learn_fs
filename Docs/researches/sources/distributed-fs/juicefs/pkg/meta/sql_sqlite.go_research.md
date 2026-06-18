# sources/distributed-fs/juicefs/pkg/meta/sql_sqlite.go

## Purpose

`sql_sqlite.go` provides SQLite-specific registration for the SQL metadata backend. It detects SQLite constraint errors, exposes the SQLite busy error to shared retry logic, and registers the `sqlite3` scheme.

## Important APIs, Types, And Functions

`isSQLiteDuplicateEntryErr` checks whether an error is a `sqlite3.Error` with code `sqlite3.ErrConstraint`. The `init` function sets package-level `errBusy` to `sqlite3.ErrBusy`, appends the duplicate checker, and registers `sqlite3` with `newSQLMeta`.

## Control Flow

The only control flow is package initialization. SQLite-specific DSN defaults are handled in `newSQLMeta`: shared cache is enabled unless explicitly configured, WAL journaling is selected by default, busy timeout defaults to 5000 ms, and `DirBatchNum["db"]` is reduced to respect SQLite variable limits.

## State And Persistence Behavior

This file does not write metadata directly. Its main persistence impact is making SQLite lock contention retryable and making unique-constraint detection available to shared insertion, clone, restore, and session-id conflict paths.

## Dependencies And Integration Points

It depends on `github.com/mattn/go-sqlite3` and shared globals `errBusy`, `dupErrorCheckers`, and `Register`. The `txn` function in `sql.go` serializes SQLite writers by using a single inode batch lock key.

## Risks And Edge Cases

The duplicate checker only matches unwrapped `sqlite3.Error` values. SQLite's single-writer model means high write concurrency is bottlenecked even with retry and WAL mode. Constraint errors are broad; treating all `ErrConstraint` values as duplicate-entry conflicts may conflate unique conflicts with other constraint failures.

## Test Signals

`TestSQLiteClient` runs the shared metadata test suite against a temporary SQLite database. `TestSQLiteBatchUpdateChunkRefs` specifically validates SQLite clone/delete behavior for chunk reference counts.
