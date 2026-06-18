# sources/distributed-fs/juicefs/pkg/meta/sql_pg.go

## Purpose

`sql_pg.go` provides PostgreSQL-specific registration for the SQL metadata backend. It imports the pgx stdlib driver, detects unique-constraint errors, and registers the `postgres` scheme with the shared SQL metadata constructor.

## Important APIs, Types, And Functions

`isPGDuplicateEntryErr` checks whether an error is `*pgconn.PgError` with SQLSTATE `23505`, PostgreSQL's unique-violation code. The `init` function appends that checker to `dupErrorCheckers` and calls `Register("postgres", newSQLMeta)`.

## Control Flow

There is no runtime control flow beyond package initialization. `newSQLMeta` in `sql.go` rewrites the logical `postgres` driver to `pgx`, prefixes the address with `postgres://`, validates that `search_path` contains at most one schema, and sets that schema on the xorm engine after connection.

## State And Persistence Behavior

This file does not persist metadata itself. It controls how PostgreSQL duplicate-key errors are classified by the shared SQL backend, affecting transaction retry, id collision handling, and backup restore upserts.

## Dependencies And Integration Points

It depends on `github.com/jackc/pgx/v5/pgconn` and imports `github.com/jackc/pgx/v5/stdlib` for driver registration. It integrates with `dupErrorCheckers`, `Register`, and the PostgreSQL branch in `newSQLMeta`.

## Risks And Edge Cases

Only direct `*pgconn.PgError` values are recognized; wrapped errors may not match unless upstream preserves the concrete type. PostgreSQL duplicate-key errors can represent either benign races or real data corruption depending on call site, so the shared retry behavior must remain carefully scoped.

## Test Signals

`TestPostgreSQLClient` runs shared metadata tests when a local PostgreSQL database is available and `SKIP_NON_CORE` is not true. `TestPostgreSQLClientWithSearchPath` verifies that multiple schemas in `search_path` are rejected with the expected message.
