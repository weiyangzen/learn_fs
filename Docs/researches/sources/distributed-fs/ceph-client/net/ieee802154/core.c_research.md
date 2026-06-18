## sources/distributed-fs/ceph-client/net/ieee802154/core.c

Purpose: cfg802154 core lifecycle and registry for `wpan_phy` objects and their associated WPAN netdevices. It creates/registers/unregisters PHYs, tracks registered devices, handles netdevice notifier state, moves PHY/device groups across net namespaces, initializes subsystem services, and frees PAN association state.

Important APIs/types/functions: exports `wpan_phy_find()`, `wpan_phy_for_each()`, `wpan_phy_new()`, `wpan_phy_register()`, `wpan_phy_unregister()`, and `wpan_phy_free()`. Internal lookup helpers include `cfg802154_rdev_by_wpan_phy_idx()` and `wpan_phy_idx_to_wpan_phy()`. `cfg802154_switch_netns()` moves all netdevices under a registered device and rolls back on failure. `cfg802154_netdev_notifier_call()` handles register/up/down/unregister for WPAN netdevices, maintaining `wpan_dev_list`, generation counters, opencount, running interface count, association locks/lists, and netns immutability.

Control flow and state: `cfg802154_rdev_list` is RCU-protected with RTNL for writers. Registration calls `device_add()`, appends to the global list, and increments generation. Unregistration waits for `opencount == 0`, removes from the list, synchronizes RCU, increments generation, and deletes the device. Netdev up/down changes opencount and wakes waiters; unregister frees parent/children PAN structures and removes the wpan_dev once even under repeated unregister events.

Dependencies and integration points: depends on sysfs class support, rtnetlink, generic and modern netlink init, netdevice notifier chain, pernet operations, and PAN helpers. Module init order registers pernet, sysfs, notifier, legacy netlink, then nl802154.

Risks: global registry and per-device lists require strict RTNL/RCU discipline. Namespace switching has a rollback loop that must preserve netns immutability flags. `wpan_phy_unregister()` warns if interfaces remain, so drivers must delete virtual interfaces first.

Test signals: PHY register/unregister, open interface blocking unregister, netdev up/down opencount accounting, namespace move success and rollback, repeated unregister events, and module init failure unwinding.
