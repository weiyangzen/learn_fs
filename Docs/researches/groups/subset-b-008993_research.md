# Research group: subset-b-008993

This grouped report covers the assigned WiredTiger schema, session, and support files. Each section preserves the source path and is delimited for the reconciliation splitter.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_truncate.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_truncate.c

## Purpose
Implements schema-level truncate dispatch for whole objects and cursor ranges. It maps public `WT_SESSION::truncate` requests onto file, table, tiered, layered, history-store, table, and extension data-source implementations, including fallback cursor-walk removal for data sources that lack a native truncate hook.

## Important APIs, Types, and Functions
- `__wt_schema_truncate(session, uri, cfg)` is the no-range schema dispatcher. It expects checkpoint and schema locks to be held, routes by URI prefix, and maps `WT_NOTFOUND` to `ENOENT`.
- `__wt_schema_range_truncate(WT_TRUNCATE_INFO *)` dispatches range truncation by object type, including history store, file/btree, table, layered, extension `range_truncate`, and generic cursor iteration.
- `__wt_range_truncate(start, stop)` is the generic cursor-based implementation. With no start cursor it removes backward from `stop`; otherwise it removes forward from `start` until it reaches `stop`.
- `__truncate_table`, `__truncate_tiered`, `__truncate_layered`, and `__truncate_dsrc` implement whole-object truncation for composite or non-file data sources.
- `WT_TRUNCATE_INFO` carries session, URI, explicit start/stop flags, cursors, and original key buffers to downstream btree/table/layered truncate code.

## Control Flow
Whole-object truncate first distinguishes btree files, layered tables, regular tables, tiered data sources, and extension data sources. Table truncate recursively truncates every column group and then every opened index. Tiered truncate obtains an exclusive dhandle and calls range truncate without a current dhandle. Layered whole truncate opens cursors for first and last visible keys and records a range truncate entry. Unsupported or unknown URI types are rejected through shared error helpers.

Range truncate special-cases the history store, ingest replay for file URIs, btree file ranges with required key validation, table ranges, layered ranges on leaders or non-slow followers, extension `range_truncate`, and finally the generic cursor remove loop. Layered range truncate resolves a missing stop cursor to the table's last visible key because layered truncate-list entries require concrete bounds.

## State and Persistence Behavior
This file does not own durable metadata updates, but it drives durable effects through lower layers: btree truncate, table truncate, history-store truncate, layered truncate-list recording, extension data-source hooks, and cursor remove calls. Statistics (`cursor_truncate`) are incremented for whole-object paths. It also carefully releases schema tables, dhandles, and local cursors on error paths.

## Dependencies and Integration Points
Depends on schema table/index lookup, cursor opening, dhandle acquisition/release, btree truncate, table range truncate, history-store cursor truncate, layered table truncate, and data-source extension hooks from `WT_DATA_SOURCE`. It is called by `session_api.c` through `__wt_session_range_truncate` and the schema locked section of `WT_SESSION::truncate`.

## Risks
Range-bound correctness is high risk: missing `__cursor_needkey`, wrong `WT_TRUNC_EXPLICIT_STOP`, or incorrect start/stop comparisons can delete too much or too little data. Layered truncate has explicit FIXME debt around local stop-cursor creation. Whole-table truncate must maintain table/index/colgroup consistency. Extension data sources can supply partial behavior, so fallback behavior must not silently bypass custom semantics.

## Test Signals
Useful coverage includes truncate by URI and by cursor bounds, empty ranges, start-after-stop validation, table-with-index truncate, layered leader/follower behavior, tiered truncate, history-store truncate, extension source fallback and native hooks, and recovery/logging tests that confirm truncation persists correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_util.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_util.c

## Purpose
Provides shared schema utility routines for backup conflict checks, data-source lookup, internal schema sessions, namespace validation, simple-table detection, and a debug crash hook used by schema operations.

## Important APIs, Types, and Functions
- `__wti_schema_backup_check(session, name)` rejects schema operations that would conflict with an active hot backup file list.
- `__wt_schema_get_source(session, name)` scans `S2C(session)->dsrcqh` for a matching registered data-source prefix.
- `__wti_schema_internal_session` opens an internal metadata-capable schema session when the caller has a running transaction, preventing schema records from being buffered in the user's transaction.
- `__wti_schema_session_release` closes that internal session and propagates saved error information back to the original session.
- `__wt_str_name_check` and `__wt_name_check` protect the `WiredTiger` namespace and reject JSON/config grouping characters in object names.
- `__wt_is_simple_table` detects unnamed-column table configs.
- `__wti_debug_crash_if_flag_set` simulates crash points when configured debug flags are set.

