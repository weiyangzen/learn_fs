# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen.go

## Purpose

`mysql_sql_gen.go` generates MySQL SQL statements for SeaweedFS's abstract SQL filer store. It supports configurable table creation/drop, optional upsert, and byte-order fallback for listings.

## Important APIs, Types, and Functions

`SqlGenMysql` implements `abstract_sql.SqlGenerator`. It provides `GetSqlInsert`, `GetSqlUpdate`, `GetSqlFind`, `GetSqlDelete`, `GetSqlDeleteFolderChildren`, list query methods, create/drop methods, and the private `nameExpr`. `DefaultUpsertQuery` uses `ON DUPLICATE KEY UPDATE`.

## Control Flow

Each method formats a table name into a template. Insert uses a configured upsert template when present, otherwise plain insert. List queries use `nameExpr`, which returns `BINARY name` when `ForceBinaryCollation` is set, and apply the same expression to pagination comparisons, prefix `LIKE`, and `ORDER BY`.

## State and Persistence Behavior

The file does not execute SQL itself. It determines the statements used by `abstract_sql.AbstractSqlStore` to persist metadata rows keyed by `dirhash`, `name`, and `directory`.

## Dependencies and Integration Points

It depends on the MySQL driver import for registration and the abstract SQL store interface. MySQL and MySQL2 stores install this generator during initialization.

## Risks and Edge Cases

Custom templates must match placeholder order expected by `abstract_sql`. `DefaultUpsertQuery` intentionally uses `VALUES(meta)` for MariaDB compatibility; changing to MySQL 8 row-alias syntax could break MariaDB. Binary fallback may sacrifice index use.

## Test Signals

Tests should cover upsert/default insert generation, table quoting, binary list expressions for exclusive/inclusive pagination, and custom template formatting.
