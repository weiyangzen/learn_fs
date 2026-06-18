# sources/cloud-native/buildkit/cache/metadata/metadata.go

## Purpose

`cache/metadata/metadata.go` implements a small Bolt-backed metadata database used by BuildKit cache records. It stores per-record JSON values, secondary indexes, and larger external byte blobs. It provides in-memory `StorageItem` snapshots with queued transactional writes and thread-safe value access.

## Important APIs, Types, and Functions

- `Store` wraps a `db.DB` and exposes `NewStore`, `DB`, `All`, `Probe`, `Search`, `View`, `Clear`, `Update`, `Get`, and `Close`.
- Buckets are `_main` for record values, `_index` for secondary index entries, and `_external` for external byte payloads.
- `StorageItem` carries `id`, `values`, `queue`, mutexes, and a pointer back to `Store`.
- `StorageItem` methods include `Update`, `Keys`, `Get`, `GetExternal`, `SetExternal`, `Queue`, `Commit`, `Indexes`, `SetValue`, `ClearIndex`, `GetAndSetValue`, and helpers.
- `Value` stores JSON raw message plus optional index string; `NewValue` marshals arbitrary values; `Unmarshal` decodes into typed targets.
- `ErrSkipSetValue` lets compare-and-update callbacks intentionally avoid writing.

## Control Flow

`NewStore` opens the Bolt database and refuses to silently use a v1 legacy `metadata.db` beside a missing v2 database path, forcing explicit migration or removal. `All` scans `_main`, constructs `StorageItem` objects from nested buckets, and returns them in Bolt iteration order. `Get` returns an existing populated item plus `ok=true`, or an empty mutable item with `ok=false` so callers can queue creation writes.

Writes go through `Store.Update` to create the main bucket and record bucket. `StorageItem.Queue` accumulates bucket-mutating closures under `qmu`; `Commit` executes them in one update transaction and clears the queue only after success. `SetValue` updates the in-memory map and Bolt value while maintaining index entries. `Clear` deletes external data, removes index entries recorded by the storage item, and deletes the main record bucket.

`Search` scans `_index` by exact index key or prefix, resolves matching record IDs back through `_main`, logs stale index entries, and returns storage items. `Probe` is a cheaper existence check for an index prefix.

## State and Persistence Behavior

Each metadata value is JSON encoded with an optional secondary index. Index keys are stored as `index::recordID`, allowing multiple records under the same index prefix. External payloads are scoped by record ID and key under `_external`. `StorageItem` maintains an in-memory value map, so successful writes update both Bolt and the local snapshot. `GetExternal` copies Bolt byte slices before returning because Bolt buffers are invalid after the view transaction.

## Dependencies and Integration Points

The store uses BuildKit `util/db` and `boltutil` abstractions over bbolt, BuildKit logging for stale index diagnostics, and pkg/errors for stack wrapping. It is consumed by `cache/metadata.go`, which layers cache-specific schema and public ref metadata on top.

## Risks and Edge Cases

- `SetValue` adds new index entries but only clears old indexes when deleting a value; callers changing an indexed value need to ensure old indexes are not left stale unless storage semantics elsewhere handle it.
- `Search` has a `continue` path for malformed index keys before advancing the cursor; malformed keys matching the search prefix could loop forever.
- `Commit` clears the queued operations inside the update callback after all functions succeed. If a later function fails, earlier in-memory mutations may have happened before transaction rollback.
- `Get` intentionally returns an empty item for missing records; callers must check `ok` before assuming persistence.
- Legacy metadata detection blocks startup rather than attempting automatic migration.

## Test Signals

`metadata_test.go` validates value queue/commit/reopen behavior, `All`, `Clear`, exact index search cleanup, and external data storage/removal. Cache integration tests validate higher-level schema use.