## Control Flow
Backup checks first do a cheap atomic read of `conn->backup.start`, then take the hot-backup read lock only when needed and compare the target name against the active backup list. Internal schema session handling returns the current session unless a transaction is running; release mirrors that decision. Name validation peels URI/table prefixes before checking reserved names and disallowed characters.

## State and Persistence Behavior
The file does not persist metadata directly, but it protects persistence boundaries. Backup checking prevents destructive schema changes to files being backed up. Internal schema sessions isolate schema metadata operations from application transactions. Debug crash support intentionally sleeps before aborting to let previous metadata changes reach stable storage in targeted test scenarios.

## Dependencies and Integration Points
Integrated into create/drop/alter/rename/truncate and other schema paths. It depends on connection backup state, hot-backup locks, connection data-source queues, session open/close support, transaction flags, config parsing, and error propagation helpers.

## Risks
Namespace validation must stay aligned with metadata/config parser constraints; relaxing it can expose metadata corruption paths. Internal-session error propagation must preserve the first meaningful user-visible error. Backup conflict checks rely on lock ordering and the backup list lifecycle; races here could allow file removal while a backup cursor still expects the file.

## Test Signals
Look for hot-backup/drop conflict tests, schema operations inside active transactions, object-name validation tests for `WiredTiger` and punctuation-heavy names, extension data-source dispatch tests, simple-table config tests, and debug crash/failpoint coverage around schema metadata persistence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_worker.c -->
# sources/storage-engines/wiredtiger/src/schema/schema_worker.c

## Purpose
Implements generic schema traversal for operations that must apply to all physical handles backing a logical object, such as verify, salvage, checkpoint handle collection, backup, and compaction. It expands table, column-group, index, tiered, and layered URIs into underlying file or data-source operations.

## Important APIs, Types, and Functions
- `__wt_schema_worker(session, uri, file_func, name_func, cfg, open_flags)` is the main recursive dispatcher.
- `__wti_execute_handle_operation` optionally closes existing handles for exclusive operations, opens a btree checkpoint/dhandle, invokes `file_func`, and releases the dhandle.
- `__schema_tiered_worker` iterates tiers in a `WT_TIERED` handle.
- `__schema_layered_worker_verify` verifies layered stable and ingest constituents with leader/follower-specific semantics.
- `name_func` callbacks can inspect intermediate URIs and request skips; `file_func` executes against opened btree handles.

## Control Flow
The worker first gives `name_func` a chance to skip the requested URI. It rejects verify/salvage for tiered objects. It then routes: files execute directly; colgroups and indexes resolve to sources; tables open table metadata, visit all colgroups and optionally indexes; layered verify delegates to stable/ingest checks; tiered walks each tier; extension data sources use salvage/verify hooks when available. Checkpoint-related file functions are no-ops for unsupported extension sources.

## State and Persistence Behavior
This file coordinates handle state rather than writing metadata itself. Exclusive operations may close open handles before re-opening the target. Layered verification reads stable and ingest constituents, and leader ingest verification requires the ingest table to be empty. Recursive traversal must release opened table metadata on all exits.

## Dependencies and Integration Points
Used by session APIs for salvage and verify, by compaction handle gathering, checkpoint handle paths, backup-style traversals, and schema code that needs source-tree expansion. It depends on table/index/colgroup metadata APIs, dhandle open/release, layered/tiered handle types, data-source extension hooks, and `__wt_verify`, `__wt_salvage`, and checkpoint callbacks.

## Risks
Recursive traversal can miss physical files if table/index metadata is not opened under the right table lock. Operations differ in whether they need indexes opened, and this file keys that on `WT_SESSION_LOCKED_TABLE_WRITE`. Verify/salvage tiered restrictions must remain consistent with feature support. Layered follower handling intentionally ignores transient missing stable tables, which needs focused testing to avoid hiding real corruption.

