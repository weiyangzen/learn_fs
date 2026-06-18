# subset-b-008742 Research

Grouped research report for SQLite JNI C API header, annotation helpers, and core `org.sqlite.jni.capi` callback/support classes. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/c/sqlite3-jni.h -->
# sources/storage-engines/sqlite/ext/jni/src/c/sqlite3-jni.h

## Purpose
Machine-generated JNI header for the SQLite Java binding. It exposes native entry points for `org.sqlite.jni.capi.CApi`, plus JNI declarations for `SQLTester` and FTS5 helper classes. It is the ABI contract between Java native methods and the C implementation in `sqlite3-jni.c`.

## Important APIs, Types, And Functions
The header defines `org_sqlite_jni_capi_CApi_*` constants mirroring SQLite integer constants and declares `JNIEXPORT` functions for database handles, statements, blobs, backup, binding, column access, result values, hooks, configuration, preupdate APIs, value accessors, status APIs, NIO buffer support, Java object binding, and shutdown/thread-cache maintenance. Additional declarations cover `SQLTester.strglob`, `SQLTester.installCustomExtensions`, `Fts5ExtensionApi` methods, `fts5_api.getInstanceForDb`, `fts5_api.xCreateFunction`, and `fts5_tokenizer.xTokenize`.

## Control Flow
There is no executable control flow in this header. Runtime dispatch is controlled by the JVM resolving Java native method signatures to the C symbols declared here. Overloaded Java native methods are represented with JNI-mangled suffixes, for example the two `sqlite3_db_config` forms.

## State And Persistence Behavior
No state is stored here. The header describes functions that manipulate SQLite persistent state through database files and transient JNI state through native pointer wrappers, callbacks, direct buffers, and per-thread caches. Staleness risk is ABI-level: if Java native declarations and this generated header diverge, class loading or native calls fail.

## Dependencies And Integration Points
Depends on `jni.h`, `org.sqlite.jni.capi.CApi`, `SQLTester`, and `org.sqlite.jni.fts5` Java classes. It integrates with the JNI C implementation, the Java wrapper objects derived from `NativePointerHolder`, and SQLite optional features such as FTS5, preupdate hook, column metadata, normalization, and SQL log.

## Risks And Edge Cases
Because this is generated, manual edits are likely to be lost and can desynchronize native signatures. Pointer arguments appear as `jlong` or `jobject`, so C implementation must validate null and stale pointer cases. The header includes several logical API families in one file, so partial regeneration can miss FTS5 or tester declarations. Constant drift from SQLite upstream can cause Java callers to pass wrong opcodes or flags.

## Test Signals
Signals are successful native library load, `CApi.init()` resolution, JNI compilation against this header, Java tests exercising `CApi`, `SQLTester`, and FTS5 methods, and failures such as `UnsatisfiedLinkError` when signatures do not match.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/c/sqlite3-jni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Experimental.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Experimental.java

## Purpose
Defines a source-retained annotation used to label JNI APIs that are unstable and may change or be removed.

## Important APIs, Types, And Functions
`@Experimental` is documented, retained only in source, and targets methods, constructors, and types. It has no members.

## Control Flow
No runtime flow exists because the annotation is not retained in class files for runtime reflection.

## State And Persistence Behavior
No state or persistence. It affects documentation and compile-time source readability only.

## Dependencies And Integration Points
Depends on `java.lang.annotation`. Used by `CApi` to mark direct `ByteBuffer`/NIO related APIs and feature probes.

## Risks And Edge Cases
Because retention is `SOURCE`, tools running on bytecode cannot detect it. Client code must not treat annotated APIs as stable even if they compile.

## Test Signals
Compile and javadoc generation are the main signals. Runtime tests will not observe this annotation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Experimental.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/NotNull.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/NotNull.java

## Purpose
Documents parameters that must not be Java null and, for SQLite handle wrappers or native pointer longs, must not represent a closed/finalized or invalid C resource.

## Important APIs, Types, And Functions
`@NotNull` is documented, source-retained, and targets parameters. Its javadoc defines null broadly to include stale SQLite handles and invalid native pointer values.

## Control Flow
No direct runtime flow. Annotated methods may still throw Java null-related exceptions or return SQLite misuse/error codes depending on wrapper behavior and native API armor.

