# Research: subset-b-008866

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/server.rs -->
## sources/storage-engines/tikv/components/test_raftstore/src/server.rs

Purpose: builds the TiKV test RaftStore server simulator around `ServerCluster`, giving integration tests a real gRPC server, Raft store, storage engine, coprocessor endpoint, import service, GC worker, lock manager, resolved-ts path, optional in-memory engine, and simulated network filters. Important types include `AddressMap`, `ServerMeta`, `ServerCluster`, `SimulateEngine`, and transport aliases over `SimulateTransport`. `AddressMap` implements `StoreAddrResolver` for deterministic in-process address lookup.

Control flow centers on `ServerCluster::run_node_impl`, dispatched by API version. It allocates or reuses snapshot directories and listen addresses, builds coprocessor hooks, optional hybrid in-memory observers, raft routers, `RaftKv`, read pools, GC/resolved-ts workers, resource metering, import/debug/deadlock services, snapshot manager, `MultiRaftServer`, gRPC `Server`, lock manager, split checking, and finally stores all handles in `metas`. State is held in maps keyed by node/store id: storages, routers, importers, health controllers, snapshot managers, concurrency managers, raft clients, causal providers, and temp dirs.

Integration points are `Simulator` trait methods for start/stop, async commands, local reads, raft messages, filters, and routers, plus cluster constructors and gRPC client helpers. Risks are lifecycle leaks, address reuse after restarts, bind retry assumptions, optional worker cleanup, and filter direction mistakes. Test signals are helper constructors, snapshot retrieval, forwarding check in `setup_cluster`, and panics/asserts around missing leaders and service startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/transport_simulate.rs -->
## sources/storage-engines/tikv/components/test_raftstore/src/transport_simulate.rs

Purpose: provides a programmable network/raft message simulation layer for raftstore tests. `Filter` exposes `before` and `after` hooks over `Vec<RaftMessage>`, while `SimulateTransport<C>` wraps any transport/router and applies shared `RwLock`-protected filters before forwarding messages. It implements `Transport`, `StoreRouter`, `ProposalRouter`, `CasualRouter`, `SignificantRouter`, `RaftStoreRouter`, and `LocalReadRouter`.

Important filters model packet loss, partitions, isolation, region-specific drops, snapshots, delayed/duplicated snapshots, random latency, lease-read context capture/removal, and arbitrary message retain predicates. `filter_send` is the central control path: run `before` filters in order until failure, send retained messages, then run matching `after` hooks in reverse order. Factories generate per-node filters for partitions and isolation.

State is in atomics and mutexes: notification counters, block booleans or allow counts, dropped message buffers, pending snapshot maps, delayed message queues, and captured lease read contexts. There is no persistence; behavior is intentionally transient test state. Dependencies include raftstore router traits, Rocks engine snapshots, raft message protobufs, crossbeam channel errors, and `tikv_util::Either`.

Risks include nondeterminism from random drop/latency filters, `unwrap` in snapshot capture/leading filters when expected sequencing is violated, lock contention inside filters, and inverted semantics of `RegionPacketFilter::when` where false means drop. Test signals are indirect: these filters are meant to be attached by raftstore tests to force elections, snapshot races, lease-read behavior, and network partitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/transport_simulate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/util.rs -->
## sources/storage-engines/tikv/components/test_raftstore/src/util.rs

Purpose: large raftstore test utility module for request construction, engine bootstrap, storage assertions, transactional gRPC helpers, region/log checks, and cluster tuning. It exports `HybridEngineImpl` and reexports peer constructors. APIs cover `must_get*`, request builders for raft commands/admin/status, callback creation, async read/snapshot helpers, engine creation, config mutators, raw/MVCC KV helpers, lock/status assertions, `PeerClient`, region peer lookup, sync waits, and delete-range checks.

Control flow is mostly helper orchestration. Reads and writes build protobuf requests with contexts/epochs, create callbacks through `make_cb`, submit to `Cluster` or `Simulator`, then assert responses. `create_test_engine` and `start_test_engine` allocate temp dirs, configure data/raft paths, encryption, Rocks env/cache, raft engine, SST recovery worker, coprocessor region accessor, and KV engine factory. KV helpers compose prewrite/commit/rollback/check/status gRPC calls.

