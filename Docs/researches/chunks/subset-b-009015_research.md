# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 22526-30978

## Scope

This chunk covers a large core-runtime segment of SQLite's amalgamated `sqlite3.c`, starting in the compile-option diagnostics table and ending at the first line of `mallocWithAlarm()` in the front-end allocator wrapper. The amalgamated source sections included here are:

- Tail of `ctime.c`: compile-time option name emission and `sqlite3CompileOptions()`.
- `global.c`: process-wide constants, character lookup tables, default configuration, opcode/type metadata, and tracing globals.
- `status.c`, including the embedded `vdbeInt.h`: VDBE private structures and global/database status accounting.
- `date.c`: SQLite's SQL date/time parser, modifier engine, date/time scalar functions, fallback current-time functions, and registration hook.
- `os.c`: common `sqlite3_file` and `sqlite3_vfs` wrappers, test fault injection points, VFS registry management.
- `fault.c`: benign malloc failure hooks.
- `mem0.c`, `mem1.c`, `mem2.c`, `mem3.c`, `mem5.c`: low-level allocator backends selected by compile-time configuration.
- `mutex.c`, `mutex_noop.c`, `mutex_unix.c`, `mutex_w32.c`, and embedded `os_win.h`: mutex method selection and platform mutex implementations.
- Start of `malloc.c`: public heap-limit APIs, allocator initialization/shutdown, memory-use status APIs, and alarm entrypoint.

The range is third-party SQLite code vendored under WiredTiger's test tree. It is not a WiredTiger storage engine path; it supplies SQLite runtime behavior for the vendored SQLite test/tooling environment.

## Purpose

The common theme is SQLite process infrastructure: how the library reports its build shape, initializes global defaults, parses built-in date/time functions, routes abstract OS/VFS calls, chooses and instruments memory allocators, chooses and instruments mutex implementations, and exposes memory status and limits.

Within the SQLite core, this code sits below SQL compilation/execution and above platform/runtime services. Higher layers call these helpers rather than calling `malloc()`, `pthread_mutex_*`, Win32 `CRITICAL_SECTION`, `localtime()`, or VFS methods directly. That centralization lets SQLite add compile-time feature gates, fault injection, status counters, memory-pressure handling, and portability shims without scattering platform-specific logic through the pager, btree, VDBE, parser, and extension code.

## Important APIs, Types, and Functions

