# subset-b-008902 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/types.rs -->
# sources/storage-engines/tikv/components/txn_types/src/types.rs

## Purpose
Defines core transaction-facing data types for TiKV MVCC storage: encoded keys, values, mutations, old-value capture, transaction extra data, write-batch flags, last-change hints, and commit roles. The file is the shared vocabulary between RPC mutation inputs, MVCC storage internals, CDC old-value capture, and Raft request metadata.

## Important APIs, Types, and Functions
`Value`, `ValueEntry`, `KvPair`, and `KvPairEntry` wrap raw byte values with optional commit timestamps. `Key` owns the encoded key representation and exposes raw/encoded conversion, timestamp append/truncate/split/decode helpers, encoded/raw equality helpers, hash generation, formatting, cloning with timestamp reserve capacity, and heap sizing. `Mutation` maps `kvrpcpb::Mutation` into internal variants (`Put`, `Delete`, `Lock`, `SharedLock`, `Insert`, `CheckNotExists`) with assertion accessors and constructors. `OldValue`, `OldValues`, `insert_old_value_if_resolved`, `TxnExtra`, `TxnExtraScheduler`, `WriteBatchFlags`, `LastChange`, and `CommitRole` provide CDC, scheduler, Raft-header, and MVCC read-skip metadata.

## Control Flow
Raw RPC keys are encoded with TiKV byte codec in `Key::from_raw`; timestamped MVCC keys append descending `u64` timestamps so newer versions sort first. Decode helpers validate at least eight timestamp bytes before slicing or decoding. `Mutation::from(kvrpcpb::Mutation)` dispatches on protobuf operation, consuming values where needed and panicking for an unsupported op. Old values are inserted only when resolved, and `LastChange` serializes into two primitive parts where `(0,0)` is unknown, `(0,positive)` is not-exist, and `(positive,positive)` is an existing prior write.

## State and Persistence Behavior
The types are mostly value objects, but their binary representations are persistent storage contracts. `Key` encodes user keys for RocksDB key ordering, timestamp bytes encode MVCC versions, `WriteBatchFlags` bits are carried in Raft request headers, and `LastChange` is serialized into write records elsewhere. `TxnExtra` carries old values and 1PC/flashback flags across scheduling boundaries without owning durable state itself.

## Dependencies and Integration Points
Depends on `tikv_util::codec`, `kvproto::kvrpcpb::Assertion`, `bitflags`, `collections::HashMap`, `farmhash`, and memory sizing traits. It integrates with `timestamp::TimeStamp`, write-record serialization in `write.rs`, MVCC transactions, CDC old-value readers, pessimistic/shared-lock handling, Raft request headers, and log redaction wrappers.

## Risks
Many `Key` methods require the caller to know whether a key is timestamped; misuse can decode garbage or drop user-key bytes. `gen_hash` unwraps raw decoding, so invalid encoded keys panic. `from_bits_check` intentionally panics on unknown Raft flags, which is useful for invariant enforcement but brittle for mixed-version bit rollout. `Mutation::from` panics on unknown operations, and `OldValue::finalized` panics unless unresolved variants have already been materialized.

## Test Signals
The file includes unit tests for flag parsing/panic behavior, timestamp appending, encoded/raw equality, encoded-from checks, old-value resolution, and `LastChange` round trips. Additional useful tests are mixed-version flag compatibility, invalid key encodings, CDC old-value seek paths, and property tests for raw key encode/decode/timestamp ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/write.rs -->
# sources/storage-engines/tikv/components/txn_types/src/write.rs

## Purpose
Implements TiKV MVCC write-record metadata stored in the write column family. A write record identifies the logical write type, start timestamp, optional short value, protected rollback state, overlapped rollback markers, GC-fence timestamps, last-change hints, and transaction source.

## Important APIs, Types, and Functions
`WriteType` maps Put/Delete/Lock/Rollback to byte flags and can be derived from lock types. `Write` is the owned record with constructors `new` and `new_rollback`, builder-style setters for overlapped rollback, last change, and transaction source, `parse_type`, and `as_ref`. `WriteRef<'a>` is the borrowed serialization view with `parse`, `to_bytes`, `pre_allocate_size`, `check_gc_fence_as_latest_version`, `is_protected`, and `to_owned`.

## Control Flow
Serialization writes a required one-byte write type and varint start timestamp, then optional fields in order: short value, overlapped rollback flag, GC fence, last-change tuple, and transaction source. Parsing reads the required header, then loops over tagged optional fields until data ends or an unknown tag appears, preserving forward compatibility by stopping on unknown bytes. GC-fence checking treats a nonzero fence at or before the read timestamp as invalid when the fenced newer version is missing.

