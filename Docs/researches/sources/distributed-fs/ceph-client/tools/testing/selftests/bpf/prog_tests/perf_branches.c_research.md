<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_branches.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_branches.c

Purpose: tests branch stack sampling access from BPF perf-event programs with and without hardware branch sampling support.

Important APIs and functions: `check_good_sample()` and `check_bad_sample()` validate BSS/sample fields from `test_perf_branches`. `test_perf_branches_common()` attaches the BPF program to a perf event fd, triggers execution, and checks sample status. `test_perf_branches_hw()` configures a hardware perf event with branch sampling. `test_perf_branches_no_hw()` covers the no-hardware or unsupported path. `test_perf_branches()` dispatches subtests.

Control flow: create perf event, attach skeleton program, generate workload or self-trigger, inspect whether branch records are present/valid or appropriately unavailable, close perf fd and skeleton.

State and persistence: perf event fd, BPF link/program state, and BSS sample fields are transient.

Dependencies and integration: depends on perf_event_open support, branch sampling hardware/kernel support, pthread/sched helpers, libbpf internals, and `test_perf_branches.skel.h`.

Risks and test signals: valid branch entries for hardware path and clean fallback behavior for no-hardware path are signals. Risks are architecture/perf permission differences, sampling nondeterminism, and hardware feature availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_branches.c -->
