# sources/distributed-fs/seaweedfs/weed/filer/postgres2/postgres2_store.go

## Purpose

`postgres2_store.go` initializes the bucket-aware PostgreSQL filer store. It shares pgx connection logic and SQL generation with the normal Postgres store while enabling abstract SQL bucket-table support and creating the default table.

## Important APIs, Types, and Functions

`PostgresStore2` embeds `abstract_sql.AbstractSqlStore`, asserts `filer.BucketAware`, and implements `GetName`, `Initialize`, and `initialize`. It uses `postgres.SqlGenPostgres`, `postgres.DefaultUpsertQuery`, and `postgres.OpenPGXDB`.

## Control Flow

Initialization reads create-table, upsert, connection, SSL, schema, pgbouncer, and pool settings; sets `SupportBucketTable`; builds a pgx connection string and redacted version; opens the DB; creates the default table; and runs collation configuration.

## State and Persistence Behavior

Metadata persists through abstract SQL tables with bucket table support enabled. Bucket lifecycle operations can create/drop tables via embedded abstract SQL behavior. Runtime state is the DB pool and generator.

## Dependencies and Integration Points

The file depends on the postgres package's generator/connection helper, `abstract_sql`, and bucket-aware filer integrations. It is used for deployments that want bucket-level table separation.

## Risks and Edge Cases

Manual connection string assembly has the same escaping considerations as the normal store. Default table creation errors abort initialization. Custom create-table templates must match abstract SQL expectations and collation needs.

## Test Signals

Tests should cover default table creation, bucket table lifecycle, pgbouncer/search-path behavior, SSL options, upsert defaults, collation fallback, and failure on bad create-table templates.
