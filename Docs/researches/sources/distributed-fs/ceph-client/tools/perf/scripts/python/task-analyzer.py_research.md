# sources/distributed-fs/ceph-client/tools/perf/scripts/python/task-analyzer.py

Purpose: `task-analyzer.py` analyzes `sched:sched_switch` traces, printing task runtime rows and optional summaries, extended inter-run timings, highlighting, filtering, and CSV exports.

Important APIs and types: `Task` records one scheduled-in interval. `Timespans` computes out-in, out-out, in-in, and in-out gaps between occurrences of the same task. `Summary` calculates per-TID runtime statistics and dynamic column alignment. Global `db` holds running tasks, completed tasks by CPU/TID, global order, and summary alignment metadata. Perf entry points are `trace_begin`, `trace_end`, and `sched__sched_switch`.

Control flow: `trace_begin` parses arguments, validates incompatible options, opens optional CSV files, disables colors when needed, initializes the database, and prints a trace header unless summary-only. Each switch converts raw sample time to `Decimal` seconds, applies the time window, finishes the previous PID on that CPU, and starts the next PID. Finish handling records PID from the sample, prints the row when not filtered, and indexes the task for summaries. `trace_end` emits summaries when requested.

State and persistence: running and historical task state is in memory. Optional CSV paths are opened for trace and summary output. Without `--summary`, record lists are trimmed to the latest item to reduce memory.

Dependencies, integration, risks, and tests: it depends on perf's scheduler tracepoint fields and raw sample time. Risks include open CSV descriptors not explicitly closed, use of `quit()` for time-window termination, possible `None` return from `_limit_filtered`, and sensitivity to missed switch-in events. Test signals are traces with known sched switches producing correct runtime rows, filters, highlights, CSV delimiters, and summary statistics.
