# subset-b-008744 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Sqlite.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Sqlite.java

## Purpose
`Sqlite.java` is the high-level Java `wrapper1` database API over `org.sqlite.jni.capi.CApi`. It turns raw JNI SQLite handles into safer Java objects with result-code constants, argument checks, exceptions, `AutoCloseable` resource ownership, Java callback adapters, and nested wrappers for statements, backups, blobs, tracing, hooks, collations, status, and auto-extensions.

## Important APIs, types, and functions
- `Sqlite` wraps one `sqlite3 db` handle and exposes `open()`, `close()`, version/compile-option helpers, status helpers, transaction/introspection helpers, busy/authorizer/hook setup, UDF creation, backup, blob, collation, tracing, and library configuration.
- `Stmt` wraps `sqlite3_stmt` and provides `step()`, `reset()`, SQL text inspection, explain/normalized SQL, parameter binding, column accessors, Java object binding, and finalization.
- `Status`, `TableColumnMetadata`, `Backup`, and `Blob` are typed wrappers around common SQLite output-pointer and handle APIs.
- Callback interfaces include `PrepareMulti`, `ScalarFunction`/`AggregateFunction`/`WindowFunction` registration overloads, `TraceCallback`, `AutoExtension`, `Collation`, `CollationNeeded`, `BusyHandler`, `CommitHook`, `RollbackHook`, `UpdateHook`, `ProgressHandler`, `Authorizer`, `ConfigLog`, and `ConfigSqlLog`.
- Static constants mirror `CApi` SQLite result codes, open flags, status/db-status ops, limits, prepare flags, trace flags, db/lib config options, encodings, data types, and authorizer codes.

## Control flow
`open()` calls `sqlite3_open_v2`, converts failures into `SqliteException`, registers the native handle in `nativeToWrapper`, and runs Java-level auto-extensions before returning. `thisDb()` and nested `thisStmt()`/`thisBlob()` guard against use-after-close. `checkRc()` and `checkRcStatic()` centralize result-code-to-exception mapping, with `SQLITE_NOMEM` promoted to `OutOfMemoryError`.

Statement preparation has two paths: `prepare()` returns exactly one non-null statement and treats empty SQL as an `IllegalArgumentException`; `prepareMulti()` loops through a UTF-8 buffer using the tail offset and passes each parsed statement to a visitor. `Stmt.step()` maps `SQLITE_ROW` to `true`, `SQLITE_DONE` to `false`, and optionally exposes raw busy/locked codes through `step(false)`.

Callback setup builds capi adapter objects and registers them through `sqlite3_create_function`, hook, trace, collation, busy, progress, authorizer, and config APIs. Native callback handles are mapped back to Java wrappers through synchronized maps so trace and collation-needed callbacks can receive wrapper objects rather than only raw handles.

## State and persistence behavior
The class owns native lifetime for database, statement, backup, and blob handles; `close()`/`finalizeStmt()`/`finish()`/`Blob.close()` clear Java references after closing native resources. Static mutable state includes `nativeToWrapper` for database handles, `Stmt.nativeToWrapper` for statement handles, and a `LinkedHashSet` of `AutoExtension` callbacks. Database persistence itself remains SQLite-managed; this wrapper only controls handle lifetime, runtime configuration, callbacks, and native-to-Java associations.

## Dependencies and integration points
The file depends on `org.sqlite.jni.capi` handle classes, `OutputPointer`, and numerous `CApi.sqlite3_*` JNI methods. It integrates with sibling wrapper interfaces/classes such as `ScalarFunction`, `AggregateFunction`, `WindowFunction`, `SqlFunction`, and `SqliteException`. The API is intended to be used with Java try-with-resources and SQLite JNI build options such as `ENABLE_NORMALIZE` and `ENABLE_SQLLOG`.

## Risks and edge cases
- The static wrapper maps are synchronized but not weak; leaked unclosed handles can retain wrappers.
- `Stmt.finalizeStmt()` initializes `rc` to zero and ignores the return from `sqlite3_finalize`, despite comments describing a returned result code.
- `libConfigSqlLog()` checks `hasNormalizeSql` while reporting `SQLITE_ENABLE_SQLLOG`; this appears inconsistent with the nearby `hasSqlLog` variable.
- Callback exceptions have mixed behavior: some propagate as SQLite errors, while collations/config logs suppress exceptions by SQLite API necessity.
- `prepareMulti()` uses the instance field `db` rather than `thisDb()` inside the loop, so a concurrently closed connection could produce lower-level misuse behavior.
- Auto-extension callbacks can recursively call `Sqlite.open()`, which the comments identify as a stack-overflow risk.

