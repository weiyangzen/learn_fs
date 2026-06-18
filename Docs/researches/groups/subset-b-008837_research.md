# subset-b-008837 Research Report

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/write_batch.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/write_batch.rs

## Purpose
`write_batch.rs` implements `RegionCacheWriteBatch`, the in-memory-engine write batch used to mirror Raft apply writes into the region cache skiplist. It is the bridge between `engine_traits::Mutable`/`WriteBatch` operations and `RegionCacheMemoryEngine` internals: region preparation, memory admission, write buffering, skiplist insertion with encoded sequence numbers, and eviction when the cache cannot safely accept writes.

## Important APIs, Types, and Functions
- `RegionCacheWriteBatch` tracks `region_cache_status`, buffered entries, savepoints, sequence number, current/prepared/written regions, and accumulated prepare time.
- `prepare_for_region` must be called before writes for each peer delegate. It validates the same region is not prepared non-contiguously, records the previous written region, asks `engine.prepare_for_apply`, and updates `current_region`.
- `set_sequence_number` is one-shot and feeds `write_impl`; `write_opt` errors if no sequence number was set.
- `process_cf_operation` gates puts/deletes by region cache state, engine enablement, and memory quota, evicting on disabled or capacity-reached conditions.
- `RegionCacheWriteBatchEntry` stores cf id, user key, and either `PutValue(Bytes)` or deletion. `write_to_memory` encodes internal keys with `encode_key(key, seq, ValueType)` and inserts into the skiplist CF handle.
- `maybe_compact_lock_cf` schedules `BackgroundTask::CleanLockTombstone` when lock CF modification bytes exceed the 16 MiB threshold.

## Control Flow
Normal flow is `prepare_for_region` -> `put_cf`/`delete_cf`/`delete_range_cf` -> `set_sequence_number` -> `write`. Each mutation either appends an entry to `buffer` or evicts the current region and stops buffering for it. `write_impl` records the last region, drains `buffer`, counts operations per CF, writes entries with monotonically increasing RocksDB sequence numbers, clears in-being-written flags, updates lock modification bytes, and records histograms. Savepoints only track buffer length; rollback truncates buffered entries.

## State and Persistence Behavior
Data is not persisted by this file; it is written to the memory engine's skiplist and must stay consistent with the disk engine sequence number supplied by RocksDB apply. Memory is pre-acquired based on encoded key/value size, then real skiplist/node overhead is charged through `InternalBytes` and memory-controller ownership. Regions can remain in manager state while loading or active; eviction removes their cached range asynchronously. `clear` is important because an empty batch that was prepared but never written still needs to clear region in-written flags.

## Dependencies and Integration Points
The file depends on `engine_traits` write traits and CF names, `kvproto::metapb::Region`, crossbeam epoch guards, the memory controller, region manager, background worker, metrics, and TiKV failpoints. It integrates with RocksDB sequence numbering, in-memory-engine snapshot visibility, lock tombstone cleanup, and batch-system apply ordering assumptions.

## Risks
The code relies on the invariant that a region is not prepared, interrupted by another region, then prepared again in the same batch-system round; violation panics. Memory accounting intentionally excludes skiplist node overhead during admission, so real usage can exceed capacity after flush. Missing `clear_written_regions` would block range deletion/eviction. Delete range evicts whole regions rather than deleting keys, so callers must understand the coarser behavior. `should_write_to_engine` is unimplemented because this batch is not a normal disk batch.

## Test Signals
Inline tests cover skiplist writes, savepoints, write-clear-delete cycles, pending-region prepare behavior, memory-controller eviction, config disable/enable behavior, outdated pending region replacement, and dirty data during prepare. Failpoint tests in this subset add race coverage for eviction, loading, GC, and delete-range ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/mod.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/mod.rs

## Purpose
This module is the failpoint test entry for the in-memory engine component. It only declares `mod test_memory_engine;`, making the detailed failpoint suite in `test_memory_engine.rs` part of the test crate.

## Important APIs, Types, and Functions
There are no local APIs beyond the module declaration. Its important behavior is compile-time test discovery: Rust includes the sibling test module when failpoint tests are built.

## Control Flow
The file has no runtime control flow. Test execution is driven by the functions declared in `test_memory_engine.rs`.

## State and Persistence Behavior
No state is kept here.

## Dependencies and Integration Points
The integration point is the Rust module system and the in-memory-engine failpoint test target.

## Risks
Removing or renaming this declaration silently drops the whole failpoint suite from the test build. Because the file is tiny, mistakes are likely to be omission or incorrect module path errors.

## Test Signals
The file's test signal is indirect: all tests in the included module depend on this declaration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/test_memory_engine.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/test_memory_engine.rs

## Purpose
This file exercises in-memory-engine behavior under injected timing and failure conditions. It targets the parts that are difficult to validate with straight-line unit tests: disk-engine setup, GC, tombstone cleanup, snapshot load/evict races, delete-range scheduling, region split during load, and eviction callbacks.

## Important APIs, Types, and Functions
Tests construct `RegionCacheMemoryEngine` with test configs, attach RocksDB engines via `set_disk_engine`, create regions with `new_region`, write via `engine.write_batch`, and inspect skiplist CF handles. Helpers include `key_exist` for sequence-suffixed skiplist keys and closures that count internal keys in encoded region boundaries. Failpoints such as `ime_set_rocks_engine`, `ime_gc_oldest_seqno`, `ime_on_snapshot_load_finished`, `ime_before_clear_regions_in_being_written`, and `ime_on_delete_range` coordinate racing tasks.

