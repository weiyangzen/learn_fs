# Group Research: subset-b-008743

This grouped report covers selected SQLite JNI C API, FTS5, and wrapper1 UDF classes. Each file section is bounded for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLTester.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLTester.java

## Purpose
`SQLTester.java` is an internal SQL-script interpreter and command runner for testing the SQLite JNI bindings against SQLite-style test scripts. It is not a public API; it lives in `org.sqlite.jni.capi` so it can access package-visible JNI helpers and native test extensions.

## Important APIs, Types, and Functions
The file defines `SQLTester`, result formatting enums, test exceptions, `Outer`, `Util`, command classes, `CommandDispatcher`, and `TestScript`. `SQLTester.execSql()` prepares one or more UTF-8 SQL statements with `sqlite3_prepare_v2()`, steps them, formats result rows, and finalizes statements. Commands implement script operations such as `--run`, `--result`, `--glob`, `--tableresult`, `--json`, `--open`, `--new`, `--close`, `--db`, `--null`, `--column-names`, and `--testcase`. Native hooks include `strglob()` and `installCustomExtensions()`.

## Control Flow
`main()` loads custom native extensions, parses CLI flags, registers an auto-extension that applies accumulated initialization SQL, then calls `runTests()`. Each script creates a `TestScript`, which line-scans the file, recognizes directives and command lines, appends non-command SQL to the tester input buffer, and dispatches commands. Result commands consume SQL from the input buffer, call `execSql()`, and compare normalized output to expected literals or globs.

## State and Persistence Behavior
State is process-local: input/result buffers, `dbInitSql`, null display text, current database slot, counters, and up to seven `sqlite3` handles. Database files are opened by script commands; the default `test.db` is deleted before/after runs. `reset()` closes all handles and clears script-scoped state but preserves overall counters.

## Dependencies and Integration Points
The class depends heavily on `CApi`, `OutputPointer`, `sqlite3`, `sqlite3_stmt`, callback proxies, `ResultCode`, and native library `sqlite3-jni`. It integrates with `test-script-interpreter.md` semantics and SQLite auto-extension behavior.

## Risks
The parser is intentionally narrow and rejects or skips incompatible directives, C-preprocessor lines, mixed module names, and some script features. It assumes UTF-8 script input and manually decodes multibyte characters. Statement finalization/reset in error paths is critical because failed `INSERT ... RETURNING` cases can leave locks. The auto-extension plus lazy default DB open can interact with initialization timing.