- `sqlite3CompileOptions(int *pnOpt)`: returns the static `sqlite3azCompileOpt` array of compile-option strings generated through many `#ifdef` branches. This backs compile-option diagnostics when `SQLITE_OMIT_COMPILEOPTION_DIAGS` is not set.
- `sqlite3UpperToLower`, `sqlite3CtypeMap`, `sqlite3aLTb`, `sqlite3aEQb`, `sqlite3aGTb`: global lookup tables for ASCII/EBCDIC folding, SQLite-specific character classification, and comparison-opcode truth tables.
- `sqlite3Config`: the global `Sqlite3Config` singleton. It captures default mutex, allocator, page-cache, mmap, URI, lookaside, sorter, statement-journal, localtime, test, and debug-tuning defaults used during `sqlite3_initialize()` and configuration.
- `sqlite3BuiltinFunctions`, `sqlite3PendingByte`, `sqlite3TreeTrace`, `sqlite3WhereTrace`, `sqlite3OpcodeProperty`, `sqlite3StrBINARY`, `sqlite3StdType*`: global function registry and constants shared by parser, VDBE, pager, planner, and type-affinity code.
- `VdbeCursor`, `VdbeFrame`, `Mem`/`sqlite3_value`, `sqlite3_context`, `ScanStatus`, `DblquoteStr`, `Vdbe`, `PreUpdate`, `ValueList`: private VDBE data structures pulled into `status.c` by amalgamation. They define cursor state, VM frames, SQL value representation, function-call contexts, scan-status records, normalized-SQL double-quote tracking, statement lifecycle state, pre-update hook state, and value-list cleanup state.
- `sqlite3_status64()`, `sqlite3_status()`, `sqlite3_db_status()`, `sqlite3StatusUp()`, `sqlite3StatusDown()`, `sqlite3StatusHighwater()`, `sqlite3StatusValue()`, `sqlite3LookasideUsed()`: status APIs and internal counter mutators for global memory/page-cache/parser metrics and per-connection lookaside, cache, schema, statement, pager, and foreign-key metrics.
- `DateTime` plus `parseDateOrTime()`, `parseModifier()`, `isDate()`, `computeJD()`, `computeYMD()`, `computeHMS()`, `toLocaltime()`: the internal state machine for SQL date/time conversion. `iJD` is Julian day in milliseconds; validity flags track whether YMD/HMS/JD/raw numeric state is current.
- Date/time SQL functions: `juliandayFunc()`, `unixepochFunc()`, `datetimeFunc()`, `timeFunc()`, `dateFunc()`, `strftimeFunc()`, `timediffFunc()`, `ctimeFunc()`, `cdateFunc()`, `ctimestampFunc()`, fallback `currentTimeFunc()`, and debug-only `datedebugFunc()`.
- `sqlite3RegisterDateTimeFunctions()`: inserts the date/time built-ins into the global function table.
- OS wrappers: `sqlite3OsClose()`, `sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsSync()`, `sqlite3OsOpen()`, `sqlite3OsDelete()`, `sqlite3OsAccess()`, `sqlite3OsFullPathname()`, shared-memory wrappers, mmap `sqlite3OsFetch()/sqlite3OsUnfetch()`, dynamic-library wrappers, randomness/sleep/current-time wrappers, and `sqlite3OsOpenMalloc()/sqlite3OsCloseFree()`.
- VFS registry APIs: `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, `sqlite3_vfs_unregister()`, plus internal `vfsUnlink()`.
- Fault hooks: `sqlite3BenignMallocHooks()`, `sqlite3BeginBenignMalloc()`, `sqlite3EndBenignMalloc()`.
- Allocator backend method providers: `sqlite3MemSetDefault()` for zero/system/debug allocators, `sqlite3MemGetMemsys3()`, `sqlite3MemGetMemsys5()`, plus backend-specific malloc/free/realloc/size/roundup/init/shutdown methods.
- Debug allocator APIs: `sqlite3MemdebugSetType()`, `sqlite3MemdebugHasType()`, `sqlite3MemdebugNoType()`, `sqlite3MemdebugBacktrace()`, `sqlite3MemdebugBacktraceCallback()`, `sqlite3MemdebugSettitle()`, `sqlite3MemdebugSync()`, `sqlite3MemdebugDump()`, `sqlite3MemdebugMallocCount()`.
- Mutex front-end APIs: `sqlite3MutexInit()`, `sqlite3MutexEnd()`, `sqlite3_mutex_alloc()`, `sqlite3MutexAlloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, debug `sqlite3_mutex_held()` and `sqlite3_mutex_notheld()`, and optional `sqlite3MutexWarnOnContention()`.
- Mutex method providers: `sqlite3NoopMutex()`, `sqlite3DefaultMutex()` for pthread or Win32 builds, and `multiThreadedCheckMutex()` when multithreaded checks are enabled.
- Malloc front-end APIs at the end of the chunk: `sqlite3_release_memory()`, `sqlite3_memory_alarm()`, `sqlite3_soft_heap_limit64()`, `sqlite3_soft_heap_limit()`, `sqlite3_hard_heap_limit64()`, `sqlite3MallocInit()`, `sqlite3HeapNearlyFull()`, `sqlite3MallocEnd()`, `sqlite3_memory_used()`, `sqlite3_memory_highwater()`, `sqlite3MallocAlarm()`, `test_oom_breakpoint()`, and the opening of `mallocWithAlarm()`.

## Control Flow

