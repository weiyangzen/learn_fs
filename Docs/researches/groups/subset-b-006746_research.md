# subset-b-006746 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/export-to-postgresql.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/export-to-postgresql.py

## Purpose

`export-to-postgresql.py` is a perf Python script that exports `perf script` database-export callbacks into a PostgreSQL database. It is aimed at heavy perf traces, especially Intel PT branch/call traces, where users want SQL queries, views, call tables, synthetic power-event tables, and downstream browsing with `exported-sql-viewer.py`.

The script accepts a database name, an optional column mode (`all` or `branches`), optional `calls` and `callchains` modes, and an optional `pyside-version-1` selector. It creates a new PostgreSQL database, streams perf records through temporary PostgreSQL binary COPY files, bulk-loads them with libpq `COPY FROM STDIN`, and then adds primary keys, foreign keys, indexes, and display views.

## Important APIs, Types, and Functions

The script uses the perf Python export API by setting `perf_db_export_mode = True` and by exposing callback names perf knows how to call: `trace_begin`, `trace_end`, `evsel_table`, `machine_table`, `thread_table`, `comm_table`, `comm_thread_table`, `dso_table`, `symbol_table`, `branch_type_table`, `sample_table`, `call_path_table`, `call_return_table`, `synth_data`, `context_switch_table`, `trace_unhandled`, and a no-op `sched__sched_switch`.

Qt SQL APIs are imported from PySide2 or PySide1 as `QSqlDatabase` and `QSqlQuery`. `do_query()` wraps `query.exec_()` and raises with the Qt SQL error. PostgreSQL bulk loading bypasses Qt and binds libpq via `ctypes`: `PQconnectdb`, `PQexec`, `PQputCopyData`, `PQputCopyEnd`, and `PQfinish`.

Schema creation covers `selected_events`, `machines`, `threads`, `comms`, `comm_threads`, `dsos`, `symbols`, `branch_types`, `samples`, optional `call_paths`, optional `calls`, `ptwrite`, `cbr`, `mwait`, `pwre`, `exstop`, `pwrx`, and `context_switches`. It also creates display views such as `samples_view`, `calls_view`, `call_paths_view`, `power_events_view`, and `context_switches_view`.

Record writer functions use `struct.pack()` in PostgreSQL binary COPY format. `open_output_file()` writes the `PGCOPY` header, each table callback appends one row, and `close_output_file()` appends the trailer. `synth_data()` demultiplexes synthetic Intel PT payload records by `config`: `0` ptwrite, `1` mwait, `2` pwre, `3` exstop, `4` pwrx, and `5` cbr.

## Control Flow and Data Flow

Startup parses arguments, creates an output directory named `<dbname>-perf-data`, creates the PostgreSQL database from the `postgres` database, reconnects to the new database, creates all tables/views, and opens one temporary binary file per table. The `branches` mode selects a narrower `samples` layout that excludes `period`, `weight`, `transaction`, and `data_src`; the default `all` mode keeps those fields.

During `trace_begin`, the exporter prints a progress message and writes sentinel id `0` rows for unknown event, machine, thread, comm, dso, symbol, and sample data. If call export is enabled it also writes the root call path and a zero call-return row. During trace processing, perf calls table callbacks with decoded values. Each callback writes one binary COPY row to the matching file, converting strings through `toserverstr()` on Python 3 and packing nullable-ish values as concrete ids rather than SQL NULLs.

At `trace_end`, the script streams every temporary file into PostgreSQL with `COPY <table> FROM STDIN (FORMAT 'binary')`, deletes the files, removes the temporary directory, adds primary keys and foreign keys, adds call indexes when `calls` is enabled, marks `comms.has_calls`, and drops empty optional tables/views. It warns if perf delivered unhandled events.

## State and Persistence Behavior

Persistent state is the new PostgreSQL database and the tables/views within it. Intermediate state lives in local binary files under `<dbname>-perf-data`; successful completion removes that directory. Failure paths can leave a created database or temporary files behind after database creation, because only the initial `CREATE DATABASE` failure removes the directory.

The script intentionally materializes unknown id `0` records to keep foreign key references valid without replacing zeros with NULLs. The schema is append-only during export and constrained only after bulk loading, which improves speed but means referential errors surface late. Optional power-event and context-switch tables are dropped if empty, so downstream code must probe table availability rather than assume every created table remains present.

