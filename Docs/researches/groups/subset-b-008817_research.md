# subset-b-008817 Research

Grouped research for the source files assigned to `subset-b-008817`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/executor.rs -->
# sources/storage-engines/tikv/cmd/tikv-ctl/src/executor.rs

## Purpose
`executor.rs` abstracts `tikv-ctl` debug operations behind a `DebugExecutor` trait so the CLI can execute the same high-level commands against either a live remote TiKV debug service or local store files opened directly. It is the operational bridge for value dumps, MVCC scans, region and raft inspection, compaction, tombstoning, unsafe recovery, flashback, metrics, and region read-progress diagnostics.

## Important APIs, Types, And Functions
- `new_debug_executor(cfg, data_dir, host, mgr)` chooses remote mode when `host` is present; otherwise it opens local engines under `data_dir`. Local mode detects RaftKV vs RaftKV2 by directory shape, initializes encryption key manager, shared RocksDB env/cache, KV engine factory, raftdb or raft-engine, then returns either `DebuggerImpl<..., ApiV1>` or `DebuggerImplV2`.
- `new_debug_client(host, mgr)` creates a large-message debug gRPC client with TLS/security manager integration.
- `DebugExecutor` is the command surface. Default methods implement user-facing formatting and orchestration; required methods supply backend-specific primitive reads/writes.
- Remote implementation for `DebugClient` maps methods to `debugpb` RPCs such as `get`, `region_info`, `raft_log`, `scan_mvcc`, `compact`, metrics, config mutation, consistency check, flashback, and region read-progress.
- Local implementations for `DebuggerImpl` and `DebuggerImplV2` map the same trait to server debug internals. Several operations remain local-only or remote-only and fail fast when invoked in the wrong mode.
- `handle_engine_error` emits a specific warning for RocksDB LOCK conflicts and exits without encouraging unsafe lock-file removal.

## Control Flow
The main flow is mode selection followed by trait dispatch. Remote mode wraps requests into protobuf messages and exits on RPC errors via `perror_and_exit`. Local mode constructs engines and delegates to `Debugger` methods. Default trait methods validate arguments before calling primitives: MVCC scan checks `z` data-key prefixes and CF names; raw scan checks CF/range/limit; region diff creates a second executor and merges two sorted MVCC streams; compaction translates region metadata to data-key ranges.

Recovery flows are guarded by `check_local_mode`. `set_region_tombstone_after_remove_peer` and `recover_regions_mvcc` fetch authoritative region metadata from PD before local mutation. `recreate_region` fetches a PD region, allocates new region/peer IDs, rewrites epoch and peer metadata, then initializes an empty local region.

## State And Persistence Behavior
Local mode opens persistent KV and raft state directly. It can mutate durable metadata via tombstone, recovery, dropped raft logs, recreated regions, reset-to-version, compaction, and MVCC recovery. Remote mode mutates through TiKV debug RPCs. `get_engine_type` assumes exactly one of `db` or `tablets` exists and asserts otherwise. The file uses `ApiV1` for local `DebuggerImpl` construction, so API-version handling depends on the debug layer and store metadata for other paths.

## Dependencies And Integration Points
This file integrates with `tikv-ctl` command dispatch in `main.rs`, `server::debug`/`debug2`, RocksDB and raft-engine factories, `pd_client::RpcClient`, `security::SecurityManager`, `kvproto::debugpb`, raft protobuf decoding, `raftstore` key-range helpers, encryption config, and engine traits. It also shares formatting and exit helpers from `util.rs`.

## Risks And Edge Cases
- Local direct-engine access is dangerous if TiKV is still running; `handle_engine_error` detects LOCK conflict but other concurrent-access hazards still rely on RocksDB/engine behavior and operator discipline.
- `get_engine_type` unwraps directory reads and asserts mutually exclusive layout; unusual or partially migrated data directories will panic.
- Remote/local parity is incomplete. Raw scan is remote-unimplemented, metrics and consistency/config mutation are local-unavailable, and several V2 recovery methods are unimplemented.
- MVCC scan and diff can be expensive over large ranges; `limit == 0` means unbounded range scan in several paths.
- Flashback retry handling is implemented in `main.rs`; this file’s remote `flashback_to_version` only returns a retry tuple with the failed range and error.

## Test Signals
There are no unit tests in this file. Coverage is indirect through `tikv-ctl` command tests, server debug tests, backup/flashback integration tests, and compile-time trait conformance for `DebugClient`, `DebuggerImpl`, and `DebuggerImplV2`. The explicit warnings and mode guards are important manual-test targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/fork_readonly_tikv.rs -->
# sources/storage-engines/tikv/cmd/tikv-ctl/src/fork_readonly_tikv.rs

## Purpose
`fork_readonly_tikv.rs` builds an "agent" data directory from an existing TiKV data directory for read-only reuse. It copies or symlinks snapshots, KV RocksDB files, and raft engine/raftdb files while avoiding files that can be modified or unsafe to share.

