# sources/distributed-fs/ceph-client/include/linux/phy_fixed.h

## Purpose
Fixed-link PHY interface for network devices without a dynamic external PHY, such as switch CPU ports or board-wired links.

## Important APIs, Types, and Functions
Defines `struct fixed_phy_status` with speed, duplex, link, pause, and asymmetric pause. When `CONFIG_FIXED_PHY` is enabled, declares `fixed_phy_change_carrier()`, `fixed_phy_register()`, `fixed_phy_register_100fd()`, `fixed_phy_unregister()`, and `fixed_phy_set_link_update()`. Disabled builds return `ERR_PTR(-ENODEV)` for registration and no-op unregister.

## Control Flow
Drivers register a fixed PHY with static status or a default 100/full-duplex helper, optionally install a link-update callback, change carrier state, and unregister during teardown.

## State and Persistence
Fixed PHY state persists in the registered `phy_device` and status/callback managed by the fixed PHY implementation.

## Dependencies and Integration Points
Integrates with PHYLIB, netdevice carrier state, device-tree fixed-link descriptions, and MAC drivers that use PHY APIs without MDIO hardware.

## Risks
Static link parameters can diverge from actual board wiring. Disabled config stubs require callers to handle `-ENODEV`.

## Test Signals
Fixed-link MAC probe tests, carrier change tests, device-tree fixed-link parsing, and disabled-config build tests.
