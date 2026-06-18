# subset-b-008757 Research

Grouped research report for the SQLite wasm OPFS, worker, virtual table, C bootstrap, and test utility files in subset B. Each source file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-sahpool.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-sahpool.c-pp.js

## Purpose
This file installs the optional `opfs-sahpool` sqlite3 VFS for non-Node wasm builds. It is an OPFS-backed VFS that avoids the ordinary `opfs` VFS subworker and SharedArrayBuffer requirement by pre-opening a fixed pool of OPFS files and holding a synchronous `FileSystemSyncAccessHandle` for each slot. SQLite sees a synchronous `sqlite3_vfs`; the browser sees opaque OPFS files under a private metadata directory. It is intentionally not a multi-tab concurrency solution: if another page already holds the same sync handles, installation fails or unpause fails.

## Important APIs, Types, and Functions
The bootstrap initializer adds `sqlite3.installOpfsSAHPoolVfs(options)`, which returns a cached Promise per VFS name. Options include `name`, `directory`, `initialCapacity`, `clearOnInit`, `verbosity`, and `forceReinitIfPreviouslyFailed`. Successful installation resolves to an `OpfsSAHPoolUtil` instance exposing `addCapacity()`, `reduceCapacity()`, `reserveMinimumCapacity()`, `getCapacity()`, `getFileCount()`, `getFileNames()`, `exportFile()`, `importDb()`, `wipeFiles()`, `unlink()`, `removeVfs()`, `pauseVfs()`, `unpauseVfs()`, and `isPaused()`. When `sqlite3.oo1` exists, it also exposes `OpfsSAHPoolDb`, an OO1 `DB` subclass forcing the pool VFS.

The internal `OpfsSAHPool` class owns VFS registration, OPFS directory handles, sync access handles, SQLite-file-to-pool mappings, filename-to-handle mappings, and the metadata header buffer. `createOpfsVfs()` creates a `sqlite3_vfs`, inherits default `xRandomness`/`xSleep` when available, installs fallback methods otherwise, and binds JS VFS callbacks via `sqlite3.vfs.installVfs()`. `ioMethods` implements the `sqlite3_io_methods` surface: `xRead`, `xWrite`, `xTruncate`, `xSync`, `xFileSize`, lock/unlock bookkeeping, `xClose`, and simple device/access/file-control behavior. `vfsMethods` implements `xOpen`, `xDelete`, `xAccess`, pathname/time/error callbacks, and pathname copying.

## Control Flow
On initialization, `installOpfsSAHPoolVfs()` validates required OPFS APIs, runs `apiVersionCheck()` to reject older async-close sync handles, constructs `OpfsSAHPool`, waits for `reset()`, and on success returns `OpfsSAHPoolUtil`. `reset()` walks/creates the configured OPFS directory and `.opaque` subdirectory, releases old handles, and calls `acquireAccessHandles()`. Acquisition enumerates opaque files, obtains sync handles, clears them when requested, or reconstructs filename associations from their stored headers.

SQLite opens flow through `xOpen()`: normalize the requested name to an absolute URL pathname, find an existing SAH, or allocate `nextAvailableSAH()` if `SQLITE_OPEN_CREATE` and capacity permits. The pool writes a metadata association, maps the `sqlite3_file*` to `{path, flags, sah}`, assigns `opfsIoMethods` to the C struct, and returns output flags. Later I/O callbacks use only the `sqlite3_file*` pointer to recover the pool and file object. `xClose()` flushes, removes pointer mappings, and honors `SQLITE_OPEN_DELETEONCLOSE`.

## State and Persistence Behavior
Each opaque OPFS file has a 4096-byte metadata header followed by SQLite file bytes. The header stores up to 512 path bytes, a flags word, and an 8-byte digest. Persistent file types are main DB, main journal, super-journal, and WAL; delete-on-close or non-persistent types are removed or disassociated during startup. `setAssociatedPath()` writes path, flags, digest, and flushes. `getAssociatedPath()` validates flags and digest, truncates unused entries to the data offset, and disassociates entries with invalid metadata. A digest compatibility flag reuses `SQLITE_OPEN_MEMORY` to distinguish legacy all-zero digest behavior from the fixed v2 hash introduced after issue 97.

Pool capacity is persistent because each capacity slot is a real OPFS file. `addCapacity()` creates opaque files and sync handles; `reduceCapacity()` closes and deletes only currently unused handles. `pauseVfs()` unregisters the VFS and releases handles without deleting data, while `unpauseVfs()` reacquires handles and re-registers; both are meant for cooperative handoff between pages or workers and refuse to pause with active SQLite file handles.

