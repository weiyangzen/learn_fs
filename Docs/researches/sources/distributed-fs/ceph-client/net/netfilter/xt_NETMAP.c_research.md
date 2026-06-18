# sources/distributed-fs/ceph-client/net/netfilter/xt_NETMAP.c

Purpose: `NETMAP` target maps one subnet to another one-to-one by preserving host bits and replacing network bits.

Important APIs/types/functions: `netmap_tg4()`, `netmap_tg6()`, `netmap_tg4_check()`, `netmap_tg6_checkentry()`, `nf_nat_setup_info()`, and `HOOK2MANIP()`.

Control flow: check requires MAP_IPS and, for IPv4, one range, then obtains conntrack. Runtime computes netmask from min/max address, chooses source or destination by hook, creates a single-address NAT range, and sets up NAT manipulation.

State and persistence: NAT state persists in conntrack; rule holds conntrack netns reference. Dependencies include nat hooks, IPv4/IPv6 headers, nf_nat, and conntrack. Risks: surprising masks from range endpoints, conntrack availability, hook direction, and IPv6 range interpretation. Test signals: DNAT/SNAT hooks, IPv4/IPv6 mapping, MAP_IPS/rangesize validation, conntrack setup, and destroy put.
