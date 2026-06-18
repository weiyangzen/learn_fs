# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/Makefile

## Purpose
This Makefile defines the object composition for the legacy `sfc-falcon` driver module or built-in object.

## Important APIs, Types, and Functions
`sfc-falcon-y` aggregates core objects: `efx.o`, NIC/FArch/Falcon hardware support, TX/RX, self-test, ethtool, PHY/MDIO drivers, and board support. `sfc-falcon-$(CONFIG_SFC_FALCON_MTD)` conditionally adds `mtd.o`. `obj-$(CONFIG_SFC_FALCON)` emits the final `sfc-falcon.o` target.

## Control Flow
Kbuild evaluates the config variables and includes the listed object files in link order. The main entry point comes from `efx.o`, while the remaining objects provide hardware, PHY, queue, self-test, ethtool, and optional flash support referenced by the core driver.

## State and Persistence
No runtime state is stored here. It controls which compiled objects are present in the final kernel/module image.

## Dependencies and Integration Points
This file is coupled to `falcon/Kconfig` symbols and to the local source files named in `sfc-falcon-y`. It also relies on the kernel module build system's composite object convention.

## Risks
Removing or renaming an object without updating this file breaks the build. Link-order-sensitive initialization bugs are possible if objects provide tables or symbols expected by `efx.o` and hardware-specific files. Optional MTD code must remain fully guarded because it disappears when `CONFIG_SFC_FALCON_MTD` is unset.

## Test Signals
The direct signal is `make drivers/net/ethernet/sfc/falcon/` under configurations with and without `CONFIG_SFC_FALCON_MTD`. `modinfo sfc-falcon` or built-in symbol inspection should confirm the expected module/object composition.
