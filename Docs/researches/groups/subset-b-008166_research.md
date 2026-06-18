# subset-b-008166 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/xml.rs -->
# sources/object-store/garage/src/api/s3/xml.rs

Purpose: defines the S3 API XML serialization DTOs used by Garage's S3 front end. The file re-exports common XML helpers (`to_xml_with_header`, namespace serializers, `Value`, `IntValue`) and provides strongly named response structs matching AWS S3 XML element names via serde rename attributes.

Important APIs/types/functions: `Bucket`, `Owner`, `BucketList`, `ListAllMyBucketsResult`, `LocationConstraint`, delete-result structures, multipart upload/list/list-parts structures, list-objects structures, `VersioningConfiguration`, `PostObject`, and ACL structures (`Grantee`, `Grant`, `AccessControlList`, `AccessControlPolicy`). The types are plain `Serialize` structs, mostly using `Value` for escaped string content and `IntValue` for numeric XML text. Optional fields use `skip_serializing_if` where AWS omits absent elements.

Control flow: there is no runtime logic beyond serde-driven serialization. Callers construct the relevant response struct, then pass it to the common XML serializer. Namespace fields are represented as unit fields with custom serializer functions.

State and persistence: stateless; no persistence. It encodes API response state provided by bucket/object/multipart handlers.

Dependencies and integration points: depends on `serde::Serialize` and `garage_api_common::xml`. It integrates with S3 handlers that need AWS-compatible XML payloads and with `garage_util::time` in tests for RFC3339 timestamps.

Risks: compatibility is sensitive to element names, optionality, namespace placement, checksum field spelling, XML escaping, and empty-element behavior. Any change can break S3 clients even without compile errors. The file has no schema validation, so tests are the main guard against drift.

Test signals: extensive unit tests snapshot XML strings for errors, bucket listing, location/versioning/ACL, delete result, multipart initiation/completion/listing, list objects v1/v2, and list parts. These tests are strong regression signals for serialization shape and escaping.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/xml.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/Cargo.toml -->
# sources/object-store/garage/src/block/Cargo.toml

Purpose: declares the `garage_block` Rust crate, described as the block manager for the Garage object store.

Important APIs/types/functions: configures `lib.rs` as the library root and exposes the crate under version `2.3.0`, edition 2018, AGPL-3.0. It defines the `system-libs` feature to pass through `zstd/pkg-config`.

Control flow: build-time only. Cargo resolves workspace dependencies and optional system-library linkage before compiling the block manager.

State and persistence: no runtime state, but dependency choices affect persistence-critical code in the block manager, including database access, RPC, compression, async IO, and metrics.

Dependencies and integration points: workspace crates `garage_db`, `garage_net`, `garage_rpc`, and `garage_util`; third-party crates include `opentelemetry`, `arc-swap`, `async-trait`, `bytes`, `bytesize`, `hex`, `tracing`, `rand`, `async-compression`, `zstd`, `serde`, `futures`, `tokio`, and `tokio-util`.

Risks: feature linkage for zstd must remain compatible with deployment packaging. Because the crate owns on-disk blocks and repair/resync workflows, dependency upgrades can affect data durability, async behavior, and compression interoperability.

Test signals: no direct manifest tests; validation comes from compiling the block crate and exercising block manager, repair, resync, and integration tests in dependent crates.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/block.rs -->
# sources/object-store/garage/src/block/block.rs

Purpose: defines the in-memory/path/stream representation of a Garage data block, including whether bytes are stored plain or zstd-compressed.

Important APIs/types/functions: `DataBlockHeader::{Plain, Compressed}`, generic `DataBlockElem<T>`, aliases `DataBlock`, `DataBlockPath`, and `DataBlockStream`, constructors `from_parts`, `plain`, `compressed`, accessors `into_parts` and `as_parts_ref`, `DataBlockHeader::is_compressed`, `DataBlock::verify`, `DataBlock::from_buffer`, and `zstd_encode`.

Control flow: `from_buffer` offloads optional compression to `tokio::task::spawn_blocking`; on successful zstd compression it returns a compressed block, otherwise it silently falls back to plain data. `verify` hashes plain bytes with `blake2sum`, while compressed blocks are validated by zstd decode into `sink` using the included checksum.

State and persistence: no persistence by itself, but `DataBlockHeader` drives on-disk extension choice and RPC stream metadata. The checksum-enabled `zstd_encode` affects long-term compatibility of compressed block files.

Dependencies and integration points: uses `bytes::Bytes`, `garage_util::data::Hash` and `blake2sum`, `garage_util::error::Error`, `garage_net::stream::ByteStream`, and `zstd`. Integrated by `manager.rs` for local writes, reads, RPC put/get, corruption detection, and compression policy.

Risks: compressed verification checks zstd integrity but not that decoded bytes hash to the requested block hash; this relies on the compressed frame checksum and immutable hash naming model. Compression failure fallback changes storage format without surfacing a warning. `spawn_blocking(...).await.unwrap()` will panic if the blocking task is cancelled/panics.

Test signals: no local unit tests in this file; covered indirectly by block IO, resync, and S3 object integration tests that write and read blocks.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/layout.rs -->
# sources/object-store/garage/src/block/layout.rs

Purpose: maps block hashes to local data directories and manages multi-drive layout migration for block files.

Important APIs/types/functions: `DataLayout` with `data_dirs`, marker map, primary partition vector, and secondary partition vectors; `DataDir` and `DataDirState::{Active, ReadOnly}`; `initialize`, `update`, `check_markers`, `primary_block_dir`, `secondary_block_dirs`, `without_secondary_locations`; helpers `make_data_dirs` and `dir_not_empty`.

Control flow: layout initialization splits 1024 hash partitions proportionally over active directory capacity. Existing non-empty directories become secondary locations for partitions they do not primarily own, preventing older data from being lost. `update` preserves old primary assignments where possible, moves excess primaries to secondary, fills unassigned partitions according to new capacities, and detects newly added non-empty directories as secondary sources.

