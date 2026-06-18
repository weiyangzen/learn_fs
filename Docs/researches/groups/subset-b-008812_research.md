# Research Group subset-b-008812

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/speedtest1.c -->
## sources/storage-engines/sqlite/test/speedtest1.c

### Purpose
`speedtest1.c` is SQLite's standalone performance benchmark driver. It creates deterministic data sets, runs named SQL workload suites, times each test case, optionally emits the SQL instead of executing it, and can produce verification hashes and memory/page-cache statistics for comparison across SQLite builds and compile options.

### Important APIs, types, and functions
The central state is the global `g` structure, holding the SQLite handle, current prepared statement, timing totals, option flags, result hash state, pseudo-random generator state, SQL script output, and configurable schema fragments such as `WITHOUT ROWID`, `STRICT`, `NOT NULL`, and `PRIMARY KEY`. Utility APIs include `integerValue()`, `speedtest1_timestamp()`, deterministic `speedtest1_random()`, `swizzle()`, `speedtest1_numbername()`, and the SQL wrappers `speedtest1_exec()`, `speedtest1_once()`, `speedtest1_prepare()`, and `speedtest1_run()`. Benchmark suites are implemented by `testset_main()`, `testset_cte()`, `testset_fp()`, `testset_star()`, `testset_app()`, `testset_rtree()`, `testset_orm()`, `testset_trigger()`, `testset_json()`, `testset_parsenumber()`, and `testset_debug1()`.

### Control flow
`main()` parses options, configures SQLite before initialization where required, deletes and opens the target database or memory database, applies PRAGMAs and custom functions, expands the `mix1` macro testset, and runs each selected testset. Between multiple testsets it drops all main and temp tables. Each individual benchmark calls `speedtest1_begin_test()`, performs SQL work through shared wrappers, and finishes with `speedtest1_end_test()`. `speedtest1_final()` prints aggregate timing and verification data.

### State and persistence behavior
The program mutates a target database file unless `--memdb` is used. It explicitly removes existing database files through the selected VFS and `unlink()`, changes pager and schema behavior with PRAGMAs, and can write SQL scripts and verification output files. `--verify` hashes result streams, omitting exact floating-point values to reduce platform variance. The pseudo-random sequence is reset per test, making workloads reproducible.

### Dependencies and integration points
This file integrates directly with the public SQLite C API, optional R-Tree APIs, VFS time and delete methods, Linux `/proc/PID/io` for stats, optional checksum VFS registration, deprecated trace hooks, and build-time feature macros. It is wired into SQLite build targets for comparing current and historical amalgamations.

### Risks and test signals
Risks include option-order sensitivity for `sqlite3_config()`, benchmark results changing with compile-time features, SQL-only paths masking execution errors, intentionally relaxed settings such as `synchronous=OFF`, and very large generated databases at high `--size`. Strong signals are nonzero exit on SQLite errors, stable verification hash output, `PRAGMA integrity_check`, optional statement scan status and memory statistics, and deterministic test numbering/timing output.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/speedtest1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/startup.c -->
## sources/storage-engines/sqlite/test/startup.c

### Purpose
`startup.c` benchmarks SQLite startup costs, especially opening a database and parsing a large schema. The schema is modeled on Fossil repository, checkout, and global configuration databases, so it stresses schema loading, indexes, views, triggers, `WITHOUT ROWID` tables, and statistics tables without depending on row-level workload costs.

### Important APIs, types, and functions
The large `zTestSchema` string is the primary fixture. `usage()`, `hexDigitValue()`, and `integerValue()` support command-line processing. `displayLinuxIoStats()` reports `/proc/PID/io` counters on Linux. `main()` implements the `init` and `run` commands, optional `--dbname`, `--heap`, `--stats`, and `--autovacuum` parsing, though `bAutovac` is parsed but not used in the current logic.

### Control flow
`startup init` removes the database, journal, and WAL files, opens the database, runs `BEGIN`, executes `zTestSchema`, commits, and closes. `startup run` optionally configures a static heap before opening, opens the existing database, executes `PRAGMA synchronous` to force schema access, optionally prints database and global memory statistics, closes, and frees heap storage.

