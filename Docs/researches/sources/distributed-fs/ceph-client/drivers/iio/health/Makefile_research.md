# sources/distributed-fs/ceph-client/drivers/iio/health/Makefile

## Purpose
Kbuild rules for IIO health sensor drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_AFE4403`, `CONFIG_AFE4404`, `CONFIG_MAX30100`, and `CONFIG_MAX30102` to their corresponding objects.

## Control Flow
Kbuild includes each object according to its Kconfig symbol.

## State And Persistence
No runtime state; build outputs persist as built-in objects or modules.

## Dependencies And Integration Points
Must remain aligned with `drivers/iio/health/Kconfig` and source filenames in the health directory.

## Risks
Adding or renaming a health driver requires Kconfig and Makefile updates together.

## Test Signals
Build each symbol as module and built-in; verify resulting module names and object inclusion.
