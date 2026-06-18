# subset-b-008899 Research

Grouped research for the listed TiKV `tikv_util` files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/config.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/config.rs

## Purpose
Provides TiKV's common configuration utility layer: human-readable size, duration, schedule, and log-format types; filesystem and address validation helpers; kernel/data-directory checks; online-config version tracking; TOML patch writing; numeric enum serde generation; and a crash-safe Raft data migration state machine.

## Important APIs, Types, And Functions
`ConfigError` classifies config validation failures into limit, address, store-label, value, and filesystem errors. Unit constants (`B`, `KIB`, `MIB`, `GIB`, `TIB`, `PIB`) and time units back the typed wrappers.

`ReadableSize` parses and serializes byte sizes with binary units, supports integer bytes and floating/scientific values with supported units, and converts to/from `online_config::ConfigValue::Size`. `ReadableSizeOrPercent` extends that behavior for percentage strings resolved against `SysQuota::memory_limit_in_bytes`, while serializing back to an absolute size. `ReadableDuration` wraps `crate::time::Duration`, supports arithmetic, parses ordered `d`, `h`, `m`, `s`, `ms`, and `us` components, serializes to compact strings, and converts to/from `ConfigValue::Duration`.

`ReadableOffsetTime` and `ReadableSchedule` model scheduled clock times with `chrono::NaiveTime` and `FixedOffset`. They parse `HH:MM` with optional timezone offsets, serialize to strings, convert schedule config values, and expose hour or hour-minute matching against arbitrary `DateTime<Tz>`.

Path helpers include `normalize_path`, `canonicalize_path`, `canonicalize_sub_path`, `canonicalize_log_dir`, and `ensure_dir_exist`. Validation helpers include `check_max_open_fds`, `check_kernel`, `check_data_dir`, `check_data_dir_empty`, and `check_addr`.

`VersionTrack<T>` owns a `RwLock<T>` plus an atomic version. `Tracker<T>` is a cloneable consumer-side cursor that returns a read guard from `any_new` only after a successful version bump. `TomlLine` and `TomlWriter` implement targeted TOML key replacement/addition for the limited config-file shapes used by TiKV. `numeric_enum_serializing_mod!` creates serde helpers for enums represented by numeric TOML values while still accepting kebab-case variant strings. `RaftDataStateMachine` coordinates safe migration between source and target Raft data directories.

## Control Flow
Readable parsers split numeric prefixes from unit suffixes, validate ASCII input, and produce deterministic error strings for unsupported units or ordering. Duration parsing walks the input from larger to smaller units and rejects repeated/out-of-order units.

Path canonicalization first normalizes components, then canonicalizes the longest physically existing prefix so non-existing final paths can still become stable absolute paths. `canonicalize_sub_path` rejects existing files where directories are expected, while `canonicalize_log_dir` allows a direct file path but rejects a final directory.

Linux data-dir checking resolves the real path, finds the longest matching mount entry via `getmntent`, logs filesystem information, and warns when the block device reports rotational media. Kernel checks iterate a fixed `/proc/sys` table and collect, rather than short-circuit, all failed checks.

Online config updates call a caller-supplied closure under the write lock. Only successful closures increment the version. Trackers compare their remembered version with the atomic version, try a non-blocking read first, and slow-log if they must block on the read lock.

`TomlWriter::write_change` scans source lines, tracks the current table, replaces matching key/value lines, injects pending keys before leaving a table, and creates missing table sections for remaining dotted keys. It intentionally supports only common TiKV config TOML shapes.

`RaftDataStateMachine::before_open_target` cleans stale `.REMOVE` trash, detects Init/Migrating/Completed states from marker and data-directory contents, writes a synced `MIGRATING-RAFT` marker when a dump is needed, and removes inconsistent partial target/source data during recovery. `after_dump_data` keeps target data, removes source data, and removes the marker with directory syncs.

