# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_collation.go

## Purpose

`mysql_collation.go` detects whether the MySQL `filemeta.name` column uses byte-ordered collation. If not, it forces generated listing SQL to use `BINARY name` so S3 listings remain byte-lexicographic.

## Important APIs, Types, and Functions

`ConfigureListOrdering` inspects the live database and mutates `SqlGenMysql.ForceBinaryCollation`. `nameColumnCollation` queries `information_schema.COLUMNS`. `isBinaryCollation` recognizes empty, `binary`, and `*_bin` collations.

## Control Flow

On initialization, MySQL stores call `ConfigureListOrdering`. It queries the effective column collation; on query failure it logs at verbosity 1 and leaves default SQL unchanged. If the collation is not binary, it flips the generator flag and logs a warning explaining correctness and performance implications.

## State and Persistence Behavior

No durable state is changed. The generator flag affects subsequent list SQL generation in memory. Operators must alter the database schema themselves for indexed byte ordering.

## Dependencies and Integration Points

The file depends on `database/sql`, `abstract_sql.DEFAULT_TABLE`, `SqlGenMysql`, and SeaweedFS logging. It integrates with S3 list semantics and SQL store initialization.

## Risks and Edge Cases

The fallback `BINARY` expression can prevent index-ordered scans and cause filesorts. If the collation check fails, the store may keep locale ordering and produce list order mismatches. The information-schema query assumes the current database is the active schema.

## Test Signals

Unit tests cover `isBinaryCollation`; integration tests should cover real binary and non-binary columns and verify generated SQL changes after configuration.
