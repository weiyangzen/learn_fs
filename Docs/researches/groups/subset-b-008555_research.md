# subset-b-008555 Research

Grouped research report for Pebble WAL reader/manager files and raft-engine CI, CLI, engine, environment, and file-log sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/reader.go -->
# sources/storage-engines/pebble/wal/reader.go

## Purpose
Defines the logical WAL discovery and reading layer for Pebble. A `LogicalLog` is a virtual WAL number plus one or more ordered physical segment files, allowing WAL failover to present a single replay stream even when writes moved between directories or log-name indexes.

## Important APIs, Types, And Functions
Key types are `LogicalLog`, private `segment`, `Logs`, `FileAccumulator`, and `virtualWALReader`. Public entry points include `Scan`, `FileAccumulator.MaybeAccumulate`, `FileAccumulator.Finish`, `Logs.Get`, `LogicalLog.OpenForRead`, `LogicalLog.PhysicalSize`, `LogicalLog.SegmentLocation`, and `Copy`. `appendDeletableLogs` converts every physical segment into deletion candidates.

## Control Flow
`Scan` lists every supplied WAL directory and feeds filenames into `FileAccumulator`. Accumulation parses `.log` filenames, binary-searches the logical WAL slice by WAL number, and binary-searches each WAL's segments by `LogNameIndex`, rejecting duplicates. `virtualWALReader.NextRecord` lazily opens the first segment, reads record fragments through `record.Reader`, buffers full records, skips malformed tails on non-final segments, parses batch headers, skips LogData-only batches, and deduplicates repeated batches by monotonically increasing sequence number. `Copy` replays a logical WAL through the virtual reader and writes a single destination WAL until the visible sequence boundary.

## State And Persistence Behavior
The file persists no metadata itself, but it maps durable physical WAL files into logical replay state. `Offset` tracks physical file path, physical offset, and bytes read from prior segments. `lastSeqNum` is transient deduplication state; `recordBuf` owns the record returned to callers until the next read. `Copy` creates a new physical WAL and syncs the writer on close, but explicitly leaves destination directory sync to the caller.

## Dependencies And Integration Points
Depends on Pebble batch headers, `record.Reader`/`LogWriter`, `vfs`, filename helpers from `wal.go`, and CockroachDB errors/redaction. Recovery uses this reader to replay virtual WALs, and managers use `LogicalLog`/`Logs` as the common inventory representation across standalone and failover modes.

## Risks And Edge Cases
Deduplication assumes WAL records contain valid non-LogData batches with increasing sequence numbers. Invalid batch headers are treated as corruption even if the record envelope is valid. Non-final segment tail corruption is ignored to tolerate failover/recycling, but final-segment corruption is surfaced to recovery policy. `Copy` must not leak destination files on mid-copy errors and must reject batches whose assigned sequence range straddles `visibleSeqNum`.

## Test Signals
`reader_test.go` covers listing, duplicate log indexes, segment ordering, virtual read behavior, corrupt/unclean tails, forced missing segments, logical copy limits, and copy error cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/reader_test.go -->
# sources/storage-engines/pebble/wal/reader_test.go

## Purpose
Datadriven and regression tests for Pebble WAL logical listing, virtual segment replay, duplicate suppression, tail-corruption handling, and logical WAL copy.

## Important APIs, Types, And Functions
`TestList` exercises `Scan`, `FileAccumulator`, `ParseLogFilename`, and safe formatting. `TestReader` builds real record log files with `record.LogWriter`, then reads them through `LogicalLog.OpenForRead` and `virtualWALReader`. `TestCopyClosesWriterOnError` verifies `Copy` closes destination resources after corruption errors.

## Control Flow
The `list` test maintains named in-memory filesystems, accepts `touch`, `reset`, and `list` commands, and prints logical WALs. The reader test supports `define`, `copy`, and `read` commands. `define` writes fake batch records, garbage bytes, recycled files, corrupt tails, synced records, and crash-cloned unclean logs. `read` scans WALs, optionally injects nonexistent segment metadata, and prints every `NextRecord` result plus decoded batch headers. `copy` invokes `Copy` into a target directory with a requested visible sequence number.

## State And Persistence Behavior
Tests use crashable and logging `MemFS` implementations to model durable directory sync, file creation, recycling, unsynced data loss, and open file tracking. Batch sequence numbers and counts are encoded into record payloads so reader deduplication and LogData-only skip rules are observable.

## Dependencies And Integration Points
Uses `datadriven`, Pebble `batchrepr`, `record`, `vfs`, `vfstest.WithOpenFileTracking`, `datadrivenutil`, leak tests, and testify assertions. The tests bind WAL package behavior to lower record-layer semantics.

## Risks And Edge Cases
Important cases are stale readers after `NextRecord`, unclean WAL tails from crash/recycle, duplicated records across segments, records too short for batch headers, LogNameIndex gaps, missing physical segment files, and resource cleanup when `Copy` fails before the log writer closes normally.

## Test Signals
The datadriven output shows exact offsets, physical file paths, record contents, parsed headers, and errors. The regression test fails if open destination handles remain after `Copy` returns an expected corruption error.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/standalone_manager.go -->
# sources/storage-engines/pebble/wal/standalone_manager.go

## Purpose
Implements the `Manager` interface for Pebble's non-failover WAL mode, where each logical WAL maps to exactly one physical file in the primary WAL directory.

## Important APIs, Types, And Functions
`StandaloneManager` owns `Options`, a `LogRecycler`, an open directory handle, initial obsolete logs, an active `standaloneWriter`, and a mutex-protected WAL queue. Methods implement `init`, `List`, `Obsolete`, `Create`, `Stats`, `Close`, `Opts`, and `RecyclerForTesting`. `standaloneWriter` implements `Writer` through `WriteRecord`, `Close`, and `Metrics`. `firstError` preserves primary failure ordering.

## Control Flow
`init` rejects secondary-directory configuration, opens the primary WAL directory, initializes recycling, and marks all initial logs obsolete/deletable while ratcheting the minimum recyclable number. `Create` chooses either a recycled log via `ReuseForWrite` or a new file via `Create`, emits log-created events through a deferred `CreateInfo`, stats recycled size if needed, pops the recycler entry, syncs the directory, wraps the file in `vfs.NewSyncingFile`, and constructs a `record.LogWriter`. `Obsolete` removes initial and queued WALs below `minUnflushedNum`, adding some to the recycler unless `noRecycle` is set.

## State And Persistence Behavior
The queue stores live and already-flushed WAL file metadata; flushed WALs are a prefix. Active WAL size is recorded as original recycled size until close, then updated to logical writer size if larger. Directory sync after creation makes the link durable. Writer close writes the record-layer EOF trailer and syncs unless configured otherwise.

