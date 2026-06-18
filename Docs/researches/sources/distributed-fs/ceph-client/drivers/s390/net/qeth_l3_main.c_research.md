# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_main.c

Purpose: implements qeth layer 3 networking: IP address registration, IP takeover, routing assists, multicast synchronization, ARP private ioctls, sniffer/diagnostic trace integration, L3 transmit header construction, netdevice setup, online/offline transitions, and IPv4/IPv6 address notifiers.

Important APIs and functions: exported discipline is `qeth_l3_discipline`. Address management centers on `qeth_l3_add_ip()`, `qeth_l3_delete_ip()`, `qeth_l3_modify_ip()`, `qeth_l3_register_addr_entry()`, and `qeth_l3_deregister_addr_entry()`. Routing uses `qeth_l3_setrouting_v4()` and `qeth_l3_setrouting_v6()`. IPATO uses `qeth_l3_update_ipato()`, `qeth_l3_add_ipato_entry()`, and `qeth_l3_del_ipato_entry()`. TX uses `qeth_l3_hard_start_xmit()`, `qeth_l3_xmit()`, and `qeth_l3_fill_header()`. Notifier entry points are `qeth_l3_ip_event()` and `qeth_l3_ip6_event()`.

Control flow: adding an address looks up by hash/IP, refcounts duplicate normal addresses, rejects conflicting masks/types, marks takeover if covered by IPATO, caches offline addresses with `QETH_DISP_ADDR_ADD`, or issues IPA set-IP commands online. Online setup starts adapter assists, routing, qeth threads, recovers cached IPs, then registers or reattaches the netdev. Multicast rx-mode work rebuilds desired multicast addresses from IPv4/IPv6 device lists and VLANs, then sends set/delete multicast IPA commands based on disposition flags.

State and persistence: address state is runtime in `card->ip_htable`, `card->rx_mode_addrs`, `card->ipato`, and route/sniffer/HSUID options. Offline/recovery keeps address objects with `disp_flag` to replay after hardware returns. IPv6 notifier work is queued to `card->cmd_wq` to avoid doing heavier modifications directly in notifier context.

Dependencies and integration: depends on qeth core IPA helpers, qdio/NAPI, Linux inet and inet6 address notifiers, VLAN iteration, ARP private ioctl ABI, Fibre/IUCV protocol constants for IQD special cases, and diag assist for HiperSockets traffic analyzer mode.

Risks: user-visible IP state must stay coherent across notifier callbacks, sysfs VIPA/RXIP changes, offline transitions, and recovery. ARP query copies variable hardware records into a user buffer and must preserve bounds and protocol matching. L3 TX rewrites skb headroom for IPv4/IQD and fixes checksum/GSO fields; incorrect headroom or protocol handling can corrupt packets. Sniffer and CQ modes are mutually constrained by sysfs.

Test signals: IPv4/IPv6 address add/delete notifier flows including duplicate refcounts, offline recovery replay, IPATO enable/invert/prefix matching, VIPA/RXIP add/delete, multicast list changes and VLAN multicast, ARP ioctl query/add/remove/flush/set-count including permission and buffer-size failures, L3 TX for IPv4/IPv6/AF_IUCV/VLAN/GSO/checksum, IQD sniffer drops, and online/offline with carrier states.
