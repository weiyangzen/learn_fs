<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-record
Purpose: Shell launcher for a perf script record phase. It records sched wakeup, wakeup_new, switch, and migrate_task events with a larger mmap buffer.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-record -->
