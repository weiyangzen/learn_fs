# sources/distributed-fs/ceph-client/net/ipv4/arp.c

## Purpose
`arp.c` implements IPv4 Address Resolution Protocol support. It owns the ARP neighbor table, packet generation and receive processing, proxy/gratuitous ARP policy, user ioctl management, `/proc/net/arp` output, and device-event reactions.

## Important APIs, types, and functions
The central exported table is `arp_tbl`; exported helpers include `arp_send()`, `arp_create()`, `arp_xmit()`, `arp_invalidate()`, `arp_ioctl()`, `arp_ifdown()`, and `arp_init()`. Neighbor callbacks include `arp_hash()`, `arp_key_eq()`, `arp_constructor()`, `arp_solicit()`, `arp_error_report()`, `parp_redo()`, and `arp_is_multicast()`. Packet paths include `arp_rcv()` and `arp_process()`. Policy helpers include `arp_ignore()`, `arp_accept()`, `arp_filter()`, `arp_fwd_proxy()`, `arp_fwd_pvlan()`, and `arp_is_garp()`.

## Control flow
`arp_init()` initializes the neighbor table, registers the ARP packet handler, creates per-net proc entries, registers neighbor sysctls when enabled, and installs a netdevice notifier. Outbound solicitation is driven by neighbor core through `arp_solicit()`, which chooses a source address according to `arp_announce`, decides unicast/app/broadcast probing, and sends an ARP request. `arp_create()` builds hardware and protocol headers for device-specific ARP formats; `arp_xmit()` sends through the ARP netfilter output hook. Inbound `arp_rcv()` filters no-ARP/otherhost/loopback packets, validates header size and address lengths, clears neighbor control data, and passes through the ARP netfilter input hook to `arp_process()`. `arp_process()` validates hardware/protocol combinations, drops invalid targets, handles duplicate-address-detection requests, replies for local addresses or proxy cases, queues delayed proxy replies when configured, and updates neighbor entries for replies, requests, and accepted gratuitous ARP.

## State and persistence
Runtime state lives in `arp_tbl`, neighbor entries, proxy-neighbor entries, per-device IPv4 config, proc entries, and netdevice notifier registration. ioctl operations can create permanent neighbor entries or proxy settings, but these remain kernel runtime state unless userspace persists them externally.

## Dependencies and integration points
The file integrates with generic neighbor infrastructure, IPv4 routing and address-type lookups, inet device configuration, netfilter ARP hooks, netdevice events, procfs seq_file, sysctl neighbor parameters, AX.25/NETROM/FDDI/FireWire/Infiniband/IPGRE hardware variants, tunnel metadata replies, and AF_INET ioctls via `inet_ioctl()`.

## Risks and invariants
ARP reply policy is controlled by many sysctls (`arp_ignore`, `arp_accept`, `arp_filter`, proxy ARP, PVLAN, drop gratuitous ARP), so regressions can create spoofing exposure or connectivity failures. Neighbor locking and RCU contexts must be respected when updating entries. `arp_process()` intentionally treats DAD, GARP, proxy ARP, and local replies differently; merging cases can break standards behavior. Device address changes and carrier loss must flush or invalidate affected neighbor state to avoid stale L2 addresses.

## Test signals
Test ARP request/reply exchange on Ethernet and no-ARP devices, multicast mapping, neighbor solicitation retries, proxy ARP and PVLAN behavior, DAD requests with sender IP zero, gratuitous ARP accept/drop settings, ARP netfilter hooks, `SIOCSARP`/`SIOCGARP`/`SIOCDARP` permission and behavior, `/proc/net/arp` output, device address changes, carrier down eviction, and namespace-specific proc entries.