## State And Persistence Behavior
No state. The annotation documents ownership/lifetime preconditions around native resources whose real state lives in SQLite C objects and `NativePointerHolder.nativePointer`.

## Dependencies And Integration Points
Depends on `java.lang.annotation` and references `sqlite3`, `sqlite3_stmt`, and `sqlite3_context` wrapper classes. Heavily used throughout `CApi` and callback signatures.

## Risks And Edge Cases
It is informational only and not enforced programmatically. Passing null or stale handles can produce non-standard result codes, Java exceptions, suppressed callback errors, or invalid native behavior despite `SQLITE_ENABLE_API_ARMOR`.

## Test Signals
Compilation and javadoc links confirm syntax. Behavioral tests should cover null/stale handle paths on public wrappers where those are intended to return `SQLITE_MISUSE` rather than crash.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/NotNull.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Nullable.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Nullable.java

## Purpose
Documents parameters and callback arguments that may legally be null in the SQLite JNI binding.

## Important APIs, Types, And Functions
`@Nullable` is documented, source-retained, and targets parameters. It has no members.

## Control Flow
No runtime flow. It documents code paths where Java wrappers translate null into SQLite null values, clear callbacks, or optional output parameters.

## State And Persistence Behavior
No state. It communicates acceptable nullability for APIs that may mutate SQLite state or callback registrations.

## Dependencies And Integration Points
Depends on `java.lang.annotation`. Used in `CApi` overloads for nullable strings, byte arrays, callbacks, output pointers, blobs, and Java objects.

## Risks And Edge Cases
Retention is source-only and not enforced. A nullable parameter can still carry semantic differences, for example binding SQL NULL, clearing a hook, or omitting an output value.

## Test Signals
Compilation and generated docs are primary. API tests should verify null behavior for callbacks, bind/result helpers, and optional output pointers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Nullable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/package-info.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/package-info.java

## Purpose
Provides package-level javadoc for SQLite JNI-specific annotation helpers.

## Important APIs, Types, And Functions
Declares package `org.sqlite.jni.annotation` and documents that it houses annotations for the SQLite3 C API JNI bindings.

## Control Flow
No executable flow.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Integrated with javadoc for `Experimental`, `NotNull`, and `Nullable`, and with annotated APIs under `org.sqlite.jni.capi`.

## Risks And Edge Cases
Low risk. The useful behavior is documentation consistency; package renames or missing package info would degrade generated docs.

## Test Signals
Javadoc/package documentation generation and Java compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AbstractCollationCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AbstractCollationCallback.java

## Purpose
Convenience abstract base for SQLite collation callbacks that supplies a no-op destroy hook.

## Important APIs, Types, And Functions
Extends `CollationCallback` and `XDestroyCallback`. Implementers must provide `call(byte[] lhs, byte[] rhs)` using `memcmp()`-style ordering. `xDestroy()` is optional and defaults to no-op.

## Control Flow
SQLite invokes `call()` through JNI during string comparison for a registered collation and invokes `xDestroy()` when the collation is destroyed.

## State And Persistence Behavior
No built-in state. Subclasses may carry Java state retained by native callback mappings for the lifetime of the registered collation.

## Dependencies And Integration Points
Depends on `CollationCallback`, `XDestroyCallback`, and `@NotNull`. Registered through `CApi.sqlite3_create_collation`.

## Risks And Edge Cases
Comparison must obey a total order and must not throw. Stateful subclasses need cleanup in `xDestroy()` if they hold external resources.

## Test Signals
Create a custom collation, run sorted queries, and verify destroy callbacks are invoked when replaced, connection closes, or function mappings are cleared.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AbstractCollationCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AggregateFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AggregateFunction.java

## Purpose
Base class for Java aggregate SQL functions registered through `sqlite3_create_function`.

## Important APIs, Types, And Functions
Defines abstract `xStep(sqlite3_context, sqlite3_value[])` and `xFinal(sqlite3_context)`, optional `xDestroy()`, and nested `PerContextState<T>`. Protected helpers `getAggregateState()` and `takeAggregateState()` manage per-aggregate accumulator state.