Compile-option diagnostics are built entirely at compile time. Each enabled compile flag contributes a string literal to `sqlite3azCompileOpt`; `sqlite3CompileOptions()` simply stores the array length through `pnOpt` and returns the array.

`global.c` establishes immutable lookup tables and the initial `sqlite3Config` contents before any runtime initialization. Later `sqlite3_config()` calls can replace parts of `sqlite3Config` before `sqlite3_initialize()`, but the defaults here determine normal embedded behavior: URI filenames off unless requested, covering-index scans on, lookaside defaults, statement-journal spill threshold, mmap limits, page-cache defaults, and memory allocator/mutex placeholders.

The status subsystem stores current and high-water counters in `sqlite3Stat`. Each status category is mapped to either the malloc mutex or the pcache mutex through `statMutex[]`. Internal code mutates counters only while holding the proper mutex, and public `sqlite3_status64()` selects the same mutex, copies current/high-water values, and optionally resets the high-water mark to the current value.

`sqlite3_db_status()` runs under the database connection mutex and dispatches by `op`. Lookaside counters are derived from free/init slot lists, lookaside hit/miss counters are read and optionally reset, cache memory walks all attached btrees/pagers, schema and prepared-statement memory are measured by temporarily redirecting destructor paths to count freed bytes without truly freeing live state, pager cache statistics are accumulated per attached database, and deferred foreign-key status is read from connection counters.

The date/time path starts with `isDate()`. It initializes a `DateTime`, parses the first argument as current time, numeric Julian/unix candidate, ISO-like text, time-only text, `now`, or `subsec`, then applies each modifier through `parseModifier()`. Modifiers can reinterpret raw numeric values (`auto`, `unixepoch`, `julianday`), adjust calendar/time values (`+NNN days`, `+YYYY-MM-DD`, `+HH:MM:SS`), resolve month overflow (`ceiling`, `floor`), snap to boundaries (`start of month/year/day`), move to a weekday, shift between UTC and local time, or request subsecond output. After modifiers, `computeJD()` normalizes to a validated Julian-day millisecond value. Output functions then convert that canonical value into numeric, text, or formatted results.

The OS layer is a thin dispatch layer over `sqlite3_file` and `sqlite3_vfs` method tables. It applies test OOM injection before selected I/O calls, normalizes behavior such as `xSync` with zero flags returning `SQLITE_OK`, falls back from `xCurrentTimeInt64` to `xCurrentTime`, masks open flags before passing them to VFS `xOpen`, and maintains a process-global linked list of registered VFS implementations under the static main mutex.

The low-level allocator backend is selected by compile-time macros or explicit configuration. `SQLITE_ZERO_MALLOC` installs no-op methods that always fail allocation. `SQLITE_SYSTEM_MALLOC` wraps system malloc/realloc/free and either uses platform usable-size APIs or stores an 8-byte size header. `SQLITE_MEMDEBUG` wraps system allocation with headers, guard words, backtrace/title metadata, randomized fill, active-allocation lists, and counters. `SQLITE_ENABLE_MEMSYS3` exposes a fixed-pool allocator based on variable-sized chunks and freelists/hash buckets. `SQLITE_ENABLE_MEMSYS5` exposes a fixed-pool buddy allocator where allocation sizes round to powers of two and adjacent buddies coalesce on free.

Mutex initialization first copies a method table into `sqlite3GlobalConfig.mutex` if one was not supplied through configuration. If core mutexes are disabled, it selects the no-op provider. If enabled, it selects the platform default provider or the multithreaded-check wrapper. After copying all function pointers except `xMutexAlloc`, it issues a memory barrier and installs `xMutexAlloc` last, making partially initialized method tables less visible to racing readers. Allocation and enter/leave public APIs then dispatch through that method table.

