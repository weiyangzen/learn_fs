# sources/distributed-fs/ceph-client/drivers/staging/octeon/Makefile

## Purpose
Kbuild recipe for the Octeon Ethernet composite object.

## Important APIs, Types, And Functions
Maps `CONFIG_OCTEON_ETHERNET` to `octeon-ethernet.o` and lists component objects: core, MDIO/ethtool, memory pools, RGMII, RX, SGMII, SPI, and TX.

## Control Flow
Kbuild compiles and links the listed objects into one module or built-in driver when enabled.

## State And Persistence
No runtime state. Object ordering is build-time metadata.

## Dependencies And Integration Points
Consumes the `OCTEON_ETHERNET` Kconfig symbol and relies on shared headers in the same directory.

## Risks
The Makefile uses `obj-${CONFIG_OCTEON_ETHERNET}` rather than the more common `obj-$(CONFIG_OCTEON_ETHERNET)` spelling; if not accepted by Kbuild expansion, the driver would not build.

## Test Signals
Build with `CONFIG_OCTEON_ETHERNET=m/y` and verify all listed objects are included in `octeon-ethernet`.