`importDb()` and `importDbChunked()` overwrite or create a VFS-hosted database from bytes or async chunks, validate SQLite database headers, require a database-sized input, and force database header bytes 18 and 19 to `1` to disable WAL mode for the imported image. `exportFile()` returns a `Uint8Array` copy of a hosted file's SQLite bytes.

## Dependencies and Integration Points
The file depends on browser OPFS APIs, synchronous access handles, `TextEncoder`/`TextDecoder`, `navigator.storage.getDirectory()`, and SQLite wasm bindings: `sqlite3.capi`, `sqlite3.wasm`, `sqlite3.util`, `sqlite3.vfs.installVfs()`, `sqlite3_vfs`, `sqlite3_file`, and `sqlite3_io_methods` struct binders. It installs through `globalThis.sqlite3ApiBootstrap.initializers`. It is elided from Node builds. It integrates with OO1 by adding a DB constructor and with tests through options such as `$testThrowPhase1` and `$testThrowPhase2`.

## Risks and Edge Cases
The main risk is exclusivity: every pool slot stays locked by a sync handle for the page/worker lifetime, so another same-origin instance using the same directory cannot use those files until pause/removal. Capacity is fixed from the synchronous VFS perspective, so creates fail with `SQLITE_CANTOPEN` when the pool is full. Paths must be absolute URL pathnames; relative path behavior is documented as a long-standing quirk. `removeVfs()` has limited recovery if OPFS deletion fails. `pauseVfs()`/`unpauseVfs()` can leave undefined state if handle close/acquire errors occur. Metadata digest changes can make new pool files unreadable by older wasm versions, and old versions may replace files they view as digest-corrupt.

## Test Signals
Useful test signals include successful/failed installation under browsers with and without modern sync access handles, repeated install calls returning the same Promise, forced init failure/reinit options, clear-on-init wiping, capacity add/reduce behavior, pool-full create failures, import/export byte-for-byte checks, digest migration with legacy pool files, pause/unpause handoff across two contexts, delete-on-close cleanup, and OO1 `OpfsSAHPoolDb` opening with the registered VFS.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-sahpool.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-wl.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-wl.c-pp.js

## Purpose
This file installs the `opfs-wl` VFS, a variant of the standard wasm OPFS VFS that uses browser Web Locks for SQLite `xLock()`/`xUnlock()` behavior. It shares the common OPFS async proxy machinery with the regular `opfs` VFS, but changes the lock policy so that browser-managed Web Locks can provide stricter FIFO-style lock distribution under contention.

## Important APIs, Types, and Functions
The bootstrap initializer defines `installOpfsWlVfs(options)` and queues it in `sqlite3ApiBootstrap.initializersAsync`. It depends on `sqlite3.opfs.initOptions()`, `sqlite3.opfs.createVfsState()`, the common VFS state's `bindVfs()`, `opRun()`, metrics counters, timing helpers, and `__openFiles`. The VFS name is fixed to `opfs-wl`. The two VFS-specific methods supplied to `bindVfs()` are `xLock(pFile, lockType)` and `xUnlock(pFile, lockType)`.

When OO1 is present, the post-registration callback installs `sqlite3.oo1.OpfsWlDb`, a `DB` subclass that normalizes constructor arguments and forces `opt.vfs` to this VFS name. It also exposes `OpfsWlDb.importDb = opfsUtil.importDb`, reusing the common OPFS import helper.

## Control Flow
On bootstrap, the file returns immediately if `sqlite3.opfs` is unavailable or the config disables `vfs['opfs-wl']`. Async installation normalizes options for `opfs-wl`; a falsy result means the VFS is disabled by URL/config and the top-level sqlite3 object is returned without registration. Otherwise `createVfsState()` builds the shared state and `bindVfs()` registers a VFS whose methods are the common OPFS methods plus the Web-Lock-specific lock/unlock callbacks.

`xLock()` starts metrics timing, retrieves the open file record for `pFile`, calls `opRun('xLock', pFile, lockType)`, and records `f.lockType` only on success. `xUnlock()` mirrors that flow with `opRun('xUnlock', ...)`. Unlike the regular `opfs` wrapper, it does not locally skip redundant lock calls when the file already has a lock; it delegates every lock transition to the async half, where the Web Locks policy lives.

