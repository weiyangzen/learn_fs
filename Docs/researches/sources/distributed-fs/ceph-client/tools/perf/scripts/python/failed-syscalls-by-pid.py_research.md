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