State and persistence are test-local: temporary Rocks/raft DBs, encryption key files, background SST recovery workers, generated random keys, raft apply/truncated states, and cluster PD timestamps. Dependencies span engine traits, Rocks, raftstore, TiKV storage/server configs, kvproto, failpoints, futures, tempfile, PD client, and txn types.

Risks include retry loops masking slowness, many `unwrap`/panic assertions, assumptions about region 1, raw key encoding, GC/log compaction timing, and maintaining correctness across API versions. Test signals are the module itself: every helper encodes an expected outcome and several helpers (`check_compacted`, `must_region_cleared`, `wait_for_synced`) validate persistence side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore_macro/Cargo.toml -->
## sources/storage-engines/tikv/components/test_raftstore_macro/Cargo.toml

Purpose: crate manifest for the `test_raftstore_macro` procedural macro crate. It declares a private Apache-2.0 package on Rust 2021 and marks the library as `proc-macro = true`.

Important dependency choices are minimal and conventional for Rust macro generation: `proc-macro2` for token representation, `quote` for rendering, and `syn` with `full` plus `extra-traits` for parsing and comparing Rust syntax trees. There are no features, dev-dependencies, build scripts, or runtime dependencies.

Control flow and persistence behavior are Cargo-level only. The manifest integrates with the workspace as a test support crate and produces compiler plugin output consumed by tests using the attribute macro in `src/lib.rs`.

Risks are mostly version compatibility: this uses `syn` 1 APIs such as `attr.path`, so moving to `syn` 2 would require source changes. Because the crate is unpublished and private, its stability contract is internal to TiKV tests. Test signals are downstream compile-time macro expansion and the ability of crates using `#[test_case(...)]` to build generated tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore_macro/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore_macro/src/lib.rs -->
## sources/storage-engines/tikv/components/test_raftstore_macro/src/lib.rs

Purpose: implements the `#[test_case(path::to_cluster_ctor)]` proc macro that turns one generic test body into a module containing one concrete `#[test]` per annotated cluster constructor. It lets raftstore tests run the same body across node/server/v2 cluster builders.

The public API is `test_case(arg, input)`. It parses the input as `ItemFn`, collects the current macro argument and any remaining `#[test_case(...)]` attributes, removes the duplicate attributes from the cloned function, and delegates to `render_test_cases`. Rendering clones the function per case, parses package and method identifiers with `parse_test_case`, inserts `use package::{util::*, method as new_cluster, Simulator};`, adds `#[test]`, renames the function to `package_method`, and wraps all generated tests in a `#[cfg(test)] mod original_name`.

State is entirely compile-time token state; no runtime persistence. Dependencies are `syn`, `quote`, `proc_macro2`, and compiler `proc_macro`.

Risks are parser fragility: `parse_test_case` manually walks token trees and assumes simple `package::method` forms, not arbitrary paths, aliases, generics, or nested modules. It panics on invalid streams, which becomes a compile error. Name generation can collide if package/method combinations normalize identically. Test signals are compile-time expansion of multi-attribute examples and downstream tests that rely on `new_cluster` and `util::*` imports.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore_macro/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_sst_importer/Cargo.toml -->
## sources/storage-engines/tikv/components/test_sst_importer/Cargo.toml

Purpose: manifest for `test_sst_importer`, a private helper crate for SST importer tests. It disables library test harness generation with `[lib] test = false`, which is common for utility crates consumed by integration tests.

Dependencies show the crate's role: Rocks engine and engine traits for SST creation/readback, external storage for backup/restore style streams, futures/grpcio/kvproto for import service clients, `keys` and `txn_types` for TiKV key encoding, `tikv_util` for stream/external IO helpers, `tempfile`, `uuid` for SST metadata IDs, and `crc32fast` for upload integrity.

There is no runtime control flow in the manifest, but it wires the helpers in `src/lib.rs` and `src/util.rs` into the TiKV workspace. State and persistence are delegated to generated temp SST files, local external-storage directories, and Rocks test DBs.

