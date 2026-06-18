# subset-b-008799 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_thread.c -->
# sources/storage-engines/sqlite/src/test_thread.c

## Purpose

`test_thread.c` is SQLite testfixture support for exercising database handles and SQLite APIs from Tcl-created threads. It is compiled only when `SQLITE_THREADSAFE` is true. The module registers a `sqlthread` Tcl command that can spawn a child Tcl interpreter in a new Tcl thread, open SQLite connections inside that thread, post scripts back to the parent event queue, and expose thread ids. On Unix builds with `SQLITE_ENABLE_UNLOCK_NOTIFY`, it also registers blocking wrappers around `sqlite3_step()` and `sqlite3_prepare_v2()` to demonstrate and test `sqlite3_unlock_notify()`.

## Important APIs, Types, And Functions

- `SqlThread` carries the parent `Tcl_ThreadId`, parent interpreter, child script, and parent result variable name for `sqlthread spawn`.
- `EvalEvent` subclasses `Tcl_Event` so a child thread can queue a script for evaluation in the parent interpreter.
- `tclScriptEvent()` evaluates queued event scripts and reports errors through `Tcl_BackgroundError()`.
- `postToParent()` copies a Tcl object script into an `EvalEvent` and alerts the parent thread.
- `tclScriptThread()` creates the child interpreter, registers test commands, runs the child script, posts either an error report and then a `set VARNAME result` script back to the parent, and exits the Tcl thread.
- `sqlthread_spawn()`, `sqlthread_parent()`, `sqlthread_open()`, and `sqlthread_id()` implement `sqlthread` subcommands.
- `clock_seconds_proc()` and `clock_milliseconds_proc()` provide testfixture clock commands independent of Tcl library script availability.
- Under Unix unlock-notify builds, `UnlockNotification`, `unlock_notify_cb()`, `wait_for_unlock_notify()`, `sqlite3_blocking_step()`, `sqlite3_blocking_prepare_v2()`, `blocking_step_proc()`, and `blocking_prepare_v2_proc()` implement blocking shared-cache lock waits.
- `SqlitetestThread_Init()` registers all Tcl commands in the parent test interpreter.

## Control Flow

`SqlitetestThread_Init()` installs `sqlthread`, clock helpers, and optionally unlock-notify Tcl commands. `sqlthread_proc()` dispatches validated subcommands. `sqlthread spawn VARNAME SCRIPT` copies both strings into one `ckalloc()` allocation, records the current Tcl thread and interpreter, and starts `tclScriptThread()` using `Tcl_CreateThread()`.

The child thread creates a fresh interpreter, installs SQLite/Tcl test commands (`Sqlitetest1_Init`, mutex tests, `Sqlite3_Init`, and the thread command itself), evaluates the supplied script, then packages the result into Tcl list scripts for the parent. If the script fails, it first posts `error <message>`, then posts `set <varname> <result>` so the parent can `vwait` the variable. The child frees its `SqlThread`, releases Tcl references, deletes its interpreter, drains pending events nonblocking, and calls `Tcl_ExitThread()`.

`sqlthread parent SCRIPT` is a one-way parent event queue helper. The file comments mark it as not currently working for synchronous result return: it queues and alerts the parent but does not wait for or propagate a parent evaluation result.

The unlock-notify path wraps SQLite calls that return `SQLITE_LOCKED`. `sqlite3_blocking_step()` retries `sqlite3_step()` after `wait_for_unlock_notify()` signals a pthread condition variable. `sqlite3_blocking_prepare_v2()` performs the same loop around `sqlite3_prepare_v2()`. Tcl wrappers convert pointer strings to SQLite handles/statements and return `sqlite3ErrName()` strings or statement pointer strings.

## State And Persistence Behavior

The file owns transient Tcl-thread state only. `SqlThread` and `EvalEvent` payloads are heap allocated with Tcl allocators and passed across Tcl thread queues. Results persist only as Tcl variables in the parent interpreter, not in SQLite database state.

`sqlthread_open()` creates a real SQLite connection, registers the MD5 extension function, and installs a busy handler that sleeps 50 ms and always retries. That connection persists until test scripts close it through other testfixture commands.

The unlock-notify sample allocates a stack `UnlockNotification` with a pthread mutex and condition variable for each wait. It uses SQLite's connection-level unlock-notify registration and destroys pthread primitives before returning.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, `tclsqlite.h`, Tcl threads/events, SQLite testfixture entry points, and test helpers from `test1.c`. The child interpreter deliberately initializes a subset of the testfixture so thread scripts can open databases, use mutex tests, and call normal SQLite Tcl commands. `sqlite3ErrName()` from SQLite core provides symbolic result names.

The unlock-notify code is guarded by `SQLITE_OS_UNIX && SQLITE_ENABLE_UNLOCK_NOTIFY` because it uses pthread condition variables. It is also embedded between documentation extraction comments for the `sqlite3_unlock_notify()` API sample, so changes can affect generated documentation as well as tests.

## Risks And Edge Cases

- The parent interpreter pointer is shared with queued events. The parent must remain alive and enter Tcl's event loop; otherwise queued scripts do not run and child-to-parent behavior can hang or target invalid state.
- `sqlthread_parent()` is explicitly incomplete for synchronous use. Tests should treat it as fire-and-forget.
- Child thread initialization must remain consistent with testfixture command dependencies; missing commands in child interpreters can cause thread-only test failures.
- `sqlthread_open()` ignores the return code from `sqlite3_open()` before registering MD5 and a busy handler, so tests using it must handle bad pointer or failed connection behavior carefully.
- The busy handler retries indefinitely, which is useful for concurrency tests but can hide deadlocks.
- Unlock-notify waits must handle `SQLITE_LOCKED` returned directly by `sqlite3_unlock_notify()` as a deadlock signal and must not retry in that case.
- Tcl object reference counts and cross-thread script copies are correctness-critical; queued `EvalEvent` data must outlive the posting thread.