## Test Signals
Useful signals are successful execution of SQL test scripts, accurate escaped/asis result buffers, glob/table-result matching, unknown command skipping, clean finalization on errors, and no leaked open database handles after `runTests()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLTester.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ScalarFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ScalarFunction.java

## Purpose
`ScalarFunction` is the low-level JNI binding abstraction for SQLite scalar user-defined functions registered through `sqlite3_create_function()`.

## Important APIs, Types, and Functions
The abstract class implements `SQLFunction` and requires `xFunc(sqlite3_context cx, sqlite3_value[] args)`. It also provides an overridable no-op `xDestroy()` lifecycle callback. The signature mirrors SQLite's scalar callback while exposing JNI wrapper types for the function context and arguments.

## Control Flow
Client code subclasses `ScalarFunction`, registers the object with `CApi.sqlite3_create_function()`, and SQLite calls `xFunc()` during statement execution. Native proxy code translates thrown Java exceptions into SQLite result errors as documented by the class comments.

## State and Persistence Behavior
The base class stores no state. Subclasses may hold Java state, but `sqlite3_context` and `sqlite3_value` arguments are only valid during a single callback invocation and should not be retained.

## Dependencies and Integration Points
It integrates with `SQLFunction`, `sqlite3_context`, `sqlite3_value`, and the C API registration layer in `CApi`. Higher-level wrapper1 scalar functions adapt to this type through `SqlFunction.ScalarAdapter`.

## Risks
The primary risk is retaining callback-only native wrappers beyond their valid lifetime. Implementations also need to use `sqlite3_result_*()` APIs correctly to set a result or error.

## Test Signals
`Tester1.testUdf1()`, `testUdfThrows()`, `testUdfJavaObject()`, and ByteBuffer UDF tests exercise scalar execution, error translation, Java object values, `xDestroy()`, and invalidation of temporary native handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ScalarFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TableColumnMetadata.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TableColumnMetadata.java

## Purpose
`TableColumnMetadata` is a Java result object populated by the convenience overload of `sqlite3_table_column_metadata()`.

## Important APIs, Types, and Functions
The class owns package-private output holders for not-null, primary-key, autoincrement, collation sequence, and data type values. Public getters expose `getDataType()`, `getCollation()`, `isNotNull()`, `isPrimaryKey()`, and `isAutoincrement()`.

## Control Flow
Client code creates no meaningful state directly beyond constructing the object. The JNI/C API wrapper fills its `OutputPointer` fields, then callers read immutable-by-convention metadata through getters.

## State and Persistence Behavior
The object is a snapshot holder. It has mutable fields internally, but no setters; values persist until overwritten by package-level code or discarded.

## Dependencies and Integration Points
It depends on `OutputPointer.Bool` and `OutputPointer.String`, and is returned by `CApi.sqlite3_table_column_metadata(sqlite3, String, String, String)`.

## Risks
Because fields are package-visible and mutable holders, misuse inside the package could mutate a previously returned snapshot. Callers must also handle null return from the C API wrapper when a database/table lookup fails.

## Test Signals
`Tester1.testColumnMetadata()` compares raw output-pointer calls with this wrapper, checks declared type/collation flags, verifies missing database/table return null, and tests table-existence lookup when column name is null.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TableColumnMetadata.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/Tester1.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/Tester1.java

## Purpose
`Tester1` is the main regression and smoke-test suite for the SQLite JNI C API bindings. It can run single-threaded, repeated, shuffled, or multi-threaded, and validates handle lifetimes, callback proxies, UDFs, metadata, blob/backup APIs, error paths, and optional FTS5 support.

## Important APIs, Types, and Functions
The file defines annotations `ManualTest`, `SingleThreadOnly`, and `RequiresJniNio`, shared helpers `affirm()`, `createNewDb()`, `execSql()`, and `prepare()`, plus many `test*()` methods discovered reflectively. It covers open/close, prepare/tail handling, binding/fetching integers, doubles, text, blobs, Java objects, NIO buffers, SQL expansion, collations, status APIs, scalar/aggregate/window UDFs, trace/profile hooks, busy/progress/commit/update/preupdate/rollback/authorizer hooks, auto-extensions, table metadata, transaction state, explain, limits, keywords, backup, randomness, incremental blob I/O, prepare-multi, custom errmsg, config log, SQL log, shutdown, and JNI thread cache release.

## Control Flow
`main()` parses flags, optionally installs config callbacks, builds the reflective method list, validates `sqlite3_threadsafe()` configuration transitions, then runs loops either directly or through an `ExecutorService`. Each `Tester1` instance invokes all selected `test*()` methods and collects thread errors in a synchronized list.

## State and Persistence Behavior
Static state tracks multi-thread mode, shuffling, quiet output, run counts, selected methods, accumulated errors, assertion count, and DB-open metrics. Most tests use in-memory databases; file-backed tests clean up named files in `finally`. Native handles are checked for pointer zeroing after close/finalize.

## Dependencies and Integration Points
It imports nearly all `CApi` functions and integrates with low-level handle classes, output pointers, callbacks, UDF interfaces, FTS5 tester loading, and optional compile features such as `ENABLE_FTS5`, `ENABLE_PREUPDATE_HOOK`, `ENABLE_COLUMN_METADATA`, and `ENABLE_SQLLOG`.

## Risks
Threaded runs intentionally skip tests whose global state or SQLite behavior is thread-agnostic. Timing in `awaitTermination(nThread*200ms)` can be tight under slow environments. Tests assert JNI-specific lifetime defenses by retaining invalid handles; production code must not copy that pattern. Optional compile features change coverage.

## Test Signals
The whole class is itself the test signal. Strong indicators are zero thrown exceptions, nonzero assertion count, expected DB-open metrics, all pointer invalidation assertions passing, hook replacement return values matching previous callbacks, and FTS5 tests running when compiled in.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/Tester1.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TraceV2Callback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TraceV2Callback.java

## Purpose
`TraceV2Callback` models the callback accepted by `sqlite3_trace_v2()` in Java.

## Important APIs, Types, and Functions
It extends `CallbackProxy` and exposes `int call(int traceFlag, Object pNative, @Nullable Object pX)`. The native callback's user-data argument is elided because Java objects can keep instance-local state.

## Control Flow
After registration, SQLite invokes `call()` for trace events. `pNative` is a `sqlite3_stmt` for statement/profile/row events and a `sqlite3` for close events. `pX` is a SQL string for `SQLITE_TRACE_STMT`, a `Long` nanosecond estimate for `SQLITE_TRACE_PROFILE`, and null for row/close events.

## State and Persistence Behavior
The interface stores no state. Implementations commonly close over counters or logging targets. Event wrapper objects are transient native views and should not be retained beyond the callback.

## Dependencies and Integration Points
It integrates with `CApi.sqlite3_trace_v2`, `CallbackProxy`, `sqlite3`, `sqlite3_stmt`, and nullable annotations.

## Risks
Incorrect casts based on `traceFlag` will fail at runtime. Throwing is allowed by the binding contract but is converted to C-level error information rather than normal Java propagation.

## Test Signals
`Tester1.testTrace()` registers all trace flags, validates event object types, checks non-BMP SQL survives Java/native round trips, counts statement/profile/row events, and confirms close tracing fires when the DB is closed.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TraceV2Callback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/UpdateHookCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/UpdateHookCallback.java

## Purpose
`UpdateHookCallback` represents the Java callback for `sqlite3_update_hook()`.

## Important APIs, Types, and Functions
The single method `void call(int opId, String dbName, String tableName, long rowId)` reports insert, update, or delete operations with database/table names and affected rowid. It extends `CallbackProxy`.

## Control Flow
Registration through `CApi.sqlite3_update_hook()` installs a callback and returns the previously installed hook. SQLite invokes `call()` after eligible row changes.

## State and Persistence Behavior
The interface has no internal state. Implementations may close over counters or expected operation codes. Installed hook identity is retained by the JNI proxy until replaced, cleared, or the database closes.

## Dependencies and Integration Points
It depends on `CallbackProxy` and integrates with C API constants such as `SQLITE_INSERT`, `SQLITE_UPDATE`, and `SQLITE_DELETE`.

## Risks
Exceptions from callbacks are translated into database-level errors. Hook callbacks run in SQLite execution context, so implementations should be lightweight and avoid reentrant misuse.

## Test Signals
`Tester1.testUpdateHook()` validates old-hook return semantics, insert/update/delete operation IDs, clearing the hook, replacing with another hook, and continued database operation after hook changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/UpdateHookCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ValueHolder.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ValueHolder.java

## Purpose
`ValueHolder<T>` is a tiny mutable box used where Java requires captured variables to be effectively final and where UDF aggregate state needs a mutable reference.

## Important APIs, Types, and Functions
The class exposes public field `T value`, a no-arg constructor, and `ValueHolder(T v)`.

## Control Flow
There is no behavior beyond construction and direct field access. Anonymous callback implementations mutate the boxed value to communicate with surrounding test or function code.

## State and Persistence Behavior
The holder persists exactly one mutable value. It provides no synchronization, validation, or ownership semantics.

## Dependencies and Integration Points
It is used throughout `Tester1`, SQL function implementations, aggregate/window state helpers, callback counters, and wrapper1 equivalents.

## Risks
Because `value` is public and unsynchronized, concurrent use requires external coordination. Its simplicity is intentional but easy to misuse as a shared mutable global.

## Test Signals
Indirect test signals appear in UDF accumulators, callback counters, xDestroy flags, auto-extension counters, and aggregate state checks across `Tester1` and `TesterFts5`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ValueHolder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/WindowFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/WindowFunction.java

## Purpose
`WindowFunction<T>` is the low-level JNI UDF abstraction for SQLite window functions.

## Important APIs, Types, and Functions
It extends `AggregateFunction<T>` and adds abstract `xInverse(sqlite3_context cx, sqlite3_value[] args)` and `xValue(sqlite3_context cx)`, matching `sqlite3_create_window_function()` callbacks. Inherited aggregate methods provide `xStep()`, `xFinal()`, and per-context state helpers.

## Control Flow
SQLite invokes `xStep()` as rows enter a frame, `xInverse()` as rows leave, `xValue()` for the current frame result, and `xFinal()` at the end. The JNI registration layer dispatches native calls into this object.

## State and Persistence Behavior
State is inherited from `AggregateFunction`, usually keyed by `sqlite3_context.getAggregateContext()`. Implementations must clear state in `xFinal()` and be prepared for null state.

## Dependencies and Integration Points
It depends on `AggregateFunction`, `sqlite3_context`, `sqlite3_value`, and registration through `CApi.sqlite3_create_function()` or related wrapper logic.

## Risks
The comments warn exceptions in `xInverse()` or `xValue()` may not propagate normally and may only appear through diagnostics. Incorrect state cleanup can cross-contaminate repeated statement execution.

## Test Signals
`Tester1.testUdfWindow()` implements a rolling integer sum and validates expected SQLite window-function example results for five rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/WindowFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/XDestroyCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/XDestroyCallback.java

## Purpose
`XDestroyCallback` is a shared lifecycle callback for Java objects whose client-provided state is destroyed by SQLite.

## Important APIs, Types, and Functions
It declares `void xDestroy()`. The documentation states implementations must not throw and must not call back into SQLite, because that can deadlock.

## Control Flow
SQLite or the JNI proxy calls `xDestroy()` when registered state is finalized, such as a collation, SQL function, or FTS5 aux/function object.

## State and Persistence Behavior
The interface itself stores no state, but implementations typically release or mark Java-side resources. It is part of the lifecycle contract for state retained by native proxies.

## Dependencies and Integration Points
It is referenced by callback/function abstractions that need an xDestroy equivalent, including collations and SQL functions.

## Risks
The documented major risk is registering the same instance multiple times. Duplicate native ownership can lead to double free, memory corruption, or crashes when native references are released.

## Test Signals
`Tester1.testCollation()` and UDF tests check that destroy callbacks are called on close/finalization and not prematurely.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/XDestroyCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/package-info.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/package-info.java

## Purpose
`package-info.java` documents the `org.sqlite.jni.capi` package: a JNI binding intended to map SQLite's C API into Java with minimal abstraction.

## Important APIs, Types, and Functions
The package's primary API surface is `CApi`. The documentation describes goals: near 1-to-1 C API mapping, C documentation reuse, Java 8 support, environment independence, and no third-party dependencies.

## Control Flow
There is no runtime control flow. The file supplies package-level Javadoc and package declaration.

## State and Persistence Behavior
No runtime state exists. The documentation defines expected handle/threading semantics for the package.

## Dependencies and Integration Points
It links to `org.sqlite.jni.capi.CApi` and SQLite C API docs. It frames the relationship between low-level bindings and optional client-created higher-level wrappers.

## Risks
Important risk guidance is in threading notes: Java-facing SQLite handles and database-specific resources must not be used concurrently from multiple threads, even if SQLite itself is thread-safe. Mixed Java/C native use can bypass proxy bookkeeping and break callback/resource management.

## Test Signals
`Tester1` operationalizes these guarantees by exercising thread modes, handle invalidation, callback proxies, and no-third-party low-level usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3.java

## Purpose
`sqlite3` is the Java wrapper type for C-level `sqlite3*` database handles.

## Important APIs, Types, and Functions
The class extends `NativePointerHolder<sqlite3>` and implements `AutoCloseable`. Its private constructor is for JNI creation only. `toString()` includes the native pointer and main database filename via `CApi.sqlite3_db_filename()`. `close()` delegates to `CApi.sqlite3_close_v2(this)`.

## Control Flow
Instances are returned by open APIs. User code passes them back to `CApi` methods, or uses try-with-resources to call `close()`.

## State and Persistence Behavior
The wrapper does not own the pointer independently; the native API owns lifecycle and sets the pointer to zero after close. The Java object remains as a typed carrier even after invalidation.

## Dependencies and Integration Points
It integrates with `NativePointerHolder`, `CApi.sqlite3_open*`, `sqlite3_close_v2`, filename lookup, and wrapper1 `Sqlite.fromNative()` mappings.

## Risks
Calling methods after close yields null/zero pointer semantics and may be misuse depending on the API. Concurrent use follows package-level threading restrictions.

## Test Signals
Many `Tester1` tests assert nonzero pointer after open and zero pointer after close; `testOpenDb1()`, `testOpenDb2()`, and try-with-resources paths validate `close()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_backup.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_backup.java