Risks include dependency API drift in grpc streaming, Rocks SST writer traits, and external storage traits. Test signals are downstream SST importer tests compiling and using generated `SstMeta`, upload/write streams, ingest checks, and local storage metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_sst_importer/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_sst_importer/src/lib.rs -->
## sources/storage-engines/tikv/components/test_sst_importer/src/lib.rs

Purpose: provides Rocks-backed SST test fixtures and metadata helpers. It exports `TestEngine`, `RocksSstWriter`, all utilities from `util`, and `PROP_TEST_MARKER_CF_NAME`, a table property marker recording the CF used to create an SST.

Important APIs create test Rocks engines with CF options and optional env, SST readers/writers, CRC32 checksums, DB range assertions, and several SST generators: by numeric range, raw TiDB key/value pairs, plain key/value pairs, or an existing DB. `read_sst_file` reads bytes, computes CRC32, assigns a UUID, fills key range/length/CF name, and returns `(SstMeta, data)`. `TestPropertiesCollectorFactory` injects marker properties into SST table properties.

Control flow is synchronous: build Rocks options, attach the property collector, create DB/SST writer, encode keys through `keys::data_key` or `txn_types::Key`, finish SST, then compute metadata from file bytes. Persistence is explicit on the supplied paths: Rocks DB directories and SST files remain until the test temp dirs are dropped.

Dependencies include `engine_rocks` raw table property APIs, `engine_traits` writer traits, `kvproto::import_sstpb`, `uuid`, `keys`, and `txn_types`. Risks include assuming input KVs are non-empty and sorted enough for SST writing, defaulting CF name to `"default"` in metadata, and panics on file/engine errors. Test signals are range checks and downstream importer tests validating CRC, length, range, CF marker properties, and ingest behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_sst_importer/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_sst_importer/src/util.rs -->
## sources/storage-engines/tikv/components/test_sst_importer/src/util.rs

Purpose: gRPC and external-storage helper module for SST importer tests. It builds upload/write request streams, invokes ingest RPCs, validates ingested raw/txn data, checks cleanup, and constructs restore-style `KvMeta` plus rewrite/range metadata.

Important APIs include `new_sst_meta`, `send_upload_sst`, `send_write_sst`, `must_ingest_sst`, `must_ingest_sst_error`, `ingest_sst`, `check_ingested_kvs(_cf)`, `check_applied_kvs_cf`, `check_ingested_txn_kvs`, `check_sst_deleted`, `make_plain_file`, `rewrite_for`, `register_range_for`, and `local_storage`. The streaming helpers send a metadata message followed by data or write batch, close the sink, and surface send/close errors if the response future fails.

State and persistence are external to the functions: importer service state, uploaded SST files, local storage directories, and in-memory buffers that are written through `ExternalStorage`. `make_plain_file` encodes key/value stream events, records the minimum start ts, length, compression marker, file name, and default CF.

Dependencies are `grpcio`, `futures`, `kvproto` import/tikv/br protobufs, `external_storage`, `tikv_util` event encoding and external IO blocking, `txn_types::Key`, `tempfile`, and `uuid`. Risks include panics on failed RPCs in `must_*`, cleanup polling with fixed 10x10 ms waits, `rewrite_for` requiring equal prefix lengths and existing prefixes, and key ordering assumptions. Test signals are direct assertions on raw get, batch get, region/import errors, and cleanup upload retry.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_sst_importer/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/Cargo.toml -->
## sources/storage-engines/tikv/components/test_storage/Cargo.toml

Purpose: manifest for `test_storage`, a private test helper crate that wraps TiKV storage APIs with synchronous test utilities and assertions.

Features mirror `test_raftstore` engine combinations: default RocksDB KV plus raft-engine, plus optional all-RocksDB and panic-engine modes. This keeps storage tests able to switch underlying engine implementations through feature propagation to `test_raftstore`.

Dependencies identify the integration surface: `api_version`, `engine_rocks`, `engine_traits`, `kvproto`, `raftstore`, `test_raftstore`, `tikv`, `tikv_util`, `tracker`, `txn_types`, `collections`, and `futures`. The crate depends heavily on TiKV's storage command API and raftstore cluster helpers.

