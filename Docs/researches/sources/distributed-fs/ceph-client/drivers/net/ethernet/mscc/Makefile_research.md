# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/Makefile

## Purpose
This Makefile defines the object composition for the Microsemi Ocelot switch library and the platform Ocelot switch driver.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MSCC_OCELOT_SWITCH_LIB)` builds `mscc_ocelot_switch_lib.o` from common modules including `ocelot.o`, devlink, flower, IO, MAC Merge, policing, PTP, stats, VCAP, and register definitions. `ocelot_mrp.o` is conditionally included when `CONFIG_BRIDGE_MRP` is set. `obj-$(CONFIG_MSCC_OCELOT_SWITCH)` builds `mscc_ocelot.o` from FDMA, netdev, and VSC7514 platform pieces.

## Control Flow
Kbuild links common library objects whenever the library symbol is enabled, then links the platform driver objects when the platform symbol is enabled. Conditional object inclusion keeps MRP support tied to bridge MRP availability.

## State And Persistence
The file has no runtime state. Its persistent effect is the module or built-in object graph for the configured kernel.

## Dependencies And Integration Points
It mirrors the Kconfig split between shared Ocelot hardware library and platform switchdev driver. `ocelot.c` is the core library file for many exported switch operations.

## Risks
Object list drift is the main risk. Adding new exported library functionality without updating `mscc_ocelot_switch_lib-y`, or adding platform-specific code without updating `mscc_ocelot-y`, would produce link or feature gaps.

## Test Signals
Build with the library only, with the platform driver, and with `CONFIG_BRIDGE_MRP` toggled. Confirm expected objects are linked into either built-in archives or modules.
