<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipvs.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_ipvs.c

## Purpose
`xt_ipvs.c` implements matching on Linux IPVS connection metadata. It lets firewall rules identify packets associated with virtual services, real servers, forwarding methods, and IPVS connection direction.

## Important APIs, Types, and Functions
The match path is `ipvs_mt()`, driven by `struct xt_ipvs_mtinfo`. It uses IPVS lookup helpers to find an `struct ip_vs_conn`, tests flags such as virtual address, virtual port, protocol, direction, method, and vport control, and releases IPVS connection references after evaluation. `ipvs_mt_check()` validates unsupported flags and family constraints.

## Control Flow, State, and Persistence
For each packet, the matcher asks IPVS whether the skb belongs to an IPVS connection in the configured direction. It then compares requested service tuple fields and method bits, applying inversion as encoded in the rule. The module itself persists no connection state; it observes IPVS-owned connection entries.

## Dependencies and Integration Points
It depends on IPVS being enabled, x_tables, IPv4/IPv6 address handling, and IPVS connection reference management. It is an integration bridge between iptables filtering and the IP virtual server load-balancing subsystem.

## Risks and Test Signals
Risks include stale assumptions about IPVS hook timing, connection reference leaks, mismatched direction flags, IPv4/IPv6 tuple comparison errors, and behavior when IPVS is not loaded or no connection exists. Tests should cover inbound and outbound IPVS packets, no-IPVS packets, virtual service address/port/protocol, real-server direction, forwarding method flags, inversion, IPv6 service tuples, and module dependency loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipvs.c -->