## Dependencies And Integration Points
Integrates with Pebble commit pipeline synchronization, WAL recycling, event listener callbacks, file-operation histograms, `record.LogWriter`, `vfs.SyncingFile`, and DB log-obsolescence decisions.

## Risks And Edge Cases
The implementation relies on external serialization for create/write/close. Recycled file size may be inaccurate until stat because `ReuseForWrite` may replace instead of reuse. The previous writer must be closed before a new WAL is created; otherwise two unclean tails after a crash can make recovery treat the earlier WAL as corrupt. Initial obsolete logs can contain multi-segment failover WALs and must be handled separately from the single-file queue.

## Test Signals
Coverage is indirect through WAL manager, DB open/recovery, recycling, event listener, and standalone WAL behavior tests. Metrics and `Obsolete` outputs expose live versus obsolete accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/standalone_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/wal.go -->
# sources/storage-engines/pebble/wal/wal.go

## Purpose
Defines shared WAL package contracts: directory metadata, logical WAL numbering, physical filename parsing, manager/writer/reader interfaces, failover options, event payloads, stats, deletion records, and offsets.

## Important APIs, Types, And Functions
Important exported items are `StableIdentifierFilename`, `Dir`, `NumWAL`, `LogNameIndex`, `ParseLogFilename`, `Options`, `Init`, `Options.Dirs`, `FailoverOptions`, `FailoverOptions.EnsureDefaults`, `EventListener`, `CreateInfo`, `Stats`, `FailoverStats`, `Manager`, `DeletableLog`, `SyncOptions`, `Writer`, `RefCount`, `Reader`, and `Offset`.

## Control Flow
`Init` selects `StandaloneManager` when `Options.Secondary` is empty and `failoverManager` otherwise, then delegates initialization with the existing scanned `Logs`. `ParseLogFilename` accepts backward-compatible `NNNN.log` names as log index zero and failover segment names of the form `NNNN-III.log`; non-WAL `.log` files that do not parse as disk file numbers are ignored. `FailoverOptions.EnsureDefaults` fills probe, health, sampling, threshold, and elevated-stall defaults.

## State And Persistence Behavior
`Dir.ID` is a stable persisted directory identity used to detect incorrect secondary WAL mounts. The `Manager` abstraction owns durable WAL lifecycle, while `Writer` exposes append, close, and record-layer metrics. `Offset` records physical replay location and prior segment byte count for failover-aware diagnostics.

## Dependencies And Integration Points
Integrates with Pebble options, DB recovery, commit pipeline synchronization, event listeners, Prometheus histograms, file locks, `record.LogWriter`, and virtual WAL readers. The package documents that the manifest knows only logical WAL numbers; this package reconstructs physical segment mappings from directory contents.

## Risks And Edge Cases
Filename parsing intentionally ignores unrelated `.log` files to preserve CockroachDB compatibility. Failover defaults govern write-stall and failback behavior, so too-aggressive thresholds can cause unnecessary directory switches, while too-lax thresholds hurt latency. `WriteRecord` may retain the caller buffer unless a `RefCount` is supplied. `Manager.Obsolete` must not delete unflushed WALs.

## Test Signals
Signals appear in WAL filename/list tests, failover manager tests elsewhere, standalone manager behavior, and `wal_failover_identifier_test.go` for stable secondary identifiers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/wal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal_failover_identifier_test.go -->
# sources/storage-engines/pebble/wal_failover_identifier_test.go

## Purpose
Tests Pebble's WAL failover stable identifier mechanism, which protects recovery from accidentally using the wrong secondary WAL directory or mounted disk.

## Important APIs, Types, And Functions
`TestWALFailoverIdentifier` uses public `Open`, `Options`, `WALFailoverOptions`, `wal.Dir`, and `wal.StableIdentifierFilename`. Helper `writeTestIdentifier` writes and syncs a secondary `stable_identifier` file through `vfs.FS`.

## Control Flow
The test has four subtests. First open with failover generates an identifier, writes it to the secondary directory, and records it in the OPTIONS file. A mismatch between an existing secondary identifier and configured `Dir.ID` must fail open with a wrong-disk error. If the primary options lack an identifier but the secondary already has one, open adopts it and persists it in OPTIONS. Reopening a database with a different user-supplied identifier than the recovered OPTIONS value must fail.

## State And Persistence Behavior
The durable state under test is both the secondary `stable_identifier` file and the primary database OPTIONS content. The tests use `vfs.NewMem`, but explicitly create, open, read, and sync identifier files to model the persistence contract.

## Dependencies And Integration Points
Integrates Pebble DB open option parsing, WAL failover directory initialization, OPTIONS serialization, WAL package directory IDs, and `vfs` file APIs.

## Risks And Edge Cases
The critical risk is silently accepting a stale or wrong secondary WAL directory, which could replay unrelated logs or miss required logs. Adoption behavior must distinguish a legitimate existing secondary ID from a conflicting user-provided ID. The test reads OPTIONS by listing for `OPTIONS-` files, so changes in options-file naming would affect it.

## Test Signals
Signals are non-empty generated identifiers, presence of `[WAL Failover]` and `secondary_identifier=...` in OPTIONS, successful adoption of existing IDs, and expected wrong-disk error strings on mismatches.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal_failover_identifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/.github/dependabot.yml -->
# sources/storage-engines/raft-engine/.github/dependabot.yml

## Purpose
Configures GitHub Dependabot for the raft-engine subtree so Cargo dependency updates are proposed automatically.

## Important APIs, Types, And Functions
The YAML uses Dependabot schema `version: 2` with one `updates` entry. It targets `package-ecosystem: cargo`, `directory: /`, and a daily schedule.

## Control Flow
There is no runtime control flow. GitHub's Dependabot service reads this file and periodically evaluates Cargo manifests and lockfiles at the repository root.

## State And Persistence Behavior
The file does not affect engine persistence. Its state impact is repository metadata: generated dependency update pull requests may later change Cargo dependency versions.

## Dependencies And Integration Points
Integrates with GitHub automation, Cargo manifest dependency declarations, and the CI workflow in `.github/workflows/rust.yml` that validates generated dependency PRs.

## Risks And Edge Cases
Daily update cadence can create frequent PR churn. It only targets the root directory, so workspace members are covered through the root workspace, but separate nested ecosystems would require more entries. Dependabot PRs are ignored by the workflow push trigger through branch filtering.

## Test Signals
Signals are operational rather than unit-test based: Dependabot PR creation, CI execution on dependency changes, and absence of stale security/dependency alerts.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/.github/workflows/rust.yml -->
# sources/storage-engines/raft-engine/.github/workflows/rust.yml