## Test Signals

Useful tests spawn child scripts, wait with `vwait`, verify parent variables receive normal results and error results, and confirm `sqlthread id` differs between parent and child. Concurrency tests should open handles in multiple child threads, exercise busy-handler retry behavior, and ensure parent events drain. Unlock-notify tests should cover blocking and nonblocking prepare, blocking step, deadlock detection, statement reset before retry, and correct Tcl tail variable handling.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_vdbecov.c -->
# sources/storage-engines/sqlite/src/test_vdbecov.c

## Purpose

`test_vdbecov.c` is test-only Tcl support for SQLite VDBE branch coverage instrumentation. When both `SQLITE_TEST` and `SQLITE_VDBE_COVERAGE` are enabled, it registers `vdbe_coverage` so Tcl tests can start coverage collection, run SQL, and report VDBE source lines and branch paths that were never exercised.

## Important APIs, Types, And Functions

- `aBranchArray[200000]` is a static byte array indexed by VDBE source line or instrumentation id.
- `test_vdbe_branch()` is the callback registered with `SQLITE_TESTCTRL_VDBE_COVERAGE`; it ORs branch bits into `aBranchArray[iSrc]`.
- `appendToList()` appends `{line path never-description}` triples to a Tcl result list.
- `test_vdbe_coverage()` implements `vdbe_coverage start|report|stop`.
- `Sqlitetestvdbecov_Init()` registers the Tcl command when instrumentation is compiled in.

## Control Flow

`vdbe_coverage start` zeroes the array and installs `test_vdbe_branch()` through `sqlite3_test_control()`. VDBE execution elsewhere calls that callback with a source id, branch bit, and branch type. `vdbe_coverage report` scans every nonzero byte in the array and emits missing path entries for branch bits that were not seen. `vdbe_coverage stop` unregisters the callback by passing null pointers to the same test-control opcode.

The reporting logic treats high-nibble type `4` as a three-way comparison and labels missing paths as `less than`, `equal`, or `greater-than`; other instrumented branches are labeled `falls through`, `taken`, or `NULL`.

## State And Persistence Behavior

All state is process-local and test-only. Coverage data lives in `aBranchArray` until the next `start`, process exit, or command stop. No SQLite database state is modified, but the global VDBE coverage callback affects all connections in the test process while active.

## Dependencies And Integration Points

The module depends on `sqlite3_test_control(SQLITE_TESTCTRL_VDBE_COVERAGE, ...)`, VDBE instrumentation sites that call the registered callback, Tcl object APIs, and `sqliteInt.h` token/type definitions. It integrates with SQLite's Tcl testfixture through `Sqlitetestvdbecov_Init()`.

## Risks And Edge Cases

- Source ids beyond `sizeof(aBranchArray)` are silently ignored, so instrumentation growth can hide uncovered paths unless the array remains large enough.
- Coverage state is global and not thread-local; concurrent tests could race or mix coverage observations.
- Branch bits are accumulated with OR only, so there is no execution count or ordering information.
- The `iType` callback parameter is unused; reporting infers labels from bits stored in the high nibble of the branch byte.
- The file compiles to a no-op initializer when coverage support is omitted, so tests must gate expectations on compile options.

## Test Signals

Tests should verify `start` resets old observations, SQL execution populates expected branch entries, `report` returns missing paths with stable line/path labels, and `stop` disables further accumulation. Build-matrix tests should verify the command exists only when `SQLITE_VDBE_COVERAGE` is defined.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_vdbecov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_vfs.c -->
# sources/storage-engines/sqlite/src/test_vfs.c

## Purpose

`test_vfs.c` implements the Tcl `testvfs` command used by SQLite tests to create instrumented VFS wrappers. A test VFS forwards real file I/O to a parent VFS while invoking Tcl callbacks, injecting I/O/full/cantopen faults, overriding device characteristics and sector size, and optionally replacing WAL shared-memory methods with an in-memory model. It is compiled only under `SQLITE_TEST`.

## Important APIs, Types, And Functions

- `Testvfs` stores the registered VFS, parent VFS, Tcl interpreter/script, callback mask, SHM buffers, fault injectors, device flags, and sector size.
- `TestvfsFile` is the public `sqlite3_file` wrapper; `TestvfsFd` stores the parent real file, filename, SHM id, SHM buffer link, and local SHM lock masks.
- `TestvfsBuffer` stores per-database in-memory SHM pages shared by all handles opened through the test VFS.
- `TestFaultInject` and `tvfsInjectFault()` implement transient or persistent fault countdowns.
- `tvfs_io_methods` provides xClose, xRead, xWrite, xTruncate, xSync, xFileSize, locks, file-control, SHM, fetch, and unfetch wrappers.
- `tvfsOpen()`, `tvfsDelete()`, `tvfsAccess()`, `tvfsFullPathname()`, `tvfsRandomness()`, `tvfsSleep()`, and `tvfsCurrentTime()` implement `sqlite3_vfs` methods.
- `tvfsShmOpen()`, `tvfsShmMap()`, `tvfsShmLock()`, `tvfsShmBarrier()`, and `tvfsShmUnmap()` implement the in-memory SHM backend unless `-fullshm` forwards to the parent VFS or `-noshm` removes SHM methods.
- `testvfs_obj_cmd()` implements object subcommands: `shm`, `delete`, `filter`, `ioerr`, `fullerr`, `cantopenerr`, `script`, `devchar`, and `sectorsize`.
- `testvfs_cmd()` creates and registers a named VFS plus a Tcl object command of the same name.
- `vfs_shmlock` and `vfs_set_readmark` are direct Tcl helpers for WAL SHM locking and readmark mutation.

