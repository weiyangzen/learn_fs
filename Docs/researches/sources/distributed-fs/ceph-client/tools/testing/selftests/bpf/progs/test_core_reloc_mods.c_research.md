<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_mods.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_mods.c

Purpose: CO-RE relocation test for const/volatile/restrict and typedef modifier chains.

Important APIs/types/functions: Defines output structs, substructs, modified fields, and `test_core_mods`.

Control flow: Handler reads through modifier-wrapped types and records values.

State and persistence: Persistent state is output data.

Dependencies and integration: Depends on BTF modifier stripping/preservation during relocation.

Risks: Incorrect modifier handling can fail type compatibility.

Test signals: Tests validate relocated reads across modifier variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_mods.c -->
