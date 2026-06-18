# Research Report: subset-b-008238

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/special_chars_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/special_chars_test.rs

Purpose: end-to-end S3 compatibility coverage for object keys containing spaces, plus signs, percent signs, equals signs, Unicode, punctuation, and control characters. The file is entirely test code under `#[cfg(test)]`, using `RustFSTestEnvironment` to start a real RustFS server and `aws_sdk_s3::Client` for normal API calls.

Important APIs and flow: `create_s3_client`, `create_bucket`, and `signed_get` are local helpers. `signed_get` builds a raw `http::Request`, signs it with `rustfs_signer::sign_v4`, copies signed headers into `reqwest`, and validates canonical path/signature behavior for keys ending in `=`. Test cases then exercise `put_object`, `get_object`, `head_object`, `copy_object`, `delete_object`, and `list_objects_v2` with prefixes and delimiters.

State and persistence: each serial async test creates its own server process and bucket, writes objects into the test backend, verifies exact bytes/listing behavior, then calls `env.stop_server()`. No durable state should escape the test environment.

Dependencies and integration points: depends on the common e2e harness, AWS SDK S3 primitives, the local HTTP client, S3S `Body`, SigV4 signer, and `serial_test` to avoid cross-test server/bucket interference.

Risks: bucket names are mostly fixed, so failed cleanup or parallel external runs could collide despite `serial`. Some tests use `assert!(result.is_err())` rather than checking S3 error codes. Control-character coverage deliberately does not require tab rejection.

Test signals: strong regression signal for URL decoding/canonicalization, list-prefix delimiter behavior, raw signed requests, and common object operations over unusual key names.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/special_chars_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/stale_multipart_cleanup_cluster_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/stale_multipart_cleanup_cluster_test.rs

Purpose: cluster e2e regression test proving stale incomplete multipart uploads are removed across all RustFS nodes.

Important APIs and functions: `list_parts_reports_missing_upload` and `complete_reports_missing_upload` both probe an upload ID and normalize `NoSuchUpload` service errors to `true`. `wait_for_cleanup_on_all_nodes` loops for up to 30 seconds, requiring every client to report missing upload for both list-parts and complete-multipart.

Control flow: the test starts a four-node `RustFSTestClusterEnvironment`, sets `RUSTFS_API_STALE_UPLOADS_EXPIRY=5s` and `RUSTFS_API_STALE_UPLOADS_CLEANUP_INTERVAL=1s`, creates a bucket, starts a multipart upload through node 0, uploads part 1 through node 1, verifies visibility through node 2, then waits until every node observes cleanup.

State and persistence: the multipart upload metadata and part data are intentionally left incomplete so background cleanup can remove them. The test observes distributed metadata convergence, not just local disk deletion.

Dependencies and integration points: uses AWS SDK multipart APIs, cluster harness clients, `tokio::time::sleep`, `uuid` for unique object keys, and `serial_test`.

Risks: timing based on real background intervals can be flaky under slow CI. The helper treats only exact `NoSuchUpload` as success; any alternate S3-compatible error mapping fails the test.

Test signals: confirms stale upload expiration configuration, background cleanup scheduling, and cluster-wide propagation for incomplete multipart state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/stale_multipart_cleanup_cluster_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/tls_gen.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/tls_gen.rs

Purpose: CLI/library helper for generating a local RustFS TLS and mTLS certificate bundle for e2e tests.

Important APIs and types: `Args` is a `clap::Parser` with `--out-dir`, `--days`, and `--force`. `run` validates positive validity days and delegates to `write_bundle`. `OUTPUT_FILES` defines the seven generated artifacts: server cert/key, CA/public/client CA, and client cert/key. `ensure_writable` prevents overwriting existing bundle files unless `force` is set.

Control flow: `write_bundle` creates the output directory, checks overwrite rules, creates a CA key/certificate, builds a localhost server leaf with DNS and loopback IP SANs, builds a client-auth leaf, and writes all PEM files. `base_params` centralizes subject, validity window, and a five-minute clock-skew allowance.