## Control Flow
SQLite calls `xStep()` for each row, then `xFinal()` once per aggregate invocation. `getAggregateState()` uses `sqlite3_context.getAggregateContext(true)` to map a C aggregate context key to a Java `ValueHolder<T>`. `takeAggregateState()` removes the mapping at finalization.

## State And Persistence Behavior
State is transient Java heap state stored in a `HashMap<Long, ValueHolder<T>>`. The key comes from native aggregate context allocation. Callers must remove state in `xFinal()` to avoid retaining per-statement state.

## Dependencies And Integration Points
Depends on `SQLFunction`, `sqlite3_context`, `sqlite3_value`, and `ValueHolder`. The JNI layer recognizes the callback method names/signatures when installing UDFs.

## Risks And Edge Cases
If a query has no result rows, `xFinal()` may see no existing state. Exceptions in `xStep()` are suppressed with possible debug output; exceptions in `xFinal()` are converted to result errors. Missing `takeAggregateState()` leaks Java state until the function object is discarded.

## Test Signals
Register aggregate UDFs over grouped and empty inputs, multiple invocations in one `SELECT`, exception paths, and `xDestroy()` cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AggregateFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AuthorizerCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AuthorizerCallback.java

## Purpose
Java callback interface for `sqlite3_set_authorizer`.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call(int opId, String s1, String s2, String s3, String s4)`, with all string arguments nullable.

## Control Flow
SQLite invokes the callback while compiling SQL statements. Return values follow SQLite authorizer semantics such as `SQLITE_OK`, `SQLITE_DENY`, and `SQLITE_IGNORE`.

## State And Persistence Behavior
The interface stores no state. Implementations may keep policy state and are retained by the native callback registration on a database handle.

## Dependencies And Integration Points
Depends on `CallbackProxy` and nullability annotations. Installed via `CApi.sqlite3_set_authorizer`.

## Risks And Edge Cases
Thrown exceptions are converted to database-level errors and suppressed. Policy code runs during prepare/compile and must avoid reentrant or slow operations.

## Test Signals
Prepare statements that trigger read, write, pragma, attach, function, and transaction authorizer opcodes and verify return-code handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AuthorizerCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AutoExtensionCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AutoExtensionCallback.java

## Purpose
Java representation of a SQLite auto-extension callback invoked for newly opened database connections.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call(sqlite3 db)`. The javadoc documents recursion and statefulness hazards.

## Control Flow
After registration through `CApi.sqlite3_auto_extension`, SQLite/JNI invokes the callback for database opens. Return codes influence open error handling and exceptions become database error strings.

## State And Persistence Behavior
The interface has no fields. Registered callback objects are retained globally by the JNI/native auto-extension registry until canceled or reset.

## Dependencies And Integration Points
Integrates with `CApi.sqlite3_auto_extension`, `sqlite3_cancel_auto_extension`, and `sqlite3_reset_auto_extension`. Depends on `sqlite3` wrapper and `CallbackProxy`.

## Risks And Edge Cases
Opening another database inside the callback can recurse indefinitely. Mutating the extension list while extensions are running has unpredictable ordering. Closing the provided database from the callback is undefined.

## Test Signals
Register, cancel, and reset auto extensions; open databases; verify callback order, error propagation, and no recursion for safe implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AutoExtensionCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/BusyHandlerCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/BusyHandlerCallback.java

