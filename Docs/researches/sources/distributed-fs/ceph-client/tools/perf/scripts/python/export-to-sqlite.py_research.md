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
