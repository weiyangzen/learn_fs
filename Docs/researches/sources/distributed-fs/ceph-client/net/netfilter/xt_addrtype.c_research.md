# sources/distributed-fs/ceph-client/net/netfilter/xt_addrtype.c

Purpose: `addrtype` match tests source/destination address type, with optional input/output interface limits.

Important APIs/types/functions: `match_type()` for IPv4, `match_lookup_rt6()` and `match_type6()` for IPv6, `addrtype_mt_v0()`, `addrtype_mt_v1()`, and check functions.

Control flow: runtime chooses interface based on flags, classifies source and/or destination, applies inversion, and for IPv6 performs route lookup when local/anycast/unreachable checks are needed. Checks reject invalid interface limits for hook direction and unsupported IPv6 masks.

State and persistence: no persistent state. Dependencies include x_tables, IPv4 address type, IPv6 routing/FIB, netdevice context, and hook masks. Risks: route lookup cost/failure, unsupported IPv6 address types, hook/interface mismatch, and v0/v1 inversion differences. Test signals: IPv4 local/broadcast/unicast, IPv6 multicast/anycast/unreachable, inversion, iface constraints, hook validation, and route errors.