## Test Signals
Coverage should include verify/salvage for files, tables, indexes, colgroups, tiered rejection, layered leader/follower verify, name callback skip behavior, exclusive-handle close behavior, and checkpoint/backup traversal paths that depend on index opening under table write lock.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/schema/schema_worker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_api.c -->
# sources/storage-engines/wiredtiger/src/session/session_api.c

## Purpose
Defines most of the public `WT_SESSION` API vtable and its internal helpers: session open/close/reset/reconfigure, cursor open/cache behavior, schema APIs, logging APIs, transaction APIs, checkpointing, truncate, error inspection, and read-only/minimal-mode method tables.

## Important APIs, Types, and Functions
- `__open_session`, `__wt_open_session`, and `__wt_open_internal_session` allocate and initialize session slots, method tables, cursors, dhandle caches, transaction state, hazard arrays, statistics buckets, event handlers, and error buffers.
- `__wt_session_close_internal`, `__session_close_cursors`, and `__session_clear` unwind transactions, cursors, cached handles, metadata tracking, hazard pointers, resources, and session-array state.
- `__session_open_cursor_int`, `__wt_open_cursor`, and `__session_open_cursor` route cursor URIs to table/file/index/config/log/layered/backup/statistics/version/extension cursor implementations and integrate cursor caching.
- Schema-facing APIs include `create`, `alter`, `drop`, `publish`, `salvage`, `truncate`, `verify`, `compact` vtable binding, and checkpoint.
- Transaction APIs wrap begin, commit, prepare, rollback, timestamp/prepared-id setters, query timestamp, reset snapshot, and pinned range.
- `__wt_session_range_truncate` normalizes URI/cursor truncate requests and builds `WT_TRUNCATE_INFO` for schema/btree/table truncate layers.

## Control Flow
All public methods enter through `SESSION_API_*` macros that enforce connection/session state, configuration parsing, transaction/prepared checks, and error mapping. Cursor open first validates connection readiness and URI/duplicate arguments, tries the cursor cache, dispatches by URI prefix or data source, duplicates positions when needed, and records timing stats in diagnostic builds. Schema methods validate names and take schema/table/checkpoint locks in operation-specific combinations. Transaction methods check context, update counters, call transaction core functions, and handle rollback or panic rules for failed prepared commits/rollbacks.

Session close disables cursor caching, rolls back active transactions, releases snapshots, closes active and cached cursors, closes cached dhandles, destroys hazard and metadata state, releases common resources, updates session counters under the API lock, then carefully clears only the safe prefix of the reusable session object. Session open chooses normal, minimal, or read-only method tables, initializes queues and hash tables, transaction state, flags, prefetch defaults, config, error state, and finally publishes `active` with a release barrier.

## State and Persistence Behavior
This file is a central state coordinator. It maintains session active state, cursor lists/cache buckets, dhandle cache arrays, transaction state, hazard arrays, scratch/error buffers, stats, operation tracking buffers, prefetch flags, and per-session API method pointers. It drives durable behavior through transaction commit/rollback/prepare, checkpoint, log flush/printf, schema metadata updates, salvage, truncate logging, and checkpoint-created snapshots. `__wt_session_range_truncate` preserves original keys for write-ahead truncate logging even when the resolved range is empty.

## Dependencies and Integration Points
Highly integrated with transaction, cursor, schema, checkpoint, logging, statistics, event handler, dhandle, hazard, metadata tracking, prefetch, call-log, and connection lifecycle subsystems. It calls into `schema_truncate.c`, `schema_worker.c`, `session_compact.c`, `session_dhandle.c`, `session_helper.c`, and many cursor implementations.

## Risks
The largest risks are lock-order regressions, session reuse races, cursor-cache stale-handle retention, incorrect transaction error handling, prepared-transaction panic semantics, and URI dispatch drift as new object types are added. Session close/open barriers protect hazard/session-array users; clearing too much or publishing active too early can create use-after-free or uninitialized-read bugs. Truncate has high correctness risk because it moves application cursors, logs original bounds, handles empty ranges, and maps prepare conflicts to rollback.

## Test Signals
Relevant signals include API contract tests for each `WT_SESSION` method, read-only and minimal connection tests, cursor cache reuse/sweep tests, duplicate cursor tests, backup cursor duplication, truncate range and empty-range recovery tests, transaction prepare/commit/rollback error tests, checkpoint-in-transaction rejection, session open/close stress, hazard/session-array race tests, and diagnostic timing/stat counter assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_compact.c -->
# sources/storage-engines/wiredtiger/src/session/session_compact.c