## Purpose
Callback interface for SQLite busy-handler decisions.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call(int n)`, where `n` is SQLite's busy invocation count.

## Control Flow
SQLite invokes the callback when a database lock cannot be acquired. Return non-zero to retry and zero to stop waiting.

## State And Persistence Behavior
No intrinsic state. Stateful implementations are retained by the database connection registration and may count attempts or consult application cancellation state.

## Dependencies And Integration Points
Installed through `CApi.sqlite3_busy_handler`; related to `sqlite3_busy_timeout`.

## Risks And Edge Cases
Callback must be fast and should not reenter the same connection in unsafe ways. Exceptions follow `CallbackProxy` no-throw semantics and may be suppressed.

## Test Signals
Two-connection lock contention tests, retry count assertions, clearing the handler with null, and timeout interaction checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/BusyHandlerCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CApi.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CApi.java

## Purpose
Primary Java surface for the SQLite C API JNI binding. It loads `sqlite3-jni`, declares native methods, wraps raw pointer-oriented native calls with safer Java object overloads, provides UTF conversion helpers, exposes SQLite constants, and adds Java-specific convenience APIs.

## Important APIs, Types, And Functions
Major API families include open/close, prepare/prepare multi, bind/result/column/value access, blob I/O, backup, hooks, authorizer, collation, UDF creation, aggregate context, auxdata, config/db_config/status, preupdate hooks, trace/update/commit/rollback/progress callbacks, keyword and compile option helpers, error handling, memory/shutdown/thread maintenance, and experimental NIO direct-buffer functions. `nulTerminateUtf8()` protects C APIs needing NUL-terminated UTF-8. `JNI_SUPPORTS_NIO` caches native direct-buffer support after `init()`.

## Control Flow
Class initialization loads the native library, initializes constants through native version calls, calls native `init()`, then probes NIO support. Most public wrappers unwrap `NativePointerHolder` instances to raw pointers, call private native methods, and sometimes clear or transfer ownership. `sqlite3_prepare_multi()` loops over UTF-8 input, prepares one statement at a time using tail offsets, passes ownership to a `PrepareMultiCallback`, and converts callback exceptions into database errors.

## State And Persistence Behavior
Persistent database state is owned by SQLite files and handles. Java-side state includes static constants, NIO support flag, callback objects held by native registrations, native pointer values in handle wrappers, and output pointer objects. Ownership-sensitive methods clear native pointers on `close`, `close_v2`, `finalize`, `blob_close`, `backup_finish`, and `value_free` to avoid stale Java handles.

## Dependencies And Integration Points
Depends on `StandardCharsets`, `Arrays`, annotations, `OutputPointer`, handle wrappers, callback interfaces, `SQLFunction`, `AggregateFunction`, and native implementation symbols declared in `sqlite3-jni.h`. It is the integration point for wrapper-level APIs under `wrapper1`, tests, and FTS5 helpers.

## Risks And Edge Cases
UTF-8 versus JNI modified UTF-8 is a central risk; byte-array APIs must use standard UTF-8 and some string APIs must append NUL terminators. Null/stale handles annotated `@NotNull` may still produce Java exceptions or SQLite misuse codes. Direct buffer APIs are experimental and can crash if buffers are mutated concurrently or native direct access is unavailable. Preupdate value handles must not escape callback scope. Shutdown while handles are active leaks or leaves undefined behavior.

## Test Signals
Signals include loading `sqlite3-jni`, sanity SQL tests, bind/column/value round trips for all supported types, prepare tail handling, multi-statement callback ownership, UDF/aggregate/window tests, hook callback tests, null/stale handle checks, direct-buffer tests gated on `sqlite3_jni_supports_nio()`, and constant parity with upstream SQLite.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CApi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CallbackProxy.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CallbackProxy.java

## Purpose
Marker interface and documentation anchor for Java callbacks that proxy SQLite C callbacks.

## Important APIs, Types, And Functions
Defines no methods. Its javadoc states common naming rules and exception-handling expectations for callback interfaces.

## Control Flow
No executable flow. Implementing interfaces define callback-specific `call()` methods invoked from JNI.

## State And Persistence Behavior
No state. Native code may retain instances of implementing callback objects depending on the registration API.

## Dependencies And Integration Points
Implemented by callback interfaces such as busy handler, authorizer, hooks, collation, auto-extension, and prepare multi.

## Risks And Edge Cases
The no-throw convention is documented rather than enforced. Exceptions may be converted only where SQLite has an error reporting path; otherwise they are suppressed.

## Test Signals
Indirect callback tests should verify thrown exceptions do not escape native frames and are translated or suppressed according to each callback contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CallbackProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationCallback.java

## Purpose
Interface for custom SQLite collation implementations in Java.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and `XDestroyCallback`. Declares `int call(byte[] lhs, byte[] rhs)` with `memcmp()` semantics and `void xDestroy()`.

## Control Flow
Registered collations are invoked during SQL comparison/sort operations. SQLite invokes `xDestroy()` when the collation is replaced or destroyed.

## State And Persistence Behavior
No interface state. Implementations may hold comparator state retained by the database connection's collation registry.

## Dependencies And Integration Points
Registered through `CApi.sqlite3_create_collation`; `AbstractCollationCallback` supplies a no-op destroy method.

## Risks And Edge Cases
Invalid comparator semantics can corrupt query ordering or indexes using the collation. Exceptions should not escape JNI callback dispatch. Byte arrays represent text encoding chosen by SQLite/JNI and should be compared consistently.

## Test Signals
Sort and equality tests using custom collations, replacement/destroy cleanup tests, and exception-path tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationNeededCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationNeededCallback.java

## Purpose
Callback interface for lazy collation registration when SQLite encounters an unknown collation.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `void call(sqlite3 db, int eTextRep, String collationName)`.

## Control Flow
SQLite invokes the callback from `sqlite3_collation_needed` handling. Implementations normally call `sqlite3_create_collation` for the requested name.

## State And Persistence Behavior
No intrinsic state. Registration persists on the database handle until replaced or closed.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_collation_needed`, which behaves like SQLite's UTF-16 collation-needed interface because Java strings are UTF-16.

