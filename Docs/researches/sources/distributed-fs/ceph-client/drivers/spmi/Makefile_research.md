# sources/distributed-fs/ceph-client/drivers/spmi/Makefile

## Purpose

`drivers/spmi/Makefile` maps SPMI Kconfig symbols to the common framework, devres helper, and platform controller object files.

## Important APIs, Types, And Functions

The file builds `spmi.o` and `spmi-devres.o` when `CONFIG_SPMI` is enabled. It conditionally builds `spmi-apple-controller.o`, `hisi-spmi-controller.o`, `spmi-pmic-arb.o`, and `spmi-mtk-pmif.o` from the vendor-specific symbols.

## Control Flow And State

There is no runtime control flow. Kbuild uses the `obj-$(CONFIG_...)` assignments to include objects built-in or as modules according to the tristate state of each symbol.

## State And Persistence Behavior

Build output changes according to `.config`; the Makefile itself stores no runtime state. Because `spmi-devres.o` follows `CONFIG_SPMI`, managed allocation/add APIs are available whenever the framework is built.

## Dependencies And Integration Points

This file integrates with `drivers/spmi/Kconfig` and the kernel build system. It also implies that vendor drivers depend on the common SPMI framework either directly through `CONFIG_SPMI` visibility or through the menu hierarchy.

## Risks And Test Signals

Risks are missing object mappings after adding a Kconfig symbol, accidentally building helper code without the framework, or stale object names after file renames. Test signals are Kbuild coverage for each SPMI tristate as built-in and module, and module alias/probe checks for the selected platform drivers.