State and persistence are controlled by the Rust sources rather than Cargo; this manifest controls compile-time feature selection only. Risks include feature drift if `test_raftstore` feature names change, and tight coupling to internal TiKV workspace crates. Test signals are compile coverage under the different feature sets and downstream storage tests importing the reexported helper modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/assert_storage.rs -->
## sources/storage-engines/tikv/components/test_storage/src/assert_storage.rs

Purpose: high-level assertion wrapper around `SyncTestStorage` for MVCC, raw KV, Raft-backed storage, locks, scans, GC, and error-shape validation. `AssertionStorage<E, F>` carries a synchronous store plus request `Context`; aliases specialize API v1.

Important APIs include constructors for plain Rocks and Raft storage, cluster leader refresh through `update_with_key_byte`, two-phase write/delete helpers with retry on not-leader/stale-command, get/batch/scan assertion methods, prewrite conflict/lock checks, commit/cleanup/rollback/resolve-lock/GC/delete-range helpers, raw KV CRUD/scan/batch/atomic/checksum assertions, and reusable GC test scenarios.

Control flow wraps storage calls, converts raw byte keys into `txn_types::Key`, and asserts either exact values or specific error variants. Raft-backed helpers retry a small number of times, inspect nested storage/txn/mvcc errors for region leadership failures, update context/engine to the current leader, then retry. State is the mutable `ctx` and `store` reference for raft tests; data persistence is in the underlying engine and raft cluster.

Dependencies include `test_raftstore`, `tikv::storage`, `kvproto`, `txn_types`, `api_version`, and `tikv_util` locks. Risks include fragile pattern matching on boxed error internals, retry count of three, assumptions about leader lookup by key, and panic-heavy test behavior. Test signals are explicit assertion helpers for success, error, invalid TSO, write conflict, lock contents, raw atomic compare-and-swap, checksum, and GC outcomes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/assert_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/lib.rs -->
## sources/storage-engines/tikv/components/test_storage/src/lib.rs

Purpose: crate root for test storage helpers. It enables the unstable `box_patterns` feature required by error-pattern matches in assertion code, imports `tikv_util` macros, declares internal modules, and reexports all public helpers from `assert_storage`, `sync_storage`, and `util`.

There are no runtime functions in this file. Its API is the aggregated public surface of the crate: synchronous storage wrappers, assertion helpers, raft-engine macros, and utility constructors. Control flow is compile-time module wiring.

State and persistence are absent here, but the reexports expose helpers that create temporary engines, raft clusters, storage contexts, and GC workers. Dependencies are indirect through the submodules and `tikv_util` macros.

Risks are crate-wide: use of nightly-only `box_patterns` and macro import style means compiler/toolchain changes can break tests before runtime. Test signals are successful compilation of downstream tests that import `test_storage::*` rather than individual modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/sync_storage.rs -->
## sources/storage-engines/tikv/components/test_storage/src/sync_storage.rs

Purpose: converts TiKV async `Storage` APIs into blocking test APIs. `SyncTestStorageBuilder<E, F>` builds a `SyncTestStorage<E, F>` from either a default test Rocks engine or a provided engine, optional storage config, and optional GC config. `SyncTestStorage` owns a `Storage<E, MockLockManager, F>` and a `GcWorker<E>`.

Important APIs cover MVCC reads, batch gets, command batch gets, scans/reverse scans, prewrite/commit/cleanup/rollback, lock scanning and resolution, GC, delete range, raw get/put/delete/scan/batch/atomic operations, checksum, and `start_auto_gc`. Async futures are blocked with `block_on`; callback-based commands use `wait_op!`.

Control flow for building storage constructs a `TestStorageBuilder` from engine plus mock lock manager, sets API version, starts a GC worker with a mock region provider, then returns the wrapper. Operation methods mostly pass through context, keys, timestamps, CF names, and options to the underlying storage command.

State and persistence live in the underlying engine and in the started GC worker. `SyncTestStorage` clones the storage and engine handles, while callbacks are synchronous waits. Dependencies include `tikv::storage`, command types, `GcWorker`, raftstore mock region providers, kvproto request types, futures, tracker tokens, and txn types.

