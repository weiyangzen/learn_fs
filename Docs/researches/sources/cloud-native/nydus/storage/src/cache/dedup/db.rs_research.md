# sources/cloud-native/nydus/storage/src/cache/dedup/db.rs

## Purpose
`dedup/db.rs` implements the SQLite persistence layer for local content-addressable deduplication. It records cache blob file paths and maps chunk digest keys to file offsets so later cache entries can reuse already-downloaded chunks.

## Important APIs, Types, And Functions
`CasDb` owns an `r2d2` pool of `rusqlite` connections. `new` appends `cas.db` to a directory; `from_file` opens/creates the database, enables WAL journal mode, creates `Blobs` and `Chunks` tables, and creates an index on `Chunks(ChunkId)`. Blob APIs include `get_blob_id_with_tx`, `get_blob_id`, `get_blob_path`, `get_all_blobs`, `add_blobs`, `add_blob`, and `delete_blobs`. Chunk APIs include `get_chunk_info`, `add_chunks`, and `add_chunk`. `begin_transaction` creates immediate transactions with rollback-on-drop, and `get_connection` installs a busy handler.

## Control Flow
Initialization opens a read-write/create SQLite database and ensures schema availability. Adding chunks first resolves the blob path to `BlobId`, then inserts `(ChunkId, ChunkOffset, BlobId)` with conflict-ignore semantics. Querying a chunk joins `Chunks` to `Blobs`, orders by `BlobId`, and returns the first matching file path and offset. Deleting blobs removes chunk rows first, then blob rows, inside one immediate transaction.

## State And Persistence Behavior
Persistent state is held in `cas.db`. `Blobs` maps integer ids to unique file paths. `Chunks` stores many chunk keys per blob with uniqueness on `(ChunkId, BlobId)`, allowing the same chunk key to exist in multiple files. WAL mode improves concurrent read/write behavior. Transactions are used for batch blob/chunk mutations and rollback automatically if dropped before commit.

## Dependencies And Integration Points
The module depends on `r2d2`, `r2d2_sqlite`, `rusqlite`, and the parent dedup module’s `Result<CasError>`. `CasMgr` uses it to record cache chunks, look up dedup sources, and remove stale blob records during garbage collection.

## Risks And Edge Cases
`add_blob` returns `last_insert_rowid`, which is meaningful for newly inserted rows but can be misleading after `INSERT OR IGNORE` for an already-existing blob; current callers do not rely on the returned id for existing rows. In `add_chunks`/`add_chunk`, missing blob ids become SQL `NULL` values through `Option<u64>` binding, which may create chunk records with no valid blob association unless SQLite constraints reject the row; callers normally add the blob first. The busy handler always returns true, so lock waits can be unbounded. Foreign keys are declared but SQLite foreign-key enforcement is not explicitly enabled.

## Test Signals
Tests cover blob insertion/query/deletion, reopening the same database, listing blobs, adding chunks, first-match lookup across duplicate chunk keys, and deletion cascading behavior implemented manually by deleting chunks before blobs.
