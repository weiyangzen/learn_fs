<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_read_macros.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_read_macros.c

Purpose: Tests `BPF_CORE_READ` macro forms with shuffled local struct layouts.

Important APIs/types/functions: Defines local `callback_head` variants and raw tracepoint `handler`.

Control flow: Handler uses macro variants to read nested fields from CO-RE-relocated structures.

State and persistence: Persistent state is output globals.

Dependencies and integration: Depends on `bpf_core_read` macros and BTF field relocations.

Risks: Macro expansion must preserve relocation chains and bounds.

Test signals: Tests verify read values match expected fields despite layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_read_macros.c -->