## Purpose
Implements `WT_SESSION::compact`, including foreground compaction, background compaction control, per-handle compaction setup, timeout/interruption checks, checkpoint scheduling, and cleanup. The long file header documents WiredTiger's cooperative compaction model between btree and block manager.

## Important APIs, Types, and Functions
- `__wti_session_compact` is the public compact method implementation bound in `session_api.c`.
- `__compact_handle_append` gathers file handles through `__wt_schema_worker`, starts block-manager compaction on each, and stores handles in `session->op_handle`.
- `__compact_worker` runs the checkpoint/compact/checkpoint/checkpoint loop over gathered handles.
- `__wt_session_compact_check_interrupted` handles foreground event-handler interruption, background compact disable, and timeout.
- `__wt_compact_check_eligibility` rejects `.wtobj` tiered objects.
- `__wti_session_compact_readonly` provides the read-only vtable failure path.

## Control Flow
The public method first rejects disaggregated storage, handles `background` configuration as a signal to the background compaction server, validates foreground URI requirements, rejects in-memory and transactional contexts, validates object names, and dispatches extension data-source compaction if the URI is not a core btree/table object. For core objects, it initializes `WT_COMPACT_STATE`, reads `free_space_target`, `timeout`, and `dryrun`, uses schema traversal under schema/table locks to gather file handles, and runs the worker if files were found.

The worker optionally performs an initial checkpoint for foreground compact, then up to 100 passes. Each pass runs `__wt_compact` with each handle, tracks whether another pass is worthwhile, treats `EBUSY` as cache-pressure failure, ignores internal `ECANCELED`, and after progress performs two checkpoints with tree dirty marking between them.

## State and Persistence Behavior
Compaction persists through checkpoints. It rewrites selected pages, then checkpoints twice so blocks freed by old checkpoints become truly available and file truncation can happen safely. The file sets `session->compact`, `session->compact_state`, `session->op_handle`, per-handle `compact_skip`, stats such as running/fail/success/pass counters, and block-manager compact start/end state. Cleanup always ends compaction on gathered handles and releases dhandles.

## Dependencies and Integration Points
Depends on block-manager `compact_start`/`compact_end`, btree `__wt_compact`, checkpoint DB code, schema traversal, session dhandle reference management, background compaction server state, event handlers, configuration parsing, verbose/stat infrastructure, transaction context checks, and object-name validation.

## Risks
Compaction is sensitive to checkpoint ordering and handle lifecycle. Missing `compact_end` or dhandle release can leave handles pinned. Incorrect interruption mapping can expose expected background shutdown as warnings or hide foreground cancellation. Adding new storage backends requires rechecking assumptions about block address opacity, checkpoints, and file truncation. Background compact configuration validation must reject incompatible options when disabling the server.

## Test Signals
Coverage should include foreground compact success, timeout, application interruption, background enable/disable/run-once/exclude/free-space configs, in-memory/disaggregated rejection, tiered `.wtobj` rejection, extension data-source compact hooks, cache-pressure `EBUSY`, dry-run mode, checkpoint count/stat behavior, and leak checks for dhandle release after errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_compact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_dhandle.c -->
# sources/storage-engines/wiredtiger/src/session/session_dhandle.c

## Purpose
Manages per-session data-handle lookup, caching, locking, checkpoint-handle resolution, release, sweep, and checkpoint locking. It is the session-side synchronization layer between URI-based operations and shared connection dhandle state.

## Important APIs, Types, and Functions
- `__wt_session_get_dhandle` locates, locks, opens, and installs `session->dhandle` for a URI/checkpoint.
- `__wt_session_get_btree_ckpt` interprets checkpoint configuration and opens matching data-store and optional history-store checkpoint handles with consistent snapshot metadata.
- `__wt_session_lock_dhandle` enforces read/write/exclusive locking, special-operation exclusion, and dead-handle handling.
- `__wt_session_release_dhandle_v2` closes bulk/special/discard handles as needed, unlocks read/write locks, decrements exclusive references, and clears `session->dhandle`.
- `__wt_session_close_cache` and `__wt_session_dhandle_sweep` discard cached dhandle references.
- `__wt_session_lock_checkpoint` locks checkpoint handles for overwrite and evicts cached checkpoint pages.
- `__wt_dhandle_clear_add` records debug breadcrumbs for dhandle clearing.

