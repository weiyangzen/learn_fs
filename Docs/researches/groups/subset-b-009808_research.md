# subset-b-009808 research

Grouped research report for Samba source3 library files. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.c -->
# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.c

Purpose: implements a `dbwrap` decorator that stores per-record watcher metadata before the application payload and wakes waiting Samba processes via internal messaging when a watched record changes. It lets higher layers block on database record mutation without adding watcher semantics to every backend.

Important APIs/types/functions: `struct dbwrap_watcher` serializes a `server_id` plus per-process instance; `struct db_watched_record` wraps the backend `db_record`; `db_open_watched()` builds the decorated `db_context`; `dbwrap_watched_watch_add_instance()`, `dbwrap_watched_watch_remove_instance()`, alert-control helpers, `dbwrap_watched_watch_send()`, and `dbwrap_watched_watch_recv()` form the public watch API. Internal parsing is centralized in `dbwrap_watch_rec_parse()`, with `dbwrap_watched_record_storev()` rebuilding the watcher header and payload.

Control flow: fetch/do-locked paths lock the backend record, parse the watcher header, expose only the user payload as `rec->value`, and install store/delete methods that rewrite both watcher and payload state. On mutation, `dbwrap_watched_record_prepare_wakeup()` selects the first live watcher, `dbwrap_watched_record_storev()` persists the updated header/payload, and destructors trigger `MSG_DBWRAP_MODIFIED`. `dbwrap_watched_watch_send()` optionally adds a watcher instance, then waits with `messaging_filtered_read_send()` and optionally `server_id_watch_send()` for a blocker process death.

State/persistence behavior: each record is encoded as `uint32 num_watchers`, an array of fixed-size watcher entries, then the real data. Empty records mean no watcher header. Watcher addition/removal is persisted back at record release or store time; invalid headers are logged and treated as empty user data. The backend DB is moved under the watched context and its lock order is suppressed so the wrapper owns that ordering surface.

Dependencies/integration: depends on `dbwrap`, `messaging`, `serverid`, `server_id_watch`, TDB data helpers, and NTSTATUS/tevent request conventions. `g_lock.c` is the main consumer for global lock waiting and data-change watching. Torture coverage is registered through `test_dbwrap_watch.c` and `test_dbwrap_do_locked.c`.

Risks/test signals: watcher fairness and cleanup depend on first-watcher wakeups, process-existence pruning, and destructor execution. Corrupt watcher headers can hide payloads. A watch that keeps an instance via `pkeep_instance` must later remove it. Tests should cover payload preservation across add/remove, wakeup ordering, blocker death, invalid records, and no duplicate alerting when only watcher metadata changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.h -->
# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.h

Purpose: declares the watched-dbwrap public API used by database clients that need asynchronous notification when a locked record is modified.

Important APIs/types/functions: `db_open_watched()` wraps an existing backend `db_context`; `dbwrap_watched_watch_add_instance()` and `dbwrap_watched_watch_remove_instance()` manage watcher identities on a locked record; `dbwrap_watched_watch_skip_alerting()`, `dbwrap_watched_watch_reset_alerting()`, and `dbwrap_watched_watch_force_alerting()` tune whether a store wakes waiters; `dbwrap_watched_watch_send()`/`recv()` provide tevent-based waiting with optional blocker tracking.

Control flow: callers first open or receive a watched database, fetch or operate on a locked record, add or resume a watcher instance, then wait asynchronously. The receive call returns NTSTATUS plus optional keep-instance, blocker-dead, and blocker-id outputs.

State/persistence behavior: the header does not expose the on-disk format, but its API implies watcher state is tied to the lifetime and locked mutation of a `db_record`. Resumed instances allow a caller to keep its queue position across repeated wait cycles.

Dependencies/integration: includes `tevent.h`, `dbwrap/dbwrap.h`, and Samba `messages.h`. It is consumed by `g_lock.c` and by source3 torture tests for watch semantics.

Risks/test signals: correct use requires a watched record; calling these helpers on ordinary dbwrap records would violate private-data assumptions. Test signals are compile-time API coverage and runtime watch wakeups, instance resumption, cleanup on request destruction, and unsupported messaging contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dmallocmsg.c -->
# sources/user-network-fs/samba/source3/lib/dmallocmsg.c

Purpose: registers Samba messaging handlers that integrate with optional `dmalloc` debugging so a running daemon can mark heap state and later log changed allocations.

Important APIs/types/functions: `register_dmalloc_msgs()` registers `MSG_REQ_DMALLOC_MARK` and `MSG_REQ_DMALLOC_LOG_CHANGED`; `msg_req_dmalloc_mark()` records `dmalloc_mark()` in `our_dm_mark`; `msg_req_dmalloc_log_changed()` calls `dmalloc_log_changed()` when compiled with `ENABLE_DMALLOC`.

Control flow: during messaging context initialization, `register_dmalloc_msgs()` adds classic callbacks. Incoming mark messages either save the current mark or log that dmalloc is unavailable. Incoming log-changed messages dump allocation changes since the saved mark.

State/persistence behavior: state is process-local only: a static `unsigned long our_dm_mark`. No durable storage is used, and the handlers only emit debug logs when dmalloc is disabled.

Dependencies/integration: depends on `messages.h`, Samba debug macros, and optional dmalloc symbols. It is wired from `messages.c` during `messaging_init_internal()`.

