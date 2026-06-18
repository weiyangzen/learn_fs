# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Makefile

## Purpose
This Makefile maps Wangxun Ethernet Kconfig symbols to subdirectories for the common library, physical-function drivers, and virtual-function drivers.

## Important APIs, types, and functions
The build rules are `obj-$(CONFIG_LIBWX) += libwx/`, `obj-$(CONFIG_TXGBE) += txgbe/`, `obj-$(CONFIG_TXGBEVF) += txgbevf/`, `obj-$(CONFIG_NGBE) += ngbe/`, and `obj-$(CONFIG_NGBEVF) += ngbevf/`.

## Control flow and integration
Kbuild descends into a subdirectory only when the corresponding symbol is enabled. Because device Kconfig entries select `LIBWX`, the common library directory should be built whenever any dependent Wangxun driver is enabled.

## State and persistence behavior
No runtime state exists. The file contributes build graph state only.

## Dependencies and integration points
It integrates with subdirectory Makefiles and the Kconfig symbols defined in `wangxun/Kconfig`.

## Risks and edge cases
The main risk is missing the `libwx/` descent for a driver that uses common objects, or stale directory names if drivers are renamed.

## Test signals
Build each Wangxun config symbol independently and confirm the expected directory is visited. For selected device drivers, confirm `libwx/` is also included through `CONFIG_LIBWX`.
