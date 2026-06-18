# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_collation.go

## Purpose

`postgres_collation.go` detects whether PostgreSQL list ordering for `filemeta.name` is byte-ordered. If not, it configures SQL generation to use `COLLATE "C"` so S3 listings remain byte-lexicographic.

## Important APIs, Types, and Functions

`ConfigureListOrdering` mutates `SqlGenPostgres.ForceBinaryCollation`. `nameColumnCollation` queries the column collation and database default collation. `isByteOrderedCollation` recognizes `C`, `POSIX`, `C.UTF-8`, and `C.UTF8`.

## Control Flow

At store startup, the function queries information schema and `pg_database`. If a column collation is null or empty, it uses the database default. Query failures are logged and leave default SQL unchanged. Locale-aware collations trigger generator fallback and a warning.

## State and Persistence Behavior

No schema is changed. The in-memory generator flag changes future list SQL to use `name COLLATE "C"`, which may be slower unless the schema/index supports that collation.

## Dependencies and Integration Points

The file depends on `database/sql`, `abstract_sql.DEFAULT_TABLE`, Postgres SQL generator, and logging. It protects S3 ListObjects ordering behavior for PostgreSQL-backed filers.

## Risks and Edge Cases

If detection fails, listings may remain locale-ordered. The fallback can require sorts and reduce index effectiveness. ICU or custom collations are treated as locale-aware unless explicitly recognized.

## Test Signals

Unit tests cover collation classification; integration tests should check real C and locale databases, generated SQL after configuration, and list order with mixed-case/non-ASCII names.
