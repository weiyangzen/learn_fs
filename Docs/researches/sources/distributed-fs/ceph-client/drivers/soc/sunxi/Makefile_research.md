# sources/distributed-fs/ceph-client/drivers/soc/sunxi/Makefile

## Purpose

This Makefile connects sunXi Kconfig symbols to driver objects.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SUNXI_MBUS) += sunxi_mbus.o` and `obj-$(CONFIG_SUNXI_SRAM) += sunxi_sram.o` are the only build rules.

## Control Flow

Kbuild includes the two objects when their bool symbols are enabled.

## State and Persistence Behavior

There is no runtime state.

## Dependencies and Integration Points

It depends on the symbols defined in `Kconfig` and integrates with the parent `drivers/soc` build.

## Risks and Edge Cases

Object names must track source filenames. Since both symbols are bool, these drivers are built-in rather than modules in normal configurations.

## Test Signals

Build with each symbol enabled and disabled and confirm object inclusion.
