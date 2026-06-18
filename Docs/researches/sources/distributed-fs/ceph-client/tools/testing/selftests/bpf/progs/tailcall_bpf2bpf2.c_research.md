<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf2.c

Purpose: Adds a classifier target to the BPF-to-BPF tail-call pattern.

Important APIs/types/functions: Defines `subprog_tail`, `classifier_0`, `entry`, and `jmp_table`.

Control flow: Entry calls a subprogram that tail-calls index 0; classifier returns the target value.

State and persistence: State is prog-array contents.

Dependencies and integration: Depends on subprogram call graph and static tail-call relocation.

Risks: A wrong target or lost skb context across the call boundary is the risk.

Test signals: Tests populate index 0 and verify classifier return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf2.c -->