## Important APIs, Types, And Functions
- Constants `SYMLINK` and `COPY` define accepted reuse modes.
- `run(config, agent_dir, reuse_snaps, reuse_rocksdb_files)` is the entrypoint called by `tikv-ctl reuse-readonly-remains`.
- `dup_snaps`, `dup_kv_engine_files`, and `dup_raft_engine_files` build the target directory layout.
- `reuse_stuffs` filters and copies/symlinks selected files.
- `replace_symlink_with_copy` swaps selected symlinks with writable copies.
- `rocksdb_files_should_copy` selects the highest-numbered RocksDB WAL matching `^([0-9]+).log$`.
- Small filesystem wrappers format errors with source and destination paths.

## Control Flow
`run` first rejects encrypted data directories, creates the agent directory, then duplicates snapshots, KV engine files, and raft engine files. Snapshot duplication selects only `.meta` and `.sst`. KV RocksDB duplication copies everything except `LOCK`; if WALs are external, it additionally reuses the WAL directory. In symlink mode it replaces the last WAL symlink with a copy because that WAL is the file most likely to need local modification. Raft-engine duplication either uses `RaftEngine::fork` and makes copied files writable, or applies the same RocksDB/raftdb reuse rules when raft-engine is disabled.

## State And Persistence Behavior
This module creates filesystem state under `agent_dir`. In symlink mode most SST/manifest-like files remain shared with the source, while mutable tail WAL files are copied and made writable. It intentionally refuses encryption because linking or copying encrypted file sets without matching key manager behavior could produce unsafe or unreadable clones.

## Dependencies And Integration Points
It depends on `TikvConfig` path inference, `encryption_export::data_key_manager_from_config`, `raft_engine::Engine::fork`, `DefaultFileSystem`, `regex`, Unix symlink APIs, and `main.rs` validation that restricts storage engine and raft-engine recovery/recycle settings before calling `run`.

## Risks And Edge Cases
- The code assumes Unix symlink support.
- The destination directory must not already exist; `create_dir` fails if it does.
- `reuse_stuffs` canonicalizes source entries and unwraps UTF-8 file names; unusual non-UTF-8 filenames would panic.
- Only the last WAL is copied in symlink mode; correctness relies on RocksDB WAL immutability assumptions documented in comments.
- The printed error says `reuse_redonly_remains`, a typo, but the behavior is clear.

## Test Signals
Inline tests cover snapshot filename matching and last-WAL selection. Integration safety is mostly validated by `main.rs` preconditions and by operational use against real TiKV data directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/fork_readonly_tikv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/main.rs -->
# sources/storage-engines/tikv/cmd/tikv-ctl/src/main.rs

## Purpose
`main.rs` is the `tikv-ctl` executable entrypoint. It parses CLI commands, initializes FIPS mode, logging, TiKV config, and security, then dispatches administrative, diagnostic, repair, encryption, RocksDB, backup-log compaction, flashback, and debug commands.

## Important APIs, Types, And Functions
- `main()` owns command parsing and dispatch for `Cmd`.
- `new_security_mgr` builds TLS/security configuration from CLI certificate paths.
- `dump_snap_meta_file`, `read_cluster_id`, `validate_storage_data_dir`, `read_fail_file`, `flush_std_buffer_to_log` are local utilities for specific command families.
- `get_pd_rpc_client`, `split_region`, `compact_whole_cluster`, `flashback_whole_cluster`, and `load_key_range` coordinate PD and TiKV debug clients across a cluster.
- `TemporaryRocks`, `build_rocks_opts`, `run_ldb_command`, and `run_sst_dump_command` support RocksDB tooling and compact-log-backup SST generation.
- `print_bad_ssts` and `print_overlap_region_and_suggestions` analyze corrupt SSTs and print operator recovery suggestions.

## Control Flow
Startup enables FIPS, parses `Opt`, initializes a control logger, loads default or TOML config, and constructs a security manager. If no subcommand is present it serves key conversion helpers (`hex-to-escaped`, `escaped-to-hex`, raw/encoded key conversion) or prints help.

Dispatch has several tiers. Some commands run without opening a debug executor: external RocksDB tools, raft-engine-ctl, bad SST analysis, snapshot metadata dump, file decryption, encryption metadata, encryption cleanup, cluster compaction, region split, cluster ID reading, read-only remains reuse, flashback, and compact log backup. The remaining command set requires either `--data-dir` or `--host`, constructs a `DebugExecutor`, then delegates print/raft/size/scan/mvcc/diff/compact/tombstone/recovery/failpoint/store/cluster/reset/read-progress operations.

`flashback_whole_cluster` creates remote debuggers for stores, obtains start and commit TSOs, loads region-to-leader-store ranges from PD, runs prepare and finish phases with timeout, and reloads stale ranges on retryable leader/region changes. `compact_whole_cluster` fans out remote compactions to all non-TiFlash stores.

## State And Persistence Behavior
This executable can read and mutate persistent TiKV state. Sensitive operations include decrypting files to plaintext, dumping encryption keys, cleanup of encryption metadata, direct engine compaction, tombstoning, unsafe recovery, dropping raft logs, region recreation, reset-to-version, flashback, and compact-log-backup output generation. Confirmation prompts protect plaintext decryption and key dumps. `ShowClusterId` disables auto compactions and Titan GC before opening the engine to avoid modifications.

