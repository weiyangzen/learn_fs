# sources/storage-engines/sqlite/src subset-b-008797 research

Work item `subset-b-008797` covers SQLite test-only VFS shims, virtual tables, Tcl commands, SQL functions, memory/mutex instrumentation, initialization wrappers, checksum utilities, and loadable-extension probes under `sources/storage-engines/sqlite/src`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_devsym.c -->
# sources/storage-engines/sqlite/src/test_devsym.c

## Purpose

`test_devsym.c` is a test-only VFS wrapper used to simulate device properties and abrupt process failure during writes. It registers two VFS names, `devsym` and `writecrash`, around the current default VFS. `devsym` overrides `xSectorSize` and `xDeviceCharacteristics`; `writecrash` passes through normal device information but aborts the process on a configured write count.

## Important APIs, types, and functions

The core type is `devsym_file`, a `sqlite3_file` wrapper whose real file handle is stored immediately after the wrapper in the VFS allocation. Global state in `struct DevsymGlobal g` stores the wrapped VFS, synthetic device characteristics, synthetic sector size, and pending write-crash countdown. Public entry points are `devsym_register(int iDeviceChar, int iSectorSize)`, `devsym_unregister()`, and `devsym_crash_on_write(int nWrite)`. VFS callbacks include `devsymOpen`, `devsymDelete`, `devsymAccess`, `devsymFullPathname`, dynamic-loader wrappers, randomness, sleep, and time. File callbacks are mostly pass-throughs, except `devsymSectorSize`, `devsymDeviceCharacteristics`, `writecrashWrite`, `writecrashSectorSize`, and `writecrashDeviceCharacteristics`.

## Control flow

Registration lazily captures `sqlite3_vfs_find(0)`, expands wrapper `szOsFile` by the underlying file size, and registers both wrapper VFSes. Opening a file places the underlying `sqlite3_file` after the wrapper and invokes `sqlite3OsOpen()` against `g.pVfs`. If the real file has methods, the wrapper installs either `devsym_io_methods` or `writecrash_io_methods`. Reads, writes, truncates, syncs, file-size queries, locking, file-control, shared-memory calls, deletion, access, and pathname resolution delegate to the real VFS.

## State and persistence behavior

The wrapper owns no persistent data; all durable file operations are delegated to the underlying VFS. Runtime behavior is controlled by process-global mutable state. `devsym_register()` changes the synthetic values returned by open files. `devsym_crash_on_write()` installs the VFSes if needed and sets `g.nWriteCrash`; each `writecrashWrite()` decrements it and calls `abort()` when it reaches zero before performing the real write.

## Dependencies and integration points

The file is compiled only under `SQLITE_TEST` and depends on `sqlite3.h`, `sqliteInt.h`, SQLite VFS helpers such as `sqlite3Os*`, and the default VFS. It integrates with pager tests that open databases using `vfs=devsym` or `vfs=writecrash` to exercise assumptions about sector size, atomic-write flags, safe-append/sequential properties, WAL shared memory pass-through, and crash recovery.

## Risks and edge cases

Global state is not connection-scoped, so concurrent tests can interfere. Repeated register/crash setup increments `szOsFile` only when `g.pVfs` is zero; incorrect lifecycle ordering could leave stale wrapper sizing. Shared-memory methods assume the real `pMethods` supports version-2 callbacks. `writecrash` intentionally terminates the process and is only safe in crash-test harnesses.

## Test signals

Test signals are observed through changed pager behavior under synthetic sector/device flags and through child-process termination at the configured write number. Correct behavior is that all non-overridden operations match the underlying VFS, `devsym_unregister()` removes both VFSes, and crash-recovery tests can reproduce deterministic abort points.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_devsym.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_fs.c -->
# sources/storage-engines/sqlite/src/test_fs.c

## Purpose

`test_fs.c` exposes filesystem contents to SQLite tests through three read-only virtual table modules: `fs`, `fsdir`, and `fstree`. `fs` maps rows in an index table to file contents, `fsdir` lists directory entries for a constrained directory, and `fstree` recursively walks the filesystem and exposes path, size, and data columns.

## Important APIs, types, and functions

`fs_vtab` stores the database handle and index table name; `fs_cursor` stores the active statement and reusable read buffer. `FsdirVtab`/`FsdirCsr` implement the eponymous directory lister with `DIR *`, rowid, and current `dirent`. `FstreeVtab`/`FstreeCsr` implement recursive traversal using a prepared recursive CTE over `fsdir` and an open file descriptor for the current path. Module callbacks are `fs*`, `fsdir*`, and `fstree*` families. Tcl registration is via `register_fs_module DB`, exposed by `Sqlitetestfs_Init()`.

## Control flow