## State and Persistence Behavior
`WriteRef::to_bytes` defines the durable byte layout of write CF values. Short values inline small payloads instead of requiring default-CF reads. Protected rollback records use short value `b"p"`. Overlapped rollback and GC fence metadata repair collisions between commit records and protected rollback records when commit timestamps are not globally unique.

## Dependencies and Integration Points
Uses `TimeStamp`, `LastChange`, `LockType`, shared short-value constants, TiKV number codec, and crate error types. The write bytes are consumed by MVCC readers, GC compaction filtering, CDC, TiFlash, and transaction cleanup paths.

## Risks
The optional-field byte namespace reuses `b'R'` for both rollback type and overlapped rollback optional flag; correctness relies on position in the record. Short-value parsing panics if the encoded length exceeds remaining bytes instead of returning a recoverable bad-format error. Unknown tags stop parsing, so field ordering is part of the compatibility contract. Incorrect GC-fence or last-change data can cause stale values to be served or too many versions to be scanned.

## Test Signals
Unit tests cover write type mapping, serialize/parse round trips for optional fields, bad input, unknown trailing bytes, protected rollback detection, and GC-fence validity. Further test signals should include malformed short-value length fuzzing, cross-version optional-field ordering, and integration reads across overlapped rollback plus GC compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/deny.toml -->
# sources/storage-engines/tikv/deny.toml

## Purpose
Configures `cargo-deny` policy for TiKV dependencies, with emphasis on FIPS-oriented crypto restrictions, advisory handling, allowed licenses, and trusted source origins.

## Important APIs, Types, and Functions
The `[bans]` section denies RustCrypto/hash/TLS/signature-related crates while allowing explicit wrapper paths for cloud SDKs, checksums, and runtime FIPS providers. `[advisories]` denies yanked crates, tracks unmaintained advisories at workspace scope, and documents specific ignored RustSec IDs. `[licenses]` allows Apache-compatible and approved permissive licenses with explicit exceptions. `[sources]` denies unknown registries/git sources and allows selected GitHub orgs.

## Control Flow
This file is declarative. `cargo deny` traverses the resolved dependency graph, applies wrapper exceptions to banned crates, evaluates RustSec advisory policy, checks license expressions and exceptions, then validates source provenance.

## State and Persistence Behavior
No runtime state. It is a persisted CI/security policy and should evolve with dependency updates, RustSec advisories, and legal/security decisions.

## Dependencies and Integration Points
Used by dependency-audit CI and local security checks. It integrates indirectly with the Cargo workspace lockfile and any dependency introduced by TiKV crates, cloud storage integrations, TLS clients, and OpenSSL bindings.

## Risks
Ignored advisories are intentional risk acceptances and require active review; several are tied to avoiding OpenSSL 3.x performance regressions. Wrapper exceptions can mask newly introduced crypto use if dependency paths change. The policy allows multiple versions, so supply-chain risk is controlled by bans/advisories rather than deduplication.

## Test Signals
Run `cargo deny check` after dependency changes. Review failures when adding cloud SDK, TLS, crypto, checksum, or license-sensitive crates. Periodically revalidate ignored RustSec entries and wrapper paths against the current dependency graph.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/deny.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/docker-compose.yml -->
# sources/storage-engines/tikv/docker-compose.yml

## Purpose
Defines a local six-container TiKV cluster: three PD nodes and three TiKV nodes using nightly PingCAP images, persistent named volumes, health checks, and a bridge network.

## Important APIs, Types, and Functions
Services `pd1`, `pd2`, and `pd3` expose client and peer ports, share a static initial cluster string, persist data/logs, and use PD health endpoints. Services `tikv1`, `tikv2`, and `tikv3` depend on all PD health checks, expose TiKV server/status ports, advertise service DNS names, and persist data/logs.

## Control Flow
Compose starts PD nodes together, waits for their health checks, then starts TiKV nodes. TiKV processes connect to all PD endpoints and advertise internal bridge-network hostnames for cluster communication. Health checks poll local PD/TiKV HTTP endpoints until ready.

## State and Persistence Behavior
Named Docker volumes retain PD metadata, TiKV data, and logs across container restarts. Removing volumes resets the cluster. Published host ports make the local cluster accessible outside the compose network.

## Dependencies and Integration Points
Requires Docker Compose, `pingcap/pd:nightly`, `pingcap/tikv:nightly`, container curl support, and available host ports 23791-23793, 23801-23803, 20161-20163, and 20181-20183. Useful for local integration testing against a real PD/TiKV topology.

## Risks
Nightly images are unstable and can change behavior without lockstep source updates. Static container names collide with other local deployments. Exposing status/client ports can leak operational data on shared hosts. Health checks assume `curl` exists in images.

## Test Signals
Run `docker compose up`, verify all six services become healthy, query PD health, and check TiKV `/status`. Validate restart behavior with named volumes and confirm cluster membership in PD after TiKV nodes join.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/etc/config-template.toml -->
# sources/storage-engines/tikv/etc/config-template.toml