## Risks And Edge Cases
SQLite has no callback error channel here, so exceptions are suppressed. Implementations must avoid recursive failures where the requested collation is never installed.

## Test Signals
Prepare/query SQL using an initially unknown collation and verify callback installation, encoding value, and suppressed exception behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationNeededCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CommitHookCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CommitHookCallback.java

## Purpose
Java callback interface for SQLite commit hooks.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call()`. Return semantics follow `sqlite3_commit_hook`.

## Control Flow
SQLite calls the hook during transaction commit. A non-zero return requests commit rollback.

## State And Persistence Behavior
No interface state. Registered callback state is associated with a database handle until changed.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_commit_hook`, which returns the previous hook object.

## Risks And Edge Cases
Exceptions are translated to database-level errors. Commit hooks run inside transaction processing and should avoid unsafe reentrancy.

## Test Signals
Transactions with zero/non-zero hook returns, previous-hook return checks, rollback behavior, and exception translation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CommitHookCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigLogCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigLogCallback.java

## Purpose
Callback interface for SQLite global `SQLITE_CONFIG_LOG` logging.

## Important APIs, Types, And Functions
Declares `void call(int errCode, String msg)`.

## Control Flow
After installation via `CApi.sqlite3_config(ConfigLogCallback)`, SQLite invokes the callback for global log events.

## State And Persistence Behavior
No interface state. The installed callback is global SQLite configuration state, not per database.

## Dependencies And Integration Points
Used by `CApi.sqlite3_config(ConfigLogCallback)` and native `sqlite3_config(SQLITE_CONFIG_LOG, ...)`.

## Risks And Edge Cases
`sqlite3_config` must not race other SQLite API calls. Logging callbacks should avoid calling back into unsafe SQLite operations or throwing.

## Test Signals
Install/clear logging callback before initialization-sensitive operations, trigger known log events, and verify message/error code delivery.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigLogCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigSqlLogCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigSqlLogCallback.java

## Purpose
Callback interface for optional SQLite SQL logging support through `SQLITE_CONFIG_SQLLOG`.

## Important APIs, Types, And Functions
Declares `void call(sqlite3 db, String msg, int msgType)`.

## Control Flow
If the native library is built with `SQLITE_ENABLE_SQLLOG`, SQLite invokes this callback for SQL log events after global installation.

## State And Persistence Behavior
No interface state. The callback is global process-level SQLite config state and receives database handle wrappers for events.

## Dependencies And Integration Points
Installed through `CApi.sqlite3_config(ConfigSqlLogCallback)`. If SQL log support is absent, the wrapper returns `SQLITE_MISUSE`.

## Risks And Edge Cases
Feature availability depends on native build flags. Like other global config, it is not thread-safe relative to concurrent SQLite use.

## Test Signals
Build-flag-sensitive tests: expect callback delivery when enabled and `SQLITE_MISUSE` when disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigSqlLogCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/NativePointerHolder.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/NativePointerHolder.java

## Purpose
Base class for Java wrappers that carry native SQLite pointer values across JNI while preserving some Java type separation.

## Important APIs, Types, And Functions
Generic `NativePointerHolder<ContextType>` contains private volatile `long nativePointer`, package-private `clearNativePointer()`, and public `getNativePointer()`.

