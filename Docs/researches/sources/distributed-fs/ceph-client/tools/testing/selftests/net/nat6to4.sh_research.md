## sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.sh

Purpose: minimal smoke test that loads `nat6to4.bpf.o` into a namespace loopback ingress hook and sends a UDP multicast datagram to exercise the IPv4-to-IPv6 egress section path.

Important APIs and tools: uses `ip netns`, loopback route setup, `tc qdisc add dev lo ingress`, `tc filter add ... bpf object-file ... section schedcls/egress4/snat4 direct-action`, and `socat` for UDP4 datagram generation.

Control flow: creates a temporary namespace, brings loopback up, adds a default route via loopback, attaches the BPF object to loopback ingress with protocol `ip`, then executes a `socat` UDP4 datagram send inside the namespace. There is no explicit cleanup trap in the file, so namespace cleanup is left to the caller or broader selftest environment.

State and persistence: creates a net namespace and attaches a TC qdisc/filter; those are persistent until namespace deletion. Dependencies are compiled `nat6to4.bpf.o`, `tc`, `ip`, `socat`, BPF syscall support, and privileges. Risks include namespace leak on failure, no assertion beyond command exit, and dependence on multicast loopback behavior. Test signal is command success or failure from `tc`/`socat`.