## Control Flow

`Sqlitetestvfs_Init()` registers `testvfs`, `vfs_shmlock`, and `vfs_set_readmark`. `testvfs VFSNAME ?options?` parses options such as `-noshm`, `-fullshm`, `-default`, `-szosfile`, `-mxpathname`, and `-iversion`, creates a `Testvfs` object, captures the current default VFS as its parent, installs a Tcl object command, fills a copy of the static `sqlite3_vfs`, and registers it with SQLite.

Every file open allocates a `TestvfsFd` followed by parent `szOsFile` bytes for the real file. `tvfsOpen()` optionally invokes the Tcl script as `xOpen`, supports result-code override or connection id naming, injects configured faults, opens the real file through the parent VFS, then installs a copy of `tvfs_io_methods` trimmed to the configured VFS version and SHM policy.

Most I/O methods follow the same pattern: if a script is installed and the method bit is enabled, call `tvfsExecTcl()` with method-specific arguments; interpret symbolic result strings with `tvfsResultCode()`; apply configured fault injection when appropriate; and delegate to `sqlite3Os*` on the real file. `xWrite` treats a negative Tcl result-code mapping as "skip real write but return OK", which supports tests that simulate lost writes.

The default SHM model is process-local. `tvfsShmOpen()` finds or creates a `TestvfsBuffer` by full filename and links each open handle into it. `tvfsShmMap()` lazily opens SHM, optionally invokes callbacks and faults, allocates pages on write, and returns pointers from `aPage`. `tvfsShmLock()` checks the linked handle list for conflicting exclusive/shared masks and updates per-handle masks. `tvfsShmUnmap()` unlinks the handle and frees all pages when the last handle closes.

The object command controls runtime behavior. `filter` selects which VFS methods trigger scripts and I/O faults. `script` sets the Tcl callback prefix. `ioerr`, `fullerr`, and `cantopenerr` arm countdown-based faults and return the previous failure count. `shm` reads or replaces in-memory SHM content. `devchar` and `sectorsize` override values returned by xDeviceCharacteristics and xSectorSize.

## State And Persistence Behavior

Real database, journal, WAL, and temp-file persistence remains delegated to the parent VFS unless a Tcl callback or fault changes behavior. In-memory SHM state in the default test model is not persisted to `-shm` files; it lives in `TestvfsBuffer` pages and is shared only within the test process and VFS object.

Fault injector state is mutable per `Testvfs`: `iCnt` counts down, persistent faults continue after the first failure, and `nFail` is returned and reset when the Tcl subcommand is queried. Callback filters and scripts are per VFS object. File objects own Tcl reference-counted SHM ids and copied method tables. Deleting the object command unregisters the VFS and frees object state.

## Dependencies And Integration Points

The module depends on SQLite's public VFS and I/O-method contracts, internal `sqlite3Os*` wrappers, Tcl command/object APIs, and testfixture helpers `getDbPointer()` and `sqlite3ErrName()`. It exercises pager, WAL, atomic-write, file-control, mmap fetch/unfetch, device capability, and VFS registration paths.

The Tcl script callback protocol is an integration surface for many SQLite tests. Callback method names include `xOpen`, `xClose`, `xRead`, `xWrite`, `xSync`, `xDelete`, `xAccess`, `xFullPathname`, `xLock`, `xUnlock`, `xCheckReservedLock`, `xFileControl`, `xSleep`, and SHM methods.

## Risks And Edge Cases

- The in-memory SHM model is a testing approximation, not an OS-level interprocess SHM implementation. It cannot test cross-process locking semantics.
- `TESTVFS_MAX_PAGES` caps SHM pages at 1024; out-of-range page requests rely on assertions in debug builds.
- Callback scripts run in the stored interpreter and can return result codes that alter VFS behavior; malformed or unexpected results fall back to parent behavior in several paths.
- `tvfsExecTcl()` increments the script object's refcount but does not decrement the duplicate evaluation object directly, so Tcl lifetime assumptions are important.
- Full SHM forwarding, no-SHM trimming, and VFS `iVersion` trimming change method availability and must match SQLite's VFS ABI expectations.
- Fault injection is method-mask-sensitive for many methods but not all fault types; tests must configure `filter` deliberately.
- `tvfsClose()` closes the parent file and frees wrapper state even if callbacks fail, so callback errors become background Tcl errors rather than SQLite close failures.
- `devchar` stores an internal marker bit while returning named flags, which can surprise direct numeric inspection.

## Test Signals

Tests should verify VFS creation/deletion, default VFS registration, option parsing, method filtering, callback argument shapes, symbolic result-code overrides, transient and persistent `ioerr/fullerr/cantopenerr` behavior, `xWrite` skip semantics, SHM map/lock/unmap behavior, `-noshm` and `-fullshm` modes, device characteristic and sector-size overrides, file-control pragma hooks, mmap fetch forwarding, `vfs_shmlock`, and `vfs_set_readmark`.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_window.c -->
# sources/storage-engines/sqlite/src/test_window.c

