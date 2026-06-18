# Research: subset-b-008556

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/mod.rs -->
# sources/storage-engines/raft-engine/src/file_pipe_log/mod.rs

## Purpose
This module is the public assembly point for the filesystem-backed `PipeLog` implementation. It wires together the private format, file I/O, pipe, builder, and reader modules, then re-exports the crate-visible types that higher layers use to open raft-engine storage over log files. Its `debug` submodule provides public utility readers and writers for inspecting or rewriting physical log files outside the normal `Engine` path.

## Important APIs, Types, And Functions
The top-level exports map the implementation into stable names: `FilePipeLog` is `pipe::DualPipes`, `FilePipeLogBuilder` is `pipe_builder::DualPipesBuilder`, and recovery extension points include `ReplayMachine`, `RecoveryConfig`, and `DefaultMachineFactory`. It also re-exports filename helpers `FileNameExt` and `parse_reserved_file_name`.

`debug::build_file_writer` and `debug::build_file_reader` adapt a generic `FileSystem` to `LogFileWriter` and `LogFileReader`, opening files with the requested permission and passing the parsed or requested `LogFileFormat` to `log_file` helpers.

`debug::LogItemReader<F>` is an iterator over logical `LogItem`s. It supports `new_file_reader` for one physical log file and `new_directory_reader` for every file in a directory whose name parses as a `FileId`. Directory mode sorts by `FileId` so append and rewrite file sequence order is deterministic.

## Control Flow
`LogItemReader::next` drains a local `VecDeque<LogItem>`. When empty, it asks `LogItemBatchFileReader` for the next decoded batch. If the current file is exhausted, `find_next_readable_file` opens the next queued file, parses its header, and preloads the first non-empty batch. Decode or open errors reset the batch reader and surface as the iterator item error.

The iterator implementation delegates to the inherent `next` method. This intentionally lets callers use normal iterator syntax while preserving the custom error-yielding behavior.

## State And Persistence Behavior
The debug reader stores only transient state: the `Arc<FileSystem>`, remaining `(FileId, PathBuf)` queue, current reusable `LogItemBatchFileReader`, and decoded items awaiting delivery. It does not mutate source files. The writer utility can create or reopen files; with `create = true`, it force-resets through `build_file_writer`, which is used in tests to produce clean log files with the chosen format.

Because filename parsing uses `FileId::parse_file_name`, debug directory reads ignore unrelated files and subdirectories but will report corruption if a parsed log file is empty or malformed.

## Dependencies And Integration Points
This module depends on `env::FileSystem`, `log_batch::LogItem`, `pipe_log::FileId`, `LogFileReader`, `LogFileWriter`, and `LogItemBatchFileReader`. Production callers usually consume the re-exported `FilePipeLogBuilder`; diagnostic and scripting paths consume `debug::build_file_reader`, `debug::build_file_writer`, and `debug::LogItemReader`.

## Risks And Edge Cases
`new_file_reader` rejects non-files and filenames that do not parse as log files. `new_directory_reader` uses `std::fs::read_dir` rather than the configured `FileSystem`, so it is tied to local filesystem semantics even though actual file opens use `F`. A malformed file whose name looks valid causes iteration to return an error and then stop. Empty but well-formed files are accepted in single-file mode and skipped in directory iteration.

## Test Signals
`test_debug_file_basic` writes batches containing entries, commands, puts, and deletes across several files, then verifies both single-file and directory iteration reproduce drained `LogBatch` items. `test_debug_file_error` covers invalid file/directory arguments, unrelated files, corrupted files, and empty files. `test_recover_from_partial_write` verifies reopening a partially written or truncated file can replace the header format cleanly across V1/V2 combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/pipe.rs -->
# sources/storage-engines/raft-engine/src/file_pipe_log/pipe.rs

## Purpose
This file implements the active filesystem log pipe. `SinglePipe` manages one monotonic queue of log files for either append or rewrite traffic; `DualPipes` combines append and rewrite pipes and implements the `PipeLog` trait consumed by the raft engine.