## Dependencies and Integration Points

Runtime dependencies are perf's Python scripting environment, `PERF_EXEC_PATH`, PySide/PySide2 Qt SQL bindings, Qt's PostgreSQL driver, a reachable PostgreSQL server where the current user can create databases, and `libpq.so.5`. It integrates directly with `perf script -s .../export-to-postgresql.py` and with helper wrapper `scripts/python/bin/export-to-postgresql-report`.

The generated schema is consumed by `exported-sql-viewer.py` and by direct SQL clients such as `psql`. Its table and view names intentionally match `export-to-sqlite.py` closely so the viewer can support both backends. The `calls` and `callchains` switches must align with perf's database-export callbacks; without them, call graph viewer features are unavailable.

## Risks and Edge Cases

Database names and file paths are string-concatenated into SQL without quoting, so unusual names can break SQL and untrusted names are unsafe. Existing databases are not checked before `CREATE DATABASE`; reruns with the same name fail. Python 3 string conversion assumes UTF-8 server and client encodings. The `toclientstr()` helper returns bytes for Python 3, which works for `ctypes` but differs from Qt's native string path.

The binary COPY pack formats are tightly coupled to table column order. Any schema change requires matching `struct.pack()` updates or PostgreSQL will reject or silently misinterpret data. The code loads `libpq.so.5` by soname and does not handle platforms where the library is elsewhere. Late foreign-key creation means bad perf callback ordering or missing sentinel rows can waste a full export before failing. Empty-table pruning can surprise clients that expected a created-but-empty table.

## Test Signals