Risks/test signals: the feature is compile-option dependent and silent apart from debug output. Tests are mostly build/configuration signals: handlers should register in all builds, and dmalloc builds should mark/log without affecting normal messaging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dmallocmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dumpcore.c -->
# sources/user-network-fs/samba/source3/lib/dumpcore.c

Purpose: sets up and performs controlled core dumping for Samba processes, choosing a safe core directory and handling platform-specific core-path behavior before aborting.

Important APIs/types/functions: `dump_core_setup()` derives the log base and calls `get_corepath()`; `dump_core()` enforces one-shot recursion protection, configuration gating, privilege handling, cwd selection, dumpability, signal reset, and final `abort()`. Helpers include `get_default_corepath()`, Linux `/proc/sys/kernel/core_pattern` parsing, and FreeBSD `kern.corefile` probing.

Control flow: setup computes `<logbase>/cores/<progname>` unless the OS has an absolute core path or helper-binary core handler. It creates directories with restrictive permissions. On fatal error, `dump_core()` exits if core files are disabled, becomes root if needed, changes into the core directory unless a helper handles cores, flushes debug output, marks the process dumpable on Linux, resets SIGABRT, and aborts.

State/persistence behavior: static `corepath` and `using_helper_binary` cache setup results. Persistent effects are directory creation under the log/core tree and the eventual OS-created core file. The function intentionally may retain elevated privilege through abort so the core can be written.

Dependencies/integration: depends on Samba config (`lp_enable_core_files()`), security helpers, debug flushing, file/directory helpers, optional sysctl/prctl, and platform macros. It is called from generic fatal-error paths such as utility panic handling.

Risks/test signals: incorrect directory permissions could leak cores or prevent crash diagnostics. Helper-binary detection must not chdir into a meaningless path. Recursion protection exits immediately. Test signals include setup on Linux absolute/relative/pipe core patterns, disabled core policy, non-root privilege change, and refusal when corepath cannot be created.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dumpcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/errmap_unix.c -->
# sources/user-network-fs/samba/source3/lib/errmap_unix.c

Purpose: maps Unix `errno` values to NTSTATUS results for source3 code that needs Windows-compatible error reporting.

Important APIs/types/functions: `map_nt_error_from_unix(int unix_error)` scans the static `unix_nt_errmap[]` table and returns the mapped status. The table covers transient, filesystem, network, quota, permission, unsupported, overflow, and path errors with conditional entries for platform-specific errno constants.

Control flow: callers pass an errno value; the function linearly checks known entries and returns a default NT status when no mapping exists. Conditional compilation keeps portability across systems with different errno sets.

State/persistence behavior: no mutable state or persistence. It is a pure mapping table.

Dependencies/integration: used broadly by tevent, messaging, dbwrap-watch, and system-call wrappers that convert Unix failures into NTSTATUS. It includes `includes.h` for errno and NTSTATUS definitions.

Risks/test signals: wrong mappings can affect SMB client-visible behavior, retry decisions, and access-denied versus not-found semantics. Tests should check common errno translations, platform-specific build coverage, and fallback behavior for unknown errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/errmap_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/eventlog/eventlog.c -->
# sources/user-network-fs/samba/source3/lib/eventlog/eventlog.c

Purpose: manages Samba source3 eventlog TDB files and converts between the internal TDB record representation and Windows EVENTLOG structures/EVT file blobs.

Important APIs/types/functions: `elog_init_tdb()`, `elog_tdbname()`, `elog_tdb_size()`, `prune_eventlog()`, `elog_open_tdb()`, `elog_close_tdb()`, `parse_logentry()`, `fixup_eventlog_record_tdb()`, `evlog_pull_record_tdb()`, `evlog_pull_record()`, `evlog_push_record_tdb()`, `evlog_push_record()`, `evlog_evt_entry_to_tdb_entry()`, `evlog_tdb_entry_to_evt_entry()`, and `evlog_convert_tdb_to_evt()`. `open_elog_list` holds refcounted open logs.

Control flow: logs live under `state_path("eventlog")` as lowercased `<name>.tdb`. Open either reuses an existing `ELOG_TDB`, validates version, or initializes a fresh database. Push locks `EVT_NEXT_RECORD`, assigns the next record number, NDR-encodes the TDB record, stores by record-number key, increments the next-record counter, and unlocks. Pull fetches by record number and NDR-decodes. Conversion iterates records from 1 upward, translates each into `EVENTLOGRECORD`, builds header/eof metadata, and NDR-pushes an EVT blob.

State/persistence behavior: TDB metadata keys track oldest entry, next record, maximum size, retention, and database version. Pruning deletes oldest records and advances `EVT_OLDEST_ENTRY` based on max-size and retention policy. Record payloads are binary NDR `eventlog_Record_tdb` blobs keyed by int32 record numbers. The open list is process-local with explicit force-close behavior.

Dependencies/integration: uses TDB, Samba state paths, directory helpers, DLIST, NDR-generated eventlog structures, SID/string conversion, and security headers. Selftest includes `rpc.eventlog`, and higher RPC eventlog services depend on these utilities.

Risks/test signals: record-number locking is central; missing unlocks or failed stores can corrupt sequencing. Retention logic depends on record timestamps and can reject writes when retention is infinite. Conversion must preserve UTF-16 string sizing, SID padding, and trailing record length. Tests should cover open refcounts, version reset, push/pull round trips, pruning, text parsing, SID conversion, and EVT export record counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/eventlog/eventlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/eventlog/eventlog.h -->
# sources/user-network-fs/samba/source3/lib/eventlog/eventlog.h