`register_fs_module` resolves a Tcl database handle and registers all three modules. `fs` is created with a source table name argument; `xFilter` prepares either a full scan or rowid lookup over that table, then `xColumn` returns the mapped rowid/path or opens the named file and reads its full contents. `fsdir` requires a usable equality constraint on `dir`; `xFilter` opens the directory and `xNext` advances with `readdir()`. `fstree` accepts `path` equality, LIKE, or GLOB constraints, derives a starting directory prefix, prepares a recursive CTE over `fsdir`, and opens each yielded path for metadata/content reads.

## State and persistence behavior

The modules do not persist database state beyond virtual table declarations. Cursor state includes prepared statements, buffers, directory handles, and file descriptors, all cleaned up in close/reset paths. The filesystem is read at query time, so results reflect external filesystem changes. `fstree` deliberately hides dot-prefixed directory entries in its recursive query.

## Dependencies and integration points

The code depends on `sqliteInt.h`, `tclsqlite.h`, virtual table APIs, POSIX `stat/open/read/dirent` or the local `windirent` compatibility layer. It integrates with Tcl tests that need SQL-driven filesystem inspection, file-content fixtures, corruption setup, or recursive discovery without relying on platform-specific Tcl binary behavior.

## Risks and edge cases

The modules read arbitrary host files when tests provide paths. `fstreeColumn()` uses `sBuf.st_mode` where file size is expected when allocating and reading data, which is a notable test-code bug/risk if the data column is exercised on regular files. File-size casts and buffer growth in `fs` assume sizes fit in int-sized allocations. Recursive traversal can be expensive from `/`, and constraint extraction is a heuristic based on wildcard position and path separators.

## Test signals

Useful signals include `xBestIndex` selecting cheap plans only for supported constraints, empty results for inaccessible directories, stable rowids from index tables or directory iteration, and correct file bytes exposed through SQL. Failure modes surface as `SQLITE_IOERR`, `SQLITE_NOMEM`, or virtual table planning errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_func.c -->
# sources/storage-engines/sqlite/src/test_func.c

## Purpose

`test_func.c` registers a collection of SQLite test SQL functions and Tcl commands that probe scalar-function APIs, aggregate APIs, destructor behavior, auxdata, encodings, record decoding, subtype/from-bind metadata, recursive SQL evaluation, FTS ranking, and invalid `sqlite3_create_function()` calls.

## Important APIs, types, and functions

The `registerTestFunctions()` auto-extension installs functions including `randstr`, `test_destructor`, `test_destructor16`, `test_destructor_count`, `test_auxdata`, `test_error`, `test_eval`, `test_isolation`, `test_counter`, `hex_to_utf8`, UTF-16 hex converters, `real2hex`, `test_decode`, `test_extract`, `test_zeroblob`, `test_getsubtype`, `test_setsubtype`, `test_frombind`, and aggregate `test_agg_errmsg16`. Tcl commands are `autoinstall_test_functions`, `abuse_create_function`, and `install_fts3_rank_function`. `rankfunc()` implements an FTS3/4 matchinfo-based rank function.

## Control flow

Initialization creates Tcl commands, calls `sqlite3_initialize()`, and registers `registerTestFunctions` and `Md5_Register` as auto-extensions. Most SQL functions are direct wrappers around public or internal SQLite APIs. Record decoders use `sqlite3GetVarint()`, `sqlite3VdbeSerialGet()`, and `sqlite3VdbeSerialTypeLen()` to walk SQLite record blobs. `test_eval()` prepares and steps SQL recursively on the same database handle. `abuse_create_function()` deliberately invokes invalid combinations of scalar/aggregate callbacks and argument counts and expects `SQLITE_MISUSE`.

## State and persistence behavior

No durable database state is created except registered functions. State is mostly per-call or per-connection. `test_destructor_count_var` is global and intentionally not thread-safe. Auxdata functions store per-expression cached allocations through `sqlite3_set_auxdata()`. `test_counter` stores a mutable integer as auxdata for constant arguments. Auto-extension registration affects future connections in the process.

## Dependencies and integration points

The file depends on public SQLite APIs, `sqliteInt.h`, `vdbeInt.h`, Tcl, and `Md5_Register()` from `test_md5.c`. It is a broad integration point for the SQLite Tcl test suite, especially tests for function registration, value encoding conversion, result destructors, aggregate finalizers, recursive execution, FTS3 `matchinfo()`, subtype propagation, bind-origin tracking, and record-format internals.

## Risks and edge cases

Several functions intentionally use internal VDBE structures and malformed inputs. `test_zeroblob()` bypasses normal range checking, `test_eval()` can re-enter SQL execution, and record decoders trust blob structure enough to be useful for corruption tests. Global destructor counts are unsafe under concurrent use. Error reporting paths must preserve SQLite result codes while also setting human-readable messages.

