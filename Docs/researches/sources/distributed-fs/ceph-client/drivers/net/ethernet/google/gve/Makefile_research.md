# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/Makefile

## Purpose
Defines the object composition of the Google Virtual Ethernet driver module/built-in object.

## APIs and Build Semantics
`obj-$(CONFIG_GVE) += gve.o` creates the final driver object. `gve-y` includes core, GQI and DQO Tx/Rx paths, ethtool, admin queue, utilities, flow rules, and DQO buffer management. `gve-$(CONFIG_PTP_1588_CLOCK) += gve_ptp.o` conditionally adds PTP support.

## Control Flow and Integration
The Kbuild object list aligns with declarations in `gve.h`: adminq, ethtool, flow rule, buffer management, PTP, and both queue formats are compiled together into one driver.

## State and Persistence
No runtime state. Build-time state determines whether timestamp/clock code is linked.

## Dependencies, Risks, and Tests
Risks include missing object files for prototypes declared in `gve.h`, or building PTP references without `gve_ptp.o`. Test signals include modular and built-in builds, `CONFIG_PTP_1588_CLOCK=y/m/n`, and link checks for all exported symbols declared in `gve.h`.