## State and Persistence Behavior
This file itself keeps no persistent storage state. Per-file runtime state is the shared `__openFiles[pFile].lockType`, metrics counters, and the common OPFS VFS state. Actual database persistence, OPFS file access, import behavior, and async proxy communication are delegated to the shared OPFS implementation. Lock ordering depends on browser Web Locks rather than SQLite-visible file contents.

## Dependencies and Integration Points
The file is non-Node-only and is appended after `opfs-common-shared.c-pp.js`. It requires `sqlite3.opfs` helpers, the async OPFS proxy, worker-capable OPFS support, and Web Locks support in the async half. It integrates with sqlite3 initialization through `initializersAsync` and with OO1 through `sqlite3.oo1.OpfsWlDb`. The officially undocumented `opfs-wl-disable` URL/config handling is delegated to `initOptions()`.

## Risks and Edge Cases
Functional behavior is expected to match the regular `opfs` VFS except for contention fairness. Web Locks availability and browser scheduling determine the benefit; the comments explicitly say fairer lock distribution is likely but not guaranteed. Because every lock/unlock crosses the proxy, incorrect shared-state assumptions in the async half would affect database availability. This variant deliberately does not install the busy-timeout post-open callback used by `opfs`, so applications that relied on that default must configure busy timeout themselves.

## Test Signals
Tests should verify installation success/failure under config disable and missing OPFS support, correct registration under `opfs-wl`, OO1 `OpfsWlDb` construction, import helper attachment, basic create/read/write persistence, and multi-worker or multi-tab contention where lock requests are serviced through Web Locks. Regression checks should compare SQL behavior against the standard `opfs` VFS while observing differences in lock fairness and busy-timeout defaults.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-wl.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs.c-pp.js

## Purpose
This file installs the standard `opfs` sqlite3 VFS for wasm builds. It is the synchronous JavaScript half of an OPFS-backed VFS that proxies asynchronous browser file operations through a second worker (`sqlite3-opfs-async-proxy.js`) so SQLite can call a synchronous `sqlite3_vfs` interface. It is intended to run only where dedicated workers, `SharedArrayBuffer`, Atomics, and OPFS support are available.

## Important APIs, Types, and Functions
The initializer defines `installOpfsVfs(options)` and appends an async bootstrap task that calls it. Publicly visible behavior is registration of an SQLite VFS named `opfs`, and, when OO1 is enabled, `sqlite3.oo1.OpfsDb`. The function uses `sqlite3.opfs.initOptions('opfs', options)`, `sqlite3.opfs.createVfsState()`, and the returned state's `vfs.bindVfs()`, `opRun()`, timing helpers, metrics counters, and `__openFiles`.

The only VFS-specific methods in this file are `xLock()` and `xUnlock()`. All storage, path handling, file I/O, proxying, metrics setup, and import mechanics are provided by common OPFS code loaded before this wrapper.

## Control Flow
At startup, the initializer exits when `sqlite3.opfs` is missing or `sqlite3.config.disable.vfs.opfs` is set. `installOpfsVfs()` normalizes options and exits as a no-op when OPFS is disabled by options or URL. For active installs, `createVfsState()` prepares the VFS struct and shared proxy state. `bindVfs()` receives the lock/unlock overrides and a post-registration callback, then handles registration and common method installation.

`xLock()` records timing and metrics, looks up the open file object, and only calls `opRun('xLock', pFile, lockType)` if the file was previously unlocked. SQLite lock types are tracked in `f.lockType`, but the OPFS implementation treats actual file locks as exclusive. Re-locking an already locked file only updates the tracked lock type. `xUnlock()` calls the proxy only when transitioning to `SQLITE_LOCK_NONE` from a locked state, then records the new lock type on success.

After registration, the OO1 integration creates `OpfsDb`, a DB subclass forcing this VFS. It assigns `OpfsDb.importDb` to the shared `opfsUtil.importDb`. It also sets a VFS post-open callback that applies `sqlite3_busy_timeout(db, 10000)` for this VFS, retained for compatibility even though comments call it inconsistent with core open APIs.

## State and Persistence Behavior
This wrapper owns no persistent state directly. Runtime state includes lock type on entries in `__openFiles`, metrics counts/timings, and whatever proxy state the common OPFS layer holds. Persistence is in OPFS through the async proxy and common implementation. Lock state is deliberately simplified: SQLite's fine-grained lock levels are represented to SQLite, while OPFS-level access is exclusive.

