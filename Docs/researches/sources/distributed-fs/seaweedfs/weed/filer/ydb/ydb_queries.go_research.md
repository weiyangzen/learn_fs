# sources/distributed-fs/seaweedfs/weed/filer/ydb/ydb_queries.go

## Purpose

`ydb/ydb_queries.go` defines YDB SQL query templates for filer metadata and KV operations. It was read as a complete 73-line file.

## Important APIs, Types, and Functions

Constants include `upsertQuery`, `deleteQuery`, `findQuery`, `deleteFolderChildrenQuery`, `listDirectoryQuery`, and `listInclusiveDirectoryQuery`. Each embeds `PRAGMA TablePathPrefix("%v")` and typed YDB parameter declarations.

## Control Flow

No Go runtime flow beyond constant use. `withPragma` in `ydb_types.go` formats these templates with a concrete table prefix before execution.

## State and Persistence Behavior

Queries operate on `abstract_sql.DEFAULT_TABLE`, using `(dir_hash, directory, name)` keys, `meta`, and optional `expire_at`.

## Dependencies and Integration Points

Depends on abstract SQL default table naming and YDB query syntax. Used by `YdbStore` entry and KV methods.

## Risks and Edge Cases

`LIKE prefix+"%"` semantics may treat SQL wildcard characters in prefixes specially. Template formatting must never accept untrusted table prefixes.

## Test Signals

YDB integration tests should cover upsert/find/delete/list inclusive/exclusive, prefix listing with special characters, and folder child deletion.
