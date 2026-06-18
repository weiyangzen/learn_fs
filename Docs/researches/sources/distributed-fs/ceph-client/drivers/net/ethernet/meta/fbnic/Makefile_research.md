# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/Makefile

## Purpose

`meta/fbnic/Makefile` defines the fbnic module object composition for the Meta Host Network Interface driver.

## Important APIs, Types, And Functions

`obj-$(CONFIG_FBNIC) += fbnic.o` creates the driver object or module. `fbnic-y` lists component objects: CSR access/tests, debugfs, devlink, ethtool, firmware, firmware log, hardware stats, hwmon, IRQ, MAC, netdev, PCI, phylink, RPC, MDIO, time/PTP, TLV, and TX/RX logic.

## Control Flow

Kbuild links the listed `fbnic-y` objects into `fbnic.o` when `CONFIG_FBNIC` is enabled. The ordering mostly follows subsystem dependencies, with low-level CSR and support code listed before bus/netdev data-path pieces.

## State And Persistence

There is no runtime state in the Makefile. Build output persists as a built-in object or module artifact according to kernel configuration.

## Dependencies And Integration Points

The object list maps directly to driver subsystem files and must stay synchronized with declarations in `fbnic.h` and related headers. It integrates with the parent `meta/Makefile`.

## Risks And Edge Cases

Missing a required object produces unresolved symbols; keeping an obsolete object produces build failures. The trailing continuation before the comment must remain syntactically valid for kbuild.

## Test Signals

Build tests for built-in and module configurations are the main signal. Linker errors indicate missing object membership or stale prototypes. No local executable tests were run for this research item.