## Purpose
`sqlite3_backup` is the Java wrapper for C `sqlite3_backup*` handles used by SQLite online backup APIs.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<sqlite3_backup>` and implements `AutoCloseable`. `close()` calls `CApi.sqlite3_backup_finish(this)`.

## Control Flow
`CApi.sqlite3_backup_init()` creates an instance. Client code steps it through `sqlite3_backup_step()`, inspects page counts, and finishes explicitly or via try-with-resources.

## State and Persistence Behavior
It carries a native pointer without independent ownership. Finishing should invalidate the pointer. The Java object can still exist after native finalization.

## Dependencies and Integration Points
It integrates with backup APIs in `CApi` and the `sqlite3` database handle wrappers for source/destination DBs.

## Risks
Failure to finish leaks backup resources and may keep locks. Double finishing should be handled by the C API wrapper but still signals misuse if result codes are ignored.

## Test Signals
`Tester1.testBackup()` initializes source/destination databases, steps one page at a time until `SQLITE_DONE`, checks page count, verifies `sqlite3_backup_finish()` returns zero and pointer becomes zero, then confirms copied data sums to six.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_backup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_blob.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_blob.java

## Purpose
`sqlite3_blob` wraps C `sqlite3_blob*` incremental BLOB handles.

## Important APIs, Types, and Functions
The class extends `NativePointerHolder<sqlite3_blob>` and implements `AutoCloseable`; `close()` delegates to `CApi.sqlite3_blob_close(this)`.

## Control Flow
Instances are opened through `sqlite3_blob_open()` overloads, used with read/write/reopen APIs, and closed explicitly or by try-with-resources.

## State and Persistence Behavior
The wrapper is a typed pointer carrier. Closing invalidates the native pointer. Reopen keeps the same handle but changes target row.

## Dependencies and Integration Points
It integrates with `CApi.sqlite3_blob_open`, `sqlite3_blob_read`, `sqlite3_blob_write`, `sqlite3_blob_reopen`, `sqlite3_blob_bytes`, and ByteBuffer-specific overloads when JNI NIO support is available.

## Risks
Offset/length validation is important for byte arrays and direct buffers. Open writable blob handles can hold locks; handles must be closed on all paths.

## Test Signals
`Tester1.testBlobOpen()` validates open/write/close, double-close error behavior, reopen, byte-array read, NIO read/write bounds checks, returned direct-buffer limits, and final database contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_blob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_context.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_context.java

## Purpose
`sqlite3_context` wraps SQLite UDF callback context handles and provides a Java-friendly aggregate-context key.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<sqlite3_context>` and adds synchronized `Long getAggregateContext(boolean initIfNeeded)`. This calls `CApi.sqlite3_aggregate_context()` and caches a stable key for a matching set of aggregate/window callbacks.

