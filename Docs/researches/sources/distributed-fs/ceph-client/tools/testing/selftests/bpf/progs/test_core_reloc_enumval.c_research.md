<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enumval.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enumval.c

Purpose: CO-RE test for regular enum value relocations.

Important APIs/types/functions: Defines named and anonymous enums, output struct, and raw tracepoint `test_core_enumval`.

Control flow: Program uses CO-RE enum value existence/value relocations and records results.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on BTF enum relocation support.

Risks: Renamed/missing enum values must resolve according to CO-RE rules.

Test signals: Tests inspect expected enum value/existence outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enumval.c -->
