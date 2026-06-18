# subset-b-008988 research

Grouped research report for WiredTiger logging, metadata, operation tracking, and OS abstraction files. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_slot.c -->
# sources/storage-engines/wiredtiger/src/log/log_slot.c

## Purpose
Implements WiredTiger's consolidated logging slot pool. Threads join an active `WTI_LOGSLOT`, reserve space for their log record, copy or write their portion, and release it so the log writer can flush a larger combined buffer instead of many small writes.

## Important APIs, Types, and Functions
Key public/internal entry points are `__wti_log_slot_init`, `__wti_log_slot_destroy`, `__wti_log_slot_join`, `__wti_log_slot_release`, `__wti_log_slot_switch`, `__wti_log_slot_activate`, and `__wti_log_slot_free`. The core types are `WTI_LOG`, `WTI_LOGSLOT`, and `WTI_MYSLOT`; slot state encodes joined bytes, released bytes, close/unbuffered/reserved flags, and is manipulated with atomic macros from `log_private.h`.

## Control Flow
Initialization marks every pool entry free, allocates buffers, activates slot 0, and installs it as `log->active_slot`. Writers call `__wti_log_slot_join`, loop on the active slot until they can atomically add their record size, then return the slot pointer and offsets. Oversized records or diagnostic forcing mark the join as unbuffered. `__wti_log_slot_release` advances `slot_last_offset` and atomically adds the released size. Slot switching takes the slot lock, closes the current active slot, installs a new free slot, and releases the old slot to the write path when every joined writer has released.

## State and Persistence Behavior
Slot state is in memory, but it controls persistent log file offsets and write ordering. Closing a slot computes `slot_end_lsn` from buffered and unbuffered sizes, advances `log->alloc_lsn`, and may schedule dirty-log or explicit sync flags on the slot. Destroy writes any unreleased buffered bytes before freeing buffers. Release LSNs and file handles bridge slot switching across log file rotation.

## Dependencies and Integration Points
The file depends on `wt_internal.h`, `log_private.h`, LSN helpers, log allocation/release/fill routines, stats counters, slot spinlock macros, condition variables, and connection panic handling. It integrates with `log_write.c` style callers that join/fill/release slots and with the write-LSN worker that drains closed slots.

## Risks and Edge Cases
The state word is concurrency-critical: stale slot pointers, CAS races, unbuffered handoff, and forced switching all depend on exact flag ordering. `__log_slot_close` waits for unbuffered size publication and aborts under slow-operation diagnostics if it appears stuck. `__log_slot_new` can spin if all slots are reserved and must release the slot lock to let the writer progress. Forced switches return `EBUSY` if writers are in progress. Buffer sizing is capped to one tenth of the log file maximum to avoid aggressive rotations.

## Test Signals
Useful signals are stress tests with many concurrent log writers, log file rotation, forced fsync/dsync/flush paths, oversized log records, incremental backup/system records, crash recovery, and diagnostic builds that exercise timeout dumps. Counters such as `log_slot_races`, `log_slot_yield`, `log_slot_no_free_slots`, `log_slot_unbuffered`, and `log_slot_switch_busy` indicate slot behavior under load.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_slot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_sys.c -->
# sources/storage-engines/wiredtiger/src/log/log_sys.c

## Purpose
Builds and writes logging system records and provides a verbose diagnostic dump of the logging subsystem.

## Important APIs, Types, and Functions
`__wt_log_system_backup_id` writes incremental-backup ID state as a `WT_LOGREC_SYSTEM` record. `__wti_log_system_prevlsn` writes a fixed-size previous-LSN system record directly to a chosen log file handle. `__wti_log_recover_prevlsn` unpacks that operation during recovery. `__wt_verbose_dump_log` prints log-manager flags, paths, sizes, sync policy, version, file number, and key LSNs.

## Control Flow
Backup-ID logging exits early unless logging and incremental backup are enabled and the log version supports system records. It packs a system record header, then iterates `WT_BLKINCR_MAX`, packing either each valid ID/granularity or an empty sentinel. Previous-LSN logging builds an aligned record, computes its checksum manually, activates a temporary slot, overrides its file handle, and calls the log fill routine without compression or encryption.

## State and Persistence Behavior
The backup-ID record persists the connection's incremental backup slots in the log so recovery can restore or stop IDs. The previous-LSN record persists a prior LSN marker at a log boundary. The verbose dump is read-only diagnostic output.

## Dependencies and Integration Points
This file depends on log record allocation/packing helpers, backup-ID log operation packing, previous-LSN packing/unpacking, checksum/byteswap helpers, and the slot fill path. Recovery consumes `__wti_log_recover_prevlsn`, while incremental backup and checkpoint/switch logic use the backup ID writer.

## Risks and Edge Cases
The system record path must stay compatible with `log->log_version`. Invalid incremental backup slots are deliberately written with `UINT64_MAX` granularity and an empty string, so recovery code must preserve that sentinel meaning. `__wti_log_system_prevlsn` bypasses the normal log-write path and must maintain alignment, checksum, and endian handling exactly.

## Test Signals
Incremental backup tests should verify ID persistence across restart, force-stop behavior, and recovery from system log records. Recovery tests should cover previous-LSN unpacking. Verbose logging tests or diagnostics can validate expected dump fields under enabled and disabled logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_apply.c -->
# sources/storage-engines/wiredtiger/src/meta/meta_apply.c

## Purpose
Provides a schema-lock-protected iterator that applies callbacks to every btree file entry in WiredTiger metadata, skipping the metadata file itself.

## Important APIs, Types, and Functions
The exported helper is `__wt_meta_apply_all`. Its worker `__meta_btree_apply` accepts a `file_func`, optional `name_func`, and config array. It operates over `WT_CURSOR` metadata entries and temporarily pins matching data handles with `__wt_session_get_dhandle`.

## Control Flow
`__wt_meta_apply_all` asserts the schema lock, obtains a metadata cursor, and delegates iteration. For each metadata key, the worker skips `file:WiredTiger.wt`, calls `name_func` to decide whether to skip, ignores non-btree prefixes, then opens the handle. Busy handles are tolerated with `WT_TRET_BUSY_OK`; successful opens run `file_func` with the dhandle saved/restored and then release the handle.