## Purpose

`test_window.c` is SQLite testfixture support for registering window functions from Tcl. Under `SQLITE_TEST`, it exposes commands that call `sqlite3_create_window_function()`, verify misuse cases, register a strict integer-summing window aggregate, and override the built-in `sum` aggregate for tests.

## Important APIs, Types, And Functions

- `TestWindow` stores Tcl scripts for xStep, xFinal, xValue, xInverse, plus the interpreter.
- `TestWindowCtx` stores the current Tcl object aggregate value.
- `doTestWindowStep()` invokes either the Tcl xStep or xInverse script with the previous state and SQL arguments.
- `doTestWindowFinalize()` invokes Tcl xFinal or xValue and returns text to SQLite.
- `testWindowStep()`, `testWindowInverse()`, `testWindowFinal()`, `testWindowValue()`, and `testWindowDestroy()` are callbacks passed to SQLite.
- `test_create_window()` implements Tcl `sqlite3_create_window_function`.
- `test_create_window_misuse()` verifies that missing required callbacks return `SQLITE_MISUSE`.
- `sumintStep()`, `sumintInverse()`, `sumintFinal()`, and `sumintValue()` implement a one-argument integer-only window sum.
- `test_create_sumint()` and `test_override_sum()` register test functions.
- `Sqlitetest_window_Init()` installs the Tcl commands.

## Control Flow

The generic Tcl-backed window function is created by `sqlite3_create_window_function DB NAME XSTEP XFINAL XVALUE XINVERSE`. The command duplicates and reference-counts the four Tcl callback scripts, stores them in a `TestWindow`, and passes that object as `sqlite3_user_data()`.

For each step or inverse call, `doTestWindowStep()` duplicates the configured Tcl script, appends the previous aggregate value (or an empty string), appends string versions of all SQL arguments, and evaluates it globally. On Tcl success, the result replaces `TestWindowCtx.pVal`; on error, SQLite receives `sqlite3_result_error()`. For xValue/xFinal, `doTestWindowFinalize()` evaluates the selected Tcl script with the current state and returns its string result. xFinal also releases the stored state.

The `sumint` implementation uses SQLite aggregate context as a `sqlite3_int64`, adds integer arguments in xStep, subtracts in xInverse, and returns the current sum in both xValue and xFinal. Non-integer xStep arguments produce an error.

## State And Persistence Behavior

All state is per connection and per aggregate/window frame. The registered function's `TestWindow` persists until SQLite destroys the function object and invokes `testWindowDestroy()`. Aggregate state persists in `sqlite3_aggregate_context()` for each invocation context and owns a Tcl object reference when the Tcl-backed function is used. The file does not persist database content except through SQL statements that call the registered functions.

## Dependencies And Integration Points

The file depends on `sqlite3_create_window_function()`, `sqlite3_create_function()`, SQLite aggregate context APIs, Tcl object evaluation, testfixture `getDbPointer()`, and `sqlite3ErrName()`. It integrates with window-function planner and executor tests, function registration API tests, and misuse validation.

## Risks And Edge Cases

- `sqlite3_value_text()` is used for all generic Tcl callback arguments, so NULL and non-text values are coerced to text-oriented representations for tests.
- xInverse assumes the aggregate context exists in `sumintInverse()` and does not validate integer type; this is acceptable for controlled tests but not a general extension pattern.
- The generic Tcl-backed function returns all values as text, which may affect affinity-sensitive tests.
- Callback scripts are evaluated globally in the stored interpreter, so tests must manage global Tcl state and errors carefully.
- On `sqlite3_create_window_function()` failure, `test_create_window()` returns an error without explicitly freeing `pNew`; expected SQLite destructor behavior should be checked for registration failures.

## Test Signals

Tests should cover custom Tcl step/inverse/value/final call ordering, state propagation between callbacks, error propagation from Tcl scripts, xFinal state cleanup, `SQLITE_MISUSE` for missing callback combinations, `sumint` over sliding windows, non-integer argument errors, and overriding `sum` through normal aggregate registration.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_window.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_wsd.c -->
# sources/storage-engines/sqlite/src/test_wsd.c

## Purpose

`test_wsd.c` provides sample test implementations of `sqlite3_wsd_init()` and `sqlite3_wsd_find()` for builds that define both `SQLITE_OMIT_WSD` and `SQLITE_TEST`. WSD means writable static data; this shim emulates SQLite's writable static variables using process-local heap storage.

## Important APIs, Types, And Functions

- `ProcessLocalStorage` contains a fixed hash table of `ProcessLocalVar` entries and a bump-allocation free area.
- `ProcessLocalVar` stores the original static variable key pointer and hash-chain link; the variable bytes follow the structure in memory.
- `pGlobal` is the single process-local storage arena.
- `sqlite3_wsd_init(int N, int J)` allocates the arena sized for `N` bytes of variable data plus `J` hash entries.
- `sqlite3_wsd_find(void *K, int L)` hashes the key pointer, returns an existing copy, or creates a new entry initialized from the bytes at `K`.

## Control Flow

`sqlite3_wsd_init()` lazily allocates one contiguous block with `malloc()`, clears the `ProcessLocalStorage` header, and points `pFree` after it. `sqlite3_wsd_find()` hashes the address value of `K`, searches the bucket chain for pointer identity, and if absent consumes `ROUND8(sizeof(ProcessLocalVar)+L)` bytes from the arena, links a new entry, copies `L` bytes from `K`, and returns the storage after the entry header.

