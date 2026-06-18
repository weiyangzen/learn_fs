# sources/distributed-fs/ceph-client/net/mac802154/mac_cmd.c

Purpose: wires mac802154 MLME operations to cfg802154/netdev callbacks for PAN start, MAC parameter get/set, and LLSEC table manipulation.

Important APIs and functions: `mac802154_mlme_start_req()` programs PAN ID, short address, channel/page, and LLSEC coordinator/local addressing. `mac802154_set_mac_params()` updates transmit power, CCA mode/level, CSMA retries, frame retries, and listen-before-talk, invoking driver operations only for supported PHY flags. `mac802154_get_mac_params()` snapshots current parameters. `mac802154_mlme_wpan` publishes the ops table.

Control flow and state: all functions assert RTNL. Start request mutates `dev->ieee802154_ptr`, calls `mac802154_dev_set_page_channel()`, and pushes LLSEC parameter changes through `mac802154_set_params()`. Parameter setting updates local `wpan_dev`/`wpan_phy` state first, then programs hardware.

Dependencies and integration: depends on `driver-ops.h`, `mib.c` wrappers, cfg802154 MLME interfaces, and netdevice state. It is the bridge between userspace/configuration requests and lower driver hooks.

Risks and test signals: partial hardware programming can leave software-updated values after a later driver operation fails. Test by setting combinations of PHY flags and checking error propagation and retained state. PAN start assumes short-address mode and uses `BUG_ON` for invalid callers.
