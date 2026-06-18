# sources/distributed-fs/ceph-client/drivers/thermal/testing/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/Makefile` builds the thermal core testing facility. The source was read as a complete 7-line file.

## Important APIs, Types, and Functions

The Makefile creates `thermal-testing.o` when `CONFIG_THERMAL_CORE_TESTING` is enabled. The composite object contains `command.o` and `zone.o`.

## Control Flow

There is no runtime flow here. Kbuild uses the config symbol to include or omit the debugfs testing module.

## State and Persistence Behavior

The file only affects build outputs. Runtime testing state is implemented by `command.c` and `zone.c`.

## Dependencies and Integration Points

It integrates `drivers/thermal/testing` into the kernel thermal build and depends on the Kconfig symbol being defined elsewhere.

## Risks and Edge Cases

If new testing source files are added without updating `thermal-testing-y`, module functionality will be incomplete. If the Kconfig symbol is enabled without debugfs support, the C files must still compile according to their own dependencies.

## Test Signals

Build `CONFIG_THERMAL_CORE_TESTING=m/y` and confirm the resulting object contains symbols from both command and zone handling.
