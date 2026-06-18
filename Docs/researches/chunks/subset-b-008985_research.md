# sources/storage-engines/wiredtiger/src/include/wiredtiger.h.in lines 5047-10412

Chunk: `subset-b-008985`

This chunk covers the second half of WiredTiger's public/generated API header template. It starts inside the `WT_FILE_SYSTEM` interface and then defines the file-handle, storage-source, page-log, key-provider, extension-entry, public constant, statistics-key, and verbose logging portions of `wiredtiger.h.in`. The file is an API contract rather than implementation code: the control flow is expressed as callback tables, stable numeric constants, and generated statistic identifiers that are consumed by WiredTiger core code, extensions, applications, and test tooling.

## Purpose

The chunk's main purpose is to publish ABI-facing contracts for storage and observability features:

- Custom file systems and file handles, including directory listing, object existence, open/remove/rename/size/free-space, mmap-style access, pread/pwrite, durable sync, truncate, file extension, and advisory calls.
- Non-public storage-source and page-log interfaces used by tiered/disaggregated storage, shared object storage, page logging, block cache, and checkpoint materialization.
- Key-provider hooks for encrypted checkpoint key rotation and persistence acknowledgement.
- Extension entry points (`wiredtiger_extension_init` and optional `wiredtiger_extension_terminate`).
- Stable constants for incremental backup result types, live restore state, and transaction log record/operation types.
- A generated statistic reference exposing 1,436 statistic keys: 1,019 connection keys, 406 data-source keys, and 11 session keys.
- Verbose category and verbosity-level enums used by diagnostic logging configuration.

Because this is a generated/template header, many values are part of external contracts. Comments explicitly warn that log operation values, page-log flag values, and the generated statistics section must not be casually edited or renumbered.

## Important APIs, Types, and Constants

### `WT_FILE_SYSTEM` tail and `WT_FILE_HANDLE`

The chunk begins with the tail of `struct __wt_file_system`, so the structure definition and earlier methods are in the previous chunk. Visible methods include:

- `fs_directory_list` and internal `fs_directory_list_single`: allocate arrays of path strings for directory/prefix scans.
- `fs_directory_list_free`: releases the directory-list allocation.
- `fs_exist`: probes object existence.
- `fs_open_file`: opens a `WT_FILE_HANDLE` and requires the file-system implementation to allocate the handle and its `name`.
- `fs_remove` and `fs_rename`: optional for read-only file systems and accept durable flags.
- `fs_size` and `fs_free_space`: report object size and free bytes.
- `terminate`: optional cleanup callback after WiredTiger will no longer access the file system.

`struct __wt_file_handle` is the per-file vtable returned by `fs_open_file`. It stores its owning `WT_FILE_SYSTEM *file_system` and allocated `char *name`, then exposes callbacks for:

- lifecycle: `close`;
- access hints: `fh_advise` with `WT_FILE_HANDLE_WILLNEED` and `WT_FILE_HANDLE_DONTNEED`;
- allocation and truncation: `fh_extend`, `fh_extend_nolock`, `fh_truncate`;
- interprocess locking: `fh_lock`;
- mapping: `fh_map`, `fh_map_discard`, `fh_map_preload`, `fh_unmap`;
- I/O and durability: `fh_read`, `fh_write`, `fh_size`, `fh_sync`, `fh_sync_nowait`.

Most methods may be `NULL` when unsupported, but core read/write/size/close behavior is foundational for storage engines. Thread-safety comments say WiredTiger may call most file-handle methods concurrently; extension implementers own synchronization. `fh_extend` and `fh_truncate` are documented as serialized per handle, while `fh_extend_nolock` is the opt-in concurrent extension hook.

### `WT_STORAGE_SOURCE`

The non-Doxygen `struct __wt_storage_source` is an application-provided storage-source interface registered through `WT_CONNECTION::add_storage_source`. It models object-store buckets as customized `WT_FILE_SYSTEM` instances:

- `ss_add_reference` and `terminate` implement reference management. `WT_CONNECTION::get_storage_source` adds references, and `terminate` releases them.
- `ss_customize_file_system` binds a bucket name, auth token, and optional `cache_directory` config to a returned file system. Objects created through that file system are not visible until their handle closes and are immutable after creation.
- `ss_flush` copies a default-file-system file into an object name in shared storage.
- `ss_flush_finish` renames the source file into the local cache after a flush.