State and persistence: writes PEM material to the configured directory, defaulting to `target/tls`. It does not persist metadata beyond files and does not clean old bundles.

Dependencies and integration points: uses `rcgen` for CA/leaf certificate generation, `time` for validity, `anyhow` for context-rich errors, and `clap` for CLI parsing.

Risks: generated private keys are unencrypted test assets. `--force` overwrites all bundle files. Validity depends on local system time.

Test signals: unit tests verify full bundle creation, overwrite refusal, and rejection of non-positive `--days`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/tls_gen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/version_id_regression_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/version_id_regression_test.rs

Purpose: e2e regression coverage for issue #1066, where S3 responses used by Veeam could return missing or empty `version_id` when bucket versioning was enabled.

Important APIs and functions: helpers create clients/buckets and toggle versioning through `put_bucket_versioning` with `Enabled` or `Suspended`. Tests cover `put_object`, `copy_object`, `create_multipart_upload`/`upload_part`/`complete_multipart_upload`, `head`, `list`, and `delete`.

Control flow: enabled-versioning tests assert `version_id.is_some()` and non-empty for put, copy, complete-multipart, and simulated Veeam paths. Suspended-versioning tests assert `version_id == None` for the same write classes. Non-versioned and basic-operation tests guard against broad S3 regressions. A Terraform-style put/delete/put scenario verifies a state object is readable after a delete marker workflow.

State and persistence: each serial test starts a fresh RustFS server, creates a bucket, mutates bucket versioning config, writes object versions/delete markers, and relies on the environment for cleanup.

Dependencies and integration points: uses AWS SDK S3 versioning types, multipart completion types, ByteStream, and `RustFSTestEnvironment`.

Risks: most bucket names are fixed; failed tests can leave colliding state if the harness does not isolate storage. Assertions inspect SDK output fields rather than raw headers, so serialization bugs below the SDK boundary could be missed.

Test signals: strong coverage for versioning response semantics expected by Veeam, suspended behavior, multipart completion, and delete-marker recovery.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/version_id_regression_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/Cargo.toml -->
## sources/object-store/rustfs/crates/ecstore/Cargo.toml

Purpose: Cargo manifest for the `rustfs-ecstore` crate, the erasure-coding storage backend for RustFS.

Important configuration: package metadata is inherited from the workspace, with documentation and keywords describing erasure coding storage. The crate disables doctests for the library. Feature `rio-v2` optionally enables `rustfs-rio-v2`; default features are empty. Linux targets add Tokio `io-uring`.

Dependencies: the manifest pulls in the RustFS storage stack (`rustfs-filemeta`, `rustfs-storage-api`, `rustfs-config`, `rustfs-common`, `rustfs-madmin`, replication/S3/KMS/policy crates), async/networking (`tokio`, `tonic`, `hyper`, `reqwest`, AWS SDK), encoding/checksum (`reed-solomon-erasure`, `reed-solomon-simd`, hashes, base64), observability (`tracing`, OpenTelemetry, metrics), persistence helpers, and cloud clients. Build dependency `shadow-rs` supplies build metadata used by admin server info.

Integration points: declares four Criterion benchmarks: erasure, comparison, rename data/meta, and single-block non-inline. Dev dependencies include Criterion, Tokio test utilities, tracing subscriber, and serial tests.

State and persistence behavior: not runtime code, but it controls compiled feature surfaces and benchmark availability.

Risks: broad dependency surface makes feature resolution and workspace version compatibility important. Optional `rio-v2` and target-specific `io-uring` can create platform-specific behavior.

Test signals: benchmark declarations and dev dependencies show performance-sensitive erasure code and metadata paths are expected to be measured outside normal tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/comparison_benchmark.rs -->
## sources/object-store/rustfs/crates/ecstore/benches/comparison_benchmark.rs

Purpose: Criterion performance analysis for the SIMD-backed `rustfs_ecstore::erasure_coding::Erasure` implementation across sizes, shard layouts, recovery cases, concurrency, and instance reuse.

Important APIs and functions: `TestData` builds deterministic byte vectors. `generate_test_datasets` spans 1 KiB to 4 MiB. Benchmark functions cover encode, decode, shard-size sensitivity, concurrent encode from four threads, error recovery under different loss counts, and memory/instance reuse.

