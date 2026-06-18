# Research Group: subset-b-008833

This grouped report covers the TiKV write-batch tests plus the `error_code`, `external_storage`, `file_system`, and `health_controller` component files assigned to subset B item `subset-b-008833`. Each section preserves the source path title and is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/write_batch.rs -->
# sources/storage-engines/tikv/components/engine_traits_tests/src/write_batch.rs

Purpose: this file is a conformance test suite for the `engine_traits::WriteBatch` contract, executed against both `default_engine()` and `multi_batch_write_engine()` from the surrounding test harness. It verifies that `put`, `delete`, `delete_range`, repeated `write`, capacity hints, `should_write_to_engine`, `data_size`, `clear`, save points, rollback, and pop semantics behave consistently across the basic test engine and a multi-batch engine variant.

Important APIs and functions: every test builds a `KvTestEngine` wrapper, uses `WriteBatchExt::write_batch` or `write_batch_with_cap`, mutates through the `Mutable` and `SyncMutable` APIs, and observes committed state through `Peekable::get_value`. `recover_safe` is used to assert panic behavior for invalid backward ranges, and `assert_engine_error` verifies missing-save-point errors. `KvTestEngine::WRITE_BATCH_MAX_KEYS` defines the threshold for `should_write_to_engine`.

Control flow: the suite starts with no-op and empty-write tests, then progressively covers single puts/deletes, idempotent/replayable write batches, range tombstone behavior, count/empty/data-size accounting, capacity hints, threshold signaling, and save-point stack behavior. Most tests are duplicated manually for the multi-batch engine with 256 numeric keys encoded via `usize::to_be_bytes`, forcing internal batch splitting while preserving externally visible ordering. Range tests emphasize inclusive start/exclusive end semantics: `delete_range(b"b", b"e")` deletes `b`, `c`, and `d`, but keeps `e`; empty ranges delete nothing.

State and persistence behavior: `write()` commits the whole accumulated batch to the underlying in-memory test engine and does not clear the batch; tests assert that `is_empty`, `count`, and `data_size` remain non-empty after write until `clear` or rollback changes them. Rewriting the same batch can overwrite later direct engine changes, so the batch is persistent as a reusable command buffer. Save points are stack-like markers over the command buffer: rollback removes commands after the latest point, while pop removes the marker without discarding commands. Rollback after a previous write can remove the previously written commands from the reusable batch, so a later write can make a directly deleted key remain deleted.

Dependencies and integration points: the file is not production code; it encodes the behavioral surface that TiKV engine implementations must match. It integrates with `engine_test`, `engine_traits`, and `panic_hook`, and indirectly documents assumptions for RocksDB/raft-engine style `WriteBatch` implementations. The multi-batch engine coverage is particularly important for wrappers that flush internal sub-batches when capacity is reached.

Risks: one ignored test, `write_batch_delete_range_backward_range_partial_commit`, documents questionable partial-commit behavior when an invalid range appears after earlier commands. If an implementation applies commands while validating, writes before a panic may persist, which is a serious atomicity hazard. The suite also accepts that capacity is only advisory and that oversized batches still commit, so callers must not treat `should_write_to_engine` as an enforced safety gate.

Test signals: this file is itself the test signal. It covers many ordering combinations, repeated operations, save-point edge cases, empty/backward ranges, and accounting invariants, but it is still deterministic unit-style coverage over a test engine rather than fault injection around real disk persistence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_traits_tests/src/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/Cargo.toml -->
# sources/storage-engines/tikv/components/error_code/Cargo.toml

Purpose: this manifest defines the `error_code` crate, a non-published TiKV workspace component that centralizes structured error-code constants and a generator binary. The crate is Apache-2.0 licensed, uses Rust 2021, and exposes `src/lib.rs` as library `error_code`.

Important APIs and build targets: the manifest declares one binary target, `error_code_gen`, at `bin.rs`. That binary generates the `etc/error_code.toml` catalog from selected module-level `ALL_ERROR_CODES` vectors. The library target exports the `ErrorCode` type, `ErrorCodeExt` trait, the `define_error_codes!` macro expansion products, and domain modules such as `raftstore`, `storage`, `pd`, and `cloud`.

Dependencies and integration points: `lazy_static` is required by the macro to produce `ALL_ERROR_CODES`; `kvproto` and `raft` are required for conversion implementations over protobuf and raft errors; `tikv_alloc` installs TiKV allocation behavior. The component is consumed by other TiKV crates to attach stable textual error identifiers such as `KV:Storage:Timeout`.

State and persistence behavior: the manifest has no runtime state itself, but it wires the binary that writes a persistent TOML file under `./etc/error_code.toml` when run from the repository root.

Risks: the generator binary currently enumerates only a subset of modules, omitting `backup_stream` and `causal_ts`; manifest readers should not assume every module constant is represented in the generated TOML. The crate also uses nightly-only `min_specialization` in `lib.rs`, so it depends on TiKV's toolchain assumptions.

Test signals: no manifest tests exist here; correctness is covered by library tests in `src/lib.rs` and by compilation of consumers that rely on the exported constants and conversion traits.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/bin.rs -->
# sources/storage-engines/tikv/components/error_code/bin.rs

Purpose: this binary generates an error-code catalog file at `./etc/error_code.toml`. It is intended as a repository maintenance utility rather than runtime TiKV code.

Important APIs and functions: `main` imports all public symbols from `error_code::*`, builds a vector of iterators over module-level `ALL_ERROR_CODES`, creates `etc/error_code.toml`, formats each error as a TOML table keyed by `c.code`, and writes an `error` field containing the code text. It calls `sync_all` before exit to persist the generated file.

Control flow: the binary constructs a fixed list of modules: `cloud`, `codec`, `coprocessor`, `encryption`, `engine`, `pd`, `raft`, `raftstore`, `sst_importer`, and `storage`. It flattens the iterator list, maps each `ErrorCode` to a TOML snippet, and writes snippets sequentially. All I/O uses `unwrap`, so any missing directory, permission issue, or write failure aborts the process.

State and persistence behavior: the only persistent state is `./etc/error_code.toml`, which is overwritten on each run. It does not create the parent directory and does not do atomic temp-file replacement, so interrupted generation could leave a truncated catalog.

Dependencies and integration points: it relies on the `ALL_ERROR_CODES` values generated by `define_error_codes!` and on the repo being invoked from a working directory where `./etc` is the intended target. It integrates with downstream documentation or tooling that consumes the TOML catalog.

Risks: `backup_stream` and `causal_ts` are defined in the library but omitted from the generator list, so their codes are not exported by this binary. The generated TOML stores only the code string, not the `description` or `workaround` fields, losing some structured metadata. `unwrap`-driven failure is acceptable for a maintenance binary but poor for automated pipelines unless wrapped by build scripts.

Test signals: there are no tests for this binary in the file. Generator coverage is implicit through library compilation and any external check comparing generated `etc/error_code.toml`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/bin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/backup_stream.rs -->
# sources/storage-engines/tikv/components/error_code/src/backup_stream.rs

Purpose: this module declares backup-stream/log-backup error codes under the `KV:LogBackup:` namespace. It gives richer descriptions and workarounds than most other `error_code` modules, making it useful for user-facing diagnosis.

Important APIs and constants: `define_error_codes!` expands constants such as `PROTO`, `NO_SUCH_TASK`, `OUT_OF_QUOTA`, `OBSERVE_CANCELED`, `MALFORMED_META`, `IO`, `TXN`, `SCHED`, `PD`, `RAFTREQ`, `RAFTSTORE`, `GRPC`, `ENCRYPTION`, and `OTHER`, plus a module-level `ALL_ERROR_CODES` vector. Each constant is an `ErrorCode { code, description, workaround }`.

Control flow and state: this is declarative code. Runtime users import constants or iterate `ALL_ERROR_CODES`; no dynamic mapping implementation is present. The constants are lazily collected by `lazy_static` when `ALL_ERROR_CODES` is first accessed.

