## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lock_contention.sh

Purpose: integration test for `perf lock record` and `perf lock contention`, including BPF mode, aggregations, filters, and CSV output.
Important functions: `check`, `test_record`, `test_bpf`, `test_record_concurrent`, `test_aggr_task`, `test_aggr_addr`, `test_aggr_cgroup`, `test_type_filter`, `test_lock_filter`, `test_stack_filter`, `test_aggr_task_stack_filter`, `test_cgroup_filter`, and `test_csv_output`.
Control flow: root and tracepoint availability are checked first, then a lock-contention perf.data is recorded from `perf bench sched messaging -p`. Subsequent tests replay the file or run live BPF contention with expected one-line or filtered output.
State and persistence: temp perf data, result, and stderr files are removed by traps; kernel BPF/tracepoint state is used but not persisted.
Dependencies and integration: requires root, `lock:contention_begin` tracepoints, at least four CPUs, `perf bench`, and optional BPF support.
Risks: workload may not always trigger specific locks like `tasklist_lock` or call stacks containing `unix_stream`; those subchecks skip when evidence is absent. Output column parsing is brittle to formatting changes.
Test signals: one quiet result line for top-N tests, zero nonmatching filter lines, valid comma counts, and skip code `2` for missing environment.
