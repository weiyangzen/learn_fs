# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_store.go

## Purpose

`mysql_store.go` initializes the non-bucket MySQL filer store. It configures DSN/TLS/connection pooling, installs the MySQL SQL generator, enables upsert by default, and configures retry handling for deadlocks and lock wait timeouts.

## Important APIs, Types, and Functions

`MysqlStore` embeds `abstract_sql.AbstractSqlStore` and implements `GetName` and `Initialize`. `initialize` handles all connection and generator setup. `maskedDSN` redacts passwords for error messages. `CONNECTION_URL_PATTERN` builds a default utf8mb4 binary-collated DSN.

## Control Flow

Initialization sets defaults for idle connections and upsert, reads configuration, selects the upsert template, configures `SqlGenMysql`, sets a retry callback for MySQL error 1213 and 1205, parses or builds a DSN, optionally installs a per-connector TLS config, opens a `sql.DB` via `mysql.NewConnector`, configures pool sizes/lifetime, pings the database, and runs collation detection.

## State and Persistence Behavior

Persistent metadata behavior is handled by `abstract_sql`: rows in the default table keyed by `dirhash`, `name`, and `directory`. This store does not support bucket-specific tables. Runtime state includes the DB pool, generator, and retry callback.

## Dependencies and Integration Points

The file depends on `go-sql-driver/mysql`, TLS certificate loading, `abstract_sql`, and MySQL collation detection. It integrates with all common filer store methods through the embedded abstract SQL store.

## Risks and Edge Cases

TLS config is per connector, avoiding global driver config conflicts. Empty CA means system trust roots are used. If either client cert or key path is set, both must load. Custom DSNs can override defaults and may not use binary collation. Retryable errors are limited to deadlock and lock-wait timeout.

## Test Signals

Integration tests should cover DSN parsing, password masking, TLS with system roots and mTLS, upsert default/disable, retry callback behavior, pool settings, collation fallback, and basic abstract store CRUD/list operations.