## Dependencies And Integration Points
`main.rs` coordinates most adjacent modules: CLI definitions in `cmd.rs`, executor abstractions in `executor.rs`, read-only clone helpers in `fork_readonly_tikv.rs`, and utilities in `util.rs`. Externally it integrates with PD, TiKV debug gRPC, RocksDB raw tools, raft-engine-ctl, backup-stream/compact-log-backup hooks, external storage, encryption export, FIPS crypto setup, status server lite, and TiKV config validation/path inference.

## Risks And Edge Cases
- Many commands exit the process on invalid input or backend failure; this is acceptable for a CLI but makes compositional error handling limited.
- Some destructive commands rely on operator-supplied `--force`, PD endpoints, or data-dir/host mode correctness.
- Flashback uses a `Mutex` around the debugger map inside async tasks, so RPCs are serialized while holding the map lock; this may limit parallelism.
- `thread::sleep(Duration::from_micros(WAIT_APPLY_FLASHBACK_STATE))` uses a constant documented as milliseconds but sleeps microseconds, which may be intentional or a unit bug.
- `print_bad_ssts` parses RocksDB tool output with regexes and may skip unexpected formats.

## Test Signals
This file has no direct unit tests. Its behavior is exercised through command parsing, debug service tests, backup/flashback integration tests, RocksDB tool compatibility, and manual operator workflows. High-risk paths warrant integration coverage around flashback retries, bad-SST parsing, encryption confirmation behavior, and data-dir validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/util.rs -->
# sources/storage-engines/tikv/cmd/tikv-ctl/src/util.rs

## Purpose
`util.rs` contains small shared helpers for `tikv-ctl`: logger initialization, explicit operator confirmation, hex decoding, byte-size formatting, error-and-exit, and key-range intersection checks.

## Important APIs, Types, And Functions
- `init_ctl_logger(level, format)` creates a default `TikvConfig`, routes RocksDB/raftdb info logs to `./ctl-engine-info-log`, chooses JSON or text log format, and calls `server::setup::initial_logger`.
- `warning_prompt(message)` requires the exact input `I consent`.
- `from_hex` accepts plain hex or `0x`/`0X` prefixed hex.
- `convert_gbmb` formats byte counts as bytes, MiB, or GiB plus MiB.
- `perror_and_exit` prints a prefixed error and exits gracefully.
- `check_intersect_of_range` checks whether two left-closed, right-open TiKV key ranges overlap, treating empty endpoints as unbounded.

## Control Flow
The helpers are direct and side-effect-light except for logger initialization, stdin prompting, and process exit. `check_intersect_of_range` first rejects when the region end is before or equal to the limit start, then rejects when the limit end is strictly before the region start; otherwise it reports an intersection.

## State And Persistence Behavior
The logger setup writes engine info logs under `./ctl-engine-info-log`. `warning_prompt` gates commands that may expose plaintext data or keys but does not persist consent.

## Dependencies And Integration Points
Used by `main.rs` and `executor.rs`. It depends on `kvproto::kvrpcpb::KeyRange`, `server::setup::initial_logger`, `TikvConfig`, `tikv_util::config::LogFormat`, `hex`, and raftstore test helpers.

## Risks And Edge Cases
- `init_ctl_logger` panics for invalid log level or format.
- `warning_prompt` trims only newline, not carriage return; Windows-style input may not match.
- `convert_gbmb` returns an empty string for exactly zero GiB after MiB path only below MiB returns bytes, so larger exact multiples are handled as GiB with trailing space trimmed by composition.

## Test Signals
Unit tests cover `from_hex` prefixes and range-intersection cases including unbounded endpoints, exact boundary behavior, partial overlap, containment, and last-region semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-server/Cargo.toml -->
# sources/storage-engines/tikv/cmd/tikv-server/Cargo.toml

## Purpose
This manifest defines the `tikv-server` binary crate. It is intentionally small and depends on the workspace `tikv`, `server`, `crypto`, and utility crates to build the production TiKV executable.

## Important APIs, Types, And Functions
As a Cargo manifest, it exposes features rather than Rust APIs. Key features include allocator choices (`tcmalloc`, `jemalloc`, `mimalloc`), portability/SSE, memory profiling, failpoints, OpenSSL vendoring, async task tracing, tablet lifetime tracing, pprof failpoint support, and test-engine selections. Default features enable RocksDB KV test engine and raft-engine test support.

## Control Flow
Cargo uses this file to select optional dependencies and feature forwarding. Most feature flags are simple pass-throughs to `server` or `tikv`; `trace-async-tasks` additionally enables `tracing-active-tree` and `tracing-subscriber`.

## State And Persistence Behavior
No runtime state is directly managed here. Feature selection affects allocator behavior, instrumentation, failpoint compilation, and engine availability in the compiled binary.

## Dependencies And Integration Points
The crate depends on `clap`, `crypto`, `server`, `tikv`, `tikv_util`, `toml`, `serde_json`, and optional tracing crates. Build dependencies are `cc` and workspace `time`, inherited through the included build script.

## Risks And Edge Cases
- Feature combinations can significantly change binary behavior and available tests.
- Default test-engine features in a production-looking binary crate require workspace conventions to avoid accidental mismatch.
- Optional allocator features must remain mutually sensible with downstream `server` feature constraints.

