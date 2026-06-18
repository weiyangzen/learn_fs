# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen_test.go

## Purpose

`mysql_sql_gen_test.go` tests MySQL SQL generation and collation helper behavior. It guards compatibility choices around default upsert syntax and byte-ordered list SQL.

## Important APIs, Types, and Functions

Tests cover `SqlGenMysql.GetSqlInsert`, list query generation, `ForceBinaryCollation`, `DefaultUpsertQuery`, and `isBinaryCollation`.

## Control Flow

The tests instantiate generators with and without upsert templates, inspect generated SQL strings, and assert expected substrings or absent substrings. Collation tests classify known binary and case-insensitive collation names.

## State and Persistence Behavior

No database state is touched; these are pure string-generation tests.

## Dependencies and Integration Points

The file uses Go's testing package and string containment checks. It protects SQL consumed by `abstract_sql.AbstractSqlStore`.

## Risks and Edge Cases

String-substring tests can miss placeholder ordering errors or invalid SQL grammar. They do not execute generated SQL against MySQL or MariaDB.

## Test Signals

Signals include `ON DUPLICATE KEY UPDATE` in default upsert, no MySQL 8 alias syntax, plain insert when no template is configured, and `BINARY name` applied consistently to ordering, prefix filter, and pagination comparisons.
