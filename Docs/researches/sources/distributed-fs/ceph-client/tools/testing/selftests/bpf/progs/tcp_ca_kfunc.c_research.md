<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c

Purpose: Tests BPF TCP congestion-control struct_ops callbacks and allowed TCP CA kfunc access.

Important APIs/types/functions: Defines many `struct_ops` callbacks for a `tcp_congestion_ops` map.

Control flow: Callbacks call or validate TCP congestion-control helper/kfunc behavior across init, cong_avoid, ssthresh, undo, state, cwnd event, and related hooks.

State and persistence: Persistent state is TCP CA registration and globals updated by callbacks.

Dependencies and integration: Depends on TCP stack struct_ops, kfuncs, and BTF `sock`/`tcp_sock` types.

Risks: Wrong callback prototypes or unsafe socket field access are key risks.

Test signals: Tests register the CA, drive TCP traffic, and inspect callback results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c -->
