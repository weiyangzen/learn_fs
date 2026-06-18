<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/failed-syscalls.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/failed-syscalls.pl
Purpose: Perl report script that counts failed system calls by command name.

Important APIs/types/functions: Handles `raw_syscalls::sys_exit` and aliases `syscalls::sys_exit` to it. `trace_end` prints counts sorted by descending errors. Optional first argument filters to one `comm`.

Control flow: Each syscall exit with negative `ret` increments `%failed_syscalls` keyed by `common_comm`. At trace end, rows are sorted and printed, skipping nonmatching comm values when a filter is provided.

State and persistence: `%failed_syscalls` is the only run state. Output is stdout; no files are written.

Dependencies and integration points: Paired with `bin/failed-syscalls-record` and `bin/failed-syscalls-report`. Uses perf's Perl event handler naming convention.

Risks: Counts by command name, not pid or syscall number, so processes sharing `comm` are aggregated. Raw vs typed syscall tracepoint availability varies by kernel.

Test signals: Recording failed syscalls then reporting should show nonzero rows for workloads that return negative syscall errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/failed-syscalls.pl -->