## Important APIs, Types, And Functions
`PathId`, `Paths`, `DEFAULT_PATH_ID`, and `DEFAULT_FIRST_FILE_SEQ` define how physical directories and file sequences are represented. `File<F>` records an opened file's sequence, shared handle, format, directory index, and whether it is a reserved recycled file. `WritableFile<F>` tracks the currently writable sequence, writer, and format.

`SinglePipe::open` creates or opens the last active file for writes, initializes metrics, installs active and recycled queues, and posts `EventListener::post_new_log_file` for existing active files. `append`, `read_bytes`, `sync`, `rotate`, `purge_to`, `file_span`, and `total_size` provide the queue operations behind `PipeLog`.

`rotate_imp` is the core rollover routine. It closes the current writer, reuses a recycled file or creates a new file, writes and syncs the new header, syncs the directory, swaps the writable file, appends the new active `File`, updates metrics, and notifies listeners.

`recycle_file` renames a reserved or purged file into the next queue filename and reopens it for read-write use. `new_file` selects a directory with enough free space and creates a fresh file. `find_available_dir` checks spill directories via `fs2::statvfs`, falling back to the main directory.

`DualPipes` stores exactly two `SinglePipe`s, with append at index `LogQueue::Append as usize` and rewrite at index `LogQueue::Rewrite as usize`, plus directory lock files that are unlocked on drop.

## Control Flow
Writes call `DualPipes::append`, dispatch by queue, and enter `SinglePipe::append`. The writable mutex is acquired first; if the current offset reached `target_file_size`, rotation happens before writing. The batch receives a `LogFileContext`, can emit alignment padding under V2 signing, and writes its bytes. On a no-space error, the writer truncates back, rotates to another file if possible, and returns `Error::TryAgain` so the caller can retry on the new file. Successful writes return a `FileBlockHandle` and trigger append listeners.

Reads call `get_fd` to validate the requested sequence lies in the active contiguous span, then build a `LogFileReader` over the shared handle and read the requested block. Purges split `active_files` at the requested sequence, retain the tail, and either move eligible V2 signed files into the recycled queue or delete them. Append queue recycling is capacity-limited; rewrite queue capacity is always zero.

Shutdown closes the active writer and best-effort renames non-reserved recycled append files into reserved filenames to reduce future recovery cost. Directory locks are released by `DualPipes::drop`.

## State And Persistence Behavior
The persistent state is the set of queue files on disk, their headers, and possible reserved files. `active_files` and `recycled_files` are concurrent `RwLock<VecDeque<_>>` structures; `writable_file` is a mutex and must be acquired first when both active file state and writer state are needed. New log headers are synced before the new file becomes active, and the containing directory is synced on Unix-like systems.

Recycling is conservative: only files with log signing are reused, and recycle capacity is derived from append queue configuration. Purged files outside capacity or with incompatible formats are deleted. Active file sequences are expected to be contiguous; range checks and scan-time cleanup in the builder enforce this invariant.

## Dependencies And Integration Points
The pipe relies on `Config` for target file size and recycle settings, `FileSystem` for file operations, `EventListener` for lifecycle callbacks, `metrics` and `perf_context` for observability, `LogFileWriter`/`LogFileReader` for format-aware I/O, and `ReactiveBytes` for delayed signing of write buffers. It is built by `DualPipesBuilder::finish` and used by `Engine` through the `PipeLog` trait.

## Risks And Edge Cases
No-space handling has documented corner cases when a single write is larger than the target file size and multiple directories or recycled logs are involved. Directory sync uses `unwrap`, so a directory fsync failure panics rather than returning an error. `get_fd`, `purge_to`, and `file_span` assume at least one active file. Recycled file rename failures are handled by deleting the source and falling back, which may reduce recycle capacity. The index-based `DualPipes` dispatch depends on enum discriminants and is guarded by debug assertions only.

