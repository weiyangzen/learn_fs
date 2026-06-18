# sources/distributed-fs/ceph-client/net/ipv4/igmp.c

## Purpose
`igmp.c` implements IPv4 Internet Group Management Protocol and socket multicast membership management. It handles IGMPv1/v2/v3 query/report processing, multicast group join/leave APIs, source filters for SSM/MSF, device multicast filters, netlink multicast-address notifications, procfs reporting, and netdevice rejoin events.

## Important APIs, Types, And Functions
Primary state types are `struct ip_mc_list` for per-interface multicast group membership, `struct ip_sf_list` for per-interface source filters, and `struct ip_mc_socklist` plus `struct ip_sf_socklist` for per-socket memberships and filters. The helper declaration for `inet_fill_ifmcaddr` lives in `igmp_internal.h`.

External functions include `igmp_rcv`, `ip_mc_check_igmp`, `__ip_mc_inc_group`, `ip_mc_inc_group`, `__ip_mc_dec_group`, `ip_mc_join_group`, `ip_mc_join_group_ssm`, `ip_mc_leave_group`, `ip_mc_source`, `ip_mc_msfilter`, `ip_mc_msfget`, `ip_mc_gsfget`, `ip_mc_sf_allow`, `ip_mc_drop_socket`, `ip_check_mc_rcu`, `ip_mc_init_dev`, `ip_mc_up`, `ip_mc_down`, `ip_mc_destroy_dev`, `ip_mc_unmap`, `ip_mc_remap`, `inet_fill_ifmcaddr`, and `igmp_mc_init`.

Internal report machinery includes `igmpv3_newpack`, `add_grec`, `igmpv3_send_report`, `igmpv3_send_cr`, `igmp_send_report`, `igmp_heard_query`, `igmp_heard_report`, timers for group query/interface change/group reports, and deleted-record handling through `igmpv3_add_delrec`, `igmpv3_del_delrec`, and `igmpv3_clear_delrec`.

## Control Flow
Incoming IGMP packets enter `igmp_rcv`, which resolves L3 master devices, validates an `in_device`, verifies header pull and checksum, then dispatches by IGMP type. Queries call `igmp_heard_query`: v1/v2 queries update seen timers and clear v3 change state, while v3 queries parse QRV/QQIC/source lists, start general-query timers, or mark group/source-specific query state before scheduling report timers. Reports from other hosts call `igmp_heard_report` to suppress local pending reports for the group. PIM v1 can be delegated when configured.

Group join through `ip_mc_join_group` or `ip_mc_join_group_ssm` selects an interface, checks duplicate socket membership and membership limits, links a socket membership, increments or creates the interface group, updates device multicast filters, emits rtnetlink multicast-address notifications, and starts the appropriate unsolicited report/change-report path. Leave removes socket source filters, decrements interface users, sends leave or v3 change records when applicable, removes filters, notifies rtnetlink, and frees objects through RCU.

IGMPv3 reporting builds one or more packets with router-alert IP option, TTL 1, control priority, and group records selected by current filter mode, source change state, deleted group records, and query response state. Change-report timers repeat according to QRV. For v1/v2, `igmp_send_report` emits fixed IGMP report or leave messages.

Source filter APIs update both socket-side and interface-side counts. `ip_mc_source` adds/removes individual source entries. `ip_mc_msfilter` replaces a full filter list. `ip_mc_sf_allow` and `ip_check_mc_rcu` enforce receive-side source-filter delivery decisions.

## State And Persistence
State is per network namespace, per device, and per socket. `in_device` owns `mc_list`, optional `mc_hash`, tomb records, query version timers, QRV/QI/QRI values, and timers. Sockets own `inet->mc_list`. Memberships and source filters persist until explicit leave, socket close, device down/destroy, or namespace teardown. RCU protects readers; RTNL protects membership mutation; per-group spinlocks protect source and timer fields.

## Dependencies And Integration Points
The file depends on IPv4 device configuration sysctls, routing for IGMP packet output, ARP multicast address mapping, netdevice multicast filter APIs, rtnetlink notifications, procfs, netdevice notifier events, multicast routing/PIM when enabled, checksum helpers, socket memory accounting, and namespace pernet ops. It creates proc entries `igmp` and `mcfilter` and an autojoin control socket when procfs is enabled.

## Risks
The hardest risks are timer/reference lifetime, RCU plus RTNL list mutation, source-filter count consistency, and IGMPv3 deleted-record handling. Incorrect query parsing can cause missed or excessive reports. Join/leave edge cases can leak socket memory accounting or leave device multicast filters installed. Procfs source-filter iteration holds group spinlocks while walking and must release them on all paths.

## Test Signals
Test ASM and SSM joins/leaves, duplicate joins, membership and source-filter limits, INCLUDE/EXCLUDE mode transitions, v1/v2 querier fallback, v3 general/group/source-specific queries, report suppression by heard reports, device down/up/remap/destroy, socket close cleanup, rtnetlink `RTM_NEW/DELMULTICAST`, `/proc/net/igmp` and `/proc/net/mcfilter`, checksum and packet validation via `ip_mc_check_igmp`, and receive filtering through `ip_mc_sf_allow` and `ip_check_mc_rcu`.
