# subset-b-008774 research

Grouped research for SQLite core API and memory allocator sources. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/main.c -->
# sources/storage-engines/sqlite/src/main.c

## Purpose

`main.c` is the central implementation file for SQLite's public C API. It does not contain an executable `main()`; instead it wires library initialization, global configuration, connection lifecycle, callback registration, collation and function registration, URI filename handling, WAL checkpoint APIs, error APIs, snapshot APIs, and assorted compatibility and test-control entry points. It is the point where process-global SQLite state in `sqlite3GlobalConfig` is transitioned into per-connection `sqlite3` objects and where many public routines normalize arguments before delegating to btree, pager, VFS, mutex, malloc, parser, virtual-table, WAL, and extension subsystems.

## Important APIs, Types, And Functions

The file exports version and build identity routines (`sqlite3_libversion`, `sqlite3_sourceid`, `sqlite3_libversion_number`, `sqlite3_threadsafe`), lifecycle routines (`sqlite3_initialize`, `sqlite3_shutdown`, `sqlite3_config`), connection configuration (`sqlite3_db_config`, `sqlite3_db_mutex`, `sqlite3_db_release_memory`, `sqlite3_db_cacheflush`), open/close APIs (`sqlite3_open`, `sqlite3_open_v2`, `sqlite3_open16`, `sqlite3_close`, `sqlite3_close_v2`), error APIs (`sqlite3_errmsg`, `sqlite3_errmsg16`, `sqlite3_errcode`, `sqlite3_extended_errcode`, `sqlite3_errstr`, `sqlite3_system_errno`, `sqlite3_error_offset`, `sqlite3_set_errmsg`), callbacks (`sqlite3_busy_handler`, `sqlite3_busy_timeout`, `sqlite3_progress_handler`, trace/profile hooks, commit/update/rollback/preupdate hooks, WAL hook, autovacuum-pages hook), SQL extensibility APIs (`sqlite3_create_function*`, `sqlite3_create_window_function`, `sqlite3_overload_function`, `sqlite3_create_collation*`, `sqlite3_collation_needed*`), limit and metadata APIs (`sqlite3_limit`, `sqlite3_table_column_metadata`, `sqlite3_file_control`, `sqlite3_db_name`, `sqlite3_db_filename`, `sqlite3_db_readonly`, `sqlite3_txn_state`), URI and filename utilities, snapshot APIs under `SQLITE_ENABLE_SNAPSHOT`, and compile-option diagnostics.

Internally important helpers include `setupLookaside`, built-in collations (`binCollFunc`, `rtrimCollFunc`, `nocaseCollatingFunc`), `functionDestroy`, `disconnectAllVtab`, `connectionIsBusy`, `sqlite3Close`, `sqlite3LeaveMutexAndCloseZombie`, `sqlite3RollbackAll`, `sqliteDefaultBusyCallback`, `sqlite3CreateFunc`, `createFunctionApi`, `createCollation`, `sqlite3ParseUri`, `uriParameter`, `openDatabase`, `databaseName`, and `appendText`. Major state types used here include `sqlite3`, `sqlite3GlobalConfig`, `Btree`, `Pager`, `Schema`, `FuncDef`, `FuncDestructor`, `CollSeq`, `BusyHandler`, `DbClientData`, `Savepoint`, `Module`, `Table`, and VFS/file handles.

## Control Flow

Process initialization starts in `sqlite3_initialize()`. It initializes WSD if required, checks pointer size invariants, initializes mutexes, initializes malloc, creates a recursive initialization mutex, registers built-in functions, initializes pcache, initializes the OS/VFS layer, optionally initializes memdb, configures the page-cache buffer, marks `sqlite3GlobalConfig.isInit`, and runs optional compile-time extra init hooks. Recursive calls are permitted through `pInitMutex`; other threads block on initialization completion. `sqlite3_shutdown()` unwinds the OS layer, automatic extensions, pcache, malloc, mutexes, and global directory pointers.

`sqlite3_config()` is a large variadic dispatcher. Most options are rejected once SQLite is initialized, except a limited set such as logging and pcache header-size inspection. It configures threading mode, mutex methods, malloc methods, memstatus, page cache, pcache2, fixed heap allocators, lookaside defaults, logging, URI defaults, mmap defaults, sorter and statement journal sizing, and other compile-conditional global flags.

Connection setup flows through `openDatabase()`. It auto-initializes SQLite, derives whether the connection needs a recursive mutex from global and open flags, normalizes shared-cache/private-cache flags, strips invalid VFS flags, allocates and initializes a `sqlite3` object, seeds per-connection limits and defaults, installs built-in collations, parses URI or plain filenames, opens the main `Btree`, attaches schema objects for `main` and `temp`, registers per-connection built-ins and compiled-in or automatic extensions, applies default locking and lookaside, enables default WAL autocheckpointing, then returns either an open connection, a sick connection with an error, or NULL on allocation failure. Close flows through `sqlite3Close()` into `sqlite3LeaveMutexAndCloseZombie()`, with `sqlite3_close()` refusing active statements/backups and `sqlite3_close_v2()` allowing a zombie connection that is freed after remaining statements/backups finish.

