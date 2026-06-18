# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pid.c

Purpose: Formats PID syscall arguments with the best-known command name.

Important APIs/types/functions: `syscall_arg__scnprintf_pid` prints the numeric pid and appends the thread comm when available.

Control flow: The function looks up or creates a thread in `trace->host`, lazily populates its comm from `/proc` if unset, appends `(<comm>)` when available, and releases the thread reference.

State and persistence: It can populate perf's in-memory thread cache with newly discovered comm values. No file state is written.

Dependencies and integration points: Depends on `machine__findnew_thread`, `thread__set_comm_from_proc`, `thread__comm_*`, and perf trace state.

Risks: PID reuse and `/proc` races can attach stale or missing names. Lookup can allocate during formatting.

Test signals: Trace syscalls with live, exited, and unknown PIDs; verify numeric output remains stable even when comm lookup fails.
