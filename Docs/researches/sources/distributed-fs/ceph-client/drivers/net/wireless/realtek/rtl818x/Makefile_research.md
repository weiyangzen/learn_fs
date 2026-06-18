# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/Makefile

## Purpose

This Makefile dispatches enabled rtl818x family symbols to PCI and USB subdrivers.

## Important APIs, Types, and Functions

`obj-$(CONFIG_RTL8180) += rtl8180/` and `obj-$(CONFIG_RTL8187) += rtl8187/` are the only build directives.

## Control Flow

Kbuild descends into `rtl8180/` for PCI/CardBus support and `rtl8187/` for USB support based on config state.

## State and Persistence Behavior

No runtime state is present; it is a pure kbuild routing file.

## Dependencies and Integration Points

It relies on parent Realtek Makefile selection and child subdirectory Makefiles to build concrete modules.

## Risks and Edge Cases

If both symbols are enabled, both subdirectories build. Any shared headers in `rtl818x/` must remain compatible with both child drivers.

## Test Signals

Build `CONFIG_RTL8180=m`, `CONFIG_RTL8187=m`, and both together to confirm expected modules and no duplicate object names.