## Control Flow
Lookup first searches the session hash cache, discarding inactive/outdated non-metadata entries. On miss it sweeps stale session handles, searches the shared connection list under read lock, or allocates under write lock, then caches the acquired reference. Locking loops until the handle is open in a compatible mode, dead, busy, or exclusively acquired for open/special operations. If a handle must be opened but the caller lacks schema lock, it drops the temporary exclusive lock and recursively retries under schema lock, with special checkpoint-lock handling for disaggregated stable constituents.

Checkpoint opening has a retry loop for unnamed checkpoints. It reads snapshot wall times, datastore checkpoint metadata, optional history-store checkpoint metadata, and snapshot/timestamp metadata; detects races with running checkpoints; opens dhandles; validates checkpoint order; and retries `WT_NOTFOUND`/`EBUSY` for unnamed checkpoint races.

## State and Persistence Behavior
This file does not directly persist data, but it protects durable views by pinning the correct dhandles and checkpoint versions. It maintains session dhandle cache entries, shared dhandle reference counts, dhandle lock flags, exclusive owner/refcount, discard/dead/outdated flags, checkpoint snapshot metadata, history-store checkpoint pins, and checkpoint handle locks tracked by metadata tracking. Release paths can close handles, evict checkpoint pages, and mark discard-on-release to avoid stale checkpoint contents.

## Dependencies and Integration Points
Integrated with connection dhandle allocation/open/close/sweep, schema and checkpoint locks, metadata checkpoint readers, history-store URI selection, transaction snapshot metadata, eviction, metadata tracking, session reset/close, and all cursor/schema APIs that open btree handles.

## Risks
This is concurrency-critical code. Lock-order mistakes can deadlock schema, checkpoint, and handle-list locks. Race detection for checkpoint cursors depends on monotonic checkpoint wall times and order numbers. Incorrect reference counting or cache discard can produce use-after-free or leaked handles. Exclusive special-operation semantics must prevent bulk/salvage/verify/truncate conflicts without letting internal sweep starve user operations.

## Test Signals
Stress tests should cover concurrent cursor open/close/drop/verify/checkpoint, checkpoint cursor opens during active checkpoints, named and unnamed checkpoint regeneration, history-store checkpoint matching, disaggregated stable checkpoint handling, bulk-load close-on-release, dhandle sweep of dead/outdated handles, exclusive lock `EBUSY`, and metadata tracking rollback around checkpoint handle locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_dhandle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_helper.c -->
# sources/storage-engines/wiredtiger/src/session/session_helper.c

## Purpose
Provides session-array walking, diagnostic session dumping, and helpers for per-session last-error storage used by the public `WT_SESSION::get_last_error` API.

## Important APIs, Types, and Functions
- `__wt_session_array_walk(session, walk_func, skip_internal, cookiep)` iterates active sessions and calls a callback with early-exit support.
- `__wt_session_dump(session, dump_session, show_cursors)` emits diagnostic details about a session, transaction state, and optionally cursors.
- `__wt_session_reset_last_error` resets `WT_ERROR_INFO` to success/none defaults.
- `__wt_session_set_last_error` records the first error, sub-level error, and formatted message for an API call.

## Control Flow
Session-array walk reads the session count once, then acquire-reads each slot's `active` flag, pairing with session open's release publish. It skips inactive and optionally internal sessions, asserts hazard memory exists, invokes the callback, and honors callback-requested early exit. Dumping formats fields through `__wt_msg` and uses scratch buffers for cursor flag text. Last-error setting returns if saving is disabled, the session is null, or an error is already saved.

## State and Persistence Behavior
No durable state is written. The file reads volatile session-array state safely, exposes diagnostic state through event handlers, and maintains per-session `err_info` fields plus the backing formatted-message buffer. The first-error-wins rule preserves the initial failure from an API call.

## Dependencies and Integration Points
Used by generation draining, diagnostics, verbose transaction dumps, session API error retrieval, and API macros that reset/save errors. Depends on connection session arrays, session active publication barriers, event messaging, scratch buffers, cursor queues, transaction verbose dump, and error validation helpers.

