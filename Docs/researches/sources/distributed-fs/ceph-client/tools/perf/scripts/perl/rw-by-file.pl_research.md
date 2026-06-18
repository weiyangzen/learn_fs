<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-file.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-file.pl
Purpose: Perl report script that summarizes read/write syscall requests by file descriptor for a selected command name.

Important APIs/types/functions: Handlers `syscalls::sys_enter_read` and `syscalls::sys_enter_write` update `%reads` and `%writes`; `trace_end` prints sorted summaries; `trace_unhandled` tracks unrelated events.

Control flow: The script requires a `<comm>` argument. During replay, it only records syscalls whose `common_comm` equals that argument, accumulating read counts/bytes requested and write counts/bytes requested by fd. At the end it prints read and write tables.

State and persistence: `%reads`, `%writes`, and `%unhandled` are in-memory accumulators. No file path resolution is performed despite the name; fd numbers are reported.

Dependencies and integration points: Paired with `bin/rw-by-file-record` and report wrapper. Uses Perl perf script handler signatures for syscall enter events.

Risks: It records requested byte counts, not necessarily successful bytes. FD reuse across time is not disambiguated. Filtering by `comm` can miss renamed processes or aggregate unrelated processes.

Test signals: Run against a known command doing reads/writes and verify fd rows and counts appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-file.pl -->
