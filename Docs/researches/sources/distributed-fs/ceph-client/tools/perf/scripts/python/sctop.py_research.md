# sources/distributed-fs/ceph-client/tools/perf/scripts/python/sctop.py

Purpose: `sctop.py` periodically displays syscall counts like a simple top-style view for perf syscall traces.

Important APIs and state: global `for_comm`, `interval`, and `syscalls` hold filter and count state. `trace_begin` starts a background thread running `print_syscall_totals`; syscall callbacks update counters for `raw_syscalls:sys_enter` or `syscalls:sys_enter`.

Control flow: argument parsing accepts optional command name and interval. The printer thread clears the terminal, prints sorted syscall counts, clears the counter map, sleeps, and repeats forever. Event callbacks filter by `common_comm` when requested and increment the syscall ID count.

State and persistence: counters are in memory and are periodically reset after display. There is no durable output.

Dependencies, integration, risks, and tests: it depends on perf Python trace helpers, `clear_term`, `syscall_name`, thread/_thread availability, and syscall tracepoints. Risks include unsynchronized access between printer and callback, no graceful thread termination, and terminal-oriented output that is awkward in non-interactive logs. Test signals are a live syscall trace refreshing at the requested interval and showing changing counts.