## Risks
Callbacks must tolerate sessions changing while the array is walked. Missing acquire/release pairing could expose partially initialized session slots. Last-error formatting must not overwrite an earlier error and must only run with valid sub-level error codes. Diagnostic dumping can recurse into event handlers and should avoid destabilizing already-failing paths.

## Test Signals
Relevant tests include session-array walk under concurrent open/close, skip-internal behavior, early-exit callbacks, diagnostic dump output with and without cursors, `get_last_error` first-error semantics, empty-message handling, and internal session error propagation from schema helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_prefetch.c -->
# sources/storage-engines/wiredtiger/src/session/session_prefetch.c

## Purpose
Contains the session-level gate for page prefetch. It decides whether a read of a `WT_REF` should trigger prefetch based on session configuration, handle type, queue pressure, page type, special handle state, and observed disk-read history.

## Important APIs, Types, and Functions
- `__wt_session_prefetch_check(session, ref)` returns a boolean and updates skip/success statistics.
- Uses `WT_SESSION_PREFETCH_ENABLED`, `WT_DHANDLE_TYPE_TIERED`, `WT_REF_FLAG_INTERNAL`, `WT_BTREE_SPECIAL_FLAGS`, and `session->pf.prefetch_disk_read_count`.

## Control Flow
The function exits immediately if session prefetch is disabled. It then counts an attempt and rejects tiered handles, a full global prefetch queue, internal sessions, internal pages, special btree handles other than verify, and sessions with fewer than two disk reads. Once all gates pass, it increments success stats and returns true.

## State and Persistence Behavior
No persistent state is changed. Runtime effects are limited to statistics and the decision to enqueue or skip prefetch work elsewhere. It reads the connection prefetch queue count with thread-sanitizer-aware helpers and reads dhandle/btree flags from the active session handle.

## Dependencies and Integration Points
Called from page-read paths before scheduling asynchronous prefetch. Integrated with session configuration in `session_api.c`, connection prefetch queue management, btree special-operation flags, tiered storage restrictions, and statistics counters.

## Risks
Over-permissive gating can waste IO or enqueue work for unsupported objects; over-restrictive gating can eliminate useful prefetch. The threshold of two disk reads is a heuristic. Special-handle handling must stay aligned with verify and other operations that can safely prefetch.

## Test Signals
Tests should cover disabled/enabled sessions, internal-session skip, tiered skip, internal-page skip, queue-full skip, special-handle skip with verify exception, first/second disk-read counters, and successful prefetch attempt stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/session/session_prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/cond_auto.c -->
# sources/storage-engines/wiredtiger/src/support/cond_auto.c

## Purpose
Implements adaptive condition-variable waits. Wait intervals reset to a configured minimum when useful progress or a signal occurs, and grow toward a maximum when wakeups are unproductive.

## Important APIs, Types, and Functions
- `__wt_cond_auto_alloc(session, name, min, max, condp)` allocates a condition variable and initializes `min_wait`, `max_wait`, and `prev_wait`.
- `__wt_cond_auto_wait_signal(session, cond, progress, run_func, signalled)` adjusts the wait and calls `__wt_cond_wait_signal`.
- `__wt_cond_auto_wait(session, cond, progress, run_func)` is a wrapper that ignores the signalled output.

## Control Flow
On each wait, the code asserts auto-wait initialization. If the caller reports progress, it resets `prev_wait` to `min_wait`. Otherwise it computes a tenth-of-range delta and attempts an atomic compare-and-swap to increase `prev_wait` without exceeding `max_wait`. It then waits for `prev_wait`; a signal resets the next wait to minimum.

## State and Persistence Behavior
No durable state. Runtime state is in `WT_CONDVAR` wait fields and connection statistics (`cond_auto_wait`, skipped CAS, reset). Concurrent waiters may race to update `prev_wait`; losing the CAS is acceptable and counted.

## Dependencies and Integration Points
Wraps the lower-level WiredTiger condition-variable API and is used by background/server loops that want low latency during active work and lower wake frequency when idle. It depends on atomic CAS, wait/signal functions, optional run predicates, and stats.

## Risks
Incorrect min/max configuration can cause either busy waking or sluggish response. Because waiters update shared wait state concurrently, callers must accept approximate adaptation. A missing signal reset could leave a service slow to respond after idle periods.