## Test signals
`Tester2.java` exercises this class heavily: open/close, db config, prepare/bind/column APIs, scalar/aggregate/window UDFs, keywords, explain, trace, status, auto-extensions, backup, collation-needed, busy handlers, commit/rollback/update hooks, progress, authorizer, blob I/O, prepareMulti, SQL/config logging, multithreaded execution, and thread cache cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Sqlite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqliteException.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqliteException.java

## Purpose
`SqliteException.java` is the runtime exception type for `wrapper1`. It captures SQLite primary error code, extended error code, SQL error offset, and system errno so Java callers can inspect structured SQLite failure state instead of parsing messages.

## Important APIs, types, and functions
- `SqliteException(String msg)` records a caller-supplied message and leaves both result-code fields at `SQLITE_ERROR`.
- `SqliteException(int sqlite3ResultCode)` uses `sqlite3_errstr()` and sets both primary and extended codes to the supplied result code.
- Package-private `SqliteException(sqlite3 db)` snapshots `sqlite3_errmsg`, `sqlite3_errcode`, `sqlite3_extended_errcode`, `sqlite3_error_offset`, and `sqlite3_system_errno`.
- Public constructors from `Sqlite` and `Sqlite.Stmt` bridge high-level wrappers to the native database handle.
- Accessors `errcode()`, `extendedErrcode()`, `errorOffset()`, and `systemErrno()` expose the saved state.

## Control flow
The exception is built at the point where wrapper code detects a non-OK result. Database-aware constructors read all error metadata immediately, making later connection state changes irrelevant to the exception object.

## State and persistence behavior
The object stores immutable-in-practice primitive snapshots but the fields are not declared `final`. It does not own or close database handles. It persists only the message and captured numeric state for Java error handling.

## Dependencies and integration points
It depends on `CApi`, raw `sqlite3`, `Sqlite`, and `Sqlite.Stmt`. `Sqlite.checkRc()`, `Stmt.checkRc()`, failed `open()`, backup setup, read-only checks, and wrapper argument-validation fallbacks create this exception.

## Risks and edge cases
- Constructing from a closed `Sqlite` would pass a null native handle to the package-private constructor via `nativeHandle()`.
- The statement constructor delegates to `stmt.getDb()`, so finalized statements can produce a null database path.
- The plain string constructor does not preserve a non-default code, so callers needing structured SQLite code should use the integer or handle constructor.

## Test signals
`Tester2.testOpenDb1()`, `testExplain()`, `testBusy()`, `testCommitHook()`, and negative prepare/bind paths validate nonzero codes, extended codes, offsets, and expected result-code propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqliteException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Tester2.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Tester2.java

## Purpose
`Tester2.java` is a reflection-driven sanity and regression suite for the SQLite JNI wrapper1 layer. It can run tests once, repeatedly, shuffled, quietly, with optional naps, with config/sql logging, and concurrently across multiple Java threads.

## Important APIs, types, and functions
- Annotations `@ManualTest` and `@SingleThreadOnly` control reflection-based inclusion.
- Harness state includes `mtMode`, `takeNaps`, `shuffle`, `listRunTests`, `quietMode`, `nTestRuns`, `testMethods`, shared `listErrors`, and `metrics.dbOpen`.
- `affirm()` is the assertion primitive; `out()`/`outln()` provide synchronized logging.
- `execSql()` prepares and steps all SQL statements with `Sqlite.prepareMulti()` and can either throw or return SQLite error codes.
- Test methods cover open/config, prepare/bind/columns, UDFs, window functions, keywords, explain, trace, status, auto-extension, backup, collation, busy handling, commit/rollback/update hooks, progress, authorizer, blob I/O, and multi-statement preparation.
- `main()` parses CLI flags, builds the test method list by reflection, executes serially or through `ExecutorService`, prints metrics, optionally dumps JNI internals, releases memory, shuts SQLite down, and counts `CApi.sqlite3_*` methods.

