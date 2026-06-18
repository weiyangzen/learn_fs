<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enum64val.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enum64val.c

Purpose: CO-RE test for 64-bit enum value relocations, signed and unsigned.

Important APIs/types/functions: Defines named 64-bit enum types, output struct, and raw tracepoint `test_core_enum64val`.

Control flow: Program relocates enum value constants and stores comparison/output results.

State and persistence: State is output globals.

Dependencies and integration: Depends on BTF enum64 support.

Risks: Older kernels/toolchains may lack enum64 BTF handling.

Test signals: Tests verify relocated 64-bit enum constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_enum64val.c -->