## Dependencies and Integration Points
The file is non-Node-only and depends on `sqlite3.opfs` being initialized by shared OPFS modules. It requires a dedicated worker environment and SharedArrayBuffer/Atomics because synchronous C calls must block while the async proxy performs browser file operations. It integrates with `sqlite3ApiBootstrap.initializersAsync`, `sqlite3.config.warn`, OO1 DB construction, and `sqlite3.capi.sqlite3_busy_timeout`.

## Risks and Edge Cases
The install Promise can reject if the async proxy cannot load, OPFS is unavailable, the code runs on the wrong thread, or SharedArrayBuffer is unavailable due to missing COOP/COEP headers. Lock handling deliberately avoids redundant proxy calls, so correctness depends on `__openFiles[pFile].lockType` staying in sync with the async half. The retained default busy timeout may surprise callers expecting sqlite3 core defaults. The install callback catches rejection and warns, so applications must inspect VFS availability if OPFS is required.

## Test Signals
Relevant tests include disabled/no-op installs, successful `opfs` VFS registration in a worker, graceful warning on missing SAB/OPFS/proxy support, basic open/write/read persistence, lock/unlock transitions under concurrent access, `OpfsDb` constructor behavior, `OpfsDb.importDb`, and the post-open busy-timeout setting. Tests should also cover contention and redundant lock transitions to ensure no unnecessary proxy unlock or lock calls corrupt state.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vtab-helper.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vtab-helper.c-pp.js

## Purpose
This file installs `sqlite3.vtab`, a JavaScript helper namespace for implementing SQLite virtual tables in wasm. It is active only when the wasm exports include `sqlite3_declare_vtab`, meaning virtual table support exists in the build. Its job is to make pointer-heavy `sqlite3_module`, `sqlite3_vtab`, `sqlite3_vtab_cursor`, and `sqlite3_index_info` interactions safer and more idiomatic from JavaScript.

## Important APIs, Types, and Functions
It augments `capi.sqlite3_index_info.prototype` with `nthConstraint(n, asPtr)`, `nthConstraintUsage(n, asPtr)`, and `nthOrderBy(n, asPtr)`, each performing pointer arithmetic and wrapping the target struct or returning its pointer. It defines `StructPtrMapper(name, StructType)` and uses it to expose `vtab.xVtab` and `vtab.xCursor`, each with `create(ppOut)`, `get(pCObj)`, `unget(pCObj)`, `dispose(pCObj)`, and `StructType`.

Other helpers include `vtab.xIndexInfo(pIdxInfo)`, `vtab.xError(methodName, err, defaultRc)`, `vtab.xRowid(ppRowid64, value)`, `vtab.setupModule(opt)`, and `capi.sqlite3_module.prototype.setupModule(opt)`.

## Control Flow
The initializer exits immediately in builds without virtual table support. For index-info helpers, calls validate bounds against `$nConstraint` or `$nOrderBy`, calculate offsets using struct `sizeof`, and return false when out of range. The pointer mapper closes over a `Map` keyed by C pointer values. `create()` allocates a new struct wrapper, stores its pointer into SQLite's output pointer, and maps the pointer to the wrapper. `get()` retrieves without transferring ownership. `unget()` removes the mapping so the caller must dispose. `dispose()` ungets and disposes in one step.

`setupModule()` builds or receives a `sqlite3_module`, normalizes `xCreate`/`xConnect` and `xDestroy`/`xDisconnect` when one side is `true`, optionally wraps module methods in exception-catching adapters, installs methods, and fills `$iVersion` if it is still zero. With `catchExceptions`, `xCreate` and `xConnect` handlers also allocate an SQLite error string in `pzErr` for non-allocation exceptions.

## State and Persistence Behavior
The helper's main state is in per-mapper JavaScript `Map` instances that associate live C struct pointers with JS wrapper objects. Those maps must be cleaned by calling `unget()`/`dispose()` at the correct SQLite lifecycle points; otherwise wrappers and their wasm allocations can leak. No persistent database or filesystem state is modified by this file.

## Dependencies and Integration Points
The implementation depends on `sqlite3.wasm` pointer helpers, `sqlite3.capi` struct binders, `sqlite3.SQLite3Error`, `sqlite3.WasmAllocError`, and `sqlite3.config.error`. It integrates directly with SQLite virtual table method lifecycles: `xCreate`, `xConnect`, `xBestIndex`, `xOpen`, `xClose`, `xDisconnect`, `xDestroy`, `xRowid`, and update/transaction hooks. `setupModule()` uses `sqlite3_module.installMethods()` from the struct binder layer.