### State and persistence behavior
The persistent artifact is `startup.db` or the `--dbname` target. Initialization creates only schema objects, with no bulk data population. Run mode should be read-mostly, but opening the database may create transient journal/WAL artifacts depending on environment. Heap and memory statistics are process-local and printed after connection close.

### Dependencies and integration points
The file depends on `sqlite3.h`, POSIX `unlink()`, libc parsing and I/O, optional Linux `/proc`, and SQLite status APIs. It is intended for external profilers such as cachegrind, not for the Tcl test runner.

### Risks and test signals
The embedded schema contains compatibility-sensitive SQL and object names; changes to schema parsing or SQLite DDL behavior affect the benchmark. `run` prints SQLite errors but may continue to stats reporting, so exit status alone is a weak signal. Useful signals are absence of open/exec errors, stable schema heap and statement heap metrics, and Linux I/O counter deltas under profiling.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/startup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/testloadext.c -->
## sources/storage-engines/sqlite/test/testloadext.c

### Purpose
`testloadext.c` is a loadable extension used to verify that runtime extension loading can call newer SQLite extension APIs. It exposes SQL functions that exercise `sqlite3_set_errmsg()` and 64-bit database status reporting.

### Important APIs, types, and functions
The file uses `sqlite3ext.h`, `SQLITE_EXTENSION_INIT1`, and `SQLITE_EXTENSION_INIT2`. `seterrmsgfunc()` implements `set_errmsg(CODE, MSG)` by calling `sqlite3_context_db_handle()`, `sqlite3_set_errmsg()`, and then returning a formatted tuple of the API return code, current `sqlite3_errcode()`, and current `sqlite3_errmsg()`. `tempbuf_spill_func()` implements `tempbuf_spill(RESET)` using `sqlite3_db_status64()` with `SQLITE_DBSTATUS_TEMPBUF_SPILL`. `sqlite3_testloadext_init()` registers both SQL functions.

### Control flow
SQLite loads the shared object and calls `sqlite3_testloadext_init()`. The initializer stores the extension API table, ignores the extension error-message pointer, registers `set_errmsg`, then registers `tempbuf_spill`, returning the first non-OK registration result.

### State and persistence behavior
The extension does not create persistent schema or files. It mutates only the connection error state through `sqlite3_set_errmsg()` and optionally resets an in-memory DB status counter when `tempbuf_spill(1)` is called.

### Dependencies and integration points
The file is built as a platform-specific shared library and loaded by SQLite extension-loading tests. It depends on the extension API surface rather than direct core symbols, making it a compatibility test for exported API slots.

### Risks and test signals
Risks are API availability mismatches with older SQLite builds, incorrect entry-point naming, and platform-specific symbol export issues. Test signals are successful load, successful function registration, expected `set_errmsg()` return text, and changing `tempbuf_spill()` values when temp-buffer spill behavior is exercised.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/testloadext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest1.c -->
## sources/storage-engines/sqlite/test/threadtest1.c

### Purpose
`threadtest1.c` is an older standalone pthread program that probes SQLite thread safety by running pairs of threads against shared database files. Each thread repeatedly creates, populates, queries, validates, and drops its own table in a shared database.

### Important APIs, types, and functions
The program uses the legacy `sqlite.h` interface with `sqlite *`, `sqlite3_open()`, `sqlite3_exec()`, and `sqlite3_close()`. `db_is_locked()` is a busy handler with short sleeps. `QueryResult`, `db_query_callback()`, `db_query()`, `db_execute()`, `db_query_free()`, and `db_check()` form a small SQL execution and validation layer. `worker_bee()` is the thread body, and `main()` creates detached pthreads and waits on a condition variable.