## State And Persistence Behavior

The arena is process-global and never freed by this file. It persists for the life of the test process. Each emulated WSD variable is initialized once from the original static memory image and then remains mutable in the process-local copy. There is no thread synchronization in this sample implementation.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, `ROUND8`, SQLite result constants, and C heap functions. It is only compiled in a specialized test build and supplies symbols expected by SQLite's `SQLITE_OMIT_WSD` mode.

## Risks And Edge Cases

- The implementation asserts enough arena space exists rather than returning an error from `sqlite3_wsd_find()`, so incorrect `N`/`J` sizing is fatal in debug builds and unsafe otherwise.
- `pGlobal` access is unsynchronized; concurrent first access or variable creation can race.
- Hashing pointer bytes is process-specific and uses only pointer identity, which is appropriate for static-variable keys but not generalized keys.
- There is no cleanup path and no support for per-thread storage isolation.

## Test Signals

Tests should use an `SQLITE_OMIT_WSD && SQLITE_TEST` build, call SQLite initialization paths that invoke `sqlite3_wsd_init()`, verify repeated `sqlite3_wsd_find()` calls for the same key return the same mutable copy, verify different keys do not alias, and stress arena sizing for all expected WSD variables.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_wsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/threads.c -->
# sources/storage-engines/sqlite/src/threads.c

## Purpose

`threads.c` is SQLite's small internal worker-thread abstraction. It supports real pthread worker threads on Unix, real `_beginthreadex()` worker threads on native Windows, and a deterministic single-thread fallback. The abstraction is compiled only when `SQLITE_MAX_WORKER_THREADS>0` and is used by SQLite features that can optionally parallelize work without requiring an application to use a threaded build path.

## Important APIs, Types, And Functions

- `SQLiteThread` is backend-specific. Pthread builds store `pthread_t`, completion flag, result, task function, and input. Win32 builds store thread handle, id, task function, input, and result. Fallback builds store task function/input or immediate result.
- `sqlite3ThreadCreate(SQLiteThread **, void *(*)(void*), void*)` starts or schedules a worker task and always returns an allocated `SQLiteThread` on success.
- `sqlite3ThreadJoin(SQLiteThread *, void **ppOut)` joins or executes the task and frees the `SQLiteThread`.
- `sqlite3FaultSim(200)` forces deterministic sequential execution in pthread and Win32 backends for test control.
- Win32 builds call `sqlite3Win32Wait(HANDLE)` from `os_win.c` before closing the thread handle.

## Control Flow

When pthread support is available, `sqlite3ThreadCreate()` allocates state, records the task, and either starts `pthread_create()` or, if fault simulation/thread creation fails, executes the task synchronously and marks it done. Join returns the synchronous result directly or calls `pthread_join()`.

On Windows, creation allocates state and uses `_beginthreadex()` unless core mutexes are disabled or fault simulation requests deterministic execution. Failed or disabled thread creation falls back to immediate execution on the caller thread. The thread entry shim stores `xTask(pIn)` in `pResult` and calls `_endthreadex()`. Join waits with `sqlite3Win32Wait()`, closes the handle, returns `pResult` on `WAIT_OBJECT_0`, and frees the wrapper.

If no real backend is compiled, creation randomly chooses based on the allocated pointer value whether to defer work until join or run it immediately. Join runs deferred work if needed, includes a small `SQLITE_TEST` allocation probe, frees the wrapper, and returns `SQLITE_OK`.

## State And Persistence Behavior

All state is transient heap state owned by `SQLiteThread` and freed by join. Worker results are opaque pointers returned through `ppOut`; SQLite callers own any result payload. The module does not persist database state by itself, but worker tasks may read or produce data for higher-level SQLite operations.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, SQLite memory allocation, fault simulation, compile-time OS/thread macros, pthreads, `os_win.h`, `_beginthreadex()`, and `sqlite3Win32Wait()`. It is an internal abstraction consumed by SQLite worker-thread users and honors `sqlite3GlobalConfig.bCoreMutex` to avoid real threading when core mutexing is disabled.

## Risks And Edge Cases

- `sqlite3ThreadCreate()` can execute the task before returning; callers must not assume asynchronous execution.
- Join is mandatory to retrieve results and free `SQLiteThread`.
- Pthread creation failure is not surfaced as an error; it silently falls back to synchronous execution.
- Win32 join treats non-`WAIT_OBJECT_0` as `SQLITE_ERROR` and then frees wrapper state; callers must handle missing output.
- The fallback backend's pointer-value choice intentionally varies execution timing, so tests should not rely on a fixed create-vs-join execution point unless fault simulation or compile options force it.
- Task functions must be valid until execution, including fallback deferred execution.

## Test Signals

Tests should cover real backend success, forced synchronous mode via `sqlite3FaultSim(200)`, join result propagation, create-time allocation failure, task execution exactly once, Win32 wait/close behavior, pthread join errors if injectable, and single-thread fallback immediate/deferred paths.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/tokenize.c -->
# sources/storage-engines/sqlite/src/tokenize.c

## Purpose

`tokenize.c` implements SQLite's SQL tokenizer, parser driver, identifier-character helper, contextual handling for window-function keywords, and optional SQL normalization. It converts SQL text into Lemon parser tokens, manages parser lifecycle, records parse errors/tails, and normalizes SQL text for statement comparison when `SQLITE_ENABLE_NORMALIZE` is enabled.

