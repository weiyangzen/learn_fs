<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wiredtiger_ext.h -->
# sources/storage-engines/wiredtiger/src/include/wiredtiger_ext.h

## Purpose
Defines the public extension-facing WiredTiger API table. Extensions include this header, obtain `WT_EXTENSION_API` through `WT_CONNECTION::get_extension_api`, and call through function pointers rather than linking directly against WiredTiger internals.

## Important APIs, Types, and Functions
`WT_EXTENSION_SPINLOCK` is an opaque wrapper that lets extensions use WiredTiger spin locks. `struct __wt_extension_api` is append-only for ABI compatibility and begins with a private `WT_CONNECTION *conn` field. Its methods cover diagnostics (`err_printf`, `msg_printf`, `strerror`, `map_windows_error`), scratch allocation, collator lookup and comparison, configuration lookup and parser construction, file-system discovery, metadata insert/search/update/remove, deprecated vararg struct packing, streaming pack/unpack operations, version lookup, and extension spin-lock lifecycle/lock/unlock.

## Control Flow
This header contains no executable control flow, but it defines the dispatch table used by extension code. A caller includes the header, asks the connection for an API table, then calls function pointers with the `WT_EXTENSION_API *` and optional `WT_SESSION *` context. The append-only layout is the main control constraint: new functionality must be added at the tail to preserve binary compatibility.

## State and Persistence Behavior
The table can mutate WiredTiger persistent state through the metadata methods and can expose the active `WT_FILE_SYSTEM`. Scratch allocation is short-lived and session-scoped in practice. Pack/unpack routines operate on caller-provided buffers and parser handles. The spinlock object hides WiredTiger lock storage behind an extension-owned placeholder.

## Dependencies and Integration Points
Includes `wiredtiger.h` and is itself included by `wt_internal.h`, so public extension names are visible before internal headers. It integrates with extension modules such as compressors, collators, encryptors, data sources, and storage sources, and with examples referenced by Doxygen snippets. The API is also the boundary that lets dynamically loaded modules avoid direct linkage to core WiredTiger symbols.

## Risks and Edge Cases
The ABI is sensitive to field reordering or insertion before the end of `WT_EXTENSION_API`. Several methods accept varargs or opaque config strings, so caller misuse can cause hard-to-diagnose extension failures. Metadata access from extensions must obey normal WiredTiger locking and lifecycle expectations. `file_system_get` may return `WT_NOTFOUND` during early extension initialization before the file system is established.

## Test Signals
Coverage usually comes from extension example builds and extension-specific tests for compressors/collators/encryptors/storage sources. ABI regressions are signaled by compilation or dynamic-load failures in extension modules and by tests that exercise metadata/config/packing methods through the API table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wiredtiger_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wt_internal.h -->
# sources/storage-engines/wiredtiger/src/include/wt_internal.h

## Purpose
Acts as WiredTiger's central internal include umbrella. It establishes C linkage, imports public/config/platform headers, declares generated internal typedefs, and then includes the internal subsystem headers and inline headers in dependency order.

## Important APIs, Types, and Functions
The main exported content is type visibility rather than functions. The generated `dist/s_typedef` block forward-declares and typedefs core structures for block management, btrees, cache, checkpoint, connection/session, cursors, eviction, logging, metadata, reconciliation, transactions, tiered storage, verification, and live restore. For this subset, it introduces `WT_LIVE_RESTORE_FH_META`, `WTI_LIVE_RESTORE_FILE_HANDLE`, `WTI_LIVE_RESTORE_FS`, `WTI_LIVE_RESTORE_FS_LAYER`, `WTI_LIVE_RESTORE_SERVER`, and `WTI_LIVE_RESTORE_WORK_ITEM`, then includes `../live_restore/live_restore.h`.

## Control Flow
There is no runtime control flow. The include order is the control mechanism: platform headers and compiler abstractions come first, then foundational internal headers, subsystem headers, `extern.h` prototypes, build verification, and inline helpers whose comments document prerequisite headers. This ordering lets most `.c` files include one header and receive consistent declarations.

## State and Persistence Behavior
No persistent state is stored here. The header defines the type universe and macro/platform environment that all source files compile against. Including `live_restore.h` here makes live-restore metadata/state functions visible to block, metadata, connection, and cursor code that participate in persistence and startup.

