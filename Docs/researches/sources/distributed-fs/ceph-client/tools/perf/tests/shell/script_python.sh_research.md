## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_python.sh

Purpose: validates generated Python scripts from `perf script -g`.
Important functions: `check_python_support` and `test_script`.
Control flow: sets `PERF_EXEC_PATH`, checks libpython support, records either `sched:sched_switch` or `task-clock`, generates a Python script, appends a `process_event` callback for generic events if absent, then runs it and searches output.
State and persistence: temp perf.data and generated `.py` are cleaned.
Dependencies and integration: requires perf Python scripting and recordable tracepoint or generic event.
Risks: generated script behavior differs between tracepoint and generic events; permissions can skip both event attempts.
Test signals: output includes `sched__sched_switch` for tracepoint or `param_dict` for generic event.