## Purpose
Defines raft-engine's GitHub Actions Rust CI for linting, tests, feature matrix coverage, and Codecov upload.

## Important APIs, Types, And Functions
The workflow has `stable` and `coverage` jobs. It installs Rust 1.85.0 with rustfmt, clippy, and rust-src for stable validation, and nightly-2026-01-30 with llvm-tools-preview for coverage. It uses `actions/checkout@v2`, `actions-rs/toolchain@v1`, `Swatinem/rust-cache@v1`, `grcov`, and `codecov/codecov-action@v3`.

## Control Flow
The workflow runs on pushes except `dependabot/**` branches and on pull requests except docs/OWNERS-only changes. The stable job runs `make clippy` and `make test` with `WITH_STABLE_TOOLCHAIN=force`. The coverage job waits for stable, runs `make test_matrix` under coverage instrumentation, converts `.profraw` data to lcov with grcov, and uploads `coverage.lcov`.

## State And Persistence Behavior
No production state is changed. CI cache state is shared by OS/toolchain key, and Codecov receives coverage artifacts. Environment variables set cargo color, backtraces, verbose cargo output, and coverage flags.

## Dependencies And Integration Points
Integrates with the repository `Makefile`, Cargo workspace, feature flags, failpoint tests, Codecov config, Rust toolchains, and GitHub secrets for `CODECOV_TOKEN`.

## Risks And Edge Cases
The checkout ref assumes pull_request context; push events without that field may rely on GitHub expression behavior. Actions versions are older. Coverage depends on nightly availability and grcov installation. Path ignores prevent CI from running for markdown-only changes, which is intentional but can miss generated docs that affect examples.

## Test Signals
Signals are clippy success, stable tests, failpoints test pass, nightly feature matrix pass, grcov success, and Codecov status checks with configured thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/.github/workflows/rust.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/Cargo.toml -->
# sources/storage-engines/raft-engine/Cargo.toml

## Purpose
Declares the raft-engine crate metadata, examples, tests, benchmarks, dependencies, features, patches, and workspace members.

## Important APIs, Types, And Functions
The package is `raft-engine` version 0.4.2, edition 2024, Rust 1.85.0. It declares examples `append-compact-purge` and `raft-engine-fork`, a failpoints integration test requiring internals/failpoints, and a benchmark requiring failpoints. Features include default `internals` and `scripting`, plus `nightly`, `failpoints`, `swap`, `std_fs`, and `nightly_group`.

## Control Flow
Cargo uses this manifest to build the library, examples, workspace members `stress` and `ctl`, and optional feature combinations selected by the Makefile and CI. `docs.rs` is configured to build with `internals`.

## State And Persistence Behavior
The manifest controls binary and library dependency resolution rather than runtime state. Feature choices materially affect persistence behavior: `swap` enables memory-limit behavior via memmap, `std_fs` selects a plain file descriptor path, failpoints enable injected I/O failures, and `scripting` enables repair tooling.

## Dependencies And Integration Points
Dependencies include byte encoding, CRC, failpoints, fs locking, logging, compression, protobuf, prometheus, serde, Rhai scripting, and error handling. Dev dependencies bring raft/kvproto protobuf types, random testing, temp files, TOML, and benchmarks. Patches pin raft-proto/protobuf forks and cc-rs.

## Risks And Edge Cases
Git dependencies and patch overrides can make reproducibility depend on upstream branches. Root crate Rust version is newer than `ctl`'s local manifest. Pinned `lz4-sys` and `cc` reflect build compatibility constraints. Default inclusion of `scripting` and `internals` broadens normal builds.

## Test Signals
Cargo metadata is exercised by `make clippy`, `make test`, CI matrix, examples, failpoint tests, and docs.rs feature builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/Makefile -->
# sources/storage-engines/raft-engine/Makefile

## Purpose
Provides standard developer and CI entry points for formatting, linting, testing, coverage matrix execution, cleanup, and building the control binary.

## Important APIs, Types, And Functions
Targets are `all`, `clean`, `format`, `clippy`, `test`, `test_matrix`, and `ctl`. Important variables are `EXTRA_CARGO_ARGS`, `WITH_STABLE_TOOLCHAIN`, `WITH_NIGHTLY_FEATURES`, `TOOLCHAIN_ARGS`, `BIN_PATH`, `CARGO_TARGET_DIR`, and exported `RUST_LOG=info`.

## Control Flow
The Makefile detects whether nightly features should be enabled from `WITH_STABLE_TOOLCHAIN` and current rustc version. Stable forced mode uses `+stable` and disables nightly feature groups. Nightly-capable mode runs clippy and tests with `nightly_group` and failpoints, while stable mode uses failpoints only. `test_matrix` requires nightly feature mode and runs additional default/failpoints/std_fs combinations.

## State And Persistence Behavior
The file only affects local build artifacts: `target/`, `bin/`, coverage inputs through test execution, and compiled `raft-engine-ctl`. It does not mutate engine data except temporary test directories created by tests.

## Dependencies And Integration Points
CI calls this Makefile directly. Cargo feature flags from `Cargo.toml`, failpoints tests, clippy lint configuration, and the `ctl` workspace package all integrate here.

## Risks And Edge Cases
Toolchain auto-detection can surprise users with nightly-only features if their default toolchain is nightly. `test_matrix` hard-errors under stable mode. The clippy whitelist only allows `bool_assert_comparison`, so new lints may break CI after toolchain updates.

## Test Signals
Successful `make all`, `make test`, `make test_matrix`, and `make ctl` are the primary signals. CI uses these targets as authoritative validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/codecov.yml -->
# sources/storage-engines/raft-engine/codecov.yml

## Purpose
Configures Codecov coverage status thresholds for raft-engine.

## Important APIs, Types, And Functions
The YAML defines project and patch coverage statuses. Both use `target: auto` and `threshold: 3%`. The ignore list excludes `stress` and `ctl`.

## Control Flow
After CI uploads `coverage.lcov`, Codecov evaluates project-wide and patch-level coverage against automatic baselines while allowing a three percent tolerance.

## State And Persistence Behavior
No runtime persistence is involved. The file affects repository quality-gate metadata and pull request statuses.

## Dependencies And Integration Points
Integrates with `.github/workflows/rust.yml`, the grcov-generated lcov file, and Codecov's status checks. Ignoring `ctl` means CLI code coverage does not affect the main engine threshold.

## Risks And Edge Cases
The broad threshold can permit meaningful coverage drops. Excluding `stress` and `ctl` is reasonable for non-library code but can hide regressions in tooling unless covered elsewhere.

