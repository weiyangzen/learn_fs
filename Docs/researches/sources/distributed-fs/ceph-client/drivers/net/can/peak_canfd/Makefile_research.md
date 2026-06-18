# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Makefile

## Purpose
This Makefile builds the PEAK PCIe CAN FD driver as a composite module/object.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_PEAK_PCIEFD) += peak_pciefd.o` defines the final target.
- `peak_pciefd-y := peak_pciefd_main.o peak_canfd.o` links PCIe board support with common PEAK uCAN CAN FD logic.

## Control Flow
Kbuild composes both object files into `peak_pciefd` when the Kconfig symbol is enabled.

## State And Persistence
No runtime state is defined here.

## Dependencies And Integration Points
The composition allows `peak_pciefd_main.c` to call common functions from `peak_canfd.c` without exporting a separate module.

## Risks And Edge Cases
If another PEAK bus wrapper is added, common `peak_canfd.o` may need to move to a separate library object or be linked into multiple modules carefully.

## Test Signals
Build `CONFIG_CAN_PEAK_PCIEFD=y` and `m`, and inspect that the final module contains both common and PCIe symbols.
