# sources/distributed-fs/ceph-client/net/ieee802154/sysfs.c

## Purpose
`sysfs.c` defines the sysfs device class for IEEE 802.15.4 PHY objects. It exposes a small set of read-only PHY attributes and wires class-level lifetime and power-management callbacks into cfg802154 registered devices.

## Important APIs, types, and functions
The exported class object is `wpan_phy_class`. `wpan_phy_sysfs_init()` registers it with `class_register()`, and `wpan_phy_sysfs_exit()` unregisters it. `dev_to_rdev()` maps a `struct device` back to `struct cfg802154_registered_device`. Attribute helpers define read-only `index` and `name` sysfs files. `wpan_phy_release()` frees devices through `cfg802154_dev_free()`. Under `CONFIG_PM_SLEEP`, `wpan_phy_suspend()` and `wpan_phy_resume()` delegate to `rdev_suspend()` and `rdev_resume()`.

## Control flow
Class registration installs the class name `ieee802154`, the release callback, the `pmib` attribute group, and optional PM ops. Sysfs reads resolve the class device to `cfg802154_registered_device` and format the PHY index or device name. Suspend/resume callbacks check whether the driver implements the relevant cfg802154 op, take RTNL, call the rdev wrapper, and release RTNL.

## State and persistence
The file does not create durable state. It exposes live kernel state from `wpan_phy_idx` and `wpan_phy.dev`, and class registration persists only until subsystem exit. Device memory is released when the class device refcount reaches zero.

## Dependencies and integration points
It depends on Linux driver core classes, sysfs device attributes, cfg802154 registered-device layout, RTNL locking, and cfg802154 rdev operation wrappers. It is included by the IEEE802154 core initialization path that creates and tears down PHY support.

## Risks and invariants
`dev_to_rdev()` relies on `wpan_phy.dev` being embedded in `cfg802154_registered_device`; layout changes must update the helper. PM callbacks must run under RTNL because cfg802154 device state and network devices may be touched by driver callbacks. Attribute formatting uses `sprintf()` into sysfs-provided buffers and assumes values are small.

## Test signals
Boot or module-load tests should show an `ieee802154` class. Registering a WPAN PHY should create `index` and `name` attributes with expected values. Suspend/resume tests should verify rdev callbacks are called under RTNL and that absent callbacks return success. Device teardown should free the registered device without leaks.