## Important APIs, Types, And Functions

- `aiClass[]` maps input bytes to compact character classes used by `sqlite3GetToken()`.
- `charMap()` and generated `keywordhash.h` provide keyword lookup through `keywordCode()`.
- `IdChar()` and `sqlite3IsIdChar()` define legal identifier continuation characters for ASCII and EBCDIC builds.
- `getToken()`, `analyzeWindowKeyword()`, `analyzeOverKeyword()`, and `analyzeFilterKeyword()` resolve contextual `WINDOW`, `OVER`, and `FILTER` ambiguity.
- `sqlite3GetToken()` returns the byte length and token type for the next token.
- `sqlite3RunParser()` drives tokenization, Lemon parser allocation/finalization, interrupt checks, SQL length enforcement, error logging, cleanup of partially built parse objects, and tail tracking.
- `addSpaceSeparator()` and `sqlite3Normalize()` optionally build normalized SQL with literals replaced by `?`, identifiers lowercased, keywords uppercased, and IN-list RHS compressed.

## Control Flow

`sqlite3GetToken()` switches on `aiClass[*z]` for speed. It recognizes whitespace, comments, punctuation, operators, string and quoted identifiers, bracket identifiers, numeric and floating literals, hex integer and blob literals, variables, identifiers/keywords, UTF-8 BOMs, illegal characters, and NUL input. Keyword candidates call generated `keywordCode()` unless an identifier-only continuation is found. Numeric tokens containing configured digit separators become `TK_QNUMBER` so the parser driver can reject them as unrecognized.

`sqlite3RunParser()` allocates or stack-initializes the Lemon parser, installs the current `Parse` in `db->pParse`, clears interruption state when no VDBEs are active, then loops over tokens. It enforces `SQLITE_LIMIT_SQL_LENGTH`, skips spaces and allowed comments, synthesizes `TK_SEMI` and end token at input end, rewrites contextual window tokens when necessary, reports unrecognized tokens, and calls `sqlite3Parser()` with `pParse->sLastToken`. After parsing, it records parser stack highwater when enabled, frees the parser, maps malloc failure to `SQLITE_NOMEM_BKPT`, logs parse errors unless disabled, sets `pParse->zTail`, and frees parse-side structures such as vtab locks, abandoned new tables/triggers, and variable lists.

`sqlite3Normalize()` retokenizes original SQL. It removes comments and whitespace, replaces literals and bind variables with `?`, preserves `IS NULL` and `IS NOT NULL`, dequotes and lowercases identifiers, uppercases keywords/operators, compresses parenthesized RHS values of `IN` to `(?,?,?)`, and appends a semicolon if missing.

## State And Persistence Behavior

Tokenizer tables are static read-only state. Parser execution mutates the supplied `Parse` object, `db->pParse`, `db->u1.isInterrupted`, error strings, parser highwater status, and parse-owned allocations. It does not directly mutate database storage; parser actions called by Lemon grammar may build schema objects or VDBE programs that later change persistent state.

Normalization returns a newly allocated database-owned string from `sqlite3_str_finish()` and does not alter the original SQL. `pParse->zTail` points into the original SQL at the parse stopping point.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, generated `keywordhash.h`, generated Lemon parser APIs (`sqlite3Parser*`), SQLite character maps, limits, logging, memory allocation, VDBE statement metadata, schema object cleanup, virtual table parse locks, and optional normalization APIs. It is on the prepare path for every SQL statement.

## Risks And Edge Cases

- Token boundaries are security- and compatibility-sensitive; small changes affect all SQL parsing.
- Contextual `WINDOW`, `OVER`, and `FILTER` handling works around grammar fallback ambiguity and must remain synchronized with grammar rules.
- Quoted strings and identifiers have different illegal-token behavior on unterminated input; parser error offsets depend on returned lengths.
- Numeric digit separators intentionally become invalid `TK_QNUMBER` in the parser path unless accepted elsewhere; normalization must mirror token behavior.
- Comments are ignored only during schema initialization or when comments are enabled by DB config; otherwise comments can trigger unrecognized-token behavior.
- `sqlite3RunParser()` cleans partially built tables/triggers only outside special parse modes; mistakes can leak objects or double-free rename/vtab-owned objects.
- EBCDIC and ASCII paths share behavior through different tables; both need coverage when portability matters.

## Test Signals

Tests should cover every token class, comments, BOMs, quoted identifiers and strings, blob and hex literals, numeric separators, variables including Tcl-style names, illegal characters, SQL length limits, interrupts, parser tail handling, contextual window keywords, comment DB config, malloc failure cleanup, parser tracing/highwater, normalization of literals/identifiers/IN lists/double-quoted strings, and EBCDIC-specific identifier behavior where supported.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/tokenize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/treeview.c -->
# sources/storage-engines/sqlite/src/treeview.c

## Purpose

`treeview.c` implements SQLite debug-only parse-tree and AST printers. Under `SQLITE_DEBUG`, it formats internal structures such as columns, WITH clauses, source lists, SELECTs, window definitions, expressions, expression/id lists, upserts, DML statements, trigger steps, and triggers as an ASCII tree on stdout. It also exposes `sqlite3Show*()` helper functions intended for interactive debuggers.

## Important APIs, Types, And Functions

