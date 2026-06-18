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