Purpose: defines source3 eventlog database constants and the `ELOG_TDB` handle used by eventlog utility and RPC code.

Important APIs/types/functions: `ELOG_TDB` stores a linked-list node, log name, TDB handle, and reference count. Key names such as `EVT_OLDEST_ENTRY`, `EVT_NEXT_RECORD`, `EVT_VERSION`, `EVT_MAXSIZE`, and `EVT_RETENTION` define metadata records. The database version macro identifies the supported TDB layout.

Control flow: this header has no executable flow, but consumers use its constants to initialize, validate, read, prune, and export log databases.

State/persistence behavior: constants are the persistent metadata key contract for eventlog TDB files. `ELOG_TDB` state is process-local and tracks ownership/refcounting of an open TDB.

Dependencies/integration: included by `eventlog.c` and eventlog RPC service code. It depends on generated eventlog structures and TDB declarations through surrounding include chains.

Risks/test signals: changing key strings or version values invalidates existing eventlog databases. Tests should confirm metadata initialization and compatibility behavior on version mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/eventlog/eventlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/eventlog/proto.h -->
# sources/user-network-fs/samba/source3/lib/eventlog/proto.h

Purpose: declares the eventlog utility API exported by `eventlog.c`.

Important APIs/types/functions: path/size/pruning functions, TDB close, text-entry parsing, record fixup, TDB and EVT pull/push helpers, conversion between `eventlog_Record_tdb` and `EVENTLOGRECORD`, and full TDB-to-EVT blob conversion.

Control flow: callers open logs elsewhere, then use these declarations to parse text records, push or pull records, and export log contents for RPC or file operations.

State/persistence behavior: the API exposes functions that mutate TDB metadata and records, return allocated record structures, and update output record numbers/counts.

Dependencies/integration: includes `eventlog.h` and generated NDR eventlog types indirectly. It is part of source3's internal prototype style for eventlog consumers.

Risks/test signals: declarations must match implementation exactly, especially ownership of returned talloc objects and NTSTATUS returns. Compile coverage and RPC eventlog tests are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/eventlog/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/file_id.c -->
# sources/user-network-fs/samba/source3/lib/file_id.c

Purpose: provides small helpers for comparing, formatting, and serializing Samba `struct file_id` values.

Important APIs/types/functions: `file_id_equal()` compares device, inode, and extension fields; `file_id_str_buf()` formats into `struct file_id_buf`; `push_file_id_16()` writes a compact 16-byte representation with device and inode.

Control flow: all functions are direct utility paths with no allocation except caller-provided buffers.

State/persistence behavior: no mutable state. Serialization with `push_file_id_16()` is a byte-level persistence/interchange format that omits `extid`, so callers must only use it where 16-byte dev/inode identity is sufficient.

Dependencies/integration: used by locking, open-file tracking, debug output, and tests such as `locktest2.c`. Depends on Samba byte-order store macros.

Risks/test signals: equality must include `extid`; any mismatch between formatting and equality can confuse diagnostics. Tests should cover equality with extid differences and stable byte ordering of serialized ids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/file_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/file_id.h -->
# sources/user-network-fs/samba/source3/lib/file_id.h

Purpose: declares the file-id helper API and the fixed-size formatting buffer type.

Important APIs/types/functions: `struct file_id_buf` holds printable file-id text; `file_id_equal()`, `file_id_str_buf()`, and `push_file_id_16()` are the exported helpers.

Control flow: no runtime flow in the header. It defines the contract used by callers that compare, log, or serialize file identities.

State/persistence behavior: the header establishes that file-id formatting is caller-buffer based and that 16-byte serialization is available for compact storage.

Dependencies/integration: included by source3 locking, VFS, and torture code that manipulates `struct file_id`.

Risks/test signals: consumers must pass a correctly sized destination buffer and understand the 16-byte representation. Compile coverage and lock/open-file tests catch contract drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/file_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/filename_util.c -->
# sources/user-network-fs/samba/source3/lib/filename_util.c

Purpose: centralizes manipulation, copying, debug formatting, and stream parsing for `struct smb_filename` and related file/EA helper types.

Important APIs/types/functions: `get_full_smb_filename()`, `synthetic_smb_fname()`, `cp_smb_basename()`, `cp_smb_filename_nostream()`, `synthetic_smb_fname_split()`, `smb_fname_str_dbg()`, `fsp_str_dbg()`, `fsp_fnum_dbg()`, `cp_smb_filename()`, stream predicates `is_ntfs_stream_smb_fname()`, `is_named_stream()`, `is_ntfs_default_stream_smb_fname()`, EA validation helpers, and `split_stream_filename()`.

Control flow: construction helpers build a temporary local `smb_filename` then deep-copy it using a pooled talloc object. Debug helpers derive a full name and append an `@GMT` timestamp when `twrp` is set. Stream checks validate invariants first, then classify stream-name presence/defaultness. Split finds the first colon and returns separately allocated base and stream strings.

State/persistence behavior: no global state. Returned objects own copies of base and stream names plus stat/timestamp/flag fields. The code enforces the invariant that `stream_name == NULL` means no stream and non-NULL stream names are nonempty; POSIX-path filenames must not carry stream names.

