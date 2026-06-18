<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-pid.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-pid.pl
Purpose: Perl report script that summarizes read/write activity and errors by pid.

Important APIs/types/functions: Handles syscall enter/exit for read and write. `%reads` tracks requested bytes, successful bytes read, errors, count, and comm. `%writes` tracks requested write bytes, write counts, errors, and comm. `trace_end` prints four tables: reads, failed reads, writes, failed writes.

Control flow: Enter handlers increment request totals. Exit handlers add successful read return values or error counts for failed reads/writes. End processing sorts by bytes read/written and by error count.

State and persistence: All state is in `%reads`, `%writes`, and `%unhandled`; output is stdout only.

Dependencies and integration points: Paired with `bin/rw-by-pid-record` and report wrapper. Uses syscall tracepoints produced by perf record.

Risks: Writes count requested bytes, not successful positive write return values. Long-running pid reuse can combine data if trace spans reuse. Some hash dereferences assume nested `errors` hashes exist and may warn for pids without errors.

Test signals: Replay a perf.data containing read/write syscalls and verify sorted pid tables and error tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-pid.pl -->
