<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_refcounted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_refcounted.c

Purpose: dispatches struct_ops refcounted-object verifier coverage, including valid handling and expected failures for reference leaks, global subprogram use, and tail-call use.

Important APIs/types/functions: `RUN_TESTS()` over `struct_ops_refcounted` and three failure skeletons.

Control flow: sequentially runs generated skeleton tests; expected accept/reject behavior is encoded in those skeletons/BPF programs.

State and persistence: none in wrapper.

Dependencies and integration: depends on generated skeletons and kernel verifier support for refcounted kptr semantics in struct_ops. Integrated as `test_struct_ops_refcounted`.

Risks: wrapper has no additional environment setup; all detail is in paired BPF sources. Missing negative coverage would surface as unexpected `RUN_TESTS` failure.

Test signals: generated tests for successful load and rejected invalid refcount patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_refcounted.c -->
