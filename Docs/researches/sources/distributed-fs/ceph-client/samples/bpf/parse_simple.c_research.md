# sources/distributed-fs/ceph-client/samples/bpf/parse_simple.c

Purpose: minimal direct-packet-access parser for Ethernet/IPv4/UDP traffic.

Important APIs/types/functions: local `struct eth_hdr` and `SEC("simple") int handle_ingress(struct __sk_buff *skb)`.

Control flow: computes pointers to Ethernet, IP, and UDP headers from `skb->data`, checks `data_end` bounds, validates protocol fields, and returns a packet verdict based on UDP port matching.

State and persistence: stateless per packet.

Dependencies and integration: compiled as a BPF parser sample and used by BPF sample tests comparing direct access parsing styles.

Risks: assumes no VLAN and fixed IPv4 header length. Any missing bounds check would be rejected by verifier; current simplicity limits protocol coverage.

Test signals: verifier accepts direct packet access, and pktgen/default UDP traffic exercises the expected path.
