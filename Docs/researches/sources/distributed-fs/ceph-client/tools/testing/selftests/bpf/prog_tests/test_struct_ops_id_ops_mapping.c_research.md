<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_id_ops_mapping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_id_ops_mapping.c

Purpose: verifies mapping from struct_ops map ids to the correct operations implementation across two independently loaded skeletons.

Important APIs/types/functions: generated `struct_ops_id_ops_mapping1` and `struct_ops_id_ops_mapping2`, `bpf_map_get_info_by_fd()`, `bpf_prog_test_run_opts()`, and BSS fields `st_ops_id`, `test_pid`, and `test_err`.

Control flow: load both skeletons, query each struct_ops map id, store each id in its own BSS, attach both skeletons, trigger tracing programs through `sys_gettid()`, run each syscall program directly, then require both `test_err` fields to be zero.

State and persistence: transient map ids and BSS pid/error fields. Skeleton destruction releases links and maps.

Dependencies and integration: depends on struct_ops map id reporting and generated skeletons. Integrated as `test_struct_ops_id_ops_mapping`.

Risks: assumes map info ids are stable while skeletons are alive and that simultaneous attachments do not interfere. Failures could indicate wrong id-to-ops lookup or cross-object confusion.

Test signals: map info query success, attach success for both objects, syscall test-run success, and zero error fields in both skeletons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_id_ops_mapping.c -->
