<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_args.c

Purpose: Negative test around struct_ops refcounted callback with many arguments and a tail-call map present.

Important APIs/types/functions: Defines `prog_array`, a `test_refcounted_multi` callback annotated for expected verifier failure, and a linked map.

Control flow: The callback path is crafted to expose verifier restrictions for multi-argument referenced kptr handling.

State and persistence: No successful runtime state is intended.

Dependencies and integration: Depends on bpf_testmod refcounted multi-argument op, prog-array map, and failure annotations.

Risks: Verifier must not lose reference ownership across argument slots or helper/tail-call possibilities.

Test signals: Pass signal is expected verifier rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/struct_ops_multi_args.c -->