## Test Signals
Cargo feature resolution and workspace CI are the primary signals. There are no manifest-local tests, but compile jobs with allocator, failpoints, tracing, and test-engine permutations are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-server/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-server/build.rs -->
# sources/storage-engines/tikv/cmd/tikv-server/build.rs

## Purpose
This build script delegates to the shared command-level build script by including `../build.rs`.

## Important APIs, Types, And Functions
The only active statement is `include!("../build.rs");`, so all build-time logic is centralized one directory up.

## Control Flow
During Cargo build, Rust expands the included build script contents as if they were in this file. That keeps `tikv-server` aligned with sibling command crates that share version/build metadata behavior.

## State And Persistence Behavior
Any emitted `cargo:` directives, environment-derived build metadata, or generated artifacts come from the included script, not from local logic.

## Dependencies And Integration Points
This file relies on the existence and compatibility of `cmd/build.rs` and the build dependencies declared in `Cargo.toml`.

## Risks And Edge Cases
The indirection makes local behavior invisible unless the included file is inspected. A path move or divergent binary-specific build need would require changing this include pattern.

## Test Signals
Compile/build-script execution in CI is the test signal. There are no direct unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-server/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-server/src/main.rs -->
# sources/storage-engines/tikv/cmd/tikv-server/src/main.rs

## Purpose
`tikv-server/src/main.rs` is the production TiKV server entrypoint. It handles early FIPS setup, version metadata, CLI parsing, config loading/overrides/checking, logging, memory initialization, optional async tracing, and dispatch to the correct server implementation by storage engine type.

## Important APIs, Types, And Functions
- `main()` is the only function.
- CLI options include config path, config check/info, log level/file, listen and advertise addresses, status addresses, data directory, capacity, PD endpoints, labels, sample config printing, and a hidden metrics push address.
- It uses `TikvConfig::from_file`, `server::setup::overwrite_config_with_cmd_args`, `logger_compatible_adjust`, `validate_and_persist_config`, `ensure_no_unrecognized_config`, `to_flatten_config_info`, `initial_logger`, and `config.storage.validate_engine_type`.
- Runtime launch calls `server::server::run_tikv` for `EngineType::RaftKv` and `server::server2::run_tikv` for `EngineType::RaftKv2`.

## Control Flow
The entrypoint enables FIPS immediately, builds version strings, defines clap arguments, and handles `--print-sample-config` before loading any user config. It records unrecognized config keys only for `--config-check`. After command-line overrides and logger compatibility adjustment, `--config-check` validates and exits, while `--config-info json` prints flattened config metadata and exits. Normal startup validates storage engine type, optionally initializes async-backtrace tracing, initializes logging, logs version/FIPS status, initializes memory settings, creates a service event channel, and starts the selected server implementation.

## State And Persistence Behavior
The server process will own all TiKV persistent state after `run_tikv`, but this file itself only reads config and may persist validated config via `validate_and_persist_config` in config-check mode. It initializes global logger, memory settings, optional tracing subscriber, and service event channel.

## Dependencies And Integration Points
This entrypoint is a coordinator for the `server` and `tikv` crates. It integrates with Clap, FIPS crypto, serde_json config-info output, TiKV config validation, memory initialization, and storage-engine-specific server modules.

## Risks And Edge Cases
- Panics on invalid config file loading are intentional but can be abrupt.
- `config-info` only accepts JSON and exits before runtime validation beyond loading/overrides.
- Engine-type validation must happen before server startup because it can adjust engine type.
- Optional tracing is compile-time feature gated; missing feature means no active-tree layer.

## Test Signals
Server startup integration tests and config validation tests provide coverage. CLI paths worth testing include sample config, config check with unknown keys, config-info JSON, engine type validation, and command-line override precedence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-server/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/codecov.yml -->
# sources/storage-engines/tikv/codecov.yml

## Purpose
`codecov.yml` configures Codecov reporting thresholds, comment layout, flag carryforward, and ignored paths for the TiKV source tree.

## Important APIs, Types, And Functions
This is YAML configuration. It sets coverage precision to 4, rounds down, displays a `65...90` range, and uses automatic project/patch targets with a 3% threshold. It also defines default flag-management rules requiring 85% project and patch coverage for flags.

## Control Flow
Codecov consumes this file during coverage upload/reporting. Pull request comments use `header, diff, flags`, default behavior, and do not require changes to post.

## State And Persistence Behavior
No runtime state is affected. The file affects CI status interpretation and PR feedback.

## Dependencies And Integration Points
It integrates with Codecov CI uploads and path layout. Ignored paths include integration tests/tools, fuzz cases, test components, component test crates, and component-local `tests` directories.

## Risks And Edge Cases
- Ignoring test directories can make source coverage easier to interpret but hides coverage of test utilities.
- Automatic targets with thresholds may allow coverage drops within 3%.
- Carryforward can mask missing uploads for a flag if not monitored separately.

## Test Signals
The signal is Codecov status output in CI. Changes to source layout should be checked against the ignore globs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/Cargo.toml -->
# sources/storage-engines/tikv/components/api_version/Cargo.toml