Dependencies and integration points: the module depends on the crate-level macro and `ErrorCode` struct. It is meant to integrate with backup stream components that translate local error variants into stable error-code values.

Risks: despite being a declared module in `lib.rs`, it is not included in `bin.rs`'s generated TOML list, so catalog generation can omit these codes. Several strings contain grammar issues but are otherwise meaningful. Since there is no `ErrorCodeExt` implementation here, correctness depends on backup-stream error types manually returning the right constants elsewhere.

Test signals: no local tests exist. Compile-time expansion of the macro is the only direct signal in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/backup_stream.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/causal_ts.rs -->
# sources/storage-engines/tikv/components/error_code/src/causal_ts.rs

Purpose: this module declares causal timestamp error-code constants under the `KV:CausalTs:` namespace.

Important APIs and constants: it defines `PD`, `TSO`, `TSO_BATCH_USED_UP`, `BATCH_RENEW`, and `UNKNOWN`. The macro also creates `ALL_ERROR_CODES` for iteration. The suffixes identify PD client failures, timestamp oracle failures, exhausted TSO batches, batch-renew failures, and an unknown fallback.

Control flow and state: the file is declarative; there are no functions, trait implementations, or mutable state beyond the `lazy_static` vector generated by `define_error_codes!`.

Dependencies and integration points: callers in causal timestamp or TSO-related components can map their domain errors to these constants. The module depends only on the crate-level macro and `ErrorCode` type.

Risks: all descriptions and workarounds are empty, limiting diagnostic quality. Like `backup_stream`, this module is absent from `bin.rs`'s generator list, so its constants may not appear in the generated external catalog.

Test signals: no tests exist in this file. Macro expansion is indirectly checked by crate compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/causal_ts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/cloud.rs -->
# sources/storage-engines/tikv/components/error_code/src/cloud.rs

Purpose: this module declares cloud-storage related error codes under `KV:Cloud:` for object-store, encryption-key, and API failures.

Important APIs and constants: exported constants include `IO`, `SSL`, `PROTO`, `UNKNOWN`, `TIMEOUT`, `INVALID_INPUT`, `API_INTERNAL`, `API_NOT_FOUND`, `API_AUTHENTICATION`, `WRONG_MASTER_KEY`, and `BOTH_MASTER_KEY_FAIL`. `ALL_ERROR_CODES` is generated for catalog iteration.

Control flow and state: the module is pure declarations. Runtime state is limited to the lazy vector of constants. There is no conversion trait implementation in this file, so callers must choose constants manually or through wrappers in cloud-related crates.

Dependencies and integration points: the constants are consumed by cloud/external-storage/encryption error handling paths that need stable code strings for logging, metrics, or user-facing responses. `bin.rs` includes this module in generated catalog output.

Risks: descriptions and workarounds are empty, so the generated catalog contains only codes. Cloud backends often have provider-specific error classes, but this file keeps a coarse set of buckets; misclassification can make support diagnosis harder.

Test signals: no direct tests exist. Coverage comes from crate compilation and downstream consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/cloud.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/codec.rs -->
# sources/storage-engines/tikv/components/error_code/src/codec.rs

Purpose: this module declares codec-layer error-code constants under `KV:Codec:`.

Important APIs and constants: it exports `IO`, `BAD_PADDING`, `KEY_LENGTH`, `KEY_NOT_FOUND`, `VALUE_LENGTH`, and `VALUE_META`, plus `ALL_ERROR_CODES`. These cover low-level byte encoding/decoding and key/value format issues.

Control flow and state: there is no executable control flow beyond the macro expansion. `ALL_ERROR_CODES` is lazily initialized for iteration.

Dependencies and integration points: codec and storage layers can attach these constants to decode failures. The generator binary includes this module when producing `etc/error_code.toml`.

Risks: empty descriptions and workarounds reduce the usefulness of catalog output. The module does not implement `ErrorCodeExt` for any concrete codec error type, so mapping consistency depends on external code.

Test signals: no local tests exist; macro expansion is indirectly tested by `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/codec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/coprocessor.rs -->
# sources/storage-engines/tikv/components/error_code/src/coprocessor.rs

Purpose: this module provides stable coprocessor error codes under `KV:Coprocessor:` for request execution, expression evaluation, encoding, storage interaction, and quota errors.

Important APIs and constants: constants include request/control failures such as `LOCKED`, `DEADLINE_EXCEEDED`, `MAX_PENDING_TASKS_EXCEEDED`, and `MEMORY_QUOTA_EXCEEDED`; expression/data failures such as `INVALID_DATA_TYPE`, `ENCODING`, `COLUMN_OFFSET`, `UNKNOWN_SIGNATURE`, `EVAL`, `CORRUPTED_DATA`, and `INVALID_CHARACTER_STRING`; storage-related failures such as `STORAGE_ERROR`, `DEFAULT_NOT_FOUND`, and `INVALID_MAX_TS_UPDATE`. `ALL_ERROR_CODES` is generated.

Control flow and state: declarative constants only. No direct conversion implementation is present.

Dependencies and integration points: this namespace is for TiKV coprocessor code that evaluates pushed-down SQL expressions and reads MVCC data. The generator binary includes it in the TOML catalog.

Risks: all descriptions and workarounds are empty. The list contains both user-input/data issues and internal storage issues; downstream mapping must preserve that distinction for actionable responses.

Test signals: no module-local tests exist. Compilation validates macro expansion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/coprocessor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/encryption.rs -->
# sources/storage-engines/tikv/components/error_code/src/encryption.rs

Purpose: this module declares encryption subsystem error codes under `KV:Encryption:`.

Important APIs and constants: it exports `ROCKS`, `IO`, `CRYPTER`, `PROTO`, `UNKNOWN_ENCRYPTION`, `WRONG_MASTER_KEY`, `BOTH_MASTER_KEY_FAIL`, and `PARSE_INCOMPLETE`, plus the generated `ALL_ERROR_CODES`. These represent storage-engine errors, filesystem errors, encryption algorithm/key failures, protocol serialization, unknown method, key mismatch, dual master-key failure, and incomplete tail-record parsing.

Control flow and state: it is declarative and has no conversion implementation. The only runtime allocation is the lazy vector of constants.

Dependencies and integration points: encryption code and cloud/external-storage code can use these constants when mapping encryption-related failures. The generator binary includes this namespace.

Risks: empty descriptions and workarounds limit diagnostics. Several key-related codes overlap with `KV:Cloud` constants; callers should choose the subsystem where the error originates to avoid ambiguous telemetry.

Test signals: no local tests exist. Macro expansion and constant availability are covered by crate compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/engine.rs -->
# sources/storage-engines/tikv/components/error_code/src/engine.rs

Purpose: this module declares storage-engine abstraction error codes under `KV:Engine:`.

Important APIs and constants: constants include `ENGINE`, `NOT_IN_RANGE`, `PROTOBUF`, `IO`, `CF_NAME`, `CODEC`, `DATALOSS`, `DATACOMPACTED`, and `BOUNDARY_NOT_SET`, plus the generated `ALL_ERROR_CODES`.

Control flow and state: there is no runtime logic besides lazy vector initialization. No `ErrorCodeExt` implementation appears here; engine error types must map to these constants elsewhere.

Dependencies and integration points: these codes sit under the `engine_traits`/engine abstraction layer and are expected to be used by RocksDB, raft-engine, and related wrappers when exposing common error categories to upper layers. The generator binary includes this module.

Risks: empty descriptions and workarounds make the code strings the only catalog payload. The typo-like suffix `DATACOMPACTED` differs from `DATA_COMPACTED` in the PD namespace, so cross-subsystem normalization must be deliberate.

Test signals: no local tests exist. The crate-level macro test validates the expansion pattern used here.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/lib.rs -->
# sources/storage-engines/tikv/components/error_code/src/lib.rs

Purpose: this is the root of the `error_code` crate. It defines the shared `ErrorCode` representation, the `ErrorCodeExt` trait, the `UNKNOWN` fallback, all public domain modules, and the macro used by every module to declare constants.

Important APIs and types: `ErrorCode` is a `Copy` struct with static `code`, `description`, and `workaround` fields, and implements `Display` by printing the code. `ErrorCodeExt` defines `fn error_code(&self) -> ErrorCode` for downstream error types. `define_error_codes!` takes a prefix and `NAME => (suffix, description, workaround)` entries, emits `pub const` values with `concat!($prefix, $suffix)`, and creates a module-local `ALL_ERROR_CODES: Vec<ErrorCode>` in `lazy_static!`.

Control flow and state: most behavior is compile-time macro expansion plus runtime lazy vector initialization. The root exports modules including `backup_stream`, `causal_ts`, `cloud`, `codec`, `coprocessor`, `encryption`, `engine`, `pd`, `raft`, `raftstore`, `sst_importer`, and `storage`. The crate uses `#![feature(min_specialization)]`, so it assumes a nightly toolchain.