## Control Flow
Scalar, aggregate, and window callbacks receive a context. Aggregate/window functions call `getAggregateContext(true)` from step/value/inverse paths and `getAggregateContext(false)` from final paths.

## State and Persistence Behavior
The `aggregateContext` field caches the native key. Numeric zero is treated as null in public return semantics. A no-row aggregate finalization can legally return null because no state was initialized.

## Dependencies and Integration Points
It integrates with low-level `AggregateFunction`, `WindowFunction`, wrapper1 aggregate helpers, and `CApi.sqlite3_aggregate_context()`.

## Risks
The returned key is valid only within a single SQL statement execution and must not be reused across statements. Retaining the `sqlite3_context` object after a callback is illegal; tests verify native pointer invalidation.

## Test Signals
`Tester1.testUdfAggregate()` and `testUdfWindow()` validate distinct aggregate contexts for multiple invocations, state reset after statement reset/finalize, and null final state for empty result sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_context.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_stmt.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_stmt.java

## Purpose
`sqlite3_stmt` is the Java wrapper for C `sqlite3_stmt*` prepared statement handles.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<sqlite3_stmt>` and implements `AutoCloseable`. `close()` calls `CApi.sqlite3_finalize(this)`.

## Control Flow
Prepare APIs create instances. Client code binds values, steps rows, reads columns, resets as needed, and finalizes or uses try-with-resources.

## State and Persistence Behavior
The wrapper carries a native pointer that should become zero after finalization. It does not own resources outside the native statement lifecycle.

## Dependencies and Integration Points
It integrates with `CApi.sqlite3_prepare*`, bind APIs, column APIs, `sqlite3_step`, `sqlite3_reset`, `sqlite3_finalize`, `sqlite3_db_handle`, and trace callbacks.

## Risks
Unfinalized statements can hold locks and memory. Temporary column `sqlite3_value` wrappers are only valid while the statement row is active.

## Test Signals
`Tester1.testPrepare123()`, bind/fetch tests, SQL expansion tests, explain/status tests, and try-with-resources uses validate pointer invalidation, DB-handle lookup after finalize, readonly/busy status, tail parsing, and finalization behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_stmt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_value.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_value.java

## Purpose
`sqlite3_value` is the Java wrapper for C `sqlite3_value*` values passed through SQLite expressions, columns, and UDF arguments.

## Important APIs, Types, and Functions
The class extends `NativePointerHolder<sqlite3_value>` and has a private JNI-only constructor. It defines no methods beyond inherited pointer access.

## Control Flow
Instances are returned by column-value APIs, UDF arguments, preupdate APIs, and duplication APIs. Callers pass them into `CApi.sqlite3_value_*()` readers or result setters.

## State and Persistence Behavior
Most instances are transient and valid only for a callback or active row. Duplicated values must be freed with `sqlite3_value_free()`.

## Dependencies and Integration Points
It integrates with scalar/aggregate/window functions, `SqlFunction.Arguments`, column accessors, Java object value APIs, and FTS5 extension functions.

## Risks
Retaining non-duplicated values beyond their legal lifetime is invalid. Tests intentionally retain them to verify the JNI layer clears native pointers after callbacks.

## Test Signals
`Tester1` checks value type, bytes/text conversion, `sqlite3_value_frombind()`, NIO buffer exposure, Java object extraction, duplicated value freeing, and invalidation of saved UDF argument values.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_value.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5.java

## Purpose
`Fts5` is a final constants holder for FTS5 tokenization flags used by the JNI FTS5 bindings.

## Important APIs, Types, and Functions
It defines `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, `FTS5_TOKENIZE_AUX`, and `FTS5_TOKEN_COLOCATED`. The constructor is private.

