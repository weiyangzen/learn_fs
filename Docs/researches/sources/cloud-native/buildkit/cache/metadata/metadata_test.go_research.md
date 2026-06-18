# sources/cloud-native/buildkit/cache/metadata/metadata_test.go

## Purpose

`metadata_test.go` provides focused unit coverage for the generic metadata store. It verifies basic value persistence, all-record enumeration, clearing records, exact index search, index cleanup on clear, and external byte payload handling.

## Important APIs, Types, and Functions

- `TestGetSetSearch` exercises `NewStore`, missing `Get`, `NewValue`, `Queue`, `Commit`, reopen persistence, `All`, `Clear`, and post-clear `Get`.
- `TestIndexes` writes three records with indexed values, searches exact index values, and verifies `Clear` removes index entries.
- `TestExternalData` verifies `SetExternal`, `GetExternal`, missing external data errors, persistence across `Get`, and external cleanup after `Clear`.

## Control Flow

Each test uses `t.TempDir()` and a standalone `storage.db`. Tests create missing `StorageItem` placeholders via `Get`, queue or set data, commit, and inspect the store before and after close/reopen or clear. The index test creates multiple records with overlapping and distinct indexes, then searches `tag:baz` and `tag:bax` to confirm matching record IDs.

## State and Persistence Behavior

The tests confirm queued writes create real records, JSON values survive store reopen, `All` returns created records, `Clear` removes main records and indexes, and external data is scoped to record IDs and deleted with the record. They also demonstrate that a missing `Get` returns a usable item for creation.

## Dependencies and Integration Points

The tests use bbolt bucket closures directly when queuing `SetValue`, `testify/require` assertions, and Go temporary directories. They do not depend on the higher-level cache manager, making them a narrow signal for the storage package.

## Risks and Edge Cases

- Coverage is exact-index oriented; prefix search and `Probe` are not directly tested.
- The tests do not exercise changing an indexed value to a different index, malformed index keys, concurrent `Queue`/`Commit`, or transaction rollback behavior after partial queued mutations.
- External data is tested only with small byte slices.

## Test Signals

These tests are the direct regression net for `cache/metadata/metadata.go`; they support cache manager confidence by proving the basic storage primitives work across close/reopen and cleanup.
