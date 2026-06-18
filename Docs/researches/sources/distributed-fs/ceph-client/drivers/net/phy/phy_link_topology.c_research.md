<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_link_topology.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_link_topology.c

Purpose: Maintains a per-netdev topology of PHY devices directly or indirectly attached to a MAC, including PHYs behind another PHY such as SFP module PHYs.

Important APIs and functions: `phy_link_topo_add_phy()` creates the topology container if needed, allocates a `phy_device_node`, records upstream relationship metadata, and assigns or reuses a stable `phyindex`. `phy_link_topo_del_phy()` removes a PHY from the topology xarray and frees its node. Static `netdev_alloc_phy_link_topology()` initializes `struct phy_link_topology` and its xarray.

Control flow: Adding a PHY lazily creates `dev->link_topo`, fills `pdn->phy`, stores either upstream netdev or upstream PHY based on `enum phy_upstream`, captures parent SFP bus when applicable, records upstream type, then inserts by existing `phy->phyindex` or allocates cyclically from index 1. Deletion erases by `phy->phyindex` and intentionally leaves that index on the PHY for reuse if the same object is later reattached.

State and persistence: Mutates `dev->link_topo`, the topology xarray, `next_phy_index`, and `phy->phyindex`. State is in-memory per netdev and persists across detach/reattach of the same PHY object until the netdev topology is destroyed elsewhere.

Dependencies and integration points: Depends on `linux/phy_link_topology.h`, `linux/phy.h`, RTNL assumptions, xarray allocation, and SFP helpers. It is called from `phy_attach_direct()`, `phy_detach()`, SFP connect/disconnect upstream ops, and user-visible topology consumers such as ethtool netlink.

Risks: The file includes `rtnetlink.h` but does not assert RTNL in these helpers; callers must serialize topology updates. A failed insert must free the node. Leaving `phyindex` set after deletion is intentional, but stale indexes can collide if a different node is inserted at the same ID before reuse. Topology lifetime for `dev->link_topo` must be handled by netdev core or other owners outside this file.

Test signals: Attach first PHY to a netdev with no topology; add nested SFP PHYs; detach and reattach same PHY to verify index reuse; allocation and xarray insertion failure; invalid upstream type; multiple PHYs on one netdev with stable unique indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_link_topology.c -->