Dependencies and integration points: `lazy_static` powers catalog vectors; `kvproto` and `raft` are used by submodules for conversion implementations; `tikv_alloc` installs TiKV allocator hooks. Other crates integrate by importing constants or implementing/using `ErrorCodeExt`.

Risks: `UNKNOWN` has code `KV:Unknown` with empty metadata, making it a coarse fallback. The macro creates a fixed `Vec`, not a sorted or deduplicated catalog, so duplicate constants would only be caught by external review. Generated catalogs can diverge from exported modules because `bin.rs` maintains its own module list.

Test signals: `test_define_error_code` verifies that the macro concatenates prefixes and suffixes correctly and emits public constants with expected metadata. It does not test `ALL_ERROR_CODES` contents or duplicate handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/pd.rs -->
# sources/storage-engines/tikv/components/error_code/src/pd.rs

Purpose: this module defines Placement Driver error codes under `KV:Pd:`.

Important APIs and constants: constants include `IO`, `CLUSTER_BOOTSTRAPPED`, `CLUSTER_NOT_BOOTSTRAPPED`, `INCOMPATIBLE`, `GRPC`, `STREAM_DISCONNECT`, `REGION_NOT_FOUND`, `STORE_TOMBSTONE`, `DATA_COMPACTED`, `STALE_SERVICE_GC_SAFE_POINT`, and `UNKNOWN`, plus the generated `ALL_ERROR_CODES`.

Control flow and state: it is a declarative macro invocation with no conversion implementation. Runtime state is the lazy vector.

Dependencies and integration points: PD client and scheduling code can use these constants for cluster bootstrap, region lookup, safe-point, and gRPC connectivity errors. The generator binary includes this namespace.

Risks: some code suffixes contain spelling mistakes (`ClusterBootstraped`, `ClusterNotBootstraped`, `Imcompatible`) that may already be part of the stable external contract. Fixing them would be breaking for dashboards or support docs. Descriptions and workarounds are empty.

Test signals: no module-local tests exist. Compile-time macro expansion is the only direct signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/pd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raft.rs -->
# sources/storage-engines/tikv/components/error_code/src/raft.rs

Purpose: this module defines `KV:Raft:` error-code constants and maps `raft::Error` variants to them via `ErrorCodeExt`.

Important APIs and constants: constants include `IO`, `STORE`, `STEP_LOCAL_MSG`, `STEP_PEER_NOT_FOUND`, `PROPOSAL_DROPPED`, `CONFIG_INVALID`, `CODEC_ERROR`, `EXISTS`, `NOT_EXISTS`, and `CONF_CHANGE_ERROR`. The `impl ErrorCodeExt for raft::Error` matches each current variant to its corresponding constant.

Control flow: `error_code()` is a direct `match` over raft errors. `Error::RequestSnapshotDropped` is marked `unreachable!()`, implying the TiKV call paths using this conversion should never observe that variant or should handle it earlier.

State and persistence behavior: the module has no persistent state. The lazy `ALL_ERROR_CODES` vector is used for enumeration, while conversion is stateless.

Dependencies and integration points: it depends on the external `raft` crate and the crate-local `ErrorCodeExt`. It is consumed by raftstore or engine code that propagates raft library errors through TiKV's error-code system. The generator binary includes this module.

Risks: the `unreachable!()` arm can panic if upstream raft starts returning `RequestSnapshotDropped` through a path that calls `error_code()`. Any new `raft::Error` variants require updating this match or compilation will fail. Descriptions and workarounds remain empty.

Test signals: there are no local tests for the mapping. Exhaustiveness of the match is a compile-time signal for most variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raft.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raftstore.rs -->
# sources/storage-engines/tikv/components/error_code/src/raftstore.rs

Purpose: this module defines raftstore error codes under `KV:Raftstore:` and maps `kvproto::errorpb::Error` protobuf payloads to stable codes.

Important APIs and constants: the namespace includes region/leader errors (`NOT_LEADER`, `REGION_NOT_FOUND`, `KEY_NOT_IN_REGION`, `EPOCH_NOT_MATCH`), store/transport errors (`DISK_FULL`, `STORE_NOT_MATCH`, `TRANSPORT`, `TIMEOUT`), command state errors (`STALE_COMMAND`, `READ_INDEX_NOT_READY`, `PROPOSAL_IN_MERGING_MODE`, `DATA_IS_NOT_READY`), flashback/recovery/witness errors, and snapshot errors (`SNAP_ABORT`, `SNAP_TOO_MANY`, `SNAP_UNKNOWN`). `ALL_ERROR_CODES` is generated.

Control flow: `impl ErrorCodeExt for errorpb::Error` checks `has_*` fields in priority order and returns the first matching code. The order matters when a protobuf contains multiple sub-errors. Several declared constants, such as `PENDING_PREPARE_MERGE`, `MISMATCH_PEER_ID`, and snapshot codes, are not covered by the conversion function, likely because they map from other error types.

State and persistence behavior: no mutable state exists beyond the lazy catalog vector. Conversion is read-only over the protobuf message.

Dependencies and integration points: it depends on `kvproto::errorpb` and is central to client-visible raftstore error reporting. The generator binary includes this module.

Risks: unmapped declared constants and fallback to `UNKNOWN` can hide precise protobuf fields if new `errorpb::Error` variants are added without updating the match chain. The priority order should be treated as part of the contract. Descriptions are empty, so downstream UX relies on code names.

Test signals: there are no tests in this file for the `has_*` mapping order. Compile-time availability of protobuf methods is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/raftstore.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/sst_importer.rs -->
# sources/storage-engines/tikv/components/error_code/src/sst_importer.rs

Purpose: this module declares SST importer error codes under `KV:SstImporter:`, used by TiKV import/ingest paths.

Important APIs and constants: the namespace covers I/O and transport (`IO`, `GRPC`), identifiers and futures (`UUID`, `FUTURE`), RocksDB/engine failures (`ROCKSDB`, `ENGINE`), file validation (`FILE_EXISTS`, `FILE_CORRUPTED`, `INVALID_SST_PATH`, `INVALID_CHUNK`, `BAD_FORMAT`, `FILE_CONFLICT`), external storage (`CANNOT_READ_EXTERNAL_STORAGE`), API/TTL/key-mode compatibility, request staleness, disk space, mismatched requests, and `ERROR_WRAPPER`. `SUSPENDED` includes non-empty diagnostic metadata.

Control flow and state: this is declarative macro expansion with lazy `ALL_ERROR_CODES`. No conversion trait implementation is local to the file.

Dependencies and integration points: importer code maps domain errors to these constants, and `bin.rs` includes the namespace in generated catalog output.