State and persistence: `DataLayout` implements `InitialFormat` with marker `G09bmdl` and is persisted by `BlockManager` under metadata as `data_layout`. Per-directory `garage-marker` files bind persisted layout entries to actual mountpoints and prevent accidental mount/path swaps.

Dependencies and integration points: consumes `garage_util::config::DataDirEnum`, `bytesize` parsing, `hex`, `garage_util::data::Hash`, and migration/error helpers. Used by block manager to decide primary write directory, read fallback directories, rebalance traversal, and post-rebalance cleanup.

Risks: uses assertions for invariants such as nonzero active capacity and exactly 1024 partitions; invalid persisted/config state can panic. `dir_not_empty` treats marker files and hex-named directories as meaningful data, so unusual user files may influence secondary-location behavior. Marker mismatch errors are intentionally strict because wrong mounts can corrupt data placement assumptions.

Test signals: no file-local unit tests; test coverage is mostly operational/integration. Manual validation should cover single-dir, multiple active dirs, read-only dirs, capacity changes, removed dirs, non-empty added dirs, and marker mismatch cases.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/lib.rs -->
# sources/object-store/garage/src/block/lib.rs

Purpose: crate root for `garage_block`; wires modules and exposes the limited public surface needed by other Garage crates.

Important APIs/types/functions: public modules `manager`, `repair`, and `resync`; private modules `block`, `layout`, `metrics`, and `rc`; public re-exports `zstd_encode` and `CalculateRefcount`.

Control flow: no runtime logic. Module visibility intentionally keeps low-level block layout/metrics/reference-count internals crate-private.

State and persistence: none directly; persistence is delegated to module implementations.

Dependencies and integration points: imports tracing macros globally. Other crates typically interact through `manager::BlockManager`, repair/resync worker types, and `CalculateRefcount` callbacks.

Risks: re-export choices define crate boundary. Making internals public would increase compatibility burden; removing current re-exports can break model/admin integration.

Test signals: compile-time module linkage is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/manager.rs -->
# sources/object-store/garage/src/block/manager.rs

Purpose: central local/remote block storage manager. It stores immutable block files, exchanges blocks over RPC, tracks local reference counts, schedules resync/repair/scrub workers, and exposes operational metrics.

Important APIs/types/functions: constants `INLINE_THRESHOLD`, `BLOCK_GC_DELAY`, `BlockRpc`, `BlockManager`, `BlockResyncErrorInfo`; constructor `new`; worker hooks `spawn_workers`, `register_bg_vars`; public operations `rpc_get_block_streaming`, `rpc_put_block`, `block_incref`, `block_decref`, `get_block_rc`, `list_resync_errors`, `send_scrub_command`; local operations `read_block`, `write_block`, `find_block`, `fix_block_location`, `delete_if_unneeded`; RPC handler implementation.

Control flow: initialization loads or creates `DataLayout`, validates markers, persists layout, opens `block_local_rc`, creates `BlockResyncManager`, RPC endpoint, RAM buffer semaphore, metrics, and scrub persister. Writes compress optionally, reserve buffer memory for remote sends, and call target storage nodes with quorum. Local writes lock one of 256 hash-sharded mutation mutexes, write a random temp file, optionally fsync file and directory, then atomically rename and clean old location/format. Reads search primary then secondary directories, enforce a read semaphore timeout, verify data, quarantine corrupt files as `.corrupted`, and enqueue resync. RPC get iterates read candidates with timeout fallback.

State and persistence: persistent state includes block files under data directories, `data_layout` metadata file, directory marker files, `block_local_rc`, resync queue/error DB trees, and scrub/resync worker configs. `BLOCK_GC_DELAY` delays physical deletion after RC reaches zero. `data_fsync` controls file and directory durability.

Dependencies and integration points: integrates `garage_db`, `garage_rpc` endpoint/strategy/quorum helpers, `garage_net` streams, `garage_util` config/persister/background/time/metrics/error/data, `DataLayout`, `BlockRc`, `BlockResyncManager`, repair workers, and OpenTelemetry. It is consumed by model tables and admin local APIs for block repair/info.

Risks: block durability depends on temp-write/rename/fsync correctness and the `data_fsync` configuration. Compression preference affects `find_block` ordering and existing file reuse. Corrupt compressed data is not decoded to a hash before accepting the header-level verification result. Background enqueue after transaction commit is spawned immediately by `block_incref/decref`, so process crashes can delay resync scheduling unless repaired later. Quorum and layout calculations are critical during cluster reconfiguration.

Test signals: no local unit tests; behavior is covered by broader Garage integration tests and operational repair/resync paths. High-value tests include interrupted write temp cleanup, compressed/plain migration, corrupt file quarantine, secondary-location rebalance, and RPC fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/metrics.rs -->
# sources/object-store/garage/src/block/metrics.rs

Purpose: registers OpenTelemetry metrics for the block manager, including queue sizes, IO counters, resync outcomes, and corruption counts.

Important APIs/types/functions: `BlockManagerMetrics` struct and `BlockManagerMetrics::new`. Fields include value observers for compression level, RC size, resync queue length, errored blocks, and RAM buffer permits; counters/recorders for resync attempts/errors/duration/send/recv, bytes read/written, read semaphore timeouts, write/read durations, deletes, and corruptions.

Control flow: `new` binds meter instruments under meter name `garage_model/block`. Observer closures capture DB trees or semaphores and report current approximate values when scraped.

State and persistence: no persisted state. It observes persistent DB trees and runtime semaphore state.

Dependencies and integration points: depends on `opentelemetry`, `tokio::sync::Semaphore`, and `garage_db::Tree`. Constructed by `BlockManager::new`; updated throughout `manager.rs` and `resync.rs`.

Risks: observers call `approximate_len` and ignore failures; metrics can silently omit data when DB access fails. Metric names are part of monitoring contracts and should be changed carefully.

