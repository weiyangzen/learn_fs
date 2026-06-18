# sources/distributed-fs/ceph-client/net/netfilter/xt_HMARK.c

Purpose: `HMARK` target computes a deterministic hash from packet or conntrack tuple fields and stores it in `skb->mark`.

Important APIs/types/functions: `struct hmark_tuple`, `hmark_ct_set_htuple()`, `hmark_pkt_set_htuple_ipv4()`, IPv6 tuple builder, `hmark_swap_ports()`, `hmark_hash()`, and `hmark_tg_check()`.

Control flow: runtime builds tuple from conntrack or packet headers, handles ICMP/ICMPv6 inner headers and fragments, normalizes address/port ordering, hashes with jhash plus proto mask, scales by modulus, adds offset, and writes skb mark.

State and persistence: no module state; skb mark persists downstream. Dependencies include optional conntrack, IPv4/IPv6 parsing, jhash, reciprocal scaling, and ICMP parsing. Risks: no conntrack or parse failure leaves packet unchanged, fragments skip ports, endian-stable hash must remain stable, and incompatible SPI/port flags are rejected. Test signals: packet and conntrack modes, IPv4/IPv6, ICMP errors, fragments, L3-only mode, modulus zero, and invalid flag combinations.
