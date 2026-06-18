# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_store.go

## Purpose

`postgres_store.go` initializes the non-bucket PostgreSQL filer store using pgx. It configures connection strings, SSL parameters, schema/search path behavior, upsert defaults, and list-order detection for the abstract SQL backend.

## Important APIs, Types, and Functions

`PostgresStore` embeds `abstract_sql.AbstractSqlStore` and implements `GetName`, `Initialize`, and `initialize`. It uses `SqlGenPostgres`, `DefaultUpsertQuery`, and `OpenPGXDB`.

## Control Flow

Initialization sets defaults for idle connections and upsert, reads connection/SSL/schema/pgbouncer settings, enables non-bucket mode, selects the upsert template, builds a pgx connection string with `connect_timeout=30`, redacts password in the adapted URL, omits `search_path` when pgbouncer-compatible mode is requested, opens the DB through `OpenPGXDB`, and configures list ordering.

## State and Persistence Behavior

The embedded abstract SQL store persists metadata in the default table and keeps runtime state in the `sql.DB` pool and generator. This store does not create the table itself in this file and does not support bucket tables.

## Dependencies and Integration Points

The file depends on pgx, `abstract_sql`, `pgxutil` via `OpenPGXDB`, and Postgres collation detection. It integrates with normal filer metadata operations through the embedded store.

## Risks and Edge Cases

Connection string assembly is manual; values containing spaces or special characters rely on pgx keyword parsing behavior. Pgbouncer compatibility disables search path injection. Upsert is enabled by default to avoid duplicate-key errors poisoning PostgreSQL transactions.

## Test Signals

Integration tests should cover SSL options, schema versus pgbouncer behavior, upsert enable/disable, password redaction, collation fallback, and basic abstract store CRUD/listing.
