# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-neigh.yaml

Purpose: this raw rtnetlink schema describes IP neighbour and forwarding database management plus neighbour-table dump/set operations.

Important APIs, types, and functions: `ndmsg` is the main fixed header, carrying family, ifindex, neighbour state, neighbour flags, and route message type. `ndtmsg` is used for table operations. Definitions include NUD states, neighbour flags (`use`, `self`, `master`, `proxy`, `ext-learned`, `offloaded`, `sticky`, `router`), extended flags (`managed`, `locked`, `ext-validated`), `rtm-type`, neighbour cacheinfo, table config, and table stats. `neighbour-attrs` contains destination, link-layer address, cacheinfo, probes, VLAN/VNI/port, ifindex/master, namespace id, protocol, nexthop id, FDB extension data, extended flags, and masks. `ndt-attrs` and `ndtpa-attrs` expose neighbour table thresholds and per-interface timing/queue parameters.

Control flow: `newneigh` value 28 adds entries; `delneigh` value 29 removes by destination and ifindex; deletion and creation notifications reuse `getneigh`. `getneigh` value 30 does single lookup by destination and dumps by ifindex/master. `getneightbl` value 66 dumps tables with reply value 64. `setneightbl` value 67 mutates table thresholds, parameters, and GC interval.

State and persistence: neighbour entries live in per-namespace neighbour tables and may be static, learned, offloaded, or garbage-collected depending on state and flags. Table parameters persist until changed or namespace/device teardown.

Dependencies and integration: depends on `linux/rtnetlink.h`, ARP/ND/FDB kernel internals, bridge/VXLAN offload users, and multicast group `rtnlgrp-neigh`.

Risks: FDB and IP neighbour use the same message family but interpret fields differently. Extended flags and masks need careful compatibility handling. Test signals include neighbour add/delete/get in an isolated namespace, bridge FDB entries with VLAN/VNI if supported, table dump parsing, table parameter mutation tests, and notification observation.