## State And Persistence
Most typed config wrappers are value-only and persist through serde/TOML or `online_config::ConfigValue`. `ReadableSizeOrPercent` loses percentage intent after parsing because it stores only resolved bytes. `VersionTrack` state is in-memory and lock/atomic protected.

Persistent effects include directory creation, fd limit changes, Linux `/proc` and mount inspection, data-dir file counts, log-path canonicalization, and Raft migration marker/data-directory mutation. The Raft state machine explicitly syncs marker files and parent directories and renames directories through `.REMOVE` trash before deletion to support crash recovery.

## Dependencies And Integration
Depends on `serde`, `serde_json`, `thiserror`, `chrono`, `online_config`, `url`, `libc`, `lazy_static`, TiKV `time`, `sys::SysQuota`, and logging macros. The module is consumed by TiKV server config loading, online config updates, logger setup, storage engine directory validation, and Raft engine migration paths.

## Risks
Percentage size parsing depends on runtime memory quota and serializes as absolute bytes, so re-emitting config can obscure the original operator intent. `parse_string_to_vec` unwraps JSON parsing and can panic on invalid schedule strings before returning its own error. Several filesystem helpers and the Raft state machine use `unwrap`/`assert` because they run during startup or migration and treat unexpected states as fatal. `TomlWriter` is not a general TOML rewriter and can mishandle quoted keys, inline tables, or multi-line values. The tracker version/value update is not atomic, so false positives are possible as documented.

## Test Signals
Tests cover size parsing/serde including scientific notation and invalid units, percentage sizes, duration construction/parsing, offset time and schedule matching, path canonicalization, Linux kernel/data-dir helpers, address validation, file-count and empty-dir checks, multi-tracker updates, TOML rewriting and empty-content insertion, and many Raft migration/recovery states including partial marker writes and nested target paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/deadline.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/deadline.rs

## Purpose
Defines a small deadline abstraction around TiKV's coarse `Instant` plus an error helper for mapping deadline expiry into kvproto busy errors.

## Important APIs, Types, And Functions
`DeadlineError` implements `std::error::Error` and `Display` with the message `deadline has elapsed`. `Deadline` stores one `Instant` and exposes `new`, `from_now`, `inner`, `check`, `to_std_instant`, and `remaining_duration`. `set_deadline_exceeded_busy_error` fills a `kvproto::errorpb::Error` with a `ServerIsBusy` reason of `deadline is exceeded`.

## Control Flow
`from_now` adds a TiKV `Duration` to `Instant::now_coarse`. `check` first consults the `deadline_check_fail` failpoint, then compares the stored instant with current coarse time and returns `DeadlineError` when expired. `remaining_duration` uses saturating subtraction so expired deadlines report zero. `to_std_instant` translates by adding the remaining TiKV duration to `std::time::Instant::now`.

## State And Persistence
State is only the immutable deadline instant. No persistence or global mutation exists except the caller-provided protobuf error mutation.

## Dependencies And Integration
Depends on `fail`, `kvproto::errorpb`, and `super::time::{Duration, Instant}`. It integrates with request paths that need cheap deadline checks and with RPC error construction for overload/deadline signalling.

## Risks
Coarse time can make boundary behavior fuzzy by a few milliseconds. `to_std_instant` depends on the difference between coarse and standard clocks and should be used for relative timeout conversion, not exact timestamp identity. The failpoint can force errors in tests or failpoint-enabled deployments.

## Test Signals
Tests cover remaining duration for future, expired, current, and large deadlines, and verify consistency between `remaining_duration` and `check`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/deadline.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/future.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/future.rs

## Purpose
Provides small futures utilities for bridging callbacks to futures, buffering streams, polling futures directly from wakeups, applying timeouts without a Tokio runtime, and periodically running async checks.

## Important APIs, Types, And Functions
`paired_future_callback` returns a boxed one-shot callback and a `futures::channel::oneshot::Receiver`. `paired_must_called_future_callback` wraps the sender in `callback::must_call` so a fallback value is produced if the callback is dropped uncalled.