## Control Flow
The tests commonly set failpoint callbacks/channels, prepare engine state, trigger async background work through writes or explicit background tasks, then block on channels or `eventually` polling. Race-oriented tests pause background operations, assert intermediate state, remove failpoints, and assert eventual cleanup or active state. Stream-like flows are not used; synchronization is via sync channels, Tokio channels, and failpoint callbacks.

## State and Persistence Behavior
The tests write both RocksDB data and in-memory skiplist data. They verify that loading filters MVCC history by safe point, GC removes old versions, lock tombstone cleanup keeps versions newer than the snapshot sequence, failed loads remove region metadata, and evictions delete in-memory range data only after active writers leave in-written state. Temporary RocksDB directories isolate persistence per test.

## Dependencies and Integration Points
The file integrates `engine_rocks`, `engine_traits`, `keys`, `txn_types`, Tokio, crossbeam epoch guards, and the in-memory-engine test utilities. It is tightly coupled to background task failpoint names and region manager states such as `Loading`, `Active`, and eviction states.

## Risks
The tests assume failpoint callbacks are reached within short deadlines; timing-sensitive regressions may appear as flakes. Some assertions inspect internal skiplist ordering and counts, so changes to internal key encoding or GC retention rules require test updates. Because many tests pause failpoints, missing cleanup could contaminate later tests if run in-process.

## Test Signals
Coverage is strong for concurrency boundaries: set-disk-engine callback, GC old-version removal, lock tombstone cleanup, eviction overlapping loading ranges, load failure cleanup, delete-range vs write-to-memory serialization, duplicate delete-range scheduling, load with GC safe point, region split before batch loading starts, and async eviction callback ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/test_memory_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/into_other/Cargo.toml -->
# sources/storage-engines/tikv/components/into_other/Cargo.toml

## Purpose
This manifest defines the private `into_other` crate, a small conversion crate used to avoid direct dependency cycles between error-producing crates and consumers that need protocol or Raft errors.

## Important APIs, Types, and Functions
The manifest exposes no code itself. It names the crate, sets Rust 2021 edition, marks it unpublished, and declares dependencies on `engine_traits`, `kvproto`, and `raft`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies and Integration Points
The dependency set matches `src/lib.rs`: `engine_traits::Error` is converted into `kvproto::errorpb::Error` and `raft::Error`.

## Risks
The crate's reason to exist is dependency separation. Adding broad dependencies here could reintroduce coupling or cycles in TiKV's component graph.

## Test Signals
There are no local tests in the manifest. Compile success of downstream crates is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/into_other/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/into_other/src/lib.rs -->
# sources/storage-engines/tikv/components/into_other/src/lib.rs

## Purpose
This crate provides conversions between error types that cannot depend directly on one another. It is primarily an adapter from `engine_traits::Error` into protobuf PD/store errors and Raft storage errors.

## Important APIs, Types, and Functions
- `IntoOther<O>` is a local conversion trait with `into_other`.
- `impl IntoOther<ProtoError> for EngineTraitsError` creates a default `errorpb::Error`, stores the formatted message, and fills `key_not_in_region` fields for `EngineTraitsError::NotInRange`.
- `impl IntoOther<RaftError> for EngineTraitsError` wraps the engine error in `raft::StorageError::Other`.
- `into_other<F, T>` is a generic helper for callers that want function-style conversion.

## Control Flow
The conversion is a simple match on the consumed error. `NotInRange` gets structured protobuf fields; all other engine errors only produce a message.

## State and Persistence Behavior
No state is persisted. The source error is consumed.

## Dependencies and Integration Points
The file integrates `engine_traits`, `kvproto::errorpb`, and `raft`. It is useful at boundaries where storage errors must be sent to clients or returned through Raft APIs without creating direct dependencies in the original error crate.

## Risks
Only `NotInRange` preserves structured details in `ProtoError`; other variants lose type information except for the message. Because the conversion consumes the error, future code must not need to inspect it afterwards. Formatting-sensitive messages can become wire-visible.

## Test Signals
No local tests are present. Behavior is covered indirectly wherever engine errors are converted for raftstore or API responses.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/into_other/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/keys/Cargo.toml -->
# sources/storage-engines/tikv/components/keys/Cargo.toml

## Purpose
This manifest defines the private `keys` crate, which centralizes TiKV key-prefix constants, region/raft key encoding helpers, data key helpers, and prefix rewriting utilities.

## Important APIs, Types, and Functions
The manifest declares runtime dependencies on `byteorder`, `kvproto`, `log_wrappers`, `thiserror`, `tikv_alloc`, and `tikv_util`; dev tests depend on `panic_hook`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest itself has no state, but it supports code that defines persisted RocksDB key layouts.

## Dependencies and Integration Points
`byteorder` is required for big-endian sortable ids, `log_wrappers` redacts/hex-encodes keys in errors, and `kvproto` supplies region metadata.

## Risks
Changing dependency versions here can affect low-level storage key formatting and test behavior. Because this crate sits on a performance-critical path, adding heavy dependencies should be avoided.

## Test Signals
Tests are in `src/lib.rs` and `src/rewrite.rs`; the manifest has no independent tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/keys/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/keys/src/lib.rs -->
# sources/storage-engines/tikv/components/keys/src/lib.rs

## Purpose
`keys/src/lib.rs` defines TiKV's common key-space layout helpers. It builds and decodes local keys, raft log keys, region metadata keys, and data keys while preserving RocksDB lexicographic ordering.