The storage-source contract is tightly coupled to tiered storage and object storage semantics. Local `WT_FILE_HANDLE::fh_sync` only syncs the local cached file and does not imply remote object transfer; remote transfer is handled by storage-source flush methods.

### Page Log and Disaggregated Storage

The chunk defines page-log constants, service interfaces, argument structs, and handle methods behind `#if !defined(DOXYGEN)`:

- `WT_PAGE_LOG_LSN_MAX` is `UINT64_MAX`, used as a maximum/latest LSN sentinel.
- `WT_DISAGG_START_LSN` is `1 << 32`, used by server step-up to avoid eviction of pages before a materialization point.
- `struct __wt_page_log` provides callbacks for reference management, checkpoint abandon/complete/query, testing-only last-LSN hooks, open-checkpoint query, per-table handle open, last-materialized LSN update, table trim, and termination.
- `struct __wt_page_log_handle` provides per-table page operations: `plh_put`, `plh_get`, `plh_get_page_ids`, `plh_discard`, `plh_close`, and block-cache helpers `plh_cache_put`, `plh_cache_has`, `plh_cache_del`, `plh_cache_available`.

Associated argument structs encode page-log state:

- `WT_PAGE_LOG_COMPLETE_CHECKPOINT_ARGS`: checkpoint id, checkpoint timestamp, checkpoint metadata, oldest timestamp, and output LSN.
- `WT_PAGE_LOG_GET_COMPLETE_CHECKPOINT_ARGS`: completed checkpoint LSN/id/timestamp/metadata.
- `WT_PAGE_LOG_PUT_ARGS`: backlink/base LSNs, backlink/base checkpoint ids, image size, stable flags, output LSN, and block-cache delta count.
- `WT_PAGE_LOG_GET_ARGS`: optional requested LSN, flags, returned backlink/base state, and delta count.
- `WT_PAGE_LOG_DISCARD_ARGS`: backlink/base state plus currently-unused flags and output LSN.

Page-log flags `WT_PAGE_LOG_COMPRESSED`, `WT_PAGE_LOG_DELTA`, `WT_PAGE_LOG_ENCRYPTED`, and `WT_PAGE_LOG_COLD` are documented as externally consumed and potentially persisted, so their numeric values must remain stable. `WT_BTREE_STORAGE_TIER` currently distinguishes no tier from cold tier, and the page-log flag range reserves values for storage tiers.

### Encryption Key Provider

`struct __wt_crypt_keys` stores encrypted key material plus a timestamp and a union result field: checkpoint LSN on success or an error code on failure. `struct __wt_key_provider` exposes:

- `load_key`: load the current persisted key during checkpoint load.
- `get_key`: fetch the latest key for checkpoint writes. WiredTiger may call once with an empty `keys` item to learn required size, then allocate and call again for data. Implementations must keep the key stable across those calls within one checkpoint.
- `on_key_update`: notify whether a key has been persisted, with LSN or error in `WT_CRYPT_KEYS::r`.
- `set_key`: hand WiredTiger a future checkpoint key associated with a timestamp. The timestamp must exceed both the global stable timestamp and any previous `set_key` timestamp. The call is explicitly non-transactional.
- `terminate`: cleanup when the provider is no longer accessed.

This interface creates a persistence boundary between checkpoint state, encrypted key blobs, stable timestamp rules, and external key-management modules.

### Extension Entrypoints and Public Constants

Extensions must export `wiredtiger_extension_init(WT_CONNECTION *, WT_CONFIG_ARG *)`, called by `WT_CONNECTION::load_extension`. They may export `wiredtiger_extension_terminate(WT_CONNECTION *)`, called during connection close.

The chunk also defines stable macro constants for:

- Incremental backup item types: invalid, whole file, file range.
- Live restore states: init, in progress, complete.
- Transaction log record and operation types: checkpoint, commit, file sync, message, system records; column/row put/remove/truncate/modify operations; checkpoint start; previous LSN; diagnostic timestamp operation; backup id. The comments say these values are written into the log and must never change except by appending new values.

### Statistics Reference

The statistics block is generated by `dist/stat.py` and marked `DO NOT EDIT`. It defines integer keys for `statistics:` cursors:

