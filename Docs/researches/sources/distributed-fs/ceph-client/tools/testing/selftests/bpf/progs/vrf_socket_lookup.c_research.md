<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/vrf_socket_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/vrf_socket_lookup.c

## Purpose
This functional BPF program tests socket lookup helpers from both tc and XDP contexts, including behavior under VRF/current-netns lookup and the choice between `bpf_sk_lookup_tcp` and `bpf_skc_lookup_tcp`.

## Important APIs, Types, and Functions
Globals `lookup_status`, `test_xdp`, and `tcp_skc` are controlled by userspace tests. `socket_lookup()` parses Ethernet and IPv4 headers, builds a `struct bpf_sock_tuple` view over IP addresses/ports, and calls `bpf_sk_lookup_tcp`, `bpf_skc_lookup_tcp`, or `bpf_sk_lookup_udp` with `BPF_F_CURRENT_NETNS`. Entry points are `tc_socket_lookup` and `xdp_socket_lookup`.

## Control Flow
Both entry points extract packet data pointers and gate execution on `test_xdp`. The shared parser validates Ethernet, IPv4, tuple bounds, and protocol. For TCP it chooses SKC or full socket lookup based on `tcp_skc`; for UDP it uses UDP lookup. It clears `lookup_status` before lookup and sets it to 1 only if a socket is found and released.

## State and Persistence
Persistent BSS globals expose test controls and outcome. Socket references returned by lookup helpers are released immediately with `bpf_sk_release`.

## Dependencies and Integration Points
The program integrates with network selftests that attach it at tc or XDP and then inspect global data. It depends on packet header definitions, endian helpers, and socket lookup helper availability.

## Risks
The tuple is formed by casting `&iph->saddr`, so layout assumptions must match IPv4 tuple layout. Missing release would leak references, but current code releases all non-null lookups.

## Test Signals
Userspace can toggle `test_xdp` and `tcp_skc`, send TCP/UDP IPv4 traffic, and observe `lookup_status` to confirm helper behavior in the selected hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/vrf_socket_lookup.c -->