## Control Flow
There is no runtime flow. Client or native-facing tokenizer code reads constants.

## State and Persistence Behavior
No mutable state exists.

## Dependencies and Integration Points
The constants correspond to SQLite FTS5 C API tokenization flags and are used with `fts5_tokenizer.xTokenize()` and `XTokenizeCallback`.

## Risks
The file explicitly marks itself incomplete and untested. Drift from SQLite's native constants would break tokenizer behavior.

## Test Signals
There is no direct test in `TesterFts5` for these constants; tokenizer callback tests indirectly cover tokenization through `Fts5ExtensionApi.xTokenize()` rather than custom tokenizer registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Context.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Context.java

## Purpose
`Fts5Context` wraps C-level `Fts5Context*` values passed to FTS5 extension functions.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5Context>` and adds no public methods.

## Control Flow
The native FTS5 bridge passes `Fts5Context` into `fts5_extension_function.call()` and `Fts5ExtensionApi` methods consume it.

## State and Persistence Behavior
The wrapper does not own its pointer. Its validity is tied to the current FTS5 auxiliary function invocation.

## Dependencies and Integration Points
It depends on `NativePointerHolder` and integrates with `Fts5ExtensionApi`, `fts5_extension_function`, and `fts5_api.xCreateFunction()`.

## Risks
Retaining the context after a callback can reference invalid native state. It is also not a general database handle; it is only meaningful with FTS5 extension APIs.

## Test Signals
`TesterFts5` exercises the wrapper through every custom auxiliary function, including rowid, column info, phrase iteration, auxdata, row count, query phrase, and tokenization calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Context.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5ExtensionApi.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5ExtensionApi.java

## Purpose
`Fts5ExtensionApi` is the Java wrapper for the FTS5 extension API table offered to auxiliary functions.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5ExtensionApi>`, exposes singleton `getInstance()`, and native methods for `xColumnCount`, `xColumnSize`, `xColumnText`, `xColumnTotalSize`, auxdata get/set, `xInst`, `xInstCount`, phrase counts/iteration, phrase size, `xQueryPhrase`, `xRowCount`, `xRowid`, `xTokenize`, and `xUserData`. `XQueryPhraseCallback` models the query-phrase callback.