Runtime API calls consistently take the connection mutex, modify fields on `sqlite3`, call lower layers, then return through `sqlite3ApiExit()` or direct error normalization. Function and collation registration validate encodings and arity, refuse replacement while active VDBEs are running, expire prepared statements when semantics change, and manage destructor ownership. WAL checkpoint APIs locate target schemas, reset busy counters, delegate to `sqlite3Checkpoint()`/btree checkpoint code, and normalize busy/error results. URI parsing decodes `file:` URIs into SQLite's internal filename layout and updates open flags based on `mode=`, `cache=`, and `vfs=` parameters.

## State And Persistence Behavior

The most important persistent process state is `sqlite3GlobalConfig`: initialization flags, mutex/malloc/pcache methods, default lookaside, heap/page-cache buffers, logging hooks, URI defaults, mmap bounds, and compile-conditional tuning knobs. Connection state is stored in `sqlite3`: open state, mutex, error code and message value, flags, limits, callback pointers and callback data, lookaside freelists, schema slots, btree handles, transaction/autocommit state, savepoints, client data, virtual-table modules, function and collation hash tables, WAL callback, busy handler, and filename/VFS data.

Database persistence is delegated rather than implemented locally. `openDatabase()` opens the main database through `sqlite3BtreeOpen()` and resolves pager/VFS filenames through `sqlite3ParseUri()`. `sqlite3RollbackAll()` rolls back all attached btrees and invalidates cursors when needed. `sqlite3_db_cacheflush()` pushes dirty pager-cache pages for write transactions. WAL APIs invoke pager/btree checkpoint and snapshot routines. Filename helpers preserve a memory layout that includes database, URI query parameters, journal filename, and WAL filename, allowing VFS and pager code to retrieve associated paths.

Lookaside state is per connection and rebuilt by `setupLookaside()`. It may be caller-supplied memory or heap memory owned by SQLite. Two-size lookaside builds split the buffer into full-size and `LOOKASIDE_SMALL` slots. Lookaside cannot be reconfigured while in use.

## Dependencies And Integration Points

