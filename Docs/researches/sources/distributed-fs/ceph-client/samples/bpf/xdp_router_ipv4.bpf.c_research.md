<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4.bpf.c

## Purpose
`xdp_router_ipv4.bpf.c` is an XDP IPv4 router sample. It combines exact-route, LPM route, ARP, devmap, and shared sample statistics maps to redirect IPv4 packets at XDP.

## Important APIs, Types, And Functions
Maps include `lpm_map`, `arp_table`, `exact_match`, and `tx_port`, plus shared `rx_cnt` from `xdp_sample.bpf.h`. `xdp_router_ipv4_prog()` handles packet parsing and redirect. Structures include `trie_value`, `union key_4`, `arp_entry`, and `direct_map`.

## Control Flow
The program increments receive stats, parses Ethernet and optional VLAN headers, passes ARP, and handles IPv4. It first checks `exact_match` for destination IP and cached MAC data. If absent, it builds a 32-bit LPM key, looks up the route prefix, finds the destination MAC by destination or gateway in `arp_table`, and passes to the stack if gateway ARP discovery is needed. With source and destination MACs resolved, it rewrites Ethernet addresses and redirects through `tx_port`.

## State And Persistence
Routing state persists in BPF maps populated by userspace from netlink route and neighbour tables. Statistics persist in shared sample maps until userspace collects them.

## Dependencies And Integration Points
It depends on XDP, BPF LPM trie maps, hash maps, devmap redirect, shared XDP sample stats infrastructure, and `xdp_router_ipv4_user.c`.

## Risks And Edge Cases
Only ARP and IPv4 are explicitly handled; other traffic drops by default after parsing. The LPM key builds bytes from network-order destination fields and must match userspace population. Missing ARP for a gateway passes packets to the kernel, while missing route drops them.

## Test Signals
Route/ARP maps populated from userspace should produce `XDP_REDIRECT` and increment redirect stats. Missing ARP should increment pass stats; malformed or unroutable packets should increment drop stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4.bpf.c -->