## Test signals

Signals include destructor counts returning to zero, auxdata reuse patterns of `0` then `1`, `SQLITE_MISUSE` from invalid function registration, stable record decode/extract output, exact IEEE754 hex output, correct subtype/frombind metadata, and FTS ranking errors for malformed matchinfo blobs.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_hexio.c -->
# sources/storage-engines/sqlite/src/test_hexio.c

## Purpose

`test_hexio.c` supplies Tcl commands for byte-level database file inspection and mutation using hexadecimal text. It avoids historical Tcl binary-command portability issues and also provides helpers for UTF-8 normalization tests and FTS3 varint/record construction.

## Important APIs, types, and functions

Reusable C helpers are `sqlite3TestBinToHex()` and `sqlite3TestHexToBin()`. Tcl commands registered by `Sqlitetest_hexio_Init()` are `hexio_read`, `hexio_write`, `hexio_get_int`, `hexio_render_int16`, `hexio_render_int32`, `utf8_to_utf8`, `read_fts3varint`, and `make_fts3record`. Internal helpers `getFts3Varint()` and `putFts3Varint()` encode and decode FTS3 little-endian-style varints.

## Control flow

`hexio_read` opens a file, seeks to an offset, reads a requested byte count, converts the bytes in-place to uppercase hex, and returns the string. `hexio_write` decodes hex text while ignoring non-hex characters such as spaces, seeks to the target offset, writes the bytes, and returns the written byte count. Integer render/get commands convert between hex and big-endian or optional little-endian 16/32-bit forms. `utf8_to_utf8` is only available in debug builds and runs bytes through `sqlite3Utf8To8()`. FTS3 commands read one varint from a Tcl byte array or concatenate varints and literal bytes into a byte-array record.

## State and persistence behavior

The only persistent side effect is direct modification of files via `hexio_write`. All other state is transient heap or stack storage. The helper functions are also reused by memory tests for pointer-memory inspection and mutation.

## Dependencies and integration points

The file depends on `sqliteInt.h`, `tclsqlite.h`, C stdio, and debug-only `sqlite3Utf8To8()`. It is used by corruption, pager, btree, encoding, and FTS tests that need exact byte control over database files, journal files, and encoded records.

## Risks and edge cases

File commands operate outside SQLite locking and journaling and can corrupt files by design. Some error paths after failed `fopen()` leak the allocated buffer, acceptable for short-lived tests but still a risk. Hex decoding silently ignores characters not in the map and drops a dangling high nibble. Offset and amount are int-sized, limiting very large file manipulation.

## Test signals

Signals are exact hex strings from file reads, byte counts from writes, endian conversions, debug availability errors for `utf8_to_utf8`, varint byte-consumption counts, and generated FTS3 byte arrays matching expected fixture layouts.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_hexio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_init.c -->
# sources/storage-engines/sqlite/src/test_init.c

## Purpose

`test_init.c` tests SQLite initialization and shutdown behavior when pluggable subsystems fail during `sqlite3_initialize()`. It wraps the active memory allocator, mutex implementation, and page-cache implementation with forwarding methods that can fail initialization and report which subsystems are currently initialized.

## Important APIs, types, and functions

Global `wrapped` stores saved `sqlite3_pcache_methods2`, `sqlite3_mem_methods`, `sqlite3_mutex_methods`, initialization flags, and failure flags. Wrapper families are `wrMem*`, `wrMutex*`, and `wrPCache*`. `installInitWrappers()` shuts SQLite down, captures current subsystem methods with `SQLITE_CONFIG_GET*`, and installs wrapper methods with `SQLITE_CONFIG_*`. Tcl commands are `init_wrapper_install`, `init_wrapper_query`, `init_wrapper_uninstall`, and `init_wrapper_clear`.

## Control flow

`init_wrapper_install ?mem? ?mutex? ?pcache?` installs wrappers and marks selected subsystems to fail their initialization method. During `sqlite3_initialize()`, each wrapper either returns `SQLITE_ERROR` or delegates to the real subsystem. Successful init sets the corresponding `*_init` flag. Shutdown wrappers delegate to the real shutdown methods and clear those flags. `init_wrapper_query` returns a Tcl list of subsystems still initialized, allowing tests to verify partial cleanup after failure.

## State and persistence behavior

All state is process-global and affects SQLite configuration for the whole process until uninstalled. There is no database persistence. `init_wrapper_uninstall` performs a shutdown and restores the captured original methods, so lifecycle ordering matters.

## Dependencies and integration points