The pthread provider uses static mutex objects for `SQLITE_MUTEX_STATIC_*`, dynamic allocations for fast/recursive mutexes, optional native recursive mutex attributes, and optional home-grown recursive tracking. The Win32 provider explicitly initializes static `CRITICAL_SECTION` objects during `winMutexInit()`, uses interlocked state to serialize initialization/shutdown, and uses `TryEnterCriticalSection()` only when available on NT-class builds. Debug builds in both providers track owner/refcount and assert correct recursive versus non-recursive use.

The start of `malloc.c` is the allocator front-end around whichever backend was selected. `sqlite3MallocInit()` installs defaults if no allocator exists, obtains the static memory mutex, validates page-cache backing memory, and calls the selected backend `xInit`. Heap-limit APIs update `mem0.alarmThreshold`, `mem0.hardLimit`, and `mem0.nearlyFull` under the malloc mutex, then try to release page-cache memory if current usage exceeds the new soft limit. `sqlite3_memory_used()` and `sqlite3_memory_highwater()` are small wrappers over `sqlite3_status64(SQLITE_STATUS_MEMORY_USED, ...)`.

## State and Persistence Behavior

Most state in this chunk is process-global SQLite runtime state:

- `sqlite3Config` persists across the process and drives initialization, unless reset by shutdown/reconfiguration paths outside this chunk.
- `sqlite3BuiltinFunctions` becomes the read-only built-in SQL function registry after initialization.
- `sqlite3PendingByte` is a global database-file format parameter; changing it through test controls creates incompatible file layouts and is only for testing.
- `sqlite3TreeTrace`, `sqlite3WhereTrace`, coverage counters, profile counters, I/O fault counters, diskfull counters, and open-file counters are test/debug globals.
- `sqlite3Stat` stores global status counters and high-water marks; public reset only lowers high-water values to current values, not current usage.
- `vfsList` is a global linked list of VFS implementations. Registration order matters because the head is the default VFS.
- Allocator global structs (`mem`, `mem3`, `mem5`, `mem0`) hold active heap accounting, fixed-pool state, debug allocation lists, and heap limit state.
- Mutex static arrays in no-op/debug/pthread/Win32 providers hold process-global static mutex objects.

Database-file persistence is indirect. The date/time, status, mutex, and allocator sections do not themselves write database pages. The OS wrapper section dispatches all VFS file writes, syncs, truncates, deletes, shared-memory operations, and file controls used by pager and WAL code elsewhere. That makes it a persistence boundary: failures, flag masking, mmap availability, VFS registration order, and test fault injection here affect durability and recovery semantics elsewhere.

The date/time functions are mostly stateless. The exception is "current" time, which reads statement time through `sqlite3StmtCurrentTime()` and the active VFS time method, and local-time conversion, which depends on C library timezone behavior or test-supplied localtime fault hooks.

## Dependencies and Integration Points

This chunk depends on many SQLite internal subsystems defined outside the range: mutex and allocator configuration structures, pager/btree APIs, pcache mutexes, VDBE deletion and memory routines, hash-table iterators, schema/table/trigger destructors, SQL function registration, `sqlite3StmtCurrentTime()`, string accumulators, public `sqlite3_value_*` and `sqlite3_result_*` helpers, VFS/file method tables, and public initialization/configuration routines.

Compile-time flags are major integration points. The behavior in this range changes significantly under `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_DATETIME_FUNCS`, `SQLITE_OMIT_LOCALTIME`, `SQLITE_UNTESTABLE`, `SQLITE_TEST`, `SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_ZERO_MALLOC`, `SQLITE_SYSTEM_MALLOC`, `SQLITE_MEMDEBUG`, `SQLITE_ENABLE_MEMSYS3`, `SQLITE_ENABLE_MEMSYS5`, `SQLITE_MUTEX_OMIT`, `SQLITE_MUTEX_NOOP`, `SQLITE_MUTEX_PTHREADS`, `SQLITE_MUTEX_W32`, `SQLITE_ENABLE_MULTITHREADED_CHECKS`, `SQLITE_HOMEGROWN_RECURSIVE_MUTEX`, `SQLITE_ENABLE_API_ARMOR`, Windows platform macros, Apple zone-malloc macros, and feature flags listed in the compile-option table.