Useful smoke tests are `perf record -e intel_pt//u` followed by `perf script -s export-to-postgresql.py <dbname> branches calls`, verifying progress reaches `Done`, `psql <dbname> -c '\d'` shows the schema, and `samples_view`, `calls_view`, and `call_paths_view` return rows. A non-call export should omit `calls` features while still providing samples. Synthetic data tests should verify `ptwrite_view`, `power_events_view`, and `context_switches_view` appear only when backed by rows. Failure tests should cover existing database names, missing Qt PostgreSQL driver, missing libpq, and bad `PERF_EXEC_PATH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/export-to-postgresql.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/export-to-sqlite.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/export-to-sqlite.py

## Purpose

`export-to-sqlite.py` exports perf database-export callbacks into a SQLite3 database. It provides the same logical perf schema as `export-to-postgresql.py` but stores it in a local SQLite file and uses prepared Qt SQL inserts rather than PostgreSQL binary COPY. It is the lightweight path for creating a portable database that can be browsed with `sqlite3` or `exported-sql-viewer.py`.

The command-line shape mirrors the PostgreSQL exporter: `<database name> [all|branches] [calls] [callchains] [pyside-version-1]`. `branches` creates a narrower samples table, `calls` creates both `calls` and `call_paths`, and `callchains` creates `call_paths` without the call-return table.

## Important APIs, Types, and Functions

The script sets `perf_db_export_mode = True` and implements perf callback functions with names matching the database-export interface. `QSqlDatabase.addDatabase('QSQLITE')` opens the target file, `QSqlQuery.prepare()` builds insert statements, and `bind_exec()` adds bound values before executing a prepared query.

The schema includes the same core tables and most of the same views as the PostgreSQL exporter: `selected_events`, `machines`, `threads`, `comms`, `comm_threads`, `dsos`, `symbols`, `branch_types`, `samples`, optional `call_paths`, optional `calls`, Intel PT synthetic event tables, and `context_switches`. The only intentional schema naming difference called out by the source is `samples.transaction_`, because `transaction` is reserved in SQLite.

SQLite-specific helpers include `sqlite_has_printf` detection and `emit_to_hex()`, which emits `printf("%x", column)` for newer SQLite and raw column values otherwise. Synthetic data callbacks parse raw buffers with `struct.unpack_from()` and bind values into the appropriate synthetic event table.

## Control Flow and Data Flow

Startup imports PySide2 when available, falls back to PySide1, validates arguments, rejects an already existing output file, opens a SQLite database, disables journaling with `PRAGMA journal_mode = OFF`, and creates the schema inside a transaction. It then prepares one insert query per destination table.

`trace_begin` starts the write transaction and inserts id `0` sentinel rows. Each perf callback converts incoming values to strings via `addBindValue(str(xx))` and executes the prepared insert. `sample_table()` is the only conditional writer: in `branches` mode it binds the first fifteen common sample fields and then fields 19 through 24 to match the reduced samples table, skipping `period`, `weight`, `transaction`, and `data_src`.

`trace_end` commits the transaction, creates call-related indexes when applicable, adds `comms.has_calls`, drops empty optional tables/views, prints a warning for unhandled events, and finishes. Unlike the PostgreSQL exporter, primary keys are declared inline at table creation and foreign keys are not added after load.

## State and Persistence Behavior

Persistent state is a single SQLite database file named by the user. The script refuses to overwrite an existing file. There are no intermediate data files. The transaction stays open across the trace export, so a large export accumulates uncommitted changes until `trace_end`; interrupted runs can leave a partial or unusable database file.

The script disables journaling for speed, trading crash resistance for throughput. Values are bound as strings even for numeric columns, relying on SQLite affinity and Qt conversion. Optional tables are created early but may be removed at the end if empty, matching viewer expectations that capabilities are probed dynamically.

## Dependencies and Integration Points

Dependencies are perf's Python scripting environment, `PERF_EXEC_PATH`, PySide/PySide2 Qt SQL bindings, and Qt's SQLite driver. It integrates with `perf script -s .../export-to-sqlite.py`, helper wrapper `scripts/python/bin/export-to-sqlite-report`, the command-line `sqlite3` tool, and `exported-sql-viewer.py`.

The exporter intentionally keeps table names, view names, and report-facing columns close to the PostgreSQL exporter so the GUI viewer can issue backend-neutral queries with only small adaptations for booleans, hex formatting, and metadata introspection.

## Risks and Edge Cases

`PRAGMA journal_mode = OFF` can corrupt or truncate results if the process or host fails mid-export. Binding every value as `str()` may hide type issues until later query sorting or arithmetic. The database existence check opens the path without mode and catches all exceptions; permission errors and non-file paths are not distinguished from nonexistence. SQL statements are assembled by string concatenation for table drops and views; user-controlled database names are not embedded in SQLite SQL, but report clauses in the viewer later can be raw SQL.

The fallback `emit_to_hex()` returns raw numeric columns on older SQLite, so display output can differ across systems. The `branches` and `all` sample layouts must stay synchronized with perf callback argument order. As with PostgreSQL, dropping empty optional tables means clients must test table presence.

## Test Signals

Run a small `perf record -e intel_pt//u` trace through `perf script -s export-to-sqlite.py pt_example branches calls`, verify the file is created, and query `samples_view`, `calls_view`, and `call_paths_view` with `sqlite3`. A second run with the same output name should fail before writing. Tests should compare the SQLite and PostgreSQL schemas for viewer-visible columns, exercise both `branches` and `all` modes, and verify empty synthetic/context-switch tables are dropped while non-empty ones keep their views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/export-to-sqlite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/exported-sql-viewer.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/exported-sql-viewer.py

## Purpose

`exported-sql-viewer.py` is a Qt MDI GUI for browsing databases created by `export-to-sqlite.py` and `export-to-postgresql.py`. It provides context-sensitive call graphs, chronological call trees, branch-event reports with optional disassembly, selected-branch filtering, top-calls reports, context-switch time charts by CPU, generic table browsing, clipboard export, find bars, and built-in help.

The script can either open a database or show only help text. For PostgreSQL it accepts a Qt/libpq-style connection string with host, port, user, password, and dbname options. For SQLite it detects the database file by checking the `SQLite format 3` header.

## Important APIs, Types, and Functions

The GUI uses PySide2 or PySide1 modules from QtCore, QtGui, QtSql, and QtWidgets. It uses `QSqlDatabase`/`QSqlQuery` for database access, `QAbstractItemModel` and `QAbstractTableModel` subclasses for lazy models, `QTreeView` and `QTableView` for reports, `QMdiArea` for subwindows, and `QGraphicsScene`/`QGraphicsItem` for the time chart. Optional branch disassembly uses `libxed.LibXED` through the local `libxed` Python wrapper and `ctypes` buffers.