This file includes `sqliteInt.h` and conditionally includes FTS3, RTree, and ICU headers. It calls into almost every core subsystem: mutex (`sqlite3MutexInit`, static and recursive mutex allocation), malloc (`sqlite3MallocInit`, `sqlite3MallocZero`, `sqlite3_free`, `sqlite3ApiExit`), pcache, VFS/OS (`sqlite3OsInit`, `sqlite3_vfs_find`, `sqlite3OsSleep`, file-control), btree and pager, schema initialization, parser helpers, virtual tables, extension autoloading, WAL, memdb, UTF conversion, hash tables, value/error objects, status/fault simulation, and compile-option generation. Public behavior is highly compile-option-sensitive, with many branches guarded by options such as `SQLITE_OMIT_WAL`, `SQLITE_OMIT_UTF16`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_THREADSAFE`, `SQLITE_ENABLE_MEMSYS3/5`, and `SQLITE_OMIT_DESERIALIZE`.

## Risks And Edge Cases

Initialization and shutdown are sensitive to concurrency and lifetime. `sqlite3_config()` misuse after initialization can leave global method tables inconsistent if not guarded. URI parsing has security-sensitive behavior around authorities, `%00`, path truncation, and open-mode permission checks. The internal filename memory layout is pointer-arithmetic based; passing arbitrary strings to filename helpers can corrupt memory. Function and collation replacement while statements are active must return `SQLITE_BUSY` or existing VDBEs may execute changed semantics. Closing must properly handle virtual tables, backups, active statements, client-data destructors, and `close_v2` zombies. Error paths during `openDatabase()` intentionally return either NULL or a sick handle, so callers and tests need to validate both. WAL checkpoint and snapshot APIs are constrained by transaction state, schema selection, and WAL availability. Lookaside setup must avoid integer overflow and must not be reconfigured while allocations are outstanding.

## Test Signals

Strong test signals include API lifecycle tests for repeated initialize/shutdown, configuration-before/after-init behavior, open flag combinations, URI options (`mode`, `cache`, `vfs`, `%00`, authorities), NULL and misuse handling under API armor, `sqlite3_close` versus `sqlite3_close_v2` with active statements/backups, function/collation destructor and busy behavior, default collation ordering, busy-timeout retry timing, WAL autocheckpoint and explicit checkpoint results, snapshot get/open/recover state requirements, table-column metadata for rowid and normal columns, file-control special opcodes, lookaside reconfiguration busy cases, and OOM/fault-simulation paths around `sqlite3TestExtInit`, `openDatabase`, UTF conversion, and registration APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/malloc.c -->
# sources/storage-engines/sqlite/src/malloc.c

## Purpose

`malloc.c` is SQLite's high-level memory allocation wrapper. It sits above the selected low-level allocator in `sqlite3GlobalConfig.m` and implements public allocation APIs, memory usage accounting, soft and hard heap limits, memory pressure handling, per-connection lookaside-aware allocation helpers, string duplication helpers, and connection-level OOM state propagation. The low-level allocator files (`mem0.c`, `mem1.c`, `mem2.c`, `mem3.c`, `mem5.c`, or platform-specific alternatives) provide `sqlite3_mem_methods`; this file enforces SQLite API semantics and integrates allocation with status counters and database-handle error state.

## Important APIs, Types, And Functions

Public APIs implemented here include `sqlite3_release_memory`, `sqlite3_soft_heap_limit64`, `sqlite3_soft_heap_limit`, `sqlite3_hard_heap_limit64`, `sqlite3_memory_used`, `sqlite3_memory_highwater`, `sqlite3_malloc`, `sqlite3_malloc64`, `sqlite3_msize`, `sqlite3_free`, `sqlite3_realloc`, and `sqlite3_realloc64`. Internal allocation APIs include `sqlite3MallocInit`, `sqlite3MallocEnd`, `sqlite3MallocMutex`, `sqlite3HeapNearlyFull`, `sqlite3Malloc`, `sqlite3MallocSize`, `sqlite3DbMallocSize`, `sqlite3DbFreeNN`, `sqlite3DbNNFreeNN`, `sqlite3DbFree`, `sqlite3Realloc`, `sqlite3MallocZero`, `sqlite3DbMallocZero`, `sqlite3DbMallocRaw`, `sqlite3DbMallocRawNN`, `sqlite3DbRealloc`, `sqlite3DbReallocOrFree`, `sqlite3DbStrDup`, `sqlite3DbStrNDup`, `sqlite3DbSpanDup`, `sqlite3SetString`, `sqlite3OomFault`, `sqlite3OomClear`, and `sqlite3ApiExit`.

The central local state is `Mem0Global mem0`, which stores the static memory mutex, soft limit (`alarmThreshold`), hard limit (`hardLimit`), and atomic `nearlyFull` signal. The functions also interact heavily with `sqlite3GlobalConfig.m`, `sqlite3GlobalConfig.bMemstat`, global status counters such as `SQLITE_STATUS_MEMORY_USED`, and per-connection fields including `db->mallocFailed`, `db->lookaside`, `db->pnBytesFreed`, `db->nVdbeExec`, `db->u1.isInterrupted`, and parse error state.

## Control Flow

Initialization starts in `sqlite3MallocInit()`: if no low-level allocator has been configured, it calls `sqlite3MemSetDefault()`, obtains the static memory mutex, normalizes page-cache buffer configuration, and calls the low-level allocator's `xInit`. Shutdown calls `xShutdown` and clears `mem0`.

`sqlite3Malloc()` filters zero and oversized requests, then either enters `mem0.mutex` and calls `mallocWithAlarm()` with accounting enabled or calls `xMalloc` directly when memstatus is disabled. `mallocWithAlarm()` rounds through `xRoundup`, updates highwater request size, checks the soft threshold, releases cache memory if needed, enforces the hard heap limit, calls `xMalloc`, and updates memory-used and allocation-count status counters. Reallocation follows the same pattern in `sqlite3Realloc()`: NULL and zero sizes are normalized to malloc/free behavior, size is rounded, the hard limit is checked against growth, `xRealloc` is invoked, and memory-used counters are adjusted by the size delta.

Per-connection allocation flows through `sqlite3DbMallocRawNN()`. If lookaside is enabled and the request fits, it pops from the small or full-size lookaside freelists or initial slot lists. Otherwise it calls `dbMallocRawFinish()`, which uses heap allocation and marks `sqlite3OomFault(db)` on failure. Freeing through `sqlite3DbFreeNN()` pushes lookaside blocks back to the correct freelist, optionally accumulates size into `db->pnBytesFreed`, or marks the allocation as heap and calls `sqlite3_free()`. Reallocation preserves lookaside pointers when the new size still fits; otherwise it copies out of lookaside into a new block or delegates heap reallocation.

OOM handling is connection-sticky. `sqlite3OomFault()` sets `db->mallocFailed`, interrupts active VDBEs, disables lookaside, and records parse errors. Later allocations on the same connection fail consistently until `sqlite3OomClear()` runs when no VDBEs are executing. `sqlite3ApiExit()` maps pending OOM or `SQLITE_IOERR_NOMEM` into `SQLITE_NOMEM_BKPT` and updates the connection error.

## State And Persistence Behavior

This file has no on-disk persistence, but it strongly affects persistent database operations by deciding whether page-cache memory can be released and whether VDBEs must be interrupted. The global soft heap limit triggers `sqlite3_release_memory()`, which delegates to pcache memory release when `SQLITE_ENABLE_MEMORY_MANAGEMENT` is enabled. The hard heap limit prevents growth before calling the low-level allocator. Status counters persist for the lifetime of the process or until reset through status APIs. Per-connection OOM state persists across calls until the API boundary clears it, deliberately making allocation failure ordering predictable within one database handle.

Lookaside slots are transient connection-local memory pools. Their freelists are not persisted, but their state must remain consistent across parser, VDBE, schema, and extension allocations. `db->pnBytesFreed` supports measurement-only passes where freeing records sizes rather than releasing memory.

## Dependencies And Integration Points

`malloc.c` depends on `sqliteInt.h`, low-level `sqlite3_mem_methods`, mutexes, atomic helpers, status counters, pcache memory release, debug memory typing (`sqlite3Memdebug*`), lookaside macros and types, VDBE interruption state, parser error reporting, and public initialization. It is invoked by nearly every SQLite subsystem, including btree, pager, parser, VDBE, schema, extension loading, URI parsing, and string formatting.

## Risks And Edge Cases

Risks concentrate around accounting correctness and OOM semantics. If a low-level allocator's `xSize` or `xRoundup` is inconsistent, global memory counters and hard-limit decisions become wrong. The hard-limit checks use current memory status before allocation/reallocation; stale status counters can reject or allow allocations incorrectly. Realloc failure must leave the original allocation valid. Lookaside pointer range checks must distinguish small slots, full slots, and heap blocks exactly, especially with two-size lookaside enabled. `sqlite3OomFault()` must avoid marking benign malloc failures as fatal. `sqlite3ApiExit()` requires the connection mutex; calling it outside that contract is unsafe. Oversized `u64` requests must be blocked before conversion to signed `int`.

## Test Signals

Useful tests include public malloc/realloc/free semantics for zero, NULL, oversized, and same-size requests; status counter and highwater updates; soft heap limit release behavior; hard heap limit rejection; OOM fault injection with sticky `db->mallocFailed`; parser/VDBE interruption on OOM; lookaside allocation, fallback, free, resize, and reconfigure-busy behavior; `sqlite3DbReallocOrFree()` ownership transfer on failure; `sqlite3_msize()` accuracy; benign malloc sections; and debug memory type assertions for heap versus lookaside allocations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem0.c -->
# sources/storage-engines/sqlite/src/mem0.c

## Purpose

`mem0.c` provides a no-op low-level allocator for builds compiled with `SQLITE_ZERO_MALLOC`. It is intentionally nonfunctional: every allocation and reallocation fails, size queries return zero, and free/shutdown calls do nothing. Its role is to provide placeholder `sqlite3_mem_methods` so an application can install a real allocator through `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)` before `sqlite3_initialize()`.

## Important APIs, Types, And Functions

All allocator methods are static except `sqlite3MemSetDefault()`. The method table contains `sqlite3MemMalloc`, `sqlite3MemFree`, `sqlite3MemRealloc`, `sqlite3MemSize`, `sqlite3MemRoundup`, `sqlite3MemInit`, and `sqlite3MemShutdown`. `sqlite3MemSetDefault()` builds a static `sqlite3_mem_methods` object and passes it to `sqlite3_config(SQLITE_CONFIG_MALLOC, &defaultMethods)`.

## Control Flow

The file is compiled only under `SQLITE_ZERO_MALLOC`. If selected as the default allocator, `sqlite3MallocInit()` in `malloc.c` eventually calls `sqlite3MemSetDefault()`, causing the global allocator table to point at these stubs. Initialization returns `SQLITE_OK`, so the library can initialize structurally, but any actual heap request through `sqlite3Malloc()` or public `sqlite3_malloc()` receives NULL. Because allocation failure is immediate and universal, ordinary SQLite operation cannot proceed unless the host application replaces the allocator first.

## State And Persistence Behavior

There is no allocator-local state and no persistent data. `xRoundup` returns the requested size unchanged, but `xMalloc` and `xRealloc` never reserve memory. Since no allocation succeeds, there is no ownership to track and `xFree` is a no-op. SQLite global state may still record the method table, but no memory pool, freelist, or size metadata exists in this module.

## Dependencies And Integration Points

The only dependency is `sqliteInt.h` for SQLite types, `sqlite3_mem_methods`, constants, and `sqlite3_config()`. The integration point is the same low-level allocator contract used by all allocator backends. This file relies on the higher-level allocator wrapper in `malloc.c` to handle public API semantics, status counters, and OOM propagation.

## Risks And Edge Cases

The intended risk is explicit: if an application builds with `SQLITE_ZERO_MALLOC` and forgets to configure a usable allocator before initialization, nearly all SQLite operations fail with OOM symptoms. Because `xInit` returns success, failure is deferred until the first allocation. `xSize` returning zero is only safe because no valid allocation can originate from this allocator. This backend is unsuitable for production by itself.

## Test Signals

Tests should verify that a `SQLITE_ZERO_MALLOC` build can accept a replacement allocator via `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)` before initialization and that leaving the placeholder installed causes allocation APIs to return NULL without crashing. It is also useful to assert that `sqlite3MemSetDefault()` registers exactly these stubs and that repeated free/shutdown calls are harmless.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem1.c -->
# sources/storage-engines/sqlite/src/mem1.c

## Purpose

`mem1.c` is SQLite's default low-level allocator for `SQLITE_SYSTEM_MALLOC` builds. It adapts platform memory allocation APIs to the `sqlite3_mem_methods` contract used by `malloc.c`. On most systems it wraps standard `malloc`, `realloc`, and `free`; on supported Apple builds it can use malloc zones; on platforms without a usable allocation-size API it stores the requested size in an 8-byte header preceding each returned allocation.

## Important APIs, Types, And Functions

The allocator methods are `sqlite3MemMalloc`, `sqlite3MemFree`, `sqlite3MemSize`, `sqlite3MemRealloc`, `sqlite3MemRoundup`, `sqlite3MemInit`, and `sqlite3MemShutdown`, installed by the externally visible `sqlite3MemSetDefault()`. Platform macros map to `SQLITE_MALLOC`, `SQLITE_FREE`, `SQLITE_REALLOC`, and optionally `SQLITE_MALLOCSIZE`. The file conditionally uses Apple `malloc_zone_*`, GLIBC-style `malloc_usable_size`, or MSVC `_msize`.

## Control Flow

When no custom allocator, memdebug allocator, Win32 allocator, or fixed heap allocator is selected, `sqlite3MallocInit()` calls `sqlite3MemSetDefault()`, which registers this backend. Allocation calls are guaranteed by the higher layer to have `nByte > 0`. If a platform usable-size function exists, `sqlite3MemMalloc()` directly allocates `nByte` bytes and `sqlite3MemSize()` asks the platform for the usable size. Without such a function, it allocates `nByte + 8`, stores `nByte` in the leading `sqlite3_int64`, and returns the pointer after the header. Freeing and reallocating reverse that header offset. Reallocation similarly relies on the higher layer to pass non-NULL pointers and rounded positive sizes.

`sqlite3MemInit()` performs Apple-specific zone setup. On multi-core systems it uses the default zone; on single-core systems it creates a dedicated SQLite heap zone to reduce global allocator lock contention. Non-Apple initialization is effectively a no-op. Shutdown does not destroy the Apple zone in this code path and otherwise just consumes the unused argument.

## State And Persistence Behavior

The only allocator-local state is the Apple `_sqliteZone_` pointer. Non-Apple system allocator state is owned by the C runtime. If `SQLITE_MALLOCSIZE` is unavailable, each allocation carries an 8-byte persistent header until free/realloc. There is no on-disk persistence. Memory size reporting feeds the higher-level status counters in `malloc.c`, so correctness of `xSize` is essential for soft/hard heap limits and `sqlite3_memory_used()`.

## Dependencies And Integration Points

This file depends on `sqliteInt.h`, the C runtime allocator, optional `<malloc.h>`, Apple `<malloc/malloc.h>` and `<sys/sysctl.h>`, and SQLite logging through `sqlite3_log()` on allocation failure. It plugs into `sqlite3GlobalConfig.m` through `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)`. It is normally used beneath `malloc.c`, which serializes and accounts allocations when memstatus is enabled.

## Risks And Edge Cases

The fallback header mode requires returned pointers to stay 8-byte aligned and requires all frees/reallocs to be passed pointers created by this allocator. Header corruption breaks `xSize` and can cascade into memory accounting failures. Platform usable-size functions may return a usable size larger than requested; higher layers rely on this value for accounting and msize. Apple zone selection is process-global and must be initialized once. Reallocation failure logs the old and new sizes and must leave the original pointer valid. Compile-time detection of `malloc_usable_size` and `_msize` must match headers and runtime ABI.

## Test Signals

Tests should exercise malloc/realloc/free through public SQLite APIs with memstatus on and off, confirm 8-byte alignment, validate `sqlite3_msize()` and memory-used counters, force realloc growth and shrink paths, check OOM logging/fault simulation, and run under platform configurations with and without `SQLITE_MALLOCSIZE`. Apple builds should cover zone initialization paths where feasible.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem2.c -->
# sources/storage-engines/sqlite/src/mem2.c

## Purpose

`mem2.c` implements SQLite's debug low-level allocator for `SQLITE_MEMDEBUG` builds. It wraps each allocation with guard words, optional title text, optional backtrace storage, allocation type metadata, linked-list tracking of outstanding allocations, randomized fill patterns, and allocation-size statistics. Its purpose is to expose leaks, buffer overruns, use-after-free, incorrect allocation type use, and stale pointer assumptions during development and tests.

## Important APIs, Types, And Functions

The key metadata type is `struct MemBlockHdr`, which records requested size, doubly linked list pointers, backtrace counts, title size, allocation type (`MEMTYPE_HEAP`, `MEMTYPE_LOOKASIDE`, or related masks), and a foreguard. A rear guard word follows the rounded allocation. Static methods include `adjustStats`, `sqlite3MemsysGetHeader`, `sqlite3MemSize`, `sqlite3MemInit`, `sqlite3MemShutdown`, `sqlite3MemRoundup`, `randomFill`, `sqlite3MemMalloc`, `sqlite3MemFree`, and `sqlite3MemRealloc`. Externally visible debug helpers include `sqlite3MemSetDefault`, `sqlite3MemdebugSetType`, `sqlite3MemdebugHasType`, `sqlite3MemdebugNoType`, `sqlite3MemdebugBacktrace`, `sqlite3MemdebugBacktraceCallback`, `sqlite3MemdebugSettitle`, `sqlite3MemdebugSync`, `sqlite3MemdebugDump`, and `sqlite3MemdebugMallocCount`.

Global allocator state is grouped in `mem`: mutex, outstanding allocation list head/tail, backtrace depth and callback, title buffer, allocation-disallow counter, and per-size allocation/current/highwater arrays.

## Control Flow

Allocation enters `sqlite3MemMalloc()`, takes the debug allocator mutex, asserts allocations are currently allowed, rounds the request to 8 bytes, computes total bytes for title, backtrace slots, header, payload, and rear guard, then calls system `malloc`. On success it links the header onto the outstanding list, stores guard words and metadata, captures a GLIBC backtrace if enabled, copies title text, updates size-class statistics, fills the user payload with pseudo-random data, fills rounded padding bytes with `0x65`, and returns the payload pointer.

Freeing calls `sqlite3MemsysGetHeader()` first, which validates foreguard, rear guard, and padding bytes. It then unlinks the header from the outstanding list, updates statistics, overwrites the entire allocation record with pseudo-random bytes, and calls system `free`. Reallocation always allocates a new block, copies the overlap, random-fills any growth, and frees the old block. This deliberately makes stale uses of the old pointer more likely to fail.

Debug type APIs only inspect or mutate headers when the active allocator's `xFree` is this module's `sqlite3MemFree`; otherwise they return permissive results so asserts remain valid with other allocators. Dump APIs walk outstanding allocations and optionally print captured backtraces and size-class counts.

## State And Persistence Behavior

There is no disk persistence. In-process state persists until shutdown or process exit: outstanding allocations remain on a linked list for leak reporting, size-class counters accumulate allocation attempts and current/highwater usage, title text applies to subsequent allocations, and backtrace settings affect future allocations. Each allocation stores its own metadata and guard words for lifetime validation.

## Dependencies And Integration Points

This file depends on `sqliteInt.h`, system `malloc/free`, `<stdio.h>`, optional GLIBC `backtrace` APIs, SQLite mutexes, and SQLite memory debug type constants. It integrates beneath `malloc.c` as the selected `sqlite3_mem_methods` backend. Higher-level code uses `sqlite3MemdebugSetType/HasType/NoType` in assertions to distinguish heap and lookaside ownership.

## Risks And Edge Cases

Because this allocator asserts on corruption, it is intended for testing, not graceful production recovery. Incorrect mutex assumptions can occur when `sqlite3GlobalConfig.bMemstat` means the higher wrapper already holds the static memory mutex; `sqlite3MemInit()` accounts for that by only allocating its own mutex when needed. Backtrace depth is capped and rounded, so callers should not assume arbitrary depth. Padding checks only catch writes into rounded slack or guard words, not all intra-buffer logic errors. `sqlite3MemdebugSync()` assumes a backtrace callback is installed. Realloc always moving memory can expose stale pointers but also changes performance and fragmentation characteristics compared with production allocators.

## Test Signals

Test signals include intentional guard corruption assertions, leak dump output containing outstanding allocations and titles, backtrace callback invocation, malloc count growth, allocation type assertions for heap/lookaside transitions in `malloc.c`, randomized fill exposing uninitialized reads, freed-memory fill exposing use-after-free, and realloc movement exposing stale old-pointer use. Debug test suites should run with `SQLITE_MEMDEBUG` and both memstatus modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem3.c -->
# sources/storage-engines/sqlite/src/mem3.c

## Purpose

`mem3.c` implements the optional `SQLITE_ENABLE_MEMSYS3` fixed-heap allocator. It avoids system `malloc()` after initialization by allocating from a caller-supplied heap configured with `SQLITE_CONFIG_HEAP`. The allocator uses 8-byte `Mem3Block` units, boundary-tag chunk headers, exact small freelists, hashed larger freelists, and a special "key chunk" that tracks the largest free region for efficient tail carving.

## Important APIs, Types, And Functions

The core type is `Mem3Block`, whose first block in a chunk stores `prevSize` and `size4x` flags and whose second block stores freelist links when the chunk is free. `Mem3Global mem3` stores the pool pointer and size, alarm reentry guard, mutex, key-chunk index and size, minimum observed key size, small freelist roots (`aiSmall`) and hash freelist roots (`aiHash`). Static helpers include `memsys3UnlinkFromList`, `memsys3Unlink`, `memsys3LinkIntoList`, `memsys3Link`, `memsys3Enter`, `memsys3Leave`, `memsys3OutOfMemory`, `memsys3Checkout`, `memsys3FromKeyBlk`, `memsys3Merge`, `memsys3MallocUnsafe`, `memsys3FreeUnsafe`, `memsys3Size`, `memsys3Roundup`, `memsys3Malloc`, `memsys3Free`, `memsys3Realloc`, `memsys3Init`, and `memsys3Shutdown`. External entry points are `sqlite3Memsys3Dump()` in debug builds and `sqlite3MemGetMemsys3()`, which returns the method table.

## Control Flow

Initialization requires `sqlite3GlobalConfig.pHeap`; otherwise `memsys3Init()` returns `SQLITE_ERROR`. It maps the supplied heap to `mem3.aPool`, computes `nPool`, and initializes one large key chunk covering the pool with sentinel metadata at the end. Allocation converts bytes to a block count, with a minimum two-block chunk. `memsys3MallocUnsafe()` first looks for an exact-size chunk in the small freelist or hashed freelist. If not found, it carves the tail from the key chunk if large enough. If the key chunk is too small, it repeatedly triggers `sqlite3_release_memory()`, temporarily links the key chunk, scans all freelists to coalesce adjacent free chunks via `memsys3Merge()`, selects the largest free chunk as the new key chunk, unlinks it, and tries tail carving again. Failure returns NULL.

Freeing marks the checked-out chunk free, updates boundary tags, links it into the appropriate freelist, and then attempts to expand the key chunk by coalescing adjacent free chunks around the existing key chunk. Reallocation keeps the old pointer when the new size is no larger than the old size and within 128 bytes of it; otherwise it allocates a new chunk, copies the overlap, and frees the old chunk. Size and roundup functions translate between user bytes and internal chunk sizes while omitting the header block overhead.

## State And Persistence Behavior

All allocator state lives inside `mem3` and the caller-provided heap. The heap is fixed after `sqlite3_initialize()`; `sqlite3_config(SQLITE_CONFIG_HEAP, ...)` changes only before initialization. No disk persistence exists. Fragmentation state persists as freelist membership, boundary tags, and key-chunk metadata. Debug dumps can inspect chunk layout, free lists, key chunk, current estimated use, and max use inferred from the minimum key block.

## Dependencies And Integration Points

`mem3.c` depends on `sqliteInt.h`, SQLite mutexes, `sqlite3GlobalConfig.pHeap/nHeap`, `sqlite3_release_memory()`, and the `sqlite3_mem_methods` interface. It is selected by `sqlite3_config(SQLITE_CONFIG_HEAP, ...)` in `main.c` when `SQLITE_ENABLE_MEMSYS3` is compiled. `malloc.c` remains the higher-level wrapper responsible for public API semantics, memory status, and hard/soft limits.

## Risks And Edge Cases

This allocator is pointer-arithmetic intensive. Corrupt boundary tags, incorrect `prevSize`, or wrong checked-out/free bits can break coalescing and freelists. The key chunk is intentionally not normally on a freelist, so code that temporarily links and unlinks it must be exact. The allocation retry loop depends on `sqlite3_release_memory()` and avoids recursive alarms with `alarmBusy`. Heap size must leave at least two sentinel blocks; misconfigured or unaligned heap memory can violate assumptions. Realloc's "within 128 bytes" no-move behavior may leave internal fragmentation. The allocator is not selected merely by compiling it; it must be configured.

## Test Signals

Useful tests include configuring a fixed heap and verifying allocations proceed without system malloc, exact small-size freelist reuse, large hash-list reuse, key-chunk tail carving, coalescing after frees, allocation failure after exhausting the heap, retry after page-cache memory release, realloc no-move and move paths, debug dump consistency checks, and status accounting through the higher `malloc.c` layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem5.c -->
# sources/storage-engines/sqlite/src/mem5.c

## Purpose

`mem5.c` implements the optional `SQLITE_ENABLE_MEMSYS5` fixed-heap allocator. Like memsys3, it serves allocations from memory supplied by `SQLITE_CONFIG_HEAP`, but it uses a buddy-allocation algorithm: request sizes are rounded to powers of two, blocks are split from larger free blocks, and adjacent free buddies are coalesced when freed. The file cites Robson's fragmentation bound and records debug/test statistics needed to evaluate allocator behavior.

## Important APIs, Types, And Functions

The minimum allocation unit is `Mem5Link`, used as the in-pool linked-list node for free blocks. `Mem5Global mem5` stores the atom size, block count, pool pointer, mutex, debug/test allocation statistics, power-of-two freelist roots (`aiFreelist`), and one-byte-per-block control array (`aCtrl`). Control bytes store `CTRL_LOGSIZE` and `CTRL_FREE`. Helper macros and functions include `MEM5LINK`, `memsys5Unlink`, `memsys5Link`, `memsys5Enter`, `memsys5Leave`, `memsys5Size`, `memsys5MallocUnsafe`, `memsys5FreeUnsafe`, `memsys5Malloc`, `memsys5Free`, `memsys5Realloc`, `memsys5Roundup`, `memsys5Log`, `memsys5Init`, and `memsys5Shutdown`. External entry points are `sqlite3Memsys5Dump()` under `SQLITE_TEST` and `sqlite3MemGetMemsys5()`.

## Control Flow

Initialization disables the mutex temporarily, reads `sqlite3GlobalConfig.pHeap`, `nHeap`, and `mnReq`, computes `szAtom` as a power of two large enough for both the configured minimum request and `Mem5Link`, divides the heap between payload atoms and the control array, clears freelists, then decomposes the available block count into free power-of-two chunks from largest to smallest. If memstatus is disabled, it allocates its own static memory mutex.

Allocation rejects requests above 1 GiB, records max request in debug/test builds, rounds up from `szAtom` to the next power-of-two full size, finds the first freelist at that size or larger, unlinks one larger block, repeatedly splits it while linking the right-hand buddies onto smaller freelists, marks the selected block checked out, updates allocation statistics, optionally fills memory with `0xAA`, and returns the pool pointer. Freeing marks the block free, updates current stats, finds the buddy based on block index and log size, coalesces while the buddy is free and the same size, fills freed memory with `0x55` in debug builds, and links the final coalesced block. Realloc keeps the same pointer when the new rounded size fits in the existing block; otherwise it allocates, copies, and frees.

## State And Persistence Behavior

There is no on-disk persistence. The allocator state persists in the supplied heap and in `mem5`: freelist roots, block control bytes, current and highwater stats, and maximum request. The fixed heap cannot be resized after initialization. The control array is stored at the end of the same supplied memory region after the atom pool, so heap sizing directly controls both usable memory and metadata capacity.

## Dependencies And Integration Points

`mem5.c` depends on `sqliteInt.h`, SQLite global heap configuration, mutexes, `sqlite3_log()` for allocation failure logging, and the `sqlite3_mem_methods` interface. It is selected by `sqlite3_config(SQLITE_CONFIG_HEAP, ...)` in `main.c` when `SQLITE_ENABLE_MEMSYS5` is compiled. The higher `malloc.c` layer performs public API normalization, accounting, soft/hard heap limit behavior, and OOM propagation around these low-level methods.

## Risks And Edge Cases

Internal fragmentation is expected because every request rounds to a power of two. The configured minimum request (`mnReq`) and `sizeof(Mem5Link)` determine `szAtom`; too large a minimum wastes memory, while too small is rounded up. The 1 GiB allocation ceiling returns zero from `memsys5Roundup()` or `memsys5MallocUnsafe()`. Control-byte corruption can make free coalescing unsafe. Buddy coalescing depends on correct block alignment and log-size metadata. Debug/test statistics are compile-conditional, so production code cannot rely on dump counters. As with memsys3, compiling the allocator does not activate it unless heap configuration selects it.

## Test Signals

Tests should cover fixed-heap initialization with different `mnReq` values, power-of-two rounding, split allocation from larger blocks, exact freelist reuse, buddy coalescing across free order permutations, oversize allocation rejection, realloc no-move and growth-copy paths, debug memory fill patterns, `sqlite3Memsys5Dump()` freelist/stat output in test builds, and end-to-end memory status through `malloc.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/mem5.c -->