Risks include deadlocks or hangs if callback paths fail to invoke `wait_op!`, mock lock manager differences from production, GC worker lifecycle cleanup by drop only, and fixed raw TTL defaults of zero. Test signals are the assertion layer and direct downstream use of blocking return values/errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/sync_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/util.rs -->
## sources/storage-engines/tikv/components/test_storage/src/util.rs

Purpose: small utility module for constructing raft-backed storage fixtures. It exports macros for selecting leader/follower raft engines and functions that build `SyncTestStorage` from a running `test_raftstore::ServerCluster`.

Important APIs are `prepare_raft_engine!`, `leader_raft_engine!`, `follower_raft_engine!`, `new_raft_engine`, and `new_raft_storage_with_store_count`. The macros run the cluster if needed, force leader election with `must_get`, locate the region for a key, derive `Context` with region id, epoch, and peer, and return cloned `SimulateEngine` handles for leader or followers.

Control flow creates a new server cluster, runs it, extracts engine/context, and builds `SyncTestStorageBuilder::from_engine(engine).build(store_id)`. State and persistence are in the raft cluster and underlying engines; this module only picks handles and contexts.

Dependencies are `api_version::KvFormat`, `kvproto::Context`, `test_raftstore` cluster/server types, and `tikv_util::HandyRwLock`. Risks include using peer id vs store id carefully when indexing `storages`, assuming a leader is elected after `must_get`, and macro hygiene because the macros expand into caller scope. Test signals are downstream raft storage tests using leader/follower contexts to verify stale reads, leadership errors, and replicated storage behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_storage/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/Cargo.toml -->
## sources/storage-engines/tikv/components/test_util/Cargo.toml

Purpose: manifest for the shared `test_util` crate. It is a private Apache-2.0 Rust 2021 package of general testing helpers for TiKV components.

Dependencies cover the helper scope: `backtrace` for CI warmup and leak diagnostics, `chrono`/`slog`/`slog-global`/`time` for test logging, `fail` for failpoint test runners, `grpcio` and `security` for TLS fixtures, `encryption_export`/`kvproto` for encryption helpers, `rand`/`rand_isaac` for data generation, `tempfile`, `tikv_util`, collections, and log redaction wrappers.

Control flow is Cargo-level; source modules provide setup, logging, cert loading, encryption key managers, retry macros, and custom test framework runners. State and persistence are source-managed through temp dirs, env vars, log files, cert files, and failpoint thread locals.

Risks include tight coupling to nightly test framework internals, workspace crate APIs, and generated cert paths. Test signals are broad downstream usage plus benches in `kv_generator` and custom runner integration with Rust's unstable `test` crate.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/data/generate_certs.sh -->
## sources/storage-engines/tikv/components/test_util/data/generate_certs.sh

Purpose: regenerates TLS fixture certificates for `test_util` security tests. It writes CA key/cert and server key/CSR/cert into the script directory.

Control flow is strict Bash with `set -euo pipefail`. It resolves its own path, derives output filenames, sets 3650-day validity and 2048-bit RSA keys, generates a CA private key and self-signed CA cert with critical CA constraints/key usages, prints it, generates a server key and CSR with CN `tikv-server`, CA false constraints, digital signature/key encipherment, server/client auth EKUs, SANs for `172.16.5.40` and `127.0.0.1`, signs it with the CA using copied extensions, then prints the server cert.

State and persistence are the generated `ca.key`, `ca.pem`, `key.pem`, `server.csr`, `server.pem`, and CA serial file created by OpenSSL. Dependencies are Bash, `realpath`, `dirname`, and OpenSSL with `-addext`/`-copy_extensions` support.

Risks include overwriting existing fixtures, OpenSSL version compatibility, long-lived static test keys, and SAN values becoming insufficient for new tests. Test signals are `security.rs` successfully loading these certs and grpcio channels accepting the generated credentials.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/data/generate_certs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/encryption.rs -->
## sources/storage-engines/tikv/components/test_util/src/encryption.rs

Purpose: builds file-based encryption fixtures for tests. It creates deterministic master key files and `EncryptionConfig`/`DataKeyManager` instances backed by `encryption_export`.