Foundational model classes are `TreeModel` and `TableModel`. `LookupCreateModel()` and `LookupModel()` cache expensive models in a `weakref.WeakValueDictionary`. `FindBar` provides reusable exact/pattern search UI. `Thread` wraps `QThread` for non-blocking GUI tasks.

Call graph functionality is implemented by `CallGraphLevel*` item classes, `CallGraphModelParams`, `CallGraphModelBase`, `CallGraphModel`, and `CallGraphWindow`. Call tree functionality mirrors it with `CallTreeLevel*`, `CallTreeModel`, and `CallTreeWindow`. Both query `calls`, `call_paths`, `symbols`, `dsos`, `comms`, `threads`, and `comm_threads`.

Large SQL result streaming is handled by `SQLFetcherProcess`, `SQLFetcherFn`, and `SQLFetcher`. A child `multiprocessing.Process` opens its own database connection, runs chunked SQL, pickles rows into a shared ring buffer, and signals the GUI thread as records arrive. `FetchMoreRecordsBar` lets users request more chunks.

Branch reporting uses `BranchModel`, `BranchLevelOneItem`, `BranchLevelTwoItem`, `BranchWindow`, and data prep functions such as `BranchDataPrep()` and `BranchDataWithIPCPrep()`. Generic table viewing uses `SQLAutoTableModel`, `SQLTableModel`, and `TableWindow`. Top calls use `TopCallsModel`, `TopCallsDialog`, and `TopCallsWindow`.

Time-chart functionality is centered on `SwitchGraphDataCollection`, `SwitchGraphData`, `SwitchGraphWidget`, `SwitchGraphGraphicsItem`, `SwitchGraphDataGraphicsItem`, `SwitchGraphLegend`, `GraphAttributes`, and related geometry/region classes. Global database and runtime state live in `Glb`; backend connection logic lives in `DBRef`; application wiring is in `MainWindow` and `Main()`.

## Control Flow and Data Flow

`Main()` parses options, optionally shows help, detects SQLite, opens a main database connection via `DBRef.Open()`, builds a `Glb` object, starts `QApplication`, creates `MainWindow`, runs the event loop, shuts down background instances, closes the database, and exits.

`MainWindow` builds menus based on database capability probes. `IsSelectable()` determines whether tables or columns exist, so reports appear only when the export contains needed data. Reports create subwindows through `AddSubWindow()`, and subwindow names are made unique. Generic table menus are built from `sqlite_master` for SQLite or `information_schema` for PostgreSQL.

Call graph data flows from `comms` to `threads` to aggregated child `calls` grouped by `call_path_id`. Percent columns are computed relative to the parent node, and IPC columns appear if `calls.insn_count` and `calls.cyc_count` are selectable. Call tree data uses `calls.parent_id` and call time ordering instead of aggregation.

Branch data is fetched lazily in id order with `SQLFetcher`. Each top-level branch row contains time, CPU, command, pid/tid, branch type, transaction state, optional IPC data, and a formatted source-to-target branch string. Expanding a branch row may disassemble target instructions by finding the DSO in the perf build-id cache or kernel core file and decoding bytes with XED.

Time-chart data flows from `context_switches`: one graph is built per CPU, horizontal regions identify scheduled tasks, a legend maps colors to pid/tid/comm, and mouse hover/rubber-band selection updates labels, highlights, zoom state, and optional right-click call-tree navigation.

## State and Persistence Behavior

The viewer does not modify exported perf databases during normal browsing. It keeps transient UI state in models, find contexts, selection state, graph zoom history, cached models, and background fetch buffers. `Glb` caches host machine id and start/finish times, stores the build-id directory, tracks live fetchers for shutdown, and keeps the optional disassembler instance.

Background fetchers own separate database connections and process state. `Glb.ShutdownInstances()` asks them to stop when the application exits. Report windows are deleted on close via `Qt.WA_DeleteOnClose`, while weak model caching allows reuse when windows still reference a model and cleanup when they do not.

## Dependencies and Integration Points

The primary integration contract is the schema produced by the two exporters: table names, view names, id columns, call-path relationships, optional `has_calls`, optional `context_switches`, optional synthetic power tables, and backend-specific boolean literals. `DBRef.TRUE` and `DBRef.FALSE` abstract SQLite `1`/`0` versus PostgreSQL `TRUE`/`FALSE`.