## Test Signals
Unit tests should validate allocation fields, progress reset, no-progress growth capped at max, CAS-race tolerance, signal reset, stats increments, and behavior with a `run_func` that ends waits early.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/cond_auto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/crypto.c -->
# sources/storage-engines/wiredtiger/src/support/crypto.c

## Purpose
Provides common buffer framing for WiredTiger encryption and decryption. It preserves unencrypted header bytes, stores encrypted result length, calls configured encryptor/decryptor hooks, and reports required destination sizes.

## Important APIs, Types, and Functions
- `__wt_encrypt(session, WT_KEYED_ENCRYPTOR *, skip, in, out)` encrypts bytes after an unencrypted prefix and writes a length field after the prefix.
- `__wt_decrypt(session, WT_ENCRYPTOR *, skip, in, out)` reads the stored length, decrypts encrypted bytes after the prefix and length field, and restores the prefix.
- `__wt_encrypt_size(session, kencryptor, incoming_size, sizep)` computes `incoming_size + size_const + WT_ENCRYPT_LEN_SIZE`.
- Key types include `WT_ITEM`, `WT_ENCRYPTOR`, and `WT_KEYED_ENCRYPTOR`.

## Control Flow
Encryption points `src` after `skip`, reserves a 32-bit stored-size field in the output after the prefix, encrypts into the remaining output buffer sized with the encryptor's constant expansion, asserts the encryptor did not exceed the buffer, stores the final framed length with endian conversion, copies prefix bytes, and sets `out->size`. Decryption reads the framed length, validates it against input size, allocates the output buffer, decrypts payload bytes, copies the prefix, and sets the real decrypted size.

## State and Persistence Behavior
This file defines the durable on-disk/in-memory encrypted item frame: unencrypted prefix, 32-bit encrypted-frame length, then encrypted payload. It does not manage keys directly; it calls the configured encryptor. Endian conversion is applied to the stored length field.

## Dependencies and Integration Points
Used by block/page/log or metadata paths that encrypt `WT_ITEM` buffers. Depends on WiredTiger buffer allocation, endian helpers, encryptor extension APIs, and `WT_ENCRYPT_LEN_SIZE`/`size_const` contracts.

## Risks
Length validation and buffer sizing are security-sensitive. The code assumes encryptors do not expand beyond `size_const` and asserts byte-for-byte bounded behavior. Misaligned access to the stored `uint32_t` or incorrect `skip` values can corrupt framing. Decrypt rejects only `encrypt_len > in->size`; malformed smaller lengths rely on lower decryptor behavior and buffer boundaries.

## Test Signals
Tests should cover round-trip encryption with nonzero skipped headers, big-endian length handling where supported, corrupt length rejection, encryptor `size_const` sizing, zero-length payloads, custom encryptor failure propagation, and fuzzing malformed encrypted buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/err.c -->
# sources/storage-engines/wiredtiger/src/support/err.c

## Purpose
Implements WiredTiger event/error/message/progress reporting, default event handlers, verbose formatting, panic handling, extension message APIs, object-type error helpers, and a thread-local recent-error ring used for diagnostics.

## Important APIs, Types, and Functions
- `__wt_event_handler_set` installs defaults for null event-handler methods.
- `__eventv` is the central formatter for errors and verbose messages, supporting plain text and JSON output, prefixes, dhandle/session names, timestamps, thread IDs, categories, levels, log IDs, dynamic scratch buffers, and fallback to stderr.
- Public wrappers include `__wt_err_func`, `__wt_errx_func_id`, `__wt_errx_func`, `__wt_panic_func`, `__wt_verbose_worker_id`, `__wt_verbose_worker`, `__wt_msg`, `__wt_progress`, and extension APIs.
- `__wt_inmem_unsupported_op`, `__wt_object_unsupported`, `__wt_bad_object_type`, and `__wt_unexpected_object_type` centralize common API errors.
- `__wt_error_log_add`, `wiredtiger_dump_error_log`, `__wt_error_log_dump_recent`, and `__wt_error_log_to_handler` manage a thread-local circular error log.

## Control Flow
Default handlers write errors to stderr, messages to stdout, and ignore progress/close/general events. `__eventv` handles null sessions by writing to stderr, otherwise formats into a stack buffer first, grows scratch buffers for long messages, optionally JSON-encodes the message string, appends error strings without duplicating existing suffixes, calls the configured handler, and reports handler failures through `__handler_failure`. Panic first dumps the recent error log, reports the panic and restart message, optionally aborts in diagnostic corruption settings, then sets the connection panic flag.

