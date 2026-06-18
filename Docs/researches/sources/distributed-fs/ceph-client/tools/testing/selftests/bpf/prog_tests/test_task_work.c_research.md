<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_work.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_work.c

Purpose: validates BPF task-work scheduling from perf-event programs across hash, array, and LRU maps, and dispatches negative verifier tests.

Important APIs/types/functions: `perf_event_open()`, `struct elem` with `struct bpf_task_work`, `verify_map()`, `task_work_run()`, generated `task_work` and `task_work_fail` skeletons, `bpf_program__attach_perf_event()`, and map iteration via `bpf_map__lookup_elem()`.

Control flow: `task_work_run()` creates a pipe and child process, blocks the child until BPF is attached, opens skeleton with only one target program autoloaded, stores a userspace string pointer in BSS, loads, opens a hardware CPU-cycles perf event for the child, attaches, releases the child, waits for samples/exit, finds the target map, and verifies at least one map value contains `"hello world"`. Main runs hash/array/LRU variants and `RUN_TESTS(task_work_fail)`.

State and persistence: transient child process, pipe fds, perf event/link ownership, BPF maps with task-work entries, and userspace pointer in BSS. Cleanup unblocks/waits for child if needed.

Dependencies and integration: depends on perf hardware event support, task-work kfunc/helper support, generated skeletons, and ptr-to-user string handling in the BPF program. Integrated as `test_task_work`.

Risks: skips when `PERF_COUNT_HW_CPU_CYCLES` is unsupported. Sampling can be nondeterministic; child loop attempts to generate enough cycles. User pointer lifetime must outlive BPF use.

Test signals: pipe/fork/load/attach assertions, optional skip on unsupported perf, map verification that processed entries have expected data and at least one value was processed, plus negative `task_work_fail` skeleton results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_work.c -->
