# sources/distributed-fs/ceph-client/samples/bpf/sockex2_kern.c

Purpose: socket filter BPF program that parses packets into flow keys and counts packets/bytes per flow.

Important APIs/types/functions: `struct flow_key_record`, VLAN/GRE helpers, `proto_ports_offset`, `ip_is_fragment`, `ipv6_addr_hash`, `parse_ip`, `parse_ipv6`, `flow_dissector`, `struct pair`, and `SEC("socket2") int bpf_prog2`.

Control flow: dissector parses Ethernet/VLAN, IPv4/IPv6, tunnels/fragments where supported, extracts protocol/addresses/ports into a flow key, and the main program increments a hash map value containing packet and byte counts.

State and persistence: flow counter hash map persists while attached.

Dependencies and integration: loaded by `sockex2_user.c`; uses BPF skb load helpers and network protocol headers.

Risks: parser supports a sample subset and hashes IPv6 addresses rather than storing full addresses. Header parsing must satisfy verifier bounds. Encapsulation support is limited.

Test signals: attach to traffic interface and observe map entries for flows with packet/byte counts.