Test signals: no unit tests. Validation is compile-time plus runtime metrics scraping in deployments with telemetry enabled.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/rc.rs -->
# sources/object-store/garage/src/block/rc.rs

Purpose: implements local block reference-count storage and repair recalculation hooks.

Important APIs/types/functions: `CalculateRefcount`, `BlockRc`, `block_incref`, `block_decref`, `get_block_rc`, `clear_deleted_block_rc`, `recalculate_rc`, and internal `RcEntry::{Present, Deletable, Absent}` with parse/serialize/increment/decrement/state helpers.

Control flow: increments parse current DB entry and write a positive count. Decrements transition count 1 to `Deletable` with timestamp `now + BLOCK_GC_DELAY`; already zero states remain unchanged. `recalculate_rc` runs registered callbacks inside a DB transaction, compares calculated count to stored count, and writes either `Present` or delayed `Deletable`.

State and persistence: RC entries live in the `block_local_rc` tree. Format is 8-byte big-endian count for present, or 16 bytes with a zero prefix and deletion timestamp for deletable, preserving compatibility with older zero-count semantics.

Dependencies and integration points: uses `garage_db::Tree` and transactions, `arc_swap::ArcSwapOption` to publish recalculation callbacks, `garage_util::data::Hash`, and time helpers. `BlockManager` invokes it during metadata mutations, resync, repair, and admin block info.

Risks: invalid RC byte lengths panic with a corruption message. Decrementing an absent/deletable entry is idempotent rather than underflowing, which avoids crashes but can hide caller mistakes. Recalculation is unavailable until higher layers register callbacks, so early repair calls can fail.

Test signals: no direct tests here; DB test suite covers transaction mechanics, while block repair/resync integration should cover RC transitions and recalculation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/rc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/repair.rs -->
# sources/object-store/garage/src/block/repair.rs

Purpose: implements block repair, data scrub, rebalance, and block-store enumeration workers.

Important APIs/types/functions: `RepairWorker`, `ScrubWorker`, persisted `ScrubWorkerPersisted`, `ScrubWorkerCommand`, `RebalanceWorker`, `BlockStoreIterator`, `BsiTodo`, and helpers `randomize_next_scrub_run_time`, iterator `progress`/`next`.

Control flow: `RepairWorker` phase 1 batches RC-table hashes into the resync queue to avoid SQLite iterator/write deadlock, then phase 2 walks disk blocks and enqueues them too. `ScrubWorker` is a periodic/manual worker with running/paused/finished state, persisted checkpoints every minute, tranquility throttling, and command handling for start/pause/resume/cancel. It reads every block and increments persistent corruption count on `CorruptData`. `RebalanceWorker` scans blocks, moves files outside their primary location by re-reading/re-writing, and finally persists a layout without secondary locations.

State and persistence: scrub state persists in `scrub_info`, migrating from v081 to v082 with `time_next_run_scrub` and iterator checkpoint. Rebalance updates `data_layout`. Repair feeds persistent resync queue entries. Disk iterator state is serializable for checkpointing.

Dependencies and integration points: depends on `garage_util::background::Worker`, `PersisterShared`, `Tranquilizer`, time/data/error utilities, tokio filesystem/channel/watch, and the block manager. Admin repair commands trigger these worker paths through local admin APIs.

Risks: block-store enumeration assumes data directory structure and 64-hex filenames; extra files are mostly ignored but malformed block-like filenames can be considered. Directory progress division uses discovered entry count; empty directory branches need care. Repair phase batching is tailored around SQLite locking behavior. Rebalance removes secondary locations only after its scan completes, so interrupted runs leave conservative layout state.

Test signals: no local unit tests. Operational tests should cover scrub checkpoint resume, pause/cancel commands, corrupted block detection, SQLite repair batching, rebalance of secondary locations, and iterator progress invariants.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/repair.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/block/resync.rs -->
# sources/object-store/garage/src/block/resync.rs

Purpose: manages the asynchronous queue that reconciles local block files with local reference counts and cluster placement expectations.

Important APIs/types/functions: `BlockResyncManager`, persistent `ResyncPersistedConfig`, queue constants, `put_to_resync`, `put_to_resync_at`, `clear_backoff`, `clear_resync_queue`, `register_bg_vars`, `resync_iter`, `resync_block`, `ResyncWorker`, `ErrorCounter`, and `BusyBlock`.

Control flow: resync queue keys are timestamp plus hash, ordered by due time. Workers claim non-busy queue entries, honor due time and exponential backoff in `errors`, run `resync_block`, then clear or update error/backoff state. `resync_block` deletes locally unneeded blocks after optional offload to nodes that need them, clears deletable RC entries, or fetches missing needed blocks from remote storage nodes if the current layout says this node should store them.

State and persistence: persistent DB trees `block_local_resync_queue` and `block_local_resync_errors`; `resync_cfg` persists worker count and tranquility. Error counters encode two u64 values: consecutive errors and last try time. In-memory busy set prevents duplicate concurrent processing of the same queue key.

Dependencies and integration points: uses `garage_db`, `garage_util` background/persister/time/metrics/tranquilizer, `garage_rpc`, OpenTelemetry, and `BlockManager` read/write/delete/RPC methods. Exposed to admin block commands for listing errors and retrying backoff.

Risks: correctness depends on tolerating inconsistent queue/error state and ordering insert-before-remove to survive crashes. Missing needed block fetch can fail repeatedly until backoff; recalculating RC on missing remote data may repair metadata but also surfaces data-loss scenarios. Offload refuses when write quorum is unavailable, delaying deletion. The comment says no more than four workers, but the constant is eight, so operational expectations should follow the constant/API.

Test signals: no local tests; integration should verify backoff encoding, clear-backoff, queue persistence across restart, missing-block fetch, unneeded-block offload/delete, and multi-worker busy-set behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/block/resync.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/Cargo.toml -->
# sources/object-store/garage/src/db/Cargo.toml

