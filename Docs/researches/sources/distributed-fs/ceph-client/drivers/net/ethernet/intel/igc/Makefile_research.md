# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/Makefile

## Purpose
This Makefile builds the Intel I225/I226 2.5G Ethernet Controller driver when `CONFIG_IGC` is enabled and optionally includes LED support when `CONFIG_IGC_LEDS` is enabled.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_IGC) += igc.o`, composes `igc-y` from core source files such as `igc_main.o`, `igc_mac.o`, `igc_i225.o`, `igc_base.o`, `igc_nvm.o`, `igc_phy.o`, `igc_diag.o`, `igc_ethtool.o`, `igc_ptp.o`, `igc_dump.o`, `igc_tsn.o`, and `igc_xdp.o`, and conditionally appends `igc_leds.o`.

## Control Flow
Kbuild evaluates the configuration symbols and links the selected objects into the `igc` module or built-in object.

## State And Persistence
No runtime state is stored. The persistent contract is module composition and optional LED object inclusion.

## Dependencies And Integration Points
The object list reflects the driver's subsystems: main PCI/netdev, MAC/NVM/PHY, diagnostics and ethtool, PTP, dump support, TSN, XDP/AF_XDP, and LEDs.

## Risks
Forgetting to list a new implementation file causes unresolved symbols or missing feature code. Conditional LED support must match declarations in `igc.h` and call sites in main driver code.

## Test Signals
Build the driver with `CONFIG_IGC=m/y` and with `CONFIG_IGC_LEDS` both enabled and disabled. Link errors are the primary signal.