External dependencies include PySide/PySide2, Qt SQL drivers for SQLite and PostgreSQL, Python multiprocessing, `libxed` for disassembly, `perf report --header-only` indirectly for generated databases, the perf build-id cache under `PERF_BUILDID_DIR` or `~/.debug/.build-id`, and optional `PERF_KCORE` for kernel disassembly.

## Risks and Edge Cases

Several SQL fragments are built by concatenating user-entered values or raw SQL clauses from dialogs. This is acceptable for a local diagnostic GUI but unsafe for hostile database contents or shared PostgreSQL credentials. Find and filter behavior differs by backend: PostgreSQL uses LIKE/ILIKE-style assumptions while SQLite uses GLOB for patterns.

The lazy fetcher pickles rows into a fixed 16 MiB ring buffer. Very large individual rows can exhaust buffer assumptions, and process/thread shutdown depends on event signaling. `SQLFetcher` creates additional database connections, so PostgreSQL connection limits and SQLite locking behavior matter.

Disassembly is best-effort. It assumes object code is present in the build-id cache or kernel core path, supports only XED, caps decoded ranges, and mostly assumes the current machine rather than virtualization. In Python 3, `Is64Bit()` compares an ELF byte prefix with a string literal, so it can fail to identify file class and fall back to pointer-size mode.

Some SQL appears fragile against the declared exporter schema. In `Glb.CallsMinTime()` and `Glb.CallsMaxTime()`, the join references `threads.thread_id`, but exporter `threads` tables use `id`, `machine_id`, `process_id`, `pid`, and `tid`; these helpers catch query failures through `SelectValue()`, so call timing may be omitted from global start/finish calculations rather than crashing. The raw SQL filter fields can also create invalid SQL that only fails when a report is opened.

## Test Signals

Basic validation is opening both a SQLite export and PostgreSQL export and verifying menus match available tables. Call export databases should show context-sensitive call graph, call tree, and top-calls reports; branch exports should show all/selected branch reports; context-switch exports should show the time chart. Large samples tables should fetch incrementally and continue fetching with `F8`/Fetch More. Clipboard copy should work for tree and table selections in aligned and CSV modes.

Disassembly tests need a trace whose DSOs are present in the build-id cache and should verify branch row expansion produces decoded instructions. Backend tests should verify table introspection for SQLite `sqlite_master` and PostgreSQL `information_schema`. Regression tests should cover Python 2/PySide1 compatibility paths only if that support is still intended, because many workarounds are version-specific.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/exported-sql-viewer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/failed-syscalls-by-pid.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/failed-syscalls-by-pid.py

## Purpose

`failed-syscalls-by-pid.py` is a small perf trace script that summarizes failed system calls by command, pid, syscall id, and errno. It can optionally filter to a single command name or pid supplied on the script command line. It is intended for live or recorded syscall tracing where the useful output is a final aggregate report rather than per-event logging.

## Important APIs, Types, and Functions

The script imports perf trace helpers from `perf_trace_context`, `Core`, and `Util` after extending `sys.path` with `PERF_EXEC_PATH`. `autodict()` provides nested dictionaries that auto-create levels, `syscall_name()` maps syscall ids to names, and `strerror()` formats negative return codes.

Perf entry points are `trace_begin()`, `trace_end()`, `raw_syscalls__sys_exit()`, and `syscalls__sys_exit()`. The raw tracepoint handler receives the common perf fields plus `id` and `ret`; the non-raw handler forwards to the raw implementation using `locals()`.

## Control Flow and Data Flow

Startup parses zero or one optional argument. If the argument parses as an integer it becomes `for_pid`; otherwise it becomes `for_comm`. More than one argument exits with the usage string. `trace_begin()` prints a message instructing the user to stop with Ctrl-C.

For every syscall exit event, the handler applies the optional comm/pid filter, checks `ret < 0`, and increments `syscalls[comm][pid][id][ret]`. `trace_end()` calls `print_error_totals()`, which iterates the nested dictionaries and prints each command/pid group, syscall name, errno string, and count sorted by count and errno descending within each syscall id.

## State and Persistence Behavior

All state is in-memory in the global `syscalls` autodict plus optional filter globals. There is no file or database output. Data persists only until the perf script process ends, at which point the summary is printed to stdout.

## Dependencies and Integration Points

