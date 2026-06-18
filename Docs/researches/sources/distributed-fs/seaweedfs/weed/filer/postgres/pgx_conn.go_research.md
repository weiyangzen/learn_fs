# sources/distributed-fs/seaweedfs/weed/filer/postgres/pgx_conn.go

## Purpose

`postgres/pgx_conn.go` preserves a small compatibility entry point for opening PostgreSQL connections with pgx-backed utilities. It lets existing callers keep using `postgres.OpenPGXDB` while centralizing implementation in `util/pgxutil`.

## Important APIs, Types, and Functions

The only function is `OpenPGXDB(sqlUrl, adaptedSqlUrl string, pgbouncerCompatible bool, maxIdle, maxOpen, maxLifetimeSeconds int) (*sql.DB, error)`.

## Control Flow

The function immediately delegates to `pgxutil.OpenDB` with the same arguments and returns its result.

## State and Persistence Behavior

No state is held here. The returned `sql.DB` pool and its persistence behavior are controlled by `pgxutil.OpenDB` and the PostgreSQL server.

## Dependencies and Integration Points

The file depends on `database/sql` and `github.com/seaweedfs/seaweedfs/weed/util/pgxutil`. It is used by both postgres and postgres2 filer stores.

## Risks and Edge Cases

The wrapper can hide changes in the underlying utility from callers. Since it is a compatibility alias, removing it would break postgres2 and external package references.

## Test Signals

Coverage is mostly through postgres store initialization tests. A unit test could verify argument forwarding with a fake only if the utility were abstracted.