Dependencies/integration: used throughout smbd VFS and path-based operations while `smb_filename` is being threaded through call paths. It depends on talloc, NT time conversion, GMT path format helpers, stream parsing, and EA list structures.

Risks/test signals: stream parsing with colons is security-sensitive for alternate data streams and POSIX path behavior. Pooled copies must preserve ownership safely. Tests should cover base-only, named stream, default stream, empty/invalid stream invariants, timestamp debug strings, invalid Windows EA characters, and split allocation failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/filename_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/fstring.c -->
# sources/user-network-fs/samba/source3/lib/fstring.c

Purpose: provides fixed-size ASCII conversion helpers for source3 `fstring` and NetBIOS `nstring` buffers.

Important APIs/types/functions: `push_ascii_fstring()`, `pull_ascii_fstring()`, `push_ascii_nstring()`, and `pull_ascii_nstring()`. The nstring push path uses `convert_string_error()` from Unix to DOS codepage and truncates safely when conversion hits `E2BIG`.

Control flow: fstring helpers delegate to `push_ascii()`/`pull_ascii()` with `sizeof(fstring)` and terminating semantics. Nstring push clears `errno`, converts into `sizeof(nstring)`, forces the last byte to NUL on success/truncation, and clears the destination on hard conversion failure. Nstring pull allows expansion from DOS codepage into a larger caller buffer.

State/persistence behavior: no global state or durable persistence. The important state behavior is truncation/bounds handling inside fixed stack or struct buffers.

Dependencies/integration: used by ID mapping, path, debug, and protocol helper code that still relies on `fstring` buffers. It depends on Samba string and debug infrastructure.

Risks/test signals: off-by-one truncation, conversion failure handling, and guaranteed NUL termination are the primary risks. Tests should include oversized multibyte names, unconvertible characters, and destination-size boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/fstring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/g_lock.c -->
# sources/user-network-fs/samba/source3/lib/g_lock.c

Purpose: implements global read/write/update locks over a watched TDB record, with process-death cleanup, data payload storage, async waiting, and watcher wakeups.

Important APIs/types/functions: `g_lock_ctx_init_backend()`, `g_lock_ctx_init()`, `g_lock_set_lock_order()`, `g_lock_lock_send()/recv()`, synchronous `g_lock_lock()`, `g_lock_unlock()`, `g_lock_writev_data()`, `g_lock_write_data()`, `g_lock_locks[_read]()`, `g_lock_dump[_send]/recv()`, `g_lock_watch_data_send()/recv()`, `g_lock_wake_watchers()`, and callback helpers `g_lock_lock_cb_*`. Internal `struct g_lock` encodes exclusive owner, shared owners, lock/data epochs, and arbitrary data.

Control flow: lock records are parsed by `g_lock_parse()` from a TDB value. Fast synchronous read/write acquisition uses `g_lock_lock_simple_fn()` for uncontended paths; contended or upgrade/downgrade paths use `g_lock_lock_send()`, `g_lock_trylock()`, and `dbwrap_watched_watch_send()` to wait for the blocker or timeout, then retry. Unlock removes either shared or exclusive ownership, advances the lock epoch, and wakes waiters when appropriate. Data writes require exclusive ownership and advance the data epoch. Data-watch requests loop until `unique_data_epoch` changes, requeueing behind lock-epoch-only changes for fairness.

State/persistence behavior: each lock record stores serialized exclusive `server_id`, two 64-bit epochs, shared-count, shared `server_id` array, and optional data blob. The default backend is volatile `g_lock.tdb` under the lock directory with `TDB_CLEAR_IF_FIRST`; custom backends can be wrapped. Process liveness cleanup removes dead exclusive holders and randomly prunes dead shared holders. Callback unlock can delete empty records.

Dependencies/integration: depends on `dbwrap_watch`, source3 messaging, server-id databases, lock-order instrumentation, TDB utilities, tevent requests, and source3 lock paths. Torture tests in `test_g_lock.c` cover basic locks, data, upgrade/downgrade, contention, death cleanup, watchers, and ping-pong behavior.

Risks/test signals: lock correctness depends on epoch handling, single first-watcher wakeup, reliable process-death detection, and strict `ctx->busy` assertions preventing reentrancy. Upgrade paths can produce possible-deadlock status. Tests should stress cross-process contention, stale holder cleanup, timeout retry, data-watch fairness, callback writes/unlocks, and lock-order accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/g_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/gencache.c -->
# sources/user-network-fs/samba/source3/lib/gencache.c

Purpose: implements a persistent process-shared generic cache backed by `gencache.tdb`, with timeout metadata, CRC validation, deletion markers, string/blob APIs, and pattern iteration.

Important APIs/types/functions: `gencache_set_data_blob()`, `gencache_get_data_blob()`, `gencache_set()`, `gencache_get()`, `gencache_del()`, `gencache_parse()`, `gencache_iterate_blobs()`, `gencache_iterate()`, `gencache_timeout_expired()`, and internal `gencache_init()`, `gencache_pull_timeout()`, and chain pruning helpers.

Control flow: initialization opens `lock_path("gencache.tdb")` with mutex locking and a configurable hash size; non-root `EACCES` falls back to `~/.cache/samba/gencache.tdb`. Set locks the key hash chain, prunes expired entries on that chain, stores timeout+payload+CRC, and unlocks. Get parses and validates the record, treats expired entries as failures after writing a delete marker, and optionally returns timeout/expiration state. Iteration traverses all records, validates CRC, filters by `fnmatch`, and calls user callbacks.