Important APIs are `create_test_key_file`, `new_test_file_master_key`, `new_file_security_config`, and `new_test_key_manager`. The key file contains a fixed hex key. `new_file_security_config` selects AES-256-CTR, seven-day data key rotation, dictionary logging, a high rewrite threshold, and the same file master key as current and previous. `new_test_key_manager` creates current and previous backends and configures low dictionary rewrite threshold for tests.

Control flow writes files into a temp path, constructs master key configs, then calls `DataKeyManager::new` with backend factories and rotation/dictionary arguments. State and persistence are the test key file and data key dictionary under the temp directory.

Dependencies include `encryption_export`, `kvproto::encryptionpb::EncryptionMethod`, `ReadableDuration`, `tempfile`, and standard file IO. Risks include fixed key material, unwraps on file writes and path conversion, and test behavior differing from production key management. Test signals are successful key-manager creation and downstream encrypted Rocks/storage tests reading dictionary files.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/kv_generator.rs -->
## sources/storage-engines/tikv/components/test_util/src/kv_generator.rs

Purpose: provides `KvGenerator`, a fast iterator that yields random fixed-length key/value byte pairs for tests and benchmarks.

Important APIs are `KvGenerator::new`, `KvGenerator::with_seed`, `KvGenerator::generate`, and the `Iterator` implementation. `new` seeds an `IsaacRng` from entropy; `with_seed` provides deterministic output; `generate` consumes the generator and collects `n` pairs.

Control flow for `next` allocates key and value vectors of configured lengths, fills them with random bytes, and returns `Some((k, v))` indefinitely. State is the RNG plus configured lengths; there is no persistence.

Dependencies are `rand` traits and `rand_isaac::IsaacRng`. Risks include per-iteration allocation cost, unlimited iterator behavior if used without bounds, and randomness causing non-reproducibility unless `with_seed` is used. Test signals include the included benchmark and downstream tests that need quick arbitrary KV material.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/kv_generator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/lib.rs -->
## sources/storage-engines/tikv/components/test_util/src/lib.rs

Purpose: crate root and shared test setup utilities. It enables unstable `test`, exports encryption, KV generation, logging, runner, and security helpers, and defines CI setup, port allocation, temp directory selection, debug assertion formatting, and eventual polling.

Important APIs are `setup_for_ci`, `alloc_port`, `temp_dir`, `assert_eq_debug`, and `eventually`. `setup_for_ci` preloads backtraces, sets grpc polling strategy in CI, initializes logging when requested, installs panic abort hooks, checks environment variables, and enforces open file descriptor minimums. `alloc_port` uses an atomic randomized start below the Linux local port range. `temp_dir` optionally uses `TIKV_TEST_MEMORY_DISK_MOUNT_POINT`.

State is process-global: environment variables, atomic port cursor, logger/panic hooks, and temp directories returned to callers. Persistence is limited to temp dirs and optional log files initialized by logging module.

Dependencies include `backtrace`, `rand`, `tikv_util`, `tempfile`, module reexports, and standard env/thread/time. Risks include global env mutation, port allocation races with external processes, panic on low FD limits, and memory-disk path assumptions. Test signals are downstream test harness setup, helpful diff panics, and `eventually` timeout panics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/logging.rs -->
## sources/storage-engines/tikv/components/test_util/src/logging.rs

Purpose: custom synchronous slog logger for tests. It prefixes log lines with the test case tag, timestamp, file, line, level, message, and key-value pairs, writing either to `LOG_FILE` or stderr.

Important types are `Serializer`, `CaseTraceLogger`, and a local `Never` error type. `CaseTraceLogger::write_log` skips configured tags, derives the thread test tag via `tikv_util`, formats local time through `chrono`, serializes record and inherited KV pairs, writes a newline, and flushes. `init_log_for_test` is guarded by `Once`, reads `LOG_FILE`, `LOG_LEVEL`, and `LOG_APPEND`, disables noisy RocksDB/raftdb log tags and tokio targets, then initializes TiKV logging without async drain.

State and persistence are the optional log file mutex, global logger initialization, and environment-controlled append/truncate behavior. Dependencies are `slog`, `chrono`, `slog-global` through the crate root, `tikv_util::logger`, and standard IO.