The file depends on `sqliteInt.h`, Tcl, and SQLite global configuration APIs. It integrates with initialization tests that assert failure propagation, shutdown cleanup of partially initialized components, and subsequent retry behavior after clearing failure flags.

## Risks and edge cases

Because it rewrites global SQLite configuration, it must run before normal use or after shutdown. It is not suitable for concurrent tests. If the saved subsystem methods are uninitialized or stale, uninstall can restore an invalid configuration. Failure flags are string-driven and reject unknown arguments.

## Test signals

Primary signals are the return code of `sqlite3_initialize()`, the list returned by `init_wrapper_query`, and successful restoration through `init_wrapper_uninstall`. Tests should see initialized subsystems shut down after a failed initialization and uninitialized subsystems retried on later initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_intarray.c -->
# sources/storage-engines/sqlite/src/test_intarray.c

## Purpose

`test_intarray.c` implements a test-only read-only virtual table whose rows come from a C array of `sqlite3_int64` values. It lets tests use a bound integer array as the right side of an `IN` operator without binding many individual SQL parameters.

## Important APIs, types, and functions

The opaque `sqlite3_intarray` stores element count, element pointer, and an optional array destructor. `intarray_vtab` points at that object; `intarray_cursor` stores the current index. Public APIs are `sqlite3_intarray_create(sqlite3 *db, const char *zName, sqlite3_intarray **ppReturn)` and `sqlite3_intarray_bind(sqlite3_intarray *pIntArray, int nElements, sqlite3_int64 *aElements, void (*xFree)(void*))`. Under `SQLITE_TEST`, Tcl commands `sqlite3_intarray_create` and `sqlite3_intarray_bind` expose these APIs.

## Control flow

Creating an intarray allocates the object, registers a per-object module named `zName` with `sqlite3_create_module_v2()`, then creates `temp.zName` using that module. The virtual table has schema `value INTEGER PRIMARY KEY`. Scans are simple: `xFilter` resets cursor index to zero, `xColumn` returns `pContent->a[i]`, `xRowid` returns the cursor index, `xNext` increments, and `xEof` checks `i >= n`. Binding frees the previous array through its stored destructor and installs the new array pointer/count/destructor.

## State and persistence behavior

The virtual table object lives in the TEMP schema and is destroyed on DROP or connection close. The integer array data is not copied by `sqlite3_intarray_bind()`; callers own stability until the next bind or object destruction. The bound array is freed through `xFree` when replaced or when the intarray object is freed.

## Dependencies and integration points

The file depends on `test_intarray.h`, SQLite virtual table APIs, and Tcl pointer conversion helpers in test builds. It integrates with planner and expression tests for `x IN intarray_table`, virtual table lifecycle, and C API binding semantics.

## Risks and edge cases

No constraints are advertised in `xBestIndex`, so all access is a full scan. Rebinding during an active query is documented as undefined behavior and can expose freed or mutated memory. Duplicate values are returned as duplicate rows even though the column is declared primary key, because this is a virtual table over caller memory.

## Test signals

Signals include created pointer strings, successful binding of Tcl integer lists, query results reflecting the bound array order and values, previous-array destructor execution on rebind/drop, empty initial arrays, and correct cleanup on connection close.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_intarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_intarray.h -->
# sources/storage-engines/sqlite/src/test_intarray.h

## Purpose

`test_intarray.h` is the public C header for the test-only intarray virtual table implemented in `test_intarray.c`. It documents how tests can expose a C integer array as a TEMP virtual table and use it in SQL `IN` expressions.

## Important APIs, types, and functions

The header declares opaque type `sqlite3_intarray` and two APIs: `sqlite3_intarray_create(sqlite3 *db, const char *zName, sqlite3_intarray **ppReturn)` and `sqlite3_intarray_bind(sqlite3_intarray *pIntArray, int nElements, sqlite3_int64 *aElements, void (*xFree)(void*))`. It includes `sqlite3.h`, uses `SQLITE_API`, and is guarded by `SQLITE_INTARRAY_H` with C++ `extern "C"` support.

## Control flow

The comments define the intended lifecycle: create one or more named arrays for a database connection, prepare statements that reference those names as virtual tables or `IN` right-hand sides, bind C arrays before execution, and optionally rebind between executions. Dropping the TEMP virtual table or closing the connection destroys the intarray object.

## State and persistence behavior

The API is explicitly non-persistent. Each intarray maps to a TEMP virtual table and a process-memory array. `sqlite3_intarray_bind()` does not copy elements; the caller-provided array must remain unchanged while any query is using the virtual table. The optional destructor controls when heap arrays are released.

## Dependencies and integration points

This header is included by `test_intarray.c` and by any test code that wants direct C access to the intarray API. It points users who need production behavior toward the `carray` extension instead, making the testing boundary explicit.