## State and Persistence Behavior
The file itself writes no metadata. It pins and releases data handles so callbacks can safely inspect or mutate btree state without the handle being concurrently dropped. Persistence effects depend entirely on the supplied callback.

## Dependencies and Integration Points
It integrates metadata cursor access, schema lock discipline, data-handle cache management, and bulk operations such as checkpoint, verification, or schema scans that need to visit all btrees.

## Risks and Edge Cases
The iterator accumulates errors while continuing to the end, so callers must inspect the final return. Busy handles are skipped rather than fatal, which is correct for some global operations but can hide work not performed. Callback code runs with the target dhandle active and must respect the surrounding schema-lock assumptions.

## Test Signals
Tests that run checkpoint or metadata-wide operations while handles are busy, bulk-loading, or being verified should show skips rather than crashes. Error aggregation can be tested with callbacks that fail for selected entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_apply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_ckpt.c -->
# sources/storage-engines/wiredtiger/src/meta/meta_ckpt.c

## Purpose
Owns parsing, validating, querying, and rewriting checkpoint-related metadata for btree files and system checkpoint state. It translates metadata config strings into `WT_CKPT` structures and serializes updated checkpoint lists, timestamps, snapshots, live-restore metadata, and incremental-backup block-modification information back into metadata.

## Important APIs, Types, and Functions
Major APIs include `__wt_meta_checkpoint`, `__wt_meta_checkpoint_last_name`, `__wt_meta_checkpoint_by_name`, `__wt_meta_checkpoint_clear`, `__wt_ckpt_last_name`, `__wt_ckpt_last_size`, `__wt_meta_ckptlist_get`, `__wt_meta_ckptlist_get_from_config`, `__wt_meta_ckptlist_to_meta`, `__wt_meta_ckptlist_update_config`, `__wt_meta_ckptlist_set`, `__wt_meta_sysinfo_set`, `__wt_meta_sysinfo_clear`, `__wt_meta_read_checkpoint_snapshot`, `__wt_meta_read_checkpoint_timestamp`, `__wt_meta_read_checkpoint_oldest`, `__wt_meta_load_prior_state`, `__wt_meta_correct_base_write_gen`, and `__wt_reset_blkmod`. Important private helpers include `__ckpt_load`, `__ckpt_last`, `__ckpt_named`, `__ckpt_set`, `__ckpt_version_chk`, `__meta_blk_mods_load`, `__ckpt_blkmod_to_meta`, and `__ckpt_parse_time`.

## Control Flow
Read paths fetch a metadata config with `__wt_metadata_search`, check btree version compatibility, parse the `checkpoint` config array, and select either a named checkpoint or the highest-order checkpoint. List paths either reuse `btree->ckpt` or rebuild from config, sorting by order and optionally allocating a new add checkpoint. Write paths convert a `WT_CKPT` list to `checkpoint=(...)`, append live-restore and `checkpoint_backup_info` strings when needed, add a checkpoint LSN if supplied, and call `__ckpt_set` to collapse the new config into the file metadata. System info paths write or remove `system:checkpoint`, `system:oldest`, and `system:checkpoint_snapshot` entries, including named variants.

## State and Persistence Behavior
The file persists checkpoint addresses, raw cookies as hex strings, order, wall-clock time, size, time aggregates, write generations, run write generations, disaggregated next page IDs, checkpoint LSNs, incremental backup block bitmaps, encrypted block metadata, live-restore file-handle metadata, checkpoint timestamps, oldest timestamps, snapshot arrays, and base write generation. It updates connection state such as `base_write_gen` and `ckpt.most_recent` from prior metadata at startup and after recovery.

## Dependencies and Integration Points
It depends on the metadata table layer, config parser/collapser, btree/block manager checkpoint state, encryption helpers, live restore, tiered/disaggregated storage, incremental backup, timestamp parsing, transaction snapshot data, and version compatibility definitions. It is central to checkpoint, recovery, backup, rollback-to-stable, live restore, and startup compatibility checks.

## Risks and Edge Cases
Unsigned wall-clock times are parsed manually because config numeric values are signed. Backward compatibility is maintained for older durable timestamp field names and missing runtime write generation or `next_page_id`. Cached checkpoint lists must match metadata; diagnostic validation compares both paths. `__ckpt_set` can use the dhandle metadata base fast path but panics if the base hash changed unexpectedly. Incremental backup block-mod state must be reset when IDs change or files are renamed. Snapshot parsing assumes count/list consistency. System timestamp entries are removed instead of storing zero to preserve downgrade compatibility.

## Test Signals
Strong signals include checkpoint/restart/recovery suites, named checkpoint queries, timestamp and snapshot recovery tests, compatibility/downgrade tests, incremental backup rename/reset tests, encrypted metadata tests, live-restore metadata tests, disaggregated checkpoint size accounting, and diagnostic checkpoint validation comparing cached and rebuilt lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_ckpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_ext.c -->
# sources/storage-engines/wiredtiger/src/meta/meta_ext.c

## Purpose
Exposes selected metadata operations through the extension/public API boundary.

## Important APIs, Types, and Functions
The extension wrappers are `__wt_ext_metadata_insert`, `__wt_ext_metadata_remove`, `__wt_ext_metadata_search`, and `__wt_ext_metadata_update`, all taking `WT_EXTENSION_API` plus an optional `WT_SESSION`. Public utility entry points are `__wt_metadata_get_ckptlist` and `__wt_metadata_free_ckptlist`, exported for the `wt list` tool.

## Control Flow
Each extension wrapper maps `wt_api->conn` to `WT_CONNECTION_IMPL`, falls back to `conn->default_session` when the caller passes `NULL`, then delegates to the internal metadata function. Checkpoint-list retrieval delegates to `__wt_meta_ckptlist_get` and freeing delegates to `__wt_ckptlist_free`.

## State and Persistence Behavior
Insert/update/remove wrappers can modify metadata and therefore durable schema/checkpoint state. Search returns an allocated copy that the caller must free. The checkpoint-list API allocates a `WT_CKPT` array and expects callers to release it through the matching free function.

## Dependencies and Integration Points
This file bridges `wiredtiger_ext.h` users and internal metadata APIs. Examples and extensions that demonstrate metadata operations depend on this wrapper layer instead of directly including internal symbols.