Risks include synchronous flushing overhead, global one-time logger configuration, skipped tags hiding useful details, and reliance on thread names for case tags. Test signals are log output shape, absence of async logger tag loss, and downstream CI logs when `LOG_FILE` is set.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/logging.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/macros.rs -->
## sources/storage-engines/tikv/components/test_util/src/macros.rs

Purpose: exports a small retry macro for tests.

`retry!($expr)` evaluates an expression returning a `Result`-like value and retries when `is_ok()` is false. Defaults are 10 retries and 100 ms interval; overloads allow count and interval. The macro sleeps with `std::thread::sleep(Duration::from_millis(interval))`, reevaluates the expression, and stops early on success, returning the final result.

Control flow is caller-expanded and synchronous. State is only the local `res` binding created in the expansion. There is no persistence and no logging. Dependencies are standard thread sleep and an in-scope `Duration` type, because the macro refers to `Duration::from_millis` without a fully qualified path.

Risks include requiring `Duration` in caller scope, repeated side effects in `$expr`, fixed sleep granularity, and hiding transient failures without recording attempts. Test signals are downstream uses where flaky async operations are expected to converge.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/runner.rs -->
## sources/storage-engines/tikv/components/test_util/src/runner.rs

Purpose: bridges Rust's unstable custom test framework APIs with TiKV test setup and optional failpoint lifecycle management.

Important APIs are `run_tests`, `TestHook`, `run_test_with_hook`, `clear_failpoints`, and `run_failpoint_tests`. `run_test_with_hook` calls `setup_for_ci`, wraps each static test or bench in a dynamic function that creates a `CaseLifeWatcher`, invokes hook setup before the case, and relies on `Drop` for teardown and end logging. It then calls `test_main`. `FailpointHook` manages a thread-local `fail::FailScenario` for each case.

State is thread-local failpoint scenario storage plus per-case watcher names/hooks. Persistence is none, but failpoints affect global test behavior while active. Dependencies are the nightly `test` crate exposed by the crate root, `fail`, environment args, and logging macros.

Risks include nightly API instability, failpoint cleanup during panics requiring explicit `clear_failpoints`, unsupported dynamic test function variants causing panic, and hook clone/send requirements. Test signals are failpoint tests not leaking failpoints across cases and logs showing case start/end around each wrapped test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/security.rs -->
## sources/storage-engines/tikv/components/test_util/src/security.rs

Purpose: loads static TLS fixture files and builds TiKV `SecurityConfig` and grpcio channel credentials for tests.

Important APIs are `new_security_cfg`, `new_channel_cred`, and private `load_certs`. `new_security_cfg` points CA, cert, and key paths at `data/ca.pem`, `data/server.pem`, and `data/key.pem` under `CARGO_MANIFEST_DIR`, sets optional allowed CNs, default encryption config, empty override target, and redaction on. `new_channel_cred` loads cert strings and builds `ChannelCredentials` with root cert and client cert/key.

Control flow is straightforward file path construction and file reads. State/persistence are the checked-in/generated cert files under `data`; returned configs are immutable values consumed by test servers/clients.

Dependencies include `security::SecurityConfig`, `grpcio::ChannelCredentialsBuilder`, `encryption_export::EncryptionConfig`, `collections::HashSet`, and `log_wrappers` redaction options. Risks include panics if cert files are missing, static cert expiration or SAN mismatch, and tests unintentionally depending on redaction behavior. Test signals are successful secure channel creation and security tests honoring allowed CN sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_util/src/security.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/Cargo.toml -->
## sources/storage-engines/tikv/components/tidb_query_aggr/Cargo.toml

Purpose: manifest for `tidb_query_aggr`, the vector aggregate-function crate for TiDB pushed-down query execution inside TiKV.

Dependencies include `tidb_query_codegen` for `AggrFunction` derive machinery, `tidb_query_common` results/errors, `tidb_query_datatype` for vector values and field types, `tidb_query_expr` for RPN expression evaluation, `tipb` protobuf expressions, `tikv_util`, and `match-template`. Dev dependencies are `panic_hook` and `tipb_helper` for tests.

Control flow is Cargo-level; the source modules parse aggregate expression definitions, rewrite child expressions as needed, maintain aggregate states, and push vectorized partial results. State/persistence are in in-memory aggregate state structs only.

