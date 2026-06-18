# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen.go

## Purpose

`postgres_sql_gen.go` generates PostgreSQL SQL statements for the abstract SQL filer store. It supports optional upsert, table create/drop templates, and `COLLATE "C"` fallback for byte-ordered listings.

## Important APIs, Types, and Functions

`SqlGenPostgres` implements `abstract_sql.SqlGenerator`. It defines `DefaultUpsertQuery`, `GetSqlInsert`, update/find/delete/delete-children, inclusive/exclusive list queries, create/drop methods, and `nameExpr`.

## Control Flow

Methods format a quoted table name into SQL strings with `$1`-style placeholders. Insert uses configured upsert when available; the default upsert uses `ON CONFLICT (dirhash, name)` and updates `directory` and `meta`. List queries apply `nameExpr` consistently to pagination comparisons, prefix `like`, and ordering.

## State and Persistence Behavior

The generator does not persist state directly. Its statements are executed by `abstract_sql.AbstractSqlStore` against rows keyed by `dirhash`, `name`, and `directory`.

## Dependencies and Integration Points

It depends on pgx stdlib driver registration and the abstract SQL generator interface. Postgres and Postgres2 stores install it during initialization.

## Risks and Edge Cases

Custom templates must preserve placeholder order and conflict semantics. The default conflict target omits `directory`, matching the abstract schema's uniqueness expectations; mismatched schemas can break upsert. Collation fallback may cost performance.

## Test Signals

Tests should cover quoted table names, upsert/plain insert switching, conflict-safe default, and consistent `COLLATE "C"` use in list comparisons/order.