## Dependencies and Integration Points
Depends on `wiredtiger_config.h`, `wiredtiger_ext.h`, OS headers, compiler-specific headers, POSIX/Windows shims, queue/mutex/stat/error/session/connection headers, and a broad set of subsystem headers. `live_restore.h` is integrated midway with other subsystem interfaces before metadata, OS, checkpoint, session, connection, and extern includes.

## Risks and Edge Cases
Because this file is transitively included almost everywhere, any added include or typedef can increase rebuild cost, create dependency cycles, or affect platform portability. The generated typedef block must stay in sync with source declarations. Preprocessor platform choices such as `_WIN32`, Linux, and Apple guards determine what APIs are available across the rest of the codebase.

## Test Signals
The strongest signal is a full WiredTiger build across supported platforms. Live-restore-specific compile signals include references from `block_open.c`, `meta_ckpt.c`, `meta_table.c`, `meta_turtle.c`, `conn_api.c`, and `conn_open.c` resolving through this header. Generated-header drift is caught by WiredTiger distribution/build verification tooling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/wt_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore.h -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore.h

## Purpose
Declares the live-restore public-internal interface used by the rest of WiredTiger. It exposes persisted file-handle metadata and prototypes for live-restore file-system setup, server lifecycle, turtle-file interception, metadata conversion, validation, and stats initialization.

## Important APIs, Types, and Functions
`WT_LIVE_RESTORE_STATE_STRING_MAX` bounds persisted state parsing. `WT_LIVE_RESTORE_FH_META` stores the `live_restore=(bitmap=...,nbits=...)` metadata fields plus `allocsize`; `nbits == -1` means migration for that file is complete. Prototypes include `__wt_os_live_restore_fs`, `__wt_live_restore_server_create/destroy`, `__wt_live_restore_metadata_to_fh`, `__wt_live_restore_fh_to_metadata`, `__wt_live_restore_clean_metadata_string`, `__wt_live_restore_get_state_string`, turtle wrappers, non-live-restore validation, and `__wt_live_restore_init_stats`. Under `HAVE_UNITTEST`, it exposes wrappers for bitmap encoding/decoding, bit filling, read-end computation, and hole filling.

## Control Flow
Connection setup calls `__wt_os_live_restore_fs` when `live_restore.enabled=true`, then starts the server through `__wt_live_restore_server_create`. Block open reconstructs file-handle bitmaps through `__wt_live_restore_metadata_to_fh`; checkpoints append file metadata through `__wt_live_restore_fh_to_metadata`; metadata/turtle operations use the turtle wrappers to preserve lock ordering. Shutdown calls `__wt_live_restore_server_destroy`.

## State and Persistence Behavior
The header documents the durable per-file metadata shape: a hex bitmap string, a bit count, and allocation size. State strings are persisted through turtle metadata, while file-hole state is persisted in checkpoint metadata. Backup cleanup can rewrite `nbits=-1` to `nbits=0` so a future restore source does not falsely indicate already-migrated files.

## Dependencies and Integration Points
Included by `wt_internal.h` after live-restore typedefs have been declared. The prototypes are consumed by block manager file open, checkpoint metadata code, backup cursor cleanup, metadata/turtle code, connection open/reconfigure/close paths, utility configuration, and live-restore tests.

## Risks and Edge Cases
The generated prototype section must match the implementations. The `nbits` sentinel values are subtle: `0` means not started, positive values mean a persisted bitmap exists, and `-1` means migration completed. Unit-test-only functions expose static internals and must remain guarded to avoid changing production ABI.

## Test Signals
Catch2 unit tests under `test/catch2/live_restore/unit` directly exercise the unit-test wrappers. API tests under `test/catch2/live_restore/api`, Python suite tests `test_live_restore01.py` through `test_live_restore08.py`, and `test/cppsuite/tests/test_live_restore.cpp` exercise the declared integration points.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_fs.c -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_fs.c

## Purpose
Implements the live-restore `WT_FILE_SYSTEM` and `WT_FILE_HANDLE` wrappers. The wrapper presents the destination home as the active database while lazily reading missing data from a backup source and tracking migrated data-file blocks with bitmaps.

