# sources/distributed-fs/ceph-client/net/6lowpan/core.c

## Purpose
`net/6lowpan/core.c` provides core registration and lifecycle glue for 6LoWPAN netdevices. It initializes per-device 6LoWPAN properties, registers notifier handling for link-local addressing and context reset, and initializes global debugfs and NHC autoload requests.

## Important APIs, types, and functions
Exported functions are `lowpan_register_netdevice()`, `lowpan_register_netdev()`, `lowpan_unregister_netdevice()`, `lowpan_unregister_netdev()`, and `addrconf_ifid_802154_6lowpan()`. The file also defines `lowpan_event()` as a netdevice notifier, `lowpan_notifier`, `lowpan_module_init()`, and `lowpan_module_exit()`.

## Control flow
Registration sets `addr_len` based on link-layer type, sets `ARPHRD_6LOWPAN`, clamps MTU to `IPV6_MIN_MTU`, initializes the IPHC context table ids and lock, installs 6LoWPAN neighbor discovery ops, registers the netdevice, and creates per-device debugfs. `lowpan_register_netdev()` wraps that in RTNL locking; unregister wrappers mirror it. The notifier adds an IEEE802154 short-address link-local address on `NETDEV_UP` or `NETDEV_CHANGE`, and clears active IPHC context flags on `NETDEV_DOWN`. Module init creates debugfs, registers the notifier, and asynchronously requests common NHC modules.

## State and persistence
State is per netdevice: link-layer type, IPHC context table ids/flags, neighbor discovery ops, debugfs dentries, and auto-configured link-local IPv6 addresses. Context active bits are volatile and cleared on device down.

## Dependencies and integration points
The file integrates with netdevice registration/RTNL, IPv6 addrconf, IEEE802154 address helpers, 6LoWPAN debugfs, neighbor discovery ops from `ndisc.c`, and NHC compression modules.

## Risks and invariants
`lowpan_unregister_netdevice()` calls `unregister_netdevice()` before debugfs cleanup, so debugfs users must not outlive device teardown unsafely. `addrconf_ifid_802154_6lowpan()` rejects invalid/all-zero short addressing and constructs the RFC-derived IID; mistakes here affect SLAAC. Context reset on `NETDEV_DOWN` avoids stale compression contexts.

## Test signals
Register/unregister IEEE802154 and BTLE 6LoWPAN devices, verify MTU/type/address length, check link-local address creation for valid short addresses, ensure context flags clear on down/up cycles, and verify debugfs directories are created/removed.