Control flow: each benchmark constructs `Erasure::new(data_shards, parity_shards, len)`, pre-validates whether `encode_data` supports the configuration, and then uses Criterion groups with explicit sample sizes and measurement durations. Decode and recovery benchmarks convert encoded shards into `Vec<Option<Vec<u8>>>`, drop selected shards, and call `decode_data`.

State and persistence: no persistent state; Criterion writes result artifacts under `target/criterion` when executed.

Dependencies and integration points: depends on Criterion, standard `black_box`, threads for concurrency, and the ecstore erasure module.

Risks: many iterations allocate cloned shard vectors, so results include allocation cost, not pure Reed-Solomon math. Skipped unsupported configurations print warnings instead of failing, which is useful for portability but can hide lost coverage.

Test signals: useful baseline for SIMD erasure throughput, decode recovery cost, shard-size thresholds, and reuse-vs-new instance overhead.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/comparison_benchmark.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/erasure_benchmark.rs -->
## sources/object-store/rustfs/crates/ecstore/benches/erasure_benchmark.rs

Purpose: Criterion benchmark suite comparing ecstore erasure encode/decode performance and selected direct `reed_solomon_erasure` paths.

Important APIs and types: `BenchConfig` captures data shard count, parity shard count, data size, block size, and a display name. `generate_test_data` creates deterministic payloads. Benchmarks call `Erasure::encode_data`, `Erasure::decode_data`, and `calc_shard_size`.

Control flow: encode benchmarks run SIMD ecstore implementation for configurations from 1 KiB through 16 MiB, then optionally benchmark direct `reed_solomon_erasure::galois_8::ReedSolomon` when shard size is at least 512 bytes. Decode benchmarks pre-encode, remove one data and one parity shard, then reconstruct. Additional groups measure shard-size impact, coding-configuration impact, and reuse of an `Erasure` instance.

State and persistence: no application state. Criterion persists benchmark measurements and reports externally under target output.

Dependencies and integration points: benchmarks the public erasure-coding module and optionally direct Reed-Solomon library behavior for comparison.

Risks: direct comparison paths do not include all wrapper behavior and may not be apples-to-apples. Some benchmark names mention SIMD even when overhead includes buffer allocation and wrapper setup.

Test signals: performance regression detector for data-size scaling, shard-count scaling, decode reconstruction, and memory pattern costs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/erasure_benchmark.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/rename_data_meta_benchmark.rs -->
## sources/object-store/rustfs/crates/ecstore/benches/rename_data_meta_benchmark.rs

Purpose: Criterion benchmark for file metadata read-modify-write behavior during data/meta rename or version replacement paths.

Important APIs and functions: `make_file_info` creates a `rustfs_filemeta::FileInfo` with version ID, data directory, size, mod time, metadata, and erasure layout. `build_meta_with_versions` seeds a `FileMeta` with 1, 8, 32, or 64 versions. The benchmark exercises `FileMeta::load`, `find_unshared_data_dir_for_version`, `data.remove_two`, `add_version`, and `marshal_msg`.

Control flow: for each version count, it serializes seeded metadata, picks the first version ID for replacement, and compares three paths: full read-modify-write, prepared add-version plus marshal, and remove-only after load.

State and persistence: no disk state; serialized metadata buffers model on-disk xlmeta-like state in memory.

Dependencies and integration points: directly targets `rustfs-filemeta`, UUID version/data-dir identifiers, erasure metadata layout, and time-based version ordering.

Risks: deterministic structure may not capture all production metadata complexity. Benchmark includes UUID generation for replacement versions in some paths, which may affect timing.

Test signals: performance insight for versioned metadata mutation hot paths, especially as version count grows.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/rename_data_meta_benchmark.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/single_block_non_inline_benchmark.rs -->
## sources/object-store/rustfs/crates/ecstore/benches/single_block_non_inline_benchmark.rs

Purpose: Criterion benchmark comparing the general erasure encode pipeline with a `encode_single_block_non_inline` fast-path candidate for small payloads that still use non-inline writers.