## Control Flow
JNI sets the private field directly. Public wrappers pass `getNativePointer()` to native methods. Close/finalize-style CApi wrappers call `clearNativePointer()` to transfer the old pointer to native cleanup and zero the Java handle.

## State And Persistence Behavior
The only state is the volatile pointer value. The object does not own native memory by itself; ownership is controlled by the SQLite API and explicit close/finalize/free methods.

## Dependencies And Integration Points
Subclassed by opaque handle wrappers such as `sqlite3`, `sqlite3_stmt`, `sqlite3_blob`, `sqlite3_backup`, `sqlite3_context`, and `sqlite3_value`.

## Risks And Edge Cases
Using a handle after `clearNativePointer()` produces a zero pointer. The class does not prevent double-close races or operations on stale handles beyond clearing local state. Volatile gives visibility but not full lifecycle synchronization.

## Test Signals
Open/finalize/close tests should verify pointer clearing, double close behavior, and misuse handling for stale wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/NativePointerHolder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/OutputPointer.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/OutputPointer.java

## Purpose
Defines Java holder classes that model C output pointer parameters for SQLite JNI methods.

## Important APIs, Types, And Functions
Nested classes include opaque handle outputs `sqlite3`, `sqlite3_blob`, `sqlite3_stmt`, `sqlite3_value` with private `value`, `get()`, `clear()`, and `take()`, plus primitive/object outputs `Bool`, `Int32`, `Int64`, `String`, `ByteArray`, and `ByteBuffer` with public `value` and accessors.

## Control Flow
Callers instantiate an output holder, pass it to a `CApi` method, then read with `get()` or transfer with `take()`. JNI mutates private opaque values directly; Java code cannot set handle outputs.

## State And Persistence Behavior
All state is transient Java heap state. `take()` clears opaque outputs so ownership of returned wrappers is explicit. The classes are not thread-safe and should not be shared across threads.

## Dependencies And Integration Points
Used by open, prepare, blob open, preupdate old/new, db/status APIs, table metadata, FTS5 APIs, and other JNI methods needing C-style out parameters.

## Risks And Edge Cases
Sharing output holders across threads can corrupt assumptions around native state. Forgetting `take()` may leave aliases to a handle. Primitive outputs are publicly mutable, so callers can overwrite returned values accidentally.

## Test Signals
Open/prepare/blob/preupdate/status tests using output holders, `take()` clearing checks, null optional output pointer tests, and thread confinement review.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/OutputPointer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PrepareMultiCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PrepareMultiCallback.java

## Purpose
Callback interface used by `CApi.sqlite3_prepare_multi` to process each prepared statement from a multi-statement SQL input.

## Important APIs, Types, And Functions
Declares `int call(sqlite3_stmt st)`. Nested `Finalize` wraps another callback and always finalizes each statement. Nested `StepAll` steps through a statement until completion and returns zero for `SQLITE_DONE`.

## Control Flow
`sqlite3_prepare_multi` prepares statements one by one and transfers each non-empty statement to `call()`. The callback decides whether to finalize, retain, step, or stop. Non-zero returns stop the loop.

## State And Persistence Behavior
The interface has no state. Ownership of each `sqlite3_stmt` transfers to the callback. `Finalize` enforces cleanup in a `finally` block.

## Dependencies And Integration Points
Depends on `CallbackProxy`, `sqlite3_stmt`, and `CApi.sqlite3_step/finalize` constants. Used by Java multi-statement execution helpers and tests.

## Risks And Edge Cases
If a callback neither finalizes nor stores a statement for later finalization, native statements leak. Exceptions are converted by `sqlite3_prepare_multi` into database errors. `StepAll` itself does not finalize unless wrapped with `Finalize`.

## Test Signals
Multi-statement inputs with whitespace/comments, callback stop codes, exception conversion, finalization verification, and stepping result handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PrepareMultiCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PreupdateHookCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PreupdateHookCallback.java

## Purpose
Java callback interface for SQLite preupdate hook notifications.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `void call(sqlite3 db, int op, String dbName, String dbTable, long iKey1, long iKey2)`.