Purpose: declares the `garage_db` crate, a transactional key/value abstraction over multiple embedded storage engines.

Important APIs/types/functions: configures `lib.rs`; features `default = ["lmdb", "sqlite"]`, `bundled-libs`, `lmdb`, `fjall`, and `sqlite`; optional dependencies for `heed`, `rusqlite`, `r2d2`, `r2d2_sqlite`, `fjall`, and `parking_lot`.

Control flow: Cargo feature resolution determines which adapters compile and which `Engine` values can be opened at runtime.

State and persistence: build-time feature choices select supported metadata DB formats. `bundled-libs` affects SQLite library linkage.

Dependencies and integration points: used by `garage`, `garage_model`, and block/table components. Development tests use `mktemp`.

Risks: disabling a feature makes that engine unavailable even though `Engine` still parses the name. Adapter dependency upgrades can affect locking, transaction behavior, snapshot semantics, and file format compatibility.

Test signals: crate tests in `test.rs` run per enabled feature and are the main cross-engine conformance signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/fjall_adapter.rs -->
# sources/object-store/garage/src/db/fjall_adapter.rs

Purpose: implements the `garage_db` facade over Fjall transactional keyspaces and partitions.

Important APIs/types/functions: `open_db`, `FjallDb`, `FjallDb::init`, `IDb` implementation, `FjallTx`, `ITx` implementation, iterator remappers, bound cloning helpers, and table-name `encode_name`/`decode_name`.

Control flow: opening rejects `metadata_fsync`, configures optional block cache size, and opens a transactional keyspace. `open_tree` encodes Garage tree names to safe Fjall partition names and tracks opened partitions in an `RwLock`. Single operations use read/write transactions and commit immediately. Cross-partition transactions use one `WriteTransaction`, commit on `TxFnResult::Ok`, and rollback on abort/db error.

State and persistence: Fjall partitions under `db.fjall` store Garage trees. Snapshots create a separate keyspace under the engine-specific path and copy all partitions from a read transaction before `persist(SyncAll)`.

Dependencies and integration points: depends on `fjall`, `parking_lot`, core `garage_db` traits, and `Engine::Fjall.db_path`. Used when `fjall` feature is enabled and selected in config/conversion.

Risks: marked experimental via `engine()`. Transactional `clear` is unimplemented, so user code calling `tx.clear` on Fjall will panic. Tree IDs opened after a transaction starts are intentionally invalid inside that transaction. Name encoding rejects non-byte-sized characters. Snapshot copy loops all entries and may be expensive.

Test signals: local `test_encdec_name`; shared DB test suite runs with `feature = "fjall"` and covers simple CRUD, transaction commit/abort, and iteration/range ordering.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/fjall_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/lib.rs -->
# sources/object-store/garage/src/db/lib.rs

Purpose: defines Garage's engine-neutral transactional key/value database API and internal adapter traits.

Important APIs/types/functions: `Db`, `Tree`, `Transaction`, `Error`, `TxOpError`, `TxError`, `TxResult`, `unabort`, `Db::{open_tree,list_trees,transaction,snapshot,import}`, `Tree` CRUD/iteration/range APIs, `Transaction` CRUD/iteration/on_commit APIs, internal traits `IDb`, `ITx`, `ITxFn`, and `TxFnResult`.

Control flow: `Db::transaction` wraps user closures in `TxFn`, delegates to the adapter, then reconciles adapter result with the closure's stored result. On successful commit, queued `on_commit` callbacks run after the adapter returns. `Db::import` rejects non-empty destination DBs, opens each source tree, and copies entries in a transaction while printing progress every 1000 items.

State and persistence: state is in adapter-specific trees. `Tree` is a lightweight handle with DB pointer and tree id. `on_commit` callbacks are volatile and run only after successful commit.

Dependencies and integration points: adapter modules are feature-gated; `open` is re-exported. Higher-level Garage tables rely on this stable contract for metadata persistence and transaction semantics.

Risks: `Db::transaction` has several subtle result combinations and panics on impossible states. Long imports happen inside one transaction per tree, which can stress memory/locks on large trees. Iterators expose boxed dynamic iterators and rely on adapters to preserve transaction lifetimes safely.

Test signals: `db/test.rs` validates CRUD, commit/abort, forward/reverse iteration, and ranges across adapters.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/lmdb_adapter.rs -->
# sources/object-store/garage/src/db/lmdb_adapter.rs

Purpose: implements `garage_db` on top of LMDB via the Heed crate.

Important APIs/types/functions: `open_db`, `LmdbDb`, `LmdbDb::init`, `IDb` implementation, `LmdbTx`, `ITx` implementation, self-referential iterator wrapper `TxAndIterator`, `tx_iter_item`, and `recommended_map_size`.

Control flow: opening creates the LMDB directory, configures max DBs/readers/map size, sets `NO_READ_AHEAD` and `NO_META_SYNC`, and adds `NO_SYNC` when fsync is disabled. It maps OutOfMemory to a detailed configuration error. `open_tree` creates named LMDB databases in a write transaction and caches handles. Transactions use one LMDB write transaction with commit/abort based on closure result.

State and persistence: LMDB environment stored under `db.lmdb`. Snapshots use compacting `copy_to_path`. Default map size is 1 TiB on 64-bit and 1 GiB on 32-bit.

Dependencies and integration points: depends on `heed`, `garage_db` traits, and `Engine::Lmdb.db_path`. Used as a default metadata engine and by DB conversion.

Risks: uses unsafe lifetime extension for read-transaction iterators; safety depends on iterator wrapper drop order. LMDB map-size and virtual-memory limits can prevent startup. `NO_SYNC` when fsync disabled trades durability for performance. Tree handles opened after transaction start are unavailable in that transaction.