## Risks and Edge Cases
The most important risk is ownership confusion. `get()` returns an object that must not be disposed by the caller, while `unget()` transfers disposal responsibility. Forgetting to unmap cursors or vtabs at failure paths leaks JS/wasm wrapper state. Letting exceptions escape virtual table methods without `catchExceptions` causes undefined behavior across the C ABI. `xError()` only logs if `xError.errorReporter` is a function and maps unknown errors to `SQLITE_ERROR`, which can hide detailed causes unless callers inspect logs. `setupModule()` mutates the passed `methods` object when resolving `true` aliases.

## Test Signals
Tests should cover pointer mapper lifecycle for vtabs and cursors, out-of-range index-info access returning false, pointer-return mode, `xRowid()` writing 64-bit rowids, exception-to-result-code mapping including `WasmAllocError`, `SQLite3Error`, and default cases, `xCreate`/`xConnect` alias preservation, automatic `$iVersion` selection for v1 through v4 method sets, and cleanup on `setupModule()` failure when it created the module object.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vtab-helper.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-wasm.c -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-wasm.c

## Purpose
This C file is the wasm-specific SQLite compilation unit. It sets SQLite build defaults for wasm, includes the SQLite amalgamation directly so wasm helpers can access private state, and exports internal helper functions used by the JavaScript bindings. The exported helpers are not public SQLite APIs; they bridge wasm memory management, enum/struct metadata, VFS file operations, serialization/import/export helpers, kvvfs internals, variadic config wrappers, optional WASMFS OPFS initialization, and C-side test hooks.

## Important APIs, Types, and Functions
Build configuration defines `SQLITE_WASM`, hardens or adjusts defaults such as `SQLITE_ENABLE_API_ARMOR`, `SQLITE_THREADSAFE=0`, `SQLITE_TEMP_STORE=2`, URI support, default page/cache sizes, disabled deprecated/load-extension/shared-cache/UTF16 features, optional bare-bones feature removal, and optional `SQLITE_EXTRA_INIT_MUTEXED`. It defines `SQLITE_WASM_EXPORT`, `SQLITE_WASM_EXPORT_NAMED`, and `SQLITE_WASM_EXPORT2` for explicit wasm exports.

The pseudo-stack API includes `sqlite3__wasm_pstack_ptr()`, `sqlite3__wasm_pstack_restore()`, `sqlite3__wasm_pstack_alloc()`, `sqlite3__wasm_pstack_remaining()`, and `sqlite3__wasm_pstack_quota()`, backed by a static 4 KiB aligned buffer. `sqlite3__wasm_enum_json()` emits JSON for constants and struct layouts, including result codes, open flags, config values, VFS/io/file structs, kvvfs structs, and virtual table structs when enabled.

Operational wrappers include `sqlite3__wasm_vfs_unlink()`, `sqlite3__wasm_db_vfs()`, `sqlite3__wasm_db_reset()`, `sqlite3__wasm_db_export_chunked()`, `sqlite3__wasm_db_serialize()`, `sqlite3__wasm_vfs_create_file()`, `sqlite3__wasm_posix_create_file()`, `sqlite3__wasm_kvvfsMakeKey()`, `sqlite3__wasm_kvvfs_methods()`, `sqlite3__wasm_vtab_config()`, `sqlite3__wasm_db_config_ip()`, `sqlite3__wasm_db_config_pii()`, `sqlite3__wasm_db_config_s()`, `sqlite3__wasm_config_i()`, `sqlite3__wasm_config_ii()`, `sqlite3__wasm_config_j()`, `sqlite3__wasm_qfmt_token()`, `sqlite3__wasm_kvvfs_decode()`, `sqlite3__wasm_kvvfs_encode()`, and `sqlite3__wasm_init_wasmfs()`.

When `SQLITE_WASM_ENABLE_C_TESTS` is enabled, additional exported probes exercise struct binding, pointer, int64, stack overflow, string deallocation, and SQLTester glob behavior.

## Control Flow
Compilation first applies wasm-specific SQLite options, optionally strips features for bare-bones builds, includes `sqlite3.c`, then defines helper exports. The pseudo-stack is a downward-growing stack: callers save the current pointer, allocate zeroed aligned blocks, and restore to a saved pointer. `sqlite3__wasm_enum_json()` lazily fills a static JSON buffer. It leaves byte 0 empty until the end to reduce a small race where a concurrent caller could observe a partially generated buffer.