## Important APIs, Types, and Functions
`__wt_os_live_restore_fs` constructs the layered file system. File-system methods include directory listing, existence checks, open, remove, rename, size, and terminate. File-handle methods include read, write, size, sync, truncate, lock, and close. Core helpers include `__live_restore_fs_find_layer`, stop-file creation/checking, backing-path construction, bitmap encode/decode/fill, `__live_restore_can_service_read`, `__live_restore_fill_hole`, `__wti_live_restore_fs_restore_file`, `__wt_live_restore_metadata_to_fh`, `__wt_live_restore_fh_to_metadata`, `__wt_live_restore_clean_metadata_string`, and `__wti_live_restore_cleanup_stop_files`.

## Control Flow
Path translation asserts that incoming paths start with the destination home and maps them to either destination or source. Existence and directory listing are destination-first, hide `.stop` and `.lr_tmp` files, and suppress source files hidden by destination stop files. Opening a data file can open the source, create a same-sized destination placeholder atomically, then open the destination; opening regular/log files copies the whole source file through a temporary destination file and rename. Reads consult the bitmap under a read lock: fully migrated ranges read from destination, holes read from source. Writes go to destination, then set bitmap bits for the written allocation-size range. Background migration repeatedly finds the first clear bitmap bit, reads source chunks, writes destination chunks, and closes the source handle when complete. Remove and rename create stop files so later source entries with the same name remain hidden.

## State and Persistence Behavior
Each live-restore data-file handle owns a bitmap sized to the original source file in allocation-size units. `1` bits mark destination-resident data, clear bits mark holes still served from source. Checkpoint metadata stores `live_restore=(bitmap=<hex>,nbits=<n>)`; `nbits=0` means migration has not started and reconstructs an empty bitmap from destination size, and `nbits=-1` means the file is complete and source can be closed. Temporary files with `.lr_tmp` make atomic copy/create operations crash-tolerant. Stop files with `.stop` persist user delete/rename decisions until cleanup. Cleanup removes stop files after background migration and checkpoints have durably removed live-restore metadata.

## Dependencies and Integration Points
Uses WiredTiger file-system abstractions, POSIX creation for nested directories on Linux/Apple, block/file-handle callbacks, bitstring helpers, scratch buffers, verbose/stat APIs, checkpoint metadata hooks, turtle/state helpers, and connection flags. It is invoked from connection setup, block open, checkpoint metadata serialization, backup cleanup, and the background server. Stats include bytes copied, source-read count, and source-read latency histogram.

## Risks and Edge Cases
Bitmap correctness is central: reads assert the range pattern is `1*0*`, writes/truncates require allocation-size alignment, and crashes after truncation but before metadata persistence are guarded by reopen assertions. Source and destination path handling assumes destination-prefix paths. Rename is intentionally restricted to files already present in destination because partially migrated data files cannot be renamed safely at this layer. Regular/log files are copied on open rather than lazily migrated. The implementation is currently POSIX-only and readonly mode is rejected. Directory listing holds the state lock across both layers to avoid state-change races. Backup cleanup asserts that non-empty bitmaps are not backed up.

## Test Signals
Catch2 API tests cover file existence, open-file behavior, file-handle size/read/write/lock/close/sync/truncate, file-system size, remove/rename, and directory listing. Unit tests cover bitmap encode/decode, bit-range filling, read-end computation, and hole filling through `HAVE_UNITTEST` wrappers. Python suite and cppsuite live-restore tests exercise end-to-end restore, restart, cleanup, stats/progress, backup interactions, and user-visible file-system behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_private.h -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_private.h

## Purpose
Defines private live-restore constants, lock macros, state enums, layered file-system structures, file-handle state, and background-server queue structures used only by the live-restore implementation.

