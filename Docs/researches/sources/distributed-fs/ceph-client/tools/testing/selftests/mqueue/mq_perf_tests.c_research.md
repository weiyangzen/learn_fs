<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_perf_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_perf_tests.c

## Purpose
Performance and stress benchmark for POSIX message queues, focused on large queue depths, send/receive latency, priority ordering patterns, and optional continuous cache-thrashing workloads pinned to selected CPUs.

## Important APIs, Types, and Functions
- Command-line options use popt: `--continuous/-c`, `--fake/-f`, and `--path/-p`.
- `shutdown()` frees CPU sets, stops worker threads, closes/unlinks the queue, and restores sysctls.
- `increase_limits()` raises `RLIMIT_MSGQUEUE`, grows mqueue maxima as far as accepted, and raises process priority.
- `open_queue()` creates the global queue and records actual attributes.
- Continuous workers: `cont_thread()` repeatedly fills and drains one message; `fake_cont_thread()` busy loops without mqueue operations.
- Benchmark worker `perf_test_thread()` times send/receive on an empty queue and near-full queue with constant, increasing, decreasing, and random priorities.

## Control Flow
`main()` requires root, parses CPU/path options, allocates a CPU set, opens and saves mqueue sysctls/limits, installs signal handlers, raises limits, opens the queue unless fake mode is selected, and creates CPU-pinned worker threads. Non-continuous mode runs one `perf_test_thread()` on the last online CPU and exits through cleanup. Continuous mode sleeps forever while worker threads run until signaled.

## State and Persistence Behavior
The program mutates mqueue sysctls, process rlimits, process nice value, CPU affinity, signal handlers, and a POSIX message queue. Cleanup restores sysctls and unlinks the queue, but it does not restore the nice value. Continuous mode intentionally persists until killed.

## Dependencies and Integration Points
Requires root, POSIX mqueue support, writable `/proc/sys/fs/mqueue` controls, pthread CPU affinity APIs, popt, realtime clocks, and scheduler/resource-limit syscalls. Built by the mqueue makefile.

## Risks and Edge Cases
`increase_limits()` loops until sysctls stop accepting larger values; behavior depends on kernel caps. Continuous fake mode does not open a queue and just consumes CPU. Signal-driven cleanup is important because worker threads can run forever. The CPU parser ignores out-of-range CPUs and rejects duplicate CPUs.

## Test Signals
Output includes initial/adjusted system state, queue attributes, timing totals, and nanoseconds per message for each workload. Root absence exits skip. Fatal errors call `shutdown()` with nonzero exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_perf_tests.c -->