Database file helpers use core SQLite or VFS methods. `sqlite3__wasm_db_export_chunked()` obtains the main database file pointer via `SQLITE_FCNTL_FILE_POINTER`, chooses a chunk size aligned to the database size when possible, reads through `xRead`, and invokes a callback for each chunk. `sqlite3__wasm_db_serialize()` wraps `sqlite3_serialize()` and returns `SQLITE_NOMEM` only when no output pointer is produced and `SQLITE_SERIALIZE_NOCOPY` was not requested. `sqlite3__wasm_vfs_create_file()` opens a VFS file, optionally locks it, truncates, writes in 512-byte blocks, unlocks/closes, and deletes newly created files on failure. The POSIX variant uses `fopen()`/`fwrite()` for Emscripten-style filesystems.

## State and Persistence Behavior
Static state includes the pseudo-stack buffer, the enum JSON buffer, static kvvfs key buffer, and the optional singleton WASMFS OPFS backend. `sqlite3__wasm_db_reset()` changes a database by enabling reset-database mode and running `VACUUM`; it warns that virtual table `xDestroy()` is not called. VFS create/unlink helpers modify storage behind the selected VFS. WASMFS initialization creates and mounts an OPFS backend at a single-component mount point such as `/opfs` when compiled with Emscripten WASMFS support, otherwise returns `SQLITE_NOTFOUND`.

## Dependencies and Integration Points
This file depends on SQLite internals from `sqlite3.c`, `os_kv.c` private kvvfs symbols, C99, wasm export attributes, optional Emscripten WASMFS headers, and build-time macros from the wasm build system. JavaScript bindings consume `sqlite3__wasm_enum_json()` to build constant maps and struct binders, use pseudo-stack functions for temporary output pointers, and call VFS/config/serialization wrappers to avoid unsupported variadic or private C interfaces in JS.

## Risks and Edge Cases
`sqlite3__wasm_enum_json()` has a fixed 20 KiB static buffer guarded by assertions and can return null if metadata grows too large. Memory64 builds are noted as problematic. The pseudo-stack is tiny and only for small temporaries; misuse of restore pointers is undefined outside assertions. `sqlite3__wasm_vfs_create_file()` is deprecated for generic VFS import because out-of-scope VFS use can trigger SQLite debug assertions. It also uses 32-bit `nData`, limiting large imports. Variadic config wrappers intentionally return `SQLITE_MISUSE` for unsupported op codes. The wasm build is single-threaded except where browser storage VFSes provide their own coordination.

## Test Signals
Test coverage should verify enum JSON parses and matches C struct sizes/offsets, pseudo-stack alignment/quota/restore behavior, serialization and chunked export results, VFS create/unlink behavior on default, OPFS, and unsupported VFSes, POSIX file creation, kvvfs encode/decode/key size behavior, db/vtab/config wrapper allowed and rejected op codes, WASMFS init return codes with and without support, and C-test exports when enabled. SQLTester glob tests should cover `*`, `?`, bracket ranges, inversion, and `#` numeric matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-wasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1-promiser.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1-promiser.c-pp.js

## Purpose
This file implements a Promise-based client wrapper for SQLite Worker API #1. It can run in the main thread or in a worker that supports nested workers, creates or accepts a worker loading `sqlite3-worker1.js`, and turns request/response message exchanges into Promises. It is omitted when OO1 is omitted because Worker API #1 depends on the higher-level API.

## Important APIs, Types, and Functions
The main global is `sqlite3Worker1Promiser(config)`, which returns a stateful `promiserFunc`. Calls may be `promiserFunc(type, args)` or `promiserFunc({type, args, ...})`. The config accepts `worker`, `onready`, `onunhandled`, `generateMessageId`, `debug`, and an internal `onerror`. The default config creates a worker from the appropriate build artifact: bundler-friendly module, ES module, or classic `sqlite3-worker1.js`, preserving `sqlite3.dir` URL handling where relevant.

`sqlite3Worker1Promiser.v2(config)` wraps the original API and returns a Promise that resolves to the promiser function after the worker emits the ready message. In ES module builds, v2 is exported as default and the temporary global is deleted.

## Control Flow
The factory normalizes config, instantiates a worker if `worker` is a function, replaces `worker.onmessage`, and maintains `handlerMap` keyed by generated message IDs. The ready event is identified as `{type:'sqlite3-api', result:'worker1-ready'}` and triggers `onready(promiserFunc)`. Normal response messages look up `handlerMap[messageId]`, delete it, reject on `type:'error'`, update current `dbId` on open/close, and resolve with the worker payload.