State/persistence behavior: records are stored under NUL-terminated string keys as raw `time_t`, payload bytes, and CRC32 over key+timeout+payload. Corruption or format errors can delete individual records or wipe the whole cache. Timeout `0` is a delete marker ignored by iterators. The static `cache` handle is process-global.

Dependencies/integration: used by idmap, name-map, wins, remote announce, and local torture tests. Depends on TDB wrap, zlib CRC32, Samba path helpers, string-vector helpers, and configuration parameters.

Risks/test signals: `time_t` storage is ABI-sensitive across architectures. CRC protects against stale/corrupt data but wipe-all on corruption is broad. Expiration writes a marker rather than deleting immediately. Tests should cover strings versus blobs, NUL termination, expiration, pattern iteration, fallback user cache path, and local torture `run_local_gencache`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/gencache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/gencache.h -->
# sources/user-network-fs/samba/source3/lib/gencache.h

Purpose: declares the generic cache API for string and blob values with explicit timeouts.

Important APIs/types/functions: `gencache_set()`, `gencache_del()`, `gencache_get()`, `struct gencache_timeout`, `gencache_timeout_expired()`, `gencache_parse()`, `gencache_get_data_blob()`, `gencache_set_data_blob()`, `gencache_iterate_blobs()`, and `gencache_iterate()`.

Control flow: callers set keys with absolute expiration times, fetch values or parse raw blobs with a callback, and iterate matching keys using shell-style patterns.

State/persistence behavior: the header exposes timeout objects as opaque except for expiration checking. Values are allocated on caller-provided talloc contexts where appropriate.

Dependencies/integration: included by idmap/name-map/WINS utilities and tests. It depends on `DATA_BLOB`, `time_t`, and talloc types.

Risks/test signals: callback ownership and expiry semantics must be understood by consumers; expired entries can still be detected via parse APIs. Compile coverage and cache torture tests validate the contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/gencache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/global_contexts.c -->
# sources/user-network-fs/samba/source3/lib/global_contexts.c

Purpose: lazily creates and owns process-global source3 tevent and messaging contexts for code paths that need shared event/messaging services.

Important APIs/types/functions: `global_event_context()`, `global_event_context_free()`, `global_messaging_context()`, and `global_messaging_context_free()`.

Control flow: the event accessor initializes a singleton tevent context on first use. The messaging accessor ensures the event context exists, then initializes a singleton messaging context on that event loop. Free functions release the singleton pointers.

State/persistence behavior: process-global static pointers hold the contexts. No durable state is stored directly, but messaging initialization creates sockets/lock-directory state through `messages.c`.

Dependencies/integration: depends on Samba tevent creation and `messaging_init()`. Used by source3 code that does not carry explicit context handles.

Risks/test signals: singleton lifecycle is sensitive after fork, shutdown, and test isolation. Tests should check repeated accessor calls, explicit free/recreate, and failure propagation when messaging initialization fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/global_contexts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/global_contexts.h -->
# sources/user-network-fs/samba/source3/lib/global_contexts.h

Purpose: declares accessors for process-global tevent and messaging contexts.

Important APIs/types/functions: forward declarations for `struct tevent_context` and `struct messaging_context`, plus create/access and free functions for each singleton.

Control flow: no implementation flow; callers use it to avoid directly managing common process contexts.

State/persistence behavior: advertises singleton ownership through explicit free functions. The underlying state is process-local.

Dependencies/integration: included by source3 modules needing default event or messaging contexts.

Risks/test signals: header users must not assume ownership of returned pointers. Compile tests and lifecycle tests of `global_contexts.c` catch signature drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/global_contexts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/id_cache.c -->
# sources/user-network-fs/samba/source3/lib/id_cache.c

Purpose: provides messaging-driven invalidation of ID-related caches, including idmap gencache entries and username passwd-cache entries.

Important APIs/types/functions: `struct id_cache_ref` identifies UID, GID, SID, or username references; `id_cache_ref_parse()` parses `UID <n>`, `GID <n>`, SID strings, and `USER <name>`; `id_cache_delete_from_cache()` delegates to idmap-cache or memcache deletion; `id_cache_delete_message()` is the messaging callback; `id_cache_register_msgs()` registers `ID_CACHE_DELETE`.

Control flow: a message payload is parsed into an id-cache reference. Depending on type, the delete path calls `idmap_cache_del_uid()`, `idmap_cache_del_gid()`, `idmap_cache_del_sid()`, or deletes `GETPWNAM_CACHE` from memcache with a NUL-terminated username blob. Invalid messages are logged and ignored. Registration hooks the callback into the messaging context.

State/persistence behavior: this file has no durable state of its own. Its effects are deleting persistent `gencache.tdb` idmap entries through `idmap_cache.c` and process-local memcache username entries.

Dependencies/integration: depends on source3 messaging, SID parsing/NDR security headers, source3 memcache, and `idmap_cache.h`. Torture coverage exists for idmap cache behavior in `test_idmap_cache.c`.

Risks/test signals: parser ambiguity can cause stale mappings to remain or wrong mappings to be deleted. Tests should cover all ref syntaxes, malformed payloads, and cross-process invalidation via messaging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/id_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/id_cache.h -->
# sources/user-network-fs/samba/source3/lib/id_cache.h

Purpose: declares the ID-cache invalidation reference type and messaging hooks.