- `sqlite3TreeViewPush()`, `sqlite3TreeViewPop()`, `sqlite3TreeViewLine()`, and `sqlite3TreeViewItem()` manage indentation state and line output.
- `sqlite3TreeViewColumnList()`, `sqlite3TreeViewWith()`, `sqlite3TreeViewSrcList()`, and `sqlite3TreeViewSelect()` print schema/query structures.
- `sqlite3TreeViewBound()`, `sqlite3TreeViewWindow()`, and `sqlite3TreeViewWinFunc()` print window frame and function structures when window functions are enabled.
- `sqlite3TreeViewExpr()` is the central expression-node formatter and handles many token opcodes and expression flags.
- `sqlite3TreeViewBareExprList()`, `sqlite3TreeViewExprList()`, `sqlite3TreeViewBareIdList()`, and `sqlite3TreeViewIdList()` print list structures.
- `sqlite3TreeViewUpsert()`, and `TREETRACE_ENABLED` DML printers (`sqlite3TreeViewDelete()`, `sqlite3TreeViewInsert()`, `sqlite3TreeViewUpdate()`) show higher-level statement inputs.
- `sqlite3TreeViewTriggerStep()` and `sqlite3TreeViewTrigger()` print trigger structures.
- `sqlite3ShowExpr()`, `sqlite3ShowSelect()`, `sqlite3ShowTrigger()`, and related wrappers provide debugger-friendly entry points.

## Control Flow

Printer calls push a tree level, emit a line with prefix characters based on `TreeView.bLine[]`, recursively print child structures, then pop the level. Passing a null `TreeView *` to top-level routines lazily allocates a view on first push and frees it after the final pop.

`sqlite3TreeViewSelect()` prints WITH, result set, window functions, FROM, WHERE, GROUP BY, HAVING, WINDOW definitions, ORDER BY, LIMIT/OFFSET, and compound SELECT links. `sqlite3TreeViewExpr()` switches on expression opcode to print literals, columns, functions, aggregates, subqueries, IN/BETWEEN/CASE, trigger references, vectors, collations, truth operators, and binary/unary operators, recursing into children and lists as needed.

The DML and trigger printers are compiled only when their feature macros are enabled. Debugger wrappers omit many parameters and print a complete tree for a single object.

## State And Persistence Behavior

The module does not alter persistent database state. It allocates transient `TreeView` objects and temporary formatted strings, writes to stdout, and flushes after output. It inspects internal AST flags, pointers, cursor numbers, and schema metadata but should not mutate them.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, internal AST structs (`Select`, `Expr`, `SrcList`, `Window`, `Trigger`, `Upsert`, etc.), `sqlite3_str`/`StrAccum` formatting helpers, debug feature macros, and stdout. It integrates with tree-tracing code and debugger workflows across parser, resolver, planner, trigger, and window-function development.

## Risks And Edge Cases

- It is debug-only but often used while diagnosing parser/planner bugs; stale formatting can mislead debugging.
- The code dereferences many internal unions and flag-dependent fields, so it must stay synchronized with AST layout invariants such as `ExprUseXList()` and `ExprUseXSelect()`.
- Output includes raw pointers and flags; this is useful for debugging but unsuitable as stable test output across processes.
- Fixed-size buffers are used for lines, relying on SQLite string accumulators to avoid overflow.
- Very deep trees are truncated visually by the fixed `bLine` depth array, though recursion still proceeds.

## Test Signals

Signals are mostly debug-build checks: compile with `SQLITE_DEBUG`, call `sqlite3Show*()` from targeted tests or debugger sessions, and verify no assertions for representative SELECTs, joins, CTEs, expressions, window frames, triggers, upserts, and DML tree traces. Golden-output tests should avoid pointer values or mask them.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/treeview.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/trigger.c -->
# sources/storage-engines/sqlite/src/trigger.c

## Purpose

`trigger.c` implements SQLite trigger lifecycle and execution. It builds `Trigger` and `TriggerStep` objects during parsing, installs and removes triggers from schema hashes, finds triggers that apply to DML operations, expands and executes `RETURNING` clauses through a trigger-like path, compiles row-trigger subprograms, emits `OP_Program` calls, and computes old/new column usage masks. The file is omitted when `SQLITE_OMIT_TRIGGER` is defined.

## Important APIs, Types, And Functions

- `sqlite3DeleteTriggerStep()` and `sqlite3DeleteTrigger()` free trigger structures and owned expressions/selects/lists.
- `sqlite3TriggerList()` merges table-attached triggers with applicable TEMP triggers and statement-local RETURNING triggers.
- `sqlite3BeginTrigger()` validates CREATE TRIGGER syntax/target/schema/authorization and stores a partially built trigger in `pParse->pNewTrigger`.
- `sqlite3FinishTrigger()` fixes database references, writes `sqlite_schema` rows for normal CREATE TRIGGER statements, and links triggers during schema initialization.
- `sqlite3TriggerSelectStep()`, `sqlite3TriggerInsertStep()`, `sqlite3TriggerUpdateStep()`, and `sqlite3TriggerDeleteStep()` create trigger body steps.
- `sqlite3DropTrigger()`, `sqlite3DropTriggerPtr()`, and `sqlite3UnlinkAndDeleteTrigger()` remove triggers from persistent schema and in-memory hashes.
- `sqlite3TriggersExist()` determines whether DML needs BEFORE/AFTER trigger handling and returns a trigger list plus timing mask.
- RETURNING helpers include `sqlite3ExpandReturning()`, `sqlite3ProcessReturningSubqueries()`, and `codeReturningTrigger()`.
- `codeTriggerProgram()`, `codeRowTrigger()`, `getRowTrigger()`, `sqlite3CodeRowTriggerDirect()`, and `sqlite3CodeRowTrigger()` compile and invoke trigger VDBE subprograms.
- `sqlite3TriggerColmask()` computes old/new column masks needed by triggers.

