<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_multi_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_multi_kern.c

## Purpose
This program tests multi-target XDP redirect behavior with devmap and devmap-hash, protocol-specific redirect flags, and second-stage devmap programs.

## Important APIs, Types, and Functions
Maps include `map_all` devmap, `map_egress` devmap-hash, `mac_map`, and `redirect_flags`. Entry points are `xdp_redirect_map_multi_prog`, `xdp_redirect_map_all_prog`, and `xdp_devmap_prog`. It uses `bpf_redirect_map` and `bpf_map_lookup_elem`.

## Control Flow
The main XDP program validates Ethernet bounds, reads EtherType, optionally reads redirect flags by protocol, and redirects IPv4 with broadcast/exclude-ingress defaults, IPv6 to ingress ifindex with default flags 0, and other protocols with broadcast default. The second XDP program redirects all packets through the devmap-hash. The devmap program runs on egress, looks up MAC by egress ifindex, and overwrites Ethernet source MAC if present.

## State and Persistence
Userspace populates devmaps, MAC map, and flags map. The devmap egress program mutates packet Ethernet source address.

## Dependencies and Integration Points
The file integrates with XDP redirect multi selftests and kernel devmap/devmap-hash infrastructure. It depends on devmap program attachment for `SEC("xdp/devmap")`.

## Risks
The code uses `bpf_htons(eth->h_proto)` into a host-order-looking protocol variable; behavior is tied to test expectations and endian macros. Missing map entries fall back to default flags or no MAC rewrite.

## Test Signals
Packet fanout/exclusion, protocol-specific flag override, and source-MAC rewrite on devmap egress are observable through traffic and map state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_multi_kern.c -->
