<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/rtnetlink.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/rtnetlink.h

Purpose: this header defines rtnetlink message types, core route/link/traffic-control message structs, attribute helpers, route constants, nexthop layouts, multicast groups, and dump filters used to manage networking state from userspace.

Important APIs/types: the `RTM_*` enum covers links, addresses, routes, neighbours, rules, qdiscs/classes/filters/actions, multicast/anycast, neighbour tables, netconf, MDB, namespace IDs, stats, chains, nexthops, VLANs, buckets, and tunnels. Core structs are `rtattr`, `rtmsg`, `rtnexthop`, `rtvia`, `rta_cacheinfo`, `rta_session`, `rta_mfc_stats`, `rtgenmsg`, `ifinfomsg`, `prefixmsg`, `tcmsg`, `nduseroptmsg`, and `tcamsg`. Helper macros (`RTA_*`, `RTM_RTA`, `RTNH_*`, `TCA_RTA`, `TA_RTA`) define aligned parsing of nested payloads.

Control flow: userspace opens a netlink route socket, sends messages with `nlmsghdr` plus one of these payload structs, and appends aligned `rtattr` attributes. Kernel networking subsystems reply and multicast changes to `RTNLGRP_*` groups.

State and persistence: live state is in kernel network namespaces: interfaces, addresses, routes, neighbours, tc objects, and multicast subscriptions. The header only defines serialization and stable numeric IDs.

Dependencies/integration: includes `linux/netlink.h`, `if_link.h`, `if_addr.h`, and `neighbour.h`; used by iproute2, network managers, container runtimes, routing daemons, and tc tooling. It integrates directly with `pkt_cls.h` and `pkt_sched.h` through `tcmsg`.

Risks and test signals: risks include alignment bugs, incomplete `rta_len` validation, message-family drift, attribute nesting mistakes, and privilege/network-namespace behavior. Tests should add/dump/delete routes, links, qdiscs, filters, actions, and nexthops, including multipart dumps and multicast notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/rtnetlink.h -->