## Test Signals
`test_dir_lock` verifies exclusive directory locking. `test_pipe_log` covers initial file creation, rollover, purge range validation, append offsets, reads, and invalid read handles. `test_pipe_log_with_recycle` exercises purge-to-recycle, unreadability of old handles, reuse, and data integrity under an obfuscated filesystem. `test_release_on_drop` verifies lock release.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/pipe.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/pipe_builder.rs -->
# sources/storage-engines/raft-engine/src/file_pipe_log/pipe_builder.rs

## Purpose
`pipe_builder.rs` discovers existing log files, locks directories, recovers logical state by replaying log batches, prepares recycled files, and finally constructs `DualPipes`. It is the startup and recovery coordinator for the filesystem-backed pipe log.

## Important APIs, Types, And Functions
`ReplayMachine` is the recovery extension trait. `replay` consumes each decoded `LogItemBatch` with its `FileId`; `merge` combines a machine that consumed newer items from the same queue. The associativity requirement allows parallel recovery over chunks.

`DefaultMachineFactory<M>` adapts any default `ReplayMachine` to the crate's `Factory` trait. `RecoveryConfig` bundles queue, recovery mode, concurrency, and read block size. `DualPipesBuilder<F>` owns `Config`, `FileSystem`, listeners, scanned directories and locks, parsed file names, and opened file handles.

`scan` calls `scan_and_sort`, opens append and rewrite files read-only except for last files or `TolerateAnyCorruption`, opens reserved files read-only, removes non-contiguous leading spans, and clears obsolete metadata before the first retained sequence. `scan_dir` creates or validates directories, optionally locks them, and classifies filenames as append, rewrite, or reserved.

`recover` allocates a bounded rayon thread pool, splits threads between append and rewrite queues, and invokes `recover_queue_imp` for both queues in parallel. `recover_queue_imp` chunks files, opens each file with `LogItemBatchFileReader`, replays decoded batches, tolerates and truncates corruption according to `RecoveryMode`, and reduces chunk machines with `ReplayMachine::merge`.

`initialize_files` pre-fills reserved recycle files up to configured capacity and removes excess reserved files. `finish` creates append and rewrite `SinglePipe`s and wraps them in `DualPipes`. `lock_dir` creates and exclusively locks the lock file under a directory.

## Control Flow
Startup normally calls `new`, `scan`, `recover`, and `finish`. Scanning fills file-name vectors, sorts by sequence, opens handles, and prunes invalid prefix ranges caused by holes or duplicates. Recovery then reads append and rewrite queues in parallel. Within each file, `LogItemBatchFileReader::open` parses the file header and records the format back into `File<F>`. Each item batch is replayed, with a lookahead read used to identify the last batch and verify its entry block before committing it to the replay machine.

If a file header or batch is corrupted, behavior depends on `RecoveryMode`: absolute consistency fails immediately; tail corruption mode truncates only the final file; tolerate-any mode may truncate any corrupted file. Entry-block checksum or decompression failures on the last item are handled similarly, truncating to the batch header offset in non-absolute modes.

After recovery, `finish` initializes reserved files and opens `SinglePipe`s. Append receives the reserved files for later recycling; rewrite receives no recycled files.

## State And Persistence Behavior
The builder mutates on-disk state during recovery when configured to tolerate corruption, using `truncate` and `sync` on broken files. It may create missing directories, create lock files, prefill reserved files with zeros up to `target_file_size`, and delete excess reserved files. It also deletes stale metadata from old file-system implementations once it identifies a retained active range.

Opened `File<F>` entries initially carry `LogFileFormat::default`; recovery updates each format after parsing the header. This matters because later purge/recycle logic only recycles files whose parsed version supports log signing.

## Dependencies And Integration Points
The builder connects `Config`, `RecoveryMode`, `FileSystem`, `Handle`, `EventListener`, `LogItemBatch`, `FileId`, `LogQueue`, `LogFileReader`, `LogItemBatchFileReader`, and `SinglePipe`. It uses `rayon` for parallel replay, `fs2` for locking, and the filename helpers from `format`. `Engine::open` and tooling such as `fork` depend on its scan and finish behavior.