When sending, the promiser builds or accepts a message envelope, injects the current `dbId` for non-open messages unless one is already set, assigns a unique `messageId`, records `departureTime`, stores resolve/reject handlers, and posts to the worker. For `exec` with a function callback, it synthesizes a row callback ID (`messageId + ':row'`), replaces `args.callback` with that string for the worker protocol, and routes per-row worker messages by temporary `handlerMap` entry. String callbacks are rejected because the promiser owns `worker.onmessage` and cannot dispatch arbitrary client message types.

## State and Persistence Behavior
State is entirely in JavaScript: `handlerMap`, optional generated message ID counters, and the current `dbId` used as the default target database. No database state is persisted by this wrapper; persistence is handled by the worker and SQLite. The row callback handler is removed in `finally()` so it is cleared after the exec request settles.

## Dependencies and Integration Points
The file depends on Web Workers, `performance.now()`, `URL`, `import.meta.url` in module builds, `document.currentScript` in classic builds, and the Worker API #1 message protocol implemented by `sqlite3.initWorker1API()`. It integrates with `sqlite3-worker1.c-pp.js`, which posts the ready message after module initialization. The default worker path logic keeps classic and module builds aligned with generated artifact names.

## Risks and Edge Cases
The factory replaces `worker.onmessage`, so callers cannot independently use `onmessage` on the same worker without going through `onunhandled`. Message IDs must be unique; custom generators that collide will misroute or leak Promises. `dbId` defaulting is convenient for a single active DB but can surprise multi-DB clients unless they pass explicit `dbId`. Per-row callbacks arrive asynchronously as worker messages and must tolerate the final row message with `row=undefined` and `rowNumber=null`. v1 readiness uses a callback rather than a Promise, so v2 is safer for module-style initialization.

## Test Signals
Tests should cover default worker creation paths for classic/module builds, ready callback and v2 Promise resolution, open setting `dbId`, close clearing it, error messages rejecting, unhandled messages reaching `onunhandled` or `onerror`, custom message ID generation, exec function callbacks receiving row and end-of-result messages, string exec callbacks throwing, and cleanup of row handlers after success or failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1-promiser.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1.c-pp.js -->
# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1.c-pp.js

## Purpose
This is the worker entrypoint for SQLite Worker API #1. It loads the generated sqlite3 JavaScript module, initializes it, then starts the worker API by calling `sqlite3.initWorker1API()`. The indirection is necessary because a worker that directly loads `sqlite3.js` cannot reliably call `sqlite3InitModule()` in the right order or visibility context.

## Important APIs, Types, and Functions
The file imports or loads `sqlite3InitModule` using build-mode-specific code. Bundler-friendly ES module builds import `./sqlite3-bundler-friendly.mjs`; ES module builds import `./sqlite3.mjs`; classic builds use `importScripts()` to load `sqlite3.js`. After loading, it calls `sqlite3InitModule().then(sqlite3 => sqlite3.initWorker1API())`.

The worker API started by `initWorker1API()` is expected to post the ready message `{type:'sqlite3-api', result:'worker1-ready'}`, which is consumed by clients such as `sqlite3-worker1-promiser.c-pp.js`.

## Control Flow
In classic builds, the file inspects `globalThis.location.href` search parameters. If `sqlite3.dir` exists, it prepends that directory when building the `sqlite3.js` URL; otherwise it loads `sqlite3.js` from the current worker script location. Once the script or module import has provided `sqlite3InitModule`, initialization is asynchronous and the Worker API is installed only after the sqlite3 module Promise resolves.

If the build is compiled with `omit-oo1`, the file is replaced by a comment because Worker API #1 depends on the OO1 layer.

## State and Persistence Behavior
This file owns no persistent state. It controls module-loading state in the worker global scope and delegates all database, VFS, and message handling state to the initialized sqlite3 module and Worker API #1 implementation.

## Dependencies and Integration Points
Dependencies are Web Worker globals, `importScripts()` for classic builds, ES module imports for module builds, `sqlite3InitModule`, and `sqlite3.initWorker1API()`. It integrates directly with worker clients that wait for the ready message, especially the promiser wrapper. The `sqlite3.dir` URL argument is a path integration point for deployments that host generated sqlite3 assets outside the worker entrypoint directory.