## Risks and Edge Cases
Using the default session when `wt_session` is `NULL` is convenient but can bypass caller-specific isolation or error context. Extension callers must obey metadata locking expectations even though this layer does not acquire schema locks itself. Search allocation ownership is explicit and easy to leak.

## Test Signals
Extension API examples that insert/search/update/remove metadata exercise these wrappers. `wt list` and checkpoint-list listing paths validate the exported checkpoint-list functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_table.c -->
# sources/storage-engines/wiredtiger/src/meta/meta_table.c

## Purpose
Implements the common metadata table access layer, including cached metadata cursors and special routing for bootstrap keys stored in the turtle file.

## Important APIs, Types, and Functions
Key functions are `__wt_metadata_cursor_open`, `__wt_metadata_cursor`, `__wt_metadata_cursor_release`, `__wt_metadata_cursor_close`, `__wt_metadata_insert`, `__wt_metadata_update`, `__wt_metadata_remove`, `__wt_metadata_search`, `__wt_metadata_turtle_rewrite`, `__wt_metadata_btree_id_to_uri`, and `__wt_verbose_dump_metadata`. `__metadata_turtle` identifies keys handled by the turtle file: metadata file URI, version, compatibility, version string, and live-restore state.

## Control Flow
Cursor open uses `__wt_open_cursor` on `file:WiredTiger.wt` without an active dhandle and skews metadata eviction priority. `__wt_metadata_cursor` reuses a per-session cached cursor unless it is already marked in use, in which case it opens a temporary cursor. Insert rejects turtle keys. Update routes turtle keys through live-restore turtle update or locked turtle update, otherwise records meta tracking when active and performs overwrite insert. Remove first searches and releases the cursor so meta tracking can use the cached cursor, then removes the key. Search routes turtle keys to turtle readers and reads normal metadata at read-uncommitted isolation.

## State and Persistence Behavior
Normal metadata writes persist schema, file, checkpoint, and system entries in the metadata btree. Turtle-key updates rewrite the text turtle file. Session state includes `session->meta_cursor` and `WT_CURSTD_META_INUSE`; cursor release either resets the cached cursor or closes temporary cursors. Metadata reads intentionally use read-uncommitted isolation because schema/metadata locks, not normal transactions, serialize metadata updates.

## Dependencies and Integration Points
The file depends on cursor APIs, metadata/turtle locks, live-restore turtle hooks, meta tracking, eviction priority, config strings, and diagnostic message output. It is the central dependency for schema, checkpoint, recovery, extension, and diagnostic metadata operations.

## Risks and Edge Cases
Turtle keys cannot be inserted or removed through normal metadata operations. Cursor caching requires correct in-use flag handling to avoid nested metadata operations clobbering the cursor. Read-uncommitted metadata access is intentional but means correctness relies on external locks. Remove performs a pre-search so that rollback can restore prior values. `__wt_metadata_btree_id_to_uri` scans all metadata and tolerates entries without `id`.

## Test Signals
Schema create/drop/rename tests, metadata cursor nesting, turtle update/read paths, live-restore turtle operations, metadata rollback, and verbose metadata dumping all exercise this layer. Eviction behavior should keep the metadata btree highly resident under cache pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_track.c -->
# sources/storage-engines/wiredtiger/src/meta/meta_track.c

## Purpose
Provides a non-transactional metadata operation log used to roll back failed schema operations and apply post-commit filesystem cleanup.

## Important APIs, Types, and Functions
The private `WT_META_TRACK` records operations such as checkpoint resolution, deferred file drop, deferred object drop, file operation rollback, handle lock release, metadata remove, and metadata set. Public helpers include `__wt_meta_track_on`, `__wt_meta_track_off`, `__wt_meta_track_sub_on`, `__wt_meta_track_sub_off`, `__wt_meta_track_checkpoint`, `__wti_meta_track_insert`, `__wti_meta_track_update`, `__wt_meta_track_fileop`, `__wt_meta_track_drop`, `__wt_meta_track_drop_object`, `__wt_meta_track_handle_lock`, `__wt_meta_track_init`, `__wt_meta_track_destroy`, and `__wt_meta_track_discard`.

## Control Flow
Tracking turns on by incrementing a nest counter and allocating the operation array. Each metadata or filesystem action appends a record, duplicating strings or saving handles as needed. `__wt_meta_track_off` disables tracking at the outer level, optionally checkpoints/log-syncs metadata, then either applies records in forward order or unrolls in reverse order. Subtracking lets a suffix of operations be applied independently before the enclosing operation finishes.

## State and Persistence Behavior
Tracking state lives on `WT_SESSION_IMPL` as a dynamically grown operation array, next pointer, subtransaction pointer, allocation size, and nesting count. Commit paths may checkpoint or log-sync metadata, resolve block-manager checkpoints, release handles, and physically drop files/objects. Unroll paths restore metadata values, remove newly inserted metadata, undo creates/renames when possible, release locked handles, and mark newly created handles for discard.

## Dependencies and Integration Points
It integrates metadata updates, schema operations, block manager checkpoint resolution, filesystem rename/remove, object storage drops, session handle locking, sweep thread wakeup, log checkpoint sync, and the separate `meta_ckpt_session` used when logging is disabled.

## Risks and Edge Cases
The operation log is not a general transaction system: file removes cannot be undone, so schema code must order operations carefully. Nested tracking must leave the outer operation array consistent after sub-off. If apply/unroll fails, the connection panics because metadata state may be inconsistent. Metadata checkpoints are skipped in in-memory or no-op cases. The non-logged path copies transaction time-point state into `meta_ckpt_session`, so isolation and locking assumptions matter.

## Test Signals
Failed create/drop/rename/alter tests should verify metadata and filesystem rollback. Checkpoint failure injection should exercise `WT_ST_CHECKPOINT` unroll. Logged and non-logged metadata updates, in-memory drops, tiered object drops, and session close cleanup validate the major paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_track.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_turtle.c -->
# sources/storage-engines/wiredtiger/src/meta/meta_turtle.c

## Purpose
Bootstraps and maintains the turtle file, the small text file that points to the metadata btree and stores startup-critical metadata such as version, compatibility, and live-restore state. It also loads metadata from hot-backup files and handles partial-backup restore setup.

