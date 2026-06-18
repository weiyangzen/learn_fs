# sources/distributed-fs/ceph-client/tools/perf/scripts/python/syscall-counts.py

Purpose: `syscall-counts.py` summarizes syscall entry counts across the whole trace, optionally filtered by command name.

Important APIs and state: `for_comm` holds the optional filter and `syscalls` maps syscall ID to count. Perf entry points are `trace_begin`, `trace_end`, `raw_syscalls__sys_enter`, `syscalls__sys_enter`, and `print_syscall_totals`.

Control flow: callbacks filter by `common_comm` and increment counts. At end, the script prints a count-sorted table of syscall names and totals. The `syscalls__sys_enter` handler delegates to the raw tracepoint handler through `locals()`.

State and persistence: state is process-local and printed once on exit; no files are written.

Dependencies, integration, risks, and tests: it depends on perf's syscall tracepoint callback contract and `Util.syscall_name`. Risks include aggregating across all PIDs for a shared comm, missing output until the script exits, and memory growth bounded by syscall ID variety rather than event count. Test signals are expected syscall totals from a known workload and correct optional comm filtering.
