<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sockmap.c

Purpose: MPTCP sockmap test that injects accepted sockets into a sockmap and redirects stream verdict traffic. The file has 44 source lines and 943 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `sockops:mptcp_sockmap_inject, sk_skb/stream_verdict:mptcp_sockmap_redirect`. Local functions/subprograms: `mptcp_sockmap_inject, mptcp_sockmap_redirect`. Maps: `sock_map`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_sk_redirect_map, bpf_sock_map_update`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `sockops:mptcp_sockmap_inject, sk_skb/stream_verdict:mptcp_sockmap_redirect`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `sock_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; MPTCP kernel types and socket helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of sockops:mptcp_sockmap_inject, sk_skb/stream_verdict:mptcp_sockmap_redirect; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sockmap.c -->