- Connection statistics start at `WT_STAT_CONN_AUTOCOMMIT_READONLY_RETRY = 1000` and run through `WT_STAT_CONN_TXN_UPDATE_CONFLICT = 2018`.
- Data-source statistics start at `WT_STAT_DSRC_AUTOCOMMIT_READONLY_RETRY = 2000` and run through `WT_STAT_DSRC_TXN_UPDATE_CONFLICT = 2405`.
- Session statistics start at `WT_STAT_SESSION_BYTES_READ = 4000` and run through `WT_STAT_SESSION_CACHE_TIME_MANDATORY = 4010`.

Major metric families include autocommit, background compaction, backup and incremental backup, block cache, disaggregated block manager, block manager, btree shape, cache and eviction, capacity throttling, checkpoint and checkpoint cleanup, compression, connection resources, cursor operations and cursor bounds, data-handle sweep, disaggregated role/checkpoint pickup, layered table manager, live restore, load control, locks, log manager, performance histograms, prefetch, reconciliation/page deltas/time windows, session schema operations, thread state/yield waits, tiered storage, and transactions/rollback-to-stable/timestamps.

The statistic macros are not behavior themselves; they are numeric API keys. Their correctness depends on exact alignment with generated metadata and runtime statistic tables. Duplicate-looking concepts intentionally appear at both connection and data-source scopes with different key ranges.

### Verbose Logging

`WT_VERBOSE_CATEGORY` enumerates diagnostic categories such as API, backup, block manager, checkpoint, disaggregated storage, eviction, extension, file operations, history store, layered, live restore, log, metadata, page delta, prefetch, reconcile, recovery, rollback-to-stable, tiered, timestamp, transaction, verify, and write. The enum is bracketed by `VERBOSE ENUM START/STOP`, suggesting generation or tooling rewrites the category list.

`WT_VERBOSE_LEVEL` is severity/verbosity ordered from `WT_VERBOSE_ERROR = -3` through warning, notice, info, and `WT_VERBOSE_DEBUG_1` to `WT_VERBOSE_DEBUG_5`.

## Control Flow and Call Sequences

This header does not execute code directly, but it defines expected call sequences:

- File-system lifecycle: WiredTiger gets a `WT_FILE_SYSTEM`, calls directory/object/open methods, receives allocated `WT_FILE_HANDLE` objects, performs file-handle I/O/mapping/sync/truncate operations, then calls handle `close` and eventually file-system `terminate`.
- Storage-source lifecycle: the connection registers or retrieves a storage source, references it, customizes bucket-backed file systems, writes local immutable objects, flushes them to shared storage, optionally finishes by moving the local source into cache, then terminates references.
- Page-log lifecycle: the connection registers/retrieves a page log, opens per-table handles, writes page images or deltas with checkpoint/page ids, reads by checkpoint and optional LSN, lists live page ids, discards entries, trims tables, completes or abandons checkpoints, and closes handles/services.
- Key-provider lifecycle: checkpoint load calls `load_key`, checkpoint write calls `get_key` possibly twice for size/data, persistence completion calls `on_key_update`, administrative key rotation calls `set_key`, and connection shutdown calls `terminate`.
- Statistics access: applications open statistics cursors and use these macros as keys. Runtime values are populated elsewhere; this header only binds names to numeric IDs.
- Verbose logging: applications configure categories and levels by enum values; logging sites elsewhere classify events using the same enum.

## State and Persistence Behavior

Several definitions in this chunk describe durable or externally visible state:

- File-system durability flows through `WT_FS_DURABLE` flags on remove/rename and through `fh_sync`/`fh_sync_nowait` on file handles. A custom file system that weakens these semantics can break checkpoint, log, and metadata durability.
- Storage-source objects become visible only after the creating handle closes and are immutable once created. Remote object transfer is separate from local file sync and is represented by `ss_flush`/`ss_flush_finish`.
- Page-log LSNs, checkpoint ids, checkpoint timestamps, backlink/base LSNs, and page flags encode disaggregated storage history. The header explicitly treats page-log flags as stable persisted/external values.
- `WT_DISAGG_START_LSN` is a cross-component server coordination sentinel for step-up/materialization behavior.
- Encrypted checkpoint keys carry timestamps and persisted LSN/error results. `set_key` is non-transactional and constrained by stable timestamp ordering.
- Log record and operation macro values are persisted in transaction logs and must not be renumbered.
- Statistic key values are public cursor keys. Renumbering breaks clients, tests, and tooling that refer to `WT_STAT_*` constants.

## Dependencies and Integration Points

