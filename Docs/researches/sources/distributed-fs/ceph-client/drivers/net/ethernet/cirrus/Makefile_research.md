# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Makefile

## Purpose

This Makefile maps Cirrus Ethernet Kconfig symbols to driver objects.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_CS89x0) += cs89x0.o` builds the shared CS89x0 driver object.
- `obj-$(CONFIG_EP93XX_ETH) += ep93xx_eth.o` builds the EP93xx Ethernet driver.
- `obj-$(CONFIG_MAC89x0) += mac89x0.o` builds the Macintosh CS89x0 driver.

## Control Flow

Kbuild includes each object when the corresponding Kconfig symbol is `y` or `m`. The hidden `CONFIG_CS89x0` symbol is selected by ISA/platform CS89x0 options in `Kconfig`.

## State and Persistence Behavior

No runtime state exists. Build inclusion follows configuration state.

## Dependencies and Integration Points

This file integrates with the kernel networking driver build under `drivers/net/ethernet/cirrus` and consumes symbols defined in the adjacent Kconfig.

## Risks and Edge Cases

If a frontend selects `CONFIG_CS89x0`, only `cs89x0.o` is built here; platform-specific behavior must be contained in that source or elsewhere in the directory. New driver symbols require matching object entries.

## Test Signals

Build with each Cirrus option as module and built-in, then verify the expected object is compiled and no disabled driver object appears.
