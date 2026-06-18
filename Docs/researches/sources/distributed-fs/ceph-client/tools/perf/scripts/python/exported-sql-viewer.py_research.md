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