Risks include tight coupling to TiDB protobuf field-type contracts and codegen macro APIs. Test signals are per-aggregate unit/integration tests that build `tipb` expressions, parse them into aggregate functions, evaluate RPN over lazy columns, and assert vector outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_avg.rs -->
## sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_avg.rs

Purpose: implements vectorized AVG aggregate parsing and state for Decimal, Real, Enum, and Set inputs. AVG returns two partial result columns, `(count, sum)`, which TiDB can finalize into an average.

Important APIs are `AggrFnDefinitionParserAvg`, generic `AggrFnAvg<T>`, `AggrFnStateAvg<T>`, and special enum/set aggregate/state pairs. The parser verifies `ExprType::Avg`, requires one child, rewrites the child expression for SUM/AVG typing, checks the rewritten return type matches the encoded sum field type, appends unsigned `LongLong` count plus sum field type to output schema, and returns the correct aggregate implementation.

Control flow in state updates ignores NULLs, adds non-null values to `sum` through `Summable::add_assign`, and increments `count`. Enum and Set convert their numeric value to `Decimal`. `push_result` writes count and either NULL sum for empty input or the accumulated sum. State is only `sum` and `count`; no persistence.

Dependencies include aggregate codegen macros, datatype vector abstractions, EvalContext, RPN expressions, `tipb`, and utility expression rewriting. Risks include type mismatch between TiDB field metadata and rewritten expression, decimal overflow/error propagation through `EvalContext`, and count stored as `usize` then cast to TiDB `Int`. Test signals cover scalar/vector updates, NULL handling, enum/set conversion, integration parsing/evaluation, and illegal request rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_avg.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_bit_op.rs -->
## sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_bit_op.rs

Purpose: implements BIT_AND, BIT_OR, and BIT_XOR aggregate functions through a shared `BitOp` trait and generic aggregate state.

Important APIs are `BitOp`, macro-generated marker types `BitAnd`, `BitOr`, `BitXor`, `AggrFnDefinitionParserBitOp<T>`, `AggrFnBitOp<T>`, and `AggrFnStateBitOp<T>`. Each operation declares its `ExprType`, initial state, and in-place u64 operation. The parser verifies expression type, checks one child, emits the root field type as the output schema, rewrites the child expression for bit operations, and returns the generic aggregate.

Control flow updates ignore NULLs and apply the operation to `self.c` using the input `Int` cast to `u64`; result is pushed back as TiDB `Int`. BIT_AND starts at all ones, OR and XOR at zero, matching SQL aggregate behavior for empty/all-null inputs. State is a single `u64`; no persistence.

Dependencies include aggregate codegen, datatype vectors, RPN expression rewriting, EvalContext, and `tipb`. Risks include signed/unsigned casting semantics for negative values, schema/root field type trust, and ensuring expression rewriting converts supported child types into integer-compatible values. Test signals cover initial/NULL behavior, repeated and vector updates, negative value wraparound, and integration parsing/evaluation for all three bit operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_bit_op.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_count.rs -->
## sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_count.rs

Purpose: implements vectorized COUNT aggregate parsing and state. COUNT outputs one unsigned `LongLong` partial result representing the number of non-null evaluated child values.

Important APIs are `AggrFnDefinitionParserCount`, `AggrFnCount`, and `AggrFnStateCount`. The parser verifies `ExprType::Count`, requires one child, appends an unsigned `LongLong` output field, stores the child RPN expression, and returns `AggrFnCount`.

Control flow is optimized manually rather than using only concrete state macros. `update` increments for a non-null scalar value. `update_repeat` adds `repeat_times` for repeated non-null constants such as `COUNT(1)`. `update_vector` iterates logical row indexes and counts non-null physical values. `push_result` writes the count as `Int`. State is a `usize` counter; no persistence.

Dependencies include aggregate codegen, datatype vector traits, EvalContext, RPN expressions, and `tipb` field metadata. Risks include `usize` to `Int` casting on extremely large groups, correctness depending on logical row indexes matching evaluated chunks, and parser acceptance of only one-child COUNT forms. Test signals cover null vs non-null scalar updates, repeated updates, vector updates over selected rows, and enum/set references.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_count.rs -->
