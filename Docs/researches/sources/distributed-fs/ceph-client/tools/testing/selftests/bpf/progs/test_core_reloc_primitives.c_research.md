<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_primitives.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_primitives.c

Purpose: CO-RE primitive type relocation test including enum and scalar primitives.

Important APIs/types/functions: Defines primitive enum/struct and handler `test_core_primitives`.

Control flow: Program checks primitive type sizes/compatibility and reads scalar fields.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on primitive BTF type relocations.

Risks: Primitive signedness/size compatibility can vary by target.

Test signals: Tests validate values and type checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_primitives.c -->
