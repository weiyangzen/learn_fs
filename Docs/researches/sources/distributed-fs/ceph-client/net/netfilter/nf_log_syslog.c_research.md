
# sources/distributed-fs/ceph-client/net/netfilter/nf_log_syslog.c

Purpose: Provides the built-in syslog-style netfilter packet logger implementations for ARP, IPv4, IPv6, bridge, and netdev families.

Important APIs and functions: Static logger callbacks include `nf_log_arp_packet()`, `nf_log_ip_packet()`, `nf_log_ip6_packet()`, `nf_log_netdev_packet()`, and `nf_log_unknown_packet()`. Header renderers include `dump_arp_packet()`, `dump_ipv4_packet()`, `dump_ipv6_packet()`, `nf_log_dump_tcp_header()`, `nf_log_dump_udp_header()`, `dump_mac_header()`, and `nf_log_dump_packet_common()`. Module init registers loggers globally and binds them as defaults per net namespace.

Control flow: On log callback, the module rejects non-init-net logs unless `sysctl_nf_log_all_netns` allows them, opens an `nf_log_buf`, emits common IN/OUT/bridge physical device fields, decodes MAC/VLAN when requested, then decodes family-specific headers and L4 fields. IPv4 and IPv6 ICMP error logging recurses once into the embedded packet. Init registers pernet defaults first, then global logger providers; exit unregisters both.

State and persistence: Stores static `nf_logger` descriptors and default loginfo. Per-net default bindings are maintained through `nf_log_set()`/`nf_log_unset()`. Output is transient kernel log text.

Dependencies and integration: Uses the generic logger core, xt_LOG log flags, skb header accessors, bridge netfilter physical device helpers, IPv4/IPv6/ARP/TCP/UDP/ICMP parsers, and syslog printk output from `nf_log_buf_close()`.

Risks: Packet parsing must tolerate truncation and fragments without reading past skb data. Other risks include log flooding from namespaces, recursive ICMP decode bounds, IPv6 extension header loops/truncation, UID/GID lookup under RCU, MAC header assumptions for tunnel devices, and fixed log buffer size truncation. Test signals include LOG target output for ARP/IPv4/IPv6/netdev/bridge, fragments, malformed short packets, TCP options, IPv6 extension headers, ICMP embedded packets, UID logging, VLAN tags, and namespace sysctl gating.