## Control flow
`main()` parses arguments, installs optional SQL/config logging callbacks, discovers `test*` methods excluding manual and thread-incompatible tests, then loops for `-repeat`. Serial mode calls `runTests(false)` directly; multithread mode submits `Tester2` runnables, collects exceptions in `listErrors`, and rethrows the first failure. Each `run()` calls `Sqlite.uncacheThread()` in `finally` to release thread-local JNI resources.

## State and persistence behavior
Most test data uses in-memory databases, but `testBusy()` creates and deletes `_busy-handler.db`. Static counters and lists accumulate across loops and threads. Each test is responsible for closing database, statement, backup, and blob handles; many use try-with-resources while older paths close explicitly.

## Dependencies and integration points
The suite depends on `Sqlite`, `ValueHolder`, `ScalarFunction`, `AggregateFunction`, `WindowFunction`, `SqlFunction.Arguments`, Java reflection/concurrency utilities, and `CApi`. It directly validates behavior promised by `Sqlite.java` and JNI support for Java object binding, Unicode round trips, and native callback adapters.

## Risks and edge cases
- `ExecutorService.awaitTermination(nThread*200ms)` may be short under slow or instrumented environments and then calls `shutdownNow()`.
- Static counters and mutable lists are shared across threads; operations that mutate test list/order are done before execution, and error list is synchronized only around insertion/reading in key places.
- Some tests are sensitive to SQLite build options, VFS behavior, filesystem permissions, and timing.
- `testBusy()` increments `metrics.dbOpen` both inside `openDb(name)` and manually, apparently double-counting for those opens.

## Test signals
This file is itself the test signal for wrapper1. Successful output reports assertions checked, databases opened, SQLite version/source id/threadsafe mode, `CApi.sqlite3_*` method counts, and elapsed time. The `-fail` flag intentionally injects a failure path into reflected test execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Tester2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ValueHolder.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ValueHolder.java

## Purpose
`ValueHolder.java` is a minimal generic mutable box used to pass values out of anonymous classes and callbacks that require captured references to be effectively final.

## Important APIs, types, and functions
- `public class ValueHolder<T>` exposes a single mutable `public T value`.
- The no-argument constructor leaves `value` null.
- The one-argument constructor initializes `value`.

## Control flow
There is no internal control flow beyond construction. Callers read and write `value` directly.

## State and persistence behavior
All state is the public field. There is no synchronization, validation, persistence, or ownership semantics.

## Dependencies and integration points
It has no non-JDK dependencies. `Tester2.java` uses it to count callback invocations, propagate result codes from `execSql()`, and hold expected hook state. Aggregate/window tests also use it as UDF state.

## Risks and edge cases
The class is intentionally mutable and unsynchronized. Sharing one holder between threads requires external synchronization or volatile/atomic alternatives if memory visibility matters.

## Test signals
Its behavior is implicitly tested wherever `Tester2` relies on callback-side mutation, especially UDF, hook, authorizer, progress, and trace tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ValueHolder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/WindowFunction.java -->
# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/WindowFunction.java

## Purpose
`WindowFunction.java` defines the Java-side abstract base for SQLite window UDFs in wrapper1. It extends aggregate UDF behavior with inverse and value callbacks needed by `sqlite3_create_window_function()` semantics.

## Important APIs, types, and functions
- `WindowFunction<T>` extends `AggregateFunction<T>`, inheriting aggregate state helpers and requiring aggregate step/final behavior.
- `xInverse(SqlFunction.Arguments args)` removes a row from the current window frame.
- `xValue(SqlFunction.Arguments args)` emits the current frame value without finalizing aggregate state.

## Control flow
The class itself has no implementation logic. `Sqlite.createFunction(..., WindowFunction f)` wraps instances in `SqlFunction.WindowAdapter`, and SQLite invokes `xStep`, `xInverse`, `xValue`, and `xFinal` through JNI callback flow.

## State and persistence behavior
Window state is managed by inherited aggregate state mechanisms in `AggregateFunction`; this file only defines the additional callback contract. Implementations decide the type and lifecycle of accumulated state.