`create_stream_with_buffer` returns an mpsc receiver stream plus a driver future that forwards items from a remote stream into the bounded buffer. `poll_future_notify` installs a custom `ArcWake` implementation that immediately polls the boxed future on the thread invoking `wake`.

`try_poll` synchronously polls once and returns `Some` only for immediately ready futures. `block_on_timeout` blocks the current thread until a future or global timer delay completes. `async_timeout` is async and uses a fast path that avoids creating a timer if the wrapped future completes immediately. `RescheduleChecker` runs a future builder after a configured TiKV duration has elapsed.

## Control Flow
The callback helpers send through oneshot channels and log a warning if the receiver was dropped. Stream buffering maps each stream item into `Ok` and forwards into the mpsc sender, logging send failures.

The `PollAtWake` state machine uses `IDLE`, `POLLING`, and `NOTIFIED` in an `AtomicU8`. A poller wins `IDLE -> POLLING`, polls the future, and tries to return to `IDLE`; wakeups during polling switch `POLLING -> NOTIFIED`, causing the polling thread to loop and poll again before releasing. When the future returns ready, the stored future is taken and later wakeups are ignored.

`block_on_timeout` selects between the fused future and a global timer delay. `async_timeout` first uses `select_biased!` against `ready(())`; if the future is pending, it creates a timer and selects between completion and timeout. `RescheduleChecker::check` compares elapsed coarse time with the configured interval, awaits the built future, and resets its start time.

## State And Persistence
State is in-memory: one-shot channels, mpsc buffers, the `UnsafeCell<Option<BoxFuture>>` inside `PollAtWake`, atomic poll state, and `RescheduleChecker`'s last-run instant. There is no persistence.

## Dependencies And Integration
Depends on `futures`, `futures_util::compat`, TiKV `GLOBAL_TIMER_HANDLE`, `callback::must_call`, and TiKV time wrappers. It is useful in yatp/future-pool contexts where Tokio runtime assumptions are undesirable.

## Risks
`PollAtWake` relies on unsafe `UnsafeCell` sharing and careful atomic transitions; incorrect future `Send` assumptions or unexpected reentrant wake patterns would be high risk. `block_on_timeout` blocks the current thread and should not be used where blocking harms scheduler progress. `async_timeout` returns a boxed dynamic error for timeout and does not cancel external side effects of the wrapped future beyond dropping it. The lazy timer fast path intentionally polls the future once immediately, so future implementations must tolerate normal poll semantics.

## Test Signals
Tests verify in-place wake repolling counts, `try_poll` ready/pending behavior, successful timeout completion, timeout error messages, immediate completion fast path, propagation of `Result` outputs, and the lazy timer behavior for fast and slow futures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/future.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/keybuilder.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/keybuilder.rs

## Purpose
Implements `KeyBuilder`, a low-allocation helper for constructing byte keys when a prefix may be reserved and filled later.

## Important APIs, Types, And Functions
`KeyBuilder` owns a `Vec<u8>` and a `start` offset. Constructors are `new(max_size, reserved_prefix_len)`, `from_vec(vec, reserved_prefix_len, reserved_suffix_len)`, and `from_slice(slice, reserved_prefix_len, reserved_suffix_len)`. Mutators and views are `set_prefix`, `append`, `as_ptr`, `is_empty`, `len`, `as_slice`, and `build`.

## Control Flow
`new` reserves capacity and unsafely sets length for reserved prefix bytes. `from_vec` reuses the input vector when capacity permits by copying existing bytes forward to make prefix space; otherwise it falls back to `from_slice`. `set_prefix` asserts the reserved prefix length exactly matches the supplied prefix, copies bytes into the beginning of the buffer, and sets `start` to zero. `build` shifts visible bytes to the front if the prefix was never filled.

## State And Persistence
State is only the owned vector and visible-start offset. No persistence or sharing exists.

## Dependencies And Integration
Uses `std::ptr` for overlapping and non-overlapping byte moves. It integrates with key-encoding paths that need to prepend region/table/engine prefixes without repeated allocation.