Important APIs/types/functions: `struct id_cache_ref` carries a type discriminator and union of uid/gid/SID/name data; `id_cache_ref_parse()`, `id_cache_delete_from_cache()`, `id_cache_register_msgs()`, and `id_cache_delete_message()` form the API.

Control flow: consumers can parse text references and either delete directly or register/delete through messaging callbacks.

State/persistence behavior: the header describes cache-deletion operations but stores no state. Deletions affect idmap entries in gencache.

Dependencies/integration: depends on source3 messaging and SID/idmap definitions via includes.

Risks/test signals: the struct layout must match parser/deleter assumptions. Compile coverage and idmap-cache torture tests are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/id_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/idmap_cache.c -->
# sources/user-network-fs/samba/source3/lib/idmap_cache.c

Purpose: stores, retrieves, and deletes SID-to-Unix-ID and Unix-ID-to-SID mappings in the generic cache, including positive and negative mapping results.

Important APIs/types/functions: `idmap_cache_find_sid2unixid()`, `idmap_cache_find_sid2uid()`, `idmap_cache_find_sid2gid()`, `idmap_cache_find_xid2sid()`, `idmap_cache_set_sid2unixid()`, `idmap_cache_del_uid()`, `idmap_cache_del_gid()`, and `idmap_cache_del_sid()`. Internal key helpers build `IDMAP/SID2XID/<sid>`, `IDMAP/UID2SID/<id>`, and `IDMAP/GID2SID/<id>`.

Control flow: find-by-SID fetches a string value and parses `<id>:<type>` where type is U/G/B/N. Find-by-XID parses a cached SID string or `-` negative marker via `gencache_parse()`. Set writes the SID2XID entry unless the SID is null, and writes UID2SID/GID2SID entries unless the Unix ID is `-1`. Delete-by-XID removes the reverse key and, if positive, the associated SID key. Delete-by-SID looks up the mapping, removes corresponding UID/GID reverse keys, then deletes the SID key.

State/persistence behavior: entries live in gencache with timeouts from `lp_idmap_cache_time()` or `lp_idmap_negative_cache_time()`. Negative SID mappings use Unix ID `-1`; negative XID mappings use null SID and value `-`. Expired state can be returned to callers rather than being invisible in all code paths.

Dependencies/integration: depends on `gencache`, SID string conversion, generated idmap `struct unixid`, and Samba loadparm cache-time settings. It is invoked by winbind/idmap paths and by `id_cache.c` invalidation. Torture `test_idmap_cache.c` exercises basic positive and delete behavior.

Risks/test signals: asymmetric delete errors can leave stale reverse mappings. Type parsing controls whether UID/GID/BOTH mappings are returned. Negative cache times affect correctness after external mapping changes. Tests should cover positive UID/GID/BOTH, negative SID and XID, expiration flags, delete-by-SID, delete-by-UID/GID, and malformed cache values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/idmap_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/idmap_cache.h -->
# sources/user-network-fs/samba/source3/lib/idmap_cache.h

Purpose: declares idmap cache lookup, set, and invalidation functions.

Important APIs/types/functions: lookup by SID to `unixid`, UID, or GID; lookup by Unix ID to SID; `idmap_cache_set_sid2unixid()`; and delete helpers for UID, GID, or SID.

Control flow: callers use find functions with output `expired` flags, write mappings after ID resolution, and delete when mappings are invalidated.

State/persistence behavior: API implies persistent cache mutation through gencache while exposing only typed mapping results.

Dependencies/integration: forward-declares `struct unixid` and uses `dom_sid`, UID/GID types, and bool.

Risks/test signals: output pointers must be valid, and callers must interpret negative values/null SID according to implementation comments. Compile and torture tests validate signatures and basic semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/idmap_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/interface.c -->
# sources/user-network-fs/samba/source3/lib/interface.c

Purpose: probes, filters, configures, stores, and queries the local network interfaces Samba should bind to or advertise.

Important APIs/types/functions: query helpers `ismyaddr()`, `ismyip_v4()`, `is_local_net()`, `setup_linklocal_scope_id()`, `iface_count()`, `first_ipv4_iface()`, `get_interface()`, `iface_n_*()`, `iface_ip()`, `iface_local()`, `interfaces_changed()`, `interface_ifindex_exists_with_options()`, plus `load_interfaces()` and `gfree_interfaces()`. Internal `interpret_interface()` parses smb.conf interface tokens and `parse_extra_info()` handles speed/capability/if_index/options metadata.

Control flow: `load_interfaces()` clears existing state, probes kernel interfaces with `get_interfaces()`, and either adds all broadcast-capable probed interfaces or parses configured tokens. Tokens can match interface names/wildcards, DNS/IP addresses, IP/mask, broadcast/mask, or synthetic interfaces, with optional `;key=value` metadata. Queries then walk the `local_interfaces` linked list for exact address, same-net, indexed, or family-matching answers.

State/persistence behavior: `probed_ifaces`, `total_probed`, and `local_interfaces` are process-global mutable state. No durable persistence exists, but state mirrors kernel/interface configuration and smb.conf. `gfree_interfaces()` releases names and probed arrays.

Dependencies/integration: depends on socket/interface probing, loadparm `lp_interfaces()`, SMB string-to-number helpers, FSCTL network interface capability constants, sockaddr utilities, and DLIST memory helpers. Used by server bind/listen, address-selection, and network interface info reporting.

