# sources/distributed-fs/ceph-client/drivers/extcon/Makefile

## Purpose
The extcon Makefile maps extcon Kconfig symbols to core and provider objects.

## Important APIs, types, and functions
It builds `extcon-core.o` from `extcon.o` and `devres.o` when `CONFIG_EXTCON` is enabled, and adds one object per provider, including all files covered by this work item.

## Control flow
Kbuild includes the core for `CONFIG_EXTCON` and appends provider objects according to their `CONFIG_EXTCON_*` symbols. There is no runtime logic.

## State and persistence behavior
This is build-time-only state.

## Dependencies and integration points
It integrates the extcon core with platform, I2C, GPIO, PMIC, USB, and Type-C provider drivers selected in Kconfig.

## Risks and edge cases
Object names must stay aligned with source files and Kconfig symbols. Missing core object composition would break exported devres/provider APIs. Adding a new driver requires both Kconfig and Makefile entries.

## Test signals
Build each provider symbol as `y` and `m`, verify `extcon-core.o` includes both `extcon.o` and `devres.o`, and run allmodconfig/allnoconfig compile coverage.
