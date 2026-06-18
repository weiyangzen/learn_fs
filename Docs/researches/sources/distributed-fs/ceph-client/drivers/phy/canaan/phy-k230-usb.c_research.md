# sources/distributed-fs/ceph-client/drivers/phy/canaan/phy-k230-usb.c

## Purpose
This driver exposes two Canaan Kendryte K230 USB 2.0 PHY instances backed by shared HiSysConfig MMIO registers. It programs fixed analog tuning and pull-up/pull-down state on power-on.

## Important APIs, types, and functions
`struct k230_usb_phy_global` owns the mapped base and two `struct k230_usb_phy_instance` records. `k230_usb_phy_power_on()` writes `K230_PHY_CTL0_VAL` and `K230_PHY_CTL1_VAL`, sets ID pull-up, and conditionally sets DM/DP pull-downs for instance 1. `k230_usb_phy_power_off()` clears DM/DP pull-downs. `k230_usb_phy_xlate()` selects a PHY by phandle argument index. Probe maps resource 0, creates two PHYs, and registers the provider.

## Control flow
Probe creates static USB0/USB1 offset mappings, initializes per-instance state, creates each Generic PHY, and registers a custom xlate provider. Power-on applies fixed control-register settings and updates `TEST_CTL3`; power-off partially unwinds pull-down state.

## State and persistence behavior
Software state is the mapped base plus per-instance offsets. Hardware register writes persist after power-on. Power-off does not clear ID pull-up or restore control registers. There is no clock, reset, runtime PM, or suspend/resume handling.

## Dependencies and integration points
The driver uses platform MMIO, OF compatible `canaan,k230-usb-phy`, Generic PHY, and bitfield helpers. It is selected by `CONFIG_PHY_CANAAN_USB`.

## Risks and test signals
`k230_usb_phy_xlate()` assumes a phandle argument exists. Tuning values and asymmetric pull-down behavior are hard-coded. Test both indexes, invalid indexes, USB enumeration on both ports, repeated power cycles, and compile-test coverage.
