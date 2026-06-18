<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_global_funcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_global_funcs.c

Purpose: exercises global BPF function verification across many generated skeletons and verifies libbpf rewriting of `__arg_ctx`-annotated global-function arguments on kernels without native argument-context metadata.

Important APIs/types/functions: `RUN_TESTS(test_global_func*)` dispatches generated positive/negative skeleton tests. `subtest_ctx_arg_rewrite()` uses `btf__load_vmlinux_btf()`, `btf__find_by_name_kind()`, `bpf_prog_get_info_by_fd()`, `btf__load_from_kernel_by_id()`, and `check_ctx_arg_type()`.

Control flow: run the numbered global-function skeleton suites, then optionally run `ctx_arg_rewrite`. The rewrite subtest skips on kernels with native `bpf_subprog_arg_info`, enables only `arg_tag_ctx_perf`, loads the skeleton, retrieves function-info records, loads the program BTF by id, and validates that subprogram arguments tagged as context were rewritten to pointers to `struct bpf_perf_event_data`.

State and persistence: no durable state. It allocates kernel and program BTF handles and frees them. It reads program metadata from the loaded BPF object.

Dependencies and integration: depends on generated `test_global_func*.skel.h`, `test_global_func_ctx_args.skel.h`, libbpf internal helpers, BTF helpers, and kernel BTF availability. Integrated through `test_test_global_funcs`.

Risks: the ctx rewrite subtest intentionally skips once the kernel exposes native argument metadata, so coverage shifts with kernel capability. It assumes three function-info records and exact subprogram names. BTF dump string matching can be brittle if formatting changes.

Test signals: generated suites report through `RUN_TESTS`; rewrite checks kernel BTF load, skeleton load, program info count, BTF kinds, subprogram names, argument count, and context struct type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_global_funcs.c -->