The script depends on perf's Python scripting loader, `PERF_EXEC_PATH`, and syscall tracepoints that provide `syscalls:sys_exit` or `raw_syscalls:sys_exit` fields. The helper wrapper `scripts/python/bin/failed-syscalls-by-pid-report` invokes it through `perf script`.

## Risks and Edge Cases

The usage string names `syscall-counts-by-pid.py`, which does not match this script name. Long-running system-wide traces can accumulate many nested dictionary entries. Sorting is only inside each syscall's errno bucket; command and pid iteration follows dictionary key order, which can be non-deterministic on older Python. The filter treats numeric command names as pids, so a process literally named like digits cannot be selected by comm.

## Test Signals

Trace a workload that intentionally fails syscalls, such as opening missing files, and verify the report groups by `comm [pid]`, syscall name, and errno. Run with a pid filter and a comm filter to verify excluded events do not increment counts. A no-failure trace should print headers with no syscall detail. Compatibility testing should exercise both raw and non-raw syscall exit callback signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/failed-syscalls-by-pid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/flamegraph.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/flamegraph.py

## Purpose

`flamegraph.py` converts perf script sample events into a d3-flame-graph compatible stack tree and writes either an HTML flame graph or raw JSON. It is used by `perf script report flamegraph` and by the combined `perf script flamegraph ...` flow. It supports optional event-name filtering, output path selection, template selection, color scheme selection, and controlled template download.

## Important APIs, Types, and Functions

`Node` is the stack-tree node type. It stores `name`, `libtype` (`root`, `kernel`, or user-space empty string), sample `value`, and child nodes, and serializes to the compact JSON keys expected by the d3 template.

`FlameGraphCLI` owns parsed arguments and the root `Node("all", "root")`. `get_libtype_from_dso()` tags kernel frames from `[kernel.kallsyms]` or `/vmlinux`. `find_or_create_node()` performs linear child lookup and insertion. `process_event()` maps perf event dictionaries into folded tree paths. `get_report_header()` shells out to `perf report --header-only` unless input is `-`. `trace_end()` serializes the final tree, loads or downloads an HTML template when needed, substitutes JSON placeholders, validates the known CDN template MD5 when downloaded, and writes stdout or a file.

At module execution, `argparse` builds options and assigns perf-visible globals `process_event = cli.process_event` and `trace_end = cli.trace_end`.

## Control Flow and Data Flow

For each event, `process_event()` first filters by `event["ev_name"]` if `--event` was provided. It creates a top-level child per command, adding `(<pid>)` for user processes and treating pid `0` as kernel. If the event has a `callchain`, entries are reversed so the call stack is root-first and then inserted node by node. Without a callchain, the event's own `symbol` and `dso` become a single leaf. The leaf node's `value` increments by one sample.

At end of trace, the root stack is serialized. In JSON mode the output is `stacks.json` or the requested path. In HTML mode, the script reads a local d3-flame-graph template when present, may prompt or auto-download the upstream template when allowed, falls back to a minimal embedded HTML template on read failure, replaces `/** @options_json **/` and `/** @flamegraph_json **/`, and writes `flamegraph.html` or the requested output.

## State and Persistence Behavior

The main state is the in-memory tree of `Node` objects. Output is a JSON or HTML file unless `-o -` sends it to stdout. In HTML mode, the output embeds the complete stack JSON and report options. The script does not persist intermediate folded stacks. It may perform a network download for the template if the template path is missing and the user agrees or `--allow-download` is set.

## Dependencies and Integration Points

Dependencies are Python standard modules, perf's JSON-like Python event dictionaries, `perf report --header-only` for optional report context, and d3/d3-flame-graph assets referenced by the chosen HTML template. The wrapper `scripts/python/bin/flamegraph-report` invokes it under `perf script`.

The output schema uses d3-flame-graph's compact fields `n`, `l`, `v`, and `c`, with libtype tagging that can color kernel frames differently. HTML mode integrates with packaged `/usr/share/d3-flame-graph/d3-flamegraph-base.html` or the jsDelivr CDN.

## Risks and Edge Cases

Child lookup is linear, so traces with many siblings under the same node can be slower than a dict-backed tree. Events with missing expected keys such as `comm`, `sample`, or `callchain` can raise. Kernel/user classification relies on pid and DSO strings and can misclassify unusual samples. In live mode (`input == "-"`) the script refuses template download because stdin is occupied, so missing local templates require JSON output or preinstalled assets.

