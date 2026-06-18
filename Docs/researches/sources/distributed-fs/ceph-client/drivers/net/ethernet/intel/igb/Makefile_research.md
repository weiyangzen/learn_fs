# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/Makefile

## Purpose
Defines the kernel build objects for the Intel IGB PCIe Ethernet driver.

## Important APIs, Types, And Functions
The only build target is `obj-$(CONFIG_IGB) += igb.o`. The `igb-y` object list links core driver, ethtool, shared e1000 hardware modules, PTP, hwmon, mailbox, I210 support, and AF_XDP support (`igb_xsk.o`) into `igb.o`.

## Control Flow
There is no runtime control flow. Kbuild includes the object list when `CONFIG_IGB` is enabled.

## State And Persistence
No runtime state. Build state is the ordered object composition of the module.

## Dependencies And Integration
Integrates with Linux Kbuild and the driver source set in the same directory. The object list is important because shared code such as `e1000_82575.o`, `e1000_mac.o`, `e1000_mbx.o`, and `e1000_i210.o` provides function tables and exported helpers consumed by `igb_main.o`.

## Risks
Omitting a required object causes unresolved symbols; adding objects conditionally without matching config guards can break builds. Object order can matter for duplicate definitions and link diagnostics.

## Test Signals
Build `drivers/net/ethernet/intel/igb/` with `CONFIG_IGB=m` and with optional `CONFIG_IGB_HWMON`/XDP-related configs to confirm all referenced objects link.
