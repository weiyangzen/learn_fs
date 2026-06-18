# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.h

## Purpose

This header provides conditional wrappers and declarations for the Realtek MDIO transport driver, allowing chip drivers to compile regardless of whether MDIO interface support is enabled.

## Important APIs, Types, and Functions

- When `CONFIG_NET_DSA_REALTEK_MDIO` is enabled, `realtek_mdio_driver_register()` and `_unregister()` wrap `mdio_driver_register()` and `mdio_driver_unregister()`, and probe/remove/shutdown are declared.
- When disabled, registration is a no-op success, probe returns `-ENOENT`, and remove/shutdown are empty stubs.

## Control Flow

There is no runtime flow in the enabled case beyond inline wrapper calls. In disabled builds, chip-driver init can call the wrapper and continue without registering an MDIO driver.

## State and Persistence

No state is introduced. The enabled path affects global MDIO driver registration through the MDIO core; the disabled path does nothing.

## Dependencies and Integration Points

The header integrates chip drivers with the MDIO core and Kconfig-controlled transport availability. It expects `struct mdio_driver` and `struct mdio_device` declarations from included kernel headers in compilation units.

## Risks and Edge Cases

Returning success from disabled registration wrappers means callers must not interpret that as an MDIO transport being available. Probe's `-ENOENT` stub is useful if referenced directly, but normal disabled builds should not bind MDIO devices.

## Test Signals

Compile chip drivers with MDIO support enabled and disabled. Enabled builds should register and unregister an MDIO driver; disabled builds should link through stubs without unresolved symbols.