Risks/test signals: parsing mistakes can expose unintended interfaces or fail to bind expected ones. IPv6 scope setup matters for link-local addresses. Duplicate and non-broadcast filtering affect service reachability. Tests should cover configured wildcard/IP/mask/broadcast tokens, dynamic option parsing, interfaces_changed after reprobe, and query fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/interface.h -->
# sources/user-network-fs/samba/source3/lib/interface.h

Purpose: declares source3 interface query and lifecycle functions plus interface option flags.

Important APIs/types/functions: `IFACE_NONE_OPTION`, `IFACE_DYNAMIC_OPTION`, address/net predicates, interface count/accessors, `load_interfaces()`, `gfree_interfaces()`, `interfaces_changed()`, and `interface_ifindex_exists_with_options()`.

Control flow: callers load global interface state, then query local addresses, networks, broadcasts, and interface indexes/options.

State/persistence behavior: the header exposes access to process-global interface state managed by `interface.c`; returned pointers refer to that state and should not be freed by callers.

Dependencies/integration: used by smbd/nmbd networking and FSCTL network-interface reporting paths.

Risks/test signals: callers must call `load_interfaces()` before relying on results. Compile coverage plus interface parsing and bind tests validate the API.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ldap_debug_handler.c -->
# sources/user-network-fs/samba/source3/lib/ldap_debug_handler.c

Purpose: wires LDAP/LBER library debug output into Samba debug logging when the platform provides the required callback hook.

Important APIs/types/functions: `init_ldap_debugging()` configures `lber_set_option(NULL, LBER_OPT_LOG_PRINT_FN, ...)`; `samba_ldap_log_print_fn()` logs library messages with Samba debug macros under `HAVE_LDAP && HAVE_LBER_LOG_PRINT_FN`.

Control flow: initialization is a no-op on unsupported builds. Supported builds set the print function so LDAP library diagnostics are routed through Samba logging.

State/persistence behavior: process-global library option state changes inside LBER. No durable storage.

Dependencies/integration: depends on LDAP headers from `smb_ldap.h`, build-time feature macros, and Samba debug logging. Used during LDAP-enabled daemon initialization.

Risks/test signals: callback availability is platform dependent. Misconfigured logging can drop useful LDAP diagnostics or call an incompatible function signature. Build matrix and LDAP debug smoke tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ldap_debug_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ldap_escape.c -->
# sources/user-network-fs/samba/source3/lib/ldap_escape.c

Purpose: escapes untrusted strings for LDAP filters and RDN values.

Important APIs/types/functions: `escape_ldap_string()` produces RFC-style filter escaping for special bytes such as NUL, parentheses, backslash, wildcard, and control characters; `escape_rdn_val_string_alloc()` returns a newly allocated escaped RDN value string.

Control flow: each function scans the input, calculates/allocates a destination, and emits either literal bytes or escaped hex/backslash sequences according to LDAP filter/RDN rules.

State/persistence behavior: no global state or persistence. Ownership differs: filter escaping uses a talloc context, while the RDN helper returns heap memory that callers must free with the appropriate allocator.

Dependencies/integration: used by LDAP account, idmap, and directory query construction. Depends on Samba allocation/string helpers.

Risks/test signals: incomplete escaping is injection-sensitive; over-escaping can break legitimate names. Tests should cover NUL/control bytes, `*()\\`, leading/trailing spaces, `#`, commas/plus/equal in RDNs, empty strings, and allocation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ldap_escape.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/lsa.c -->
# sources/user-network-fs/samba/source3/lib/lsa.c

Purpose: adds or finds domains in an LSA referenced-domain list used by RPC responses that return SIDs grouped by domain.

Important APIs/types/functions: `init_lsa_ref_domain_list()` updates `struct lsa_RefDomainList`, compares existing entries with `dom_sid_equal()`, reallocates `struct lsa_DomainInfo`, duplicates the domain name, and duplicates the SID.

Control flow: if a domain name is provided, the helper first scans existing referenced domains and returns the existing index when the SID is already present. Otherwise it appends at `ref->count`, enforces `LSA_REF_DOMAIN_LIST_MULTIPLIER`, updates count/max-size, reallocates the domain array, zeroes the new entry, and fills name and SID. It returns the domain index or `-1`.

State/persistence behavior: no global or durable state. Output ownership is entirely through the provided talloc context and generated LSA structures.

Dependencies/integration: depends on `DATA_BLOB`, Samba time/security SID helpers, and generated `librpc/gen_ndr/lsa.h`. Used by LSA/SAMR-style RPC code that needs consistent referenced-domain lists.

Risks/test signals: incorrect count/allocation handling can produce malformed RPC replies. Tests should cover zero domains, multiple domains, null names/SIDs, and NDR encode/decode of callers' responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages.c -->
# sources/user-network-fs/samba/source3/lib/messages.c

Purpose: implements Samba source3 internal process messaging over local datagram sockets and optional CTDB cluster transport, including classic callbacks, async filtered reads, self-posting, fd passing, cleanup, and process-name database integration.

Important APIs/types/functions: `struct messaging_context`, `messaging_init()`, `messaging_reinit()`, `messaging_server_id()`, `messaging_register()`, `messaging_deregister()`, `messaging_send()`, `messaging_send_buf()`, `messaging_send_iov_from()`, `messaging_send_iov()`, `messaging_send_all()`, `messaging_filtered_read_send()/recv()`, `messaging_read_send()/recv()`, `messaging_cleanup()`, `messaging_parent_dgm_cleanup_init()`, `messaging_tevent_context()`, and `messaging_names_db()`.

