# sources/distributed-fs/ceph-client/net/sched/act_csum.c

Purpose: implements the `csum` TC action, recalculating selected packet checksums after earlier actions edit packet headers or payload.

Important APIs/functions: `tcf_csum_act()` is the action body. Init/dump/cleanup functions manage `struct tcf_csum_params` containing `update_flags` and action opcode. Protocol helpers update IPv4 header, ICMP/IGMP, IPv4/IPv6 TCP, UDP, UDPLite, ICMPv6, and SCTP checksums; `tcf_csum_skb_nextlayer()` validates pull/writability for next-layer headers. `tcf_csum_offload_act_setup()` maps to `FLOW_ACTION_CSUM`.

Control flow: init parses `TCA_CSUM_PARMS`, allocates or replaces the action, checks control action, and RCU-swaps params. Runtime updates stats, honors immediate `TC_ACT_SHOT`, resolves the packet protocol including stacked VLAN headers, calls IPv4 or IPv6 checksum handlers based on `update_flags`, restores any pulled VLAN headers, and drops on validation or writability failure. IPv6 handling walks hop/routing/destination headers, detects jumbo hop options, and ignores fragments or unsupported next headers.

State and persistence: action parameters are RCU-managed and per-action; packet state is mutated in headers and `skb->ip_summed`/checksum fields. No external persistent state is created.

Dependencies and integration: uses TC action API, skbuff pull/write helpers, IP/IPv6/TCP/UDP/SCTP checksum helpers, VLAN handling, and flow offload action translation.

Risks: checksum correctness depends on packet linearization, header offsets, VLAN restoration, and GSO exceptions. Some malformed UDP/UDPLite length cases are treated as "ignore obscure skb" rather than drop after partial preparation. Fragmented IPv4 and IPv6 packets are intentionally not deep-recalculated. Any packet dropped by this action increments qstats.

Test signals: packet-edit plus csum pipelines for IPv4/IPv6 TCP/UDP/UDPLite/ICMP/SCTP, VLAN and QinQ encapsulation, GSO packets, malformed/truncated headers, jumbo IPv6 hop option handling, offload translation, and drop-stat assertions.
