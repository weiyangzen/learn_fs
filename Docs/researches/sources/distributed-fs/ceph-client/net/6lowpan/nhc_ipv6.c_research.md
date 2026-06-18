<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ipv6.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ipv6.c

This module registers RFC6282 IPv6 next-header compression metadata. The descriptor `nhc_ipv6` maps `NEXTHDR_IPV6` to id `0xee` with mask `0xfe`.

There are no transform callbacks, making this a recognition-only module. It allows the core to name the id but cannot compress or rebuild an IPv6-in-IPv6 header.

The only state is the descriptor's presence in the global NHC table. It depends on `nhc.h`, module lifecycle, and IPv6 next-header constants. There is no persistent configuration.

Risks are limited but important for nested IPv6 traffic: matching ids are unsupported and should be dropped cleanly. Tests should cover add/delete, id mask matching, and unsupported receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ipv6.c -->
