<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_probed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_probed.c

Purpose: CO-RE bitfield relocation test using probed/raw tracepoint reads.

Important APIs/types/functions: Defines bitfield structs and `test_core_bitfields`.

Control flow: Handler reads bitfields through probe-read style CO-RE helpers.

State and persistence: Persistent state is output data.

Dependencies and integration: Depends on BPF_CORE_READ_BITFIELD_PROBED-style relocations.

Risks: Sign/width handling and safe probing are risks.

Test signals: Tests compare expected decoded bitfield outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_bitfields_probed.c -->