## Purpose
This manifest defines the `api_version` component crate, which centralizes API-version-specific key/value encoding behavior for TiKV raw KV, TTL, API V2, and keyspace handling.

## Important APIs, Types, And Functions
The only local feature is `testexport`, used to expose test-only client tags. Dependencies include `bitflags`, `codec`, `engine_traits`, `kvproto`, `log_wrappers`, `match-template`, `tikv_util`, and `txn_types`; `panic_hook` is used in tests.

## Control Flow
Cargo uses the manifest to compile the crate and enable optional test exports. The crate itself is consumed by storage, backup, coprocessor, config, GC, debug, and test-storage components.

## State And Persistence Behavior
The manifest has no runtime state, but versioned encoding code compiled from this crate determines persistent key and value formats.

## Dependencies And Integration Points
Workspace dependencies ensure the encoding crate shares TiKV’s protobuf, transaction key, codec, and engine error types. `match-template` supports API-version dispatch macros.

## Risks And Edge Cases
Changing dependencies or features can affect broad storage compatibility. Since this crate defines persistent wire/storage encodings, semver-looking changes must be treated as data-format changes.

## Test Signals
The crate has extensive unit tests in `src/lib.rs`, `src/api_v2.rs`, and `src/keyspace.rs`. Build jobs with and without `testexport` are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/api_v1.rs -->
# sources/storage-engines/tikv/components/api_version/src/api_v1.rs

## Purpose
`api_v1.rs` implements the `KvFormat` contract for legacy API V1 raw KV. V1 stores raw keys and values without API-version-specific prefixes, TTL metadata, or delete metadata.

## Important APIs, Types, And Functions
- `impl KvFormat for ApiV1` sets `TAG = ApiVersion::V1`, `CLIENT_TAG = V1` in tests, and `IS_TTL_ENABLED = false`.
- `parse_key_mode` and `parse_range_mode` return `KeyMode::Unknown`.
- `decode_raw_value`, `encode_raw_value`, and `encode_raw_value_owned` pass user bytes through unchanged.
- `convert_raw_encoded_key_version_from` and `convert_raw_user_key_range_version_from` allow V1/V1ttl sources and reject V2 sources.

## Control Flow
All operations are direct pass-throughs except conversion, which matches on source API version. V2-to-V1 conversion is explicitly unsupported because V2 carries keyspace/prefix semantics that cannot be blindly dropped.

## State And Persistence Behavior
This defines the legacy persistent representation: raw key bytes are encoded keys, and raw value bytes are stored as user values. No TTL or deletion metadata is represented.

## Dependencies And Integration Points
It implements trait definitions from `lib.rs`, uses `txn_types::Key`, `kvproto::ApiVersion`, and `tikv_util::box_err` for conversion errors. It is dispatched through `dispatch_api_version!` throughout TiKV.

## Risks And Edge Cases
- V1 cannot infer raw/txn/TiDB mode from key prefixes.
- Conversions from V2 are rejected; callers must handle migration/backup compatibility explicitly.
- `RawValue.is_delete` and `expire_ts` are ignored by V1 encoding, so callers must not pass metadata expecting persistence.

## Test Signals
Tests in `lib.rs` cover V1 parse behavior, value encode/decode identity, raw key identity, value conversion involving V1, and rejection paths through dispatch macros.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/api_v1.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/api_v1ttl.rs -->
# sources/storage-engines/tikv/components/api_version/src/api_v1ttl.rs

## Purpose
`api_v1ttl.rs` implements `KvFormat` for API V1 with RawKV TTL. It preserves V1 key layout but appends an 8-byte expiration timestamp to every raw value.

## Important APIs, Types, And Functions
- `impl KvFormat for ApiV1Ttl` sets `TAG = V1ttl`, test `CLIENT_TAG = V1`, and `IS_TTL_ENABLED = true`.
- `parse_key_mode` and `parse_range_mode` always return `KeyMode::Raw` because txnkv is disabled in V1TTL.
- `decode_raw_value` splits the last 8 bytes as big-endian/u64 codec TTL, mapping zero to `None`.
- `encode_raw_value` and `encode_raw_value_owned` append `expire_ts.unwrap_or(0)`.
- Key and range conversion allows V1/V1ttl sources and rejects V2.

## Control Flow
Decoding validates that at least 8 bytes exist, decodes the TTL suffix, and returns the prefix as the user value. Encoding reserves/appends exactly one u64. Owned encoding mutates the user buffer to reduce allocation.

## State And Persistence Behavior
Values persist as `user_value || expire_ts_u64`; expiration timestamp zero represents no TTL. Delete metadata is not persisted in this format.

## Dependencies And Integration Points
The implementation uses TiKV codec number helpers, `engine_traits::Result`, `tikv_util::box_err`, and the shared `KvFormat`/`RawValue` types. It is used where storage config enables API V1 TTL compatibility.

## Risks And Edge Cases
- Any stored value shorter than 8 bytes is invalid in V1TTL.
- A caller setting `is_delete` loses that flag on encode.
- V2 conversion rejection must be surfaced by backup/import or migration callers.

