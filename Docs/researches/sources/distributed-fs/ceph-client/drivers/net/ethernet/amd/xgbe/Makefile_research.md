# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/Makefile

## Purpose
This Makefile defines the Kbuild composition for the AMD XGBE Ethernet driver. It builds `amd-xgbe.o` when `CONFIG_AMD_XGBE` is enabled and conditionally includes PCI, DCB, and debugfs support objects based on their Kconfig symbols.

## Important APIs, Types, And Functions
There are no runtime APIs in this Makefile. Build variables are `obj-$(CONFIG_AMD_XGBE) += amd-xgbe.o`, `amd-xgbe-objs := ...` for the core object list, and conditional object additions `amd-xgbe-$(CONFIG_PCI)`, `amd-xgbe-$(CONFIG_AMD_XGBE_DCB)`, and `amd-xgbe-$(CONFIG_DEBUG_FS)`.

## Control Flow
Kbuild links the fixed object list into `amd-xgbe.o`: main driver, netdev operations, hardware operations, descriptors, ethtool, MDIO, hardware timestamping, PTP/PPS, I2C, two PHY variants, platform support, and self-test. If PCI support is enabled, `xgbe-pci.o` is included. If AMD XGBE DCB support is enabled, `xgbe-dcb.o` is included. If debugfs is enabled, `xgbe-debugfs.o` is included.

## State And Persistence
The file has no runtime state. Its persistent role is the source-to-object build contract for XGBE. Configuration symbols determine which feature code is compiled into the driver.

## Dependencies And Integration Points
It integrates with Kbuild and Kconfig symbols `CONFIG_AMD_XGBE`, `CONFIG_PCI`, `CONFIG_AMD_XGBE_DCB`, and `CONFIG_DEBUG_FS`. Runtime integration for the listed objects includes netdev, MDIO, PTP, I2C, platform, PCI, DCB, debugfs, and self-test subsystems, but those are implemented in the referenced source files rather than in this Makefile.

## Risks
Incorrect object membership can cause missing symbols, disabled features, or dead code in certain configurations. Conditional objects must stay aligned with preprocessor/Kconfig guards in the source. Since self-test is always in the base object list, build breakage in self-test affects all XGBE builds.

## Test Signals
Run build matrix checks with `CONFIG_AMD_XGBE` built-in and modular, with PCI on/off where supported, `CONFIG_AMD_XGBE_DCB` on/off, and `CONFIG_DEBUG_FS` on/off. Link checks should confirm optional symbols appear only under the right configurations.