## Purpose
Provides the human-readable TiKV configuration template and documentation for operational tuning. Almost every setting is commented, giving default values, units, deployment caveats, and performance tradeoffs for logs, memory, thread pools, storage, Raft, RocksDB, security, backup, pessimistic transactions, and GC.

## Important APIs, Types, and Functions
The template covers top-level logging and memory limits; `[quota]`; `[log]` and `[log.file]`; `[memory]`; read pools; `[resource-control]`; `[server]`; `[storage]`, block cache, flow control, and IO rate limit; `[pd]`; `[raftstore]`; coprocessor sections; `[rocksdb]` with default/write/lock CF and Titan options; `[raftdb]`; `[raft-engine]`; TLS and encryption settings; import/backup/log-backup; pessimistic transactions; and GC.

## Control Flow
This file is consumed as a config template rather than executed. Operators uncomment and tune entries, and TiKV's configuration loader applies them at startup or, for documented dynamic settings, through runtime configuration mechanisms.

## State and Persistence Behavior
It does not persist state itself, but many settings control persistent layout and compatibility: storage engine choice, data directories, WAL directories, Raft Engine format/recycle behavior, RocksDB table format/checksum/compression, Titan enablement/fallback, encryption metadata format, and backup/log-backup behavior.

## Dependencies and Integration Points
Integrates with TiKV server startup, RocksDB/RaftDB/Raft Engine, PD connectivity, backup systems, TLS certificate provisioning, KMS/file encryption providers, Prometheus-observed resource limits, and operational tooling that generates final TiKV configs.

## Risks
Some options are not safely mutable after cluster creation, especially storage engine and Titan-related behavior. Misconfigured memory, block cache, flow control, compaction, WAL, or Raft log settings can cause OOM, write stalls, data unavailability, or disk exhaustion. Security sections can disable TLS or choose weak master-key handling if copied uncritically.

## Test Signals
Validate generated configs with TiKV config-check tooling/startup dry runs. Exercise representative workloads after changing block cache, flow control, RocksDB, Raft, or quota settings. Check downgrade/upgrade compatibility for format-version, encryption dictionary log, Titan, and Raft Engine options.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/etc/config-template.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/etc/error_code.toml -->
# sources/storage-engines/tikv/etc/error_code.toml

## Purpose
Registers stable TiKV error-code identifiers grouped by subsystem. The file maps namespaced keys such as `KV:Storage:WriteConflict` to matching string payloads used by error-code generation and diagnostics.

## Important APIs, Types, and Functions
Sections cover Cloud, Codec, Coprocessor, Encryption, Engine, PD, Raft, Raftstore, SST importer, and Storage errors. Each table contains an `error` multiline string mirroring the table key, providing a canonical textual identifier.

## Control Flow
Declarative TOML is parsed by TiKV build or tooling code that generates/validates error-code definitions. There is no branching in the file; ordering primarily aids maintainability and review.

## State and Persistence Behavior
The identifiers are persistent compatibility surface for logs, metrics, clients, support tooling, and documentation. Renaming or deleting entries can break alerting, dashboards, client matching, or generated code that expects stable codes.

## Dependencies and Integration Points
Integrated with TiKV error handling, generated error-code modules, telemetry/logging, and external tooling that classifies errors by subsystem and reason.

## Risks
Duplication between table name and `error` value can drift. Typos become stable public identifiers if not caught early. Missing entries for new errors can force generic `Unknown` handling and reduce observability.

## Test Signals
Run the repository's error-code generation/validation checks after edits. Add tests that every error table value equals its key and that Rust error enums reference registered codes. Review alert/log dashboards when introducing new high-level classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/etc/error_code.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/Cargo.toml -->
# sources/storage-engines/tikv/fuzz/Cargo.toml

## Purpose
Defines the root fuzz CLI package. It builds the `fuzz` binary from `cli.rs` and supplies dependencies for target discovery, argument parsing, workspace metadata, regex scanning, lazy globals, and error handling.

## Important APIs, Types, and Functions
The package is unpublished, edition 2021, Apache-2.0 licensed. The `[[bin]]` entry names `fuzz` with path `cli.rs`. Dependencies are `anyhow`, `cargo_metadata`, `lazy_static`, `regex`, and `structopt`.

## Control Flow
Cargo uses this manifest to compile the CLI. The CLI then orchestrates fuzzer-specific child crates rather than this manifest directly building fuzz targets.

## State and Persistence Behavior
No runtime persistence. It fixes package metadata and dependency versions/requirements for reproducible local fuzz tooling.