## Test Signals
Signals are Codecov project and patch checks after coverage upload.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/ctl/Cargo.toml -->
# sources/storage-engines/raft-engine/ctl/Cargo.toml

## Purpose
Declares the `raft-engine-ctl` workspace package, a command-line control tool for inspecting and repairing raft-engine data.

## Important APIs, Types, And Functions
Package metadata sets version 0.4.2, edition 2018, Rust 1.75.0, and Apache-2.0 license. Dependencies are `clap` with derive/cargo features, `env_logger`, and the local `raft-engine` crate with `scripting` and `internals` features.

## Control Flow
Cargo builds this package as a workspace member. The `Makefile` target `ctl` builds it in release mode and copies the binary to `bin/`.

## State And Persistence Behavior
The manifest itself has no runtime state. Enabling `scripting` and `internals` gives the CLI access to unsafe repair and internal log queue APIs, which can mutate existing raft-engine data when invoked.

## Dependencies And Integration Points
Integrates with `ctl/src/lib.rs`, `ctl/src/main.rs`, Clap 3 command parsing, logger initialization, and root crate repair/check/dump APIs.

## Risks And Edge Cases
The CLI package advertises a lower Rust version than the root crate. The dependency version says `raft-engine` 0.4.1 while the local path package is 0.4.2, so publishing/versioning should be checked carefully.

## Test Signals
Build success through `make ctl` and any tests that invoke `run_command` or control APIs are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/ctl/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/ctl/src/lib.rs -->
# sources/storage-engines/raft-engine/ctl/src/lib.rs

## Purpose
Implements the reusable control-command library behind `raft-engine-ctl`, exposing typed command-line parsing and execution over an injectable filesystem.

## Important APIs, Types, And Functions
`ControlOpt` is the Clap parser. `Cmd` variants are `Dump`, `Check`, `Repair`, and `TryPurge`. `convert_queue` maps CLI strings to `LogQueue`. `ControlOpt::validate_and_execute`, `validate_and_execute_with_file_system`, and `run_command` are the execution entry points.

## Control Flow
Execution rejects missing subcommands. `Dump` creates a `LogItemReader` via `Engine::dump_with_file_system` and prints each decoded item, optionally filtering by raft group IDs. `Repair` reads a Rhai script file and invokes `Engine::unsafe_repair_with_file_system` over append, rewrite, or all queues. `Check` runs consistency checking and prints corrupted raft groups with last intact indexes. `TryPurge` opens an engine on the target path and prints the result of `purge_expired_files`.

## State And Persistence Behavior
Dump and check are read-only. Repair can rewrite data files according to a script and is intentionally named unsafe. Try-purge opens the engine and may rewrite/purge expired files, changing log file layout while preserving logical engine state.

## Dependencies And Integration Points
Depends on Clap, `DefaultFileSystem`/`FileSystem`, `Engine`, `Error`, `LogQueue`, and Rust `std::fs` for script reading. Filesystem injection allows tests or alternate environments to reuse command execution.

## Risks And Edge Cases
Errors are printed rather than propagated by `run_command`, which is convenient for CLI use but not ideal for programmatic assertions. Dump prints item errors inline and continues iterating. Repair scripts and TryPurge can mutate production data; callers need external backups and clear queue selection.

## Test Signals
Signals include command parse validation, dump output counts/content, consistency-check output, repair behavior under scripting feature tests, and successful purge attempts on existing data directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/ctl/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/ctl/src/main.rs -->
# sources/storage-engines/raft-engine/ctl/src/main.rs

## Purpose
Small binary entry point for the raft-engine control tool.

## Important APIs, Types, And Functions
Imports `clap::Parser` and `raft_engine_ctl::ControlOpt`. `main` initializes `env_logger`, parses command-line arguments, and invokes `ControlOpt::validate_and_execute`.

## Control Flow
Startup is linear: initialize logging, parse args into `ControlOpt`, execute, and print the debug representation of any returned error.

## State And Persistence Behavior
The binary itself owns no persistent state. The selected subcommand may read or mutate raft-engine directories through the library layer.

## Dependencies And Integration Points
Integrates with the library parser in `ctl/src/lib.rs`, Clap-derived CLI metadata, environment logging configuration, and all underlying `Engine` tooling APIs.

## Risks And Edge Cases
The process exits with success even after printing an error because `main` does not set a non-zero exit code. That can hide failures in shell automation unless stdout/stderr is inspected.

## Test Signals
Build success and CLI smoke tests are the useful signals. Behavioral coverage mostly belongs to `ctl/src/lib.rs` and engine tool tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/ctl/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/examples/append_compact_purge.rs -->
# sources/storage-engines/raft-engine/examples/append_compact_purge.rs

## Purpose
Demonstrates a continuously running workload that appends Raft entries, stores last-index messages, compacts regions, and calls purge to exercise raft-engine rewrite/purge behavior.

## Important APIs, Types, And Functions
Defines `MessageExtTyped` implementing `MessageExt` for raft-rs `Entry`. Uses `Config`, `Engine`, `LogBatch`, `ReadableSize`, `get_message`, `add_entries`, `put_message`, `write`, `compact_to`, and `purge_expired_files`.

## Control Flow
The example opens `append-compact-purge-data` with a low compression threshold and 2GB purge threshold. It repeatedly chooses normally distributed region IDs and compact offsets, increments each region's persisted `RaftLocalState.last_index`, appends a 32KB entry, writes the batch, and periodically compacts based on the index. After each 1024 writes, it purges expired files and force-compacts returned regions close to their last index.

## State And Persistence Behavior
It creates a real raft-engine data directory, persists entries and per-region last-index messages, records compaction commands, and physically rewrites/purges log files. The loop is infinite, so disk usage and purge behavior are the demonstration target.

## Dependencies And Integration Points
Integrates with kvproto `RaftLocalState`, raft-rs `Entry`, rand normal distributions, env_logger, and the main engine append/compact/purge APIs.

## Risks And Edge Cases
The infinite loop can consume disk indefinitely if purge behavior is broken or the process is left running. Random region IDs can cast negative normal samples to large `u64` values. The example unwraps all errors and is not production-safe.

## Test Signals
Operational signals are debug logs and printed compact/force-compact messages, plus stable engine behavior under sustained append/compact/purge load.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/examples/append_compact_purge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/examples/fork.rs -->
# sources/storage-engines/raft-engine/examples/fork.rs

## Purpose
Minimal command-line example for forking/copying a raft-engine directory from a source path to a target path.

## Important APIs, Types, And Functions
Uses `Config`, `Engine::<_, _>::fork`, `DefaultFileSystem`, `Arc`, and basic `std::env::args` parsing.