### Control flow
`main()` accepts an optional thread count, deletes stale database files, creates thread arguments such as `1.testdb-1` and `2.testdb-1`, launches detached workers, and waits for `thread_cnt` to reach zero. Each worker opens the file named after the prefix, installs the busy handler, creates table `tN`, inserts 100 rows, checks count and average values, deletes half the rows, reads back each remaining row, drops the table, closes, and repeats ten times.

### State and persistence behavior
The test uses temporary database files named `testdb-N` and old rollback journals. It deletes files at start and end but leaves thread argument allocations unfreed. Per-thread SQL tables are transient. Validation state is held in heap-allocated query result arrays.

### Dependencies and integration points
It depends on pthreads, POSIX `unlink()` and `usleep()`, legacy SQLite headers, and SQLite formatting helpers. It sits outside the normal library and is useful for historical thread-safety regression testing.

### Risks and test signals
Because detached workers increment `thread_cnt` inside the thread, a very fast main thread can reach the wait before workers increment the count; in practice startup prints and scheduling usually hide this race. Busy handling is bounded, so lock pressure can become test failure. Signals are `START`/`END` messages, exact aggregate checks, readback checks, and process exit through `Exit(1)` on any SQL or validation error.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest2.c -->
## sources/storage-engines/sqlite/test/threadtest2.c

### Purpose
`threadtest2.c` is a compact legacy pthread stress test where five workers repeatedly open the same database, disable synchronous writes, insert a row, and close. It is designed to expose corruption or locking bugs under concurrent connection churn.

### Important APIs, types, and functions
The code uses legacy `sqlite.h` APIs, pthreads, and a global volatile `all_stop`. `check_callback()` inspects `PRAGMA integrity_check` results, `integrity_check()` can run one or two checks, `worker()` performs repeated open/insert/close cycles, and `main()` initializes the database and joins the workers.

### Control flow
`main()` removes `test.db` and its rollback journal, creates table `t1`, launches five worker threads, joins them, and prints success or failure. Each worker loops up to 10000 iterations or until `all_stop`, repeatedly opens `test.db`, sets `PRAGMA synchronous=OFF`, inserts a row, and closes. The integrity-check call is present but commented out in the worker loop.

### State and persistence behavior
All threads share the persistent `test.db` file. The workload is append-only after initialization and intentionally weakens durability with `synchronous=OFF`. `all_stop` is the cross-thread stop flag but is not protected by a mutex.

### Dependencies and integration points
The file depends on pthreads, POSIX `unlink()`, scheduler yielding, and the legacy SQLite API. It is a standalone executable test, not a reusable module.

### Risks and test signals
The test casts pointers to `int` for worker ids, which is non-portable on some architectures. The disabled integrity check means the default success signal mainly checks for crashes and API errors, not final logical row counts. Useful signals are worker progress messages, no unexpected SQLite return codes, final `Everything seems ok.`, and optional re-enabling of integrity checks for stronger corruption detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest3.c -->
## sources/storage-engines/sqlite/test/threadtest3.c

### Purpose
`threadtest3.c` is the main modern multithreaded SQLite stress-test harness. It contains common infrastructure and several built-in tests, then includes scenario files `tt3_*.c` to form one executable with glob-selectable tests for WAL, shared-cache, schema churn, checkpointing, vacuum, lookaside, and stress workloads.

### Important APIs, types, and functions
The harness defines `Error`, `Sqlite`, `Statement`, `Thread`, and `Threadset`. Macros such as `opendb`, `sql_script`, `execsql_i64`, `launch_thread`, and `setstoptime` record source lines before delegating to `_x` implementations. It embeds an MD5 aggregate (`md5step()`, `md5finalize()`), statement caching (`getSqlStatement()`), SQL execution helpers, cross-platform thread launch/join, file-size/copy helpers, and a VFS-backed timer. Built-in tests include `walthread1` through `walthread5`, `cgt_pager_1`, and `dynamic_triggers`.

### Control flow
`main()` configures SQLite multithread mode, parses `-multiplexor` and test glob arguments, validates that each argument matches at least one test, then runs matching entries from `aTest`. Each test initializes `test.db`, sets a stop time, launches workers, joins them, prints thread results, and increments the global error count through `print_err()`.

