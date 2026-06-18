# sources/cloud-native/nydus/src/bin/nydus-image/deduplicate.rs

## Purpose
This Rust module implements chunk deduplication metadata persistence and chunkdict generation for `nydus-image`. It stores blob/chunk metadata from RAFS bootstraps in SQLite, validates bootstrap version compatibility, updates build context from parent bootstraps, and implements dictionary selection algorithms based on cross-image clustering and version-level exponential smoothing.

## Important APIs, Types, And Functions
`DatabaseError` wraps SQLite and poisoned mutex errors. `Database` abstracts table creation, inserts, and lookups. `SqliteDatabase` owns `ChunkTable` and `BlobTable`. `get_fs_version`, `check_bootstrap_versions_consistency`, and `update_ctx_from_parent_bootstrap` inspect bootstraps and mutate `BuildContext`. `Deduplicate<SqliteDatabase>::new` opens file or in-memory DB. `save_metadata` loads a bootstrap, creates tables, inserts blob info, walks the RAFS tree, and records each chunk with image reference and version. `Algorithm<SqliteDatabase>` loads chunks and runs `chunkdict_generate`. Algorithm helpers include `fill_chunkdict`, `exponential_smoothing`, `distance`, `divide_by_image`, `divide_set`, misspelled `dbsacn`, `expand_cluster`, `aggregate_chunk`, `deduplicate_image`, and `deduplicate_version`. `Table` abstracts SQL table operations. `ChunkTable`, `BlobTable`, `CustomString`, and `DataPoint` support storage and ordering. The test module covers ordering, table CRUD/paging, and algorithm behavior.

## Control Flow
Metadata ingestion loads RAFS metadata, extracts blob infos, creates SQLite tables if needed, inserts blob rows, builds a `Tree` from the bootstrap, walks DFS, and inserts chunk rows associated with the relevant blob ID. Generation loads all chunks, builds image-cluster dictionaries, builds per-version dictionaries, combines them, logs size, computes noise images, then expands selected chunks to include all chunks from any selected blob plus blob metadata.

## State And Persistence
The module persists two SQLite tables: `chunk` with image/version/blob/digest/crc/size/offset fields and `blob` with blob ID, sizes, compressor, and metadata chunk-info offsets/sizes. Table connections are protected by `Arc<Mutex<Connection>>`. In-memory DB mode is supported only when the URL is exactly `:memory:`.

## Dependencies And Integration Points
It depends on `nydus_rafs` for bootstrap/superblock/tree traversal, `nydus_builder` for `BuildContext`, conversion type, and chunkdict info structs, `nydus_storage::BlobInfo`, `nydus_api::ConfigV2`, and `rusqlite`. It is tied to `nydus-image` chunkdict CLI behavior and to smoke tests that inspect CAS/Chunks/Blobs counts.

## Risks
`SqliteDatabase::new` panics if the path exists but is not a file. `ChunkTable` and `BlobTable` open separate SQLite connections; in-memory mode creates separate private databases for chunk and blob tables, which is safe only because they are used independently. The DBSCAN implementation uses `min_points=10`, repeated O(n^2) distance scans, and mutates reusable `data_point` across radii, making large datasets expensive and behavior sensitive. `CustomString` ordering compares only extracted numeric sequences, so nonnumeric version distinctions can collapse in ordering. `chunkdict_generate` currently supports only `"exponential_smoothing"` by name even though image clustering is also invoked inside that path.

## Test Signals
Unit tests validate table insertion/listing/paging, version-string numeric ordering, distance calculation, train/test division, DBSCAN clustering, aggregate chunk selection, image deduplication, version deduplication, and smoothing output. Runtime smoke signals include CAS table population and chunkdict generation paths.