## Control Flow
The program prints usage, reads source and target positional arguments, builds a default config with `dir` set to the source, constructs a default filesystem, calls `Engine::fork`, unwraps errors, and prints success.

## State And Persistence Behavior
The source engine directory is read and the target directory is populated by `Engine::fork`. The example does not open the copied engine afterward or validate contents.

## Dependencies And Integration Points
Integrates with the engine fork API, default filesystem abstraction, and path handling. It is useful as a runnable example for backup/copy workflows.

## Risks And Edge Cases
Argument parsing is intentionally minimal and panics on missing arguments. There is no overwrite protection or validation in this wrapper beyond whatever `Engine::fork` enforces. All errors panic through `unwrap`.

## Test Signals
Signals are successful example build and a manual run producing `success!` with a usable target directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/examples/fork.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/rustfmt.toml -->
# sources/storage-engines/raft-engine/rustfmt.toml

## Purpose
Configures rustfmt behavior for the raft-engine workspace.

## Important APIs, Types, And Functions
The only setting is `wrap_comments = true`, enabling comment wrapping during formatting.

## Control Flow
`cargo fmt --all`, invoked by the Makefile and developers, reads this file and applies the setting to Rust source formatting.

## State And Persistence Behavior
It affects source formatting only and has no runtime or persistence impact.

## Dependencies And Integration Points
Integrates with rustfmt installed by CI, the `make format` target, and the stable toolchain component list in the GitHub workflow.

## Risks And Edge Cases
Comment wrapping can create larger diffs when comments are reformatted, especially around long URLs, generated comments, or carefully aligned documentation.

## Test Signals
The main signal is `cargo fmt --all --check` or `make format` producing no unexpected diff.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/rustfmt.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/codec.rs -->
# sources/storage-engines/raft-engine/src/codec.rs

## Purpose
Provides low-level numeric encoding and decoding helpers used by raft-engine binary formats, including mem-comparable big-endian encodings, descending-order encodings, protobuf-compatible varints, and little-endian primitives.

## Important APIs, Types, And Functions
Exports `BytesSlice`, codec `Error`, `Result`, trait `NumberEncoder`, and decoders such as `decode_i64`, `decode_u64`, `decode_var_u64`, `decode_var_i64`, `decode_f64`, little-endian decoders, and `read_u8`. Internal helpers include `order_encode_i64`, `order_decode_i64`, `order_encode_f64`, `order_decode_f64`, and `read_num_bytes`.

## Control Flow
Encoders are extension methods on any `Write`. Ordered integer encodings flip the sign bit or invert bytes for descending order. Ordered float encodings transform IEEE bits so lexicographic byte order matches numeric order for supported values. Varint encoding emits seven-bit chunks compatible with protobuf unsigned varints, and signed varints use zig-zag style transformation. Decoders consume from `&mut &[u8]`, advancing slices only after successful byte consumption.

## State And Persistence Behavior
This file directly defines on-disk byte layout for numbers embedded in log files and batches. It is stateless at runtime, but any format change would affect backward compatibility.

## Dependencies And Integration Points
Depends on `byteorder`, `thiserror`, protobuf tests, and Rust I/O traits. File-format code uses `NumberEncoder` and decoders to encode log headers and versions.

## Risks And Edge Cases
Incorrect order transforms would break sorted comparisons. Varint decoding uses unchecked indexing after length guards, so guard correctness is critical. Floating NaN is intentionally not part of ordering tests. Unexpected EOF and overflow must be distinguishable from format errors.

## Test Signals
Unit tests cover serialization round trips, lexicographic order, protobuf varint compatibility, little-endian helpers, EOF handling, overflow, and `read_u8` exhaustion.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/codec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/config.rs -->
# sources/storage-engines/raft-engine/src/config.rs

## Purpose
Defines raft-engine runtime configuration, recovery modes, defaults, validation, and derived capacities for log recycling and prefill.

## Important APIs, Types, And Functions
Exports `RecoveryMode` and `Config`. `Config::default` sets directory, recovery, compression, format, target size, purge thresholds, memory limit, recycle, and prefill defaults. `Config::sanitize` validates and normalizes values. `recycle_capacity` and `prefill_capacity` calculate file counts from thresholds and format support.

## Control Flow
`sanitize` rejects `purge_threshold < target_file_size`, fills `purge_rewrite_threshold`, warns on deprecated `bytes_per_sync`, raises too-small recovery read block and thread counts, rejects log recycling for unsigned format versions, rejects prefill when recycling is disabled, clears ignored prefill limits, fills missing prefill limits, and warns if `memory_limit` is set without the `swap` feature.

## State And Persistence Behavior
Configuration controls on-disk format version, recovery tolerance, file size rotation, purge/rewrite thresholds, compression, and file recycling. `format_version` and recycle options are especially persistence-sensitive because unsigned V1 files cannot be safely recycled.

## Dependencies And Integration Points
Integrates with `pipe_log::Version`, serde/TOML, logging, `ReadableSize`, engine open, file pipe log builder, purge manager, and feature-gated swap support.

## Risks And Edge Cases
Misconfigured thresholds can disable purge or force excessive rewrites. Enabling recycle on unsupported formats is rejected because stale data in recycled files could be replayed. Backward-compatible spelling for tail-corruption mode must be preserved for old configs.

## Test Signals
Tests cover serde round trips, custom TOML loading, hard and soft sanitization errors, backward compatibility for recovery-mode spelling, and prefill/recycle interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/consistency.rs -->
# sources/storage-engines/raft-engine/src/consistency.rs

## Purpose
Implements a replay machine that checks recovered log streams for holes in Raft entry indexes.

## Important APIs, Types, And Functions
`ConsistencyChecker` stores per-raft-group `(first_index, last_index)` ranges and a `corrupted` map from raft group ID to last valid index. It exposes `finish` and implements `ReplayMachine` through `replay` and `merge`.

## Control Flow
During `replay`, the checker scans each `LogItemBatch`, considers only `EntryIndexes` content, extracts incoming first/last indexes, initializes a group range when first seen, and records corruption if the next incoming first index is more than one past the current last index. `merge` combines checker outputs from recovered files or queues and detects holes between merged ranges as well as holes already found in the right-hand checker.

## State And Persistence Behavior
The checker does not mutate persisted files. It derives transient corruption diagnostics from durable log contents and returns the earliest observed last intact index per raft group.

## Dependencies And Integration Points
Depends on `ReplayMachine`, `LogItemBatch`, `LogItemContent`, `FileId`, and `LogQueue`. `Engine::consistency_check_with_file_system` uses it with `RecoveryMode::TolerateAnyCorruption`.