## Important APIs, Types, and Functions
- Constants define key-space partitions: local prefix `0x01`, region raft/meta prefixes, raft/apply/snapshot suffixes, and data prefix `b'z'`.
- `raft_log_key`, `raft_state_key`, `apply_state_key`, `snapshot_raft_state_key`, and prefix helpers construct fixed-width big-endian keys.
- `raft_log_index`, `decode_raft_log_key`, `decode_raft_key`, `decode_region_raft_key`, and `decode_region_meta_key` validate and decode persisted keys.
- `data_key`, `data_key_with_buffer`, `data_end_key`, `origin_key`, and `origin_end_key` translate raw user keys into TiKV encoded data-space keys.
- `enc_start_key` and `enc_end_key` convert initialized `Region` bounds to encoded data-space bounds and assert peers exist.
- `next_key` computes the immediate lexicographic successor, returning empty for no successor.
- `Error` reports invalid raft or region keys using `log_wrappers::Value`.

## Control Flow
Encoding functions allocate fixed arrays or vectors and write region ids/log indexes with big-endian order. Decoders first validate exact lengths, prefixes, and suffixes, then read ids. Data-key functions prepend or strip `DATA_PREFIX`, with empty end keys mapped to `DATA_MAX_KEY`.

## State and Persistence Behavior
The functions define persisted RocksDB key formats. Big-endian region ids and log indexes preserve sort order. `data_end_key` maps an unbounded raw end key to the exclusive upper data boundary, and `origin_end_key` reverses that mapping.

## Dependencies and Integration Points
The crate is used across raftstore, engine, backup/import, and region-routing code that needs stable keys. It depends on `kvproto::metapb::Region`, `byteorder`, and logging wrappers for safe key display.

## Risks
Any incompatible change to constants or fixed-width layout can make existing RocksDB data unreadable. `origin_key` and region boundary helpers assert on invalid input and can panic if callers pass unencoded keys or uninitialized regions. `next_key` returning empty means "unbounded/no successor" in several range contexts, so consumers must distinguish it from a real empty key.

## Test Signals
Inline tests verify region key prefixing, lexicographic sort order, raft log decoding errors, data key validation, initialized-region assertions via `panic_hook`, and end-key encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/keys/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/keys/src/rewrite.rs -->
# sources/storage-engines/tikv/components/keys/src/rewrite.rs

## Purpose
`rewrite.rs` rewrites key prefixes and range bounds, mainly for features that remap data from one logical prefix to another while preserving range semantics.

## Important APIs, Types, and Functions
- `WrongPrefix` marks a source key or bound that cannot be rewritten.
- `encode_bound` applies TiKV byte encoding to included/excluded `Bound<Vec<u8>>` keys.
- `rewrite_prefix` replaces `old_prefix` with `new_prefix` when `src` starts with `old_prefix`.
- `rewrite_prefix_of_end_key` also handles the special case where the source end key is exactly the successor of `old_prefix`, mapping it to `next_key(new_prefix)`.
- `rewrite_prefix_of_start_bound` and `rewrite_prefix_of_end_bound` apply these rules to `Bound<&[u8]>`, converting empty-successor end keys to `Unbounded`.

## Control Flow
Start bounds are direct rewrites except that unbounded plus empty old prefix becomes an included new prefix. End bounds use exclusive-end-key semantics: excluded bounds may be successor-expanded, and an empty rewritten end key becomes unbounded.

## State and Persistence Behavior
No state is held. The output vectors may become persisted or used in scans, so correctness depends on retaining inclusive/exclusive boundary semantics after prefix replacement.

## Dependencies and Integration Points
The module uses `tikv_util::codec::bytes::encode_bytes` and `keys::next_key`. It is likely consumed by backup/import/restore or range rewrite paths that need byte-accurate key remapping.

## Risks
End-bound handling is subtle around all-`0xff` prefixes, empty prefixes, and inclusive vs exclusive bounds. Returning `Unbounded` from an empty next key is correct for "no upper bound" but dangerous if callers interpret empty as a normal key. `WrongPrefix` has no payload, so diagnostics must come from caller context.

## Test Signals
Tests cover direct rewrites, wrong prefixes, successor end-key rewrites, all-`0xff` boundary behavior, and full start/end range combinations for included, excluded, and unbounded bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/keys/src/rewrite.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/Cargo.toml -->
# sources/storage-engines/tikv/components/log_wrappers/Cargo.toml

## Purpose
This manifest defines the private `log_wrappers` crate, which provides logging wrappers for third-party types and redacted key/value formatting.

## Important APIs, Types, and Functions
Dependencies include `atomic`, `hex`, `online_config`, `protobuf`, `serde`, `slog`, `slog-term`, `toml`, and `tikv_alloc`. These map directly to redaction state, hex encoding, online-config conversion, protobuf redaction levels, and test logging.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest has no runtime state, but the crate it defines controls process-global logging redaction state.

## Dependencies and Integration Points
`online_config` allows config-driven redaction changes; `protobuf` shares redaction marker semantics with generated protobuf logging; `slog` is TiKV's structured logging stack.

## Risks
Logging code is security-sensitive. Dependency changes that alter redaction parsing or marker formatting could expose user data or break expected log output.

## Test Signals
Tests are in `src/lib.rs` and `src/test_util.rs` support code.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/src/hex.rs -->
# sources/storage-engines/tikv/components/log_wrappers/src/hex.rs

## Purpose
This file re-exports selected functions from the `hex` crate for the `log_wrappers` API.

## Important APIs, Types, and Functions
It publicly re-exports `hex::encode` as `hex_encode` and `hex::encode_upper` as `hex_encode_upper`.

## Control Flow
No local control flow; calls dispatch to the external `hex` crate.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
`log_wrappers::Value` uses `hex_encode_upper` to print keys and values consistently. Other crates can import these helpers through `log_wrappers`.

## Risks
The wrapper fixes naming and casing expectations. Replacing uppercase encoding would change log output and tests.