### State and persistence behavior
Most tests use `test.db` plus WAL, journal, or saved copies. Connections cache prepared statements and stored text results until `closedb_x()`. WAL tests intentionally exercise checkpoint behavior, journal-mode transitions, snapshot isolation, and file replacement. The harness treats some transient `SQLITE_SCHEMA`, `SQLITE_LOCKED`, and missing-table errors as warnings or clearable expected concurrency effects.

### Dependencies and integration points
It depends on SQLite public APIs, pthreads or Windows threads, `test_multiplex.h`, optional multiplex VFS initialization, and included `tt3_*.c` files. The include pattern means the scenario files rely on symbols from this harness rather than compiling independently.

### Risks and test signals
Risks include global `timelimit` shared by all threads, expected lock/schema errors hiding unexpected failures if clear rules are too broad, and workload sensitivity to filesystem timing. Strong signals are the final `N errors out of M tests`, per-thread summaries, integrity checks, MD5 consistency checks, WAL size assertions, and nonzero exit status on global errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest4.c -->
## sources/storage-engines/sqlite/test/threadtest4.c

### Purpose
`threadtest4.c` stresses multiple threads accessing the same group of attached databases in shared-cache mode. It varies attach order per worker to expose lock-ordering, shared-cache, VACUUM, and cross-database transaction issues.

### Important APIs, types, and functions
`WorkerInfo` tracks thread identity, flags, main and worker connections, error counters, messages, pthread id, and a write mutex. Flags are `TT4_SERIALIZED`, `TT4_WAL`, and `TT4_TRACE`. Helpers include `safe_malloc()`, `worker_trace()`, `prep_sql()`, `run_sql()`, `worker_open_connection()`, `worker_close_connection()`, `worker_delete_all_content()`, `worker_add_content()`, `worker_error()`, and `worker_thread()`.

### Control flow
`main()` parses options and thread count, requires a threadsafe SQLite build, enables shared cache, initializes three database files with tables and indexes, then starts `N` workers. Each worker repeatedly opens the three files in a rotating order, attaches the other two databases, inserts rows into all three tables under a write mutex, validates counts, sometimes releases memory, performs rollback updates, may run `VACUUM`, executes a join query while yielding, deletes its rows, and closes.

### State and persistence behavior
The test creates `tt4-test1.db`, `tt4-test2.db`, and `tt4-test3.db`, with optional WAL mode on the first connection. Worker data is partitioned by `tid`, then deleted before the next outer iteration. Writes are serialized by `wrMutex`, while reads and connection/attach sequencing remain concurrent.

### Dependencies and integration points
The file depends on SQLite shared-cache support, pthreads, POSIX scheduling and unlink, and SQLite memory allocation. It can be built with thread sanitizers and run in `--multithread` or `--serialized` modes.

### Risks and test signals
Because many write operations are mutex-serialized, the test is targeted at shared-cache and attach interactions rather than unrestricted write races. `run_sql()` treats ten repeated busy/locked retries as deadlock and exits immediately. Signals are per-worker startup/finish lines, joined error/test counts, optional trace output, and final total errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest5.c -->
## sources/storage-engines/sqlite/test/threadtest5.c

### Purpose
`threadtest5.c` tests many connections in separate pthreads working against the same database file or URI database. It implements a simple task queue where workers claim tasks atomically, build two prime-number tables by different methods, and verify that the final sets match.

### Important APIs, types, and functions
Global state includes `zDbName` and `eVerbose`. `error_out()` aborts on non-OK setup errors, `exec()` and `prepare()` wrap formatted SQL execution and preparation, `waitOnTable()` polls `sqlite_schema`, `isPrime()` filters prime candidates, `worker()` claims and runs tasks, and `usage()` documents options.