Important APIs and types: `BenchConfig` describes payload size, data/parity shard counts, and block size. `build_non_inline_writers` creates `BitrotWriterWrapper` instances around `tokio::io::sink()` using `CustomWriter::new_tokio_writer` and `HashAlgorithm::HighwayHash256S`. Benchmarks call `Erasure::encode` and `Erasure::encode_single_block_non_inline`.

Control flow: a current-thread Tokio runtime is embedded in the benchmark. For each 4 KiB, 64 KiB, and 128 KiB payload, it creates fresh non-inline writers and a `BufReader<Cursor<Vec<u8>>>`, then blocks on the async encode method.

State and persistence: no durable writes because all shard output goes to `tokio::io::sink`; bitrot wrapping and shard sizing are still exercised.

Dependencies and integration points: integrates erasure coding, bitrot writer wrappers, Tokio async IO, Criterion, and RustFS hash algorithms.

Risks: sink writers exclude real disk latency and filesystem allocation behavior. Cloning payloads and writer construction are part of measured work.

Test signals: focused performance signal for deciding whether the single-block non-inline path improves small-object write throughput.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/benches/single_block_non_inline_benchmark.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/build.rs -->
## sources/object-store/rustfs/crates/ecstore/build.rs

Purpose: build script that runs `shadow_rs::ShadowBuilder` for the ecstore crate.

Important API: `main` returns `shadow_rs::SdResult<()>`, invokes `ShadowBuilder::builder().build()?`, then returns `Ok(())`.

Control flow: Cargo executes this before compiling the crate. `shadow-rs` emits generated build metadata such as package version, commit hash, tag, and commit date into the build output.

State and persistence: writes generated build metadata into Cargo's build output directory. It does not write repository files directly.

Dependencies and integration points: paired with the build dependency in `Cargo.toml`. Runtime code in `admin_server_info.rs` imports `shadow!(build)` and formats version/commit data through `get_commit_id`.

Risks: builds may fail or lose metadata if the source tree lacks expected VCS information, depending on `shadow-rs` behavior. Reproducibility depends on how commit/date metadata is captured.

Test signals: no direct tests here; indirect signal is any code depending on `get_commit_id` and build metadata compilation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/run_benchmarks.sh -->
## sources/object-store/rustfs/crates/ecstore/run_benchmarks.sh

Purpose: Bash helper for running ecstore Reed-Solomon SIMD benchmark modes and producing Criterion reports.

Important functions: colorized logging helpers, `check_requirements`, `cleanup`, mode runners for `simd`, `full`, `performance`, `large`, `quick`, `generate_comparison_report`, `show_help`, `show_test_info`, and `main`.

Control flow: `main` checks Cargo availability, prints Rust/Cargo/CPU/SIMD environment details, dispatches on the first argument, optionally removes `target/criterion`, runs `cargo bench` with selected bench names and filters, then reports where HTML output lives.

State and persistence: deletes previous Criterion results with `rm -rf target/criterion` for most full modes, then `cargo bench` recreates benchmark artifacts under `target/criterion`.

Dependencies and integration points: assumes Bash, Cargo, Rust toolchain, optional `/proc/cpuinfo` on Linux, optional Python 3 for serving generated reports. It calls `comparison_benchmark` and `erasure_benchmark` declared in `Cargo.toml`.

Risks: `set -e` stops on first failing command. The `cargo --list | grep bench` check is a weak proxy for Criterion support. `--quick` is passed through to Criterion filters/options and should be verified against the installed Criterion version.

Test signals: operational benchmark runner rather than correctness test; useful for repeatable local performance baselines.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/run_benchmarks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/admin_server_info.rs -->
## sources/object-store/rustfs/crates/ecstore/src/admin_server_info.rs

Purpose: builds admin/server information responses for local and cluster RustFS nodes, including network status, storage disks, data usage, backend erasure layout, pool/set statistics, and deployment/build metadata.