## Test Signals
The behavior is indirectly tested by `test_log_key` and redaction tests in `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/src/hex.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/src/lib.rs -->
# sources/storage-engines/tikv/components/log_wrappers/src/lib.rs

## Purpose
`log_wrappers` provides `slog::Value` adapters and redaction-aware byte formatting for keys and values. It lets code log display/debug-only types and user data without requiring third-party types to implement `slog::Value`.

## Important APIs, Types, and Functions
- `DisplayValue<T>` and `DebugValue<T>` serialize via `Display` and `Debug`.
- `RedactOption` represents user-configurable redaction: `Off`, `On`, or `Marker`; it implements `Display`, `FromStr`, `TryFrom<ConfigValue>`, `From<RedactOption> for ConfigValue`, and serde serialization/deserialization.
- `set_redact_info_log` stores a process-global `RedactLevel` and also updates protobuf's redaction level.
- `Value<'a>` wraps bytes for key/value logging. As `slog::Value`, `Display`, and `Debug`, it prints uppercase hex, `"?"`, or marker-wrapped uppercase hex depending on redaction state.

## Control Flow
Redaction parsing accepts booleans and selected case variants. Serialization emits booleans for on/off and string `"marker"` for marker mode. `Value` formatting reads the atomic redaction level at formatting time, so a global config update affects subsequent logs immediately.

## State and Persistence Behavior
`REDACT_INFO_LOG` is static process-global state. It is relaxed-atomic because formatting only needs eventual consistency. No data is persisted, but logs emitted before and after changes may use different redaction levels.

## Dependencies and Integration Points
The file integrates with `online_config::ConfigValue`, protobuf atomic redaction flags, serde/TOML config parsing, `slog`, and the local hex re-export. `keys` and many storage components use `Value::key` in error/log messages.

## Risks
Redaction mode is global; tests and runtime config changes must restore desired state to avoid cross-test or cross-module surprises. Accepted strings are asymmetric (`MARKER` accepted, `Marker` rejected), so UI/config layers must match parser behavior. With `Off`, raw user data is hex-encoded but still present in logs.

## Test Signals
Tests validate debug wrapper output with a deterministic logger, uppercase key logging, redaction option parsing/serde conversion, config-value conversion, and output for off/on/marker modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/src/test_util.rs -->
# sources/storage-engines/tikv/components/log_wrappers/src/test_util.rs

## Purpose
This file provides a synchronized in-memory logging buffer for tests that need deterministic `slog` output.

## Important APIs, Types, and Functions
- `SyncLoggerBuffer` wraps `Arc<Mutex<Vec<u8>>>`.
- `new` creates an empty buffer.
- `build_logger` builds a compact `slog::Logger` with a constant `TIME` timestamp.
- `as_string` clones and decodes the buffer as UTF-8.
- `clear` empties buffered bytes.
- The `io::Write` impl appends to the shared byte vector and flushes the vector writer.

## Control Flow
Tests create a buffer, build a logger from a clone, emit logs, and inspect `as_string`. Writes lock the buffer for each append.

## State and Persistence Behavior
State is process-local test memory protected by a mutex. No persistence.

## Dependencies and Integration Points
Used by `log_wrappers` tests. It depends on `slog-term` compact formatting and the `o!` macro imported at crate root.

## Risks
`as_string` panics if log output is not UTF-8, which is fine for current text logs. Mutex poisoning also panics through `unwrap`. The deterministic timestamp means tests should not use this utility to validate real time formatting.

## Test Signals
Its behavior is exercised by `log_wrappers` tests that compare exact log lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/log_wrappers/src/test_util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/memory_trace_macros/Cargo.toml -->
# sources/storage-engines/tikv/components/memory_trace_macros/Cargo.toml

## Purpose
This manifest defines `memory_trace_macros`, a proc-macro crate for deriving memory tracing helper methods.

## Important APIs, Types, and Functions
The manifest marks the library as `proc-macro = true` and depends on `quote` and `syn` with full AST parsing and extra traits.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
The generated code references `tikv_alloc::trace::TraceEvent`, but the macro crate itself only needs `syn` and `quote`.

## Risks
Proc-macro crates are compiled and run at build time. Dependency changes can affect generated code compatibility and compiler error quality.

## Test Signals
No local tests are present in the manifest.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/memory_trace_macros/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/memory_trace_macros/src/lib.rs -->
# sources/storage-engines/tikv/components/memory_trace_macros/src/lib.rs

## Purpose
This proc-macro implements `#[derive(MemoryTraceHelper)]`, adding `reset` and `sum` methods to structs whose named fields represent memory counters.

## Important APIs, Types, and Functions
- `memory_trace_reset_derive` parses the derive input and emits an inherent impl for the target type.
- For named structs, generated `reset(&mut self, rhs: Self)` sums old and new field values, assigns all fields from `rhs`, and returns `Some(TraceEvent::Sub(delta))`, `Some(TraceEvent::Add(delta))`, or `None`.
- Generated `sum(&self)` returns the sum of all fields.

## Control Flow
The macro accepts only structs with named fields. It iterates over fields twice: once for reset assignment/delta generation and once for sum generation. Non-named fields or non-struct input use `unimplemented!()`, producing a build-time panic rather than a structured compile error.

## State and Persistence Behavior
The generated `reset` mutates the receiver by replacing every field with `rhs` values. It does not persist state outside the receiver.

## Dependencies and Integration Points
Generated code imports `tikv_alloc::trace::TraceEvent` and `std::cmp::Ordering`. The macro is intended for TiKV memory trace structs whose fields are `usize`; the code assumes addition/subtraction is valid for all selected fields.

