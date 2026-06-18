# sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Makefile

## Purpose

This Makefile builds the IDT NTB hardware driver object when selected.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB_IDT) += ntb_hw_idt.o` maps the IDT Kconfig symbol to its driver object.

## Control flow and state behavior

There is no runtime behavior.

## Dependencies and integration points

It pairs with `idt/Kconfig` and the IDT hardware driver source, which is outside this specific work-item list.

## Risks and edge cases

The Makefile assumes the selected object exists in the same directory and that `CONFIG_NTB_IDT` dependencies are complete in Kconfig.

## Test signals

Build with `CONFIG_NTB_IDT=m` or `y` and verify `ntb_hw_idt` is produced and linked with any required HWMON dependencies.
