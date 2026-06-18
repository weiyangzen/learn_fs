# sources/distributed-fs/ceph-client/drivers/w1/slaves/Makefile

## Purpose
Kbuild object list for Dallas/Maxim 1-Wire slave family drivers.

## Important APIs, Types, and Functions
This file maps Kconfig symbols to object files, for example `CONFIG_W1_SLAVE_THERM` to `w1_therm.o`, `CONFIG_W1_SLAVE_DS28E17` to `w1_ds28e17.o`, and similar entries for each listed family driver.

## Control Flow
During kernel build, each `obj-$(CONFIG_...) += file.o` line includes the object when the symbol is built-in or modular. There is no runtime control flow in this file.

## State and Persistence
Build state is determined by `.config`. The output is either built-in code or loadable modules with family aliases supplied by the source files.

## Dependencies and Integration Points
Integrates Kconfig with kbuild and the W1 core family registration model. Each object generally registers one or more `struct w1_family` instances at module init.

## Risks and Test Signals
The main risk is mismatch between Kconfig symbol names and object names, which would silently omit a driver or break builds. Test with targeted module builds and check that every Kconfig symbol in the menu has the expected object entry.