## Risks
The implementation uses unsafe `set_len` and pointer copies. It is sound only if callers respect the reserved prefix invariant and never read uninitialized reserved bytes through `as_slice`; the `start` offset protects that until `set_prefix`. `set_prefix` panics on mismatched prefix length. `as_ptr` returns the visible start pointer and is unsafe for callers to dereference beyond `len`.

## Test Signals
The unit test covers construction through `new`, `from_vec` with and without setting the prefix, vector reuse with enough capacity, and `from_slice`, verifying final byte output and length changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/keybuilder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/lib.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/lib.rs

## Purpose
Defines the root `tikv_util` crate surface, re-exporting utility modules and implementing shared process, panic, collection, byte-escaping, readiness, and small generic helper APIs used across TiKV.

## Important APIs, Types, And Functions
The crate enables nightly features used by submodules and exposes modules such as `config`, `future`, `deadline`, `logger`, `lru`, `math`, `sys`, `timer`, and `worker`. Global flags include `PANIC_WHEN_UNEXPECTED_KEY_OR_DATA`, `PANIC_MARK`, and `GLOBAL_SERVER_READINESS`.

Core helpers include panic mark file functions, marker traits (`AssertClone`, `AssertCopy`, `AssertSend`, `AssertSync`), `slices_in_range`, `HandyRwLock`, `escape`, `unescape`, `TryInsertWith::or_try_insert_with`, `get_tag_from_thread_name`, `DeferContext`, `Either`, `RingQueue`, `is_even`, `MustConsumeVec`, panic-context storage and `set_panic_context!`, `set_panic_hook`, `check_environment_variables`, `run_and_wait_child_process`, `is_zero_duration`, `empty_shared_slice`, `build_on_master_branch`, `set_vec_capacity`, and `ServerReadiness`.

## Control Flow
Panic flag helpers wrap atomics with sequential consistency. `escape` converts bytes to printable ASCII with protobuf-style octal escapes; `unescape` reverses supported escape forms and panics on malformed input. `TryInsertWith` runs a fallible initializer only for vacant hash-map entries. `DeferContext` executes its closure on drop.

`RingQueue::push` drops the oldest item when capacity is full. `MustConsumeVec` dereferences as a vector but panics safely on drop if non-empty, making resource leaks visible without double-panicking during unwind. Panic context is thread-local; `set_panic_context!` prefixes keys with file/line and returns a guard that removes them on drop.

`set_panic_hook` warms backtrace metadata in a background thread, logs panic message/thread/location/backtrace/context, swaps async logging to a synchronous terminal logger for flush safety, optionally creates a panic mark file, and then aborts or calls `libc::_exit(1)`. `check_environment_variables` ensures `TZ` is set on Unix and logs selected networking/proxy variables. `run_and_wait_child_process` forks, runs a closure in the child, and returns the parent's observed exit status. `ServerReadiness::is_ready` requires both PD connectivity and raft peer catch-up flags.

## State And Persistence
Persistent effects include creating `panic_mark_file` in a data directory and environment mutation for missing `TZ`. Most other state is process-local: atomics, thread-local panic context, ring buffers, readiness atomics, and logger replacement during panic handling.

## Dependencies And Integration
Depends on many standard utilities plus `nix` fork/wait, `lazy_static`, `serde`, `backtrace`, TiKV logger/thread wrappers, and exported macros. It is the integration hub used by nearly all TiKV components importing `tikv_util`.

## Risks
`unescape` intentionally panics for malformed input and assumes trusted/validated strings. `set_panic_hook` runs in crash context, so logging, backtrace generation, and file creation must remain best-effort and avoid relying on full runtime health. `run_and_wait_child_process` is Unix/fork oriented and should not be used in multi-thread-sensitive paths outside tests. `set_vec_capacity` uses `reserve_exact(cap - len)` when growing toward capacity, so callers should pass a capacity at least as large as the current length.