## Important APIs, Types, and Functions
Primary APIs include `__wt_turtle_exists`, `__wt_turtle_init`, `__wt_turtle_validate_version`, `__wt_turtle_read`, `__wt_turtle_update`, and `__wt_read_metadata_file`. Private helpers create default metadata config, create the metadata file, load `WiredTiger.backup`, rebuild missing bulk-load stubs, manage partial backup target URI hashes, and process metadata backup entries.

## Control Flow
Startup removes leftover turtle set files when allowed, checks for `WiredTiger.backup` and `WiredTiger.turtle`, and either validates the existing turtle or rebuilds metadata from backup. When loading backup metadata, it reads key/value line pairs, updates metadata, and for partial restores records non-target tables so schema drop can clean linked entries and collect btree IDs for history-store truncation. If metadata is newly loaded or the turtle was unreadable under salvage, it writes a new turtle file with default metadata config.

## State and Persistence Behavior
The turtle file is rewritten by creating `WiredTiger.turtle.set`, writing compatibility/live-restore/version/key/value pairs, syncing, and renaming into place. `__wt_turtle_read` returns default metadata config when the turtle file is absent during initial metadata creation. Hot backup loading sets connection flags such as `WT_CONN_WAS_BACKUP` and partial-restore state. Version validation stores `conn->recovery_version`.

## Dependencies and Integration Points
This file depends on the stream layer, filesystem exists/remove/rename helpers, schema create/drop, metadata table updates, config parsing, live restore turtle hooks, backup target hashes, block manager bulk file creation, version compatibility helpers, and the turtle lock.

## Risks and Edge Cases
Windows rename behavior can leave only the turtle set file; `__wt_turtle_exists` repairs that by renaming it into place. Turtle read failures normally panic with `WT_TRY_SALVAGE`, except optional compatibility/live-restore keys or salvage mode. Restore from backup is incompatible with metadata verification. Partial backup restore only accepts `table:` targets and must load all metadata first so schema drop can clean secondary references. Turtle updates are fatal on failure because startup metadata may be corrupt.

## Test Signals
Startup/reopen tests, salvage with corrupted turtle files, backup restore, partial backup restore, live restore, compatibility-version checks, bulk-load backup restore, and failpoint-style abort before turtle update are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/meta/meta_turtle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/optrack/optrack.c -->
# sources/storage-engines/wiredtiger/src/optrack/optrack.c

## Purpose
Implements lightweight operation tracking output: mapping function names to process-unique IDs and flushing per-session binary operation records to session-specific files.

## Important APIs, Types, and Functions
`__wt_optrack_record_funcid` assigns and records a 16-bit function ID. `__optrack_open_file` creates the current session's optrack file and writes `WT_OPTRACK_HEADER`. `__wt_optrack_flush_buffer` opens the file on demand and writes buffered `WT_OPTRACK_RECORD` entries.

## Control Flow
Function ID recording allocates scratch space, locks `conn->optrack.map_spinlock`, assigns the static process-lifetime ID if the caller's ID is zero, appends `id name` to the map file, and panics on initialization failures. Flush opens the session file if needed, then directly calls the file handle's `fh_write` at `session->optrack_offset` and advances the offset on success.

## State and Persistence Behavior
Persistent artifacts are the optrack map file and per-session optrack files named by path, process ID, and session ID. Session state includes `optrack_fh`, `optrack_offset`, buffer pointer, and record buffer. The header persists version, internal-session flag, timestamp-counter conversion ratio, and epoch seconds.

## Dependencies and Integration Points
It depends on filename construction, file handle open/write/size, scratch buffers, connection optrack configuration, process timing ratio, and the session instrumentation macros that fill `optrack_buf`.

## Risks and Edge Cases
The function ID counter is static and 16-bit, so extremely many instrumented functions would wrap. The hot flush path deliberately bypasses standard write wrappers for overhead, so it also bypasses some accounting and throttling. Failed file opening just drops flush output. Map-file failures panic because IDs would become undecodable.

## Test Signals
Enable optrack and verify map-file entries, per-session headers, internal-session flags, monotonically advancing offsets, and decodeability of records. Error injection around map file writes should panic.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/optrack/optrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/filename.c -->
# sources/storage-engines/wiredtiger/src/os_common/filename.c

## Purpose
Provides common path construction, conditional removal, and safe copy-and-sync behavior for WiredTiger files.

## Important APIs, Types, and Functions
Functions include `__wt_filename`, `__wt_filename_construct`, `__wt_remove_if_exists`, and exported `__wt_copy_and_sync`. Private `__nfilename` joins relative names to the connection home while preserving absolute paths.

## Control Flow
`__wt_filename` delegates to `__nfilename`, which handles `NULL` sessions and absolute names by duplicating the input. Generated names append a prefix and optional zero-padded identifiers. `__wt_remove_if_exists` checks existence and refuses removal on read-only connections. `__wt_copy_and_sync` removes existing target/temp files, opens source and exclusive temp destination, copies in 128 KiB chunks, fsyncs the temp file, closes both handles, and renames temp into place.

## State and Persistence Behavior
Path helpers allocate caller-owned strings or buffers. Remove and copy paths modify the filesystem; copy uses a temp file plus fsync and durable rename to avoid leaving a silently corrupted target.

## Dependencies and Integration Points
The file depends on path separator/absolute-path helpers, allocation, file-system exists/remove/rename, `WT_FH` open/read/write/fsync/close, and stream-safe scratch buffers. Backup and tooling code use `__wt_copy_and_sync`.

## Risks and Edge Cases
`__wt_remove_if_exists` returns `EACCES` for read-only homes even if the caller expected cleanup. `__wt_copy_and_sync` removes the original target before a successful copy; recovery relies on the temp name and caller context. Name construction resets the buffer only when a non-empty path is supplied, so callers must understand append behavior.

## Test Signals
Tests should cover absolute and relative paths, `NULL` session use by test utilities, read-only remove failures, copy of empty and large files, interruption before rename, and target replacement semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/filename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_abort.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_abort.c

## Purpose
Centralizes process termination behavior for fatal WiredTiger errors and debug crash injection.

## Important APIs, Types, and Functions
`__wt_abort` logs an abort message, optionally waits for debugger attachment under `HAVE_ATTACH`, sends pending error logs to the event handler, and calls `abort`. `__wt_debug_crash` either calls `__wt_abort` on Windows or kills the process with `SIGKILL` elsewhere.