## Control Flow
When preupdate support is enabled and a hook is installed, SQLite calls this before row changes. Callers can use related `CApi.sqlite3_preupdate_*` methods during callback scope.

## State And Persistence Behavior
No interface state. Callback registration lives on the database handle. Values returned by preupdate old/new APIs are valid only during the hook callback.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_preupdate_hook`. Integrates with `sqlite3_preupdate_count`, `depth`, `blobwrite`, `old`, and `new`.

## Risks And Edge Cases
Feature may be absent unless built with `SQLITE_ENABLE_PREUPDATE_HOOK`. Exceptions are translated to db errors and suppressed. Holding `sqlite3_value` references after callback scope is unsafe.

## Test Signals
Insert/update/delete cases, old/new value extraction during callback, disabled-build `SQLITE_MISUSE` behavior, and exception translation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PreupdateHookCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ProgressHandlerCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ProgressHandlerCallback.java

## Purpose
Callback interface for SQLite progress-handler interruption decisions.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call()`.

## Control Flow
SQLite invokes the callback every configured number of virtual machine opcodes. Return non-zero to interrupt the running operation.

## State And Persistence Behavior
No interface state. Installed callback is associated with a database handle and can consult external cancellation state.

## Dependencies And Integration Points
Installed with `CApi.sqlite3_progress_handler`.

## Risks And Edge Cases
Runs frequently on query execution hot paths, so it must be cheap. Exceptions are converted to database error information and suppressed.

## Test Signals
Long-running query interruption, clearing handler with null, invocation count behavior, and exception-to-error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ProgressHandlerCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ResultCode.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ResultCode.java

## Purpose
Enum mapping SQLite core and extended integer result codes to named Java values for higher-level code.

## Important APIs, Types, And Functions
Each enum entry stores public final `int value`, initialized from `CApi` constants. `getEntryForInt(int rc)` looks up a result code through nested `ResultCodeMap`, which stores a static `HashMap<Integer, ResultCode>`.

## Control Flow
Each enum constructor inserts itself into the map. Lookup returns the enum value or null when no entry exists.

## State And Persistence Behavior
State is process-local static enum/map data initialized at class load. No persistence.

## Dependencies And Integration Points
Depends on `CApi` constants, which require native library initialization for version-related constants but result code constants are Java static finals. Useful for wrappers and diagnostics that want names instead of raw integers.

## Risks And Edge Cases
It only includes codes listed at compile time; new SQLite extended codes return null until updated. Static initialization order is handled by the nested map indirection.

## Test Signals
Assert every enum maps back from its integer value, representative core/extended code lookups, and null for unknown integers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ResultCode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/RollbackHookCallback.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/RollbackHookCallback.java

## Purpose
Java callback interface for SQLite rollback hooks.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `void call()`.

## Control Flow
SQLite invokes the hook when a transaction rolls back.

## State And Persistence Behavior
No interface state. Registration is database-handle state until replaced or cleared.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_rollback_hook`, which returns the previous hook object.

## Risks And Edge Cases
Exceptions are translated to database-level errors. Callback code runs during rollback handling and should avoid unsafe connection reentry.

## Test Signals
Explicit rollback and failed commit scenarios, previous-hook return checks, clearing hook, and exception translation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/RollbackHookCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLFunction.java

## Purpose
Marker base interface for Java SQL functions installed through `CApi.sqlite3_create_function`.

## Important APIs, Types, And Functions
Defines no methods. The javadoc describes expected callback shapes for scalar, aggregate, and window function implementations recognized by JNI.

## Control Flow
No direct flow in this interface. Native UDF dispatch checks for expected method names/signatures on objects passed as `SQLFunction` implementations.

## State And Persistence Behavior
No state. Implementing function objects may carry per-function state and are retained by SQLite/JNI until function destruction.

## Dependencies And Integration Points
Implemented by function classes such as scalar, aggregate, and window UDF helpers. Used by `CApi.sqlite3_create_function`.

## Risks And Edge Cases
Because it is a marker, compile-time enforcement of required callback methods is limited to helper classes/interfaces. Custom implementations must match JNI-dispatched method signatures exactly.

## Test Signals
Register scalar, aggregate, and window functions; verify callbacks dispatch, state cleanup, exception handling, and invalid custom implementation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLFunction.java -->
