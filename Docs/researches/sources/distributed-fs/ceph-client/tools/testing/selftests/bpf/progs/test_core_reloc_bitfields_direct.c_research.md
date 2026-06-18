<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_direct.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_direct.c

Purpose: CO-RE bitfield relocation test using direct BTF-enabled context access.

Important APIs/types/functions: Defines bitfield input/output structs plus tracepoint BTF context types and `test_core_bitfields_direct`.

Control flow: Program reads signed/unsigned bitfields directly and stores normalized outputs.

State and persistence: State is output globals.

Dependencies and integration: Depends on direct bitfield CO-RE access and tp_btf context.

Risks: Bit offset, sign extension, and endian handling are risks.

Test signals: Tests validate all extracted bitfield values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_direct.c -->
