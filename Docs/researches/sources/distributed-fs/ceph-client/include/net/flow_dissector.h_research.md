# sources/distributed-fs/ceph-client/include/net/flow_dissector.h

Purpose: declares the packet flow-dissection key model used by classifiers, hashing, BPF flow dissectors, receive steering, and offload rules. It defines small typed key structs for control metadata, basic protocol ids, VLAN/CVLAN, MPLS, tunnel options, IPv4/IPv6/TIPC addresses, ARP, ports and ranges, ICMP, Ethernet addresses, TCP flags, IP TOS/TTL, ingress metadata, conntrack, hash, PPPoE, L2TPv3, IPsec, and CFM.

Important APIs/types: `enum flow_dissector_key_id` is the central key namespace. `struct flow_dissector` stores `used_keys` and per-key offsets into an arbitrary target container. `struct flow_keys` is the common hash-oriented container with basic, tags, VLAN, keyid, ports, ICMP, and final address union. `dissector_uses_key()` tests key availability; `skb_flow_dissector_target()` computes a typed target pointer from offsets. Hash/digest helpers include `flow_hash_from_keys()`, `flow_hash_from_keys_seed()`, `make_flow_keys_digest()`, `flow_get_u32_src()`, and `flow_get_u32_dst()`.

Control flow and state: callers configure a `flow_dissector` with offsets, run packet parsing elsewhere, and then read only keys whose bits are set. Inline helpers set MPLS-used bits, clear key-control/basic storage, and report whether L4 entropy is present via ports or IPv6 flow label. BPF attachment validation is exposed under `CONFIG_BPF_SYSCALL`.

Dependencies and integration: uses Linux fixed-width types, IPv6 addresses, siphash alignment, Ethernet and tc flower UAPI flags. It is consumed directly by `flow_offload.h`, classifiers, skb hashing, BPF, GRO/RPS paths, and tunnel-aware matching.

Risks: `used_keys` is a 64-bit bitset, so key count growth must preserve capacity. Offset/key-id mismatches corrupt output containers. Tunnel option length is capped at 255. Test signals include flower classifier matches for each key, first-fragment and encapsulation parsing flags, BPF attach checks, flow hash stability, and digest uniqueness under address/port changes.
