# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Makefile

## Purpose

This Makefile builds the AMD NTB hardware driver object when selected.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB_AMD) += ntb_hw_amd.o` maps the Kconfig symbol to the driver source.

## Control flow and state behavior

There is no runtime behavior.

## Dependencies and integration points

It pairs with `amd/Kconfig` and the source/header files `ntb_hw_amd.c` and `ntb_hw_amd.h`.

## Risks and edge cases

If the object name changes or multi-object composition is introduced, this Makefile must be updated. Otherwise the AMD option will not link the expected driver.

## Test signals

Build with `CONFIG_NTB_AMD=m` or `y` and confirm `ntb_hw_amd` is produced.
