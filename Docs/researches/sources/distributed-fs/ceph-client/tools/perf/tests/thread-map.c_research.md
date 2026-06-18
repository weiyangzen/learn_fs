## sources/distributed-fs/ceph-client/tools/perf/tests/thread-map.c

Purpose: unit tests for thread map creation, synthesis, and removal.
Important functions: `test__thread_map`, `process_event`, `test__thread_map_synthesize`, and `test__thread_map_remove`.
Control flow: sets current process name to `perf`, creates a map by current PID and a dummy map, reads comms and validates pid/comm/refcount; synthesizes a thread map event and reconstructs it; creates a two-PID map and removes entries until empty, then verifies extra removal fails.
State and persistence: temporary `perf_thread_map` objects are refcounted and freed.
Dependencies and integration: thread map APIs, PR_SET_NAME, synthetic event callback path.
Risks: process name mutation affects current process during test; verbose output can print maps to stderr.
Test signals: three suites for thread map, synthesize thread map, and remove thread map return success on correct counts/refcounts.
