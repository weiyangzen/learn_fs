# sources/distributed-fs/ceph-client/tools/include/uapi/linux/neighbour.h

Purpose: defines rtnetlink neighbor/ARP/NDP table ABI for neighbor entries, proxy entries, neighbor table parameters, statistics, and FDB activity extensions.

Important APIs/types: `struct ndmsg` identifies neighbor family, interface, state, flags, and type. Neighbor attributes include destination, link-layer address, cache info, probes, VLAN, port, VNI, ifindex, master, protocol, nexthop ID, FDB extended attributes, flags extension, and NDM state masks. Flags/states cover permanent, noarp, stale, reachable, delay, probe, failed, router/proxy, externally learned, offloaded, sticky, managed, locked, and extended state validity. `struct nda_cacheinfo`, `ndt_stats`, `ndtmsg`, and `ndt_config` support timing and table introspection. `NDTPA_*`, `NDTA_*`, and `NFEA_*` enums define tunable table parameters and FDB activity notification attributes.

Control flow, state, and persistence: userspace sends `RTM_NEWNEIGH`, `DELNEIGH`, `GETNEIGH`, and table requests. Kernel updates neighbor/FDB cache entries and table parameters; entries persist until timeout, deletion, device teardown, or namespace teardown.

Dependencies and integration points: depends on netlink/types. Integrates iproute2 `ip neigh`, bridge FDB, ARP/NDP, switchdev/offload, VXLAN/bridge learning, and network managers.

Risks and test signals: risks include stale cache semantics, offload/extern-learned mismatch, hardware FDB sync races, incorrect lifetime units, and nested FDB extension parsing. Tests should add/delete/dump IPv4/IPv6 neighbors, proxy entries, bridge FDB entries, table parameter changes, stale/reachable transitions, and offload/activity notification attributes.