## Test Signals
Tests cover panic hook behavior in a child process, panic mark path/existence, ring queue eviction/removal, defer execution, RwLock guard behavior, VecDeque slicing across wrap points, must-consume leak detection and double-panic prevention, unescape forms, zero-duration checks, and scoped panic-context cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/log.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/log.rs

## Purpose
Defines TiKV's global logging macros and helpers for formatting slog logger key/value context in panic or error strings.

## Important APIs, Types, And Functions
Macros `crit!`, `warn!`, `info!`, `debug!`, and `trace!` forward to `slog_global`. The custom `error!` macro supports `?err` and `%err` forms and appends `err_code` via `error_code::ErrorCodeExt`; `error_unknown!` does the same with `error_code::UNKNOWN`. `info_or_debug!` and `info_or_error!` choose a log level by condition.

`SlogFormat<'a>` implements `Display` for a logger's owned key/value list. `format_kv_list` serializes borrowed values before owned logger values. `slog_panic!` panics with a message plus formatted slog context.

## Control Flow
Logging macros expand directly into `slog_global` calls. Error macros have special arms for literal-only and full slog argument forms so the error and error code fields are appended correctly. `FormatKeyValueList` serializes slog values as `[key=value]` tokens, inserting spaces after the first token. `slog_panic!` builds the combined context string and omits the trailing context when empty.

## State And Persistence
The file has no owned persistent state. It reads logger key/value state through slog APIs and emits logs through the global logger.

## Dependencies And Integration
Depends on `slog`, `slog_global`, and `error_code`. It integrates with `logger/mod.rs` formatting and with all TiKV code using crate-level logging macros.

## Risks
The specialized `error!` macro expects errors to implement `ErrorCodeExt`; callers without that trait must use `error_unknown!` or regular slog form. Formatting panics use `unwrap` internally while serializing slog values, which is acceptable for diagnostic code but could panic if an unusual serializer error occurred.

## Test Signals
Tests verify empty and nested logger key/value formatting order and `slog_panic!` output with no context, borrowed context, owned context, and combined borrowed plus owned context.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/logger/file_log.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/logger/file_log.rs

## Purpose
Implements rotating file logging and archived-log cleanup for TiKV's logger backend.

## Important APIs, Types, And Functions
`open_log_file` creates parent directories and opens the active log file in append/create mode. `Rotator` defines the rotation lifecycle: `is_enabled`, `prepare`, `should_rotate`, `on_write`, and `on_rotate`. `RotatingFileLoggerBuilder` assembles a path, rename callback, cleanup limits, and rotators, then builds a `RotatingFileLogger`. `RotatingFileLogger` implements `Write`. `RotateBySize` is the built-in size-based rotator. `Runner` implements `worker::Runnable` for archive cleanup tasks.

## Control Flow
Building opens the active file, starts a lazy archive worker, schedules an initial archive pass, and prepares each enabled rotator from current file metadata. `write` updates all rotator state before writing bytes to the active file. `flush` checks rotators; on the first rotator requesting rotation, it flushes the file, asks the rename callback for an archive path, renames the active log, opens a fresh active file, resets all rotators, schedules archive cleanup, and returns. If no rotation is needed, it just flushes.

`Runner::list_old_logs` scans the log directory for files whose stems contain the active log prefix plus a parseable timestamp, sorts newest first, and returns metadata. `Runner::run` removes files exceeding `max_backups` and/or older than `max_days`.

## State And Persistence
Persistent state is the active log file, renamed archived log files, and deletion of old archives. In-memory state includes rotator counters, builder options, a lazy worker, and archive selection data.

## Dependencies And Integration
Depends on `chrono`, `ReadableSize`, `ReadableDuration`, TiKV `LazyWorker`, `Runnable`, and logger thread-name constants. It is used by `logger::file_writer`, which wraps the rotating logger in a `BufWriter`.

## Risks
Rotation happens during `flush`, not immediately during `write`; callers that do not flush may exceed configured rotation size. `RotateBySize` rotates only when `file_size > rotation_size`, so exactly equal size does not rotate. Rename or open failures propagate from `flush`; tests ensure they do not panic on drop. Archive timestamp parsing is filename-convention dependent and intentionally ignores malformed names. Cleanup uses `unwrap` around directory listing in the worker and logs remove failures.

