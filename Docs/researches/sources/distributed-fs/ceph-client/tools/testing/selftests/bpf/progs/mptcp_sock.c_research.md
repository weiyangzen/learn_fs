<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sock.c

Purpose: MPTCP socket-storage and sockops/fentry test for MPTCP/TCP socket BTF conversions. The file has 89 source lines and 1894 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `sockops:_sockops, fentry/mptcp_pm_new_connection:BPF_PROG`. Local functions/subprograms: `_sockops, BPF_PROG`. Maps: `socket_storage_map`. Types: `mptcp_storage`. BPF helpers/kfuncs/macros used as calls: `bpf_core_field_exists, bpf_sk_storage_get, bpf_skc_to_mptcp_sock, bpf_skc_to_tcp_sock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `sockops:_sockops, fentry/mptcp_pm_new_connection:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `socket_storage_map` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; MPTCP kernel types and socket helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of sockops:_sockops, fentry/mptcp_pm_new_connection:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sock.c -->