## Control Flow
`__wt_abort` is marked noreturn and exported. Under attach builds it logs the process ID and sleeps repeatedly; otherwise it logs a generic abort message. `__wt_debug_crash` chooses core-producing abort on Windows and non-core SIGKILL on POSIX-like systems.

## State and Persistence Behavior
There is no normal persistent state, but fatal termination can leave partial database state for recovery tests. Error logs are flushed to the configured handler before aborting.

## Dependencies and Integration Points
The file depends on signal/process APIs, `__wt_errx`, `__wt_error_log_to_handler`, and platform feature macros. It is used by panic, failpoint, diagnostic timeout, and crash-test paths.

## Risks and Edge Cases
`HAVE_ATTACH` can deliberately hang the process for debugger attachment. `SIGKILL` bypasses cleanup and handlers, which is useful for crash simulation but not for graceful fatal error reporting. Callers must treat both functions as terminal.

## Test Signals
Crash/recovery tests, panic injection, and debug crash tests validate that the process terminates in the expected mode and that recovery handles the resulting on-disk state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_abort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_alloc.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_alloc.c

## Purpose
Wraps allocation, reallocation, duplication, and free operations with WiredTiger error handling, statistics, optional debug behavior, and optional Windows TCMalloc integration.

## Important APIs, Types, and Functions
Functions include exported `__wt_calloc`, `__wt_malloc`, `__wt_realloc`, `__wt_realloc_noclear`, `__wt_memdup`, `__wt_strndup`, and exported `__wt_free_int`. Private `__realloc_func` implements the shared realloc path.

## Control Flow
Allocation functions defensively NULL the output pointer before trying allocation, increment stats when a session exists, and return `WT_RET_MSG` on failure. Realloc asserts growth, optionally forces malloc/copy/free under `WT_CONN_DEBUG_REALLOC_MALLOC`, clears new memory unless using the noclear variant, and updates the tracked allocation size. Free reads a pointer-to-pointer, sets it to NULL before freeing, and increments free stats.

## State and Persistence Behavior
No durable state is written. Runtime state includes connection memory allocation/grow/free counters and the caller-owned allocation-size variable. The zeroing contract is important because some WiredTiger structures assume newly grown memory is cleared.

## Dependencies and Integration Points
This is the base allocation layer for nearly all WiredTiger modules. It depends on session stats, debug flags, errno mapping, explicit overwrite, and macros that pass pointer addresses into `__wt_free`.

## Risks and Edge Cases
Functions must support `NULL` sessions. Realloc requires callers to pass correct old allocation size when clearing memory; otherwise assertions catch mismatches. `__wt_memdup` with zero length would violate `__wt_malloc`'s nonzero assertion. `__wt_free_int` reduces but cannot eliminate double-free races if callers lack synchronization.

## Test Signals
Allocator failure injection, debug `realloc_malloc`, memory stats, zeroed growth checks, string duplication with embedded NUL handling through `__wt_strndup`, and sanitizer runs are useful signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_errno.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_errno.c

## Purpose
Provides portable error-code normalization and stringification for WiredTiger and system errors.

## Important APIs, Types, and Functions
`__wt_errno` returns `errno` or `WT_ERROR` if errno is zero. `__wt_strerror` returns a WiredTiger constant string when available or formats a generic numeric error string into a caller buffer or the session error buffer. `__wt_ext_map_windows_error` exposes Windows-to-POSIX error mapping to extensions on Windows and panics if called on non-Windows builds.

## Control Flow
Error string lookup first checks WiredTiger-specific constants, then tries the provided buffer, then the session buffer, and finally a fixed fallback string. The Windows mapping wrapper compiles to the real mapper only on `_WIN32`; otherwise it treats use as an API misuse panic.

## State and Persistence Behavior
There is no persistence. `__wt_strerror` may update `session->err`, which is per-session transient diagnostic state.

## Dependencies and Integration Points
The file depends on `errno`, `__wt_wiredtiger_error`, `__wt_snprintf`, `__wt_buf_fmt`, and extension API ABI. It is used by nearly every OS wrapper and error-reporting path.

## Risks and Edge Cases
`__wt_errno` hides missing errno by returning a generic error, which is safer than success but less precise. `__wt_strerror` does not call libc `strerror`; unknown POSIX errors are reported numerically. Non-Windows extension calls to map Windows errors panic by design.

## Test Signals
Tests should cover WiredTiger error constants, unknown numeric errors with caller and session buffers, `errno == 0` normalization, and platform-specific extension mapping behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_errno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fhandle.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_fhandle.c

## Purpose
Manages common `WT_FH` file-handle lifecycle, shared handle lookup, reference counts, open/close behavior, background fsync, and file zeroing above the configured `WT_FILE_SYSTEM`.

## Important APIs, Types, and Functions
Important functions are `__wt_open`, `__wt_close`, `__wt_handle_is_open`, `__wt_remove_locked`, `__wt_fsync_background_chk`, `__wt_fsync_background`, `__wt_close_connection_close`, and `__wt_file_zero`. Private helpers finalize required `WT_FILE_HANDLE` methods, hash/search handles, open with a specific filesystem, close final handles, and issue one background fsync.

## Control Flow
Open first checks the connection handle hash; if a name is already open it increments the refcount and returns it. Otherwise it allocates a `WT_FH`, applies read-only connection rules, builds a path unless `WT_FS_OPEN_FIXED` is set, calls `fs_open_file`, validates required methods, and inserts the handle after a second race check. Close decrements the refcount under `fh_lock` and only calls the underlying close when it reaches zero. Background fsync walks data handles, temporarily increments references around unlocked fsync calls, and may close handles whose count drops to zero.

## State and Persistence Behavior
Connection state includes hash buckets, a file-handle queue, `open_file_count`, per-handle reference counts, file type, name hash, `written`, and `last_sync`. Persistent effects are underlying file opens, closes, fsyncs, removals through `__wt_remove_locked`, and zero writes through `__wt_file_zero`.

## Dependencies and Integration Points
The file integrates `WT_FILE_SYSTEM` implementations, file operation verbosity, path construction, read-only connection semantics, tiered/local object cleanup, capacity throttling, stats, and background fsync workers.

