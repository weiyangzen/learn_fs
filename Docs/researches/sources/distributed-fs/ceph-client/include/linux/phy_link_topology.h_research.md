# sources/distributed-fs/ceph-client/include/linux/phy_link_topology.h

## Purpose
Network-device PHY topology tracking API. It models chains of PHYs and SFP-attached PHYs so userspace can address individual PHY capabilities.

## Important APIs, Types, and Functions
Defines `struct phy_link_topology` with an `xarray` of PHY nodes and next index, and `struct phy_device_node` with upstream type, upstream netdev/PHY, optional parent SFP bus, and target PHY. Exposes `phy_link_topo_add_phy()`, `phy_link_topo_del_phy()`, and `phy_link_topo_get_phy()` when PHYLIB is enabled; otherwise stubs return success or NULL.

## Control Flow
PHYs are added to a netdevice topology when attached or discovered, looked up by `phyindex` for userspace operations, and removed on detach. The inline lookup handles absent topology by returning NULL.

## State and Persistence
Topology state persists in `net_device->link_topo`, an xarray, and assigned PHY indexes. Nodes track upstream relationships to support chained links.

## Dependencies and Integration Points
Depends on ethtool topology definitions, netdevice, xarray, PHYLIB, and SFP bus integration.

## Risks
Index allocation and deletion must be synchronized by implementation code. Stale nodes could expose detached PHYs to userspace. Disabled stubs mean callers must not assume topology exists.

## Test Signals
EtHTool PHY index queries, SFP-with-PHY attach/detach tests, chained PHY topologies, and xarray lifetime tests under netdevice teardown.