## Risks and Edge Cases
Wrong asset paths will fail before the ready message is posted, leaving clients waiting or receiving worker errors. Module type must match the artifact: module workers need the `.mjs` variants, while classic workers need `importScripts`. The file assumes `sqlite3InitModule()` resolves successfully; initialization failures are not caught here. Builds without OO1 cannot use this worker entrypoint.

## Test Signals
Tests should instantiate the worker in classic, ES module, and bundler-friendly build modes where applicable, verify the ready message is posted after initialization, verify `sqlite3.dir` path rewriting, and perform a simple open/exec/close through Worker API #1 or the promiser wrapper. Negative tests should cover missing asset paths and omit-OO1 builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1.c-pp.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/common/SqliteTestUtil.js -->
# sources/storage-engines/sqlite/ext/wasm/common/SqliteTestUtil.js

## Purpose
This file provides browser/worker test bootstrap utilities for SQLite wasm test pages. It defines assertion helpers under `self.SqliteTestUtil` and an Emscripten module configuration object under `self.sqlite3TestModule`. The utilities support test counting, error assertions, URL argument parsing, module loading progress UI, stdout/stderr forwarding, and temporary sqlite3 API configuration.

## Important APIs, Types, and Functions
`SqliteTestUtil` exposes `counter`, `toBool(expr)`, `assert(expr, ...msg)`, `affirm(expr, msg)`, `mustThrow(f, msg)`, `mustThrowMatching(f, filter, msg)`, `throwIf(expr, msg)`, `throwUnless(expr, msg)`, and `processUrlArgs(str)`. The local `E()` and `EAll()` functions proxy `querySelector()` and `querySelectorAll()` and are used by the module status UI.

`sqlite3TestModule` provides `postRun`, `print`, `printErr`, `setStatus(text)`, `sqlite3ApiConfig`, and `initSqlite3()`. The default `sqlite3ApiConfig` sets `wasmfsOpfsDir: "/opfs"`.

## Control Flow
The file is an IIFE over `self`, so it works in window or worker-like globals. Assertion-style helpers increment `SqliteTestUtil.counter` for every check. `assert()` lazily chooses either global `abort` or a throwing fallback, then aborts/throws on failure. `affirm()` always throws on failure. `mustThrow()` and `mustThrowMatching()` execute a callback and require an exception, with matching by regex, predicate, or exact string.

`processUrlArgs()` defaults to `window.location.search.substring(1)` when no argument is supplied and a window search string exists. It strips fragments, splits on ampersands, decodes keys and values, and returns a prototype-less object; keys without values receive boolean `true`.

`sqlite3TestModule.setStatus()` lazily locates `#module-status`, `#module-progress`, and `#module-spinner`, ignores repeated text, advances progress on each status change, displays non-empty status text, and removes/hides progress UI when loading completes. `initSqlite3()` temporarily installs `self.sqlite3ApiConfig`, calls `self.sqlite3InitModule(this)`, and removes the global config in `finally()`.

## State and Persistence Behavior
State is transient test harness state: the assertion counter, cached abort function, cached status UI references, last status text/step, module `postRun` callbacks, and temporary `self.sqlite3ApiConfig`. It does not persist data or modify SQLite databases directly. The temporary config affects sqlite3 initialization only during `initSqlite3()`.

## Dependencies and Integration Points
The file depends on browser DOM APIs when status UI is used, `console.log/error`, optional global `abort`, `window.location`, and Emscripten's `sqlite3InitModule()` factory. It is used by test scripts in the same wasm common/test area and feeds `sqlite3ApiBootstrap()` indirectly through `sqlite3ApiConfig`. It works in workers for non-DOM paths because DOM access is delayed until `setStatus()`.

## Risks and Edge Cases
`setStatus()` assumes DOM elements exist before manipulating classes or text; tests without those IDs must avoid status UI or provide stubs. `assert()` may call `abort()` instead of throwing, which can terminate execution differently across environments. `processUrlArgs()` is simple and treats missing values as `true`; it does not preserve duplicate keys. `initSqlite3()` mutates global `self.sqlite3ApiConfig` temporarily, so concurrent initialization attempts with different configs could interfere.

## Test Signals
Tests should cover assertion counter increments, function and value truthiness via `toBool()`, abort/throw failure behavior, exception matching modes, URL parsing with encoded keys/values, flags, fragments, and no-window fallback, status UI transitions with repeated and final empty status, stdout/stderr forwarding, `postRun` preservation, and `initSqlite3()` installing/removing `sqlite3ApiConfig` around a mocked module factory.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/wasm/common/SqliteTestUtil.js -->
