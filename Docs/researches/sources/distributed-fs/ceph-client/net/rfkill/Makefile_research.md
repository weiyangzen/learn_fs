# sources/distributed-fs/ceph-client/net/rfkill/Makefile

## Purpose
Maps RFKILL Kconfig symbols to object files for the core rfkill module and GPIO driver.

## Important APIs, Types, and Functions
Builds `rfkill-y += core.o`, conditionally adds `input.o` through `rfkill-$(CONFIG_RFKILL_INPUT)`, builds the aggregate `rfkill.o` for `CONFIG_RFKILL`, and builds `rfkill-gpio.o` for `CONFIG_RFKILL_GPIO`.

## Control Flow
The kernel build system links `core.o` and optional `input.o` into the rfkill module or built-in object. The GPIO platform driver is independent and only built when selected.

## State and Persistence
No runtime state; the file defines build artifacts.

## Dependencies and Integration
Integrates with Kbuild and the symbols declared in `Kconfig`. It ensures input support is part of the core rfkill object rather than a separate module.

## Risks and Test Signals
Risks are limited to build omissions when object lists fall out of sync with source or Kconfig. Test signals are successful builds for `RFKILL=y/m`, `RFKILL_INPUT=y/n`, and `RFKILL_GPIO=y/m`.
