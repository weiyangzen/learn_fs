# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/Makefile

## Purpose

This Makefile builds the RTL8180/8185/8187SE PCI module object composition.

## Important APIs, Types, and Functions

`rtl818x_pci-objs` links `dev.o`, RF front ends (`rtl8225.o`, `sa2400.o`, `max2820.o`, `grf5101.o`, `rtl8225se.o`), and `obj-$(CONFIG_RTL8180) += rtl818x_pci.o`. `ccflags-y += -I $(src)/..` exposes shared rtl818x headers.

## Control Flow

When `CONFIG_RTL8180` is enabled, kbuild compiles all listed objects into the `rtl818x_pci` module/built-in object. RF implementations are linked unconditionally because `dev.c` chooses the correct `rtl818x_rf_ops` at probe time.

## State and Persistence Behavior

There is no runtime state. Build state is derived from config and object timestamps.

## Dependencies and Integration Points

The module integrates the PCI driver core with all supported RF front-end implementations and shared register definitions one directory up.

## Risks and Edge Cases

Removing an RF object can break devices whose EEPROM RF type selects that frontend even if other devices still build. The include path must remain aligned with shared `rtl818x.h` placement.

## Test Signals

Build `rtl818x_pci` as module and built-in, verify all RF object symbols resolve, and probe cards for RF types 3, 4, 5, and 9.
