# sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts-by-pid.py

Purpose: `syscall-counts-by-pid.py` summarizes syscall entry counts grouped first by command name and PID, then by syscall.

Important APIs and state: optional `for_comm` or `for_pid` filters are parsed from argv. `syscalls` is an auto-vivifying nested dictionary from comm to pid to syscall ID. `trace_begin`, `trace_end`, `raw_syscalls__sys_enter`, `syscalls__sys_enter`, and `print_syscall_totals` are the perf-facing functions.

Control flow: syscall-entry callbacks filter by command or PID and increment the nested count. The non-raw syscall callback delegates to the raw handler through `locals()`. At `trace_end`, output is sorted by syscall count within each comm/pid section and syscall IDs are resolved via `syscall_name`.

State and persistence: counts are in memory until the script exits or is interrupted, then printed to stdout. There is no external persistence.

Dependencies, integration, risks, and tests: it depends on perf Python trace helpers and syscall tracepoint signatures. Risks include command-name collisions across processes, non-deterministic comm/pid section order, and large memory use on long traces with many processes. Test signals are traces where a PID or comm filter reduces output and unfiltered runs show per-process syscall sections.
