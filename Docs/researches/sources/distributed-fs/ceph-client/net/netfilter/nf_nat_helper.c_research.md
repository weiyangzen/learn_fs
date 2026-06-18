
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_helper.c

Purpose: Provides generic NAT helper support for payload rewriting, TCP sequence adjustment, UDP length/checksum update, follow-master expectation NAT setup, and expectation port reservation.

Important APIs and functions: `__nf_nat_mangle_tcp_packet()` rewrites TCP payload spans and optionally records sequence adjustment. `nf_nat_mangle_udp_packet()` rewrites UDP payload spans and updates UDP length/checksum. `nf_nat_follow_master()` configures related conntracks to use the master flow's NAT mapping. `nf_nat_exp_find_port()` tries to register an expectation at a requested or random replacement port.

Control flow: Payload mangle first ensures the skb is writable and expandable, then `mangle_contents()` memmoves trailing data, inserts replacement bytes, adjusts skb length and IP/IPv6 total length, recalculates transport checksums, and optionally records seqadj. Follow-master sets source mapping to the master's opposite destination and destination mapping to the master's opposite source plus saved protocol port. Port finding repeatedly calls `nf_ct_expect_related()` until success or bounded attempts fail.

State and persistence: No local persistent state. It mutates skb contents and conntrack expectation/NAT/seqadj state.

Dependencies and integration: Used by protocol-specific helpers such as FTP, IRC, and Amanda. Depends on skb mutation APIs, conntrack helpers/expectations, NAT core, and seqadj extension support.

Risks: High-risk behavior includes packet expansion under GFP_ATOMIC, memmove bounds, IPv4/IPv6 length recalculation, checksum correctness after payload size changes, TCP sequence adjustment alignment, and expectation cleanup by callers. Tests should exercise larger/smaller/same-size replacements, no-tailroom expansion, IPv4/IPv6 TCP and UDP checksums, seqadj across subsequent packets, and port collision exhaustion.
