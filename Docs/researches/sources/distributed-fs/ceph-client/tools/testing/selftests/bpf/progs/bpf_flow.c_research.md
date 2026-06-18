<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_flow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_flow.c

## Purpose

BPF flow dissector selftest that parses Ethernet, IPv4, IPv6, GRE, VLAN, MPLS, TCP, UDP, and fragmentation paths through tail calls.

## Important APIs, Types, and Functions

- BPF sections: `flow_dissector`, `.maps`, `.maps`, `flow_dissector`, `license`
- Maps: `jmp_table`, `last_dissection`
- Important functions/callbacks: `export_flow_keys`, `parse_eth_proto`, `_dissect`, `parse_ip_proto`, `parse_ipv6_proto`
- BPF helpers/kfunc-like calls: `bpf_flow_dissect_get_header`, `bpf_htonl`, `bpf_htons`, `bpf_map_update_elem`, `bpf_skb_load_bytes`, `bpf_tail_call_static`

## Control Flow and Data Flow

The root flow dissector dispatches by ethertype through a prog-array tail-call table. Parser stages advance `thoff`, handle encapsulation/fragmentation, fill `struct bpf_flow_keys`, export the last dissection to a hash map, and return OK, DROP, or CONTINUE.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `jmp_table`, `last_dissection`

## Dependencies and Integration Points

Includes `limits.h`, `stddef.h`, `stdbool.h`, `string.h`, `linux/pkt_cls.h`, `linux/bpf.h`, `linux/in.h`, `linux/if_ether.h`, `linux/icmp.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/tcp.h`, and 7 more.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_flow_dissect_get_header`, `bpf_htonl`, `bpf_htons`, `bpf_map_update_elem`, `bpf_skb_load_bytes`, `bpf_tail_call_static`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `jmp_table`, `last_dissection` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_flow.c -->
