<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_kern.c

## Purpose
`xdp_fwd_kern.c` implements an XDP forwarding sample using `bpf_fib_lookup()` and a devmap of allowed egress ports.

## Important APIs, Types, And Functions
The `xdp_tx_ports` `BPF_MAP_TYPE_DEVMAP` map stores egress ifindexes. Helpers are `ip_decrease_ttl()` and `xdp_fwd_flags()`. Entry programs are `xdp_fwd_prog()` and `xdp_fwd_direct_prog()`.

## Control Flow
The program parses Ethernet, IPv4, and IPv6 headers, skips packets with TTL/hop-limit <= 1, fills `struct bpf_fib_lookup`, and calls `bpf_fib_lookup()` with normal or direct flags. On success, it verifies the returned egress ifindex is present in the devmap, decrements TTL/hop-limit, rewrites Ethernet source/destination MACs from FIB results, and redirects through the devmap. Other cases pass or drop malformed packets.

## State And Persistence
Persistent state is the devmap populated by userspace with interfaces eligible for XDP transmit. Packet header updates are transient.

## Dependencies And Integration Points
It depends on XDP, devmap lookup and redirect, kernel FIB/neighbour tables, forwarding sysctls, and the userspace loader.

## Risks And Edge Cases
Packets are passed to the stack when neighbor resolution is missing, forwarding disabled, or egress is not configured. VLAN parsing is not included. Direct lookup skips fib rules. Not all egress devices support XDP xmit, causing drops after redirect.

## Test Signals
Valid routed IPv4/IPv6 packets should be redirected with updated MACs and decremented TTL/hop-limit when the egress ifindex is in `xdp_tx_ports`; missing neighbours should show `XDP_PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_kern.c -->
