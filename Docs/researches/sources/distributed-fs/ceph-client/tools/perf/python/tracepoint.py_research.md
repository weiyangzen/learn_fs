<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/tracepoint.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/tracepoint.py
Purpose: Example perf Python binding consumer for tracepoint samples, focused on `sched:sched_switch`. It streams context-switch records and prints decoded fields.

Important APIs/types/functions: `change_proctitle()` optionally uses `setproctitle`. `main()` creates `perf.cpu_map`, `perf.thread_map(-1)`, parses `sched:sched_switch`, disables tracking events, configures sample formats, mmaps the evlist, polls forever, and reads `perf.sample_event` instances.

Control flow: After setup, an infinite poll loop reads one event per CPU when available, ignores non-sample records, and prints timestamp plus previous/next task information.

State and persistence: Maintains live mmap buffers and perf event configuration only. Output is an unbounded stdout stream.

Dependencies and integration points: Requires perf Python bindings and sched tracepoint availability. Optional `setproctitle` only improves process listing.

Risks: Infinite runtime, permission requirements, and potential output volume are the main operational risks. It assumes sched_switch sample fields are exposed as Python attributes.

Test signals: Running under suitable privileges should print sched switch lines; failures isolate tracepoint decoding or mmap/poll binding issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/tracepoint.py -->