Test signals: shared DB test suite runs under `feature = "lmdb"` and validates basic semantics; no adapter-specific tests for snapshot, map-size errors, or unsafe iterator edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/lmdb_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/open.rs -->
# sources/object-store/garage/src/db/open.rs

Purpose: provides runtime database engine selection and common open options.

Important APIs/types/functions: `Engine::{Lmdb, Sqlite, Fjall}`, `Engine::as_str`, `Engine::db_path`, `Display`, `FromStr`, `OpenOpt`, and `open_db`.

Control flow: parses engine aliases (`heed` for LMDB, `sqlite3`/`rusqlite` for SQLite), rejects `sled` with migration guidance, and dispatches `open_db` to feature-gated adapter modules. If a valid engine is not compiled in, it returns a clear support-not-available error.

State and persistence: engine-specific paths are `db.lmdb`, `db.sqlite`, and `db.fjall` under a base metadata path. `OpenOpt` carries `fsync`, LMDB map size, and Fjall block-cache size.

Dependencies and integration points: used by Garage startup, local DB conversion CLI, and config parsing paths.

Risks: `Engine` lists all supported engines independent of compile features, so command-line/config validation can succeed and runtime open can still fail. Path conventions are part of migration/conversion tooling.

Test signals: indirectly covered by adapter tests and CLI conversion compile checks.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/open.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/sqlite_adapter.rs -->
# sources/object-store/garage/src/db/sqlite_adapter.rs

Purpose: implements `garage_db` using SQLite through rusqlite and an r2d2 connection pool.

Important APIs/types/functions: `open_db`, `SqliteDb`, `SqliteDb::open`, `IDb` implementation, `SqliteTx`, `ITx` implementation, iterator wrappers `DbValueIterator` and `TxValueIterator`, `bounds_sql`, and `iter_next_row`.

Control flow: opening sets `journal_mode=WAL` and `synchronous=NORMAL` or `OFF` based on fsync. Tree names become SQL tables prefixed with `tree_`, with `:` escaped as `_COLON_`. Single writes take `write_lock` to emulate one writer. Transactions take the same lock and run a rusqlite transaction. Iteration builds SQL queries with ordered `SELECT k, v` and range predicates generated by `bounds_sql`.

State and persistence: SQLite database file is `db.sqlite`; each Garage tree is a table with BLOB primary key and BLOB value. Snapshots use `VACUUM INTO` to write a compact copy.

Dependencies and integration points: depends on `rusqlite`, `r2d2`, `r2d2_sqlite`, core DB traits, and `Engine::Sqlite.db_path`. Used as a default metadata engine and as a conversion target/source.

Risks: uses formatted SQL identifiers based on escaped tree names; current escaping handles `:` only, relying on callers to use safe names. Iterator implementations use unsafe self-referential structures around statements/rows/connections. Non-transactional `insert` reads old value then update/insert under write lock, which is safe for single-writer but more complex than `INSERT OR REPLACE`. SQLite iterator/write locking limitations influenced block repair batching.

Test signals: shared DB test suite covers CRUD, transactions, and iteration; no direct tests for snapshot, SQL identifier edge cases, or pool behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/sqlite_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/db/test.rs -->
# sources/object-store/garage/src/db/test.rs

Purpose: shared conformance tests for every enabled `garage_db` backend.

Important APIs/types/functions: `test_suite`, feature-gated tests `test_lmdb_db`, `test_sqlite_db`, and `test_fjall_db`.

Control flow: creates a tree, tests insert/get, transaction commit, transaction abort rollback, outside-transaction iteration/ranges/reverse iteration, and equivalent inside-transaction iterators. Each feature-specific test constructs a temporary or in-memory database and runs the same suite.

State and persistence: LMDB and Fjall tests use temporary directories; SQLite uses an in-memory connection manager. Test data is small fixed byte slices.

Dependencies and integration points: uses all public DB APIs and feature-gated adapter constructors. The suite is a contract for engine parity.

Risks: coverage is intentionally basic; it does not cover `clear`, `snapshot`, `import`, `on_commit`, concurrent access, large values, invalid tree IDs, or adapter-specific durability flags.

Test signals: direct unit tests are strong smoke tests for ordering and transaction semantics across enabled engines.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/db/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/format-table/Cargo.toml -->
# sources/object-store/garage/src/format-table/Cargo.toml

Purpose: declares the tiny `format_table` helper crate used by CLI output.

Important APIs/types/functions: configures `lib.rs`, version `0.1.1`, edition 2018, AGPL-3.0, no explicit dependencies.

Control flow: build-time manifest only.

State and persistence: none.

Dependencies and integration points: consumed heavily by `garage` CLI remote command modules for human-readable tables.

Risks: the crate's simple API means formatting behavior changes can affect many CLI snapshots/manual workflows. No dependency surface limits build risk.

Test signals: no direct manifest tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/format-table/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/format-table/lib.rs -->
# sources/object-store/garage/src/format-table/lib.rs

Purpose: formats tab-delimited strings into padded text tables for terminal output.

Important APIs/types/functions: `format_table_to_string(data: Vec<String>) -> String` and `format_table(data: Vec<String>)`.

Control flow: splits each row on tab, computes maximum character width per column, then emits rows with two spaces after every non-last column. `format_table` prints the returned string to stdout.

State and persistence: stateless; output only.

Dependencies and integration points: no external dependencies. Used by CLI modules for bucket/key/layout/status/worker/block/admin-token tables.

Risks: assumes every row has at least one column; an empty string row works as one empty column, but a truly empty data vector produces an empty string. Width uses `chars().count()`, not display width, so East Asian wide characters or ANSI escapes may misalign. The API consumes `Vec<String>`, causing callers to allocate.

Test signals: no unit tests, but many CLI code paths depend on it. Simple examples in docs explain expected input format.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/format-table/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/Cargo.toml -->
# sources/object-store/garage/src/garage/Cargo.toml

Purpose: manifest for the main `garage` binary crate and its integration test target.