Important APIs and functions: `is_server_resolvable` pings a remote node service with a signed Tonic client and flatbuffer `PingBody` under a one-second timeout. `get_local_server_property` builds `ServerProperties` from global endpoints, boot time, object store state, network reachability, and local storage info. `get_server_info` merges notification-system remote server info with local properties and usage/backend summaries. Helpers compute online/offline disk stats, pool info, and commit ID.

State and persistence: reads global singletons (`GLOBAL_Endpoints`, `GLOBAL_BOOT_TIME`, object store handle, notification sys, deployment ID), loads data usage cache/backend data, and inspects storage admin state. It does not mutate persistent state.

Dependencies and integration points: integrates `rustfs_madmin` response models, `StorageAdminApi`, data usage cache, node RPC/Tonic signing, flatbuffers, shadow build metadata, and heal drive states.

Risks: server info can block on remote ping and backend usage calls; warnings indicate timing diagnostics. Disk online/offline classification treats root disks specially and can underflow if counts become inconsistent. Pool indexing assumes disk-reported indexes align with `store.pools`.

Test signals: unit test verifies `get_server_info(false)` includes global deployment ID. Broader behavior relies on integration/admin API tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/admin_server_info.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/batch_processor.rs -->
## sources/object-store/rustfs/crates/ecstore/src/batch_processor.rs

Purpose: provides reusable async batch execution utilities with concurrency caps and quorum-style early return.

Important APIs and types: `AsyncBatchProcessor` stores `max_concurrent`. `execute_batch` accepts a vector of futures returning disk `Result<T>`, runs them under a Tokio semaphore in a `JoinSet`, and returns results in original task order. `execute_batch_with_quorum` returns once `required_successes` have completed successfully or once quorum becomes impossible. `GlobalBatchProcessors` exposes read, write, and metadata processors with fixed concurrency levels 16, 8, and 12. `get_global_processors` initializes a `OnceLock`.

Control flow: all tasks are spawned immediately, but semaphore permits limit active work. Join results are collected as tasks finish; panics and semaphore errors are logged and converted to failures where possible.

State and persistence: only process-local singleton state; no durable persistence.

Dependencies and integration points: uses `crate::disk::error::{Error, Result}`, Tokio `JoinSet` and `Semaphore`, and is intended for disk/storage fan-out paths.

Risks: `execute_batch_with_quorum` returns without explicitly aborting slow spawned tasks; dropping `JoinSet` aborts remaining tasks, so callers must tolerate cancellation. `max_concurrent == 0` would deadlock tasks waiting for permits.

Test signals: unit tests cover ordered success, mixed errors, quorum success, early return before slow tail, and early failure once quorum is impossible.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/batch_processor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bitrot.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bitrot.rs

Purpose: factory helpers for bitrot-verifying readers and bitrot-writing wrappers over inline data or disk-backed shard files.

Important APIs: `create_bitrot_reader` accepts optional inline bytes or disk, bucket/path, logical offset/length, shard size, checksum algorithm, verification flag, and zero-copy preference. It adjusts offset/length to include per-shard checksum overhead, then returns a `BitrotReader<Box<dyn AsyncRead...>>`. `create_bitrot_writer` chooses an inline buffer or disk-created file, adjusts expected length for checksum overhead, and returns `BitrotWriterWrapper`.

Control flow: reader creation prioritizes inline data. Disk reads use zero-copy when requested and local; success records zero-copy metrics, failure records fallback metrics and tries stream read, returning the original zero-copy error if fallback also fails.

State and persistence: inline mode stores data in memory; disk mode creates/reads shard files through `DiskStore`. Metrics are recorded through `rustfs_io_metrics`.

Dependencies and integration points: depends on disk APIs, erasure-coding bitrot wrappers, `Bytes`, `Cursor`, Tokio `AsyncRead`, and `rustfs_utils::HashAlgorithm`.

Risks: offset/length math must stay consistent with bitrot writer layout. Returning the original zero-copy error after fallback failure can hide the fallback error. Callers must pass valid shard sizes.

Test signals: async unit tests cover inline readers, zero-copy flag with inline data, inline offset correctness, missing data/disk behavior, inline writer data, and disk writer without disk error.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bitrot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/mod.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/mod.rs