## Risks
The macro does not type-check fields itself; non-`usize` fields fail later in generated code. Unsupported input shapes panic during macro expansion. The advertised `attributes(name)` is accepted by the derive declaration but not inspected in the implementation, so consumers should not expect field renaming behavior here.

## Test Signals
No local tests are present. Compile-time use sites provide coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/memory_trace_macros/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/Cargo.toml -->
# sources/storage-engines/tikv/components/online_config/Cargo.toml

## Purpose
This manifest defines `online_config`, the runtime trait and value crate for TiKV online configuration updates.

## Important APIs, Types, and Functions
Runtime dependencies are `chrono`, the local `online_config_derive` proc macro, and `serde`; tests use `toml`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest has no state, but the crate supports mutable runtime configuration state in consumers.

## Dependencies and Integration Points
`chrono` supports schedule/time config values; `serde` supports encoder output for config serialization; `online_config_derive` generates trait implementations.

## Risks
The crate exports the derive macro, so manifest path/version changes can break many config structs. Serialization compatibility matters for config files and admin tooling.

## Test Signals
Tests are in `src/lib.rs` and cover generated online config behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/online_config_derive/Cargo.toml -->
# sources/storage-engines/tikv/components/online_config/online_config_derive/Cargo.toml

## Purpose
This manifest defines the `online_config_derive` proc-macro crate that generates `OnlineConfig` implementations.

## Important APIs, Types, and Functions
It marks the library as `proc-macro = true` and depends on `proc-macro2`, `quote`, and `syn` with `extra-traits` and `full`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
The crate is consumed by `online_config`, which re-exports the derive macro for TiKV config structs.

## Risks
Proc-macro dependency changes can alter generated syntax or compiler diagnostics. The derive assumes the runtime crate is named `online_config`, so renaming/re-exporting patterns are important.

## Test Signals
The generated code is tested through `online_config/src/lib.rs` tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/online_config_derive/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/online_config_derive/src/lib.rs -->
# sources/storage-engines/tikv/components/online_config/online_config_derive/src/lib.rs

## Purpose
This proc macro derives `online_config::OnlineConfig` for named, non-generic structs. It generates diff, update, type-description, and hidden-field-aware encoder code.

## Important APIs, Types, and Functions
- `config` is the `#[proc_macro_derive(OnlineConfig, attributes(online_config))]` entry point.
- `generate_token` validates generics, builds a stable-ish encoder type name with a hash, gathers fields, and emits the trait impl plus encoder struct.
- `update` generates logic for normal fields, `Option<T>` fields, and `#[online_config(submodule)]` fields.
- `diff` generates field-by-field differences as `ConfigChange`.
- `typed` generates a map describing current field value types, using `ConfigValue::Skip` for skipped or hidden fields.
- `encoder` generates a serde-serializable borrowed encoder that omits hidden fields and recursively encodes submodules.
- Attribute parsing recognizes `skip`, `hidden`, and `submodule`.

## Control Flow
The macro only accepts named-field structs without generics or where clauses. Hidden and skip fields are not updated or diffed; hidden fields are also omitted from encoder output. Submodules call `OnlineConfig` recursively. Option fields use `ConfigValue::None` to clear the option, otherwise `TryInto` to set `Some`.

## State and Persistence Behavior
The generated `update` mutates the config instance in place. The generated encoder only borrows the original config and does not own state. The generated type map can be used by config tooling to understand mutable and skipped fields.

## Dependencies and Integration Points
The macro emits references to a crate named `online_config`, serde derives, and `std::convert::TryInto`. It preserves only serde attributes on the generated encoder, which is critical for kebab-case and field rename behavior.

## Risks
The derive is not usable on generic structs or tuple/unit structs. Field names in diffs are Rust field identifiers, not serde-renamed names, while encoder serialization respects serde attributes; callers must not confuse update keys with serialized config keys. `is_option_type` is path-string based and only recognizes common `Option` paths.

## Test Signals
Runtime tests in `online_config` cover updates, skipped fields, submodules, hidden encoder output, optional fields, and enum conversion failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/online_config_derive/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/src/lib.rs -->
# sources/storage-engines/tikv/components/online_config/src/lib.rs

## Purpose
`online_config` defines the runtime data model and trait for comparing, applying, serializing, and describing online configuration changes.

## Important APIs, Types, and Functions
- `ConfigChange = HashMap<String, ConfigValue>`.
- `ConfigValue` represents typed values: duration, size, numeric primitives, bool, string, module, schedule strings, skip, and none.
- `Display`/`Debug` make `ConfigValue` user-visible; `From` impls create values from primitive types and module maps; selected `From<ConfigValue>` impls extract values and panic on mismatches.
- `OnlineConfig<'a>` requires associated `Encoder`, `diff`, `update`, `get_encoder`, and `typed`.
- `ConfigManager` provides a `dispatch(ConfigChange)` hook for applying changes.

## Control Flow
Most runtime behavior is supplied by the derive macro. The trait contract is that `diff` produces a `ConfigChange`, `update` applies compatible changes, `get_encoder` returns a serde encoder with hidden fields omitted, and `typed` reports field types/skip markers. Tests exercise generated behavior through sample configs.

## State and Persistence Behavior
This crate does not own global state. Consumer configs are mutated in place through `update`; encoders borrow configs for serialization. `ConfigValue::None` is a sentinel for clearing optional fields, while `Skip` marks non-updatable fields in type descriptions.

## Dependencies and Integration Points
The crate re-exports `online_config_derive::*`, uses `chrono` aliases for schedules, and depends on serde for encoder serialization. Many TiKV components use `ConfigManager` implementations to apply runtime config changes.