## Control Flow

CREATE TRIGGER parsing starts in `sqlite3BeginTrigger()`. It resolves the trigger schema, handles TEMP trigger naming, optionally ignores legacy qualified target names during schema reparse, looks up the target table/view, rejects virtual tables and protected shadow/system tables, checks duplicate trigger names and authorization, validates BEFORE/AFTER/INSTEAD OF rules, translates INSTEAD OF to internal BEFORE-on-view representation, and allocates a `Trigger`.

After body parsing, `sqlite3FinishTrigger()` attaches the step list, fixes all schema references, rejects writes to read-only shadow tables from trigger bodies, writes a `sqlite_schema` row and parse-schema op for normal CREATE statements, or during schema initialization inserts the trigger into `trigHash` and links same-schema table triggers into `Table.pTrigger`.

Trigger body step constructors duplicate or retain parse subtrees depending on rename mode. INSERT steps hold target, column list, SELECT, conflict policy, and UPSERT. UPDATE steps duplicate SET/WHERE and fold UPDATE-FROM into an appended nested source term. DELETE steps hold target and WHERE. SELECT steps discard results at execution.

For DML, `sqlite3TriggersExist()` fast-paths tables with no table/TEMP triggers or disabled triggers, then `triggersReallyExist()` filters by operation, UPDATE column overlap, trigger enablement, TEMP trigger policy, and RETURNING behavior. `sqlite3CodeRowTrigger()` iterates the trigger list for a specific timing and operation. Normal triggers call `sqlite3CodeRowTriggerDirect()`, which gets or compiles a cached `TriggerPrg` and emits `OP_Program`. RETURNING triggers are generated inline by `codeReturningTrigger()`.

`codeRowTrigger()` creates a sub-`Parse`, resolves the WHEN expression, emits a jump to the final halt when WHEN is false or null, compiles each trigger step through normal `sqlite3Update()`, `sqlite3Insert()`, `sqlite3DeleteFrom()`, or `sqlite3Select()` calls, captures the VDBE op array as a `SubProgram`, records old/new column masks, transfers parse errors, and caches the program on the top-level parse.

## State And Persistence Behavior

Persistent trigger definitions are stored in `sqlite_schema` as rows of type `trigger`. In-memory trigger state lives in schema `trigHash` tables and, for same-schema table triggers, in `Table.pTrigger` lists. Dropping a trigger deletes the schema row, changes the schema cookie, emits `OP_DropTrigger`, and unlinks/frees in-memory structures during schema change processing.

Execution-time trigger programs are cached per top-level parse in `Parse.pTriggerPrg` and linked into the parent VDBE as `SubProgram` objects. RETURNING uses a statement-local `Returning` object and ephemeral cursor/register state to collect result records. Column masks in `TriggerPrg.aColmask[]` influence how much old/new row data DML callers must load.

## Dependencies And Integration Points

The file depends on parser structures, schema hashes, authorization, DB fixer utilities, name resolution, expression/list/select duplication and deletion, DML code generators, VDBE subprogram APIs, ALTER TABLE rename support, virtual table context rules, shadow table protections, recursive-trigger configuration, RETURNING support, and foreign-key action infrastructure that also uses trigger subprogram mechanics.

It integrates directly with `insert.c`, `update.c`, `delete.c`, `select.c`, `resolve.c`, `build.c`, `alter.c`, `vdbe.c`, schema initialization, and DB config flags such as `SQLITE_EnableTrigger` and `SQLITE_RecTriggers`.

## Risks And Edge Cases

- Schema selection for TEMP triggers, attached databases, orphan TEMP triggers, and legacy qualified target names is compatibility-sensitive.
- Trigger lists are temporarily rewired through `pNext` when TEMP triggers are prepended, so callers must treat returned lists as transient.
- Recursive trigger control depends on `OP_Program` P5 and `SQLITE_RecTriggers`; mistakes can allow infinite recursion or block legal recursion.
- RETURNING is implemented through trigger-like objects but has different timing and inline code generation, especially for virtual tables and UPSERT update paths.
- UPDATE OF column filtering uses name overlap only; renamed columns and duplicated expression lists must stay consistent.
- Trigger subprogram caching is keyed by trigger pointer and conflict policy; schema changes or parse reuse must not retain stale programs.
- Error transfer from sub-parse to outer parse must avoid leaks and preserve the first meaningful error.
- Shadow table/system table restrictions protect internal structures and depend on compile-time options and `sqlite3ReadOnlyShadowTables()`.

## Test Signals

Tests should cover CREATE/DROP trigger schema rows, TEMP triggers on main tables, attached schema names, IF NOT EXISTS, orphan TEMP trigger handling, authorization failures, view/table BEFORE/AFTER/INSTEAD OF validation, virtual/shadow/system table rejection, INSERT/UPDATE/DELETE/SELECT trigger steps, UPDATE OF filtering, UPDATE-FROM in triggers, WHEN clauses, conflict-policy inheritance, recursive trigger enablement, old/new column references and colmasks, RETURNING expansion including `*`, RETURNING subqueries and UPSERT, trigger program cache reuse by conflict policy, schema reparse, ALTER TABLE rename mode, and cleanup on OOM or parse errors.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/trigger.c -->