## Risks And Edge Cases
Head or tail corruption cannot be detected by this range continuity method. Out-of-order replay or incorrect merge order could create false positives or miss holes. The checker reports only the first last-valid index per group.

## Test Signals
Signals are CLI/check outputs and engine consistency-check tests that expect sorted corrupted raft-group pairs.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/consistency.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/engine.rs -->
# sources/storage-engines/raft-engine/src/engine.rs

## Purpose
Implements raft-engine's main public storage engine: opening and recovering file logs, writing batches, reading entries and messages through memtables, compacting, purging, syncing, dumping, consistency checking, unsafe repair, metrics flushing, and cached entry decoding.

## Important APIs, Types, And Functions
`Engine<F, P>` owns config, listeners, stats, memtables, pipe log, purge manager, write barrier, and metrics flusher. Key APIs include `open`, `open_with_listeners`, `open_with_file_system`, `open_with`, `write`, `sync`, `get_message`, `get`, `scan_messages`, `scan_raw_messages`, `get_entry`, `fetch_entries_to`, `compact_to`, `purge_expired_files`, `raft_groups`, `is_empty`, `file_span`, `get_used_size`, `path`, `consistency_check_with_file_system`, `unsafe_repair_with_file_system`, `dump_with_file_system`, `read_entry_from_file`, and `read_entry_bytes_from_file`.

## Control Flow
Open sanitizes config, adds a purge hook listener, scans log files, recovers append and rewrite queues through `FilePipeLogBuilder`, merges append context into rewrite context, builds memtables/stats, constructs a purge manager, and starts a background metrics flusher. `write` finalizes a `LogBatch`, enters the write barrier so a leader appends grouped writers, optionally syncs the append queue, handles one `TryAgain` retry for no-space spill behavior, applies written commands to memtables, notifies listeners, and records metrics/perf context. Reads consult memtables for entry indexes or key-values and fetch entry bytes from pipe-log blocks using a thread-local one-block cache. Tooling APIs recover with special replay machines or readers.

## State And Persistence Behavior
Durable state lives in append and rewrite log queues. Memtables and stats are reconstructed from replay on open. Compaction writes `Command::Compact`; clean commands remove raft groups; purge rewrites live entries and deletes or recycles obsolete files. `sync` fdatasyncs the append queue. `Drop` stops and joins the metrics thread.

## Dependencies And Integration Points
Integrates with `Config`, `FileSystem`, `FilePipeLog`, `PipeLog`, `LogBatch`, memtables, `PurgeManager`, `EventListener`, write barrier grouping, protobuf decoding, metrics, perf context, consistency checker, dump readers, and optional Rhai repair filters.

## Risks And Edge Cases
The non-empty write path panics on sync error while `Engine::sync` returns an error. Empty synced writes must still call `sync`, which is explicitly handled. Fetching entries must tolerate indexes becoming stale during concurrent rewrite by rereading memtable under lock. Recovery mode determines corruption tolerance. Unsafe repair can destroy data if scripts filter incorrectly. Metrics thread shutdown unwraps send/join results.

## Test Signals
In-file tests cover empty engines, get/fetch/read after recovery, key-value scan/delete, clean and compact interactions, purge triggers, rewrite/recover, empty protobuf messages, empty synced batches, dirty recovery, large rewrite batches, format-version/recycle compatibility, dump and repair tools, tail corruption, wrong filesystem detection, managed deletion/reuse metadata, perf context, atomic rewrite groups, concurrent fetch with rewrite, internal-key filtering, and multi-directory spill behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/default.rs -->
# sources/storage-engines/raft-engine/src/env/default.rs

## Purpose
Provides the default filesystem implementation and a `LogFile` adapter that turns shared low-level log file handles into standard `Read`, `Write`, `Seek`, and `WriteExt` objects.

## Important APIs, Types, And Functions
`LogFile` wraps `Arc<LogFd>` plus an offset. It implements `Write`, `Read`, `Seek`, and `WriteExt`. `DefaultFileSystem` implements `FileSystem` with `create`, `open`, `delete`, `rename`, `new_reader`, and `new_writer`.

## Control Flow
Reads and writes delegate to offset-based `LogFd` operations and advance the logical offset. `Seek` updates the offset from start/current/end positions. `truncate` delegates to the handle and resets offset. `allocate` delegates to the handle. Filesystem operations create/open/delete/rename underlying files and wrap handles as readers or writers. Failpoints inject zero writes and I/O errors for tests.

## State And Persistence Behavior
`LogFile` tracks only an in-memory offset; durable behavior comes from `LogFd` write, truncate, allocate, and sync operations. Delete removes physical files. Rename is used for file reuse and log movement.

## Dependencies And Integration Points
Depends on `env::FileSystem`, `Handle`, `Permission`, `WriteExt`, platform-specific `LogFd`, and failpoints. File pipe log readers/writers are built on this abstraction.

## Risks And Edge Cases
Offset arithmetic for `SeekFrom::Current` and `SeekFrom::End` casts signed values to `usize`; invalid negative seeks would wrap if callers misuse it. Failpoint zero writes validate upper layers. `flush` is a no-op because durability is explicit through handle sync.

## Test Signals
Failpoint-driven tests in the engine and file log layers exercise create/open/read/write/seek/truncate/allocate errors and zero writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/default.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/log_fd.rs -->
# sources/storage-engines/raft-engine/src/env/log_fd.rs

## Purpose
Selects the concrete low-level log file descriptor implementation for the current target and feature set.

## Important APIs, Types, And Functions
Re-exports `unix::LogFd` when not Windows and `std_fs` is not enabled; otherwise re-exports `plain::LogFd`.

## Control Flow
Compilation-time `cfg` gates choose the module. There is no runtime branch.

## State And Persistence Behavior
Persistence semantics depend on the selected implementation. Unix uses raw file descriptors and positional I/O; plain uses synchronized standard `File` handles.

## Dependencies And Integration Points
Integrated by `env/default.rs`, which imports `crate::env::log_fd::LogFd`. The `std_fs` feature in Cargo and platform target decide which backend backs all default file operations.

## Risks And Edge Cases
Different implementations can have subtle performance and sync behavior differences. CI's feature matrix includes `std_fs` to catch fallback-specific regressions.

## Test Signals
Compilation on supported targets and `std_fs` feature test runs validate module selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/log_fd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/log_fd/plain.rs -->
# sources/storage-engines/raft-engine/src/env/log_fd/plain.rs

## Purpose
Provides a portable, simple `LogFd` implementation based on `std::fs::File`, used on Windows or when the `std_fs` feature is enabled.