## Test Signals
`lib.rs` tests cover V1TTL parse mode, no-meta and TTL value encoding, decode errors for too-short values, raw key identity, and value conversions to/from other versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/api_v1ttl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/api_v2.rs -->
# sources/storage-engines/tikv/components/api_version/src/api_v2.rs

## Purpose
`api_v2.rs` implements API V2 key/value format. V2 separates raw, transactional, and TiDB-compatible key modes by prefixes, reserves a 3-byte keyspace id, memcomparable-encodes raw keys, optionally appends timestamps, and stores value metadata flags for TTL and logical deletion.

## Important APIs, Types, And Functions
- Prefix constants: raw `b'r'`, txn `b'x'`, TiDB meta `b'm'`, TiDB table `b't'`, default keyspace `[0,0,0]`, and default keyspace end `[0,0,1]`.
- `TIDB_RANGES` and `TIDB_RANGES_COMPLEMENT` describe TiDB-compatible key ranges.
- `ValueMeta` bitflags define `EXPIRE_TS` and `DELETE_FLAG`.
- `impl KvFormat for ApiV2` implements mode parsing, raw value encode/decode, raw key encode/decode, and V1/V1ttl-to-V2 conversion.
- `ApiV2::append_ts_on_encoded_bytes`, `decode_ts_from`, `split_ts`, `add_prefix`, `get_rawkv_range`, and `ENCODED_LOGICAL_DELETE` are helper APIs.

## Control Flow
Key-mode parsing reads the first byte. Range-mode parsing only succeeds when bounded start/end share a mode prefix or use the special exclusive end of `prefix + 1`. Value decoding removes the final flag byte, optionally removes an 8-byte expire timestamp, and returns delete/TTL metadata. Raw key encoding memcomparable-encodes the user key and optionally appends a descending timestamp. Conversion from V1/V1ttl adds raw prefix plus default keyspace before encoding.

## State And Persistence Behavior
V2 persistent keys are memcomparable encoded and can carry MVCC-like raw timestamps. Timestamp zero is invalid for raw MVCC because such entries cannot be retrieved correctly. V2 values always end in a metadata byte; TTL and logical deletion are durable flags.

## Dependencies And Integration Points
This file depends on `codec::byte::MemComparableByteCodec`, TiKV byte/number codecs, `txn_types::Key` and `TimeStamp`, shared `KvFormat`, and API-version dispatch. It is integrated by backup, GC worker, server storage, coprocessor, config validation, and keyspace parsing.

## Risks And Edge Cases
- Several validity checks are `debug_assert!`; invalid encoded keys can panic in tests but may rely on upstream validation in release builds.
- API V2 range parsing returns `Unknown` for unbounded or cross-prefix ranges, requiring callers to split ranges correctly.
- Conversion from V1 empty end key maps to default keyspace end; mistakes here can leak across keyspace boundaries.
- Logical deletion is represented as an encoded one-byte value `[DELETE_FLAG]`, so consumers must decode values rather than compare raw bytes casually.

## Test Signals
Inline tests cover invalid key decoding, invalid timestamp append, timestamp splitting, timestamp decoding, append-ts behavior, and logical delete encoding. `lib.rs` adds parse, range, raw key/value identity, conversion, TTL, metadata, and decode-error coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/api_v2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/keyspace.rs -->
# sources/storage-engines/tikv/components/api_version/src/keyspace.rs

## Purpose
`keyspace.rs` adds keyspace-aware KV entry handling on top of API-version formats. V1/V1TTL have no keyspace prefix; API V2 parses a 3-byte keyspace id following the mode prefix and exposes user keys without that prefix.

## Important APIs, Types, And Functions
- `KvPairEntry` abstracts key/value/optional commit-ts access and provides `kv()`.
- `Keyspace` trait defines `make_kv_pair` and `parse_keyspace`.
- `KeyspaceId(u32)` wraps parsed keyspace identifiers.
- V1 and V1TTL `Keyspace` impls pass entries through and return `(None, key)`.
- V2 `Keyspace` impl returns `KeyspaceKv`, requiring valid raw or txn V2 keys with at least 4 prefix bytes.
- `KeyspaceKv` stores full encoded key, value, commit timestamp, and keyspace id while exposing `key()` without the first four bytes.

## Control Flow
`ApiV2::parse_keyspace` first delegates to `ApiV2::parse_key_mode`; only raw and txn keys are accepted. It rejects too-short or non-V2 data keys, builds a u32 from the 3 keyspace bytes, and returns the remaining user key slice. `make_kv_pair` parses the keyspace and stores it alongside the original tuple.

## State And Persistence Behavior
For V2, keyspace is persisted in the first four bytes of the data key: one mode byte plus three id bytes. `KeyspaceKv` preserves the original full key internally but hides the keyspace prefix from `KvPairEntry::key`.

## Dependencies And Integration Points
The module depends on `engine_traits::Result/Error`, `tikv_util::box_err`, `log_wrappers`, and API-version types. It is used by coprocessor/checksum/analyze and other components that need keyspace-stripped iteration while retaining keyspace identity.

## Risks And Edge Cases
- `ApiV2::make_kv_pair` unwraps `keyspace` after parse, relying on V2 parse always returning `Some`.
- `KeyspaceKv` equality against tuple compares exposed key/value/commit-ts, while equality against another `KeyspaceKv` compares full keys; this distinction is intentional but easy to misunderstand.
- Only raw and txn V2 keys are accepted; TiDB mode keys return errors for keyspace parsing.

