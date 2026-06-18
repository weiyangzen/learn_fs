## sources/distributed-fs/ceph-client/net/ieee802154/nl-mac.c

Purpose: legacy generic-netlink handlers for IEEE 802.15.4 MAC/MLME management and low-level security table management. It parses legacy attributes, resolves WPAN netdevices, invokes `ieee802154_mlme_ops`, formats interface information, and dumps/mutates LLSEC keys/devices/devkeys/security levels.

Important APIs/types/functions: address helpers convert netlink hardware/short addresses. `ieee802154_nl_fill_iface()` reports device name/index, phy name, hardware address, short address, PAN ID, and optional MAC params. `ieee802154_nl_get_dev()` resolves by device name or index in `init_net` and enforces `ARPHRD_IEEE802154`. MLME handlers include `ieee802154_associate_req()`, `ieee802154_associate_resp()`, `ieee802154_disassociate_req()`, `ieee802154_start_req()`, `ieee802154_scan_req()`, `ieee802154_list_iface()`, `ieee802154_dump_iface()`, and `ieee802154_set_macparams()`. LLSEC handlers parse/fill key IDs, get/set params, add/delete/dump keys, devices, device keys, and security levels.

Control flow and state: most requests validate required attrs, get a dev reference, check operation availability, call the MLME/LLSEC callback, and `dev_put()`. MAC params are read/modified under RTNL and rejected while the netdev is running. LLSEC dumps iterate netdevices and tables using `cb->args[]` as cursors, locking each LLSEC table around list traversal.

Dependencies and integration points: depends on legacy `netlink.c`, UAPI attributes, `ieee802154_mlme_ops`, netdevice lookup, RTNL, LLSEC table callbacks, and IEEE address helpers.

Risks: use of `init_net` in `ieee802154_nl_get_dev()` limits namespace awareness relative to modern nl802154. Attribute validation is manual and some returns use `-ENOBUFS` for parse-like failures. LLSEC dump cursor handling is coarse; nested devkey iteration uses two indices and must avoid repeating/skipping under table mutation.

Test signals: legacy association/start/scan requests, interface dumps, set-macparams rejection while running, LLSEC parameter round trips, add/delete/list for each LLSEC object type, malformed attr rejection, and netns behavior expectations.