## Important APIs, Types, And Functions
`LogFd(Arc<RwLock<File>>)` exposes `open`, `create`, `read`, `write`, `truncate`, and `allocate`, and implements `Handle` with `file_size` and `sync`.

## Control Flow
Open/create build a read-write `File` in an `Arc<RwLock<_>>`. Reads and writes take the write lock, seek to the requested offset, then perform the operation. Truncate calls `set_len`; allocate is a no-op. Sync takes the write lock and calls `sync_all`. Failpoints inject no-space, file-size, and sync errors.

## State And Persistence Behavior
The shared `File` object is protected by a lock to emulate positional I/O safely. Writes, truncation, and sync mutate durable file contents. Allocation does not reserve space in this backend.

## Dependencies And Integration Points
Depends on parking_lot `RwLock`, failpoints, `std::fs`, and the `Handle` trait. It is selected by `env/log_fd.rs` for fallback builds and is used by `DefaultFileSystem`.

## Risks And Edge Cases
All I/O serializes through the file lock, so performance differs from Unix `pread`/`pwrite`. `OpenOptions::create(true)` without truncate can preserve old content unless higher layers reset headers/truncate. No-op allocation means allocation-related paths need Unix coverage too.

## Test Signals
The `std_fs` CI feature matrix and failpoint tests exercise this implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/log_fd/plain.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/log_fd/unix.rs -->
# sources/storage-engines/raft-engine/src/env/log_fd/unix.rs

## Purpose
Provides the optimized Unix low-level log file descriptor implementation using raw file descriptors, positional reads/writes, fallocate, and fdatasync/fsync.

## Important APIs, Types, And Functions
`LogFd(RawFd)` exposes `open`, `create`, `close`, `read`, `write`, `truncate`, and `allocate`, and implements `Handle` with `file_size` and `sync`. Helpers include `from_nix_error` and `From<Permission> for OFlag`.

## Control Flow
Open maps engine permissions to `O_RDONLY` or `O_RDWR`, creates files with mode 0644, and has a failpoint path that calls `posix_fadvise64(DONTNEED)`. Reads loop on `pread` until the buffer is full or EOF, retrying `EINTR`. Writes loop on `pwrite`, retrying `EINTR`, mapping `ENOSPC` to a recognizable no-space error. Allocation uses Linux `fallocate` and ignores unsupported-operation errors. Drop closes the fd and logs close errors.

## State And Persistence Behavior
This backend mutates durable file contents at explicit offsets without maintaining a shared seek cursor. `truncate` changes file length, `allocate` may reserve disk blocks, and `sync` uses `fdatasync` on Linux or `fsync` elsewhere.

## Dependencies And Integration Points
Depends on `nix`, `libc` on Linux, failpoints, logging, and `env` traits. It is the default backend for Unix builds unless `std_fs` is enabled.

## Risks And Edge Cases
Short writes returning zero stop the loop without filling the buffer, so upper layers must handle incomplete write results. Sync errors are returned through the handle but some upper layers panic on sync failure. Raw fd ownership relies on `Drop`; accidental duplication would be dangerous.

## Test Signals
Failpoint tests inject no-space, sync, file-size, and close failures. Normal engine tests exercise pread/pwrite, truncate, fallocate, and sync behavior under real temp directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/log_fd/unix.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/mod.rs -->
# sources/storage-engines/raft-engine/src/env/mod.rs

## Purpose
Defines raft-engine's filesystem abstraction layer so the engine can run over default, test, obfuscated, or user-provided file systems.

## Important APIs, Types, And Functions
Exports `DefaultFileSystem` and `ObfuscatedFileSystem`. Defines `Permission`, trait `FileSystem`, trait `Handle`, and trait `WriteExt`.

## Control Flow
`FileSystem` implementors provide create/open/delete/rename, optional reuse/reuse-and-open, metadata cleanup hooks, and reader/writer construction. `Handle` provides truncate, file-size, and sync. `WriteExt` provides writer-side truncate and allocation. Default `reuse` is rename, and default metadata hooks are no-ops.

## State And Persistence Behavior
The abstraction is the persistence boundary for log files and associated external metadata. Metadata hooks support cleanup for older versions that deleted physical files without invoking user metadata cleanup.

## Dependencies And Integration Points
Used by `Engine`, `FilePipeLog`, file readers/writers, test file systems, CLI injection, and examples. `Permission` maps into platform open flags in backend modules.

## Risks And Edge Cases
Implementors must preserve expected durability semantics for sync, truncate, rename/reuse, and metadata deletion. A filesystem whose `exists_metadata` disagrees with physical files can confuse recovery cleanup. Reuse semantics may be stronger or weaker than rename depending on implementation.

## Test Signals
The unit test verifies `Permission` copy/equality. Broader signals come from engine tests using `ObfuscatedFileSystem` and `DeleteMonitoredFileSystem`.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/obfuscated.rs -->
# sources/storage-engines/raft-engine/src/env/obfuscated.rs

## Purpose
Implements a special test filesystem that transforms bytes on read/write and tracks file counts, helping catch assumptions about direct filesystem contents and file lifecycle.

## Important APIs, Types, And Functions
`ObfuscatedReader`, `ObfuscatedWriter`, and `ObfuscatedFileSystem` implement the file abstraction. `file_count` reports the tracked count of successfully created minus deleted files.

## Control Flow
The reader reads at most one byte and subtracts one from it before returning. The writer writes at most one byte, adding one first. Seeks, truncate, and allocate delegate to the default implementation. `ObfuscatedFileSystem` delegates create/open/delete/rename/new_reader/new_writer to `DefaultFileSystem`, increments count on successful create, decrements on successful delete, and implements `reuse` as delete plus create.

## State And Persistence Behavior
The on-disk bytes are intentionally obfuscated relative to logical bytes. File count is in-memory atomic state used by tests to validate deletion/reuse behavior. Durable data is still stored through the default filesystem.

## Dependencies And Integration Points
Used heavily in engine tests to run through the generic `FileSystem` abstraction. It depends on `DefaultFileSystem`, `Permission`, `WriteExt`, and atomics.

## Risks And Edge Cases
One-byte read/write behavior stresses callers that assume full-buffer progress. It is not a production filesystem and has different reuse semantics from rename-based filesystems.

## Test Signals
Engine recovery, rewrite, purge, and read tests using this filesystem signal that higher layers tolerate short I/O and abstract byte transformations.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/env/obfuscated.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/errors.rs -->
# sources/storage-engines/raft-engine/src/errors.rs

## Purpose
Defines raft-engine's public error type, result alias, and a helper for recognizing no-space I/O errors.

