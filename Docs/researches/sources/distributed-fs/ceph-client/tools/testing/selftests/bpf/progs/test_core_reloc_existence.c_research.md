<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_existence.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_existence.c

Purpose: CO-RE field/type existence relocation test.

Important APIs/types/functions: Defines input/output structs and raw tracepoint `test_core_existence`.

Control flow: Program checks field/type existence and writes booleans/results.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on CO-RE existence relocation builtins.

Risks: False positives for missing fields or false negatives for present fields break portability.

Test signals: Tests run against flavor structs and compare existence flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_existence.c -->