Risks: `RESOURCE_NOT_ENOUTH` has a spelling error in the constant name while the suffix is `ResourceNotEnough`; changing the Rust constant would affect source compatibility. Most descriptions are empty. Some code suffix casing, such as `MisMatchedRequest`, may be externally stable despite inconsistency.

Test signals: no module-local tests exist. Compilation checks macro syntax only.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/sst_importer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/storage.rs -->
# sources/storage-engines/tikv/components/error_code/src/storage.rs

Purpose: this module defines storage/MVCC/transaction error codes under `KV:Storage:`.

Important APIs and constants: general scheduler and request codes include `TIMEOUT`, `EMPTY_REQUEST`, `CLOSED`, `IO`, `SCHED_TOO_BUSY`, `GC_WORKER_TOO_BUSY`, `KEY_TOO_LARGE`, `INVALID_CF`, and `CF_DEPRECATED`. Data-format and API codes include `TTL_NOT_ENABLED`, `TTL_LEN_NOT_EQUALS_TO_PAIRS`, `PROTOBUF`, `INVALID_TXN_TSO`, `INVALID_REQ_RANGE`, `BAD_FORMAT_LOCK`, `BAD_FORMAT_WRITE`, `API_VERSION_NOT_MATCHED`, and `INVALID_KEY_MODE`. Transaction codes include `COMMITTED`, `PESSIMISTIC_LOCK_ROLLED_BACK`, `TXN_LOCK_NOT_FOUND`, `TXN_NOT_FOUND`, `LOCK_TYPE_NOT_MATCH`, `WRITE_CONFLICT`, `DEADLOCK`, `ALREADY_EXIST`, `DEFAULT_NOT_FOUND`, `COMMIT_TS_EXPIRED`, `KEY_VERSION`, `PESSIMISTIC_LOCK_NOT_FOUND`, and `COMMIT_TS_TOO_LARGE`.

Control flow and state: this is a declarative module with no local conversion implementation. It creates `ALL_ERROR_CODES` through the macro.

Dependencies and integration points: TiKV storage, transaction, scheduler, GC, API-version, flashback, and assertion paths can use these constants. The generator binary includes this module.

Risks: the large mixed namespace means downstream mapping must be precise; using `UNKNOWN` or general `IO` can obscure transaction safety issues. Descriptions and workarounds are empty despite many codes being user-actionable.

Test signals: no local tests exist beyond macro expansion during compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/Cargo.toml -->
# sources/storage-engines/tikv/components/external_storage/Cargo.toml

Purpose: this manifest defines the non-published `external_storage` crate, TiKV's abstraction layer for local, HDFS, S3, GCS, Azure Blob, and noop storage used by backup, restore, import, and export workflows.

Important build surface: it exposes a `failpoints` feature and an example binary `scli` at `examples/scli.rs`. Runtime dependencies include cloud provider crates (`aws`, `azure`, `gcp`, `gcp_v2`, `cloud`), `encryption`, `file_system`, protobuf definitions through `kvproto`, async libraries, `openssl`, `serde`, `tokio`, `walkdir`, and metrics through `prometheus`.

Integration points: the crate bridges TiKV BR protobuf `StorageBackend` messages to concrete storage implementations. It reuses `file_system::Sha256Reader` for encrypted checksum tracking and `encryption` for local restore encryption and remote file decryption.

State and persistence behavior: the manifest itself has no state, but it wires crates that persist local files, invoke HDFS commands, and write/read remote object storage. The selected dependencies indicate both async stream behavior and blocking file compatibility through `tokio-util`.

Risks: the crate has many optional operational dependencies and provider-specific behavior, so feature and workspace version drift can break storage creation. The example-only `structopt`, `rust-ini`, and `hyper` dev dependencies are separated from runtime dependencies.

Test signals: manifest coverage is indirect through crate tests, provider adapter compilation, and the `scli` example target.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/examples/scli.rs -->
# sources/storage-engines/tikv/components/external_storage/examples/scli.rs

Purpose: this example implements `scli`, a small command-line tool for saving a local file to an external storage backend or loading an object back to a local file. It demonstrates the public `external_storage` construction and read/write APIs.

Important APIs and functions: `Opt` defines CLI flags for backend type, local file, remote name, local/HDFS path, credential file, endpoint, region, bucket, prefix, and subcommand. `StorageType` supports `Noop`, `Local`, `Hdfs`, `S3`, `GCS`, and `Azure`. Helper functions build protobuf `StorageBackend` values: `create_s3_storage`, `create_gcs_storage`, and `create_azure_storage` parse flags and optional INI/JSON credential data. `process` selects a backend, calls `create_storage`, then dispatches `Save` or `Load`.

Control flow: for save, it opens the local file, gets metadata length, wraps it with `AllowStdIo`, and calls `storage.write` through `block_on_external_io`. For load, it calls `storage.read`, creates the local output file, starts a Tokio runtime, and copies the async reader into the blocking file wrapper.

State and persistence behavior: save persists remote objects or local-storage files; load overwrites/creates the local file. Credentials are read from disk but not persisted. Errors are printed by `main` instead of returned with process-specific exit handling.

Dependencies and integration points: it integrates `structopt`, `rust-ini`, BR protobuf backend messages, `futures_util::copy`, `tokio::Runtime`, and the crate's backend helper constructors. It is an example, not a production CLI.

Risks: `opt.path.unwrap()` is used for local and HDFS storage, so missing path panics rather than producing a clean error. S3 requires region and bucket, while GCS/Azure require bucket. Credential parsing assumes a `default` INI section with specific key names. The load path uses `storage.read` directly, so HDFS, whose read is unimplemented, is not usable for load.

Test signals: no tests exist in the example. Its value is compile-time example coverage and manual smoke testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/examples/scli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/export.rs -->
# sources/storage-engines/tikv/components/external_storage/src/export.rs

Purpose: this module adapts protobuf `StorageBackend` configurations and provider-specific blob clients into the crate's `ExternalStorage` trait. It also provides helper constructors and a wrapper for encrypted local restore files.

Important APIs and types: `create_storage` dispatches to `create_backend`. `make_s3_backend`, `make_local_backend`, `make_hdfs_backend`, `make_noop_backend`, `make_gcs_backend`, and `make_azblob_backend` build protobuf backend messages. `Compat<Blob>` wraps cloud `BlobStorage + IterableStorage + DeletableStorage` clients and implements `ExternalStorage`. `AutoEncryptLocalRestoredFileExternalStorage<S>` delegates all storage operations but overrides `restore` to create the local output file through an `encryption::DataKeyManager`.

Control flow: `create_backend` matches `StorageBackend_oneof_backend`: local creates `LocalStorage`, HDFS creates `HdfsStorage`, noop creates `NoopStorage`, S3 configures multipart size, GCS optionally selects `gcp_v2`, Azure constructs `AzureStorage`, and unsupported `CloudDynamic` returns an error. Creation latency is recorded through `record_storage_create`.

State and persistence behavior: backend creation mostly builds client objects. `AutoEncryptLocalRestoredFileExternalStorage::restore` mirrors the default restore pipeline: read full/range object, optionally checksum encrypted bytes, decrypt if needed, decompress if needed, then write through a local encrypted file writer and validate length/checksums.

Dependencies and integration points: it integrates `aws`, `azure`, `gcp`, `gcp_v2`, `cloud::blob`, `kvproto::brpb`, `DataKeyManager`, and crate-level helpers such as `compression_reader_dispatcher`, `encrypt_wrap_reader`, and `read_external_storage_into_file`.

Risks: unsupported or missing backend variants return generic `NotFound` errors. GCS v1/v2 selection is a config flag, so behavior can diverge across deployments. The encrypted restore wrapper duplicates much of the default restore logic, so future restore-pipeline changes must be applied in both places.