## Risks and edge cases

The header documents two important hazards: do not re-create an intarray with the same database/name pair, and do not mutate or free a bound array while a query is active. The type is opaque so implementation details cannot be relied upon outside the module.

## Test signals

Test signals are compile-time API availability, C++ compatibility, successful object creation/binding from callers, and runtime SQL visibility through the corresponding TEMP virtual table.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_intarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_journal.c -->
# sources/storage-engines/sqlite/src/test_journal.c

## Purpose

`test_journal.c` implements the `jt` wrapper VFS, a test-only rollback-journal verifier. It asserts that SQLite writes original database pages to the rollback journal and syncs the journal before modifying database pages that require protection.

## Important APIs, types, and functions

`jt_file` wraps a real file and stores filename, open flags, lock state, transaction page count/page size, a writable-page `Bitvec`, original page checksums, journal sync count, journal maximum offset, and a linked-list pointer. Global `g` stores the wrapped VFS and list of open files. Public APIs are `jt_register(char *zWrap, int isDefault)` and `jt_unregister()`. Key helpers are `locateDatabaseHandle()`, `decodeJournalHdr()`, `openTransaction()`, `readJournalFile()`, and `closeTransaction()`. File methods are `jtOpen`, `jtWrite`, `jtTruncate`, `jtSync`, locking methods, and pass-through VFS methods.

## Control flow

Registration clones a real VFS and overrides file/VFS methods. Open database and journal handles are tracked in `g.pList`. When a main journal receives its first valid header, `jtWrite()` locates the matching reserved-locked database handle, reads original database page checksums and freelist leaves, and starts transaction tracking. On journal sync or journal header finalization, `readJournalFile()` walks all journal records, verifies each saved page checksum against the original database page, and marks those pages writable. Writes or truncates to the main database assert that existing pages are either freelist pages or have been journaled and synced, and that growth happens only after a journal sync.

## State and persistence behavior

The wrapper does not alter persistence except by delegating real operations. It keeps transaction metadata in memory per open database handle and discards it when the journal header is zeroed, the journal is truncated to zero, the journal is deleted, or the file closes. It temporarily disables global I/O error simulation while reading pages for verification so the checker does not perturb the test being run.

## Dependencies and integration points

The file depends on SQLite VFS APIs, `sqliteInt.h`, `Bitvec`, pager journal format constants, `PENDING_BYTE`, global I/O error simulation variables, and the SQLite mutex subsystem. It integrates with rollback-journal pager tests and is documented as incompatible with `PRAGMA synchronous=off`.

## Risks and edge cases

The checker is assertion-driven, so failures abort debug/test runs rather than returning recoverable errors. It assumes rollback-journal format details and main-journal naming conventions. It tracks open files in a global list protected by a reused static mutex. WAL mode, synchronous-off behavior, and unusual VFS naming can bypass assumptions.

## Test signals

Successful tests complete without assertions. Failures indicate database-page writes before safe journaling/syncing, malformed journal headers, wrong original-page contents in the journal, unsafe truncation, or lifecycle failures when journals are zeroed, truncated, deleted, or closed.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_journal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_loadext.c -->
# sources/storage-engines/sqlite/src/test_loadext.c

## Purpose

`test_loadext.c` is a tiny loadable extension used to test `sqlite3_load_extension()` success and failure paths. It registers simple SQL functions through the extension API and provides a second entry point that always reports an error.

## Important APIs, types, and functions

The file uses `sqlite3ext.h`, `SQLITE_EXTENSION_INIT1`, and `SQLITE_EXTENSION_INIT2`. SQL functions are `halfFunc()` and `statusFunc()`. Extension entry points are exported as `testloadext_init()` and `testbrokenext_init()`. `statusFunc()` maps integer or text property names to `sqlite3_status()` opcodes including memory used, pagecache used/overflow, scratch used/overflow, and malloc size.

## Control flow

When `testloadext_init()` is invoked by SQLite's extension loader, it initializes the extension API pointer and registers `half(X)`, `sqlite3_status(X)`, and `sqlite3_status(X,RESET)` on the target database. `half()` returns `0.5 * sqlite3_value_double(argv[0])`. `sqlite3_status()` parses the requested opcode, optionally applies the reset flag, calls `sqlite3_status()`, and returns either the current value or the high-water value depending on arity. `testbrokenext_init()` allocates error text `broken!`, stores it in `*pzErrMsg`, and returns failure.

## State and persistence behavior

The successful extension only adds functions to the connection. It does not create schema objects or persistent state. `sqlite3_status()` may reset high-water counters when called with a reset flag, affecting process-global SQLite status state.

## Dependencies and integration points

