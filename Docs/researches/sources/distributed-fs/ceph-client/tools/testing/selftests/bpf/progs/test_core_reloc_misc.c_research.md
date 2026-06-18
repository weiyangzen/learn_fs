<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_misc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_misc.c

Purpose: Miscellaneous CO-RE relocation cases for extensible structs and compatible variants.

Important APIs/types/functions: Defines output struct, variants `core_reloc_misc___a/b`, extensible struct, and handler `test_core_misc`.

Control flow: Program reads fields and checks compatibility/existence across miscellaneous layout cases.

State and persistence: State is output globals.

Dependencies and integration: Depends on libbpf CO-RE matching for extensible and flavored types.

Risks: Edge-case matching rules can regress without obvious compile failures.

Test signals: Tests compare output flags/values for each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_misc.c -->