## Dependencies and Integration Points
Integrates with the workspace, `fuzz/cli.rs`, and fuzzer subcrates under `fuzz/fuzzer-*`. `cargo_metadata` discovers workspace root; `regex` discovers functions in `targets/mod.rs`.

## Risks
Older `structopt`/`cargo_metadata` versions may lag current Cargo/clap behavior. If the CLI path or target discovery contract changes, this manifest must remain aligned.

## Test Signals
Run `cargo run -p fuzz -- list-targets` and `cargo check -p fuzz`. Dependency-audit checks should include this package even though it is unpublished.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/cli.rs -->
# sources/storage-engines/tikv/fuzz/cli.rs

## Purpose
Implements a command-line driver for TiKV fuzz targets. It lists discovered targets and runs a selected target through AFL, Honggfuzz, or libFuzzer by generating fuzzer-specific binary source files from templates.

## Important APIs, Types, and Functions
Lazy globals compute `WORKSPACE_ROOT`, `FUZZ_ROOT`, `FUZZ_TARGETS`, and `SEED_ROOT`. `Cli` supports `list-targets` and `run`. `Fuzzer` maps to package names and directories. `write_fuzz_target_source_file`, `run`, `get_seed_dir`, `create_corpus_dir`, `pre_check`, `run_afl`, `run_honggfuzz`, and `run_libfuzzer` implement generation and execution.

## Control Flow
Target discovery reads `fuzz/targets/mod.rs` and extracts `pub fn fuzz_(\w+)(` names. `run` validates the target, writes `src/bin/<target>.rs` for the chosen fuzzer, then dispatches. AFL builds an instrumented binary and invokes `cargo afl fuzz`; Honggfuzz sets sanitizer flags and `HFUZZ_RUN_ARGS`; libFuzzer sets sanitizer coverage flags, target triple, ASAN options, corpus dir, and seed dir.

## State and Persistence Behavior
Creates or overwrites generated fuzzer binary files and corpus directories under fuzzer package directories. Reads seed directories, falling back to `common/seeds/default`. It also relies on and mutates process environment passed to child `cargo` commands.

## Dependencies and Integration Points
Depends on `anyhow`, `structopt`, `cargo_metadata`, `regex`, `lazy_static`, and external cargo subcommands `cargo afl` or `cargo hfuzz`. Integrates with fuzzer templates and the `fuzz-targets` library.

## Risks
`pre_check` unwraps command status, so a missing executable can panic instead of returning context. Regex discovery can miss valid targets or match unintended public functions if signature style changes. Generated source is written into the tree and may become stale. Sanitizer flags require nightly/toolchain/platform support.

## Test Signals
Run `list-targets`, validate generated source for each fuzzer, and perform dry-run/pre-check tests with missing and installed fuzzer tools. Add tests for target regex discovery and seed fallback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/common/seeds/fuzz_codec_bytes/0 -->
# sources/storage-engines/tikv/fuzz/common/seeds/fuzz_codec_bytes/0

## Purpose
Provides an initial seed corpus input for the `fuzz_codec_bytes` target.

## Important APIs, Types, and Functions
The file is raw corpus data rather than code. Its bytes are ASCII `Hello, World!`.

## Control Flow
Fuzzer drivers pass the containing seed directory to AFL/libFuzzer/Honggfuzz. The bytes are fed as input data to `fuzz_codec_bytes`.

## State and Persistence Behavior
Static repository seed. Fuzzers may derive expanded corpora in separate corpus output directories, but this seed file itself is unchanged during normal runs.

## Dependencies and Integration Points
Used by `fuzz/cli.rs::get_seed_dir` when the target name is `fuzz_codec_bytes`; otherwise the CLI falls back to default seeds.

## Risks
The seed is tiny and exercises only simple byte encoding paths at startup. It is useful for bootstrapping but not broad coverage by itself.

## Test Signals
Verify the file is non-empty and that `cargo run -p fuzz -- run <fuzzer> fuzz_codec_bytes` picks this seed directory. Corpus minimization and coverage reports should confirm additional interesting cases are learned.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/common/seeds/fuzz_codec_bytes/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-afl/Cargo.toml -->
# sources/storage-engines/tikv/fuzz/fuzzer-afl/Cargo.toml

## Purpose
Defines the AFL-specific fuzzing crate used by the CLI to compile generated AFL harness binaries.

## Important APIs, Types, and Functions
The package is unpublished, edition 2024, and depends on `fuzz-targets`. On non-Windows x86_64 targets it adds the `afl` crate dependency.

## Control Flow
`fuzz/cli.rs` generates binaries into this package and runs `cargo afl build --bin <target>` followed by `cargo afl fuzz`.

## State and Persistence Behavior
No runtime state in the manifest. It controls dependency resolution and target-gated availability for AFL.

## Dependencies and Integration Points
Integrates with generated `src/bin/*.rs`, `template.rs`, the `fuzz-targets` crate, and the external `cargo afl` tool.

