<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf6.c

Purpose: BPF-to-BPF tail-call variant that checks classifier-to-subprogram transfer ordering.

Important APIs/types/functions: Defines `classifier_0`, `subprog_tail`, `entry`, and prog-array map.

Control flow: Entry invokes a subprogram or classifier path that attempts a static tail call and returns fallback on miss.

State and persistence: Prog-array is the durable state.

Dependencies and integration: Depends on static tail calls through subprogram call graph.

Risks: Misordered patching or context loss can change return values.

Test signals: Harness return-code checks validate the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf6.c -->