## Risks and Edge Cases
Method finalization requires close, lock, read, size, sync, and write depending on read-only status; incomplete custom filesystems fail open. Race handling opens a file before the second hash check, so losing the race must close and free the duplicate. Background fsync drops and reacquires `fh_lock`, so reference management is delicate. `__wt_file_zero` uses offset/size arithmetic and throttled writes; callers must pass the intended end range correctly.

## Test Signals
Custom filesystem tests, shared open/close refcount tests, read-only open behavior, background fsync support and no-wait paths, local object remove-while-open behavior, and file-zeroing tests validate this layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fhandle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fs_inmemory.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_fs_inmemory.c

## Purpose
Implements WiredTiger's in-memory `WT_FILE_SYSTEM`, storing file contents in process memory rather than the OS filesystem.

## Important APIs, Types, and Functions
The private filesystem type `WT_FILE_SYSTEM_INMEM` embeds `WT_FILE_SYSTEM`, hash buckets, a queue of in-memory handles, and a spinlock. Key methods are directory list/free, exist, remove, rename, size, open, terminate, and per-file close/lock/read/size/sync/write. `__wt_os_inmemory` initializes and installs the filesystem.

## Control Flow
All filesystem operations acquire the in-memory filesystem lock. Open searches by name and either returns the existing file if its refcount is zero or creates a new `WT_FILE_HANDLE_INMEM` with read/write/size/sync methods. Reads copy from the backing buffer if the offset is within size. Writes grow the buffer, copy data at the requested offset, and extend size. Rename updates the stored name and rehashes the handle. Remove refuses busy handles unless forced during terminate.

## State and Persistence Behavior
All file data is volatile in `WT_ITEM` buffers attached to in-memory handles. The filesystem maintains name hashes, queue links, per-handle refcount, and content size. Sync is a no-op because there is no durable backing store.

## Dependencies and Integration Points
This file implements the same `WT_FILE_SYSTEM` ABI used by the common handle layer. It depends on connection hash size, spinlocks, `WT_FILE_HANDLE` method conventions, buffer growth, and allocation helpers. It is selected for in-memory connection configurations.

## Risks and Edge Cases
Only one open handle per file is supported; a second concurrent open returns `EBUSY`. Directory listing filters by a directory string prefix and optional filename prefix, which differs from full POSIX directory semantics. Read past EOF returns `WT_ERROR`. Rename does not check destination existence. Because contents are volatile, crash/restart persistence assumptions do not apply.

## Test Signals
In-memory engine tests should cover create/open/read/write/rename/remove/list/size, busy remove/open failures, teardown with forced handle removal, and running normal metadata/logging code over the in-memory filesystem.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fs_inmemory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fstream.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_fstream.c

## Purpose
Provides a portable `WT_FSTREAM` implementation over WiredTiger file handles for line-oriented reads and buffered formatted writes.

## Important APIs, Types, and Functions
`__wt_fopen` creates stream handles. Private methods are `__fstream_close`, `__fstream_flush`, `__fstream_getline`, `__fstream_printf`, and not-supported variants for invalid read/write operations. `WT_STREAM_BUFSIZE` is 8192 bytes.

## Control Flow
Open wraps `__wt_open`, allocates a `WT_FSTREAM`, records file size, sets append offset if requested, and installs either write/append methods or read methods. `__fstream_getline` refills an internal buffer from `WT_FH` reads, discards empty lines, strips the newline, and NUL-terminates the caller buffer. `__fstream_printf` appends formatted output to the stream buffer, growing as needed, and flushes when the buffer reaches the stream size threshold. Close flushes non-read streams, closes the handle, frees buffers, and frees the stream.

## State and Persistence Behavior
Stream state includes the underlying `WT_FH`, current offset, total size, buffer, flags, and method table. Writes persist only when flushed or closed. Reads advance the stream offset and internal data pointer.

## Dependencies and Integration Points
Used by turtle/metadata backup text files and other code wanting portable file-stream behavior independent of libc stdio. It depends on common file handles, buffer allocation, formatted printing helpers, and `__wt_read`/`__wt_write`.

## Risks and Edge Cases
Empty lines are skipped and EOF is indicated by a returned buffer size of zero, which is a WiredTiger-specific contract. Switching method tables means calling `getline` on a write stream or `printf` on a read stream returns `ENOTSUP`. Buffered writes must be flushed before close errors are ignored by callers.

## Test Signals
Turtle file read/write, metadata backup loading, append-mode writes, long lines larger than 8192 bytes, empty-line skipping, and unsupported operation errors exercise this module.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fstream_stdio.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_fstream_stdio.c

## Purpose
Initializes `WT_FSTREAM` wrappers for process stdout and stderr.

## Important APIs, Types, and Functions
`__wt_os_stdio` initializes `WT_STDERR(session)` and `WT_STDOUT(session)` using private `__stdio_init`. Implemented stdio methods are `__stdio_flush` and `__stdio_printf`; close and getline return `ENOTSUP`.

## Control Flow
Initialization stores the stream name and `FILE *`, then installs method pointers. Printing delegates to `vfprintf`; flushing delegates to `fflush`; errors are mapped through `__wt_errno`.

## State and Persistence Behavior
State is the session's stdout/stderr stream wrappers and libc `FILE *` handles. Output is process I/O rather than database persistence.

## Dependencies and Integration Points
The file depends on libc stdio, `WT_FSTREAM`, session stream macros, and WiredTiger error handling. Message and diagnostic output paths use these initialized streams.

## Risks and Edge Cases
Close is unsupported because WiredTiger does not own stdout/stderr. Getline is unsupported. `vfprintf`/`fflush` errors surface as WiredTiger return codes and should not be silently ignored by callers that need reliable output.

## Test Signals
Startup stream initialization, stdout/stderr diagnostic printing, flush failures under redirected/closed descriptors, and unsupported close/getline calls are relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_fstream_stdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_getopt.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_getopt.c

## Purpose
Provides a public-domain getopt implementation namespaced as WiredTiger globals and optionally returning WiredTiger-specific error constants.

## Important APIs, Types, and Functions
The exported parser is `__wt_getopt`. Global parser state includes `__wt_opterr`, `__wt_optind`, `__wt_optopt`, `__wt_optreset`, `__wt_optwt`, and `__wt_optarg`.