## Risks
Extractor `From<ConfigValue>` impls panic on type mismatch; safer callers should prefer `TryFrom` where available. `Display` for module/schedule values is debug-like and not a stable machine format. Derived update keys use Rust field names, which may differ from serde names in serialized config files.

## Test Signals
Tests cover update/diff behavior, no-op updates, skipped fields, submodule updates, hidden fields omitted from encoder output, serde output with renamed fields, and enum conversion including invalid values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/online_config/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/panic_hook/Cargo.toml -->
# sources/storage-engines/tikv/components/panic_hook/Cargo.toml

## Purpose
This manifest defines the private `panic_hook` test utility crate.

## Important APIs, Types, and Functions
It sets package metadata only: name, version, edition, unpublished status, and license. There are no runtime dependencies.

## Control Flow
No manifest control flow.

## State and Persistence Behavior
No state in the manifest.

## Dependencies and Integration Points
The crate is used as a dev dependency by low-level crates that need to assert panics without printing stack traces.

## Risks
Because production TiKV uses fatal panics, this crate should remain test-only. Adding it as a production dependency would conflict with its own documentation.

## Test Signals
The manifest has no tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/panic_hook/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/panic_hook/src/lib.rs -->
# sources/storage-engines/tikv/components/panic_hook/src/lib.rs

## Purpose
`panic_hook` is a test-only helper that temporarily mutes panic output and catches unwinds. It keeps tests that intentionally panic from emitting noisy stack traces.

## Important APIs, Types, and Functions
- `mute` installs the custom hook once and marks the current thread as muted.
- `unmute` clears the current thread's muted flag.
- `recover_safe` mutes, runs a closure inside `catch_unwind(AssertUnwindSafe)`, unmutes, and returns the panic result.
- `track_hook` delegates to the original default hook unless the thread-local muted flag is true.

## Control Flow
`initialize` stores the original hook in a leaked raw pointer and installs `track_hook` through `Once`. Muting is thread-local, so only the calling thread suppresses output. `recover_safe` always calls `unmute` after `catch_unwind` returns.

## State and Persistence Behavior
State is global hook installation plus thread-local `MUTED`. The original hook pointer is stored for process lifetime and is not restored. No persistent storage is used.

## Dependencies and Integration Points
Used by tests such as `keys::test_data_key` to verify assertions without noisy panic logs. It depends only on `std::panic`, `Once`, and thread-local storage.

## Risks
The global hook uses `static mut` and raw pointer storage. Although installation is protected by `Once`, this design assumes the original hook remains valid forever. If a closure aborts the process or uses non-unwind panics, `recover_safe` cannot recover. `AssertUnwindSafe` shifts unwind-safety responsibility to the caller.

## Test Signals
No local tests are present; dev-dependency use in other crates validates behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/panic_hook/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/Cargo.toml -->
# sources/storage-engines/tikv/components/pd_client/Cargo.toml

## Purpose
This manifest defines the private `pd_client` crate, TiKV's Placement Driver client abstraction and implementations.

## Important APIs, Types, and Functions
It declares `failpoints` and `testexport` features. Dependencies include `grpcio`, `kvproto`, `security`, `futures`, `tokio`, `tokio-timer`, `yatp`, `txn_types`, `prometheus`, `slog`, `semver`, and several workspace utility crates.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest has no state; the crate it defines maintains PD connections, streams, feature gates, and metrics.

## Dependencies and Integration Points
Dependencies show the crate's role: gRPC/protobuf communication with PD, security/TLS setup, async and legacy future interop, metrics, failpoints, and cluster-version feature gating.

## Risks
The crate sits on critical cluster-control paths. Feature flags expose failpoints and test-only APIs; enabling them incorrectly in production would be risky. Async dependency compatibility matters because this crate bridges futures 0.1, futures 0.3, Tokio, and grpcio.

## Test Signals
Tests are distributed across modules not all in this subset; manifests themselves are compile-time checked.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/client.rs -->
# sources/storage-engines/tikv/components/pd_client/src/client.rs

## Purpose
`client.rs` implements the original `RpcClient` for the `pd_client::PdClient` trait and `MetaStorageClient`. It owns cluster id, a reconnecting shared PD `Client`, and a monitor pool for periodic metadata refresh and TSO stream repair.

## Important APIs, Types, and Functions
- `RpcClient::new`/`new_async` validate PD endpoints, build a gRPC environment, create `Client`, spawn update and TSO-reconnect loops, and return a cluster-bound client.
- `header` creates PD request headers with the fixed cluster id.
- `get_region_and_leader` and `get_store_and_stats` are common async helpers.
- The `PdClient` impl covers cluster bootstrap/status, id allocation, store/region lookup, region and store heartbeats, split/scatter/report requests, GC safe point, TSO, service safe point updates, min resolved ts, bucket reports, RU metrics, and feature gate access.
- Stream senders for region heartbeat, bucket reports, and RU metrics lazily convert grpcio sinks into futures mpsc senders held under the inner client lock.
- The `MetaStorageClient` impl wraps get/put/delete/watch requests and fills meta-storage cluster id headers.

## Control Flow
Most unary requests build a protobuf request, set the PD header, create an executor closure over `Client`, issue grpcio async calls with current call options, check response headers, update histograms, and execute through `pd_client.request(..., retry).execute()`. Synchronous trait methods use `sync_request` or `block_on`. Periodic heartbeats often use `NO_RETRY`; leader-sensitive requests use `LEADER_CHANGE_RETRY`. Stream send paths initialize the stream on first use, enqueue messages to unbounded channels, and keep gauges for pending heartbeats/buckets.