### Control flow
`main()` parses a database name, `-num-workers`, and `-v`, defaults to `file:/mem?vfs=memdb`, enables URI handling, creates a `task` table with 100 tasks, launches workers, and joins them. Workers use `UPDATE ... RETURNING` to claim one unassigned task. Task 1 creates `p1`; tasks 2-51 insert prime numbers into `p1`; task 52 creates `p2` containing 1..10000; tasks 53-62 delete composites from `p2`. The main thread prints task ownership and verifies `p1` and `p2` are equal with `EXCEPT` queries.

### State and persistence behavior
The default database is an in-memory memdb URI shared by connections. A supplied database path persists until overwritten by setup drops. Task claims are stored in `task.doneby`, and final computed state lives in `p1` and `p2`.

### Dependencies and integration points
The program depends on SQLite URI support, pthreads, `sqlite3_sleep()`, `UPDATE RETURNING`, and the memdb VFS for the default mode. It is Unix-oriented and standalone.

### Risks and test signals
`isPrime()` returns true for values below 2, so `p2` intentionally retains `1` to match `p1` semantics if generated; this is a test convention, not mathematical primality. Busy handling is a fixed 2 second timeout. Signals are successful task ownership output, `OK`, no incorrect-result messages, and no abort from prepare/open/exec wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/threadtest5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/time-wordcount.sh -->
## sources/storage-engines/sqlite/test/time-wordcount.sh

### Purpose
`time-wordcount.sh` is a small shell benchmark driver for the `wordcount` test program. It runs the same input through multiple wordcount operation modes and table layouts to produce comparable timing summaries.

### Important APIs, types, and functions
The script uses POSIX shell, `rm -f`, and the local `./wordcount` executable. It forwards all user arguments after the required filename to `wordcount`, adding tags `A:` through `J:`, `--timer`, `--summary`, database names, operation flags, and optional `--without-rowid`.

### Control flow
The script requires at least one argument. It deletes `wcdb1.db` or `wcdb2.db` before insert/replace/select phases, runs rowid and `WITHOUT ROWID` variants for `--insert`, `--replace`, and `--select`, then runs query and delete phases against the generated databases. It removes both temporary databases at the end.

### State and persistence behavior
Only `wcdb1.db` and `wcdb2.db` are created, reused, and deleted. The source text is read by `wordcount`; this script does not inspect it directly. Timing and summaries are printed by child processes.

### Dependencies and integration points
It depends on a built `wordcount` executable in the current directory and standard shell utilities. It is intended as a manual performance comparison helper.

### Risks and test signals
The script does not use `set -e`, so a failed `wordcount` command does not automatically stop later phases. Filenames are passed through `$*`, so arguments with spaces are not preserved robustly. Signals are tagged timing lines from each phase and absence of leftover temporary database files after cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/time-wordcount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_checkpoint.c -->
## sources/storage-engines/sqlite/test/tt3_checkpoint.c

### Purpose
`tt3_checkpoint.c` adds checkpoint starvation scenarios to `threadtest3`. It compares passive and restart WAL checkpoints while long-lived readers repeatedly hold snapshots.

### Important APIs, types, and functions
`CheckpointStarvationCtx` stores checkpoint mode and peak frame count. `checkpoint_starvation_walhook()` is registered with `sqlite3_wal_hook()` and invokes `sqlite3_wal_checkpoint_v2()` when the WAL reaches `CHECKPOINT_STARVATION_FRAMELIMIT`. `checkpoint_starvation_reader()` checks snapshot isolation during 100 ms read transactions. `checkpoint_starvation_main()` runs the shared setup. `checkpoint_starvation_1()` and `_2()` assert expected WAL growth behavior.

### Control flow
The main helper creates `test.db` in WAL mode, launches four staggered readers, installs the WAL hook on the writer connection, and inserts random blobs until timeout. It prints checkpoint mode, peak WAL frames, and transaction count, then joins readers. The passive variant expects large WAL growth; the restart variant expects the WAL to stay near the frame limit.

### State and persistence behavior
All activity is in `test.db` and its WAL file. Readers hold transactions open across sleeps, preserving snapshots. The writer appends rows and performs hook-driven checkpoints.