## Control Flow
The parser maintains a static `place` pointer into the current argv element. It handles new option scanning, end-of-options `--`, solitary `-`, illegal options, options with required arguments, inline arguments, and next-argv arguments. When `__wt_optwt` is set, bad option/argument returns are `WT_GETOPT_BAD_OPTION` and `WT_GETOPT_BAD_ARGUMENT`; otherwise it returns traditional `?` or `:`.

## State and Persistence Behavior
All state is process-global and transient. Callers reset parsing through `__wt_optreset` and `__wt_optind`. There is no database persistence.

## Dependencies and Integration Points
Command-line tools and tests use this parser to avoid relying on platform getopt availability or behavior. It depends on stderr for optional diagnostics and WiredTiger return constants for WT-specific mode.

## Risks and Edge Cases
The API is not thread-safe because parser state is global and `place` is static. Callers must reset state between independent parses. `__wt_optwt` changes the error contract, so callers must know which mode is active.

## Test Signals
Tool argument parsing tests should cover grouped short options, missing arguments, inline and separated arguments, `--`, solitary `-`, parser reset, disabled error printing, and WT-specific error codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_getopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_strtouq.c -->
# sources/storage-engines/wiredtiger/src/os_common/os_strtouq.c

## Purpose
Provides a small unsigned 64-bit string conversion wrapper.

## Important APIs, Types, and Functions
`__wt_strtouq` returns `uint64_t` and accepts `const char *nptr`, `char **endptr`, and a numeric base.

## Control Flow
The function directly calls `strtoull` and casts the result to `uint64_t`.

## State and Persistence Behavior
No state is stored. The caller observes libc conversion behavior through the return value, `endptr`, and `errno`.

## Dependencies and Integration Points
This wrapper provides a portable WiredTiger-named conversion API used by configuration/tool parsing code that wants an unsigned 64-bit value.

## Risks and Edge Cases
Overflow and invalid input behavior are inherited from `strtoull`; the wrapper does not clear or inspect `errno`. On platforms where `unsigned long long` is wider or narrower than expected, the cast semantics matter, though WiredTiger assumes it can represent 64-bit values.

## Test Signals
Parse decimal, hex, octal/base-specific values, invalid input with `endptr`, max `uint64_t`, overflow with `errno`, and empty strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_common/os_strtouq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_darwin/os_futex.c -->
# sources/storage-engines/wiredtiger/src/os_darwin/os_futex.c

## Purpose
Implements WiredTiger futex wait/wake primitives on Darwin using Apple's private ulock APIs.

## Important APIs, Types, and Functions
`__wt_futex_wait` waits on a `WT_FUTEX_WORD` matching an expected value with a microsecond timeout. `__wt_futex_wake` stores a wake value and wakes either one waiter or all waiters depending on `WT_FUTEX_WAKE`.

## Control Flow
Wait converts microseconds to nanoseconds and calls `__ulock_wait2` with `UL_COMPARE_AND_WAIT_SHARED | ULF_NO_ERRNO`. Nonnegative returns and `-EFAULT` are treated as success after loading the wake value. Other negative returns are converted to `errno` and `-1`. Wake stores `wake_val`, calls `__ulock_wake`, ignores `-ENOENT`, and maps `-EINTR`/`-EAGAIN` to `errno=EINTR` and `-1`.

## State and Persistence Behavior
State is the futex word in memory. There is no persistence.

## Dependencies and Integration Points
It depends on `<ulock.h>`, Apple private API semantics, atomic loads/stores, and WiredTiger condition/lock primitives built on futexes.

## Risks and Edge Cases
The API is private and poorly documented. `-EFAULT` may mean the page was paged out rather than an invalid address, so the code intentionally reloads the address. The ulock wake value argument is wider than the futex word and is assumed unused unless `ULF_WAKE_THREAD` is set.

## Test Signals
Darwin concurrency tests should cover timed waits, wake-one, wake-all, no-waiter wake, signal interruption behavior, and stress under paging/memory pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_darwin/os_futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_darwin/os_mtx_sem.c -->
# sources/storage-engines/wiredtiger/src/os_darwin/os_mtx_sem.c

## Purpose
Provides Darwin semaphore primitives for WiredTiger using Grand Central Dispatch semaphores.

## Important APIs, Types, and Functions
Functions are `__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait`. `WT_SEMAPHORE` stores a name and dispatch semaphore object.

## Control Flow
Initialization creates a dispatch semaphore with count zero, then signals it `count` times because creation does not accept a nonzero initial count. Post signals the semaphore and ignores the wake-status return. Wait blocks forever with `DISPATCH_TIME_FOREVER`. Destroy releases the dispatch object and clears the struct.

## State and Persistence Behavior
Semaphore state is in memory and kernel/dispatch runtime state. There is no persistence.

## Dependencies and Integration Points
This file backs WiredTiger's platform semaphore abstraction on Darwin for worker threads and synchronization primitives.

## Risks and Edge Cases
Initialization loops once per initial count, so very large initial counts are inefficient. Wait should not time out, so any nonzero dispatch return is treated as `EINVAL`. Destroy assumes a valid initialized dispatch object.

## Test Signals
Thread synchronization tests on Darwin should cover initial counts, post/wait ordering, blocking wakeup, destroy after use, and failure injection for semaphore creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_darwin/os_mtx_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_linux/os_futex.c -->
# sources/storage-engines/wiredtiger/src/os_linux/os_futex.c

## Purpose
Implements WiredTiger futex wait/wake primitives on Linux using the `SYS_futex` syscall.

## Important APIs, Types, and Functions
`__wt_futex_wait` wraps `FUTEX_WAIT_PRIVATE`. `__wt_futex_wake` wraps `FUTEX_WAKE_PRIVATE` and supports `WT_FUTEX_WAKE_ONE` or `WT_FUTEX_WAKE_ALL`.

## Control Flow
Wait asserts a positive microsecond timeout, converts it to `timespec`, and calls `syscall(SYS_futex, addr, FUTEX_WAIT_PRIVATE, expected, &timeout, NULL, 0)`. On success it loads the wake value atomically. Wake computes a wake count of `1` or `INT_MAX`, stores the wake value, calls the futex wake syscall, and returns zero for any nonnegative syscall result or the negative syscall value on error.

## State and Persistence Behavior
State is the futex word in memory; no durable state is involved.

## Dependencies and Integration Points
The file depends on Linux futex headers, syscall ABI, timespec conversion, and atomic stores/loads. It supports higher-level spin/condition abstractions used throughout WiredTiger.

