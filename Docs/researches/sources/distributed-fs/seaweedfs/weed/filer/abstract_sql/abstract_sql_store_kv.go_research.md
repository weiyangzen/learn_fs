# sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store_kv.go

## Purpose
This file adapts `AbstractSqlStore` to SeaweedFS's simple key-value store interface by encoding arbitrary byte keys into the same SQL table shape used for filer metadata.

## Important APIs, Types, and Functions
- `KvPut` inserts a key/value pair and falls back to update on duplicate insert.
- `KvGet` retrieves the stored bytes and maps `sql.ErrNoRows` to `filer.ErrKvNotFound`.
- `KvDelete` deletes a key.
- `GenDirAndName` pads keys to at least 8 bytes, derives an int64 directory hash from the first eight bytes, and base64 encodes the directory and name components.

## Control Flow and State
All KV operations call `getTxOrDB` without bucket mapping and use `DEFAULT_TABLE`. `KvPut` computes `(dirStr, dirHash, name)`, attempts insert, logs duplicate fallback, then updates. `KvGet` runs the generated find statement and scans the metadata column directly into the value byte slice. `KvDelete` uses the generated delete statement.

## State and Persistence Behavior
The first eight key bytes form the directory partition and hash, while remaining bytes become the encoded name. Values are stored as raw bytes in the metadata column, not as encoded `Entry` protobufs. Short keys are padded with zero bytes, so callers must treat the key encoding as store-internal and not expect a reversible textual key.

## Dependencies and Integration Points
It shares SQL statement generation, transaction selection, and DB connection handling with `AbstractSqlStore`. It integrates with the filer KV interface and `util.BytesToUint64`.

## Risks and Edge Cases
- Short keys are padded in a local slice copy, making keys with trailing zero differences potentially non-obvious.
- Duplicate detection logs regardless of exact duplicate cause; comments intentionally avoid returning non-duplicate insert errors before fallback.
- The same `filemeta` table may contain both metadata rows and KV rows, so key partitioning must avoid collision with real filer directory/name pairs.
- `RowsAffected` behavior is driver-specific.

## Test Signals
Useful tests should cover put/get/delete, overwrite fallback, short keys, binary keys, transaction context use, and compatibility with SQL generator predicates. No local tests are listed.
