<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_maybe_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_maybe_null.c

Purpose: validates verifier handling of nullable struct_ops pointer arguments: checked access is accepted and unchecked access is rejected.

Important APIs/types/functions: generated `struct_ops_maybe_null` and `struct_ops_maybe_null_fail` skeletons, `open_and_load()` helpers, `ASSERT_OK_PTR`, and `ASSERT_ERR_PTR`.

Control flow: subtest `maybe_null` loads the valid object and destroys it. Subtest `maybe_null_fail` attempts to load the invalid object and returns successfully only if load produces an error pointer.

State and persistence: none beyond transient skeleton handles.

Dependencies and integration: depends on struct_ops maybe-null verifier annotations and separate BPF objects to isolate load-time verification. Integrated as `test_struct_ops_maybe_null`.

Risks: does not attach or execute programs; all signal is verifier load behavior. If verifier diagnostics change but accept/reject remains stable, test still passes.

Test signals: load success for the checked program and load failure for unchecked nullable access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_maybe_null.c -->
