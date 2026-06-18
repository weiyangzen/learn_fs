<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf1.c

Purpose: Tests static tail calls issued from a BPF subprogram called by a tc entry program.

Important APIs/types/functions: Defines `subprog_tail`, `entry`, and `jmp_table`.

Control flow: `entry` calls `subprog_tail`; the subprogram attempts a static tail call and returns a fallback derived from skb state on miss.

State and persistence: Prog-array map is persistent test state.

Dependencies and integration: Depends on BPF-to-BPF calls plus static tail-call support.

Risks: Verifier/JIT must handle tail-call patching inside subprograms.

Test signals: Expected results distinguish successful target transfer from subprogram fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf1.c -->