## Risks
AFL is only enabled for x86_64 non-Windows builds; other platforms may compile only the placeholder library. Edition 2024 requires a sufficiently new Rust toolchain.

## Test Signals
Run `cargo check -p fuzzer-afl` and an AFL pre-check on supported hosts. Verify generated binaries compile after target additions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-afl/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-afl/src/lib.rs -->
# sources/storage-engines/tikv/fuzz/fuzzer-afl/src/lib.rs

## Purpose
Placeholder library module that keeps Cargo satisfied for the AFL fuzzer package while actual fuzzer binaries are generated dynamically.

## Important APIs, Types, and Functions
No public API beyond crate existence. The file contains documentation explaining generated binaries come from `fuzz/cli.rs`.

## Control Flow
Cargo can compile the package even when no generated `src/bin` target exists.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Pairs with `fuzzer-afl/template.rs` and the CLI's source generation. It prevents an empty package from being structurally invalid.

## Risks
No behavioral risk; stale comments could mislead if generation moves.

## Test Signals
`cargo check -p fuzzer-afl` should succeed before and after generated binaries are created.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-afl/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-afl/template.rs -->
# sources/storage-engines/tikv/fuzz/fuzzer-afl/template.rs

## Purpose
Template for generated AFL binary harnesses.

## Important APIs, Types, and Functions
Imports the AFL macro crate and `fuzz_targets`, aliases the selected target via `use fuzz_targets::__FUZZ_CLI_TARGET__ as fuzz_target`, and defines `main` with `fuzz!(|data: &[u8]| { let _ = fuzz_target(data); })`.

## Control Flow
The CLI replaces `__FUZZ_CLI_TARGET__` and the generated-comment token, writes the resulting file under `src/bin`, and AFL repeatedly invokes the closure with mutated byte slices.

## State and Persistence Behavior
The template is static; generated files are persisted in the fuzzer package until overwritten. Runtime corpus/crash state is owned by AFL output directories.

## Dependencies and Integration Points
Requires AFL macro support, `fuzz-targets`, and the CLI replacement contract. It must match the target function signature `fn(&[u8]) -> Result<()>`.

## Risks
The target result is ignored, so ordinary parse errors do not fail the fuzz case; only panics/abort/sanitizer issues are findings. Template placeholders are string-replaced without syntax validation until compile time.

## Test Signals
Generate a known target and run `cargo afl build --bin <target>`. Confirm malformed target names are rejected before template generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-afl/template.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/Cargo.toml -->
# sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/Cargo.toml

## Purpose
Defines the Honggfuzz-specific fuzzing crate used by the CLI.

## Important APIs, Types, and Functions
The package is unpublished, edition 2024, and depends on `fuzz-targets`. On non-Windows targets it depends on `honggfuzz = 0.5.47`.

## Control Flow
`fuzz/cli.rs` generates binaries into this package, sets sanitizer and `HFUZZ_RUN_ARGS`, and runs `cargo hfuzz run <target>`.

## State and Persistence Behavior
No runtime state in the manifest; it provides dependency and package metadata for generated harnesses.

## Dependencies and Integration Points
Integrates with `fuzzer-honggfuzz/template.rs`, `fuzz-targets`, and the external `cargo hfuzz` command.

## Risks
Windows is excluded. Honggfuzz version/toolchain compatibility matters, and edition 2024 requires modern Rust.

## Test Signals
Run `cargo check -p fuzzer-honggfuzz` and `cargo hfuzz version`. Compile a generated target after changing fuzz target signatures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/src/lib.rs -->
# sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/src/lib.rs

## Purpose
Placeholder library for the Honggfuzz package so Cargo accepts the crate before generated binaries exist.

## Important APIs, Types, and Functions
No executable API. Comments document dynamic binary generation through `fuzz/cli.rs`.

## Control Flow
No runtime control flow; Cargo loads the library target as the package's stable anchor.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Complements the Honggfuzz template and generated `src/bin` harnesses.

## Risks
Minimal; the file can hide an otherwise empty package but does not affect fuzz execution.

## Test Signals
`cargo check -p fuzzer-honggfuzz` should remain green with no generated targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/template.rs -->
# sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/template.rs

## Purpose
Template for generated Honggfuzz binary harnesses.

## Important APIs, Types, and Functions
Imports the Honggfuzz macro crate and `fuzz_targets`, aliases the selected target, and runs an infinite loop invoking `fuzz!(|data| { let _ = fuzz_target(data); })`.

## Control Flow
The CLI substitutes the target name and generated comment. At runtime Honggfuzz controls input generation and the loop keeps requesting new inputs until crash, stop, or timeout.