## Risks and Edge Cases
The wait wrapper returns raw negative syscall results rather than mapping through `errno`, so callers must follow the expected convention. Timeout and spurious wake behavior are inherited from futex semantics. Wake-all uses `INT_MAX`, which is conventional but assumes waiter counts never need exact reporting.

## Test Signals
Linux synchronization tests should cover timeout, wake-one, wake-all, expected-value mismatch, spurious wake tolerance, and stress under many waiters.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_linux/os_futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_linux/os_mtx_sem.c -->
# sources/storage-engines/wiredtiger/src/os_linux/os_mtx_sem.c

## Purpose
Provides Linux/POSIX semaphore primitives for WiredTiger using unnamed POSIX semaphores.

## Important APIs, Types, and Functions
Functions are `__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait`.

## Control Flow
Initialization clears the struct, stores the name, and calls `sem_init` with process-local sharing and the requested count. Destroy calls `sem_destroy` and clears the struct. Post calls `sem_post`. Wait loops on `sem_wait`, retrying `EINTR` and returning other errno values.

## State and Persistence Behavior
Semaphore state is in memory and kernel/libpthread state only. There is no persistence.

## Dependencies and Integration Points
This is the Linux semaphore backend for WiredTiger thread coordination, used by background services and synchronization abstractions.

## Risks and Edge Cases
`sem_wait` interruption is handled, but other errors surface directly. Destroying a semaphore with waiters or after failed init is a caller bug. The name is stored for diagnostics but not used by POSIX semaphores.

## Test Signals
Linux thread tests should cover initial count behavior, post/wait, signal interruption, destroy, and concurrent producers/consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_linux/os_mtx_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_dir.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_dir.c

## Purpose
Implements POSIX directory listing for WiredTiger's file-system abstraction.

## Important APIs, Types, and Functions
`__wti_posix_directory_list` returns all matching entries, `__wti_posix_directory_list_single` returns at most one, and `__wti_posix_directory_list_free` frees the returned array. Private `__directory_list_worker` contains the shared `opendir`/`readdir`/`closedir` logic.

## Control Flow
The worker opens the directory with syscall retry, captures diagnostic messages with timestamps and directory file descriptors, iterates entries skipping `.` and `..`, filters by optional prefix, duplicates matching names into a growing array, and stops early for single-entry mode. It detects `readdir` failure via `errno`, closes the directory, and on close errors prints captured open/read diagnostics.

## State and Persistence Behavior
The function allocates a caller-owned array of duplicated entry names. It does not modify the filesystem.

## Dependencies and Integration Points
It depends on POSIX `DIR`, `opendir`, `readdir`, `closedir`, `dirfd`, WiredTiger scratch buffers, allocation helpers, and the `WT_FILE_SYSTEM` directory-list ABI.

## Risks and Edge Cases
Directory entries are returned as names relative to the directory, not full paths. The prefix filter applies only to `d_name`. Errors after partial allocation must free every duplicated entry. Close errors are rare but heavily diagnosed because past failures were hard to debug.

## Test Signals
Filesystem tests should cover empty directories, prefix filtering, single-entry mode, large directories that force realloc, opendir/readdir/closedir failures, and freeing partial results.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_dlopen.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_dlopen.c

## Purpose
Wraps POSIX dynamic library loading, symbol lookup, and closing for WiredTiger extensions.

## Important APIs, Types, and Functions
Functions are `__wt_dlopen`, `__wt_dlsym`, and `__wt_dlclose`. The handle type is `WT_DLH`, which stores a library name and `dlopen` handle.

## Control Flow
Open allocates a `WT_DLH`, stores `path` or `"local"` as the name, and calls `dlopen(path, RTLD_LAZY)`. Symbol lookup clears the output pointer, calls `dlsym`, returns success with NULL when missing and `fail` is false, or reports an error when `fail` is true. Close calls `dlclose` except on FreeBSD, then frees the name and handle wrapper.

## State and Persistence Behavior
Loaded dynamic library handles are process state only. No database files are modified.

## Dependencies and Integration Points
This file supports extension loading and local extension symbol lookup. It depends on `dlopen`, `dlsym`, `dlclose`, `dlerror`, allocation, and error reporting.

## Risks and Edge Cases
FreeBSD intentionally skips `dlclose` to avoid crashes in `__cxa_finalize`, leaking resources until process exit. `dlopen(NULL)` is represented as `"local"` for diagnostics. Missing optional symbols are not errors when `fail` is false.

## Test Signals
Extension tests should cover loading shared libraries, local symbol lookup, missing required and optional symbols, close behavior, and FreeBSD-specific no-close behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_dlopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_fallocate.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_fallocate.c

## Purpose
Selects and installs the best available POSIX file-extension method for a file handle.

## Important APIs, Types, and Functions
Private probes are `__posix_std_fallocate`, `__posix_sys_fallocate`, and `__posix_posix_fallocate`. The exported platform hook is `__wti_posix_file_extend`.

## Control Flow
On the first extend call, `__wti_posix_file_extend` probes `fallocate`, syscall `SYS_fallocate`, `posix_fallocate`, and finally `fh_truncate`. When a method succeeds, it stores either the lock-free `fh_extend_nolock` pointer and clears the locking `fh_extend`, or stores a locking `fh_extend` when required. If no method works, it clears `fh_extend` and returns `ENOTSUP`.

## State and Persistence Behavior
Successful calls extend the underlying file to the requested offset. The first call mutates the file handle's method table so later extensions skip probing and use the selected implementation.

## Dependencies and Integration Points
The file depends on platform feature macros for `fallocate`, `SYS_fallocate`, and `posix_fallocate`, the POSIX file handle type, and the common file-handle method table. It integrates with block manager file preallocation and extension paths.

## Risks and Edge Cases
The comments document Linux systems where `posix_fallocate` corrupted existing data, so Linux keeps it behind the locking function when selected and prefers `fallocate` variants first. The first-call probe is assumed single-threaded because it is configured as a locking call. Memory barriers protect method-table updates visible to other threads.

## Test Signals
Platform tests should cover each configured fallocate method, fallback to truncate, `ENOTSUP` when no method exists, repeated calls after method installation, and data-integrity checks around preallocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_fallocate.c -->
