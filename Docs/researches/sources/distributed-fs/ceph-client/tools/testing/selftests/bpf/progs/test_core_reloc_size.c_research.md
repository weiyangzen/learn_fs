<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_size.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_size.c

Purpose: CO-RE field/type size relocation test.

Important APIs/types/functions: Defines output and input structs plus handler `test_core_size`.

Control flow: Program uses size relocations to record field/type sizes and compare expected layout.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on CO-RE size relocation builtins.

Risks: Wrong size values break portable allocation/copy logic.

Test signals: Tests inspect recorded sizes across target flavors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_size.c -->
