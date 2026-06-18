# sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Makefile

## Purpose

This Makefile builds the EPF NTB host driver object when selected.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB_EPF) += ntb_hw_epf.o` maps the EPF Kconfig symbol to the driver object.

## Control flow and state behavior

There is no runtime behavior.

## Dependencies and integration points

It pairs with `epf/Kconfig` and `ntb_hw_epf.c`.

## Risks and edge cases

Any source rename or multi-object split must update this file to keep the selected Kconfig symbol linked correctly.

## Test signals

Build with `CONFIG_NTB_EPF=m` or `y` and verify `ntb_hw_epf` is produced.
