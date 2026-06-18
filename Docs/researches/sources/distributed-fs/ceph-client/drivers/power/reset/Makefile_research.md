# sources/distributed-fs/ceph-client/drivers/power/reset/Makefile

## Purpose
`drivers/power/reset/Makefile` maps reset/poweroff Kconfig symbols to their driver objects. It is the authoritative build list for the reset subtree.

## Important APIs, Types, and Functions
The file has only `obj-$(CONFIG_...) += ...` assignments. Important mappings include generic `gpio-poweroff.o`, `gpio-restart.o`, `syscon-reboot.o`, `syscon-poweroff.o`, `reboot-mode.o`, `syscon-reboot-mode.o`, `nvmem-reboot-mode.o`, and many platform-specific PMIC/SoC drivers such as AT91, Broadcom, Qualcomm, Renesas, Toradex EC, SpacemiT P1, and QEMU virt control.

## Control Flow
Kbuild evaluates enabled symbols and builds each object as built-in or module according to the symbol type/value. Framework objects such as `reboot-mode.o` are included when their selected symbols resolve to enabled.

## State and Persistence Behavior
No runtime state exists here. Build outputs persist in the kernel build tree.

## Dependencies and Integration Points
It depends on `drivers/power/reset/Kconfig` names staying synchronized with source filenames. It integrates each driver source file with kbuild and module generation.

## Risks and Edge Cases
A mismatched symbol or filename silently drops a driver or breaks builds. Built-in versus module behavior follows the Kconfig symbol, so changing bool/tristate status has direct reset-handler availability implications.

## Test Signals
Validate with `make drivers/power/reset/` under representative configs, allmodconfig, and scripts that compare Kconfig symbols with Makefile entries and source filenames.
