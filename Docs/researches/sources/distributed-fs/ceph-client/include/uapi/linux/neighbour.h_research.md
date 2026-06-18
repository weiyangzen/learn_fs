# sources/distributed-fs/ceph-client/include/uapi/linux/neighbour.h

## Purpose
Defines rtnetlink neighbour/FDB and neighbour-table ABI: neighbour messages, attributes, flags, NUD states, cacheinfo, table stats/config, table parameters, and FDB extension attributes.

## Important APIs, Types, And Functions
Exports `ndmsg`, `NDA_*`, neighbour flags `NTF_*`, extended flags, `NUD_*`, `nda_cacheinfo`, `ndt_stats`, `NDTPA_*`, `ndtmsg`, `ndt_config`, `NDTA_*`, FDB notification bits, and `NFEA_*`.

## Control Flow
Userspace sends rtnetlink messages to add/delete/get neighbours or FDB entries and to get/set neighbour table parameters. Dumps may be split across messages with global table data followed by device-specific parameter sets.

## State, Persistence, And Dependencies
State persists in neighbour caches, bridge FDBs, and neighbour table configuration per namespace/interface. Depends on `linux/types.h` and `linux/netlink.h`.

## Integration Points
Used by `ip neigh`, bridge tooling, routing daemons, EVPN control planes, and kernel neighbour discovery/ARP/NDP subsystems.

## Risks
Some flags are bridge-FDB-specific and states may be ignored for externally learned entries. Managed/locked/externally validated flags have control-plane semantics. Timing fields are milliseconds with 64-bit attrs.

## Test Signals
Validate add/delete/dump, state transitions, cacheinfo fields, extended flags, table parameter get/set, split table dumps, FDB activity notifications, and locked/managed entry behavior.