## Important APIs, Types, And Functions
`Error` variants are `InvalidArgument`, `Corruption`, `Io`, `Codec`, `Protobuf`, `TryAgain`, `EntryCompacted`, `EntryNotFound`, `Full`, and boxed `Other`. `Result<T>` aliases `std::result::Result<T, Error>`. `is_no_space_err` checks whether an I/O error string contains `nospace`.

## Control Flow
Most variants are converted through `From` implementations generated by `thiserror` for I/O, codec, protobuf, and boxed errors. No-space detection is string-based because stable Rust lacks a storage-full error kind in this code path.

## State And Persistence Behavior
The file owns no state, but error classification controls retry and failover behavior. In particular, `TryAgain` is used by `Engine::write` for limited retry after no-space handling.

## Dependencies And Integration Points
Depends on `thiserror`, std I/O/error traits, and `codec::Error`. Used throughout engine, file pipe log, recovery, CLI, and tests.

## Risks And Edge Cases
String matching for `nospace` is brittle and depends on backend error messages. Broad boxed `Other` can hide structured context. Some sync errors panic in callers instead of propagating this error type.

## Test Signals
No-space failpoints, write retry tests, corruption recovery tests, and CLI error printing provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/event_listener.rs -->
# sources/storage-engines/raft-engine/src/event_listener.rs

## Purpose
Defines extension callbacks for observing important raft-engine internal file and memtable events.

## Important APIs, Types, And Functions
`EventListener` is a `Sync + Send` trait with default no-op methods: `post_new_log_file`, `on_append_log_file`, `post_apply_memtables`, `first_file_not_ready_for_purge`, and `post_purge`.

## Control Flow
Engine and pipe-log components call listeners around file creation, log append, memtable application, purge readiness decisions, and post-purge notifications. Callers may install multiple listeners; engine open also appends a purge hook listener.

## State And Persistence Behavior
The trait itself is stateless. Implementations may maintain external state that affects purge behavior through `first_file_not_ready_for_purge`, making listener correctness relevant to durable file deletion timing.

## Dependencies And Integration Points
Uses `FileBlockHandle`, `FileId`, `FileSeq`, and `LogQueue` from pipe-log types. Integrated with `Engine::open_with`, write apply callbacks, and purge manager/file pipe log hooks.

## Risks And Edge Cases
Callbacks may run under different locks or threading contexts, including global queue locks, so implementations must avoid blocking or re-entering engine APIs unsafely. A conservative `first_file_not_ready_for_purge` can retain files indefinitely; an incorrect permissive one can allow premature deletion.

## Test Signals
Purge hook behavior, managed deletion/reuse tests, and listener-based integration tests elsewhere are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/event_listener.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/format.rs -->
# sources/storage-engines/raft-engine/src/file_pipe_log/format.rs

## Purpose
Defines filesystem-level raft-engine log object names, reserved-file names, lock-file path, zero-padding detection, and encoded log file header format.

## Important APIs, Types, And Functions
Exports `is_zero_padded`, trait `FileNameExt` for `FileId`, `parse_reserved_file_name`, `build_reserved_file_name`, and `LogFileFormat`. Constants define 16-digit sequence width, append/rewrite/reserved suffixes, and the magic header.

## Control Flow
`FileId::parse_file_name` parses fixed-width sequence prefixes and suffixes into append or rewrite queue IDs. Builders format file names and paths. `LogFileFormat::encode` writes the magic header, version, and V2 alignment payload. `decode` validates the magic header, decodes the version, validates payload length, and decodes alignment when present.

## State And Persistence Behavior
The file format is persisted in every log file header. V1 headers carry no alignment payload; V2 carries alignment and supports log signing/recycling elsewhere. Reserved append files use a distinct suffix and contain zero padding before reuse.

## Dependencies And Integration Points
Depends on codec number encoders/decoders, `pipe_log::{FileId, FileSeq, LogQueue, Version}`, numeric enum conversion, and engine errors. File scanning, recovery, recycling, and lock management rely on these names and headers.

## Risks And Edge Cases
`is_zero_padded` only checks first and last bytes, so corrupt interior bytes may pass this early check and fail later processing. Header corruption, unknown versions, missing payload, and V1 nonzero alignment are important compatibility cases. Filename parsing ignores short or wrong-suffix files.

## Test Signals
Tests cover padding checks, append/rewrite filename parsing/building, version conversion, header encode/decode, abnormal versions, V1 alignment assertion, and log file context signatures.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/format.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/log_file.rs -->
# sources/storage-engines/raft-engine/src/file_pipe_log/log_file.rs

## Purpose
Implements append-only log file writers and random-access log file readers on top of the generic filesystem abstraction, including header writing, preallocation, truncation, sync, and block reads.

## Important APIs, Types, And Functions
`build_file_writer`, `LogFileWriter`, `build_file_reader`, and `LogFileReader` are the core items. `FILE_ALLOCATE_SIZE` caps preallocation chunks at 2 MiB. Writer methods include `open`, `write_header`, `close`, `truncate`, `write`, `sync`, and `offset`; reader methods include `open`, `parse_format`, `read`, `read_to`, and `file_size`.

## Control Flow
Writer open inspects handle size. If the file is too small for the expected header or force-reset is requested, it rewinds and writes a fresh header; otherwise it seeks to the current file end. `write` calculates required capacity, attempts allocation using target-size hints, writes all bytes, and on write failure reseeks to the previous written offset so the writer remains reusable. `close` truncates fallocated zeros and syncs. Reader parse reads the maximum header length from offset zero and decodes format. `read_to` seeks only when needed and loops until the buffer is filled or EOF, retrying interrupted reads.

## State And Persistence Behavior
`LogFileWriter` tracks durable write offset and allocated capacity. It mutates file headers, payload bytes, truncation length, and sync durability. `LogFileReader` tracks its current offset as a cache over the underlying reader. Allocation may create extra zero bytes that are removed on close/truncate.

## Dependencies And Integration Points
Depends on `FileSystem`, `Handle`, `WriteExt`, `FileBlockHandle`, `LogFileFormat`, metrics, failpoints, and engine errors. It is used by file pipe log queues for appends, rewrites, recovery reads, and block lookup.

## Risks And Edge Cases
`sync` unwraps handle sync and panics on failure to avoid silent data loss. Allocation failures are logged but non-fatal, so later writes may still fail. A failpoint can skip truncate, leaving padded zeros for recovery to interpret. The fail-safe writer promise depends on successful reseek after failed writes.

## Test Signals
Signals come from file format tests, failpoint tests, engine recovery/rewrite tests, tail corruption handling, and purge/recycle tests that depend on proper truncation and header parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/log_file.rs -->
