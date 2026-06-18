# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen_test.go

## Purpose

`postgres_sql_gen_test.go` tests PostgreSQL SQL generation and byte-ordered collation classification. It protects default upsert behavior and list SQL correctness.

## Important APIs, Types, and Functions

The tests cover `SqlGenPostgres.GetSqlInsert`, list query generation with and without `ForceBinaryCollation`, `DefaultUpsertQuery`, and `isByteOrderedCollation`.

## Control Flow

Tests instantiate generators, inspect generated SQL strings, assert presence/absence of `ON CONFLICT` and `COLLATE`, and classify known byte-ordered versus locale-aware collation names.

## State and Persistence Behavior

No database is used. The tests validate string generation only.

## Dependencies and Integration Points

The file depends on Go `testing` and `strings`. It protects SQL used by abstract SQL stores.

## Risks and Edge Cases

Substring tests do not execute SQL and may miss invalid placeholder ordering or schema mismatch. Collation classification is a whitelist and may need expansion for platform-specific byte-ordered names.

## Test Signals

Signals are default `ON CONFLICT` presence, plain insert fallback, no default collation forcing, `COLLATE "C"` applied to order/filter/pagination when forced, and correct collation classification.
