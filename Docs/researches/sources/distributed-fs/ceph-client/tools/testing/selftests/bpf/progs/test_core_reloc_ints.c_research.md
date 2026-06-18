<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ints.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ints.c

Purpose: CO-RE primitive integer relocation test.

Important APIs/types/functions: Defines integer layout struct and raw tracepoint `test_core_ints`.

Control flow: Program reads integer fields with varied widths/signedness.

State and persistence: State is output globals.

Dependencies and integration: Depends on integer field CO-RE relocations.

Risks: Width/sign mismatches are the risk.

Test signals: Tests compare stored integer values across target layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ints.c -->
