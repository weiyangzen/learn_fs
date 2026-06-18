<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/twatch.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/twatch.py
Purpose: Experimental thread lifetime/context-switch watcher using the perf Python interface. It demonstrates software dummy events with task/comm/context-switch records instead of sampling real hardware events.

Important APIs/types/functions: `main(context_switch=0, thread=-1)` builds `perf.cpu_map`, `perf.thread_map`, one `perf.evsel` with `TYPE_SOFTWARE` and `COUNT_SW_DUMMY`, opens it, wraps it in `perf.evlist`, mmaps, polls, and prints events.

Control flow: The function configures the evsel to record task and comm lifetime events, then loops forever reading events per CPU after each poll. The bottom comment documents using `context_switch=1` and a target pid to test switch records.

State and persistence: State is live perf maps and mmap buffers; no files are persisted. Output is stdout.

Dependencies and integration points: Depends on perf Python bindings and kernel perf record support for software dummy and task/context-switch records.

Risks: It has no CLI parser despite documented possible options. Infinite output and perf permissions are expected concerns.

Test signals: Launching the script should print task lifetime or switch records; selecting a target thread can validate switch-in/switch-out decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/twatch.py -->