Test signals: `test_create_storage` verifies local path errors, valid local storage creation, noop creation, and invalid empty backends. Provider-specific creation is not exercised here.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/export.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/hdfs.rs -->
# sources/storage-engines/tikv/components/external_storage/src/hdfs.rs

Purpose: this module implements an export-only `ExternalStorage` backend for HDFS by spawning the Hadoop `hdfs dfs -put` command and streaming data into its stdin.

Important APIs and types: `HdfsConfig` holds optional `hadoop_home` and `linux_user`. `HdfsStorage::new` parses and normalizes a remote HDFS URL to a trailing slash. `get_hadoop_home`, `get_linux_user`, and `get_hdfs_bin` resolve command configuration from explicit config or environment variables. `try_convert_to_path` converts hostless `hdfs:///path` URLs to plain `/path` for the HDFS CLI.

Control flow: `write` rejects names containing the platform path separator, resolves the HDFS binary from `$HADOOP_HOME` or config, joins the remote base URL with the object name, builds an optional `sudo -u <user>` command prefix, spawns the process with piped stdin/stdout/stderr, copies the async reader into stdin, waits for command completion, and returns an error with logged stdout/stderr if the command exits non-zero.

State and persistence behavior: successful `write` persists the object in HDFS through the external CLI. The backend does not support reads, ranged reads, listing, or delete; those methods are either `unimplemented!` or return `crate::unimplemented()`.

Dependencies and integration points: it depends on `tokio::process::Command`, `tokio::io::copy`, `url::Url`, and the `ExternalStorage` trait. It is selected by `create_backend` when a BR `Hdfs` backend is supplied.

Risks: read methods panic via `unimplemented!`, unlike `iter_prefix` and `delete`, which return unsupported errors. This makes HDFS unsafe for restore/load paths that call `read`. Command invocation depends on local Hadoop installation, environment, and optional sudo behavior. Name validation rejects nested paths for HDFS, unlike local storage.

Test signals: tests cover `get_hdfs_bin` environment/config resolution and `try_convert_to_path` behavior. There is no integration test that runs a real HDFS command.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/hdfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/lib.rs -->
# sources/storage-engines/tikv/components/external_storage/src/lib.rs

Purpose: this is the root of the `external_storage` crate. It defines the `ExternalStorage` trait, common restore/read helpers, encryption/compression/checksum plumbing, backend config structs, and public module exports.

Important APIs and types: `ExternalStorage` requires `name`, `url`, async `write`, `read`, `read_part`, `iter_prefix`, and `delete`; it also provides a default async `restore`. `UnpinReader` erases reader types for async trait signatures. `BackendConfig` carries S3 multipart size, GCP v2 selection, and HDFS config. `RestoreConfig` carries range, compression type, expected plaintext checksum, file encryption info, and optional encrypted checksum. Helpers include `compression_reader_dispatcher`, `encrypt_wrap_reader`, `read_external_storage_into_file`, `read_external_storage_info_buff`, and `wrap_with_checksum_reader_if_needed`.

Control flow: default `restore` chooses full or ranged read, optionally wraps a SHA-256 reader around encrypted bytes, optionally decrypts, dispatches compression (unknown means uncompressed, zstd gets a decoder), creates the local output through `file_system::File`, and copies through `read_external_storage_into_file`. That copy loop applies per-read timeout based on a minimum speed, consumes a `Limiter`, writes to output, optionally hashes plaintext, yields periodically, validates expected length, validates encrypted checksum, and validates plaintext checksum.

State and persistence behavior: restore persists a local file. Checksum state is held in OpenSSL `Hasher` instances, including a shared hasher behind `Arc<Mutex<Hasher>>` for encrypted-byte streaming. No backend registry state is maintained.

Dependencies and integration points: the root exports `LocalStorage`, `HdfsStorage`, `NoopStorage`, `IterableStorage`, locking, metrics, and all exports from `export.rs`. It integrates `async-compression`, `encryption`, `file_system`, `kvproto`, `openssl`, `tikv_util::Limiter`, and Tokio timeout/yielding.

Risks: `calc_and_compare_checksums` calls `finish` while holding a mutex guard; callers must treat the hasher as consumed after validation. Default restore creates the output file before validating final checksums, so failed validation can leave a partial or invalid local file. `CompressionType::Unknown` is treated as uncompressed for compatibility with old log files, which is intentional but easy to misread.

Test signals: tests for helper functions are not in this file excerpt, but downstream tests in backend modules and compile-time trait implementations cover major paths. The key behavioral risk areas are timeout behavior, partial output cleanup, and checksum ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/local.rs -->
# sources/storage-engines/tikv/components/external_storage/src/local.rs

Purpose: this module implements `ExternalStorage` on top of the local filesystem. It is used for local backup/restore paths and as a testable backend for the trait.

Important APIs and types: `LocalStorage` stores a base `PathBuf` and an `Arc<tokio::fs::File>` opened on the base directory for directory fsync. `LocalStorage::new` opens the base directory and supports a failpoint that can sleep during creation. `tmp_path` creates a random temp filename in the target directory using suffix `tmp<random_hex>`. `url_for` produces `local:///...`.

Control flow: `write` rejects absolute paths and empty names, creates parent directories under the base, logs if overwriting, writes to a random temp file, copies the incoming reader into it, fsyncs the temp file, renames it over the final path, then fsyncs the base directory. `read` opens a standard file and wraps it in `AllowStdIo`, returning an error stream if open fails. `read_part` seeks to an offset and returns a `take(len)` reader. `iter_prefix` either walks a directory fast-path or walks the parent and byte-prefix-filters paths, returning relative `BlobObject` keys. `delete` removes a file if present and fsyncs the base directory.

State and persistence behavior: writes are durable best-effort through temp-file, file fsync, rename, and directory fsync. Existing files can be overwritten to match S3 put semantics. Parent directories are created automatically, and nested relative paths are allowed.

Dependencies and integration points: it uses `tokio::fs`, `walkdir`, `rand`, `futures`, `tikv_util::stream::error_stream`, and the crate's trait types. It is created by `make_local_backend`/`create_storage`.

Risks: the comment notes that `../` components could escape the base path because internal names are assumed controlled by TiKV; this is a path traversal risk if names become user-controlled. Only the base directory is fsynced after nested writes/deletes, not necessarily every newly created parent directory. Prefix matching intentionally compares raw bytes, which avoids `Path::starts_with` pitfalls but must handle platform path encoding carefully.

Test signals: tests cover basic write/read, nested paths, empty and absolute name rejection, URL formatting, and overwrite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/locking.rs -->
# sources/storage-engines/tikv/components/external_storage/src/locking.rs

Purpose: this module implements advisory remote locks over eventually regular `ExternalStorage` operations, assuming strong consistency for PUT and LIST. It supports shared read locks and exclusive write locks through an intent-file, write-and-verify protocol.

Important APIs and types: `LockMeta` serializes lock metadata: timestamp, host, pid, transaction id, and hint. `RemoteLock` records a lock file path and txn id and exposes `unlock`. `LockExt` adds async `lock_for_read` and `lock_for_write`. `ExclusiveWriteCtx` exposes `txn_id`, `intent_file_name`, `verify_only_my_intent`, and prefix checks. `ExclusiveWriteTxn` describes a transactional write with a target path, content, and optional verify step. `ExclusiveWriteExt` implements `exclusive_write` for `dyn ExternalStorage`.

Control flow: `exclusive_write` generates a UUID, verifies only the current intent can exist, runs transaction-specific verification, writes an empty intent file, re-verifies, writes the final lock file content, then deletes the intent. Read locks write `$path.READ.<random>` and verify no `$path.WRIT` file exists. Write locks write `$path.WRIT` and verify no files under the base lock prefix except the current intent exist. `unlock` reads the lock file, deserializes `LockMeta`, checks the txn id, and deletes the file.