## Dependencies and integration points
It depends on `AggregateFunction` and `SqlFunction.Arguments`. It integrates with `Sqlite.createFunction(String,int,int,WindowFunction)` and the native function adapter layer.

## Risks and edge cases
Implementations must keep `xInverse()` symmetric with `xStep()` or sliding-window results will drift. `xValue()` receives no SQL arguments but uses the context to set a result, so implementations should not assume ordinary argument data is present.

## Test signals
`Tester2.testUdfWindow()` registers a `winsumint` function and validates `xStep`, `xInverse`, `xValue`, and `xFinal` over a sliding `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` query.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/WindowFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/amatch.c -->
# sources/storage-engines/sqlite/ext/misc/amatch.c

## Purpose
`amatch.c` implements the `approximate_match` SQLite virtual table module, a demonstration approximate string matcher. It searches a configured vocabulary table for strings near an input string according to edit-cost rules stored in a separate table.

## Important APIs, types, and functions
- Virtual table structs: `amatch_vtab` stores configuration, rules, generic insertion/deletion/substitution costs, a cached vocabulary-check statement, active cursor count, and the database handle; `amatch_cursor` stores search state, cost limit, language id, input, current output, and AVL queues.
- Rule/search structs: `amatch_rule`, `amatch_word`, and `amatch_avl`.
- AVL helpers maintain priority and duplicate-detection trees: search, insert, remove, rotations, and balancing.
- Rule loading functions parse and validate the edit-distance table: `amatchLoadOneRule()`, `amatchLoadRules()`, `amatchMergeRules()`, and `amatchFreeRules()`.
- Virtual table methods: `amatchConnect()`, `amatchDisconnect()`, `amatchOpen()`, `amatchClose()`, `amatchFilter()`, `amatchNext()`, `amatchColumn()`, `amatchRowid()`, `amatchEof()`, `amatchBestIndex()`, `amatchUpdate()`.
- Entry point `sqlite3_amatch_init()` registers module name `approximate_match`.

## Control flow
Creation parses arguments such as `vocabulary_table`, `vocabulary_word`, `vocabulary_language`, and `edit_distances`, dequotes identifiers, loads edit rules, records generic rules, declares columns `word`, `distance`, `language`, `command HIDDEN`, and `nword HIDDEN`, and marks the virtual table innocuous.

Query planning recognizes `word MATCH ?`, `distance <|<= ?`, and `language = ?` constraints as a bitmask. Filtering initializes the cursor with an input string, max distance, language id, and seed empty word. `amatchNext()` repeatedly removes the lowest-cost partial word from the cost AVL tree, checks whether it is a vocabulary match, and expands candidates by direct next-codepoint match, generic insert/substitute/delete costs, and configured language-specific transformation rules. Duplicate partial states are keyed by matched input length plus output word; lower-cost duplicates update the priority queue instead of adding another node.

## State and persistence behavior
The extension does not persist its own data. It reads persistent vocabulary and rule tables from the database. Rule data is cached in memory for the lifetime of the virtual table. Cursor state is in-memory only and can grow exponentially with distance bounds. A cached `pVCheck` statement on the vtab is prepared lazily and reused across cursor advances.

## Dependencies and integration points
The file depends on SQLite virtual table APIs, extension initialization, SQL preparation/stepping, memory allocation, and host vocabulary/rule tables. Efficient operation depends on an index on the vocabulary word column. It is omitted when `SQLITE_OMIT_VIRTUALTABLE` is defined.

## Risks and edge cases
- Runtime and memory use are exponential in the distance bound; the documentation explicitly recommends tight limits.
- `amatchNext()` mutates `zNext[i-1]++` with a `FIX ME` comment, indicating rough prefix enumeration.
- Generic rule costs use `rIns`, `rDel`, and `rSub`; unset values disable those expansions.
- The cached `pVCheck` statement lives on the vtab while cursors can be active, so cursor concurrency depends on SQLite virtual table scheduling assumptions.
- The module is demonstration-quality and read-mostly; `xUpdate` rejects deletes/updates and allows only no-op command-column inserts.