Control flow: initialization creates strict lock/private socket directories, opens a datagram receiver with `messaging_dgm_ref()`, optionally attaches CTDB transport, initializes `server_id_db`, and registers debug/ping/dmalloc/talloc handlers. Incoming datagrams are decoded into `messaging_rec`, self-sends are ignored, and records are dispatched to classic callbacks or tevent waiters. Nested event contexts can repost unconsumed messages to the main context. Sending builds the message header, handles same-process posting, cluster routing by VNN, local datagram send, root retry on `EACCES`, and `ECONNREFUSED` normalization.

State/persistence behavior: `messaging_context` owns callbacks, posted messages, registered event contexts, waiter arrays, per-process transport references, and a server-id names database. Local socket and lock directories persist on disk; datagram cleanup wipes stale socket state periodically. File descriptors in messages are transferred by ownership and closed when unconsumed.

Dependencies/integration: depends on tevent, messages_dgm, messages_ctdb, CTDB support, server-id DB, loadparm paths, background jobs, debug/dmalloc/talloc message registration, and NTSTATUS/errno mapping. It underpins dbwrap watch, global locks, id-cache invalidation, debug commands, and many daemon coordination paths.

Risks/test signals: waiter array mutation during dispatch, nested event context reposting, fd ownership, fork reinitialization, and cluster/local routing are high-risk areas. Tests include `test_messaging_read.c`, `test_messaging_fd_passing.c`, `test_messaging_send_all.c`, CTDB messaging tests, and indirect dbwrap/g_lock watcher tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb.c -->
# sources/user-network-fs/samba/source3/lib/messages_ctdb.c

Purpose: provides the source3 messaging transport bridge to CTDB for clustered Samba nodes.

Important APIs/types/functions: `messaging_ctdb_init()`, `messaging_ctdb_destroy()`, `messaging_ctdb_send()`, `messaging_ctdb_register_tevent_context()`, `messaging_ctdb_fde_active()`, and `messaging_ctdb_connection()`. Internal `struct messaging_ctdb_context` holds CTDB connection and callback state; per-event-context FDE wrappers attach read handlers.

Control flow: init opens a CTDB daemon connection for a unique messaging id and installs a read callback. Send routes an iovec to a destination VNN/server id through CTDB. Registering an event context creates an object that enables CTDB readability callbacks in that tevent loop; destruction unregisters it.

State/persistence behavior: `global_ctdb_context` is process-global and represents the active CTDB transport. No durable state is created here, but it depends on CTDB daemon socket state and service id registration.

Dependencies/integration: used from `messages.c` when clustering is enabled. Depends on `ctdbd_conn`, CTDB SRVID constants, cluster support helpers, server IDs, and tevent fd handling.

Risks/test signals: global transport lifetime, multi-event-context registration, and failure to reconnect/destroy cleanly can break cluster messaging. CTDB torture/selftest coverage and clustered messaging send/read tests are key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb.h -->
# sources/user-network-fs/samba/source3/lib/messages_ctdb.h

Purpose: declares the CTDB-backed messaging transport API used by source3 messaging.

Important APIs/types/functions: opaque `struct messaging_ctdb_fde`; init/destroy/send functions; event-context registration; active-state check; and accessor for the CTDB connection.

Control flow: callers initialize the CTDB transport once, register event contexts that need reads, send cluster messages, and destroy the transport during shutdown.

State/persistence behavior: exposes process-global CTDB connection management; returned FDE handles are owned by talloc contexts.

Dependencies/integration: included by `messages.c`, CTDB reference helpers, and tests. It relies on iovec, tevent, and CTDB connection types.

Risks/test signals: API misuse when clustering is disabled should be handled by callers. Compile coverage under clustered and non-clustered builds plus CTDB messaging tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.c -->
# sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.c

Purpose: implements reference-counted CTDB messaging initialization so multiple source3 messaging users in a process can share one CTDB transport and tear it down only when the last reference is freed.

Important APIs/types/functions: `messaging_ctdb_ref()` creates a `struct msg_ctdb_ref`, initializes CTDB transport when the global ref list is empty or PID changed, registers a tevent-context FDE, and installs `msg_ctdb_ref_destructor()`. `msg_ctdb_ref_recv()` forwards CTDB messages to the caller callback.

Control flow: on first reference or after fork/PID change, existing refs are cleared and `messaging_ctdb_init()` is called. Each ref stores callback/private data and FDE registration. Incoming CTDB data goes through the ref receive trampoline. Destructor removes the ref from the global list and calls `messaging_ctdb_destroy()` when no refs remain.

State/persistence behavior: static `ctdb_pid` records the process that owns the current transport, and static `refs` holds live references. No durable state is stored, but CTDB daemon registrations exist while refs are live.

Dependencies/integration: depends on `messages_ctdb.h`, `messages_ctdb_ref.h`, DLIST utilities, talloc, tevent, and debug. It is used by `messages.c` during messaging init/reinit when clustering is enabled.

Risks/test signals: fork handling is critical; stale refs from a parent process must not keep child transports attached to the wrong PID. Tests should cover multiple refs, FDE teardown, last-ref destroy, PID changes, init failure propagation, and clustered message receive callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.c -->