The VFS wrapper functions integrate directly with platform-specific `os_unix.c`, `os_win.c`, and any third-party VFS. The VFS registry is also used by shell/test tooling and by callers that select a named VFS through URI or open flags. `sqlite3OsRandomness()` can be made deterministic through `sqlite3Config.iPrngSeed`, which is important for repeatable tests.

The memory subsystem is layered: backend providers implement `sqlite3_mem_methods`; the front-end in `malloc.c` handles limits, stats, alarms, zero-size and oversized requests, and public APIs. The status subsystem reads memory usage through the same global counters, so allocator changes must preserve expected counter semantics.

The mutex subsystem is similarly layered: platform providers implement `sqlite3_mutex_methods`; `sqlite3MutexInit()` installs one method table globally; all internal mutex use routes through `sqlite3_mutex_*`/`sqlite3MutexAlloc()`. Fixed-pool allocators and status counters depend on the static memory mutex, while VFS registration and localtime fallback use the static main mutex.

Within WiredTiger, the integration concern is vendored SQLite build/test behavior. Changes here would alter SQLite test harness behavior, date/time SQL semantics, allocator and mutex portability, VFS fault injection, and compile-option reporting used by tests.

## Risks and Edge Cases

- The compile-option list is preprocessor-driven. A missing branch can make diagnostics lie about the binary, while an incorrect value macro can expose stale or malformed option strings.
- `sqlite3UpperToLower` also stores comparison truth tables after the 256-byte mapping. Pointer arithmetic depends on comparison opcodes remaining consecutive in the documented `NE EQ GT LE LT GE` order.
- `sqlite3PendingByte` controls a reserved lock byte page in the database file. Moving it outside tests makes files incompatible.
- Status counters rely on callers holding the correct mutex. The public API protects reads, but internal `sqlite3StatusUp/Down/Highwater/Value` assert rather than acquire locks.
- `sqlite3_db_status()` schema and statement memory measurements intentionally run destructors in counting mode. Bugs in `db->pnBytesFreed` handling or lookaside boundary manipulation could corrupt live connection state.
- Date/time parsing accepts flexible modifiers but has strict numeric ranges. Month/year arithmetic tracks `nFloor` for overflow resolution, so changing normalization order can alter `floor`/`ceiling` behavior for dates such as February 31.
- `localtime` conversion maps out-of-range years into a 1970-2038 equivalent before mapping back. This depends on calendar equivalence assumptions and host timezone rules, including DST behavior.
- `utc` conversion iterates at most four guesses to resolve localtime offset. Ambiguous or nonexistent local times around DST transitions are inherently delicate.
- Date/time `now`, `localtime`, `utc`, `subsec`, and `subsecond` are gated through `sqlite3NotPureFunc()` where appropriate. Removing those checks would make non-deterministic functions appear pure.
- OS wrappers use `DO_OS_MALLOC_TEST()` in test builds. Adding a new wrapper without the macro can leave OOM/fault-injection coverage gaps.
- `sqlite3OsOpen()` masks open flags before VFS dispatch. New public open flags must be intentionally added to the mask if they should reach the VFS.
- VFS registration is a linked-list mutation under the static main mutex. Registering the same object unlinks then reinserts it; default VFS order changes if `makeDflt` is true.
- `SQLITE_ZERO_MALLOC` deliberately makes SQLite unusable until a real allocator is configured. Accidentally selecting it in a normal build causes initialization/allocation failure.
- The system allocator path either trusts platform usable-size APIs or stores a private 8-byte prefix. Mixing allocators or freeing pointers not returned by the active backend is fatal.
- The debug allocator has strict guard-word and padding assertions. It also always moves allocations on realloc, intentionally exposing stale-pointer bugs.
- `memsys3` and `memsys5` require fixed heap memory supplied before initialization. Heap size, minimum request size, and alignment errors can make initialization fail or greatly increase fragmentation.
- `memsys3`'s key-block and freelist invariants are subtle: chunk headers encode checked-out and previous-free state in low bits, and coalescing depends on correct tail `prevSize`.
- `memsys5` caps allocations at 1 GiB and rounds to powers of two. Internal fragmentation is expected and tracked in debug/test counters.
- Mutex method installation uses memory barriers and installs `xMutexAlloc` last. Reordering that sequence can expose partially initialized method tables.
- No-op mutexes are only correct for single-threaded operation. Debug no-op mutexes catch misuse but still provide no mutual exclusion.
- Pthread debug owner checks rely on `pthread_equal()` being safe enough for assert-only use; comments call out platforms where this may be unreliable.
- Win32 static mutex initialization uses global interlocked state and waits with `sqlite3_win32_sleep(1)`. Incorrect shutdown ordering could delete static critical sections still in use.
- `sqlite3_soft_heap_limit64()` computes `excess = sqlite3_memory_used() - n` after releasing the mutex. Concurrent allocation/free can make release attempts approximate rather than exact.
- The chunk ends at the start of `mallocWithAlarm()`, so allocation-front-end behavior after alarm triggering continues in the next chunk and should be reconciled there.

