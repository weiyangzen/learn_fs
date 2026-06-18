<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy1.c

Purpose: Tests hierarchical BPF-to-BPF tail-call setup with static prog-array initialization.

Important APIs/types/functions: Defines `jmp_table`, `subprog_tail`, and tc entry.

Control flow: Entry calls a subprogram that tail-calls through the initialized prog-array hierarchy.

State and persistence: Prog-array values embedded in the map definition persist after load.

Dependencies and integration: Depends on libbpf map-initializer support for prog arrays and tc tail calls.

Risks: Initializer order and subprogram target resolution are the risks.

Test signals: Expected retval/counter checks validate hierarchy setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy1.c -->
