# sources/distributed-fs/ceph-client/net/ipv4/devinet.c

## Purpose
`devinet.c` is the IPv4 per-device address and configuration manager. It creates and destroys `struct in_device` objects for netdevices, owns `struct in_ifaddr` IPv4 address lifetime and hash/list membership, implements the IPv4 address rtnetlink and legacy ioctl APIs, exposes IPv4 per-interface sysctl/netconf state, and notifies FIB, ARP, multicast, SCTP, netfilter, and other consumers when addresses or device IPv4 configuration change.

## Important APIs, Types, and Functions
The central state objects are `struct in_device`, its `cnf` `struct ipv4_devconf`, and its `ifa_list` of `struct in_ifaddr`. Per-net state includes `net->ipv4.inet_addr_lst`, `devconf_all`, `devconf_dflt`, `addr_chk_work`, and the IPv4 netconf/sysctl registrations.

Lookup and selection helpers exported to other IPv4 subsystems include `__ip_dev_find()`, `inet_lookup_ifaddr_rcu()`, `inetdev_by_index()`, `inet_ifa_byprefix()`, `inet_select_addr()`, and `inet_confirm_addr()`. Notification APIs are `register_inetaddr_notifier()`, `unregister_inetaddr_notifier()`, `register_inetaddr_validator_notifier()`, and `unregister_inetaddr_validator_notifier()`.

Address mutation is centered on `inet_alloc_ifa()`, `__inet_insert_ifa()`, `__inet_del_ifa()`, `inet_insert_ifa()`, `inet_set_ifa()`, `inet_rtm_newaddr()`, `inet_rtm_deladdr()`, and `devinet_ioctl()`. Rtnetlink serialization is handled by `inet_fill_ifaddr()`, `inet_dump_addr()`, `inet_dump_ifaddr()`, `inet_dump_ifmcaddr()`, and `rtmsg_ifa()`.

Device and namespace lifecycle entry points are `inetdev_init()`, `inetdev_destroy()`, `inetdev_event()`, `devinet_init_net()`, `devinet_exit_net()`, and `devinet_init()`. Configuration exposure is implemented through `inet_fill_link_af()`, `inet_set_link_af()`, `inet_netconf_get_devconf()`, `inet_netconf_dump_devconf()`, `inet_netconf_notify_devconf()`, and, under `CONFIG_SYSCTL`, the `devinet_sysctl` table and handlers such as `devinet_conf_proc()`, `devinet_sysctl_forward()`, and `ipv4_doint_and_flush()`.

## Control Flow
Netdevice registration calls `inetdev_event(NETDEV_REGISTER)`, which allocates an `in_device`, copies default IPv4 configuration, allocates ARP neighbour parameters, registers per-device sysctls, initializes multicast state, and finally publishes `dev->ip_ptr` with RCU. Loopback devices receive `NOXFRM` and `NOPOLICY`, and on `NETDEV_UP` get a host-scope `127.0.0.1/8` address if possible.

Address creation through rtnetlink begins in `inet_rtm_newaddr()`. It validates prefix length and mandatory `IFA_LOCAL`, converts attributes into a new `in_ifaddr`, either inserts it or replaces lifetime/metric/protocol on an existing address, optionally joins IPv4 multicast groups for `IFA_F_MCAUTOJOIN`, and emits `RTM_NEWADDR`. Legacy ioctl changes follow the same lower-level delete/insert path after translating `ifreq` and BSD alias labels.

`__inet_insert_ifa()` strips IPv6-only flags, determines primary versus secondary status by mask and prefix, calls validator notifiers before committing, links the address into `in_dev->ifa_list`, inserts it into the per-net address hash, schedules lifetime checking, sends rtnetlink notification, and then calls the blocking address notifier chain. `__inet_del_ifa()` handles primary deletion, optional secondary promotion, silent FIB route removal and re-add for promoted subnets, hash removal, `RTM_DELADDR`, and notifier delivery.

`check_lifetime()` periodically scans the per-net address hash under RCU. It batches expired or deprecated finite-lifetime addresses, takes the per-net RTNL lock only when a change is needed, deletes addresses whose valid lifetime expired, marks preferred-lifetime expirations with `IFA_F_DEPRECATED`, notifies via `RTM_NEWADDR`, and reschedules itself using addressconf fuzz windows.