## Test Signals
Tests cover size rotation threshold, rename failure behavior, max-backup cleanup at startup and after rotation, max-days cleanup at startup and after rotation, tolerance of illegal archive names, and timestamp extraction from valid and invalid filenames.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/logger/file_log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/logger/formatter.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/logger/formatter.rs

## Purpose
Provides low-level formatting helpers for TiKV's unified text log format: source file name sanitization and conditional JSON escaping of log tokens.

## Important APIs, Types, And Functions
`write_file_name` writes only ASCII alphanumeric, dot, dash, and underscore bytes from a filename. `write_escaped_str` writes a value directly unless `need_json_encode` detects bytes that must be JSON encoded according to TiKV's unified log format.

## Control Flow
`write_file_name` scans byte ranges and writes contiguous allowed segments while skipping disallowed bytes. `need_json_encode` returns true for control/space bytes through `0x20`, double quote, equals, left bracket, or right bracket. `write_escaped_str` either writes raw UTF-8 bytes or delegates to `serde_json::to_writer`.

## State And Persistence
No state or persistence; all functions stream to the caller-provided writer.

## Dependencies And Integration
Depends on `std::io` and `serde_json`. It is used by `logger/mod.rs` when writing source file, message, key, and value fields in text logs.

## Risks
The escaping predicate is byte-oriented by design; non-ASCII characters are allowed raw unless combined with a byte requiring JSON encoding. `write_file_name` silently strips disallowed characters, which is useful for log safety but can make unusual filenames less identifiable.

## Test Signals
Tests cover escaping decisions for ASCII, spaces, separators, controls, replacement/Unicode text, and mixed Unicode with spaces. Filename tests verify disallowed punctuation, controls, whitespace, and non-ASCII characters are stripped while safe filename characters remain.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/logger/formatter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/logger/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/logger/mod.rs

## Purpose
Builds TiKV's slog-based logging backend, including global initialization, async guard management, file/terminal writers, text/JSON/RocksDB formats, dynamic log-level filtering, slow-log filtering, tag-based dispatch, and thread-id injection.

## Important APIs, Types, And Functions
`init_log` wires a drain into the global logger with level, async/sync mode, stdlog redirection, disabled targets, and slow-log threshold. `set_global_logger`, `exit_process_gracefully`, and `panic_after_best_effort_flush` manage global logger replacement and async flush behavior.

Writer/format constructors include `file_writer`, `term_writer`, `text_format`, `slow_log_text_format`, `rocks_text_format`, `json_format`, and `slow_log_json_format`. Level helpers include `get_level_by_string`, `get_string_by_level`, conversion between `slog::Level` and `log::Level`, `get_log_level`, and `set_log_level`.

Formatting and filtering types include `TikvFormat`, `RocksFormat`, `LogAndFuse`, `SlowLogFilter`, `GlobalLevelFilter`, `LogCost`, `LogDispatcher`, `ThreadIDrain`, and the text-field `Serializer`.

## Control Flow
`init_log` stores the initial atomic log level, extends disabled targets from `TIKV_DISABLE_LOG_TARGETS`, builds a module filter, then wraps the drain with slow-log filtering, thread-id injection, global level filtering, and optional `slog_async::Async`. Async mode stores an `AsyncGuard` in `ASYNC_LOGGER_GUARD`; sync mode wraps the drain in a mutex.

`TikvFormat::log` writes timestamp, level, source file/line, escaped message, record key-values, logger key-values, newline, and flushes. `RocksFormat` writes a RocksDB-like line and suppresses headers for tags ending in `_header`. `json_format` emits newline-delimited JSON with message, caller, level, and optional time.

