# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Makefile

## Purpose
This Makefile builds p54 common and bus-specific modules.

## Important APIs, Types, and Functions
- `p54common-objs := eeprom.o fwio.o txrx.o main.o` defines common functionality.
- `p54common-$(CONFIG_P54_LEDS) += led.o` conditionally adds LED support.
- `obj-$(CONFIG_P54_COMMON) += p54common.o`.
- `obj-$(CONFIG_P54_USB) += p54usb.o`, `obj-$(CONFIG_P54_PCI) += p54pci.o`, and `obj-$(CONFIG_P54_SPI) += p54spi.o`.

## Control Flow
kbuild links common source objects into `p54common` and separately builds selected bus modules. The bus modules depend on exported common symbols at runtime.

## State and Persistence Behavior
No runtime state is owned. The Makefile determines which object files exist in the build.

## Dependencies and Integration Points
It integrates p54 common code with USB/PCI/SPI frontends and the optional LED object.

## Risks and Edge Cases
Forgetting to include a common object can cause unresolved exports or missing mac80211 behavior. Conditional LED linkage must match `CONFIG_P54_LEDS` usage in `p54.h` and `main.c`.

## Test Signals
Successful module/built-in builds for all enabled combinations and absence of unresolved symbols are the main signals.