## State and Persistence Behavior
The client stores immutable `cluster_id` plus mutable shared connection state inside `Client`. It does not persist data itself, but it drives persistent cluster state in PD: stores, regions, safe points, resource metrics, and meta-storage key/value operations. Feature gate state is updated from store heartbeat cluster version responses.

## Dependencies and Integration Points
It integrates with `kvproto` PD and meta-storage services, `security::SecurityManager`, `grpcio`, TiKV global timer, YATP monitor threads, metrics, failpoints, `txn_types::TimeStamp`, and the internal `util::Client` request/reconnect layer.

## Risks
Locking and stream initialization are delicate: grpc stream sender state transitions from `Either::Left` to `Either::Right` under write locks, and stream errors must trigger reconnects through the shared request machinery. Unbounded mpsc queues can accumulate if PD is slow. Some grpc async creation failures panic with `unwrap_or_else`, assuming local stub setup should not fail. `batch_load_regions` unwraps `scan_regions`, so PD scan failures panic there.

## Test Signals
This file contains failpoint hooks for heartbeat send failure and meta-storage get rejection. Broader behavior is usually covered by integration tests with mock/real PD clients, metrics assertions, and callers exercising safe point, TSO, heartbeat, and stream reconnect paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/client_v2.rs -->
# sources/storage-engines/tikv/components/pd_client/src/client_v2.rs

## Purpose
`client_v2.rs` implements a newer PD client architecture where one reconnect loop owns connection maintenance and request users subscribe to published connection changes. It avoids the older design where each request can rebuild shared connection state.

## Important APIs, Types, and Functions
- `ConnectContext` stores immutable config and connector.
- `RawClient` stores a `PdClientStub`, target info, and members; `connect` validates endpoints and `maybe_reconnect` refreshes the connection.
- `CachedRawClient` holds shared latest client state, a local cache, version counters, reconnect request broadcast, and reconnect notifications. Key methods are `wait_for_ready`, `connect`, `reconnect`, `check_resp`, `header`, and `call_option`.
- `reconnect_loop` performs initial connect, waits for readiness/state changes or reconnect requests, backs off, and publishes new clients.
- `RpcClient` wraps `CachedRawClient` plus `FeatureGate`.
- The local v2 `PdClient` trait exposes mutable-client operations and stream creation methods.
- `CachedDuplexResponse` swaps to the latest grpc response receiver when streams reconnect.

## Control Flow
Requests call `wait_for_ready`, fill headers from the current raw client, issue grpcio calls with timeouts, pass errors through `check_resp` to request reconnects, check response headers, and update metrics. Stream creation spawns loops that wait for ready clients, create grpc duplex streams, publish new response receivers, pipe request channels into grpc sinks, and reconnect on stream errors. `select!` is used in reconnect and bucket stream loops to react to either state changes or stream exits.

## State and Persistence Behavior
State is in-memory connection state: cached stubs, PD member metadata, monotonic cache version, reconnect broadcasts, and feature gate cluster version. The client mutates PD cluster state through requests but does not persist locally.

## Dependencies and Integration Points
The file integrates grpcio channel readiness APIs, `tokio::sync::broadcast` and mpsc, futures streams/sinks, global timer compatibility, failpoints, security connector, kvproto PD services, metrics, and `txn_types::TimeStamp`.

## Risks
Correctness depends on monotonically increasing cache versions and publishing only after a real new connection. `wait_for_ready` can time out and request reconnect; callers must handle transient errors. Broadcast channels are size 1, so lagging receivers can miss intermediate events by design. Unbounded request channels are still used for streams. Several stub creation failures panic. The v2 trait is distinct from the public `crate::PdClient`, so integration code must use the correct trait.

## Test Signals
Feature-gated test exports expose initialization, leader lookup, forced reconnect, reset-to-lame-client, and feature gate access. Failpoints control request timeout, reconnect backoff, forced reconnect, and heartbeat send failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/client_v2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/config.rs -->
# sources/storage-engines/tikv/components/pd_client/src/config.rs

## Purpose
`config.rs` defines `pd_client::Config`, the runtime configuration for PD endpoint connection and refresh behavior.

## Important APIs, Types, and Functions
`Config` contains endpoints, retry interval/count/log throttling, update interval, and forwarding enablement. `Default` chooses `127.0.0.1:2379`, 300 ms retry interval, unlimited retries represented by `isize::MAX`, log every 10 duplicate retry errors, 10 minute update interval, and forwarding disabled. `new` overrides endpoints. `validate` rejects empty endpoints, `retry_log_every == 0`, and `retry_max_count < -1`.

## Control Flow
Validation is straight-line guard checks returning boxed errors. Client constructors interpret `retry_max_count == -1` as infinite and otherwise add one retry attempt.

## State and Persistence Behavior
The struct is serializable/deserializable and cloneable but holds no live connection state. It feeds PD client initialization and reconnect loops.

## Dependencies and Integration Points
Uses serde and `tikv_util::config::ReadableDuration`. It is consumed by both v1 and v2 PD clients and by higher-level TiKV config loading.

## Risks
The documentation says default retry max is represented by `-1`, while the `Default` implementation uses `isize::MAX`; constructors handle `-1` specially elsewhere. Misconfigured `retry_log_every` would otherwise cause modulo/division problems, hence validation rejects zero.

## Test Signals
`test_pd_cfg` validates the default config.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/errors.rs -->
# sources/storage-engines/tikv/components/pd_client/src/errors.rs

## Purpose
`errors.rs` defines the PD client error type, retryability classification, and error-code mapping.

