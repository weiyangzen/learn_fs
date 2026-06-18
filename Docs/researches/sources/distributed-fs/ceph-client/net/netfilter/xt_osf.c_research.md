<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_osf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_osf.c

## Purpose
`xt_osf.c` implements passive operating-system fingerprint matching. It delegates TCP fingerprint classification to the nfnetlink OS fingerprint database.

## Important APIs, Types, and Functions
`xt_osf_match_packet()` is the match entry point. It consumes `struct xt_osf_info`, extracts match behavior flags, and calls the OS fingerprint matcher provided by `nfnetlink_osf`. `xt_osf_mt_reg` registers the `osf` match for IPv4 TCP traffic.

## Control Flow, State, and Persistence
The match evaluates packets against the loaded OS fingerprint table and optional TTL/logging behavior from userspace. The fingerprint database and learned/static signatures live in nfnetlink OSF state; this module does not persist its own table.

## Dependencies and Integration Points
It depends on x_tables, TCP/IP header parsing, and the nfnetlink OSF subsystem. Userspace must load fingerprints through nfnetlink tooling for meaningful matches.

## Risks and Test Signals
Risks include stale or absent fingerprints, TCP option parsing assumptions, TTL heuristics, and misleading results across NAT, middleboxes, or SYN proxies. Tests should cover known SYN fingerprints, unknown packets, database absent, TTL modes, logging flags, non-TCP rejection, and module dependency loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_osf.c -->
