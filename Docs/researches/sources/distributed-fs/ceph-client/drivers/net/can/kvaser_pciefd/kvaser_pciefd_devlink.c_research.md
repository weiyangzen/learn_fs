# sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_devlink.c

## Purpose
This file provides the devlink integration for the Kvaser PCIe FD driver. It reports firmware version information and binds each SocketCAN netdev to a physical devlink port.

## Important APIs, Types, And Functions
- `kvaser_pciefd_devlink_info_get()` reads `struct kvaser_pciefd::fw_version` and reports `DEVLINK_INFO_VERSION_GENERIC_FW` when a nonzero major version exists.
- `kvaser_pciefd_devlink_ops` exposes `.info_get`.
- `kvaser_pciefd_devlink_port_register()` initializes `devlink_port_attrs` with `DEVLINK_PORT_FLAVOUR_PHYSICAL`, registers the port at the CAN device `dev_port`, and attaches it to the netdev with `SET_NETDEV_DEVLINK_PORT()`.
- `kvaser_pciefd_devlink_port_unregister()` unregisters the previously registered port.

## Control Flow
Core probe allocates the devlink object before hardware setup. Once each channel netdev is allocated and populated, `kvaser_pciefd_devlink_port_register()` is called before candev registration. After all netdevs are registered, the core registers devlink. Removal unregisters each per-channel devlink port before freeing its candev, then unregisters and frees the devlink object.

## State And Persistence
The only state owned here is the `devlink_port` embedded in `struct kvaser_pciefd_can`. Firmware version fields are populated in the core file from system ID registers and are only reported through devlink. There is no persistent storage.

## Dependencies And Integration Points
The file depends on `<net/devlink.h>`, netdevice helpers, and Kvaser private structures from `kvaser_pciefd.h`. It is tightly coupled to the core file: core owns the devlink allocation and channel lifetime, while this file owns port registration and version reporting policy.

## Risks And Edge Cases
- Firmware version reporting is suppressed when major version is zero, which may hide valid `0.x.y` firmware if such versions exist.
- The version buffer is sized for `xxx.xxx.xxxxx`; larger field widths would truncate via `snprintf()`, though source fields are small integer types.
- Port registration failure aborts channel setup; the core path must free any candevs already allocated and unregister any ports already registered.

## Test Signals
Check `devlink dev info` for firmware version after probe, `devlink port show` for one physical port per CAN channel, netdev-to-devlink port association, and remove/reprobe without stale devlink ports.