## State and Persistence Behavior
Template is static; generated binary source persists under the fuzzer crate. Corpus and crash artifacts are managed by Honggfuzz.

## Dependencies and Integration Points
Requires the target function to be exported from `fuzz-targets` and the `honggfuzz` macro to be available on the host.

## Risks
Ignoring `Result` means expected parsing failures are not treated as crashes. Infinite loop behavior is correct for Honggfuzz but should not be copied to one-shot harnesses.

## Test Signals
Generate and compile a target with `cargo hfuzz run <target>` in a short run. Confirm sanitizer flags supplied by the CLI work with the local nightly compiler.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/template.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/Cargo.toml -->
# sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/Cargo.toml

## Purpose
Defines the libFuzzer-specific fuzzing crate.

## Important APIs, Types, and Functions
The package is unpublished, edition 2024, depends on `fuzz-targets`, and includes `libfuzzer-sys = 0.3.1`.

## Control Flow
`fuzz/cli.rs` generates binaries from `template.rs` and runs `cargo run --target <platform> --bin <target> -- <corpus> <seeds>` with sanitizer coverage flags.

## State and Persistence Behavior
No runtime state in the manifest. It pins the crate-level libFuzzer integration used by generated binaries.

## Dependencies and Integration Points
Integrates with generated `src/bin` files, `fuzz-targets`, libFuzzer runtime, ASAN, and Linux/macOS targets selected in the CLI.

## Risks
`libfuzzer-sys` 0.3.1 and sanitizer flags may require nightly or specific host support. Unsupported OSes panic in the CLI before execution.

## Test Signals
Run `cargo check -p fuzzer-libfuzzer` and a short generated libFuzzer run on Linux/macOS. Verify sanitizer flags remain valid after Rust toolchain upgrades.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/src/lib.rs -->
# sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/src/lib.rs

## Purpose
Placeholder library for the libFuzzer package so Cargo can load the package before generated binary harnesses exist.

## Important APIs, Types, and Functions
No public API; comments point to dynamic generation from `fuzz/cli.rs`.

## Control Flow
No runtime control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Complements libFuzzer template-based generated binaries.

## Risks
No direct behavioral risk.

## Test Signals
`cargo check -p fuzzer-libfuzzer` should pass without generated bins.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/template.rs -->
# sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/template.rs

## Purpose
Template for generated libFuzzer harness binaries.

## Important APIs, Types, and Functions
Uses `#![no_main]`, imports `libfuzzer_sys`, aliases the selected `fuzz_targets` function, and defines `fuzz_target!(|data: &[u8]| { let _ = fuzz_target(data); })`.

## Control Flow
After placeholder substitution, libFuzzer owns process entry and repeatedly invokes the closure with mutated inputs from seed and corpus directories.

## State and Persistence Behavior
Template is static; generated harness files persist under `src/bin`. Runtime corpus evolution is handled by libFuzzer using CLI-provided directories.

## Dependencies and Integration Points
Depends on `libfuzzer-sys`, generated target names, and the `fuzz-targets` function signature.

## Risks
The ignored `Result` filters expected decode failures out of crash reporting. Invalid placeholder substitution creates compile-time errors rather than CLI-time errors.

## Test Signals
Generate a harness and run a short libFuzzer session with ASAN. Confirm crashes are reported for intentional panics in a temporary test target.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/template.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/targets/Cargo.toml -->
# sources/storage-engines/tikv/fuzz/targets/Cargo.toml

## Purpose
Defines the shared library crate containing actual fuzz target functions.

## Important APIs, Types, and Functions
Package `fuzz-targets` is unpublished, edition 2021, and uses `mod.rs` as its library path. It depends on `anyhow`, `byteorder`, `tidb_query_datatype`, and `tikv_util`.

## Control Flow
Fuzzer-specific generated binaries import functions from this crate. The root fuzz CLI also parses this crate's `mod.rs` to discover functions named `fuzz_*`.

## State and Persistence Behavior
No runtime persistence. The manifest defines compile-time dependencies and target layout.

## Dependencies and Integration Points
Integrates with all fuzzer templates, `fuzz/cli.rs` target discovery, TiKV codec utilities, and TiDB query datatype codecs.

## Risks
Changing the library path or crate name breaks templates and CLI discovery. Adding dependencies here affects all fuzzer builds.

## Test Signals
Run `cargo check -p fuzz-targets` and `cargo run -p fuzz -- list-targets` after adding/removing target functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/targets/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/targets/mod.rs -->
# sources/storage-engines/tikv/fuzz/targets/mod.rs

## Purpose
Holds the concrete fuzz target functions for TiKV utility codecs and TiDB query datatype codecs. The file is also a discovery source for `fuzz/cli.rs`, so public functions named `fuzz_*` are the target registry.

