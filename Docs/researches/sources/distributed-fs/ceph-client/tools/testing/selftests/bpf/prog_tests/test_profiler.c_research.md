<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_profiler.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_profiler.c

Purpose: smoke-tests three profiler skeleton variants by attaching them and invoking their raw tracepoint program through `bpf_prog_test_run_opts()`.

Important APIs/types/functions: `sanity_run()` supplies a three-element `__u64` context, runs a BPF program fd, and expects both syscall success and nonzero test-run retval. The main function loads/attaches `profiler1`, `profiler2`, and `profiler3`.

Control flow: open/load profiler1, attach, sanity-run `raw_tracepoint__sched_process_exec`; repeat for profiler2 and profiler3; destroy all skeletons in cleanup.

State and persistence: no durable state. Each skeleton may install tracepoint links until destroyed.

Dependencies and integration: depends on `progs/profiler.h`, generated profiler skeletons, raw tracepoint test-run support, and sched process exec tracepoint compatibility.

Risks: test-run context shape must match the BPF program expectations. Failures in the first profiler skip later variants through shared cleanup.

Test signals: skeleton load, attach status, test-run syscall status, and retval validation for each profiler variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_profiler.c -->
