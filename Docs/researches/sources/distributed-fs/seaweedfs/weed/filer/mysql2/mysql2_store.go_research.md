# sources/distributed-fs/seaweedfs/weed/filer/mysql2/mysql2_store.go

## Purpose

`mysql2_store.go` initializes the bucket-aware MySQL filer store. It uses the same MySQL SQL generator as the normal store but enables abstract SQL support for per-bucket tables and creates the default table during startup.

## Important APIs, Types, and Functions

`MysqlStore2` embeds `abstract_sql.AbstractSqlStore`, implements `filer.BucketAware`, and provides `GetName`, `Initialize`, and `initialize`. It uses `mysql.SqlGenMysql` and `mysql.DefaultUpsertQuery`.

## Control Flow

Initialization sets defaults, reads create-table and connection options, enables `SupportBucketTable`, chooses an upsert template, builds a MySQL connection URL with optional `interpolateParams`, opens the DB via `database/sql`, configures the pool, pings, creates the default table unless the error text says it already exists, and configures list ordering based on collation.

## State and Persistence Behavior

Metadata persists through abstract SQL tables, with bucket support enabled so bucket lifecycle can map data into separate tables. Runtime state is the DB pool plus generator. Unlike `mysql_store.go`, TLS and arbitrary DSN support are not present in this older-style initializer.

## Dependencies and Integration Points

The file depends on the MySQL driver, `abstract_sql`, MySQL SQL generator/collation helpers, and `filer.BucketAware`. It integrates with bucket create/drop paths through embedded abstract SQL behavior.

## Risks and Edge Cases

The error path after `sql.Open` calls `store.DB.Close()` even when `store.DB` may be nil if open failed before assignment. Existing-table detection relies on substring text. Password redaction uses a separately built adapted URL. TLS options available in `mysql_store.go` are not exposed here.

## Test Signals

Tests should cover default table creation, bucket table create/drop behavior, existing table errors, upsert enable/disable, collation fallback, connection pool settings, and failure handling for bad credentials or unavailable DB.