The chunk depends on earlier declarations from the same header: `WT_CONNECTION`, `WT_SESSION`, `WT_CONFIG_ARG`, `WT_ITEM`, `WT_FILE_SYSTEM`, `WT_FILE_HANDLE`, `WT_STORAGE_SOURCE`, `WT_PAGE_LOG`, `WT_KEY_PROVIDER`, `WT_PAGE_LOG_HANDLE`, `WT_FS_OPEN_FILE_TYPE`, and `wt_off_t`.

Runtime integration points include:

- POSIX-like filesystem semantics: fadvise, mmap/madvise/munmap, pread/pwrite, sync, truncate, locking, durable rename/remove behavior.
- Extension loading via exported C symbols.
- Storage-source registration through connection APIs and object-store-backed file-system customization.
- Disaggregated storage/page-log consumers, checkpoint code, block cache, materialization frontier handling, layered tables, and server step-up behavior.
- Encryption/key-management modules that need checkpoint-aligned key persistence.
- Statistics cursors (`statistics:` URI family) and generated stats tooling (`dist/stat.py`).
- Verbose logging configuration and generated verbose category tooling.

## Risks and Edge Cases

- ABI and persisted-value drift: changing log operation values, page-log flags, statistic IDs, or enum ordering can break persistent data, external modules, or application binaries.
- Concurrency bugs in custom implementations: the header repeatedly states WiredTiger may call callbacks concurrently, while reentrancy is not expected for page-log interfaces. Implementers must guard shared state without assuming serialized entry.
- Memory ownership mismatches: `fs_directory_list`, `fs_open_file`, page-log `plh_get`, and key-provider `get_key` all carry allocation/ownership rules. Leaks, double frees, or returning stack-backed buffers would fail under normal core cleanup.
- Durability semantic gaps: `fh_sync_nowait`, `fh_sync`, durable remove/rename flags, and storage-source flush semantics are separate. Treating local cache sync as remote object persistence is explicitly wrong.
- Immutable object semantics: storage-source files opened with create should not be visible before close and cannot later be opened for mutation. Violating that contract can expose partial objects or corrupt tiered-storage assumptions.
- Page-log result ambiguity: `plh_get` says zero results must be associated with an error code. Returning success with no result would make callers unable to distinguish not-found, corruption, and empty data.
- Key rotation races: `get_key` must be stable between size and data fetch within a checkpoint; `set_key` must obey timestamp ordering and is non-transactional, so caller-side transaction rollback will not undo it.
- Generated-section edits: the stats block is built by tooling. Manual edits are likely to be overwritten or leave runtime tables out of sync.

## Test Signals

Useful test signals for code touching this chunk or its generators:

- API/header generation tests should verify `dist/stat.py` output matches the generated statistics block and that no manual changes are needed.
- ABI/persistence guards should detect renumbering of `WT_LOGREC_*`, `WT_LOGOP_*`, `WT_PAGE_LOG_*` flags, `WT_STAT_*` IDs, and verbose categories where external configuration depends on ordering.
- Custom file-system tests should exercise directory-list allocation/free, read/write/size, durable sync, truncate/extend, read-only `NULL` methods, exclusive open error paths, and concurrent calls.
- Storage-source tests should verify object invisibility before close, immutability after creation, bucket/prefix naming edge cases, cache-directory configuration, flush/finish ordering, and reference-count termination.
- Page-log/disaggregated tests should cover put/get/discard/checkpoint-complete/checkpoint-query/table-trim, live page-id listing, cache helper behavior, zero-result error handling, compressed/delta/encrypted/cold flags, and materialization-frontier LSN behavior.
- Key-provider tests should cover two-pass `get_key`, unchanged-key size zero, within-checkpoint key stability, `on_key_update` success/error reporting, timestamp validation against stable timestamp and previous keys, and non-transactional `set_key` behavior.
- Statistics cursor tests should confirm representative connection, data-source, and session statistics keys resolve to expected names/values, especially for newer disaggregated, layered, live-restore, page-delta, and rollback-to-stable metrics.
- Verbose tests should confirm configured categories and levels map to the intended runtime output and that `WT_VERBOSE_ERROR` remains the most critical level.

## Cross-Chunk Notes

This chunk begins mid-definition of `WT_FILE_SYSTEM`; earlier methods and type declarations are outside the assigned range. It also contains callback declarations whose implementations live in WiredTiger core, extension modules, storage-source implementations, page-log providers, and generated stats/verbose tooling. The final per-file research report should merge this with earlier chunks to describe the whole `wiredtiger.h.in` API surface coherently.