Important APIs/types/functions: binary `garage` at `main.rs`, integration test at `tests/lib.rs`, feature flags for K2V, DB engines, discovery integrations, metrics/telemetry/logging, and bundled/system libraries.

Control flow: build-time dependency and feature wiring. Default features enable bundled libs, metrics, LMDB, SQLite, and K2V.

State and persistence: feature choices control runtime DB engine support, API availability, observability endpoints, logging sinks, and library linkage.

Dependencies and integration points: depends on all major Garage internal crates (`garage_db`, `garage_api_*`, `garage_block`, `garage_model`, `garage_rpc`, etc.) plus CLI/observability/runtime crates. Dev dependencies include AWS SDK and HTTP/testing utilities for integration tests.

Risks: feature combinations must keep internal crate features aligned, especially DB engines and bundled/system libraries. The comment says bundled-libs and system-libs should be mutually exclusive, but Cargo does not enforce it here.

Test signals: integration target plus compile matrix over features. Manifest changes should be validated with at least default-feature build and relevant no-default/system-libs variants.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/completions.rs -->
# sources/object-store/garage/src/garage/cli/local/completions.rs

Purpose: generates shell completions for the Garage CLI.

Important APIs/types/functions: `generate_completions(shell: Shell)`.

Control flow: obtains the structopt/clap command from `Opt::clap()`, captures the command name, and writes completions for the requested shell to stdout.

State and persistence: no persistent state; stdout output only.

Dependencies and integration points: uses `structopt::{clap::Shell, StructOpt}` and crate root `Opt`. Invoked by local CLI command dispatch.

Risks: depends on the full CLI definition being represented by `Opt`. Changes in structopt/clap generation behavior may alter completion output.

Test signals: no direct tests; compile-time coverage and manual completion generation are primary checks.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/completions.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/convert_db.rs -->
# sources/object-store/garage/src/garage/cli/local/convert_db.rs

Purpose: implements an offline CLI for converting Garage metadata databases between supported engines.

Important APIs/types/functions: `ConvertDbOpt`, `OpenDbOpt`, `OpenLmdbOpt`, and `do_conversion`.

Control flow: structopt parses input path/engine and output path/engine. `do_conversion` rejects same-engine conversion, builds `OpenOpt` with optional LMDB map size, opens both DBs, and calls `output.import(&input)`.

State and persistence: reads one metadata database and writes a new one. Destination must be empty because `Db::import` rejects existing trees.

Dependencies and integration points: uses `garage_db::{Engine, OpenOpt, open_db, Db::import}` and `bytesize` for LMDB map-size parsing. Integrated into local CLI options.

Risks: conversion is broad and uses one transaction per tree, which can be costly for large metadata. It shares the same open options for input and output, so LMDB map size applies to both when relevant. It does not expose Fjall block-cache or fsync options.

Test signals: no direct tests; relies on DB adapter tests and manual conversion validation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/convert_db.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/init.rs -->
# sources/object-store/garage/src/garage/cli/local/init.rs

Purpose: prints this node's Garage RPC node identifier and helpful connection/bootstrap instructions.

Important APIs/types/functions: constant `READ_KEY_ERROR` and `node_id_command(config_file, quiet)`.

Control flow: reads config, reads node ID from metadata directory, prints `node_id@public_addr` if `rpc_public_addr` is set, otherwise prints raw ID and warns/instructs using `127.0.0.1:<rpc_bind_port>` as a placeholder when not quiet. Non-quiet mode prints connection command, bootstrap config snippet, and security notice.

State and persistence: reads config file and node key from metadata; does not modify state.

Dependencies and integration points: uses `garage_util::config::read_config`, `garage_rpc::system::read_node_id`, `hex`, and tracing warnings. Used by local initialization/operator CLI flows.

Risks: output with fallback loopback address is intentionally instructional and may be copied incorrectly if user ignores warning. Failure to read node key is normal before first node launch and surfaced with a long contextual message.

Test signals: no unit tests; manual CLI invocation is the main check.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/init.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/mod.rs -->
# sources/object-store/garage/src/garage/cli/local/mod.rs

Purpose: local CLI module aggregator.

Important APIs/types/functions: declares `completions`, `convert_db`, `init`, and `repair` as crate-private submodules.

Control flow: no runtime logic.

State and persistence: none directly.

Dependencies and integration points: imported by `garage/cli/mod.rs` and command dispatch code.

Risks: module visibility is crate-private; moving public APIs here could expose unwanted surface.

Test signals: compile-time module linkage only.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/repair.rs -->
# sources/object-store/garage/src/garage/cli/local/repair.rs

Purpose: runs offline metadata repair operations that need direct local Garage model access.

Important APIs/types/functions: async `offline_repair(config_file, secrets, opt)`.

Control flow: requires `--yes`, reads and secret-fills config, initializes `Garage::new`, then dispatches `OfflineRepairWhat` to recount K2V item counters or object counters. Logs progress and returns after repair.

State and persistence: opens and mutates local metadata stores by recounting counters from authoritative tables. It should be run with care because it bypasses remote admin RPC and works locally.

Dependencies and integration points: uses `garage_model::garage::Garage`, config/secrets helpers, and CLI structs. K2V branch is feature-gated.

Risks: requires correct config/secrets and should not be run casually on a live/incorrect node. The `--yes` guard prevents accidental invocation. Errors during `Garage::new` or recount abort the operation.

Test signals: no direct tests; repair table implementations should have their own coverage.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/local/repair.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/mod.rs -->
# sources/object-store/garage/src/garage/cli/mod.rs

Purpose: top-level CLI module aggregator.

Important APIs/types/functions: public modules `structs`, `local`, and `remote`.

Control flow: no runtime logic.

State and persistence: none directly.

Dependencies and integration points: the main binary imports CLI structs and local/remote command implementations through this module.

Risks: minimal; module layout changes affect CLI compile paths.

