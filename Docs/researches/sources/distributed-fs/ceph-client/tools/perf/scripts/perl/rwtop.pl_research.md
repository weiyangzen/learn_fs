<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rwtop.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rwtop.pl
Purpose: Perl live-style report that periodically displays top read/write syscall activity by pid.

Important APIs/types/functions: Read/write enter/exit handlers update `%reads` and `%writes`; `trace_begin` installs a `SIGALRM` handler; `set_print_pending`, `print_check`, and `print_totals` implement interval refresh; `clear_term` refreshes the terminal.

Control flow: Optional argument sets the refresh interval, defaulting to 3 seconds. A signal marks output pending, event handlers check and print totals when safe, then reset accumulated read/write hashes after each display. `trace_end` prints any unhandled summary and final totals.

State and persistence: Uses `%reads`, `%writes`, `%unhandled`, `$print_pending`, and signal timer state. It intentionally resets totals after each interval and writes only to stdout.

Dependencies and integration points: Paired with `bin/rwtop-record` and report wrapper. Depends on POSIX signal handling and perf syscall tracepoints.

Risks: Signal-driven printing can be timing-sensitive. Counts are interval-local, not cumulative. Write byte totals are requested bytes. Output assumes a terminal for clear-screen behavior.

Test signals: Running the record/report pair while generating I/O should refresh top read/write rows at the selected interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rwtop.pl -->
