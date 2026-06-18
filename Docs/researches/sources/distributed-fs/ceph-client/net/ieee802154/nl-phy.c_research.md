## sources/distributed-fs/ceph-client/net/ieee802154/nl-phy.c

Purpose: legacy generic-netlink handlers for IEEE 802.15.4 PHY listing and deprecated virtual-interface creation/deletion.

Important APIs/types/functions: `ieee802154_nl_fill_phy()` formats PHY name, current page/channel, and supported channel/page list into a genl message. `ieee802154_list_phy()` resolves a PHY by null-terminated name and replies with a single PHY. `ieee802154_dump_phy()` iterates all PHYs using `wpan_phy_for_each()` and callback cursor state. `ieee802154_add_iface()` creates a deprecated virtual interface through `rdev_add_virtual_intf_deprecated()`, optionally sets hardware address with RTNL, and replies with phy/device names. `ieee802154_del_iface()` resolves an IEEE802154 netdev by name, optionally verifies PHY name, and deletes through `rdev_del_virtual_intf_deprecated()`.

Control flow and state: list/dump build skbs and manage `wpan_phy` references. Add-interface validates strings, type, and optional hardware address length, creates the device, holds it while configuring, and unregisters on MAC-address failure. Delete-interface obtains a netdev reference, obtains a phy reference, and releases both on all paths.

Dependencies and integration points: uses core `wpan_phy_find()`/`wpan_phy_for_each()`, rdev deprecated ops, RTNL for MAC address and deletion, and legacy netlink helpers.

Risks: deprecated ops depend on driver support and older userspace semantics. String null-termination and `IFNAMSIZ` checks are manual. Some cleanup paths must balance `dev_hold`, `dev_put`, and `wpan_phy_put()` exactly.

Test signals: legacy PHY list/dump with multiple PHYs, interface add/delete success and invalid type/name/address cases, MAC address set failure rollback, and PHY-name mismatch rejection on delete.