Purpose: module declaration file for bucket bandwidth monitoring and throttled reader support.

Important API surface: exports two submodules, `monitor` and `reader`. `monitor` owns throttles, moving average measurements, and reports. `reader` owns `BucketOptions`, `MonitorReaderOptions`, and `MonitoredReader`.

Control flow and state: this file has no runtime control flow or state itself; it defines the namespace boundary used by bucket target replication and read throttling code.

Dependencies and integration points: allows callers to import `crate::bucket::bandwidth::monitor::Monitor` and `crate::bucket::bandwidth::reader::BucketOptions` through a stable module path.

Risks: minimal. Any public API changes in child modules affect users through this module path.

Test signals: no direct tests; child modules contain the functional tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/monitor.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/monitor.rs

Purpose: process-local bandwidth throttle and measurement subsystem keyed by bucket plus replication ARN.

Important APIs and types: `BucketThrottle` wraps a `ratelimit::Ratelimiter` and exposes `burst` and bulk-ish `consume`. `BucketMeasurement` tracks bytes in the current window and an exponential moving average. `BandwidthDetails` and `BucketBandwidthReport` are serializable reporting models. `Monitor` owns throttle and measurement maps plus cluster node count.

Control flow: `Monitor::new` clamps node count to at least one and spawns a two-second moving-average updater when inside a Tokio runtime. `set_bandwidth_limit` divides cluster limit by node count, creates a per-node throttle, and stores it. `update_measurement` fast-paths under read lock and inserts under write lock on miss. Delete methods remove all bucket throttles or one ARN.

State and persistence: all state is in memory behind standard locks and atomics; no persisted configuration. Reports multiply per-node limits back by node count.

Dependencies and integration points: used by bucket target replication throttling through `get_global_bucket_monitor`; depends on `ratelimit`, serde, tracing, and `BucketOptions`.

Risks: custom token consumption manipulates limiter availability because the crate lacks bulk consume. Very small limits clamp to one byte/sec per node. Moving-average retention uses a single start time, so `LastMinute` style precision is not present here.

Test signals: extensive unit tests cover limit splitting, deletion, invalid limits, token deficits, concurrency, poison recovery, report filtering, and current bandwidth updates.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/monitor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/reader.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/reader.rs

Purpose: `AsyncRead` wrapper that enforces bucket/replication bandwidth limits and updates bandwidth measurements as bytes are read.

Important APIs and types: `BucketOptions` is the hashable key (`name`, `replication_arn`). `MonitorReaderOptions` carries bucket options and `header_size`, allowing header bytes to consume tokens before body IO. `MonitoredReader<R>` wraps an inner reader, monitor, wait state, and reusable temporary buffer.

Control flow: `poll_read` first honors any pending sleep. If no throttle exists, it delegates directly. With a throttle, it computes allowed body bytes and token consumption via `calc_need_and_tokens`, consumes tokens, sleeps for deficit/rate when needed, then calls `poll_limited_read` so the inner reader cannot fill more than the permitted byte count. Successful body reads update the monitor measurement.

State and persistence: all state is in-memory reader-local plus monitor maps. No persistence.

Dependencies and integration points: integrates Tokio `AsyncRead`, `ReadBuf`, `Sleep`, the bandwidth `Monitor`, and replication target reads that need throttling.

Risks: `poll_read` can return ready with zero bytes for header-only token consumption, which callers must tolerate. Mutex poisoning is recovered. Ratelimit behavior depends on `Monitor::throttle` returning up-to-date cloned throttle state.

Test signals: unit tests cover passthrough, limited reads, header-only accounting, full throttled reads, header depletion, and one-byte/sec limits.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bucket_target_sys.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bucket/bucket_target_sys.rs

Purpose: manages remote bucket targets for replication or related services, including target validation, cached AWS S3 clients, endpoint health metadata, bandwidth limit updates, and remote object operations with internal replication headers.