## Test signals
The file comments describe SQL usage and constraints but no formal in-tree tests are referenced here. Practical test signals are creation with valid/invalid config, matching with language and distance constraints, ordering by distance, rejection of writes, and stress tests for bounded distance growth.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/amatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/anycollseq.c -->
# sources/storage-engines/sqlite/ext/misc/anycollseq.c

## Purpose
`anycollseq.c` is a small loadable extension that installs a `sqlite3_collation_needed()` callback. Whenever SQLite encounters an unknown collation sequence, the extension registers a fallback collation that compares bytes like `BINARY`.

## Important APIs, types, and functions
- `anyCollFunc()` compares two byte strings with `memcmp()` and length fallback.
- `anyCollNeeded()` registers `anyCollFunc()` for the requested collation name and text encoding.
- `sqlite3_anycollseq_init()` initializes extension API pointers and installs the collation-needed callback.

## Control flow
Loading the extension calls `sqlite3_collation_needed()`. Later, schema parsing or SQL execution that references an unknown collation triggers `anyCollNeeded()`, which calls `sqlite3_create_collation()` with the missing name and a binary-compatible comparator.

## State and persistence behavior
No persistent state is created. Registered collations live on the database connection after callback invocation. The extension uses no heap allocation.

## Dependencies and integration points
It depends on `sqlite3ext.h`, SQLite extension loading, collation-needed callbacks, and `string.h`. It is useful when loading schemas that mention collations absent from the current process.

## Risks and edge cases
The fallback collation may make schema loading possible but can change query ordering or uniqueness semantics if the original collation was not binary-equivalent. It intentionally ignores `pzErrMsg` and callback user data.

## Test signals
Load the extension, open or create a schema using an unknown collation, then query/order data under that collation. Expected behavior is no missing-collation error and bytewise ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/anycollseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/appendvfs.c -->
# sources/storage-engines/sqlite/ext/misc/appendvfs.c

## Purpose
`appendvfs.c` implements the `apndvfs` VFS shim, allowing an SQLite database to be appended to another file such as an executable. It exposes only the database segment to SQLite while the underlying VFS sees the full file.

## Important APIs, types, and functions
- `ApndFile` extends `sqlite3_file` with `iPgOne` (database start offset) and `iMark` (append-marker offset).
- `apnd_io_methods` translates file operations by adding `iPgOne` to database offsets.
- Marker helpers `apndWriteMark()`, `apndReadMark()`, `apndIsAppendvfsDatabase()`, and `apndIsOrdinaryDatabaseFile()` detect and maintain the `Start-Of-SQLite3-` trailer with an 8-byte big-endian offset.
- `apndOpen()` implements the decision rules for ordinary DBs, existing appended DBs, creating appended DBs, and rejecting unrecognized files.
- `sqlite3_appendvfs_init()` registers `apndvfs` over the current default VFS.

## Control flow
For main database files, `apndOpen()` opens the base file, measures it, and applies ordered detection rules: empty/ordinary databases pass through, existing appendvfs files are exposed from the trailer offset, and unknown files opened with `SQLITE_OPEN_CREATE` get a rounded-up future `iPgOne`. Reads add `iPgOne`; writes ensure the append marker exists or is moved before writing content; truncation writes a new marker first, then truncates the underlying full file after the marker.

## State and persistence behavior
Persistent state is the trailer marker appended to the host file and any padding between the prefix and database. In-memory state is per-open `ApndFile`. Ordinary SQLite database files are handled as pass-through by copying the base file object/method dispatch.

## Dependencies and integration points
It depends on SQLite VFS APIs, extension initialization, and the underlying default VFS. It forwards locking, shared-memory, randomness, time, dynamic-loading, access, delete, and syscall methods to the original VFS. `SQLITE_FCNTL_VFSNAME` is decorated with `apnd(offset)/...`.

## Risks and edge cases
- The combined file size is limited to less than `0x40000000` to avoid Windows pending-byte complications.
- Shared-memory and WAL operations are passed through to the underlying full file name, so operational behavior should be tested with journaling modes.
- If marker writes or truncate operations fail, the file can be left with old content/marker combinations; the code writes the marker before truncating to reduce data loss.
- Opening an unrecognized non-SQLite file without create fails with `SQLITE_CANTOPEN`.

