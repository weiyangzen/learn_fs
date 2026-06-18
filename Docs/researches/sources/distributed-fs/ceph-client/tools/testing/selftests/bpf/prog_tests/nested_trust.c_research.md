<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/nested_trust.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/nested_trust.c

Purpose: verifies verifier trust propagation for nested pointer acquisition/access scenarios.

Important APIs and functions: `test_nested_trust()` runs `RUN_TESTS(nested_trust_failure)`, `RUN_TESTS(nested_trust_success)`, and `RUN_TESTS(nested_acquire)` through generated skeletons.

Control flow: failure, success, and acquire suites are executed in order, letting the harness validate load failures and successful program behavior.

State and persistence: no explicit userspace state; skeletons and verifier state are transient.

Dependencies and integration: depends on `nested_trust_failure.skel.h`, `nested_trust_success.skel.h`, `nested_acquire.skel.h`, and verifier trust semantics.

Risks and test signals: expected load failures/successes are signals. Risks are verifier diagnostic or trust-propagation rule changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/nested_trust.c -->