State and persistence behavior: lock state is encoded entirely as remote objects. Intent files are temporary but may remain if a process dies before cleanup. There is no TTL, lease renewal, or automatic stale-lock cleanup.

Dependencies and integration points: it uses `serde_json`, `uuid`, `chrono`, TiKV hostname/pid helpers, `iter_prefix`, `write`, `read`, and `delete` from `ExternalStorage`. It is useful for backup/restore coordination over object stores with strong listing semantics.

Risks: the module documents possible live locks under heavy contention and performs no internal retries. Correctness depends on strong consistency for both PUT and LIST; weaker stores can admit multiple writers. Stale intent or lock files can block future lockers indefinitely. `unlock` refuses to delete if metadata txn id does not match, which protects against deleting someone else's lock.

Test signals: tests use `LocalStorage` to verify read locks block writes, write locks block reads, unlocking permits later locks, and mismatched txn ids cannot unlock others' locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/locking.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/metrics.rs -->
# sources/storage-engines/tikv/components/external_storage/src/metrics.rs

Purpose: this module defines Prometheus metrics for external-storage creation latency.

Important APIs and constants: `EXT_STORAGE_CREATE_HISTOGRAM` is a `HistogramVec` registered as `tikv_external_storage_create_seconds` with label `type` and exponential buckets from 10 microseconds upward. The crate root's `record_storage_create` observes this histogram with `storage.name()`.

Control flow and state: the metric is lazily registered through `lazy_static!`. Creation timing is recorded by callers after backend construction succeeds.

Dependencies and integration points: it depends on `prometheus` and is used by `export.rs`/`lib.rs`. It emits metrics for local, HDFS, noop, S3, GCS, Azure, or other `ExternalStorage` implementors based on their `name`.

Risks: failed backend creation is not observed because recording occurs after a concrete storage object exists. Label cardinality is low as long as `name()` returns static backend types. Registration unwraps, so duplicate metric names in the process would panic during initialization.

Test signals: no local tests exist; metric registration is checked by crate initialization in tests that call storage creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/noop.rs -->
# sources/storage-engines/tikv/components/external_storage/src/noop.rs

Purpose: this module implements a no-op `ExternalStorage` backend, mainly for tests and plumbing paths that need to consume streams without persisting objects.

Important APIs and types: `NoopStorage` is `Clone + Default`. `url_for` returns `noop:///`. The `ExternalStorage` implementation reports name `noop`, consumes all bytes on `write`, returns empty readers for `read` and `read_part`, returns an empty stream for `iter_prefix`, and returns success for `delete`.

Control flow: `write` copies the input reader to `tokio::io::sink()` rather than ignoring it. This is important because upstream wrappers such as checksum readers rely on the stream being fully consumed.

State and persistence behavior: no data is stored. Reads always return EOF, listings are empty, and deletes are idempotent no-ops.

Dependencies and integration points: it uses `tokio::io`, futures streams/futures, and `tokio-util` compatibility adapters. It is selected by `make_noop_backend`/`create_storage`.

Risks: because writes succeed and reads return empty data, accidentally using noop in production could silently discard backups or exports. It should remain clearly test-oriented. Content length is ignored.

Test signals: tests verify that writing succeeds, reading returns empty data, and the backend URL is `noop:///`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/noop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/Cargo.toml -->
# sources/storage-engines/tikv/components/file_system/Cargo.toml

Purpose: this manifest defines the `file_system` crate, a TiKV workspace component that wraps filesystem APIs with I/O typing, statistics, rate limiting, checksums, and recovery-space helpers.

Important build surface: features include `bcc-iosnoop` for optional BCC/eBPF disk tracing, `failpoints`, and `testexport`. Dependencies include `fs2` for file allocation/locking, `crc32fast`, `openssl`, `prometheus`, `prometheus-static-metric`, `online_config`, `parking_lot`, `crossbeam-utils`, `strum`, `tokio`, and Linux-only optional `bcc` plus `thread_local`.

Integration points: the crate exports replacements or wrappers for many `std::fs` functions, `File`, `OpenOptions`, `IoRateLimiter`, `IoBytesTracker`, I/O stats collectors, and `Sha256Reader`. It is used by external storage restore code and TiKV subsystems that need disk I/O accounting.

State and persistence behavior: the manifest itself has no state, but it enables code paths that reserve disk space, create/delete/sync files, and collect per-thread or eBPF I/O stats.

Risks: enabling `bcc-iosnoop` adds kernel/BCC dependencies and unsafe global state in the implementation. The crate uses `#![feature(test)]`, so test/bench builds require nightly features in TiKV's toolchain.

Test signals: dev dependency `tempfile` supports filesystem unit tests. Linux-only code is conditionally compiled based on target OS and features.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/file.rs -->
# sources/storage-engines/tikv/components/file_system/src/file.rs

Purpose: this module wraps `std::fs::File` and `std::fs::OpenOptions` so file reads and writes can be throttled by the global `IoRateLimiter` using the current thread's `IoType`.

Important APIs and types: `File` stores an inner `fs::File` and an optional `Arc<IoRateLimiter>` captured at open/create time. Constructors include `open`, `create`, `from_raw_file`, `try_clone`, and test-only variants with explicit limiters. It forwards sync, metadata, permissions, length, allocation, duplication, and file-locking methods. `OpenOptions` mirrors standard open options and implements Unix `OpenOptionsExt` on Linux.

Control flow: `Read::read` and `Write::write` check whether a limiter was captured. If present, they loop until the requested buffer is consumed or EOF/zero write occurs, asking `limiter.request(get_io_type(), IoOp::Read/Write, remains)` for the next allowed chunk. Without a limiter, operations delegate directly to the inner file. `Seek` and `flush` are transparent delegates.

State and persistence behavior: the wrapper does not add persistence semantics beyond the inner file, except that write throughput may be sliced and delayed. It snapshots the global limiter when the file is created or opened; later calls to `set_io_rate_limiter` do not affect existing `File` instances.

Dependencies and integration points: it integrates `fs2::FileExt`, crate-level `IoOp`, `IoRateLimiter`, `get_io_rate_limiter`, and `get_io_type`. The crate root re-exports `File` and `OpenOptions`.

Risks: limiter requests are based on the full remaining buffer, but the underlying OS read/write may return less, so statistics can include EOF reads, as the tests document. Existing files may keep an old limiter after global replacement. Blocking rate limiting occurs in synchronous read/write calls.

Test signals: `test_instrumented_file` verifies throttled writes/reads and statistics by I/O type. `test_unix_file_allocate_failure` validates allocation error behavior for zero length on Unix.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.c -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.c

Purpose: this BCC/eBPF C program tracks block I/O bytes and latency per TiKV `IoType`. It is compiled and loaded by `biosnoop.rs` when the `bcc-iosnoop` feature is enabled.

Important APIs and data structures: `stats_t` stores read/write bytes. `io_type` mirrors Rust `IoType` values. `info_t` stores I/O type and start timestamp per kernel `request`. BPF maps include `info_by_req`, `type_by_pid`, and `stats_by_type`, plus per-type read/write latency histograms.

Control flow: `trace_req_start` runs on `blk_account_io_start`, filters by the TiKV process TGID placeholder, reads the current thread's `io_type *` from `type_by_pid`, stores the type and timestamp in `info_by_req`, and defaults to `Other` if unavailable. `trace_req_completion` runs on `blk_account_io_completion`, looks up request info, detects read/write using kernel-version-compatible request flags, increments byte counters, buckets latency in microseconds using `bpf_log2l`, updates the matching histogram, deletes the request info, and exits.

State and persistence behavior: all state is in BPF maps in kernel memory and is consumed by the Rust wrapper. It is not persistent across process restarts or BPF detach.

Dependencies and integration points: it relies on Linux block-layer probe symbols, BCC macros, a Rust-substituted `##TGID##`, and the `type_by_pid` map being populated with user-space addresses of Rust `IoType` slots.