## Test signals
Useful tests include opening ordinary databases through `apndvfs`, creating a database appended to a non-database prefix, reopening it via marker detection, verifying `xFileSize()` reports only the database segment, writing/truncating pages, and checking `SQLITE_FCNTL_VFSNAME`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/appendvfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/base64.c -->
# sources/storage-engines/sqlite/ext/misc/base64.c

## Purpose
`base64.c` implements a loadable SQLite scalar function `base64(x)` that converts BLOB input to RFC 4648-style base64 text and text input back to BLOB bytes.

## Important APIs, types, and functions
- Encoding tables/macros classify ASCII base64 digits, whitespace, padding, and invalid characters.
- `toBase64()` encodes bytes into base64 with linefeeds every 72 visible characters and after non-empty final output.
- `skipNonB64()` and `fromBase64()` decode text while tolerating whitespace and treating padding/dark non-digits as termination.
- `base64()` is the SQLite UDF dispatcher for BLOB-to-TEXT and TEXT-to-BLOB conversion.
- `sqlite3_base64_init()` registers `base64` as deterministic, innocuous, direct-only, UTF-8.

## Control flow
The SQL function checks the input SQLite type. For BLOB input, it estimates encoded size including linefeeds and terminator, enforces `SQLITE_LIMIT_LENGTH`, allocates text, encodes, and returns text with `sqlite3_free` as destructor. For TEXT input, it estimates decoded size, allocates a blob buffer, decodes, and returns a BLOB. Non-text/blob inputs produce an error.

## State and persistence behavior
The function is stateless. It allocates only per-call output buffers and stores no database state. Encoded output includes linefeeds, so serialized text is stable but not a single unbroken line.

## Dependencies and integration points
It depends on `sqlite3ext.h`, SQLite scalar function APIs, `sqlite3_limit()`, `sqlite3_malloc64()`, and `assert.h`. Macros at the end allow shell built-in integration under `SQLITE_SHELL_EXTFUNCS`.

## Risks and edge cases
- The implementation assumes ASCII-compatible UTF-8 for the first 128 codes and is not EBCDIC-safe.
- Decode accepts and skips non-base64 leading content and terminates on padding/non-digit cases, so strict validation is not the goal.
- Large inputs are constrained by SQLite length limits; allocation failures return `base64 OOM`.

## Test signals
Round-trip tests for empty blobs, one/two/three-byte tails, long line wrapping, whitespace in encoded text, invalid input termination, and length-limit failures provide coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/base64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/base85.c -->
# sources/storage-engines/sqlite/ext/misc/base85.c

## Purpose
`base85.c` implements base85 conversion as either a SQLite extension or a standalone utility. As an extension it registers `base85(x)` for BLOB/TEXT conversion and optionally `is_base85(t)` for validation.

## Important APIs, types, and functions
- Base85 classification macros map a custom 85-character ASCII alphabet excluding troublesome punctuation/control characters.
- `toBase85()` encodes 4-byte groups to 5 numerals and 1-3 byte tails to 2-4 numerals, optionally inserting separators.
- `fromBase85()` decodes delimited base85 groups back to bytes.
- `allBase85()` and `is_base85()` validate text when not compiled with `OMIT_BASE85_CHECKER`.
- `base85()` is the SQLite UDF dispatcher; `sqlite3_base85_init()` registers SQL functions.
- Under `BASE85_STANDALONE`, `main()` reads/writes binary files and base85 on standard streams.

## Control flow
As a SQLite function, BLOB input is size-checked, allocated, encoded with newline separators, and returned as text. TEXT input is size-estimated, decoded into a BLOB, and returned. `is_base85()` returns null for null, 1 for text containing only base85 numerals/whitespace, 0 otherwise. Standalone mode parses `-r` or `-w` and streams conversion.

## State and persistence behavior
The extension is stateless apart from per-call allocations. Standalone mode touches the requested file or stdin/stdout only. Encoded data can be concatenated when groups are separated by non-base85 characters.

## Dependencies and integration points
It uses SQLite extension APIs when not standalone, and C stdio/string/assert plus optional `ctype.h`. It exposes shell integration macros `BASE85_INIT` and `BASE85_EXPOSE`.