## Important APIs, Types, and Functions
Constants include `.stop` and `.lr_tmp` suffixes, offset/bit conversion macros, `WTI_BITMAP_END`, `WTI_DEST_COMPLETE`, and the cleanup timing-stress delay. `WTI_LIVE_RESTORE_FILE_HANDLE` wraps a `WT_FILE_HANDLE`, destination/source handles, back pointer, allocation size, file type, per-file `WT_RWLOCK`, bitmap bit count, and bitmap memory. Lock macros encapsulate file-handle write locking, server queue locking, and state locking. `WTI_LIVE_RESTORE_FS_LAYER_TYPE`, `WTI_LIVE_RESTORE_FS_LAYER`, `WTI_LIVE_RESTORE_STATE`, `WTI_LIVE_RESTORE_FS`, `WTI_LIVE_RESTORE_WORK_ITEM`, and `WTI_LIVE_RESTORE_SERVER` model layers, state machine, file-system config, migration queue entries, and worker-thread server state.

## Control Flow
This header has no runtime code, but the macros determine the lock discipline used throughout live restore. The state enum defines the legal sequence `NONE -> BACKGROUND_MIGRATION -> CLEAN_UP -> COMPLETE`. The server queue is a `TAILQ` of URIs consumed by worker threads. `WTI_DEST_COMPLETE` treats a closed or absent source handle as the signal that a file no longer needs migration work.

## State and Persistence Behavior
The in-memory state mirrors persisted turtle metadata and per-file checkpoint metadata. The file-system stores source/destination homes, thread/read-size configuration, current live-restore state, and state lock. The file handle stores migration progress until serialized by checkpoint; once migration completes, the source handle is closed and the bitmap freed. Server counters back progress stats and cleanup decisions.

## Dependencies and Integration Points
Requires typedefs from `wt_internal.h` and is included by `live_restore_fs.c`, `live_restore_server.c`, and `live_restore_state.c`. Prototypes expose private cross-file calls such as state get/set/init/validation, migration-complete checks, stop-file cleanup, and restoring a single file.

## Risks and Edge Cases
The lock macros rely on callers passing valid session/file-system/server pointers; incorrect lock ordering could deadlock with turtle or metadata locks. Offset macros reference `lr_fh->allocsize` and assume correct local variable naming. The comments explicitly allow rare lock exceptions only where implementation code documents them. State transitions must remain ordered because cleanup and non-live-restore validation rely on that monotonic progression.

## Test Signals
Compile-time signals catch structure/prototype drift across the three implementation files. Runtime signals come from live-restore API and unit tests, especially tests that manipulate bitmap state, queue cleanup, state transitions, stop-file behavior, and cleanup timing-stress paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_server.c -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_server.c

## Purpose
Implements the background migration server that drains live-restore work items, opens data handles safely through cursors, copies holes from source to destination, and performs post-migration cleanup/checkpointing.

## Important APIs, Types, and Functions
Public entry points are `__wt_live_restore_server_create` and `__wt_live_restore_server_destroy`. Internal helpers include `__live_restore_init_work_queue`, `__insert_queue_item`, `__live_restore_worker_run`, `__live_restore_worker_stop`, `__live_restore_clean_up`, `__live_restore_work_queue_drain`, and `__live_restore_free_work_item`. The worker calls `__wti_live_restore_fs_restore_file` on the block manager's live-restore file handle.

## Control Flow
Server creation returns immediately if live restore is disabled. If migration is already complete, it opens an internal session and runs cleanup without starting workers. Otherwise, if `threads_max` is nonzero, it allocates the server, initializes the queue lock and work queue, sets `threads_working`, starts progress timers, and creates a fixed-size thread group. The queue is built by scanning metadata for `file:` URIs and optionally adding `file:WiredTiger.wt` unless partial-backup restore will rebuild metadata. Worker runs wait for `WT_CONN_READY`, pop one URI, report periodic progress, open a cursor to prevent exclusive schema access, restore the underlying file, and free the work item. `ENOENT` drops the item; `EBUSY` requeues it and may sleep if workers exceed remaining items. When the last worker stops and the queue is empty, cleanup runs.

## State and Persistence Behavior
Queue counters update `live_restore_work_remaining`, `work_count`, and `work_items_remaining`. Cleanup forces a checkpoint before leaving background migration so empty bitmaps are durable, advances the persisted live-restore state to `CLEAN_UP`, removes stop files, optionally delays for timing-stress sweep cleanup, forces another checkpoint to remove live-restore metadata, then persists `COMPLETE`. Destroy marks `shutting_down`, destroys the thread group if present, drains queued work, and frees server memory; unfinished work is recoverable because file bitmap/state metadata is persisted by checkpoints.