## Important APIs, Types, and Functions
- `Error` variants cover cluster bootstrap state, incompatible features, grpc errors, stream disconnects, boxed errors, missing regions, tombstone stores, compacted watch data, and unsafe service GC safe point updates.
- `Result<T>` aliases `std::result::Result<T, Error>`.
- `retryable` marks grpc, cluster-not-bootstrapped, stream disconnect, and data-compacted errors as retryable.
- `ErrorCodeExt` maps each variant to `error_code::pd::*`.

## Control Flow
Retryability and error-code mapping are direct matches over the enum. Conversions from `grpcio::Error`, futures mpsc `SendError`, and boxed errors are provided through `thiserror`.

## State and Persistence Behavior
No state. Errors may carry keys, timestamps, or formatted store data used in logs/responses.

## Dependencies and Integration Points
Uses `error_code`, `futures::channel::mpsc::SendError`, `grpcio`, `log_wrappers::Value` for redacted/hex key display, and `txn_types::TimeStamp`.

## Risks
Retry classification influences request loops; marking non-idempotent or semantic errors retryable would be dangerous, while missing transient errors reduces availability. `StoreTombstone` stores a formatted string, not the structured store. `Other` loses specific error-code detail and maps to unknown.

## Test Signals
No local tests. Behavior is exercised through PD request callers and error-code reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/feature_gate.rs -->
# sources/storage-engines/tikv/components/pd_client/src/feature_gate.rs

## Purpose
`feature_gate.rs` tracks the maximum observed cluster version and answers whether a version-gated feature can be enabled.

## Important APIs, Types, and Functions
- `FeatureGate` wraps `Arc<AtomicU64>`.
- `set_version` parses a semver string, encodes major/minor/patch into a `u64`, and updates the atomic only if the new value is greater than the current value.
- `can_enable` compares the current encoded version with a `Feature`.
- `reset_version` unsafely overwrites the version and is documented as violating monotonicity unless used carefully.
- `Feature::require` constructs a required version at compile time.

## Control Flow
`set_version` loops with `compare_exchange_weak`; if the new version is not greater than the current version it returns `Ok(false)`. Successful upgrade returns `Ok(true)`.

## State and Persistence Behavior
State is process-local and monotonic under safe APIs. It is updated from PD store heartbeat responses in both client implementations.

## Dependencies and Integration Points
Uses `semver` parsing. `PdClient::feature_gate` lets other components query feature availability based on cluster version.

## Risks
`ver_to_val` assumes major/minor/patch fit under 16-bit minor/patch packing expectations documented in comments, but it does not enforce bounds. Pre-release/build metadata is ignored after parsing. Unsafe reset can lower the version and break monotonic correctness.

## Test Signals
No local tests in this file; behavior is indirectly tested by clients or feature-gated components.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/feature_gate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/lib.rs -->
# sources/storage-engines/tikv/components/pd_client/src/lib.rs

## Purpose
`pd_client/src/lib.rs` is the public surface for the PD client crate. It re-exports client implementations and defines shared types, bucket statistics helpers, the main `PdClient` trait, constants, and small utility functions.

## Important APIs, Types, and Functions
- Re-exports include `RpcClient`, v2 `RpcClient`/`PdClient`, `Config`, `Error`, `FeatureGate`, `PdConnector`, and bucket stat utilities.
- `RegionStat` aggregates region heartbeat data, including peer state, traffic, approximate size/keys, query stats, CPU stats, and coprocessor details.
- `RegionInfo` pairs a `metapb::Region` with optional leader and derefs to `Region`.
- `BucketMeta` tracks bucket boundaries, sizes, region id/version/epoch and supports split/left-merge/total size plus heap sizing.
- `BucketStat` holds `Arc<BucketMeta>`, current protobuf stats, creation time, and methods to reset, merge, add flows, update write stats, ingest SST, split, merge, and clean a bucket.
- The public `PdClient` trait defines cluster bootstrap, store and region lookup, heartbeat streams, split/scatter/report operations, TSO, safe points, feature gate, min resolved ts, bucket reports, RU metrics, and config/meta operations.
- `take_peer_address` selects `peer_address` over `address`.
- `check_update_service_safe_point_resp` rejects unsafe service safe point requests when PD returns a higher minimal safe point.
- `RegionWriteCfCopDetail` tracks write-CF coprocessor iteration amplification.

## Control Flow
Most trait methods default to `unimplemented!`, defining an interface implemented by `client.rs`. `get_tso` delegates to `batch_get_tso(1)`. Bucket methods maintain parallel vectors in `BucketMeta` and protobuf stats, preserving split/merge alignment. Service safe point checking is a simple ttl/min-safe-point guard.

## State and Persistence Behavior
The file defines data structures used to report or modify PD's persistent cluster state, but local state is ordinary Rust structs. Bucket stats mutate in memory between reports. `BucketMeta` ordering compares epoch version first, then bucket version, which controls freshness decisions.

## Dependencies and Integration Points
The crate surface integrates with `kvproto` PD/meta/replication/resource-manager protobufs, futures boxed futures, TiKV heap sizing, time utilities, and transaction timestamps. It is consumed by raftstore, scheduling, resource control, GC, split/checker, and metadata paths.

## Risks
The trait is very broad, so mock clients must implement many methods or rely on panicking defaults. Bucket split/merge methods assert `idx != 0` and assume all stats vectors are aligned with metadata keys/sizes. `RegionWriteCfCopDetail::sub` can underflow if called with larger counters. Safe point checks only reject when ttl is nonzero and returned min exceeds requested point.

## Test Signals
Inline test `test_processed_key_0` validates MVCC amplification does not divide by zero. Other behavior is exercised by concrete client tests and downstream PD client users.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/lib.rs -->