The error log is thread-local. Add records only nonzero errors, stores file/function/line/expression/error/suberror in a ring, and dump paths either call a user callback or send recent entries through the event handler before clearing when appropriate.

## State and Persistence Behavior
No durable database state is written. Runtime state includes session event-handler pointers, connection JSON-output/error-prefix flags, thread-local error-log rings, and connection panic/data-corruption flags. Output may go to application callbacks, stdout/stderr, or extension-provided handlers.

## Dependencies and Integration Points
Used throughout WiredTiger through error macros, verbose macros, extension API, session helper last-error paths, and panic/assertion paths. Depends on scratch buffers, JSON string encoding, thread ID/time helpers, verbose category tables, event handler ABI, connection/session flags, and error string mapping.

## Risks
Error paths must avoid recursion, allocation failure crashes, and varargs misuse. JSON formatting must correctly escape user messages. Event-handler failure handling must not call a failing handler indefinitely. Panic ordering is important: applications should see the original failing thread before every API call starts returning panic. Thread-local logs help diagnostics but can miss cross-thread context.

## Test Signals
Coverage should include default handler output, application handler failure fallback, JSON/plain formatting, long message allocation, duplicate error-string suppression, null-session stderr fallback, panic flag behavior, diagnostic abort configurations, extension error/message APIs, object-type errors, error-log ring wraparound, dump-and-clear semantics, and recent-dump without clear.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/generation.c -->
# sources/storage-engines/wiredtiger/src/support/generation.c

## Purpose
Implements WiredTiger's generation-based reclamation system. Sessions publish generation numbers while accessing resources; replacers advance connection generations and wait until older session generations drain before reclaiming old objects. The file also manages per-session stashed memory that can be freed once no active session can reference its generation.

## Important APIs, Types, and Functions
- `__wt_gen_init` initializes all connection generations to 1.
- `__wt_gen_next_drain(session, which)` advances a generation and waits for older users.
- `__wt_gen_active(session, which, generation)` checks whether any session can still see a generation.
- `__wt_session_gen_enter` and `__wt_session_gen_leave` publish and clear a session's generation with required memory barriers.
- `__wt_stash_add`, `__wt_stash_discard`, and `__wt_stash_discard_all` defer and later free memory by generation.
- Internal callbacks for `__wt_session_array_walk` implement drain, oldest, and active scans.

## Control Flow
Initialization stores generation 1 for all resources. Enter loops storing the current connection generation into the session slot, uses a full barrier, and repeats if the connection generation changed during publication. Draining increments a connection generation and walks sessions; for each session with an older nonzero generation, it spins briefly, then sleeps, logging minute-level waits and optionally enabling extra verbose categories shortly before configured timeout. Oldest/active scans read session generation slots with acquire barriers.

Stash add appends a pointer/length/generation to the session stash, updates connection stashed byte/object counters, and opportunistically discards older entries. Discard computes the oldest active generation for that resource, frees stash entries older than it, subtracts counters, overwrites freed memory, and compacts the stash list when many entries were removed.

## State and Persistence Behavior
No persistent data is written. Runtime state includes connection generation counters, per-session generation slots, generation drain timeout settings, verbose levels temporarily raised near timeout, per-session stash arrays, and connection stashed memory counters. Memory reclamation is delayed until generation visibility proves safety.

## Dependencies and Integration Points
Used by split, hazard, eviction, checkpoint, snapshot, and transaction commit generation users. Depends on session-array walking from `session_helper.c`, atomic operations, memory barriers, verbose/error infrastructure, sleep/yield primitives, and WiredTiger allocation/free helpers.

## Risks
Memory ordering is the main risk. If enter/leave barriers are weakened or scans read values out of order, old objects can be freed while still visible. Draining while the current session holds the target generation triggers a panic for self-deadlock. Long drains can indicate leaked generation entries or stuck sessions. Stash ordering assumes callers generally add nondecreasing generations; out-of-order entries delay reclamation.

## Test Signals
Tests should stress concurrent enter/leave with generation advancement, active/oldest detection, self-deadlock diagnostics, drain timeout logging, stash add/discard counters, discard-all at connection close, and resource-specific users such as split/hazard/checkpoint generations under sanitizer and stress configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/generation.c -->