## Important APIs, Types, and Functions
Targets include `fuzz_codec_bytes`, `fuzz_codec_number`, decimal arithmetic/hash targets, time parse/from-packed targets, duration parse/from-nanos targets, and row v2 binary-search coverage. Helper traits map raw bytes into decimal round modes and time types. `fuzz_time` and `fuzz_duration` centralize conversion and operation coverage.

## Control Flow
Targets consume byte slices via `Cursor` and `ReadLiteralExt`, decode primitive values, construct codec/domain values, and invoke encode/decode/arithmetic/format/convert operations. Many operations intentionally ignore ordinary `Result`s so fuzzing focuses on panics, invariant violations, and sanitizer failures. Some targets require enough input bytes and return early through `?` on short or invalid data.

## State and Persistence Behavior
No persistent state. Each fuzz invocation allocates local cursors, buffers, contexts, and datatype values. Time targets create `EvalContext` values with fuzzed time zones.

## Dependencies and Integration Points
Depends on `tikv_util::codec`, `tidb_query_datatype` decimal/time/duration/row codecs, `anyhow`, and `util::ReadLiteralExt`. Imported by AFL/Honggfuzz/libFuzzer generated harnesses.

## Risks
Native-endian byte interpretation can reduce cross-platform corpus portability. Ignoring `Result` is intentional but may hide semantic correctness bugs that are not panics. The discovery regex depends on public function formatting. Some operations such as division/modulo and decimal conversion need careful panic-safety coverage.

## Test Signals
Run all discovered targets under at least one fuzzer for smoke coverage. Unit-test target discovery names. Add regression seeds for panics, boundary timestamps, invalid UTF-8/time strings, decimal edge cases, row encodings, and codec length boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/targets/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/targets/util.rs -->
# sources/storage-engines/tikv/fuzz/targets/util.rs

## Purpose
Provides byte-reading helpers for fuzz targets, converting raw input streams into primitive Rust values with native-endian decoding.

## Important APIs, Types, and Functions
`ReadLiteralExt` extends any `io::Read` with `read_as_u8`, signed/unsigned 16/32/64-bit reads, `read_as_f64`, and `read_as_bool`. It delegates to `byteorder::ReadBytesExt` with `NativeEndian` for multi-byte primitives.

## Control Flow
Fuzz targets create a `Cursor<&[u8]>` and call these methods. Short input returns `io::Error`, which propagates through target `Result`s.

## State and Persistence Behavior
No persistent state. Reads advance the caller's stream position.

## Dependencies and Integration Points
Depends on `std::io` and `byteorder`. Used by `fuzz/targets/mod.rs` to keep target parsing concise.

## Risks
`NativeEndian` makes byte interpretation host-dependent, which can make corpora less reproducible across architectures. `read_as_bool` maps even bytes to true and odd bytes to false, which is simple but nonuniform only if fuzzer input distribution is biased.

## Test Signals
Unit-test primitive decoding on known byte arrays for supported platforms. Exercise short-input behavior and verify fuzz targets treat EOF as a non-crashing rejected case.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/fuzz/targets/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/alertmanager/tikv.accelerate.rules.yml -->
# sources/storage-engines/tikv/metrics/alertmanager/tikv.accelerate.rules.yml

## Purpose
Defines Prometheus recording rules that precompute frequently used TiKV metrics for dashboards and alerts, especially p99/p95 latencies, rates, averages, pending tasks, and per-instance resource signals.

## Important APIs, Types, and Functions
The single group `tikv_accelerate` records derived series such as `tikv_grpc_msg_duration_seconds:p99:1m`, raftstore event and append/apply quantiles, thread CPU rates, engine file averages, PD request averages, coprocessor wait metrics, worker pending/handled task rates, async request failures, and no-grpc CPU variants.

## Control Flow
Prometheus evaluates each `expr` at rule intervals, using `rate`, `sum`, `avg`, `histogram_quantile`, and `avg_over_time` over raw TiKV metrics. Recorded names then serve as faster query inputs elsewhere.

## State and Persistence Behavior
Rules create derived time series in Prometheus storage. They do not affect TiKV runtime behavior.

## Dependencies and Integration Points
Depends on TiKV metric names and labels (`instance`, `type`, `le`, `cf`, `level`, `name`, etc.). Integrated with Prometheus/Alertmanager deployments and Grafana dashboards.

## Risks
Label mismatch or metric renames silently produce empty series. Recording rules without environment/job scoping may aggregate more broadly than intended depending on Prometheus setup. Some expressions use broad `instance=~".*"` selectors, so multi-cluster deployments must isolate rule groups or labels.

## Test Signals
Use `promtool check rules`, query each recorded series in a populated Prometheus, and compare dashboard latency panels against raw histogram expressions after metric changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/alertmanager/tikv.accelerate.rules.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/alertmanager/tikv.rules.yml -->
# sources/storage-engines/tikv/metrics/alertmanager/tikv.rules.yml