## Test Signals

Useful signals for this chunk include:

- Compile-option introspection returns enabled options with expected `NAME` or `NAME=value` strings and correct count from `sqlite3CompileOptions()`.
- Character classification tests cover ASCII/EBCDIC case folding, identifier characters, quote characters, and comparison opcode truth-table assumptions.
- `sqlite3_status64()` returns `SQLITE_MISUSE_BKPT` for invalid ops and resets high-water values only when requested.
- `sqlite3_db_status()` reports lookaside used/high-water, lookaside hit/miss counters, pager cache memory, shared cache memory, schema memory, statement memory, cache hit/miss/write/spill counters, and deferred foreign-key state without changing current connection behavior.
- Date/time SQL tests cover ISO dates, negative years, time-only inputs, numeric Julian days, `now`, `subsec`, `unixepoch`, `auto`, `julianday`, `floor`, `ceiling`, `start of` modifiers, `weekday`, `localtime`, `utc`, large range limits, invalid modifiers returning NULL, `strftime()` conversion codes, `timediff()` invariants, and fallback `CURRENT_TIME/DATE/TIMESTAMP` builds when full datetime support is omitted.
- Localtime tests can use `sqlite3GlobalConfig.bLocaltimeFault` and `xAltLocaltime` in non-untestable builds to force success/failure paths.
- VFS tests verify wrapper delegation, masked open flags, `xCurrentTimeInt64` fallback, deterministic randomness under `iPrngSeed`, mmap stubs when mmap is disabled, `xSync` no-op for zero flags, VFS register/find/unregister order, and test OOM injection through `DO_OS_MALLOC_TEST()`.
- Benign malloc tests verify begin/end hooks are invoked only when `SQLITE_UNTESTABLE` is not defined.
- Allocator tests should run under system malloc, memdebug, memsys3, memsys5, and zero-malloc/custom allocator configurations where applicable. Signals include allocation size reporting, roundup behavior, realloc semantics, OOM logging, guard-word assertions, backtrace/title dumps, fixed-pool initialization failure without `pHeap`, memsys3 coalescing/key-block state, memsys5 buddy splitting/coalescing, and dump counters in debug/test builds.
- Mutex tests should cover no-op single-thread mode, debug misuse assertions, pthread fast/recursive/static mutex allocation, Win32 static initialization/shutdown, `sqlite3_mutex_try()` busy/ok behavior, API-armor invalid static IDs, and multithreaded-check warnings on database-handle contention.
- Heap-limit tests cover querying prior soft/hard values, hard limit constraining soft limit, `sqlite3HeapNearlyFull()` updates, memory-used/high-water wrappers, and `sqlite3_release_memory()` returning zero when `SQLITE_ENABLE_MEMORY_MANAGEMENT` is absent.