The downloaded template MD5 is hard-coded. Any upstream template change prompts the user or exits if declined. HTML output can depend on remote JavaScript/CSS if the minimal template is used or if the selected template references CDNs. `get_report_header()` failure is non-fatal but silently removes contextual header information except for a stderr message.

## Test Signals

Record with `perf record -g` and run `perf script report flamegraph`; verify `flamegraph.html` opens and contains non-empty stack data. Run `--format json -o -` on a small trace and validate JSON structure with root `all`. Run with `--event` on a multi-event perf.data and verify only that event contributes samples. Test missing template behavior with and without `--allow-download`, and test `input == "-"` live mode to ensure it does not prompt for download.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/flamegraph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/futex-contention.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/futex-contention.py

## Purpose

`futex-contention.py` measures time spent blocked in futex waits and prints per-thread, per-lock contention statistics. It is a perf Python translation of an older SystemTap futex contention example and is designed for syscall tracepoint runs where contention is inferred from `futex(FUTEX_WAIT, ...)` duration.

## Important APIs, Types, and Functions

The script imports `FUTEX_CMD_MASK`, `FUTEX_WAIT`, `nsecs()`, and `add_stats()` from perf's `Util` library. Global dictionaries are `thread_thislock`, `thread_blocktime`, `lock_waits`, and `process_names`.

Perf callbacks are `syscalls__sys_enter_futex()`, `syscalls__sys_exit_futex()`, `trace_begin()`, and `trace_end()`. The enter callback records wait start state for `FUTEX_WAIT`; the exit callback computes elapsed nanoseconds and updates aggregate min/max/average/count stats.

## Control Flow and Data Flow

On futex enter, the script masks `op` with `FUTEX_CMD_MASK` and ignores anything other than `FUTEX_WAIT`, so wake operations and non-blocking commands do not contribute. For wait calls, it stores the thread's command name, lock address `uaddr`, and start time in nanoseconds.

On futex exit, if the tid has a recorded start time, elapsed time is `nsecs(exit) - thread_blocktime[tid]`. The script calls `add_stats(lock_waits, (tid, lock), elapsed)` and removes the per-thread active wait state. At trace end it iterates `lock_waits` and prints command, tid, lock address, count, average, max, and min nanoseconds.

## State and Persistence Behavior

State is entirely in-memory. `thread_blocktime` and `thread_thislock` hold active waits, while `lock_waits` holds long-lived aggregate stats keyed by `(tid, lock)`. `process_names` maps tid to the last observed command name. No files or databases are written.

## Dependencies and Integration Points

The script depends on perf's Python syscall tracepoint naming and `PERF_EXEC_PATH` utility modules. The helper wrapper `scripts/python/bin/futex-contention-report` runs it via `perf script`. It integrates with syscall traces that include futex enter and exit events with arguments `nr`, `uaddr`, `op`, `val`, `utime`, `uaddr2`, and `val3`.

## Risks and Edge Cases

The script measures syscall duration for all `FUTEX_WAIT` calls, which includes scheduler time and may include waits that return due to timeout, signal, or error. It does not inspect the futex exit return value, so failed or interrupted waits still contribute elapsed time. Active waits left open at trace end are not reported. Reused tids can merge stats if the trace spans thread exit and new thread creation. Lock addresses are process virtual addresses, so the same numeric address in different processes may not represent the same futex object, although the key includes tid.

## Test Signals

A workload with two threads contending on a pthread mutex should print at least one `lock <addr> contended` line with count and nanosecond stats. A workload with futex wakes but no waits should produce no contention rows. Tests should include interrupted waits and timeouts to decide whether current inclusion semantics are acceptable. A trace with unmatched enter or exit events should not crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/futex-contention.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/gecko.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/gecko.py

## Purpose

`gecko.py` converts perf samples into Firefox's Gecko Profile JSON format so traces can be inspected in `https://profiler.firefox.com/`. It supports the normal `perf script report gecko` flow and the combined `perf script gecko ...` flow. By default it writes `gecko_profile.json`, starts a local HTTP server, and opens the hosted profile URL in the default browser; with `--save-only` it only writes the selected file.

## Important APIs, Types, and Functions