`SlowLogFilter` inspects records tagged `slow_log`, extracts the `takes` field through `SlowCostSerializer`, and filters records with cost less than or equal to the threshold. `LogDispatcher` routes tags starting with `slow_log`, `rocksdb_log`, or `raftdb_log` to specialized drains, otherwise to the normal drain. `LogAndFuse` catches drain errors and logs the original record plus a critical logger-error message to stderr.

## State And Persistence
Global state is the atomic `LOG_LEVEL` and optional async logger guard. Persistent effects happen through configured writers, especially rotating file writers. `set_log_level` changes both TiKV's atomic filter and stdlog redirection.

## Dependencies And Integration
Depends on `slog`, `slog_async`, `slog_json`, `slog_term`, `slog_global`, `log`, `grpcio`, `chrono`, file logging helpers, TiKV thread wrappers, and config size/duration types. It is the backend for macros in `log.rs` and `macros.rs` and for subsystem-specific RocksDB/RaftDB/slow logs.

## Risks
Async logging can lose messages if the guard is not dropped, so explicit graceful exit and best-effort panic flush paths exist. `SLOG_CHANNEL_OVERFLOW_STRATEGY` is `Drop`, so overload can drop records. Dynamic level checks appear both in filters and formatters; inconsistent wrapping could change filtering behavior. Slow-log filtering only applies the threshold to exact `slow_log` tag records with a numeric `takes`; related tags or missing costs pass through. File writer rotation size is in MiB and rotation occurs on flush.

## Test Signals
Tests validate text and JSON formats, datetime parsing, source-file matching, global level filtering, level string/conversion helpers, unified level names, and dispatcher/slow-log filtering behavior across normal, slow, RocksDB, and RaftDB buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/logger/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/lru.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/lru.rs

## Purpose
Implements a generic LRU cache with pluggable size accounting and eviction policy, optimized around a hash map plus intrusive linked recency trace.

## Important APIs, Types, And Functions
Internal `Record<K>` nodes hold prev/next pointers and a key. `ValueEntry<K, V>` stores a value and pointer to its recency record. `Trace<K>` owns head/tail sentinel nodes, a sampling tick, and methods for create, promote, maybe-promote, delete, tail reuse, clear, remove-tail, and tail lookup.

`SizePolicy<K, V>` abstracts cache size accounting; `CountTracker` counts entries. `GetTailEntry` lets eviction policies inspect the least-recent entry lazily. `EvictPolicy<K, V>` decides whether to evict; `EvictOnFull` evicts when current size exceeds capacity.

`LruCache<K, V, T, E>` exposes constructors, `size`, `clear`, `capacity`, `internal_allocated_capacity`, `insert`, `insert_if_not_exist`, `remove`, `get`, `get_no_promote`, `contains_key`, `get_mut`, `iter`, `len`, `is_empty`, and `resize`.

## Control Flow
The trace list is newest at the head and oldest at the tail. Insertion of a new key either creates a new record or, if the eviction policy says the post-insert size should evict, reuses the tail record for the new key and removes the old key from the map. Existing-key insertions optionally replace the value and promote the record. After insertion, `evict_until_fit` repeatedly removes tail entries until the policy accepts the current size or the map is empty.

`get` and `get_mut` call `maybe_promote`, which promotes only when `tick & sample_mask == 0`, allowing sampled recency updates. `get_no_promote` and `contains_key` avoid recency mutation. `resize` clamps zero to one, evicts oldest entries when shrinking, and shrinks the map allocation after removals.

## State And Persistence
All state is in-memory: the map, linked-list nodes allocated with `Box::leak`, size policy counters, capacity, eviction policy, and sampling tick. `Drop` calls `clear`, and `Trace::drop` frees sentinel nodes.

## Dependencies And Integration
Depends on TiKV `collections::{HashMap, HashMapEntry}`, `std::ptr`, `NonNull`, and `MaybeUninit`. It integrates with caches that need custom size policies or eviction behavior, such as transaction-status style caches referenced by comments.

