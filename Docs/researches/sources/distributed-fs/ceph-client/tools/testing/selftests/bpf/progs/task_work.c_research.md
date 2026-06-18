<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work.c

Purpose: Positive tests for scheduling BPF task work from perf-event programs using hash, array, and LRU maps.

Important APIs/types/functions: Defines maps `hmap`, `arrmap`, `lrumap`, `process_work`, and perf_event programs `oncpu_*`.

Control flow: Perf-event handlers look up map elements and schedule task work; callback processes the element later.

State and persistence: Persistent state is map elements with embedded task-work state/counters.

Dependencies and integration: Depends on BPF task-work kfuncs/helpers and perf_event context.

Risks: Object lifetime between perf handler and deferred work is critical.

Test signals: Tests expect scheduled callbacks to run and map/counter state to reflect processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work.c -->