## Test Signals
Unit tests cover V1/V1TTL no-keyspace behavior, valid V2 keyspace parsing for raw and txn prefixes, multi-byte ids, and error cases for missing/invalid prefixes or too-short keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/keyspace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/lib.rs -->
# sources/storage-engines/tikv/components/api_version/src/lib.rs

## Purpose
`lib.rs` defines the public API-version abstraction for TiKV key/value formats. It exposes concrete marker types, the `KvFormat` trait, dispatch/test macros, key-mode classification, and the shared `RawValue` metadata struct.

## Important APIs, Types, And Functions
- Modules: private `api_v1`, `api_v1ttl`; public `api_v2` and `keyspace`.
- `KvFormat` defines version tag constants, key/range mode parsing, raw value encode/decode, raw key encode/decode, cross-version key/range/value conversion, and default V1-style key behavior.
- Marker structs: `ApiV1`, `ApiV1Ttl`, `ApiV2`.
- Macros: `test_kv_format_impl!`, `match_template_api_version!`, and `dispatch_api_version!`.
- `KeyMode` distinguishes Raw, Txn, Tidb, and Unknown.
- `RawValue<T>` carries user value, optional expiration timestamp, and logical delete flag, with `is_valid` and `is_ttl_expired` helpers.

## Control Flow
Callers usually dispatch from a runtime `kvproto::ApiVersion` to a concrete zero-sized type with `dispatch_api_version!`, then call trait methods statically. Default raw key methods are V1/V1TTL pass-throughs; API V2 overrides them. `convert_raw_encoded_value_version_from` decodes with the source API and re-encodes with the destination API.

## State And Persistence Behavior
This crate defines durable key/value encodings. `RawValue` validity combines logical deletion and TTL expiration. API V1 stores plain values, V1TTL stores an appended expiration timestamp, and V2 stores metadata flags plus optional TTL and delete state.

## Dependencies And Integration Points
The crate integrates with `kvproto::kvrpcpb::ApiVersion`, `txn_types::Key/TimeStamp`, `engine_traits::Result`, keyspace support, and `match-template` macro expansion. It is a foundational dependency for storage, backup/restore, GC, coprocessor, server, config validation, and tests.

## Risks And Edge Cases
- Persistent-format compatibility depends on the trait implementations remaining stable.
- `RawValue::is_valid` uses bitwise `&` on booleans; result is correct but both sides always evaluate.
- Dispatch macros generate match arms over known API versions; adding a new version requires updating macro templates and tests.
- V2 conversions are asymmetric: V1/V1TTL can convert to V2 for raw data, while V2-to-V1 key conversion is rejected in V1 files.

## Test Signals
This file has broad tests for parse behavior, range mode inference, value encoding across all versions, TTL and delete metadata, decode errors, validity checks, raw key encoding/decoding, raw key conversion to V2, raw value conversion among versions, and raw user-key range conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/api_version/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/Cargo.toml -->
# sources/storage-engines/tikv/components/backup-stream/Cargo.toml

## Purpose
This manifest defines the `backup-stream` component crate, which implements TiKV log backup/backup-stream services, metadata, routing, checkpointing, event loading, and integration tests.

## Important APIs, Types, And Functions
Features include default test engines, failpoints, OpenSSL vendoring for macOS/grpcio test builds, and `backup-stream-debug`. It declares integration and failpoint test targets. Dependencies cover async compression, gRPC/protobuf, external storage, encryption, engine traits/RocksDB, PD client, online config, metrics, raft/raftstore, resolved-ts, Tokio, tracing, UUID, and TiKV core crates.

## Control Flow
Cargo uses the manifest to compile the backup-stream library and its tests. The failpoint test target only builds when the `failpoints` feature is enabled.

## State And Persistence Behavior
The manifest has no runtime state, but selected features affect compiled failpoints, engine implementations, TLS/OpenSSL linkage, and available test suites.

## Dependencies And Integration Points
The crate sits at a high-integration point: storage engines, PD metadata, external storage backends, encryption, raftstore, online config, metrics, and server components all meet here. Server modules instantiate backup-stream endpoint/router/config manager.

## Risks And Edge Cases
- Large dependency surface increases build-feature interaction risk.
- Failpoint and vendored OpenSSL features change test/runtime behavior.
- Default test-engine features must stay aligned with workspace engine abstractions.

## Test Signals
The manifest declares `integration` and `failpoints` test suites. Compile coverage across default, failpoints, and OpenSSL-vendored configurations is important.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/checkpoint_manager.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/checkpoint_manager.rs

## Purpose
`checkpoint_manager.rs` tracks per-region backup-stream flush checkpoints, freezes resolved timestamps around flush boundaries, notifies subscribers of flush events, serves checkpoint queries, and implements flush observers for PD service safepoints and checkpoint V3 metadata integration.

