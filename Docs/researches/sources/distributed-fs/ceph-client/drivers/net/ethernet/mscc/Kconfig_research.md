# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Kconfig

## Purpose
This Kconfig file defines Microsemi Ethernet switch support, including the shared Ocelot switch library and the platform Ocelot switch driver.

## Important APIs, Types, And Functions
It declares `NET_VENDOR_MICROSEMI`, `MSCC_OCELOT_SWITCH_LIB`, and `MSCC_OCELOT_SWITCH`. The library is a tristate selected by consumers and selects `NET_DEVLINK`, `REGMAP_MMIO`, `PACKING`, and `PHYLINK`, while depending on optional PTP clock support. The platform switch driver depends on switchdev, bridge compatibility, IOMEM, OF, and PTP optional support, and selects the library plus `GENERIC_PHY`.

## Control Flow
The vendor option gates Microsemi device prompts. `MSCC_OCELOT_SWITCH_LIB` can be selected by switchdev or DSA drivers as common hardware support. `MSCC_OCELOT_SWITCH` exposes the VSC7514 Ocelot SoC switch driver and pulls in the common library.

## State And Persistence
The only persistent state is kernel configuration. There is no runtime state in this file.

## Dependencies And Integration Points
The symbols feed the sibling Makefile, which builds `mscc_ocelot_switch_lib.o` and `mscc_ocelot.o`. The dependency list documents that the full driver expects switchdev, bridge, OF, regmap MMIO, phylink, devlink, generic PHY, and optional PTP.

## Risks
Because `MSCC_OCELOT_SWITCH_LIB` is non-prompted and selected, its dependencies must remain satisfiable for all consumers. Bridge dependency handling allows builds with `BRIDGE=n`, but bridge-enabled runtime features depend on switchdev/bridge integration.

## Test Signals
Build matrix coverage should include `MSCC_OCELOT_SWITCH_LIB=m/y`, `MSCC_OCELOT_SWITCH=m/y`, PTP enabled/disabled, bridge enabled/disabled where legal, and DSA consumers that select the library without the platform driver.