## Risks And Edge Cases
The file-hole cleanup drains everything before the last detected gap, so duplicated or missing sequences can discard older files from consideration. The stale metadata deletion uses sampling to find a start point and may leave metadata if the sample misses it. Prefill writes fixed-size zero buffers and can stop early on no-space, then reset target recycle capacity to zero for that run. `from_script`-style replay machines can make merge errors visible only during parallel reduction. Recovery read concurrency of zero returns an empty machine without validating files.

## Test Signals
Direct tests for `pipe_builder.rs` are mostly reached through pipe, engine, recovery, and fork tests. Relevant covered behavior includes directory locking, open/recover/finish through `new_test_pipes`, recycle prefill/reuse behavior, and corruption-handling tests elsewhere that rely on `recover_queue_imp` truncation semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/pipe_builder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/reader.rs -->
# sources/storage-engines/raft-engine/src/file_pipe_log/reader.rs

## Purpose
`reader.rs` provides `LogItemBatchFileReader`, a reusable, buffered, format-aware iterator over `LogItemBatch` records in one physical log file. It is used by recovery, debugging, and filtering paths to decode persisted batches without loading an entire file.

## Important APIs, Types, And Functions
`LogItemBatchFileReader<F>` tracks the current `FileId`, parsed `LogFileFormat`, optional `LogFileReader`, file size, an internal prefetch buffer, the buffer's file offset, the last valid decoded offset, and the configured read block size.

`new` initializes an unopened reader. `open` parses the log file header, records the encoded header length as the first valid offset, stores file size and reader, clears the buffer, and returns the parsed format. `reset` clears all state. `next` decodes the next `LogItemBatch` or returns `None` at EOF. `valid_offset` exposes the end of verified data for truncation decisions during recovery. `peek` is the internal buffered read and prefetch primitive.

## Control Flow
`next` loops while `valid_offset < size`. It first decodes a 16-byte `LogBatch` header at `valid_offset`. If header decoding fails and the format uses alignment, it rounds up to the next alignment and skips zero padding; non-zero padding or a still-broken aligned header becomes corruption. Once the header is decoded, it validates that the whole batch fits within the file size, builds a `FileBlockHandle` pointing to the entries block, and decodes the footer with `LogItemBatch::decode`. Successful decode advances `valid_offset` by the full batch length and returns the batch.

`peek` serves slices from the internal buffer when possible. If the requested offset is beyond the current buffer, it resets the buffer to that offset and reads at least `max(size + prefetch, read_block_size)`. If the request partially extends beyond the buffer, it appends another read. EOF is an error when fewer than required bytes are available.

## State And Persistence Behavior
The reader does not mutate files. Its key state output is `valid_offset`, which recovery uses as the truncation boundary after a corrupted tail. The `LogItemBatch::decode` call receives a `LogFileContext` built from `file_id` and parsed format version, so V2 signed checksums are verified against the physical file identity.

## Dependencies And Integration Points
It depends on `LogFileReader`, `LogFileFormat`, `is_zero_padded`, `LogBatch` header decoding, `LogItemBatch` footer decoding, `FileBlockHandle`, and `round_up`. `DualPipesBuilder::recover_queue_imp`, `debug::LogItemReader`, and `RhaiFilterMachine` all rely on its decode ordering and corruption boundaries.

## Risks And Edge Cases
If a file header is shorter than the encoded format length, `open` fails through `parse_format`. `next` treats any batch header with length beyond file size as corruption. In alignment mode it only skips zero padding when the current offset is not already aligned; corrupted padding becomes a header error. The buffering logic assumes monotonic reads within a file and debug-asserts requested offsets are not before `buffer_offset`.

## Test Signals
Reader behavior is exercised by debug-reader tests, log-batch encode/decode tests, and recovery tests that parse real files. Important signals include empty well-formed files returning `None`, corrupted files returning errors, alignment padding tolerance, checksum verification, and recovery truncation using `valid_offset`.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/file_pipe_log/reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/filter.rs -->
# sources/storage-engines/raft-engine/src/filter.rs

