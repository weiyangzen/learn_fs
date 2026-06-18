<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_kern.c

## Purpose
`xdp_tx_iptunnel_kern.c` demonstrates using `bpf_xdp_adjust_head()` to encapsulate selected IPv4 or IPv6 packets in a new outer IP header and transmit them back with `XDP_TX`.

## Important APIs, Types, And Functions
Maps are `rxcnt` per-protocol counters and `vip2tnl` hash from `struct vip` to `struct iptnl_info`. Helpers include `count_tx()`, `get_dport()`, `set_ethhdr()`, `handle_ipv4()`, and `handle_ipv6()`. Entry point `_xdp_tx_iptunnel()` is in section `xdp.frags`.

## Control Flow
The entry parses Ethernet and dispatches IPv4 or IPv6. Each handler reads the transport destination port for TCP/UDP, builds a VIP key from destination/protocol/family/port, looks up tunnel info, and passes unmatched traffic. On match, it grows packet head by an IPv4 or IPv6 header, rewrites Ethernet addresses, fills outer tunnel header fields, increments protocol counters, and returns `XDP_TX`.

## State And Persistence
`vip2tnl` holds configured encapsulation policies; `rxcnt` accumulates per-protocol transmitted packet counts. Packet modifications are transient.

## Dependencies And Integration Points
It depends on XDP head adjustment, XDP fragments section support, IP header definitions, and the userspace loader that populates `vip2tnl`.

## Risks And Edge Cases
It only performs v4-in-v4 and v6-in-v6, not cross-family tunneling. Header construction assumes enough headroom after adjustment and simple TCP/UDP/other transport parsing. Outer IPv4 checksum is manually computed and must remain correct.

## Test Signals
Packets matching configured VIP entries should be encapsulated and counted under their protocol in `rxcnt`; unmatched traffic should pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_kern.c -->