## Risks and edge cases
- The alphabet is custom and not necessarily compatible with Adobe Ascii85 or other variants.
- Non-base85 characters delimit groups during decoding; this is permissive and can hide malformed dark content unless `is_base85()` or standalone warning checks are used.
- `base85()` is registered `DIRECTONLY`, so indirect schema use is blocked.
- Size estimates must remain conservative relative to SQLite length limits.

## Test signals
Round trips for 0-4 byte boundaries, long data with 80-column separators, invalid delimiter handling, `is_base85(NULL/text/blob)`, standalone `-r`/`-w`, and omitted-checker builds are meaningful.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/base85.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/basexx.c -->
# sources/storage-engines/sqlite/ext/misc/basexx.c

## Purpose
`basexx.c` combines `base64.c` and `base85.c` into one SQLite extension or shell built-in source, exposing both conversion families from one loadable entry point.

## Important APIs, types, and functions
- `init_api_ptr()` initializes the SQLite extension API pointer once for the combined unit.
- Preprocessor rewrites `SQLITE_EXTENSION_INIT1/2` and entry point names before including `base64.c` and `base85.c`.
- `sqlite3_basexx_init()` calls `BASE64_INIT(db)` and `BASE85_INIT(db)` and returns success only if both registrations succeed.
- `BASEXX_INIT` and `BASEXX_EXPOSE` support shell integration.

## Control flow
At compile time, this file includes both implementation files into one translation unit. At load time, the combined initializer initializes API pointers, registers base64 functions, registers base85 functions, and returns `SQLITE_OK` or `SQLITE_ERROR`.

## State and persistence behavior
It has no runtime state beyond the functions registered by included source files. All per-call conversion state remains in `base64.c` and `base85.c`.

## Dependencies and integration points
It depends directly on the sibling source files `base64.c` and `base85.c`. It is designed for runtime-loadable extension builds and SQLite shell built-in builds using `SQLITE_SHELL_EXTSRC`/`SQLITE_SHELL_EXTFUNCS`.

## Risks and edge cases
- Including C files relies on macro hygiene; future changes to the included files can break combined compilation.
- The success branch calls `BASE64_EXPOSE` twice, likely intending the second call to be `BASE85_EXPOSE`; currently both macros are no-ops, so behavior is unaffected.
- A failure in either component returns generic `SQLITE_ERROR`, losing the specific failing return code.

## Test signals
Load `basexx` and verify `base64`, `base85`, and optionally `is_base85` are available and round-trip values. Build tests should cover both loadable and shell-integrated modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/basexx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/btreeinfo.c -->
# sources/storage-engines/sqlite/ext/misc/btreeinfo.c

## Purpose
`btreeinfo.c` implements the read-only eponymous-only virtual table `sqlite_btreeinfo`, which reports schema b-trees and estimated structural metrics such as entries, page count, depth, page size, and rowid presence.

## Important APIs, types, and functions
- `BinfoTable` stores the SQLite connection.
- `BinfoCursor` stores the `sqlite_schema` scan statement, selected schema, last step result, and lazily computed b-tree metrics.
- `binfoConnect()` declares columns including hidden `zSchema`.
- `binfoBestIndex()` recognizes equality constraints on hidden schema.
- `binfoFilter()` queries `sqlite_schema` plus a synthetic `sqlite_schema` root row.
- `binfoCompute()` reads pages from `sqlite_dbpage('main')` and estimates tree depth, pages, entries, page size, and rowid status.
- `sqlite3BinfoRegister()` and `sqlite3_btreeinfo_init()` register the module.

## Control flow
A scan prepares a schema query for `main` or the constrained schema. Columns copied from `sqlite_schema` are returned directly. When a metric column is requested, `binfoColumn()` lazily calls `binfoCompute()` for the row's root page. `binfoCompute()` walks from root toward a representative leaf by reading b-tree pages through `sqlite_dbpage`, multiplying observed cell fanout to estimate total entries/pages and stopping at leaf page types.

## State and persistence behavior
No data is persisted. Cursor state holds prepared statements and cached metrics for the current row. The table reads database pages and schema metadata from the active connection.

## Dependencies and integration points
It depends on SQLite virtual table APIs and the `sqlite_dbpage` virtual table being available. It uses raw SQLite database page format assumptions, including page-1 header offset and b-tree page type bytes.