## Purpose
`filter.rs` implements a scripting-enabled replay machine that filters existing raft-engine log files using Rhai callbacks. It replays log items, tracks a simplified per-Raft-group state, decides whether to keep or discard incoming or existing data, and rewrites affected files safely.

## Important APIs, Types, And Functions
`FilterResult` has three outcomes: default application, discard the incoming item, or discard existing state. `RaftGroupState` tracks `first_index`, total entry `count`, and `rewrite_count`; `apply` validates and updates state for entry indexes, compact commands, and clean commands.

`RhaiFilter` owns an `Arc<Engine>`, compiled `AST`, and `Scope`. `filter` dispatches to optional Rhai functions `filter_append`, `filter_compact`, and `filter_clean`, passing raft group state, queue, and incoming item details. Missing functions default to no filtering; other script errors become corruption.

`RhaiFilterMachine` implements `ReplayMachine`. It stores file-local retained items and per-group states. `replay_item` applies script decisions, marks files as filtered when items are removed or existing state is discarded, updates group state, and stores retained items. `merge` replays the right-hand machine's retained items into the left machine so global state is recomputed in order.

`finish` rewrites only filtered files. It renames each target to `.bak`, installs a `scopeguard` recovery action, reads raw entry bytes from the backup, rebuilds `LogBatch` records in about 64 KiB chunks, writes the new file with the original format, closes it, then removes backups and defuses guards. `RhaiFilterMachineFactory::from_script` compiles and validates a script, and its `Factory` implementation creates fresh machines with shared engine and AST.

## Control Flow
During recovery, batches enter `RhaiFilterMachine::replay`. A new `FileAndItems` bucket is started whenever the `FileId` changes. Each item is inspected against current state. `DiscardIncoming` drops the item and marks the current file for rewrite. `DiscardExisting` marks the file, clears the state, injects a synthetic `Compact { index: u64::MAX }` command, then applies and stores the incoming item. Default applies and stores the item.

After replay, callers invoke `finish` to persist changes. Entry-index items require reading the original entry block from the `.bak` file, decoding it, slicing out each entry by offset and length, and re-adding raw entries to a new batch. Commands and key-values are copied logically. Any failure before guard defusal attempts to restore the original `.bak` over the target.

## State And Persistence Behavior
The replay phase is in-memory and deterministic over ordered log items. Persistence changes happen only in `finish`, and only for files marked `filtered`. The rewrite preserves log file format and file name but may pack items into different physical batch boundaries. Backup files use the `.bak` extension beside the original file. The panic-on-restore-failure guard makes partial failure visible and tells operators to manually restore from backup.

The state model treats append holes or writes to compacted entries as corruption, while rewrite holes or compacted overlaps clear state. Rewrite entries must be contiguous with the current rewrite prefix.

## Dependencies And Integration Points
This module is gated by the crate's `scripting` feature. It depends on Rhai, `hashbrown`, `scopeguard`, debug file readers/writers, `ReplayMachine`, `LogBatch`, `LogItemBatch`, `EntryIndexes`, `Command`, `KeyValue`, `LogQueue`, and `Factory`. It plugs into `DualPipesBuilder::recover` as a custom replay machine, then uses debug I/O helpers to rewrite physical files.

## Risks And Edge Cases
`RhaiFilterMachineFactory::from_script` unwraps compilation and initial execution errors, so invalid scripts panic rather than returning `Result`. `FilterResult::from_i64` treats unexpected script return values as unreachable and can panic. `finish` uses `Path::exists` on backup paths directly, which bypasses the `FileSystem` abstraction for that check and removal. Rewriting changes batch layout and requires entry bytes to decode successfully from backups. The state model is intentionally simplified and may not represent every engine invariant.

