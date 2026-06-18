<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_owner.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_owner.c

## Purpose
`xt_owner.c` implements matching locally generated packets by socket owner credentials, socket existence, and supplementary group membership. It is intended for OUTPUT and POSTROUTING style local traffic policy.

## Important APIs, Types, and Functions
`owner_mt()` consumes `struct xt_owner_match_info`, reading `skb_to_full_sk(skb)`, socket file ownership, `kuid_t`, `kgid_t`, and `struct group_info`. `owner_check()` validates hook usage and flag combinations. Registration is NFPROTO_UNSPEC.

## Control Flow, State, and Persistence
Packet evaluation obtains the full socket if available. It checks socket-exists, UID range, GID range, and supplementary group membership as requested, applying individual inversion flags. No state is persisted; it observes current socket credential state.

## Dependencies and Integration Points
The module depends on socket ownership metadata, user namespaces for UID/GID comparisons, x_tables hook validation, and local output skb socket association. It cannot reliably classify forwarded traffic.

## Risks and Test Signals
Risks include missing skb sockets, credential changes after socket creation, namespace UID/GID mapping, supplementary group iteration cost, and misuse outside local hooks. Tests should cover owned local TCP/UDP packets, raw packets with no socket, UID/GID ranges, supplementary groups, inversion, invalid hooks, and user namespace mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_owner.c -->