## Dependencies and Integration Points
Uses WiredTiger thread groups, metadata cursors, internal sessions, checkpoints, btree/block-manager internals, live-restore FS restore routines, stats, verbose progress logging, connection flags, and private state helpers. Connection open invokes create; connection close/error paths invoke destroy.

## Risks and Edge Cases
Cleanup is triggered from worker-stop while holding the queue lock, so it must not require queue operations that would self-deadlock. Workers must wait for `WT_CONN_READY` to avoid racing connection flag setup and checkpoint side effects. `EBUSY` requeue behavior protects concurrent schema/bulk operations but can delay completion. The direct block-manager access is marked as a FIXME and is fragile if the block-manager structure changes or multi-handle btrees become relevant. If `threads_max=0`, no background migration occurs until a later run with workers or application reads/writes force data movement.

## Test Signals
End-to-end live-restore tests should verify work queue population, thread startup/shutdown, EBUSY retry paths, restart during migration, cleanup checkpoints, stop-file cleanup, and final `WT_LIVE_RESTORE_COMPLETE` stats. Progress stats and logs provide operational signals: remaining work count, source reads, bytes copied, and periodic progress messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_state.c -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_state.c

## Purpose
Manages live-restore state discovery, validation, persistence, turtle-file lock ordering, external stats reporting, and guardrails for opening a database with or without live restore enabled.

## Important APIs, Types, and Functions
Public/internal entry points include `__wti_live_restore_migration_complete`, `__wt_live_restore_migration_in_progress`, `__wti_live_restore_init_state`, `__wti_live_restore_set_state`, `__wt_live_restore_get_state_string`, `__wt_live_restore_turtle_update`, `__wt_live_restore_turtle_rewrite`, `__wt_live_restore_turtle_read`, `__wti_live_restore_get_state`, `__wti_live_restore_validate_directories`, `__wt_live_restore_validate_non_lr_system`, and `__wt_live_restore_init_stats`. Private helpers convert state strings and read persisted state from turtle metadata.

## Control Flow
Startup validation lists source and destination directories, rejects invalid source/destination combinations, reads any persisted live-restore state from the destination turtle file, then initializes in-memory state from that value or defaults to `BACKGROUND_MIGRATION` without immediately creating turtle metadata. State changes validate monotonic transitions and call `__wt_live_restore_turtle_rewrite` so the live-restore metadata entry is persisted. Turtle read/update/rewrite wrappers acquire the live-restore state lock before the turtle lock. Non-live-restore startup reads the turtle state and rejects opening a database stuck in background migration or cleanup.

## State and Persistence Behavior
State is persisted as a string in turtle metadata under `WT_METADATA_LIVE_RESTORE`; `WT_LIVE_RESTORE_STATE_STRING_MAX` bounds parsing. The internal state sequence is `NONE`, `BACKGROUND_MIGRATION`, `CLEAN_UP`, and `COMPLETE`, while application stats collapse this to init, in-progress, or complete. A missing turtle state means no prior live restore state exists; live-restore startup treats that as a fresh background migration, but destination validation rejects existing WiredTiger files to avoid corrupting an initialized directory.

## Dependencies and Integration Points
Uses metadata/turtle APIs, filesystem directory listing, connection flags, stats, stop-file suffix definitions, backup-file naming, and private live-restore structures. It is called from live-restore FS initialization, server cleanup, metadata/turtle wrappers in `meta_table.c` and `meta_turtle.c`, connection open validation, and stat initialization after the stat server starts.

## Risks and Edge Cases
There is a narrow early-crash window where live restore has in-memory state but no turtle state; restart will reject destination WiredTiger files and require user cleanup. Source validation requires a backup file and rejects source stop files so a destination directory is not accidentally used as a source. Complete-state validation rejects lingering stop files. The state lock must always be acquired before turtle lock to avoid deadlocks. String parsing is intentionally fixed-width and asserts the max length constant.

## Test Signals
Python and cppsuite live-restore tests should cover fresh startup, restart during background migration, restart during cleanup, complete-state reopening, non-live-restore open rejection while in progress, invalid source/destination directories, and stats values. Unit/API tests can also observe turtle wrapper behavior indirectly through persisted state and cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_state.c -->
