# sources/distributed-fs/ceph-client/net/mac802154/mib.c

Purpose: exposes MAC PIB and LLSEC management operations for netdevices, adding netdevice validation and interface-level serialization around `llsec.c`.

Important APIs and functions: `mac802154_dev_set_page_channel()` calls the driver channel setter and updates current PHY page/channel. `mac802154_get_params/set_params()`, key/device/device-key/security-level add/delete helpers, and table lock/get/unlock wrap the corresponding LLSEC functions with `sdata->sec_mtx`.

Control flow and state: every LLSEC mutation or table exposure locks `sec_mtx`, checks `ARPHRD_IEEE802154`, then delegates to `llsec.c`. Channel setting is RTNL-only and updates software state only after successful hardware programming.

Dependencies and integration: consumed by `mac_cmd.c` LLSEC ops table and cfg802154/mac802154 control paths. It depends on netdevice-to-subinterface conversion and driver ops.

Risks and test signals: table exposure gives callers a live pointer while holding `sec_mtx`; callers must pair lock/unlock. Channel set failure leaves old channel values intact. Tests should verify serialized concurrent add/delete and table iteration behavior.