## Important APIs, Types, And Functions
- `CheckpointManager` stores `checkpoint_ts`, `frozen_resolved_ts`, `resolved_ts`, and an optional subscription-manager sender.
- `SubscriptionManager` owns gRPC/server-stream subscribers and processes `SubscriptionOp::{Add, Emit, Inspect}`.
- `GetCheckpointResult` returns `Ok`, `NotFound` with a not-leader-style protobuf error, or `EpochNotMatch`.
- `RegionIdWithVersion` and `LastFlushTsOfRegion` identify/query checkpoint state.
- `FlushObserver` defines async hooks `before`, `after`, and optional `rewrite_resolved_ts`.
- `BasicFlushObserver` updates a PD service safe point and metrics after a flush.
- `CheckpointV3FlushObserver` sends region checkpoint flush tasks, reads global checkpoint metadata, caches it per task, and delegates PD safepoint updates to a baseline observer.

## Control Flow
Resolved-ts updates enter through `resolve_regions`, which updates `resolved_ts` by region id. Before a data flush, `freeze` moves `resolved_ts` into `frozen_resolved_ts` so later incoming data cannot advance the currently flushing checkpoint. After files are fully written, `flush_and_notify` optionally applies final `last_dive` checkpoints, replaces durable `checkpoint_ts` with the frozen map, and emits `FlushEvent`s to subscribers. `get_from_region` validates both region id presence and epoch version.

The subscription manager runs an async loop. New subscribers are stored under generated UUIDs. Event emission chunks responses in groups of 1024 events, feeds and flushes each sink, and removes subscribers whose stream errors. Adding a subscriber also emits current checkpoint state as initial data.

`update_ts` only replaces existing entries when the incoming region epoch is newer, or the same epoch has a newer checkpoint. Older checkpoints are logged but ignored unless paired with newer epoch behavior.

## State And Persistence Behavior
The manager state is in memory. It represents flushed external-storage durability, not raw resolved-ts progress. PD service safepoints written by `BasicFlushObserver` persist outside the process with a 2-hour TTL at `rts - 1`. Checkpoint V3 observer reads global checkpoint metadata through `MetadataClient` and schedules region checkpoint flush operations through the backup-stream task scheduler.

## Dependencies And Integration Points
The file integrates with `endpoint.rs` for checkpoint manager ownership and observer creation, `subscription_track::ResolveResult`, backup-stream `Task` and `RegionCheckpointOperation`, metadata store/client traits, PD client, grpcio streaming sinks, `kvproto` error/logbackup/metapb messages, metrics, tracing instrumentation, and `tikv_util` scheduler/logging helpers.

## Risks And Edge Cases
- Subscription channel capacity is finite; `notify` drops events when `try_send` fails.
- `add_subscriber` sends `Add` before initial `Emit`, so initial events are broadcast through the manager rather than targeted only to the new subscriber.
- `flush_and_notify` replaces `checkpoint_ts` with the frozen set; if no new resolved regions were frozen, previously queryable checkpoints disappear. Tests document this behavior.
- `sync_with_subs_mgr` unwraps `manager_handle` and is test/support oriented.
- `CheckpointV3FlushObserver` caches global checkpoint per task and can become stale unless cache invalidation is handled by task lifecycle.

## Test Signals
Inline tests cover successful subscription notification, subscriber removal on RPC failure, freeze/flush state transitions, checkpoint epoch/version update rules, last-dive override behavior, and PD service safepoint update by `BasicFlushObserver`. Integration references in `endpoint.rs` exercise manager wiring.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/checkpoint_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/config.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/config.rs

## Purpose
`config.rs` provides online configuration management for backup-stream. It stores the current `BackupStreamConfig` and forwards validated changes to the backup-stream endpoint scheduler.

## Important APIs, Types, And Functions
- `BackupStreamConfigManager` holds a `Scheduler<Task>` and `Arc<RwLock<BackupStreamConfig>>`.
- `BackupStreamConfigManager::new` constructs the manager from scheduler and initial config.
- `impl ConfigManager for BackupStreamConfigManager` implements `dispatch(change)`.

## Control Flow
On config dispatch, the manager logs the change, takes a write lock, applies the `ConfigChange` through `OnlineConfig::update`, validates the resulting config, schedules `Task::ChangeConfig(cfg.clone())`, and returns success.

## State And Persistence Behavior
The current backup-stream config is kept in an `Arc<RwLock<_>>` shared with other components. Applying a change mutates this in-memory config before scheduling the endpoint task. Persistent config storage, if any, is handled by the wider online-config/server system, not this file.

## Dependencies And Integration Points
It integrates with `online_config::{ConfigChange, ConfigManager, OnlineConfig}`, TiKV `BackupStreamConfig`, `tikv_util::worker::Scheduler`, backup-stream endpoint `Task`, and server startup code that registers config managers for backup-stream.

## Risks And Edge Cases
- If `update` succeeds but `validate` fails, the in-memory config has already been mutated unless `OnlineConfig::update` is internally transactional.
- Scheduler failure returns an error after the config lock mutation, possibly leaving local config changed without endpoint application.
- The write lock is held while scheduling, so scheduler backpressure/errors happen inside the critical section.

## Test Signals
Router tests reference `BackupStreamConfigManager` and should cover config-change propagation. Direct unit tests for failed validation and scheduler failure would be useful because of mutation-before-schedule behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/config.rs -->