## Control Flow
FTS5 auxiliary functions receive this object, use the current `Fts5Context`, and call native methods to inspect the matched row/query or maintain per-function auxdata.

## State and Persistence Behavior
`getInstance()` returns a singleton API wrapper. Auxdata state is maintained by SQLite/FTS5 and can hold Java objects; if auxdata has an `xDestroy()` method, JNI calls it when FTS5 finalizes that state.

## Dependencies and Integration Points
It depends on `OutputPointer`, `Fts5Context`, `Fts5PhraseIter`, `XTokenizeCallback`, nullable/not-null annotations, and FTS5 function registration through `fts5_api`.

## Risks
Most methods require a valid current `Fts5Context`; misuse outside callbacks can access invalid native state. Column indexes return range errors. Auxdata lifecycle differs from C by omitting an explicit delete callback argument.

## Test Signals
`TesterFts5` validates singleton behavior, user data, column counts/text/sizes/totals, auxdata persistence/clear, instance enumeration, phrase iteration by offset and column, row count, phrase size, query-phrase callbacks, rowid extremes, and tokenization.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5ExtensionApi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5PhraseIter.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5PhraseIter.java

## Purpose
`Fts5PhraseIter` wraps the native FTS5 phrase-iterator struct used by phrase iteration APIs.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5PhraseIter>` and contains private long fields `a` and `b`, which native code updates and reads.

## Control Flow
Java creates a new iterator, passes it to `Fts5ExtensionApi.xPhraseFirst()` or `xPhraseFirstColumn()`, then repeatedly passes the same object to `xPhraseNext()` or `xPhraseNextColumn()`.

## State and Persistence Behavior
Iterator state is mutable and native-owned. The fields are intentionally opaque to Java code.

## Dependencies and Integration Points
It integrates with `Fts5ExtensionApi` phrase iteration methods and output pointers for column/offset results.

## Risks
Reusing an iterator across different phrase scans or outside the active FTS5 callback can mix stale native state. Java code cannot inspect or repair the internal fields.

## Test Signals
`TesterFts5` uses fresh iterators in `fts5_pinst` and `fts5_pcolinst` auxiliary functions and compares phrase/column/offset lists against expected query results.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5PhraseIter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Tokenizer.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Tokenizer.java

## Purpose
`Fts5Tokenizer` is a Java wrapper for C-level `Fts5Tokenizer*` instances.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5Tokenizer>` and has a JNI-only private constructor. The comments identify it as incomplete and completely untested.

## Control Flow
Intended tokenizer APIs would pass this wrapper into tokenizer methods, especially `fts5_tokenizer.xTokenize()`.

## State and Persistence Behavior
The wrapper does not own the native pointer. Tokenizer lifecycle is controlled by FTS5/native registration code.

## Dependencies and Integration Points
It depends on `NativePointerHolder` and is referenced by `fts5_tokenizer.xTokenize()`.

## Risks
The incomplete/untested status is the dominant risk. There is no Java-side registration implementation in this file, and lifecycle semantics must match FTS5 expectations to avoid dangling tokenizer pointers.

## Test Signals
No direct test coverage was found in `TesterFts5`; current FTS5 tests exercise auxiliary-function tokenization via `Fts5ExtensionApi.xTokenize()` instead.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Tokenizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/TesterFts5.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/TesterFts5.java

## Purpose
`TesterFts5` is the FTS5-specific regression suite loaded by `Tester1` when SQLite is compiled with `ENABLE_FTS5`.

## Important APIs, Types, and Functions
It defines helper `sqlite3_exec()`, `do_execsql_test()`, and `create_test_functions()`, then tests `Fts5ExtensionApi`, `fts5_api`, `fts5_extension_function`, and FTS5 context/iterator callbacks. Registered auxiliary functions include `fts5_rowid`, `fts5_columncount`, `fts5_columnsize`, `fts5_columntext`, `fts5_columntotalsize`, `fts5_aux1/2`, `fts5_inst`, `fts5_pinst`, `fts5_pcolinst`, `fts5_rowcount`, `fts5_phrasesize`, `fts5_phrasehits`, and `fts5_tokenize`.

## Control Flow
The constructor calls synchronized `runTests()`, which executes `test1()` through `test6()`. Each test opens an in-memory DB, creates FTS5 tables, registers Java auxiliary functions through `fts5_api.getInstanceForDb(db)`, runs SQL queries, compares `Arrays.toString()` results, and closes the DB.

## State and Persistence Behavior
State is mostly local to test functions. `test1()` checks singleton API objects and verifies an auxiliary function's `xDestroy()` runs on database close. Auxdata tests verify values persist per function instance and can be cleared.

## Dependencies and Integration Points
It imports `CApi`, `Tester1` helpers, C API handle types, output pointers, and FTS5 bridge classes.

## Risks
Tests depend on FTS5 compile support and exact SQLite result/error wording for some range failures. String concatenation in callbacks is simple but not performance-oriented.