The file is built as a loadable extension and integrates with tests for dynamic loading, extension entry point lookup, exported symbols on Windows, error-message ownership, SQL function creation from extension code, and status APIs callable through an extension boundary.

## Risks and edge cases

The status-name table reflects the opcodes available when this test code was written; removed or disabled status classes can return errors. The function reports unknown status names as SQL errors. The broken extension deliberately returns a non-`SQLITE_OK` integer rather than `SQLITE_ERROR`, testing loader normalization and message propagation.

## Test signals

Signals include successful load exposing `half()` and `sqlite3_status()`, expected numeric status outputs, high-water reset behavior, and failed load returning the `broken!` message from `testbrokenext_init()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_loadext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_malloc.c -->
# sources/storage-engines/sqlite/src/test_malloc.c

## Purpose

`test_malloc.c` exposes SQLite memory allocation, fault injection, memory-status, page-cache, lookaside, heap, and memdebug facilities to Tcl tests. It is the main Tcl-side control surface for out-of-memory testing and allocator configuration.

## Important APIs, types, and functions

`struct MemFault memfault` stores simulated allocation failure state, benign-failure counts, success counters, install state, and saved real `sqlite3_mem_methods`. Fault helpers include `faultsimStep()`, `faultsimMalloc()`, `faultsimRealloc()`, `faultsimConfig()`, and `faultsimInstall()`. Pointer utilities are `pointerToText()` and `textToPointer()`. Tcl commands include raw `sqlite3_malloc/realloc/free`, `memset`, `memget`, memory high-water commands, memdebug backtrace/dump/fail/pending/settitle/log, pagecache and alternate-pcache config, status/db_status, malloc faultsim install, heap/lookaside/memstatus/URI/CIS/PMASZ config, memsys dumps, memsys3 install, and VFS OOM toggling.

## Control flow

Installing fault simulation captures the active allocator, replaces `xMalloc` and `xRealloc`, and installs benign-malloc hooks with `sqlite3_test_control()`. Each allocation calls `faultsimStep()`, which counts down successes, records first/all faults, increments benign counters when in benign mode, repeats failures as configured, then disables itself. Tcl commands configure failure countdowns, query pending failures, and read/reset status. Configuration commands call `sqlite3_config()` or `sqlite3_db_config()` with buffers or options supplied from Tcl.

## State and persistence behavior

Most state is process-global SQLite configuration or global test state. Fault injection affects all SQLite allocations after installation. Static buffers are used for pagecache, heap, and db lookaside tests. `test_memdebug_log` stores a Tcl hash of allocation backtrace keys and counts until cleared. No database schema is persisted, but configuration changes can affect later connections and tests.

## Dependencies and integration points

The file depends on `sqliteInt.h`, Tcl, `test_hexio.c` hex helpers, optional `SQLITE_MEMDEBUG`, `SQLITE_ENABLE_MEMSYS3`, `SQLITE_ENABLE_MEMSYS5`, and external test page-cache hooks. It integrates with SQLite OOM test loops, memory leak diagnostics, status accounting tests, lookaside/pagecache configuration tests, and invalid config opcode tests.

## Risks and edge cases

It rewires global allocators and must be used with careful shutdown/configuration ordering. `faultsimInstall()` sets `memfault.isInstalled = 1` after both install and uninstall success, which is suspicious and can affect repeated toggles. Raw pointer Tcl commands can corrupt process memory. Static buffers have fixed sizes and require argument validation. Some features are no-ops unless optional debug/memory systems are compiled in.

## Test signals

Signals include deterministic OOM at a configured allocation count, benign-failure counts, pending-failure counters, memory used/highwater values, allocator backtrace logs, status/db_status triples, expected config return codes, and successful restoration of the allocator after fault tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_md5.c -->
# sources/storage-engines/sqlite/src/test_md5.c

## Purpose

`test_md5.c` provides an MD5 implementation for SQLite tests. It registers Tcl commands for hashing strings/files and a SQL aggregate `md5sum()` used by test scripts to compare result sets or file contents compactly.

## Important APIs, types, and functions

`MD5Context` stores initialization state, four hash words, bit counters, and a 64-byte input block. Core algorithm functions are `MD5Init()`, `MD5Update()`, `MD5Transform()`, `MD5Final()`, and `byteReverse()`. Output converters are `MD5DigestToBase16()` and `MD5DigestToBase10x8()`. Tcl command callbacks are `md5_cmd()` and `md5file_cmd()`, registered by `Md5_Init()`. SQL aggregate callbacks are `md5step()` and `md5finalize()`, registered by `Md5_Register()`.

## Control flow

Tcl string hashing initializes a context, updates it with the input string, finalizes the digest, and formats either 32 hex digits or eight five-digit decimal groups. File hashing optionally seeks to an offset and reads up to a specified amount in 10 KiB chunks. The SQL aggregate initializes context in aggregate memory on first step, appends each non-NULL argument's text bytes for every row, and finalizes to a base-16 digest. `Md5_Register()` also calls `sqlite3_overload_function()` for `md5sum` to exercise that API.

## State and persistence behavior

There is no durable state. MD5 state is per Tcl command invocation or per aggregate context. `MD5Context.isInit` guards aggregate lazy initialization. File commands read from disk but do not write.

## Dependencies and integration points

The file depends on Tcl, stdio, string functions, and SQLite function-registration APIs. It is auto-registered from `test_func.c`, making `md5sum()` broadly available in SQLite Tcl tests. Tcl commands support test scripts that verify database-file bytes, query output, or fixture stability.

## Risks and edge cases

The code is a public-domain MD5 implementation intended for tests, not security-sensitive hashing. `md5finalize()` assumes aggregate context exists; calling finalization on an empty group relies on SQLite aggregate behavior and can be a null-context risk if changed. Text inputs use `strlen()` on `sqlite3_value_text()`, so embedded NULs are not fully included in SQL aggregate hashing.

## Test signals

Signals include known MD5 digests for strings/files, consistent `md5file` slicing with offset/amount, `md5sum()` aggregate output stability across query plans, and successful function overloading registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_multiplex.c -->
# sources/storage-engines/sqlite/src/test_multiplex.c

## Purpose

`test_multiplex.c` implements the `multiplex` VFS shim, which splits a logical SQLite database, journal, or WAL file into numbered chunk files. It is used to test large-file behavior and filesystems with size limits, and it exposes file-control and pragma surfaces for runtime control.

## Important APIs, types, and functions

`multiplexGroup` represents one logical file and stores chunk handles/names, base filename, original open flags, chunk size, enabled flag, and truncation mode. `multiplexConn` is the `sqlite3_file` wrapper. Global `gMultiplex` stores the original VFS, wrapper VFS, I/O method tables, and initialization flag. Public APIs are `sqlite3_multiplex_initialize()` and `sqlite3_multiplex_shutdown()`. Key helpers include `multiplexFilename()`, `multiplexSubFilename()`, `multiplexSubOpen()`, `multiplexSubSize()`, `multiplexControlFunc()`, `multiplexOpen()`, `multiplexDelete()`, `multiplexRead()`, `multiplexWrite()`, `multiplexTruncate()`, `multiplexFileSize()`, and `multiplexFileControl()`.

## Control flow

Initialization clones the selected real VFS, increases `szOsFile`, overrides VFS callbacks, initializes version-1/version-2 I/O method tables, registers the VFS, and auto-registers SQL function `multiplex_control(op,val)`. Open allocates a group, parses URI options `chunksize` and `truncate`, rounds chunk size, adjusts it around the pending-byte region, opens chunk 0, detects existing overflow chunks, and chooses wrapper method version. Reads and writes compute chunk number and offset, opening or creating chunks as needed and splitting operations across chunk boundaries. Truncate either deletes higher chunks or truncates them to zero, then truncates the boundary chunk. File-control handles enable/chunk-size/max-chunks controls and `multiplex_*` pragmas before passing other controls through.

## State and persistence behavior

Persistent state is the set of chunk files on disk. Chunk 0 uses the base filename; later chunks append or replace extensions with three-digit numbers, with special offsets for rollback journals and WAL files under 8.3 naming. Runtime group state is per open file and freed on close. Shutdown unregisters the VFS and clears global state but does not delete user database chunks.

## Dependencies and integration points

The file depends on public SQLite VFS APIs, `sqlite3ext.h`, URI filename helpers, `test_multiplex.h`, and optionally `sqlite3PendingByte`. Test-only Tcl commands expose initialize, shutdown, and file-control operations. It integrates with pager, WAL, journal, VFS-name, URI, pragma, and large-database tests.

## Risks and edge cases

The public initialize/shutdown routines are documented as not thread-safe. Existing chunk detection and chunk-size inference must be consistent or the shim disables multiplexing for suspicious files. Reads open missing chunks with create enabled, which may create zero-length chunks during reads. `MULTIPLEX_CTRL_SET_MAX_CHUNKS` is accepted but no longer enforced. Filename generation has 8.3 collision constraints and an overflow limit near journal offsets.

## Test signals

Signals include creation/deletion of numbered chunk files, correct logical file size across chunks, split reads/writes spanning boundaries, truncation mode behavior, `multiplex_control()` return codes, `PRAGMA multiplex_enabled/chunksize/filecount/truncate` results, and VFS name strings prefixed with `multiplex/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_multiplex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_multiplex.h -->
# sources/storage-engines/sqlite/src/test_multiplex.h

