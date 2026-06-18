# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Kconfig

## Purpose
This Kconfig file enables the PEAK-System PCAN-PCIe FD family driver.

## Important APIs, Types, And Functions
- `CAN_PEAK_PCIEFD` is a PCI-dependent tristate.
- The help text documents PEAK PCIe FD cards with one or two CAN FD channels, CAN 2.0 A/B, CAN FD data bitrates up to 12 Mbit/s, galvanic isolation, and industrial temperature range.

## Control Flow
When selected, Kbuild links the PEAK CAN FD common uCAN logic with the PCIe FD board driver.

## State And Persistence
Only build configuration state is represented.

## Dependencies And Integration Points
The only explicit dependency is `PCI`; runtime integration also depends on SocketCAN and the common PEAK uCAN header in `include/linux/can/dev/peak_canfd.h`.

## Risks And Edge Cases
- The help text mentions one or two channels, while the PCIe main driver derives one to four channels from subsystem IDs.
- No explicit dependency on CAN FD core support is listed here, so it relies on surrounding CAN driver menu dependencies.

## Test Signals
Check Kconfig visibility under PCI and build the module for allmodconfig and PCI-disabled configs.