## Test Signals
No tests are defined in this file. Its behavior is indirectly testable through scripting-feature recovery flows: script callback dispatch, missing callback defaults, state corruption detection, backup restoration on rewrite failure, and final engine recovery from filtered files are the important signals to cover.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/filter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/fork.rs -->
# sources/storage-engines/raft-engine/src/fork.rs

## Purpose
`fork.rs` implements `Engine::fork` for `Engine<F, FilePipeLog<F>>`, creating a minimally copied clone of an unopened raft-engine directory. It lets source and target engines run independently afterward by symlinking immutable inactive files and copying each queue's active tail file.

## Important APIs, Types, And Functions
`CopyDetails` reports `copied` and `symlinked` destination paths. `Engine::fork` is the public method and delegates to `minimum_copy`. `minimum_copy` validates configuration, creates the target directory, scans source log files without locking, then iterates append and rewrite file lists.

For each queue, every file except the last is symlinked into the target using the queue filename built from `FileId`; the last file is copied. Paths recorded in `CopyDetails` are canonicalized destination paths.

## Control Flow
`minimum_copy` first rejects `enable_log_recycle = true`, because recycled file reuse could mutate files shared by symlink. It also rejects `RecoveryMode::TolerateAnyCorruption`, because that mode may rewrite or truncate shared symlinked files during recovery. It sanitizes a cloned config, creates the target directory, builds a `FilePipeLogBuilder`, and calls `scan_and_sort(false)` so it can discover files without taking directory locks.

The file iteration preserves queue order from the builder. If a queue has N files, files `[0..N-1)` are symlinked and file `N-1` is copied. The active copied tail gives each fork an independent append point while sharing stable history.

## State And Persistence Behavior
The function writes a new target directory containing symlinks and copies. It does not mutate source files. It assumes the source engine is not open; the doc comment warns that using an active source can corrupt data because the scan and copy are not coordinated with concurrent writes.

## Dependencies And Integration Points
It depends on `Config`, `RecoveryMode`, `FileSystem`, `FilePipeLogBuilder::scan_and_sort`, `FileNameExt`, `FileId`, and OS symlink APIs. The impl is specialized for `Engine<F, FilePipeLog<F>>`, so other `PipeLog` implementations do not receive this method.

## Risks And Edge Cases
The target must not already exist as conflicting files; `create_dir_all` permits an existing directory, so later symlink or copy calls fail if destination names exist. The source is scanned without locking, relying on the caller to ensure it is closed. Canonicalization unwraps after symlink/copy success and can panic if the destination cannot be canonicalized. On Windows it uses file symlinks, which may require privileges or developer mode.

## Test Signals
`test_fork` writes several key-value batches and rewrite cycles, forks the source, opens the target, verifies all pre-fork keys are visible, then verifies source and target can diverge independently. It also asserts rejection when log recycle is enabled or recovery mode is `TolerateAnyCorruption`.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/fork.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/lib.rs -->
# sources/storage-engines/raft-engine/src/lib.rs

## Purpose
`lib.rs` is the crate root for raft-engine. It declares feature gates and modules, defines core public exports, provides a crate-wide boxed-error macro, tracks global entry statistics, and enforces the internal-key namespace used by atomic group metadata.

## Important APIs, Types, And Functions
`box_err!` formats a boxed error with source file and line. Public exports include `Config`, `RecoveryMode`, `Engine`, `Error`, `Result`, `Command`, `LogBatch`, `MessageExt`, performance-context helpers, `Version`, and `ReadableSize`. `env` is public, while most implementation modules are private.

The `internals` feature exposes selected internal modules for advanced users or tests: event listeners, file pipe log internals, memtable, pipe log, purge, optional swap allocator, and write barrier.

`GlobalStats` holds relaxed atomics for live append entries, rewrite entries, and deleted rewrite entries. `add`, `delete`, `rewrite_entries`, `deleted_rewrite_entries`, `reset_rewrite_counters`, `live_entries`, and `flush_metrics` update and report logical entry counts by queue.

