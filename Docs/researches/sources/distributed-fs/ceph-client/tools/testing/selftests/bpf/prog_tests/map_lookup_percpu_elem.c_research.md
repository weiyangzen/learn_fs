<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lookup_percpu_elem.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lookup_percpu_elem.c

Purpose: runs skeleton tests for per-CPU element lookup helper behavior.

Important APIs and functions: `test_map_lookup_percpu_elem()` delegates to `RUN_TESTS(test_map_lookup_percpu_elem)`, which loads and runs subtests from the generated skeleton.

Control flow: harness macro manages skeleton load/run and assertion propagation.

State and persistence: per-CPU map state is owned by the BPF fixture and destroyed by the macro.

Dependencies and integration: depends on `test_map_lookup_percpu_elem.skel.h` and selftest macro support.

Risks and test signals: subtest pass/fail is driven by BPF-side assertions and verifier/runtime behavior. The wrapper risk is minimal; fixture/kernel helper semantics are the main risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lookup_percpu_elem.c -->