The script defines type aliases for string, stack, frame, category, and millisecond ids. Gecko row types are `Frame`, `Stack`, and `Sample` as `NamedTuple`s. The central builder is the `Thread` dataclass, which owns per-thread samples and intern tables: `frameTable`, `stringTable`, `stringMap`, `stackTable`, `stackMap`, and `frameMap`.

`Thread._intern_string()`, `_intern_frame()`, and `_intern_stack()` deduplicate profile entities and return ids. `_add_sample()` updates a thread's current comm and appends a timestamped sample for a root-first stack. `_to_json_dict()` emits the Gecko thread object with table schemas.

Perf entry points are `process_event()`, `trace_begin()`, and `trace_end()`. `CORSRequestHandler` adds an `Access-Control-Allow-Origin` header for profiler.firefox.com. `launchFirefox()` builds a `from-url` profiler URL. `main()` parses `--user-color`, `--kernel-color`, and `--save-only`, initializes category metadata, and sets the output path.

## Control Flow and Data Flow

When executed, `main()` parses arguments and defines two categories: User and Kernel, with configurable colors. During tracing, `trace_begin()` starts a daemon `http.server` thread on the default port when not in save-only mode. Each `process_event()` converts perf's sample timestamp from nanoseconds to milliseconds, initializes global `start_time` from the first sample, extracts pid/tid/comm, builds a stack from `callchain` entries when available, or falls back to the event's `symbol` and `dso`.

Stacks are formatted as `function (in dso)`. Callchains are reversed so root frames precede leaf frames. Samples are grouped by tid in `tid_to_thread`; each thread builder interns frames/stacks and appends a `Sample(stack_id, time_ms, responsiveness=0)`. At trace end, all thread builders are converted to JSON and wrapped with Gecko `meta`, empty `libs`, empty `processes`, and empty `pausedRanges`. The JSON is written to `output_file` or `gecko_profile.json`, and non-save-only mode opens Firefox Profiler against `http://localhost:8000/<file>`.

## State and Persistence Behavior

Global state includes `start_time`, `CATEGORIES`, `PRODUCT`, `output_file`, `tid_to_thread`, and `http_server_thread`. Per-thread intern tables persist for the duration of the conversion and reduce JSON size by sharing repeated strings, frames, and stack prefixes. Persistent output is the Gecko JSON file. Non-save-only mode also creates a local server rooted at the current working directory through `SimpleHTTPRequestHandler`.

## Dependencies and Integration Points

The script depends on perf's Python event dictionaries, `PERF_EXEC_PATH`, Firefox Profiler's Gecko profile schema, Python dataclasses, `http.server`, `webbrowser`, and the platform `uname -op` command used for the product string. Wrapper `scripts/python/bin/gecko-report` invokes it with `perf script -s`.

The profiler integration relies on CORS allowing `https://profiler.firefox.com` to fetch `http://localhost:8000/gecko_profile.json`. Category names and color strings are selected to match Firefox Profiler category CSS expectations.

## Risks and Edge Cases

`process_event()` indexes `param_dict['callchain']` directly, so events without that key can fail despite later fallback logic for empty callchains. `start_time` uses `if not start_time`, so a legitimate zero timestamp would be treated as uninitialized again. The local HTTP server uses `http.server.test()` with the default port, which can fail or serve the wrong directory if port 8000 is occupied or the process cwd changes. The server thread is daemonized and not explicitly shut down.

Kernel/user category detection in `_intern_frame()` is string-based: frames containing `kallsyms`, `/vmlinux`, or ending in `.ko)` are kernel, all others are user. The `stackMap` annotation says tuple keys, but implementation uses comma-separated strings; this works internally but can be confusing and could collide only if ids were not integers. The script imports many modules and perf helpers that are unused, increasing startup surface. Browser launch is best-effort and can be undesirable in headless environments unless `--save-only` is used.

## Test Signals

Run `perf record -g` followed by `perf script report gecko --save-only out.json` and validate that JSON contains `meta`, `threads`, `samples`, `frameTable`, `stackTable`, and `stringTable`. A no-callchain trace should still produce samples using `symbol`/`dso`. A normal non-save-only run should create `gecko_profile.json`, start an HTTP server, and open a profiler URL. Tests should cover custom category colors, occupied port 8000, missing callchain key, and traces with kernel frames to verify category assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/gecko.py -->