## Test Signals
Expected query result strings validate rowid extremes, column sizes/text/totals, auxdata behavior, instance and phrase iteration, row counts, phrase size, query-phrase callbacks, tokenizer output, singleton identity, and destroy callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/TesterFts5.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/XTokenizeCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/XTokenizeCallback.java

## Purpose
`XTokenizeCallback` models callbacks receiving tokens from FTS5 tokenization APIs.

## Important APIs, Types, and Functions
It declares `int call(int tFlags, byte[] txt, int iStart, int iEnd)`, where flags describe token properties, `txt` contains token bytes, and offsets identify the token range in the original input.

## Control Flow
`Fts5ExtensionApi.xTokenize()` or `fts5_tokenizer.xTokenize()` invokes the callback once per token. The returned int is a SQLite result code controlling continuation/error.

## State and Persistence Behavior
No state is stored. Implementations typically append decoded tokens to local lists or build an index.

## Dependencies and Integration Points
It is used by `Fts5ExtensionApi.xTokenize()` and `fts5_tokenizer.xTokenize()` and pairs with constants in `Fts5`.

## Risks
Callbacks must decode bytes with the intended encoding and respect offsets. Returning non-OK values changes native control flow.

## Test Signals
`TesterFts5.test6()` registers an auxiliary function that tokenizes input text, joins decoded UTF-8 tokens with plus signs, and validates expected token lists for simple text and punctuation/case cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/XTokenizeCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_api.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_api.java

## Purpose
`fts5_api` wraps the C `fts5_api*` table for registering FTS5 auxiliary functions.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<fts5_api>`, defines `iVersion = 2`, exposes synchronized native `getInstanceForDb(sqlite3 db)`, native `xCreateFunction(String name, Object userData, fts5_extension_function xFunction)`, and a convenience overload without user data.

## Control Flow
Client code asks for the per-database API instance, then registers Java `fts5_extension_function` objects. SQLite/FTS5 later invokes those functions during FTS5 queries.

## State and Persistence Behavior
The comments and tests indicate one singleton wrapper per database. Registered functions and user data are retained by the native/JNI layer until FTS5 or the DB releases them.

## Dependencies and Integration Points
It depends on `sqlite3`, `NativePointerHolder`, `fts5_extension_function`, and annotations. It is the registration gateway for `Fts5ExtensionApi` callbacks.

## Risks
Tokenizer creation/find APIs are still TODO/commented out. Registering functions requires correct destroy/lifetime handling for Java callback objects and user data.

## Test Signals
`TesterFts5.test1()` validates per-DB singleton behavior and user-data round trip; `create_test_functions()` validates mass registration and query execution of registered auxiliary functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_api.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_extension_function.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_extension_function.java

## Purpose
`fts5_extension_function` is the Java equivalent of C's FTS5 auxiliary function callback type.

## Important APIs, Types, and Functions
It declares `void call(Fts5ExtensionApi ext, Fts5Context fCx, sqlite3_context pCx, sqlite3_value argv[])` and `void xDestroy()`. Nested abstract class `Abstract` keeps `call()` abstract and supplies a no-op `xDestroy()`.

## Control Flow
After registration through `fts5_api.xCreateFunction()`, FTS5 invokes `call()` for matching SQL auxiliary function calls. Implementations use `ext` and `fCx` to inspect FTS5 state and `pCx`/`sqlite3_result_*()` to return SQL results.

## State and Persistence Behavior
Implementations may hold Java state or user data; `xDestroy()` is called when SQLite destroys the registered function. Callback arguments are invocation-scoped native wrappers.

## Dependencies and Integration Points
It integrates `Fts5ExtensionApi`, `Fts5Context`, `sqlite3_context`, `sqlite3_value`, and registration through `fts5_api`.

## Risks
Implementations must not retain invocation-scoped wrappers and should translate errors into SQLite results or exceptions handled by the JNI layer. `xDestroy()` should be lightweight and safe.

## Test Signals
`TesterFts5` defines many anonymous implementations, verifies result-producing behavior, and checks `xDestroy()` is called for an auxiliary function when the database closes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_extension_function.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_tokenizer.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_tokenizer.java

## Purpose
`fts5_tokenizer` is a Java wrapper for the C `fts5_tokenizer` method table, currently focused on tokenization.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<fts5_tokenizer>` and exposes native `int xTokenize(Fts5Tokenizer t, int tokFlags, byte[] pText, XTokenizeCallback callback)`.

## Control Flow
Given a native tokenizer instance and text bytes, `xTokenize()` delegates to the tokenizer's native `xTokenize` implementation and invokes the Java token callback for each token.

## State and Persistence Behavior
The wrapper does not own native tokenizer state. The `Fts5Tokenizer` argument represents the tokenizer instance whose lifecycle is external to this object.

## Dependencies and Integration Points
It depends on `NativePointerHolder`, `Fts5Tokenizer`, `XTokenizeCallback`, and `NotNull`. Commented C signatures show intended future create/delete integration.

## Risks
Creation and discovery of tokenizers are not implemented here, making this API incomplete. Incorrect lifecycle handling for `Fts5Tokenizer` could call into freed native state.