Read paths are mostly RCU-protected. Address dumps validate strict dump requests, optionally target another net namespace through `IFA_TARGET_NETNSID`, iterate devices and addresses with resumable dump context, and use `inet_base_seq()` to make netlink dump consistency depend on both address generation and device list changes.

Device events coordinate IPv4 address state with multicast, ARP, sysctl, and route behavior. `NETDEV_DOWN` drops multicast state; MTU below IPv4 minimum or unregister destroys the `in_device`; rename rewrites address labels and sysctl paths; address or peer notifications can send gratuitous ARP when `ARP_NOTIFY` is enabled.

## State and Persistence Behavior
State is runtime kernel state scoped to each network namespace and device. Address objects are kept in both per-device RCU lists and a per-net hash keyed by local IPv4 address. Lifetime fields are `ifa_valid_lft`, `ifa_preferred_lft`, `ifa_tstamp`, `ifa_cstamp`, and `IFA_F_PERMANENT` / `IFA_F_DEPRECATED`.

Reference and memory lifetime is RCU-heavy. `inet_alloc_ifa()` takes an `in_device` reference; `inet_free_ifa()` uses `call_rcu_hurry()` so the `in_device` and netdevice reference are released promptly after readers quiesce. `in_device` destruction clears `dev->ip_ptr`, unregisters sysctls, releases ARP parameters, tears down multicast, and frees after RCU once references drain.

Configuration state lives in `devconf_all`, `devconf_dflt`, and per-device `in_dev->cnf`. Sysctl writes mark explicit per-field state bits, may copy default values to devices that have not overridden a field, may flush route cache for policy-affecting fields, and notify `RTNLGRP_IPV4_NETCONF`. No durable storage is written by this file.

## Dependencies and Integration Points
The file depends on rtnetlink, net namespaces, RCU, netdevice notifiers, ARP, IGMP, neighbour parameters, IPv4 route/FIB helpers, l3mdev/VRF helpers, netconf, sysctl, workqueues, and user-copy helpers. It calls FIB helpers indirectly through notifier consumers and directly in promotion paths through `fib_add_ifaddr()`, `fib_del_ifaddr()`, and `fib_modify_prefix_metric()`.

External consumers include route source address selection, ARP validation, bridge and bonding address confirmation, SCTP and mac80211 address notifiers, netfilter masquerade cleanup, IPv4 multicast autjoin, and userspace via `RTM_NEWADDR`, `RTM_DELADDR`, `RTM_GETADDR`, `RTM_GETMULTICAST`, `RTM_GETNETCONF`, `IFLA_INET_CONF`, and legacy `SIOCGIF*` / `SIOCSIF*` ioctls.

## Risks and Edge Cases
Primary/secondary address promotion is delicate because FIB routes must be removed and restored while the device address list still contains enough context to preserve preferred source behavior. Regressions can leave stale local or broadcast routes, mis-promote aliases, or notify listeners in an order that causes route restoration races.

Lifetime handling mixes RCU reads, delayed work, RTNL mutation, and jiffies arithmetic. Important edge cases include zero preferred lifetime, finite valid lifetime, permanent addresses, batched expiry, and avoiding too-frequent rescheduling.

Input validation must preserve historical behavior while enforcing modern netlink strictness. Risks include accepting IPv6-only flags on IPv4 addresses, non-contiguous masks in ioctl paths, unsupported strict dump attributes, invalid net namespace IDs, multicast autojoin failure rollback, and sysctl device names that cannot be registered safely.

Locking assumptions are strict: list/hash address mutations require RTNL, lookup helpers require RCU or RTNL, sysctl forwarding changes may restart the syscall if RTNL cannot be acquired, and notifier callbacks run after visible state changes.

## Test Signals
Useful tests include rtnetlink add/delete/replace of primary and secondary addresses, `NLM_F_EXCL` and `NLM_F_REPLACE`, `IFA_CACHEINFO` finite lifetime expiry/deprecation, `IFA_F_MCAUTOJOIN` success and rollback, invalid prefix and missing-local errors, strict dump filtering by ifindex and target netns, and netconf get/dump for all/default/device scopes.

Lifecycle tests should cover device register/up/down/unregister, MTU below IPv4 minimum, loopback auto-address creation, rename label preservation, gratuitous ARP on notify events, sysctl unregister/re-register, namespace initialization with each `net_inherit_devconf()` mode, and teardown with pending lifetime work. Source selection tests should cover VRF/l3mdev master selection, `route_localnet`, loopback preference, and wildcard `inet_confirm_addr()` behavior.
