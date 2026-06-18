<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ptr_as_arr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ptr_as_arr.c

Purpose: CO-RE test treating pointer fields as arrays for relocation reads.

Important APIs/types/functions: Defines pointer-as-array struct and handler `test_core_ptr_as_arr`.

Control flow: Program reads indexed data through a pointer-like field using CO-RE access.

State and persistence: State is output globals.

Dependencies and integration: Depends on verifier-safe pointer/array CO-RE handling.

Risks: Bounds and pointer-to-array compatibility are risks.

Test signals: Tests validate indexed values or expected relocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_ptr_as_arr.c -->
