## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/examples/counting.c

Purpose: Demonstrates libperf counting mode using two software events.

Important APIs/functions: Initializes libperf logging, creates a dummy thread map, creates an evlist, allocates two evsels for CPU clock and task clock, sets maps, opens/enables/disables events, reads counts, and cleans up.

Control flow: Main sets two disabled perf event attributes with time-enabled/time-running read format. It creates a thread map for pid 0, adds evsels to the evlist, opens all FDs, enables, spins in a loop, disables, reads each evsel at CPU/thread index 0/0, prints values, closes and deletes resources.

State/persistence: Runtime-only perf FDs and reference-counted maps/evlist objects. No persistent output beyond stdout.

Dependencies/integration: Uses public libperf headers, Linux perf event types, and the `libperf_init()` print callback.

Risks: Busy-loop workload can be optimized away or behave differently under compiler settings. Error paths jump to cleanup but do not close partially opened evlist unless open succeeds. Requires perf_event permissions.

Test signals: Build example against installed libperf, run under permissive perf settings, verify two count lines with enabled/running fields, and run under restricted permissions to check failure messaging.