## Purpose
Defines TiKV alerting rules for critical, emergency, and warning operational conditions such as critical errors, memory growth, GC failure, network/report failures, channel full, write stalls, Raft lag, slow async requests, CPU saturation, pending tasks, low disk space, restarts, and quota pressure.

## Important APIs, Types, and Functions
The `alert.rules` group contains alert entries with PromQL `expr`, optional `for`, labels including `env`, `level`, and duplicated `expr`, and annotations with templated descriptions, values, and summaries. Metrics include TiKV critical errors, process memory, GC worker counters, raftstore histograms, scheduler/coprocessor metrics, worker pending tasks, store size, process start time, and TiDB client GC results.

## Control Flow
Prometheus evaluates each expression; if it remains true for the configured `for` duration, Alertmanager receives a firing alert with labels and annotations. Several critical alerts fire after one minute; the critical-error alert intentionally has no `for` clause.

## State and Persistence Behavior
The file creates alert state in Prometheus/Alertmanager but does not mutate TiKV. Alert state persists according to Prometheus evaluation history and Alertmanager grouping/silencing.

## Dependencies and Integration Points
Depends on stable metric names and labels exported by TiKV, TiDB clients, and process exporters. `ENV_LABELS_ENV` is a deployment-time placeholder. Integrates with Alertmanager routing and on-call runbooks.

## Risks
PromQL typos or stale metric names can disable alerts; for example exact label regex and metric spelling must match exporters. Hard-coded thresholds may be noisy or blind for clusters of different sizes. Broad selectors can cross cluster boundaries if environment labels are not templated correctly.

## Test Signals
Run `promtool check rules`, execute expressions in staging Prometheus, verify alert routing with sample labels, and review historical firing frequency after threshold changes. Add metric-rename checks when TiKV instrumentation changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/alertmanager/tikv.rules.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/common.py -->
# sources/storage-engines/tikv/metrics/grafana/common.py

## Purpose
Provides shared Python helpers for generating TiKV Grafana dashboards with `grafanalib`. It centralizes Prometheus expression construction, dashboard variables, target creation, panel layout, graph/time-series/stat/table/heatmap panel factories, legends, axes, series overrides, and histogram panel patterns.

## Important APIs, Types, and Functions
Constants define Prometheus datasource input and Grafana variables. `Expr` models PromQL aggregation/function/selectors/range/by/extra clauses, with mutation helpers for aggregation, functions, extra expression text, default instance skipping, and group-by extension. `OpExpr` combines expressions with binary operators. Helper functions include `expr_sum`, `expr_avg`, `expr_max`, `expr_min`, `expr_sum_rate`, `expr_sum_delta`, `expr_sum_increase`, `expr_histogram_quantile`, `expr_topk`, `expr_histogram_avg`, `target`, `template`, `Layout`, `timeseries_panel`, `yaxis`, `yaxes`, `graph_legend`, `graph_panel`, `series_override`, `heatmap_panel`, `stat_panel`, `graph_panel_histogram_quantiles`, histogram heatmap/graph pair creation, and `table_panel`.

## Control Flow
Dashboard modules build `Expr` objects, convert them to strings when constructing `Target`s, and then pass targets into panel factories. `Layout.row` assigns Grafana grid positions. Histogram helpers derive `_bucket`, `_sum`, and `_count` series from a base metric. Panel helpers patch grafanalib JSON where needed, such as graph fill gradients, series override fields, heatmap options, and table transformations.

## State and Persistence Behavior
No external persistence. Many helpers mutate object instances in place: `Expr.aggregate`, `Expr.function`, `Expr.extra`, `append_by_labels`, `target(additional_groupby=True)`, and y-axis decimal assignment change existing objects. Generated dashboard JSON is the durable artifact outside this file.

## Dependencies and Integration Points
Depends on `attrs`, `grafanalib.core`, and `grafanalib.formatunits`. Integrates with TiKV dashboard generator modules, Prometheus labels (`k8s_cluster`, `tidb_cluster`, `instance`), Grafana templating, and recorded/raw metrics from the alert rule files.

## Risks
Several defaults are mutable lists (`label_selectors=[]`, `by_labels=["instance"]`, panel override defaults), which can leak mutations between calls if modified. `Expr` methods mutate and return `self`, so reusing expression objects can unintentionally alter earlier targets. String-built PromQL has limited validation beyond selector assertions. `target(additional_groupby=True)` assumes a legend format is present for some paths.

## Test Signals
Generate dashboards and validate JSON with grafanalib/Grafana import checks. Unit-test representative PromQL strings, histogram suffix assertions, additional group-by legend changes, layout grid positions, table target instant mode, and series override JSON patches.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/common.py -->