`INTERNAL_KEY_PREFIX`, `make_internal_key`, and `is_internal_key` reserve internal keyspace. In non-test builds, only the atomic group key is recognized when checking the prefix without an explicit extension; in tests, any prefixed key can be treated as internal to validate broader behavior.

## Control Flow
The crate root mostly configures compile-time structure. Runtime calls to `GlobalStats` increment append or rewrite counters when entries are added and decrement or mark deleted when entries are removed. `live_entries` computes rewrite live count as total rewrite entries minus deleted rewrite entries with saturating subtraction, and `flush_metrics` publishes both queue counts.

Internal keys are created by prefixing an extension with `b"__"`. User-facing `LogBatch::put` and `put_message` reject such keys, while internal code uses unchecked insertion for atomic group markers. Replay paths filter internal keys so they do not become user-visible.

## State And Persistence Behavior
`GlobalStats` is in-memory observability state only. Internal keys are persisted as ordinary key-value log items but use a reserved prefix and are filtered from user state. The comments explicitly note that this protects current and future internal keys from being visible after downgrade as long as old versions also respect the prefix.

## Dependencies And Integration Points
`lib.rs` ties all major modules together: config, consistency, engine, errors, event listeners, file pipe log, optional filter, fork, log batch, memtable, metrics, pipe log, purge, utility code, and write barrier. `LogBatch` depends on `make_internal_key` and `is_internal_key` for atomic groups; metrics code depends on `GlobalStats::flush_metrics`.

## Risks And Edge Cases
The relaxed atomic counters are appropriate for metrics but not for synchronization. `reset_rewrite_counters` subtracts the current deleted count from both rewrite counters and assumes concurrent use tolerates approximate accounting. Non-test `is_internal_key(s, None)` only checks the atomic group extension, so adding future internal keys requires updating this function. `box_err!` embeds file and line, which is useful diagnostically but can make exact error strings unstable.

## Test Signals
The test module initializes env logging, implements `MessageExt` for raft `Entry`, and verifies internal-key matching with and without explicit extensions. Many crate-wide tests depend on that `MessageExt` implementation when encoding raft entries into `LogBatch`.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/log_batch.rs -->
# sources/storage-engines/raft-engine/src/log_batch.rs

## Purpose
`log_batch.rs` defines the logical and physical batch format for raft-engine log writes. It serializes raft entry indexes, commands, and key-value operations; stores entry bytes in a contiguous entries block; optionally compresses entry bytes; signs and verifies checksums; tracks post-write file handles; and embeds atomic group markers for persistent multi-batch rewrite atomicity.

## Important APIs, Types, And Functions
`MessageExt` abstracts over protobuf entry types so `LogBatch::add_entries` can obtain raft log indexes. `CompressionType` currently supports `None` and `Lz4`.

`EntryIndexes` encodes a count, first index, and tail offsets, reconstructing per-entry `EntryIndex` offsets and lengths during decode. `Command` supports `Clean` and `Compact { index }`. `OpType` supports `Put` and `Del`; `KeyValue` encodes operation type, key, and optional value plus an optional source `FileId`.

`LogItem` combines a raft group id with `LogItemContent` (`EntryIndexes`, `Command`, or `Kv`). `LogItemBatch` is the footer-only batch of logical items. It can merge batches, encode/decode item metadata, update entry compression type, sign footer checksum with a `LogFileContext`, and fill entry or key-value file locations after the physical write.

`LogBatch` is the full write unit. It owns a `LogItemBatch`, a state-machine enum `BufState`, and the encoded buffer. Public mutation methods include `merge`, `add_entries`, `add_command`, `delete`, `put_message`, `put`, `is_empty`, and `approximate_size`. Crate-internal persistence methods include `finish_populate`, `prepare_write`, `encoded_bytes`, `finish_write`, `drain`, `decode_header`, and `decode_entries_block`.

`verify_checksum_with_signature` validates a trailing CRC32, optionally XORing the expected checksum with a file-context signature. `AtomicGroupStatus` parses internal key markers. `AtomicGroupBuilder` writes begin, middle, and end markers using reserved internal keys.