### Dependencies and integration points
This file relies on `threadtest3.c` infrastructure, SQLite WAL hooks, WAL checkpoint APIs, and shared `Error`, `Sqlite`, and `Threadset` types. It is included into `threadtest3.c`, not compiled alone.

### Risks and test signals
The assertions depend on scheduler timing and filesystem speed; slow or unusual environments can alter frame growth. Signals are no reader isolation failures, printed peak WAL frames, transaction count, and explicit errors if passive WAL does not grow or restart WAL grows too large.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_checkpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_index.c -->
## sources/storage-engines/sqlite/test/tt3_index.c

### Purpose
`tt3_index.c` adds `create_drop_index_1` to `threadtest3`, stressing concurrent index DDL and ordered reads in shared-cache mode.

### Important APIs, types, and functions
`create_drop_index_thread()` repeatedly opens `test.db`, drops four indexes if present, recreates them, selects rows ordered by each indexed column, clears expected `SQLITE_LOCKED`, and closes. `create_drop_index_1()` initializes table `t11`, enables shared cache, launches five worker threads, then disables shared cache.

### Control flow
Setup creates `t11(a,b,c,d)` and fills it with 100 rows. Workers run until the shared stop time expires. Each iteration performs DDL churn and read queries from a fresh connection.

### State and persistence behavior
The only persistent state is `test.db`, table `t11`, and transient indexes `i1` through `i4`. Indexes may exist or be absent depending on the exact interleaving when the test ends.

### Dependencies and integration points
The file depends entirely on `threadtest3` helper macros, `sqlite3_enable_shared_cache()`, and SQLite schema-lock behavior. It is included by `threadtest3.c`.

### Risks and test signals
`SQLITE_LOCKED` is expected and cleared, so unexpected schema or corruption failures are the important signal. A successful run prints worker `ok` messages and no global errors. This test is sensitive to shared-cache behavior and DDL lock acquisition changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_lookaside1.c -->
## sources/storage-engines/sqlite/test/tt3_lookaside1.c

### Purpose
`tt3_lookaside1.c` adds `lookaside1`, a shared-cache race probe focused on lookaside allocation and statement finalization while readers and a writer operate concurrently.

### Important APIs, types, and functions
`lookaside1_thread_reader()` prepares `SELECT 1 FROM t1`, steps through rows, and inside the loop runs a second query over `t2`, then checks finalize errors. `lookaside1_thread_writer()` repeatedly updates `t3` inside a rolled-back transaction. `lookaside1()` creates the schema and launches five readers plus one writer.

### Control flow
Setup builds two `WITHOUT ROWID` tables and a small blob table. Readers repeatedly prepare, step, execute nested SQL through the harness, and finalize. The writer loops on `BEGIN`, `UPDATE`, `ROLLBACK` until timeout. Shared cache is enabled only for the test body.

### State and persistence behavior
`test.db` contains `t1`, `t2`, and `t3`. The writer rolls back all updates, so persistent logical state should remain stable. The test stresses connection-local statement and lookaside state rather than durable data changes.

### Dependencies and integration points
The file depends on `threadtest3` infrastructure, shared-cache mode, SQLite lookaside behavior, `WITHOUT ROWID` handling, and prepared statement finalization semantics.