Important APIs and types: global `BucketTargetSys` stores ARN-to-client map, bucket target map, endpoint health, health-check HTTP client, and ARN error state behind async locks. `TargetClient` wraps an AWS S3 client and implements `bucket_exists`, `get_bucket_versioning`, `head_object`, `put_object`, multipart upload/part/complete, and `remove_object`. Option structs model remove, put, advanced replication, and part headers. `BucketTargetError` and `S3ClientError` normalize errors.

Control flow: target setup validates type, credentials placeholder, bucket existence, and versioning requirements for replication. `update_all_targets` removes old targets, clears bandwidth throttles, builds new clients, installs ARN mappings, and applies bandwidth limits. `get_remote_target_client` reloads target config when cached client is missing and refresh cooldown allows. Header builders inject source version, etag, mtime, delete marker, governance, and replication flags through AWS SDK `customize().map_request`.

State and persistence: runtime maps are in memory. Durable source is bucket metadata/config loaded through metadata systems. TLS trust can be loaded from configured certificate files. Bandwidth state is delegated to the global bucket monitor.

Dependencies and integration points: AWS SDK S3, smithy HTTP/TLS, RustFS bucket metadata, replication config, versioning system, target ARN types, global monitor, rustfs HTTP header constants, and rustls cert config.

Risks: `check_endpoint_health` currently always returns true, so health status is optimistic. `validate_target_credentials` is a stub. Custom header insertion unwraps header pairs and string conversion in several paths. `LastMinuteLatency::add` retention uses a fixed start time rather than per-sample timestamps. A put header condition appears inverted for `source_etag` insertion. Target maps can diverge from persisted metadata until refreshed.

Test signals: unit tests verify remove-object internal version headers and delete-marker purge header behavior. Most target validation/client behavior needs integration tests with real S3-compatible remotes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/bucket_target_sys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/error.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bucket/error.rs

Purpose: bucket metadata error enum for missing bucket-level configuration documents and IO/other failure normalization.

Important APIs and types: `BucketMetadataError` variants represent missing tagging, policy, object lock, lifecycle, SSE, quota, replication, and remote target configs, plus `Io(std::io::Error)`. `other` wraps arbitrary errors into `std::io::Error::other`. `to_u32` and `from_u32` provide numeric mapping for serialization or cross-boundary error codes.

Control flow: `From<crate::error::Error>` maps underlying IO directly and wraps all other crate errors. `From<std::io::Error>` attempts to downcast back to `BucketMetadataError`, otherwise wraps as `Io`. `PartialEq` compares IO by kind/message and non-IO by numeric code.

State and persistence: no state. Numeric codes are persistent contract material if stored or sent over RPC.

Dependencies and integration points: depends on crate-level `Error`, `thiserror`, and std IO error handling. Used by bucket metadata systems to distinguish absent optional configs from hard failures.

Risks: `from_u32(0x09)` reconstructs a generic IO error, losing original details. Numeric code stability matters for compatibility. Equality on IO message can be brittle.

Test signals: no direct tests in this file; coverage should come from metadata load/save and RPC/error-code tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_audit.rs -->
## sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_audit.rs

Purpose: small lifecycle audit model that attaches a lifecycle event source to a lifecycle event.

Important APIs and types: `LcEventSrc` enumerates origin categories: none, heal, scanner, decom, rebalance, and S3 operations such as head/get/list/put/copy/complete-multipart. `LcAuditEvent` contains a `lifecycle::Event` and source. `LcAuditEvent::new` constructs the pair.

Control flow: no complex logic; default source is `None`, and default event comes from `lifecycle::Event` default.

State and persistence: purely in-memory struct definitions. If audit events are serialized elsewhere, this file defines the source taxonomy.

Dependencies and integration points: depends on `crate::bucket::lifecycle::lifecycle` for the actual lifecycle event type. Intended integration points are lifecycle scanner, healing, decommission/rebalance, and S3 API paths that trigger lifecycle decisions.

Risks: enum variants are not explicitly serialized here; compatibility depends on downstream serde or formatting if added. Missing source variants can reduce audit specificity for future lifecycle triggers.

Test signals: no direct tests; correctness depends on call sites populating the correct `LcEventSrc`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_audit.rs -->
