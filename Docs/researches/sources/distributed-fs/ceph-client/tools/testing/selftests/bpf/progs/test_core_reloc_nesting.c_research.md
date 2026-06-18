<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_nesting.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_nesting.c

Purpose: CO-RE relocation test for nested structs and unions.

Important APIs/types/functions: Defines nested substruct/subunion and handler `test_core_nesting`.

Control flow: Program reads nested fields through multiple levels of struct/union nesting.

State and persistence: State is output globals.

Dependencies and integration: Depends on nested field path relocations.

Risks: Union member offsets and missing nested fields are risks.

Test signals: Tests compare nested output values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_nesting.c -->
