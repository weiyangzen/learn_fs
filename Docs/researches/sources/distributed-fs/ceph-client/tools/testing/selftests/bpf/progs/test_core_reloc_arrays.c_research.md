<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_arrays.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_arrays.c

Purpose: CO-RE relocation test for arrays and nested array fields.

Important APIs/types/functions: Defines input/output structs and raw tracepoint `test_core_arrays`.

Control flow: Program reads array elements and nested substructure arrays through CO-RE relocations.

State and persistence: Persistent state is output map/global data.

Dependencies and integration: Depends on array field relocations in BTF.

Risks: Array bounds and element-size relocation mistakes are risks.

Test signals: Tests compare output values for matching, resized, and missing arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_arrays.c -->