## Control Flow
A normal write starts with an open `LogBatch` containing a 16-byte header placeholder. Callers add entries and metadata. Entry bytes are appended after the header while corresponding `EntryIndex` records are added to the item footer with offsets relative to the entries block. `finish_populate` optionally LZ4-compresses the entries block, appends an entries CRC, records the footer offset, encodes the `LogItemBatch`, writes the big-endian header `{u56 len | u8 compression type, u64 footer offset}`, and moves the buffer to `Encoded`.

`prepare_write` signs the footer checksum using the target `LogFileContext` and moves the batch to `Sealed`. `encoded_bytes` then exposes the exact slice to write. After the pipe returns a `FileBlockHandle`, `finish_write` adjusts it from full batch to entries-block coordinates and stores it into each entry index or key-value metadata. `drain` resets the buffer to the header placeholder and returns logical items for memtable application.

Decoding reverses this structure. `decode_header` validates the 16-byte header and returns footer offset, compression type, and total batch length. `LogItemBatch::decode` verifies the signed footer checksum, decodes item metadata, assigns entry handles and compression types, and records key-value file ids. `decode_entries_block` verifies the entries-block checksum and decompresses if needed.

## State And Persistence Behavior
`BufState` prevents invalid call ordering: `Open` accepts mutations, `Encoded` is populated but unsigned for a specific file, `Sealed` is ready to write, and `Incomplete` protects temporary mutation windows. Several methods use debug assertions or `unreachable!`, so violating the call protocol can panic.

The on-disk batch has a fixed 16-byte header, optional entries block plus CRC, and footer item batch plus CRC. For V2-style signed log files, footer checksums are XORed with the log file signature derived from file id and version, detecting batches moved to the wrong file. Entries-block checksums are not signed. Empty batches encode to length zero and carry no physical data.

The entries block is limited to `i32::MAX` bytes for LZ4 compatibility. User `put` and `put_message` reject reserved internal-key prefixes; atomic group markers bypass that via `put_unchecked`.

Atomic group markers are persisted as internal key-value items with an atomically assigned group id and status byte. Recovery can parse these markers and treat groups as persistent rewrite units, with caveats documented in the file: in-memory state may differ after failure until recovery, replay order is group-level rather than original write order, and older versions may expose markers as user keys.

## Dependencies And Integration Points
This file depends on varint and fixed-number codec helpers, protobuf `Message`, memtable `EntryIndex`, metrics `StopWatch`, `pipe_log` handles and contexts, CRC32 and LZ4 utilities, and crate-level internal-key helpers. `Engine` write paths build `LogBatch` values, `file_pipe_log::pipe` writes them through `ReactiveBytes`, `reader` and recovery decode them, `filter` rewrites them, and memtable/purge logic consumes the drained `LogItem`s and file handles.

## Risks And Edge Cases
`CompressionType::from_u8` and `OpType::from_u8` use `transmute` after range checks; this is compact but relies on enum discriminants remaining dense from zero or one as implemented. `KeyValue::decode` trusts encoded lengths enough to slice the input, so malformed short buffers can panic if codec length validation does not catch them first. Many call-order violations panic rather than returning errors. `AtomicGroupStatus::parse` unwraps status conversion and can panic on a malformed internal marker value. Repeated `prepare_write` intentionally re-signs the same populated batch for different file contexts; tests cover this, but callers must not mutate content afterward.

## Test Signals
Tests cover entry-index encoding, command encoding, key-value encoding including invalid op types and delete-with-value behavior, log-item encoding, `LogItemBatch` signing and decoding, full `LogBatch` encode/decode across versions and compression modes, merge offset adjustment, empty batches, internal-key rejection, header corruption, repeated signature signing, and a nightly encode benchmark. These tests also verify wrong file/version signatures fail under signed versions and that decoded entries match original raft protobuf entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/log_batch.rs -->