## Purpose

`test_multiplex.h` declares the public interface and file-control opcodes for the multiplex VFS shim implemented in `test_multiplex.c`.

## Important APIs, types, and functions

The header defines `MULTIPLEX_CTRL_ENABLE`, `MULTIPLEX_CTRL_SET_CHUNK_SIZE`, and `MULTIPLEX_CTRL_SET_MAX_CHUNKS` with private integer opcode values interpreted by the VFS `xFileControl` method. It declares `sqlite3_multiplex_initialize(const char *zOrigVfsName, int makeDefault)` and `sqlite3_multiplex_shutdown(int eForce)`, wrapped in C++ `extern "C"`.

## Control flow

The comments describe startup and shutdown flow: initialize once with an optional underlying VFS name and default-VFS flag; use the registered `multiplex` VFS directly or as default; control live database files through `SELECT multiplex_control(<op>, <val>)`; then shut down after all database connections are closed.

## State and persistence behavior

The header does not own state, but it documents that initialization registers an auto-extension for `multiplex_control()` and that shutdown expects no open SQLite connections. File-control opcodes mutate per-file multiplex state such as enabled flag and chunk size.

## Dependencies and integration points

It includes `sqlite3.h` indirectly through consumers and is included by `test_multiplex.c` and tests embedding the multiplex shim. The API is suitable for static or loadable builds of the test VFS.