Test signals: compile-time module linkage.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/admin_token.rs -->
# sources/object-store/garage/src/garage/cli/remote/admin_token.rs

Purpose: implements remote CLI administration-token management.

Important APIs/types/functions: `Cli::cmd_admin_token`, list/info/create/rename/update/delete/delete-expired command methods, and helper `print_token_info`.

Control flow: dispatches `AdminTokenOperation` variants to admin API requests. Create parses optional expiration and scope CSV, prints secret token once unless quiet. Update supports scope replacement plus `+scope` additions and `-scope` removals. Delete operations require `--yes` and resolve token search strings to IDs first.

State and persistence: mutates admin-token metadata through remote admin API calls. It never stores secret tokens locally; it prints newly created token secrets only once from the API response.

Dependencies and integration points: uses `garage_api_admin::api` request/response types, shared `Cli::api_request`, `parse_expires_in`, `table_list_abbr`, `format_table`, and chrono local time formatting.

Risks: token search must uniquely resolve server-side; `.unwrap()` on token IDs/created fields assumes admin API invariants. Scope CSV parsing trims entries but does not reject empty strings locally. Expiration parsing uses local current time through `parse_expires_in`.

Test signals: no local tests; API-level tests and CLI smoke tests should cover create/update/delete and scope modifications.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/admin_token.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/block.rs -->
# sources/object-store/garage/src/garage/cli/remote/block.rs

Purpose: implements remote CLI block diagnostics and repair controls.

Important APIs/types/functions: `Cli::cmd_block`, `cmd_list_block_errors`, `cmd_get_block_info`, `cmd_block_retry_now`, `cmd_block_purge`, and `deleted_to_str`.

Control flow: list errors calls local admin API on the selected node and formats RC/error/backoff age. Info fetches block references, prints version/upload backlinks, detects inconsistencies between block refs and versions, and warns when refcount differs from active reference count. Retry accepts either `--all` or explicit hashes. Purge requires `--yes` and sends block purge request.

State and persistence: retry mutates resync queue/backoff state; purge can delete block refs, versions, objects, and multipart uploads through admin API. Info/list are read-only.

Dependencies and integration points: uses local API wrapper, admin API request types, `format_table`, `timeago`, and CLI structs. Connects directly to block manager/resync admin surfaces.

Risks: purge is destructive and guarded only by `--yes`; callers must provide correct block hashes. Info warnings depend on response consistency fields and may not catch every metadata issue.

Test signals: no direct tests; admin API tests and manual operational checks should cover block info/error/retry/purge.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/bucket.rs -->
# sources/object-store/garage/src/garage/cli/remote/bucket.rs

Purpose: implements remote CLI bucket management, permissions, website settings, quotas, incomplete-upload cleanup, and object inspection.

Important APIs/types/functions: `Cli::cmd_bucket` dispatcher; command methods for list/info/create/delete/alias/unalias/allow/deny/website/set-quotas/cleanup-incomplete-uploads/inspect-object; helper `print_bucket_info`.

Control flow: commands resolve buckets/keys through admin API search calls, then issue specific admin requests. Delete performs CLI-side checks that the target alias is the last global alias and that no local aliases remain, then requires `--yes`. Website mode requires exactly one of allow/deny. Quota parsing accepts byte sizes, object counts, and `"none"`. Object inspection prints per-version metadata, headers, and block list.

State and persistence: mutates bucket metadata, aliases, key permissions, website config, quotas, and incomplete upload records through admin API. Inspect/list/info are read-only.

Dependencies and integration points: uses `garage_api_admin::api`, `format_table`, chrono local formatting, `bytesize`, parse-duration, shared `Cli::api_request`, and key/bucket response structures. It is a major operator-facing integration with Garage's admin API.

Risks: many operations rely on server-side search uniqueness and response invariants. Delete's alias checks are client-side convenience and must remain aligned with server rules. Website update preserves previous error document only on allow when not explicitly provided. Cleanup loops buckets sequentially and partially completed multi-bucket cleanup can leave mixed results.

Test signals: no direct module tests; admin API and CLI smoke tests should exercise destructive guards, alias/permission changes, quota parsing, and object inspection formatting.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/cluster.rs -->
# sources/object-store/garage/src/garage/cli/remote/cluster.rs

Purpose: implements remote CLI cluster health, status, and node connection commands.

Important APIs/types/functions: `Cli::cmd_health`, `cmd_status`, and `cmd_connect`.

Control flow: health prints summary unless quiet and returns an error when status is `unavailable`. Status fetches cluster status and layout, prints healthy nodes, failed/pending/draining nodes, data availability, version info, staged layout changes, and operator hints. Connect sends a `ConnectClusterNodesRequest` for a single peer and prints success or failure.

State and persistence: health/status are read-only. Connect mutates cluster peer state by asking the target node to connect.

Dependencies and integration points: uses admin API cluster types, layout helper functions, `format_table`, `timeago`, `bytesize`, and shared `Cli::api_request`.

Risks: health status string comparison is literal. Status output combines live advertisements with layout roles and staged changes, so display correctness depends on API response consistency. Connect expects exactly one response.

Test signals: no local tests; cluster integration tests and manual CLI usage validate output and error handling.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/key.rs -->
# sources/object-store/garage/src/garage/cli/remote/key.rs

Purpose: implements remote CLI access-key lifecycle and permissions.

Important APIs/types/functions: `Cli::cmd_key`, list/info/create/rename/update/delete/allow/deny/import/delete-expired command methods, and `print_key_info`.

Control flow: list sorts by created time and shows expiration. Commands resolve key patterns via admin API, then send create/update/delete/import requests. Create and update parse relative expiration through `parse_expires_in`; allow/deny mutate `create_bucket`; import requires `--yes` to discourage misuse.

State and persistence: mutates access-key metadata, secrets, expiration, and permissions via admin API. Secret key is only printed when included in response, otherwise redacted.

Dependencies and integration points: uses admin API request/response types, `format_table`, chrono local formatting, and shared remote helpers.

