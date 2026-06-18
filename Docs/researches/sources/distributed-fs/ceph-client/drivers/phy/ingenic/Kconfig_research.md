# sources/distributed-fs/ceph-client/drivers/phy/ingenic/Kconfig

## Purpose
Kconfig entry for Ingenic SoC USB PHY support.

## Important APIs, types, and functions
Defines `PHY_INGENIC_USB`, a tristate symbol for `phy-ingenic-usb.o`.

## Control flow
The symbol is visible on MIPS or `COMPILE_TEST`, requires `USB_SUPPORT` and `HAS_IOMEM`, and selects `GENERIC_PHY`.

## State and persistence
Only build configuration state in `.config`; no runtime state.

## Dependencies and integration points
Feeds the Ingenic PHY Makefile and kernel config dependency graph.

## Risks and test signals
Risk is dependency drift if the driver gains new required subsystems. Test `COMPILE_TEST`, MIPS defconfigs, and module/built-in builds.