## Risks and edge cases

The documented routines are not thread-safe and should be called exactly once at startup/shutdown. `MULTIPLEX_CTRL_SET_MAX_CHUNKS` remains part of the interface even though the implementation no longer enforces a maximum chunk count.

## Test signals

Compile-time signals are successful inclusion from C and C++ and availability of control constants. Runtime signals come from the paired `.c` implementation honoring the declared initialize, shutdown, and file-control contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_multiplex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_mutex.c -->
# sources/storage-engines/sqlite/src/test_mutex.c

## Purpose

`test_mutex.c` exposes SQLite mutex initialization, configuration, locking, and usage counters to Tcl tests. It can install a wrapper mutex subsystem that counts lock attempts and simulates initialization or try-lock failures.

## Important APIs, types, and functions

The test redefines `struct sqlite3_mutex` as a wrapper around a real mutex pointer and mutex type. Global `g` stores install/init flags, failure toggles, saved real `sqlite3_mutex_methods`, counters by mutex type, and wrapper static mutex objects. Wrapper methods are `counterMutexInit`, `counterMutexEnd`, `counterMutexAlloc`, `counterMutexFree`, `counterMutexEnter`, `counterMutexTry`, `counterMutexLeave`, `counterMutexHeld`, and `counterMutexNotheld`. Tcl commands include `sqlite3_shutdown`, `sqlite3_initialize`, `sqlite3_config`, `install_mutex_counters`, `read_mutex_counters`, `clear_mutex_counters`, `alloc_dealloc_mutex`, static mutex enter/leave, and db mutex enter/leave.

## Control flow

`install_mutex_counters true` captures the active mutex methods with `SQLITE_CONFIG_GETMUTEX` and installs counter methods using `SQLITE_CONFIG_MUTEX`. Allocation wraps dynamic mutexes with heap objects and static mutexes with entries in `g.aStatic`. Enter and try increment the counter for the mutex type before delegating, unless `disable_mutex_try` forces `SQLITE_BUSY`. Uninstall restores saved methods. Tcl linked variables `disable_mutex_init` and `disable_mutex_try` control failure simulation.

## State and persistence behavior

All state is process-global and affects SQLite's mutex subsystem while installed. Counters persist until explicitly cleared. The file creates no database state, but db-mutex commands directly enter and leave a connection's mutex and must be balanced by tests.

## Dependencies and integration points

The file depends on Tcl, `sqlite3.h`, `sqliteInt.h`, thread-safe SQLite mutex APIs, `sqlite3ErrName()`, and test pointer conversion helpers. It integrates with threading-mode tests, initialization failure tests, static mutex coverage, db mutex tests, and `sqlite3_config()` mode changes for singlethread/multithread/serialized.

## Risks and edge cases

The wrapper relies on configuring SQLite before initialization or after shutdown. Incorrectly balanced enter/leave Tcl calls can deadlock later tests. The local `getDbPointer()` assumes Tcl command client data layout or test pointer strings. Counter increments count attempts, not only successful acquisitions, especially for forced try failures.

## Test signals

Signals include named counter lists for fast/recursive/static mutex classes, expected `SQLITE_BUSY` from forced try-locks, expected `SQLITE_ERROR` or configured code from disabled initialization, successful allocation/deallocation pointer output, and correct `sqlite3_config()` return names.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_mutex.c -->
