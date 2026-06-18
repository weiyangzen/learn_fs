# sources/distributed-fs/ceph-client/net/ipv4/af_inet.c

## Purpose
`af_inet.c` is the PF_INET socket-family core for IPv4. It creates INET sockets, maps socket type/protocol pairs to protocol implementations, implements common socket operations, registers base IPv4 protocols, installs packet/offload handlers, and initializes per-network-namespace IPv4 defaults and statistics.

## Important APIs, types, and functions
Important exports include `inet_sock_destruct()`, `inet_listen()`, `inet_release()`, `inet_bind()`, `__inet_bind()`, `inet_dgram_connect()`, `__inet_stream_connect()`, `inet_stream_connect()`, `__inet_accept()`, `inet_accept()`, `inet_getname()`, `inet_send_prepare()`, `inet_sendmsg()`, `inet_splice_eof()`, `inet_recvmsg()`, `inet_shutdown()`, `inet_ioctl()`, `inet_stream_ops`, `inet_dgram_ops`, `inet_register_protosw()`, `inet_unregister_protosw()`, `inet_sk_rebuild_header()`, `inet_sk_set_state()`, `inet_gso_segment()`, `inet_gro_receive()`, `inet_current_timestamp()`, `inet_recv_error()`, `inet_gro_complete()`, `inet_ctl_sock_create()`, and SNMP fold helpers. Internal registries include `inetsw[]`, `inetsw_array[]`, `inet_family_ops`, `ip_packet_type`, and `ipip_offload`.

## Control flow
`inet_create()` looks up the requested socket type/protocol in `inetsw`, tries module autoload on misses, checks raw-socket capability, allocates the protocol socket, initializes default IPv4 fields, hashes protocol-number sockets, runs protocol init, and invokes cgroup BPF socket hooks. Bind and connect paths apply cgroup BPF hooks, address validity checks, privileged-port checks, port allocation, route lookup, autobind, nonblocking stream-connect waits, and disconnect semantics. Send/receive wrappers perform autobind/RPS bookkeeping and indirectly call TCP or UDP fast paths. `inet_init()` registers TCP/UDP/raw/ping protos, registers PF_INET, installs base `net_protocol` handlers for ICMP/UDP/TCP/IGMP, populates `inetsw`, initializes ARP/IP/TCP/UDP/raw/ping/ICMP/mroute/pernet/proc/fragmentation/tunnel subsystems, and adds the IPv4 packet handler. `ipv4_offload_init()` separately registers GSO/GRO offloads.

## State and persistence
Global state includes the `inetsw` protocol-switch lists and packet/offload registrations. Per-socket state lives in `struct inet_sock`, route caches, socket state, multicast membership, IP options, and cgroup/BPF-controlled settings. Per-net state includes IPv4 sysctl defaults, local port ranges, ping group ranges, and per-cpu MIB allocations. All state is runtime kernel state, not durable storage.

## Dependencies and integration points
The file integrates with TCP, UDP, raw, ping, ICMP, ARP, FIB/routing, IP input, fragmentation, multicast, procfs, sysctl, XFRM, BPF cgroup hooks, MPTCP stats, GRO/GSO offload, packet handlers, net namespaces, l3mdev, netfilter includes, and PSP socket association cleanup. User-visible integration is the AF_INET socket API and legacy ioctls for routes, ARP, and interface IPv4 addresses.

## Risks and invariants
The `inetsw` list ordering prevents non-permanent protocols from overriding permanent core protocols; registration changes must preserve this. Socket state transitions in stream connect, shutdown, and accept have subtle blocking and race semantics. `inet_sock_destruct()` warns on alive or non-closed stream sockets and must free IP options and dst references exactly once. Initialization order is critical: base protocols and packet handlers depend on prior proto and subsystem registration. GSO/GRO code assumes validated IPv4 headers without options for aggregation and must update IDs, lengths, checksums, and encapsulation headers correctly.

## Test signals
Signals include IPv4 TCP/UDP/raw/ping socket creation and module autoload behavior, raw capability failures, bind to local/nonlocal/multicast/broadcast addresses, cgroup BPF bind/connect hooks, blocking and nonblocking TCP connect including Fast Open, route/ARP/interface ioctls, protocol registration/unregistration for modules, network namespace creation defaults, `/proc/net` IPv4 entries, SNMP counters, packet receive through `ip_rcv`, and GSO/GRO segmentation/completion for TCP/UDP/IPIP.
