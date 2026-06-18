# sources/distributed-fs/ceph-client/net/dsa/port.h

## Purpose
This private header declares the DSA per-port operation surface shared across core, user netdev, switch notifier, conduit, and tag code.

## Important APIs, Types, And Functions
It declares bridge, LAG, VLAN filtering, ageing, MST, bridge flags, MTU, FDB/MDB, host FDB/MDB, VLAN, MRP, phylink, shared-port link, HSR, tag_8021q, host flood, and conduit-change helpers. It also declares `dsa_port_supports_hwtstamp()` and `dsa_port_set_tag_protocol()`.

## Control Flow
No executable flow is present. The declarations mirror implementation in `port.c` and are invoked by `dsa.c`, `switch.c`, `conduit.c`, `tag.h`, and user-port code.

## State And Persistence
The header has no state. Declared functions manipulate `struct dsa_port` state owned by the DSA tree.

## Dependencies And Integration Points
It includes `<net/dsa.h>` and forward-declares bridge, lag, switchdev, phy, and netlink types so DSA internal files can share port functionality.

## Risks And Edge Cases
This is a broad internal API; changes to semantics such as whether `-EOPNOTSUPP` is ignorable must be audited across many callers.

## Test Signals
Compile coverage plus bridge, LAG, VLAN, FDB/MDB, MRP, phylink, and conduit migration tests exercise this header.