## Test Signals
No direct `TesterFts5` coverage was found for this wrapper; existing tokenization coverage uses `Fts5ExtensionApi.xTokenize()` instead.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_tokenizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/AggregateFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/AggregateFunction.java

## Purpose
`wrapper1.AggregateFunction<T>` is the higher-level wrapper1 abstraction for aggregate SQL functions, marked experimental/incomplete/untested.

## Important APIs, Types, and Functions
It implements `SqlFunction`, requires `xStep(SqlFunction.Arguments args)` and `xFinal(SqlFunction.Arguments args)`, and provides no-op `xDestroy()`. Nested `PerContextState<T>` maps `sqlite3_context.getAggregateContext()` keys to `ValueHolder<T>` values. Protected helpers `getAggregateState()` and `takeAggregateState()` expose that map to subclasses.

## Control Flow
Wrapper adapters in `SqlFunction` convert low-level JNI callbacks into `SqlFunction.Arguments`. Aggregate implementations fetch or initialize state during `xStep()` and remove/finalize it during `xFinal()`.

## State and Persistence Behavior
The per-function instance owns a `PerContextState` map. Each aggregate invocation in a statement gets a separate key; finalization removes it. Empty result sets can produce null state.

## Dependencies and Integration Points
It depends on wrapper1 `SqlFunction.Arguments`, wrapper1 `ValueHolder`, and low-level `sqlite3_context` aggregate keys via the arguments object.

## Risks
The map is unsynchronized and assumes callbacks for a given function instance do not run concurrently. Forgetting `takeAggregateState()` leaks per-context entries. Documentation contains stale `SQLFunction.PerContextState` references that should likely say `SqlFunction` or this class.

## Test Signals
Direct wrapper1 tests are not in this work item. Low-level `Tester1.testUdfAggregate()` covers the underlying aggregate-context behavior used by this helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/AggregateFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ScalarFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ScalarFunction.java

## Purpose
`wrapper1.ScalarFunction` is the higher-level wrapper1 abstraction for scalar SQL functions.

## Important APIs, Types, and Functions
It implements `SqlFunction`, requires `xFunc(SqlFunction.Arguments args)`, and offers no-op `xDestroy()`. The API hides low-level `sqlite3_context` and `sqlite3_value[]` behind `SqlFunction.Arguments`.

## Control Flow
`SqlFunction.ScalarAdapter` receives low-level JNI callbacks, constructs an `Arguments` object, calls this `xFunc()`, and converts thrown exceptions into SQLite result errors.

## State and Persistence Behavior
The base class stores no state. Subclasses may hold Java state and can use argument/result helpers during callback execution.

## Dependencies and Integration Points
It depends on `SqlFunction` and is registered through wrapper1 database APIs that adapt it to `org.sqlite.jni.capi.ScalarFunction`.

## Risks
Implementations must not retain `Arguments` or objects derived from invocation-scoped native handles. The wrapper is higher-level but still executes inside SQLite callback constraints.

## Test Signals
No direct wrapper1 tests are included here. Equivalent low-level scalar behavior is tested in `Tester1.testUdf1()`, `testUdfThrows()`, and `testUdfJavaObject()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ScalarFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqlFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqlFunction.java

## Purpose
`SqlFunction` is the wrapper1 marker interface and adapter hub for scalar, aggregate, and window UDFs. It raises the API above raw JNI callback types while still delegating to `CApi`.

## Important APIs, Types, and Functions
The interface exports UDF flags and encodings from `CApi`. Nested `Arguments` wraps `sqlite3_context` plus `sqlite3_value[]`, provides typed getters (`getInt`, `getText16`, `getObject`, metadata methods), result setters (`resultInt`, `resultText`, `resultError`, `resultArg`, `resultZeroBlob`, etc.), auxdata helpers, DB lookup, and iterable `Arg` proxies. `ScalarAdapter`, `AggregateAdapter`, and `WindowAdapter` adapt wrapper1 function classes to low-level `org.sqlite.jni.capi` function classes.

## Control Flow
Registration code creates an adapter around a wrapper1 implementation. SQLite invokes the low-level adapter, which constructs an `Arguments` object and calls wrapper methods. Exceptions are caught and reported with `sqlite3_result_error()`.

## State and Persistence Behavior
`Arguments` is per callback and holds invocation-scoped native wrappers. Adapters hold the user implementation and forward `xDestroy()`. Auxdata is stored in SQLite through `sqlite3_set_auxdata()` and fetched by argument index.

## Dependencies and Integration Points
It depends on `CApi`, `sqlite3_context`, `sqlite3_value`, wrapper1 `Sqlite`, `ScalarFunction`, `AggregateFunction`, and `WindowFunction`.

## Risks
Index validation is explicit for argument access, but retaining `Arguments.Arg` after the callback remains unsafe. `getDb()` can return null if the database has been closed during a UDF. Adapters intentionally swallow Java exceptions into SQLite result errors, so callers must inspect SQLite step results.

## Test Signals
No direct wrapper1 tests are in this subset. Low-level tests cover the underlying result/error/value/auxdata behavior; wrapper-specific tests should assert adapter exception translation, iterable arguments, auxdata bounds checks, and `getDb()` mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqlFunction.java -->