Risks: the C enum must stay exactly aligned with Rust `IoType`; the comment notes auto-generation is TODO. A concrete bug is visible in the `LevelZeroCompaction` write case: it calls `level_zero_replication_write_latency.increment(...)`, but the declared histogram is `level_zero_compaction_write_latency`; this looks like a compile/load failure or missing metric update depending on BCC handling. Kernel API compatibility is fragile around request flag fields and probe symbol names.

Test signals: no tests in the C file itself; Rust `biosnoop.rs` tests exercise compilation/loading and I/O accounting when BCC is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.rs -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.rs

Purpose: this module implements the optional Linux/BCC I/O stats collector. It loads `biosnoop.c`, attaches block I/O kprobes, maps TiKV threads to `IoType` slots, fetches per-type byte counters, and flushes latency histograms.

Important APIs and types: `BpfContext` owns the `BPF`, stats table, and type table. `IO_TYPE_ARRAY` is a global padded array of per-thread types with `MAX_THREAD_IDX + 1` slots. `IdxAllocator` assigns slots, and `IdxWrapper` frees them on thread-local drop. Public APIs are `init`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, `flush_io_latency_metrics`, and `get_thread_io_bytes_total` (currently unimplemented).

Control flow: `IDX` thread-local allocation registers the current thread id in the BPF `type_by_pid` table with a pointer to its slot. `set_io_type` writes the slot unless the overflow slot is used. `init` substitutes the process id into included C code, compiles it with BCC, attaches kprobes to `blk_account_io_start` and `blk_account_io_completion`, and stores tables in global `BPF_CONTEXT`. `fetch_io_bytes` iterates all Rust `IoType` values and reads `IoBytes` from the BPF table. `flush_io_latency_metrics` drains BPF histogram buckets into Prometheus histograms and zeros them.

State and persistence behavior: it uses unsafe mutable global BPF context and global thread-type slots. When all thread-local indices are freed, `IdxWrapper::drop` takes the BPF context to detach probes. Metrics are in-memory only.

Dependencies and integration points: it depends on `bcc`, `strum`, `crossbeam_utils`, TiKV thread helpers, and file-system metrics. `io_stats/mod.rs` selects this implementation for Linux with `bcc-iosnoop`.

Risks: unsafe global state and pointer sharing with eBPF require tight lifetime assumptions. More than 192 threads fall back to the reserved slot, always `Other`, losing attribution. `get_thread_io_bytes_total` returns unimplemented, so `IoBytesTracker` cannot use this collector for per-thread totals. The included C probe contains the `level_zero_replication_write_latency` typo, making the optional path risky until fixed.

Test signals: tests initialize BPF, run direct I/O reads/writes, validate per-type byte deltas, test thread-index allocation, flush latency metrics, and include a benchmark. They require kernel/BCC capabilities and can be environment-sensitive.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/biosnoop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/mod.rs -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/mod.rs

Purpose: this module selects the platform-specific I/O statistics implementation and provides a stub for unsupported targets.

Important APIs: it re-exports `init`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, and `get_thread_io_bytes_total` from one of three implementations: a stub, `biosnoop`, or `proc`. The stub maintains a thread-local `IoType`, returns zero bytes, and reports `init` failure with "No I/O tracing tool available".

Control flow: conditional compilation chooses the implementation. Non-Linux or feature combinations that are not `target_os = "linux"` with or without `bcc-iosnoop` get the stub. Linux with `bcc-iosnoop` uses eBPF/BCC; Linux without that feature uses `/proc` polling. Test-only aligned `A512` supports O_DIRECT tests.

State and persistence behavior: the module itself has no state beyond the selected implementation. The stub's only state is thread-local I/O type.

Dependencies and integration points: the crate root re-exports these APIs for `WithIoType`, `File`, metrics, and `IoBytesTracker`. The chosen implementation determines whether byte metrics come from OS accounting or zeros.

Risks: the `cfg(not(any(target_os = "linux", feature = "bcc-iosnoop")))` condition means enabling `bcc-iosnoop` on a non-Linux target suppresses the stub while the Linux+BCC module is not selected, which can create missing exports if such a build is attempted. Operational semantics differ significantly between stub, proc, and BCC collectors.

Test signals: benchmarks exercise `fetch_io_bytes` and `set_io_type` under spawned threads. Platform-specific deeper tests live in `proc.rs` and `biosnoop.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/proc.rs -->
# sources/storage-engines/tikv/components/file_system/src/io_stats/proc.rs

Purpose: this module implements the default Linux I/O stats collector by reading `/proc/<pid>/task/<tid>/io` and attributing per-thread byte deltas to the current `IoType`.

Important APIs and types: `ThreadId` stores process id, thread id, and an optional cached `BufReader<File>` over the proc file. `LocalIoStats` stores a `ThreadId`, current I/O type, and last flushed bytes. `AtomicIoBytes` stores global per-type counters. Public APIs are `init`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, and `get_thread_io_bytes_total`.

Control flow: `ThreadId::fetch_io_bytes` lazily opens the proc file, seeks back to the start, parses `read_bytes` and `write_bytes`, and returns totals. `init` verifies proc access, initializes the current thread's sentinel, and hooks TiKV thread startup to create sentinels for new threads. `set_io_type` flushes the current thread's delta into the old type before changing the thread-local and sentinel type. `fetch_io_bytes` flushes every thread-local sentinel and returns global totals.

State and persistence behavior: byte counters are process-local atomics. Per-thread sentinels are held in `ThreadLocal<CachePadded<Mutex<LocalIoStats>>>`. The proc reader is cached per thread. No state is persisted beyond process memory.

Dependencies and integration points: it uses TiKV thread IDs/hooks, `thread_local`, `parking_lot`, and crate-level `IoBytes`/`IoType`. It is selected on Linux when `bcc-iosnoop` is not enabled.

Risks: attribution depends on callers setting `IoType` before disk work; untagged threads accumulate under `Other`. Reading `/proc` can fail due to permissions, process/thread races, or nonstandard environments. Global counters only increase when flushed, so stale threads that never change type are flushed by `fetch_io_bytes`, but dead-thread edge cases depend on `ThreadLocal` iteration behavior.

Test signals: tests use O_DIRECT reads/writes against temp files to verify proc byte deltas, thread I/O type attribution, and current-thread total fetching. These tests are Linux and filesystem dependent.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/io_stats/proc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/lib.rs -->
# sources/storage-engines/tikv/components/file_system/src/lib.rs

Purpose: this crate root re-exports instrumented filesystem APIs and implements common helpers for I/O typing, byte tracking, priorities, file operations, checksums, SHA-256 streaming, and disk-space reservation.

Important APIs and types: public exports include `File`, `OpenOptions`, `init_io_stats_collector`, `set_io_type`, `get_io_type`, `fetch_io_bytes`, `MetricsManager`, `IoRateLimiter`, and rate-limit configuration types. `IoType` enumerates TiKV workload classes such as foreground reads/writes, flush, compaction, replication, import/export, and log rewrite. `WithIoType` temporarily sets the thread I/O type and restores it on drop. `IoBytesTracker` computes deltas from per-thread OS totals, tolerating initial fetch failures. `IoPriority` is serializable/deserializable and convertible to/from `online_config::ConfigValue`.

Control flow: utility functions wrap file operations through instrumented `File`: `write`, `read`, `read_to_string`, `copy`, `copy_and_sync`, deletion/creation helpers, `sync_dir`, CRC32 helpers, and `reserve_space_for_recover`. `Sha256Reader` wraps sync or async readers and updates a shared OpenSSL hasher as bytes are read. `reserve_space_for_recover` maintains a `space_placeholder_file`, reallocating it if size changes and deleting partial files on allocation failure.

State and persistence behavior: `WithIoType` manipulates thread-local state in the selected I/O stats implementation. File helpers persist data and can fsync destination files/directories in `copy_and_sync` and reservation paths. `IoBytesTracker` stores previous/current counters in memory only.

Dependencies and integration points: it integrates `crc32fast`, `openssl`, `online_config`, `serde`, `tokio::io::AsyncRead`, and internal modules. External storage uses `File` and `Sha256Reader` for restore output and checksum validation.

Risks: several helpers assume file sizes fit in `usize` for buffer preallocation. `sync_dir` opens paths through the instrumented `File`, so it captures current limiter state. `IoBytesTracker::update` subtracts current from previous without saturating, assuming proc counters are monotonic. `reserve_space_for_recover` relies on filesystem allocation support and deletes the placeholder on failure.

Test signals: tests cover file size/existence/deletion, directory creation/deletion, directory sync, CRC32 on small/large files, SHA-256 reader behavior, and reserve-space allocation failure through `file.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics.rs -->
# sources/storage-engines/tikv/components/file_system/src/metrics.rs

