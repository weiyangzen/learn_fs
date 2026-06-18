<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Util.pm -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Util.pm
Purpose: Miscellaneous Perl helpers for perf trace scripts, primarily time conversion and terminal clearing.

Important APIs/types/functions: Exports `avg`, `nsecs`, `nsecs_secs`, `nsecs_nsecs`, `nsecs_usecs`, `print_nsecs`, and `clear_term`; implemented functions include average, nanosecond composition/decomposition, `nsecs_str`, and ANSI clear-screen output.

Control flow: Scripts call helpers while processing events or printing summaries. There is no top-level runtime beyond exports.

State and persistence: Stateless except for the constant `$NSECS_PER_SEC`. No persistence.

Dependencies and integration points: Used by Perl scripts such as wakeup latency and rwtop. It parallels Python `Util.py`.

Risks: Export list includes names not implemented in this file (`nsecs_usecs`, `print_nsecs`), which can surprise callers if they rely on them. Time division returns Perl numeric values and formatting is caller-dependent.

Test signals: Wakeup latency and rwtop scripts indirectly exercise `avg`, `nsecs`, and `clear_term`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Util.pm -->