Risks: server-side search and response IDs are assumed. Delete-expired loops sequentially and can partially succeed. Importing an existing externally supplied key is security-sensitive and guarded only by `--yes`.

Test signals: no direct tests; should be covered by admin API tests and CLI smoke tests for key lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/key.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/layout.rs -->
# sources/object-store/garage/src/garage/cli/remote/layout.rs

Purpose: implements remote CLI cluster layout staging, preview, apply, revert, history, and dead-node progress forcing.

Important APIs/types/functions: `layout_command_dispatch`; command methods `cmd_show_layout`, `cmd_assign_role`, `cmd_remove_role`, `cmd_config_layout`, `cmd_apply_layout`, `cmd_revert_layout`, `cmd_layout_history`, `cmd_skip_dead_nodes`; helpers `capacity_string`, `get_staged_or_current_role`, `find_matching_node`, `print_cluster_layout`, `print_staging_role_changes`, `display_zone_redundancy`, and `parse_zone_redundancy`.

Control flow: show fetches layout, prints current roles, staged changes, and previewed post-apply layout. Assign resolves node patterns, handles replacement removals, derives zone/capacity/tags from args or current/staged role, and stages updates. Apply requires explicit version. Revert requires `--yes`. History prints version summaries and update trackers with guidance. Skip-dead-nodes sends version and missing-data flag, then reports tracker changes or actionable errors.

State and persistence: mutates cluster layout staging parameters, staged node roles, applied layout version, and tracker state through admin API. It does not directly persist local files.

Dependencies and integration points: uses admin layout API types, `bytesize`, `format_table`, shared remote API helper, and CLI structs. Cluster status code reuses layout display helpers.

Risks: node matching by prefix errors unless exactly one candidate matches; operators must pass the apply version to avoid accidental stale layout application. Capacity/tag inheritance logic is subtle when staging over existing staged roles. `parse_zone_redundancy` treats `none`, `max`, and `maximum` as maximum redundancy, which is semantically non-obvious.

Test signals: no direct tests; layout algorithm/API tests plus CLI smoke tests should cover staging, preview, apply version guard, revert guard, and prefix ambiguity.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/mod.rs -->
# sources/object-store/garage/src/garage/cli/remote/mod.rs

Purpose: remote CLI module aggregator and shared admin RPC helper implementation.

Important APIs/types/functions: modules `admin_token`, `bucket`, `cluster`, `key`, `layout`, `block`, `node`, `worker`; struct `Cli`; methods `handle`, `api_request`, `local_api_request`, `cmd_json_api`; helpers `table_list_abbr` and `parse_expires_in`.

Control flow: `handle` dispatches high-level `Command` variants to domain modules. `api_request` wraps typed admin API requests in proxy RPC, maps typed responses, and turns admin API errors into CLI errors. `local_api_request` wraps a typed request in `MultiRequest` scoped to `rpc_host`, then requires exactly one successful response. `cmd_json_api` accepts JSON from argument or stdin, sends raw endpoint payload, and pretty-prints the matching response field.

State and persistence: no direct persistence; every mutation occurs through remote admin API/RPC. Holds RPC endpoint and target node ID.

Dependencies and integration points: central integration with `garage_rpc`, `garage_api_admin::api`, `AdminRpc` proxy server, `RequestHandler`, CLI structs, chrono/date parsing, and parse-duration.

Risks: typed response conversion failures are surfaced as unexpected responses. `local_api_request` ignores all but the first error and requires a single success, which is correct for a single target but sensitive to `MultiResponse` shape. Raw JSON API bypasses typed CLI validation.

Test signals: no direct tests; any remote command exercises these helpers. High-value tests include API error formatting, typed conversion mismatch, stdin JSON path, and multi-response error handling.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/node.rs -->
# sources/object-store/garage/src/garage/cli/remote/node.rs

Purpose: implements remote CLI metadata snapshot command for nodes.

Important APIs/types/functions: `Cli::cmd_meta`.

Control flow: currently handles `MetaOperation::Snapshot { all }`, sends `CreateMetadataSnapshotRequest` to either `*` or the selected node, prints success/error table, and returns an error if any node failed.

State and persistence: triggers metadata snapshot creation on target node(s), causing server-side snapshot files to be written. CLI itself only prints results.

Dependencies and integration points: uses admin API local/multi snapshot request types, `hex` node encoding, `format_table`, and shared `Cli::api_request`.

Risks: all-node snapshot can partially fail; the command reports all results and returns an error if any failed. Snapshot path/lifecycle are controlled server-side, not visible here.

Test signals: no direct tests; admin local API tests and manual CLI validation cover it.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/worker.rs -->
# sources/object-store/garage/src/garage/cli/remote/worker.rs

Purpose: implements remote CLI worker inspection and runtime background-variable get/set controls.

Important APIs/types/functions: `Cli::cmd_worker`, `cmd_list_workers`, `cmd_worker_info`, `cmd_get_var`, `cmd_set_var`, and `format_worker_state`.

Control flow: list fetches local workers with busy/error filters, sorts busy/throttled first, and prints state/progress/queue/error fields. Info fetches one worker and prints state, tranquility, errors, progress, queue length, persistent errors, and freeform messages. Get/set variable commands target selected node or all nodes and print per-node results/errors.

State and persistence: worker variable set can mutate runtime and persisted background settings depending on server-side variable registration, such as resync/scrub tranquility and worker count. List/info are read-only.

Dependencies and integration points: uses admin worker API types, `format_table`, `timeago`, shared local/multi API wrappers, and worker status response shape from background runner.

Risks: variable names/values are stringly typed and validated server-side. All-node set can partially succeed; errors are printed to stderr but the command returns `Ok(())`, so automation must parse output if partial failure matters.

Test signals: no direct tests; background/admin API tests and manual CLI runs should cover list/info and variable mutation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/garage/cli/remote/worker.rs -->