Purpose: this module defines Prometheus metrics and TLS buffering for file-system I/O bytes, latency, and rate-limiter waits.

Important APIs and metrics: static metric label enums cover `IoType`, `IoOp`, and `IoPriority`. Registered metrics include `tikv_io_bytes` (`IntCounterVec` by type/op), `tikv_io_latency_micros` (`Histogram` by type/op), `tikv_rate_limiter_request_wait_duration_seconds` (`HistogramVec` by priority), and `tikv_rate_limiter_max_bytes_per_sec` (`IntGauge` by priority). `FileSystemLocalMetrics` buffers rate-limiter wait histograms in TLS. Public functions are `tls_flush` and `tls_collect_rate_limiter_request_wait`.

Control flow and state: metrics are globally registered through `lazy_static!`. Request wait observations are recorded into a thread-local local histogram and flushed by `tls_flush`, which `MetricsManager::flush` calls before byte collection.

Dependencies and integration points: `rate_limiter.rs` calls `tls_collect_rate_limiter_request_wait` after sleeping. `metrics_manager.rs` uses `IO_BYTES_VEC` and `tls_flush`. `biosnoop.rs` uses `IO_LATENCY_MICROS_VEC` when draining BPF histograms.

Risks: metric label enums must stay aligned with `IoType` names and eBPF histograms. The label enum currently omits `log_rewrite` despite `IoType::RewriteLog` existing in `lib.rs`, which can limit metric coverage if that type is used in generic iteration elsewhere. Registration unwraps can panic on duplicate metric names.

Test signals: no direct tests exist. Metrics are exercised indirectly by rate limiter and metrics manager tests/usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics_manager.rs -->
# sources/storage-engines/tikv/components/file_system/src/metrics_manager.rs

Purpose: this module turns either rate-limiter counters or OS I/O stats collector values into Prometheus byte counter deltas.

Important APIs and types: `BytesFetcher` has two modes: `FromRateLimiter(Arc<IoRateLimiterStatistics>)`, which reads atomic counters from the limiter, and `FromIoStatsCollector()`, which calls `fetch_io_bytes`. `MetricsManager` stores a fetcher and `last_fetch` array of `IoBytes`.

Control flow: `MetricsManager::flush` first flushes TLS histogram metrics, fetches the latest byte totals, iterates every `IoType`, computes `latest - last_fetch` using saturating subtraction, increments `IO_BYTES_VEC` read/write counters by the delta, and updates `last_fetch`.

State and persistence behavior: manager state is in-memory only. Prometheus counters are process-global and monotonic. `last_fetch` prevents double-counting totals across flushes.

Dependencies and integration points: it depends on `strum::IntoEnumIterator` over `IoType`, `IoRateLimiterStatistics`, `io_stats::fetch_io_bytes`, and `metrics::IO_BYTES_VEC`. TiKV can choose whether metrics come from limiter-observed bytes or OS-observed disk bytes.

Risks: using rate-limiter stats records logical permitted bytes, not necessarily durable disk bytes, while OS collectors record kernel/accounted bytes; switching fetcher modes changes metric meaning. Saturating delta hides counter resets or collector failures as zero rather than negative deltas.

Test signals: no local tests exist. Behavior is small and indirectly covered by limiter statistics and I/O stats tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/rate_limiter.rs -->
# sources/storage-engines/tikv/components/file_system/src/rate_limiter.rs

Purpose: this module implements TiKV's prioritized I/O throughput limiter. It can limit writes, reads, or all I/O, assign priorities per `IoType`, record statistics, and dynamically adjust low-priority budgets.

Important APIs and types: `IoRateLimitMode` supports `WriteOnly`, `ReadOnly`, and `AllIo` and implements serde parsing. `IoRateLimiterStatistics` records read/write bytes per `IoType`. `IoBudgetAdjustor` can adjust low-priority budgets. `IoRateLimiter` exposes `new`, `new_for_test`, `statistics`, `set_io_rate_limit`, `set_io_priority`, `set_low_priority_io_adjustor_if_needed`, sync `request`, async `async_request`, and test-only skewed-clock request. Global `set_io_rate_limiter` and `get_io_rate_limiter` manage the process-wide limiter captured by `File`.

Control flow: `PriorityBasedIoRateLimiter` stores bytes-through and bytes-per-epoch arrays by `IoPriority`, plus protected pending bytes and next refill time. `request_imp!` clamps requests to the current epoch budget, records attempted bytes, returns immediately if within budget or high priority is unrestricted in non-strict mode, otherwise enqueues pending bytes, computes sleep duration, caps any single wait at 500 ms by returning partial quota, records wait metrics, sleeps, and returns granted bytes. `refill` advances epochs, serves pending high/medium bytes first, estimates recent usage, optionally adjusts total budgets before low-priority allocation, and updates per-priority max-byte gauges.

State and persistence behavior: all limiter state is in memory, with atomic counters for hot-path accounting and a mutex for epoch refill/pending queues. Rate limit zero disables flow control. Statistics persist until reset or limiter drop.

Dependencies and integration points: `file.rs` calls `request` while reading/writing, `metrics.rs` records waits and gauges, `MetricsManager` can expose stats, and online config can parse priorities/modes.

Risks: synchronous requests sleep the caller thread, so using the limiter on latency-critical threads requires careful priority config. The algorithm provides best-effort priority isolation, not a hard global cap when high priority can borrow lower-priority budgets in non-strict mode. A single process-global limiter makes test isolation fragile, noted by the "Do NOT use" comment around `set_io_rate_limiter` in test environments.

Test signals: tests cover toggling rate limits, dynamic priority, heavy/light/hybrid flows, approximate throughput, async-compatible logic through the shared macro, and a refill critical-section benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/rate_limiter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/Cargo.toml -->
# sources/storage-engines/tikv/components/health_controller/Cargo.toml

Purpose: this manifest defines the `health_controller` crate, a non-published TiKV component for health reporting/control-plane integration.

Important build surface: the crate is Rust 2021, Apache-2.0 licensed, version `0.1.0`, and depends on workspace crates for collections, `grpcio-health`, `kvproto`, logging, and TiKV utilities. It also uses `ordered-float`, `parking_lot`, and `prometheus`.

Dependencies and integration points: `grpcio-health` indicates integration with gRPC health services; `kvproto` provides TiKV protobuf types; `prometheus` supports health metrics; `slog`/`slog-global` support logging. The manifest does not define extra binaries or features in this file.

State and persistence behavior: the manifest has no runtime state. It declares dependencies for an in-process health controller rather than storage persistence.

Risks: because only the manifest is in scope here, behavioral risks in health scoring or service transitions must be researched from source files outside this work item. Dependency choices suggest concurrency through `parking_lot` and floating-point ordering through `ordered-float`, both of which can matter for health calculations.

Test signals: no tests or dev-dependencies are declared in this manifest. Test coverage must come from crate source modules or workspace-level tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/Cargo.toml -->
