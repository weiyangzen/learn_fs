# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Kconfig

## Purpose
Kconfig menu entries for Broadcom thermal drivers under `drivers/thermal/broadcom`. It declares build-time options for Raspberry Pi/BCM283x sensors, Broadcom STB AVS TMON, Northstar, and Stingray thermal blocks.

## Important APIs, Types, and Functions
This file has no C APIs. The important symbols are `BCM2711_THERMAL`, `BCM2835_THERMAL`, `BRCMSTB_THERMAL`, `BCM_NS_THERMAL`, and `BCM_SR_THERMAL`.

## Control Flow
Configuration dependencies decide which objects the Makefile builds. BCM2711 depends on `THERMAL_OF` and `MFD_SYSCON`; BCM2835 depends on `HAS_IOMEM` and `THERMAL_OF`; Broadcom STB and iProc-family drivers can be enabled for compile testing. Northstar and Stingray default on for `ARCH_BCM_IPROC`.

## State and Persistence
No runtime state exists. The selected config symbols persist only in the kernel build configuration.

## Dependencies and Integration Points
The symbols integrate with the local Makefile and broader thermal, OF, syscon, and architecture configuration menus. `COMPILE_TEST` broadens build coverage.

## Risks and Edge Cases
Incorrect dependencies can allow unusable drivers to be built or hide valid build targets. `default y if ARCH_BCM_IPROC` and `default ARCH_BCM_IPROC` have subtly different expressions but both bias iProc platforms toward including those drivers.

## Test Signals
Kconfig lint, allmodconfig/allyesconfig, and architecture-specific build matrices should verify that each selected symbol pulls only valid dependencies and builds the matching object.