### Risks and test signals
The expected failure mode is a race surfacing as prepare/step/finalize or lock errors. Since the writer rolls back, data validation is minimal. Signals are clean reader/writer `ok` summaries and no finalize errors reported through `sqlite_error()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_lookaside1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_shared.c -->
## sources/storage-engines/sqlite/test/tt3_shared.c

### Purpose
`tt3_shared.c` adds `shared1`, a minimal shared-cache connection churn test. It repeatedly opens connections and scans a simple table from multiple threads.

### Important APIs, types, and functions
`shared_thread1()` loops until timeout, opening `test.db`, running `SELECT * FROM t1`, and closing. `shared1()` creates `t1`, enables shared cache, launches five `shared_thread1` workers, joins them, and disables shared cache.

### Control flow
The setup is intentionally small: create an empty table, then run concurrent open/select/close cycles for the configured duration. All error handling is delegated to the `threadtest3` wrappers.

### State and persistence behavior
`test.db` contains only table `t1`, and no worker modifies it. The test is about shared-cache lifecycle state and schema access under concurrent connection churn.

### Dependencies and integration points
This file depends on `threadtest3` infrastructure and SQLite shared-cache support. It is included into the `threadtest3` executable.

### Risks and test signals
Because there are no writes, this test mostly detects shared-cache open/close, schema, and reference-counting regressions. Signals are five `done!` thread results and no global errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_stress.c -->
## sources/storage-engines/sqlite/test/tt3_stress.c

### Purpose
`tt3_stress.c` contributes two broad shared-cache stress tests to `threadtest3`. `stress1` mixes schema creation/drop, reads, inserts, deletes, and connection churn. `stress2` runs a larger set of concurrent workload classes including DDL, DML, VACUUM, integrity checks, journal-mode switching, and rapid open/close.

### Important APIs, types, and functions
`stress_thread_1()` through `_5()` implement `stress1` worker classes. `stress2_workload1()` through `_17()` implement individual workload functions, while `stress2_workload19()` handles connection churn. `Stress2Ctx`, `stress2_thread_wrapper()`, and `stress2_launch_thread_loop()` adapt workload functions to threadtest3 threads.

### Control flow
`stress1` sets the stop time, enables shared cache, launches two table create/drop workers, two schema scan workers, two table read workers, two insert workers, and two delete workers, then joins all threads. `stress2` initializes `t0` and index `i0`, enables shared cache, launches one thread per workload function plus two connection-churn threads, then joins them.

### State and persistence behavior
Both tests use `test.db`. `stress1` intentionally makes table `t1` appear and disappear, so many `SQLITE_LOCKED` and `SQLITE_ERROR` results are expected and cleared. `stress2` keeps base table `t0` but creates and drops side tables, changes journal mode, vacuums, and mutates rows concurrently.

### Dependencies and integration points
The file relies on `threadtest3` wrappers, shared-cache mode, SQLite recursive CTE support for bulk inserts, VACUUM, `PRAGMA integrity_check`, and journal-mode transitions.

### Risks and test signals
The stress tests intentionally tolerate several concurrency errors, so the risk is clearing too broad a class of failures. There is also a small leak of `Stress2Ctx` allocations because thread return cleanup does not free the context. Signals are per-thread attempt summaries, no unhandled errors after expected clears, and the final threadtest3 global error count.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_vacuum.c -->
## sources/storage-engines/sqlite/test/tt3_vacuum.c

### Purpose
`tt3_vacuum.c` adds `vacuum1`, a shared-cache test that runs VACUUM concurrently with write-heavy table activity.

### Important APIs, types, and functions
`vacuum1_thread_writer()` repeatedly inserts 100 blob rows, deletes by rowid, and selects rows ordered by primary key, clearing expected `SQLITE_LOCKED`. `vacuum1_thread_vacuumer()` repeatedly runs `VACUUM`, also clearing `SQLITE_LOCKED`. `vacuum1()` initializes the table and index, enables shared cache, launches three writers and one vacuumer, then joins all threads.

### Control flow
The setup creates `t1(x PRIMARY KEY, y BLOB)` plus an index on `y`. Writers and the vacuumer run until the shared stop time expires. The test then disables shared cache and reports accumulated errors.

### State and persistence behavior
The test mutates `test.db` heavily, growing and compacting it while multiple connections are active. Inserts are durable unless interrupted by lock errors; deletes and selects are part of the stress loop. VACUUM rewrites the database file when it can obtain the required locks.

### Dependencies and integration points
This file depends on `threadtest3` infrastructure, SQLite shared-cache mode, VACUUM behavior, and lock handling across concurrent connections.

### Risks and test signals
Expected lock contention is cleared, so meaningful failures are unhandled SQLite errors, corruption, crashes, or global error count increments. Useful signals are `ok` summaries from all four workers and no final errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/test/tt3_vacuum.c -->