## Risks and edge cases
- The header labels this extension unused, untested, unsupported, and demonstration-only.
- Metrics are estimates based on one root-to-leaf path, not full traversal.
- `binfoCompute()` hardcodes `sqlite_dbpage('main')`, while the outer scan can constrain `zSchema`; attached-schema page reads may not match the requested schema.
- Corrupt pages, excessive depth, or malformed cell pointers return errors.
- `BINFO_COLUMN_SZPAGE` is defined but not handled in `binfoColumn()`, so `szPage` is not returned despite being declared.

## Test signals
Tests should load `sqlite_dbpage`, query `sqlite_btreeinfo`, compare schema columns against `sqlite_schema`, verify hidden-schema constraint planning, exercise WITHOUT ROWID and index rows, and validate graceful errors on corrupt or missing page data.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/btreeinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/cksumvfs.c -->
# sources/storage-engines/sqlite/ext/misc/cksumvfs.c

## Purpose
`cksumvfs.c` implements the `cksmvfs` VFS shim, which stores and verifies an 8-byte checksum in each database page's reserved bytes. It also registers a SQL helper `verify_checksum(BLOB)` and a `checksum_verification` pragma handled through file-control.

## Important APIs, types, and functions
- `CksmFile` extends `sqlite3_file` with original filename, `computeCksm`, `verifyCksm`, and partner linkage fields.
- `cksmCompute()` computes the page checksum over all but the final 8 bytes using SQLite-style pairwise 32-bit accumulation with endian handling.
- `cksmVerifyFunc()` verifies a page-sized BLOB and returns 1, 0, or NULL.
- `cksmRead()` detects reserve-byte setting from page 1, updates flags, and returns `SQLITE_IOERR_DATA` on checksum mismatch when verification is enabled.
- `cksmWrite()` updates flags from page 1 and writes checksum bytes for page-sized writes when enabled.
- `cksmFileControl()` implements `PRAGMA checksum_verification` and blocks `PRAGMA page_size` changes on checksum databases.
- `cksmFetch()` disables memory-mapped fetch for checksum databases so page verification is not bypassed.
- `cksmRegisterVfs()`, static registration helpers, and `sqlite3_cksumvfs_init()` install the VFS as default and auto-register SQL functions.

## Control flow
Loading dynamically registers `verify_checksum()` on the current connection, then registers `cksmvfs` as the default VFS and arranges auto-extension registration for future connections. Main database opens are wrapped; non-main files pass through. Reads and writes of page 1 inspect byte 20 for exactly 8 reserved bytes, toggling checksum computation/verification. Page-sized reads compute and compare checksums; page-sized writes update the final 8 bytes before delegating to the underlying VFS.

## State and persistence behavior
Persistent state is the checksum stored in each page's final 8 reserved bytes and the database header reserve-byte value. Runtime state lives in each `CksmFile`. Verification can be disabled per connection/file via the pragma, but checksum writes continue when compute is enabled.

## Dependencies and integration points
It depends on SQLite 3.32+ for `sqlite3_database_file_object()` per comments, VFS APIs, auto-extension APIs, file-control pragmas, and optional static-link entry points. It forwards most VFS operations to the prior default VFS and decorates `SQLITE_FCNTL_VFSNAME` with `cksm/...`.

## Risks and edge cases
- Checksumming only works when reserved bytes equal exactly 8 and conflicts with other extensions using reserved bytes.
- The checksum write path casts away const and writes into `zBuf`; callers must provide mutable page buffers as SQLite normally does.
- Memory-mapped reads are disabled for checksum databases, which can affect performance.
- Partner fields are maintained on close and flag changes, but this file does not visibly establish partners in `cksmOpen()`; WAL/main coordination may rely on omitted or future code paths.
- Disabling verification enables forensic reads but can hide corruption from normal query paths.

## Test signals
Useful tests include enabling reserve bytes and vacuuming, verifying `verify_checksum(data)` over `sqlite_dbpage`, corrupting page bytes to trigger `SQLITE_IOERR_DATA`, toggling `PRAGMA checksum_verification`, checking that page size changes are blocked, and confirming ordinary reserve-byte-0 databases pass through.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/cksumvfs.c -->
