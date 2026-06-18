<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mem_rdonly_untrusted.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mem_rdonly_untrusted.c

Purpose: runs verifier/runtime coverage for read-only untrusted memory handling.

Important APIs and functions: the wrapper delegates to `RUN_TESTS(mem_rdonly_untrusted)` through the generated skeleton.

Control flow: top-level macro loads the fixture and executes each declared test program.

State and persistence: no explicit userspace state; verifier and BPF-side fixture state are transient.

Dependencies and integration: depends on `mem_rdonly_untrusted.skel.h` and the BPF selftest harness.

Risks and test signals: signals are skeleton subtest results. Risks are verifier type-name or access-rule changes for `rdonly_untrusted_mem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mem_rdonly_untrusted.c -->
