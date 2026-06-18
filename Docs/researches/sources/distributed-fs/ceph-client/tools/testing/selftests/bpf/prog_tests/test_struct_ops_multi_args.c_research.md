<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_args.c

Purpose: registers the generated struct_ops multi-argument callback selftest with the harness.

Important APIs/types/functions: includes `struct_ops_multi_args.skel.h` and calls `RUN_TESTS(struct_ops_multi_args)`.

Control flow: all open/load/attach/run expectations are delegated to the generated skeleton test macro.

State and persistence: none in this wrapper.

Dependencies and integration: depends on generated skeleton and struct_ops support for callbacks with multiple arguments. Integrated as `test_struct_ops_multi_args`.

Risks: the wrapper provides no local diagnostics beyond the generated test macro; behavioral details must be read from the paired BPF source.

Test signals: `RUN_TESTS` result for the skeleton.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_args.c -->
