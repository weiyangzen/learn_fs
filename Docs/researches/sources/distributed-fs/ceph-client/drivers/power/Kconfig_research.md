# sources/distributed-fs/ceph-client/drivers/power/Kconfig

## Purpose
`drivers/power/Kconfig` is the top-level power-driver Kconfig include point. It pulls in the power-supply, reset/poweroff, sequencing, and supply-class submenus so platform power management drivers are visible from the parent kernel configuration menu.

## Important APIs, Types, and Functions
It has no C APIs. The important declarations are four `source` statements for `drivers/power/supply/Kconfig`, `drivers/power/reset/Kconfig`, `drivers/power/sequencing/Kconfig`, and `drivers/power/supply/adapters/Kconfig`.

## Control Flow
Kconfig processing reads this file when the driver tree is configured and expands the referenced menus in order. Symbol definitions live in the included files; this file only controls menu reachability and ordering.

## State and Persistence Behavior
There is no runtime state. Configuration state persists in generated kernel config files through symbols declared in the included Kconfig fragments.

## Dependencies and Integration Points
It depends on the kernel Kconfig language and the relative layout of the `drivers/power` subtree. It integrates build-time configuration for power supply class drivers, board reset/poweroff drivers, and the power-sequencing framework.

## Risks and Edge Cases
Broken paths or reordered includes can hide entire driver families from configuration. Since it contains only includes, semantic risk is low but blast radius is high if a source line is deleted.

## Test Signals
Run `make menuconfig`/`olddefconfig` with representative architectures and verify power supply, reset, sequencing, and adapter symbols are reachable. Kconfig lint or allmodconfig builds catch missing sourced files.