## Risks
The trace is unsafe and manually manages allocation, key initialization, pointer links, and drops. Any map/list divergence would cause memory unsafety or panics. `sample_mask` changes LRU precision; nonzero masks deliberately skip many promotions. Oversized entries can cause the cache to evict everything because `SizePolicy` cannot precompute a candidate's size before insertion. The cache is `Send` when its components are `Send`, but it is not internally synchronized.

## Test Signals
Tests cover insertion replacement and eviction order, query promotion, zero-capacity clamping, removal, resize shrink/grow behavior, sampled promotion, clear/reuse, custom size tracking, oversized value handling, no-promote lookup behavior, and insert-if-absent semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/lru.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/macros.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/macros.rs

## Purpose
Defines general-purpose exported macros for error boxing, slow logging, inherited thread names, scope defer, callback waiting, option/result propagation, panic safety, and display delegation.

## Important APIs, Types, And Functions
`box_err!` creates a boxed error including source file and line. `box_try!` returns early with a boxed error. `slow_log!` logs slow-operation warnings, either from a timer-like value (`T` arm) or a duration. `thd_name!` appends inherited thread tags. `defer!` creates a `DeferContext`. `wait_op!` runs an async callback-style operation and waits on an mpsc receiver with optional timeout. `try_opt!` and `try_opt_or!` simplify `Result<Option<T>>` propagation. `safe_panic!` logs instead of panicking during unwind. `impl_format_delegate_newtype!` and `impl_display_as_debug!` implement `Display`.

## Control Flow
Most macros expand to direct control flow at call sites. `wait_op!` creates a channel, passes a boxed callback into the expression, propagates expression errors with `?`, then blocks waiting for a result or timeout. `safe_panic!` checks `std::thread::panicking`; during unwind it emits an error log with a double-panic-prevented suffix, otherwise it calls `panic!`.

## State And Persistence
Macros have no owned state. Expanded code may create channels, defer guards, boxed errors, or log records.

## Dependencies And Integration
Depends on crate logging macros, `logger::LogCost`, time conversion helpers, `DeferContext`, and `get_tag_from_thread_name`. These macros are exported at crate root and used throughout TiKV.

## Risks
`box_err!` captures call-site line numbers, so tests and diagnostics are line-sensitive. `wait_op!` blocks the current thread and assumes the expression accepts a callback and returns `Result`. `safe_panic!` avoids aborting on double panic but only logs if the logger is usable during unwinding.

## Test Signals
Tests verify `box_err!` includes the expected file/line text and that `safe_panic!` in a `Drop` implementation does not double-panic during an existing unwind.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/math.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/math.rs

## Purpose
Provides a thread-safe moving average for `u32` samples with cheap atomic reads.

## Important APIs, Types, And Functions
`MovingAvgU32Inner` stores a fixed-size circular buffer, current index, and sum. `MovingAvgU32` wraps that inner state in a `Mutex` and exposes a cached `AtomicU32`. Public methods are `new(size)`, `add(sample)`, `fetch()`, and `clear()`.

## Control Flow
`new` fills the buffer with zeros. `add` locks the mutex, advances the circular index, computes the old average, updates the sum by adding the new sample and subtracting the overwritten sample, stores the sample, computes the new average, updates `cached_avg` with relaxed ordering, and returns `(old_avg, new_avg)`. `fetch` reads the cached average without locking. `clear` zeroes the buffer, index, sum, and cached average.

## State And Persistence
All state is in-memory. The mutex protects buffer/sum/index consistency; the atomic cache provides eventually current lock-free reads. There is no persistence.

## Dependencies And Integration
Uses only `std::sync::{Mutex, AtomicU32}`. It can be embedded in metrics, rate smoothing, or adaptive control paths that need low-cost average reads.

## Risks
`new(0)` would create an empty buffer and later `add` would divide/modulo by zero; callers must provide a positive size. Sum is `u32`, so very large windows and samples can overflow in debug or wrap in release. Relaxed ordering is appropriate for approximate metrics but not for synchronization.

## Test Signals
Tests cover monotonic decreasing and increasing sequences with clear/reset behavior, plus random samples checked against an external sum for a partially filled window.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/math.rs -->
