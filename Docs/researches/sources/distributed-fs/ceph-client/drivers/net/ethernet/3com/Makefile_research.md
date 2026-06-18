# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Makefile

## Purpose
This Makefile maps 3Com Ethernet Kconfig selections to compiled driver objects.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_VORTEX) += 3c59x.o` includes the Vortex/Boomerang-family driver.
- `obj-$(CONFIG_TYPHOON) += typhoon.o` includes the Typhoon-family driver.

## Control Flow
Kbuild expands each line into built-in or module object lists depending on each tristate symbol.

## State and Persistence
There is no runtime state. The persistent effect is the build artifact set produced from `.config`.

## Dependencies and Integration Points
The file depends on symbols defined by the neighboring Kconfig and integrates with the parent kernel build.

## Risks and Edge Cases
Symbol/object mismatches would omit a selected driver. New 3Com drivers need matching Kconfig and Makefile entries.

## Test Signals
Build with `CONFIG_VORTEX` and `CONFIG_TYPHOON` as `y`, `m`, and unset, and verify expected objects/modules.
