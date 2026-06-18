# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/Kconfig

## Purpose
This Kconfig file defines the Toshiba Ethernet vendor menu and the selectable Toshiba/PS3 network drivers under it. It gates Toshiba driver visibility through `NET_VENDOR_TOSHIBA` and exposes symbols for the PS3 Gelic Ethernet driver, optional PS3 wireless support, and the Toshiba TC35815 PCI Ethernet driver.

## Important APIs, Types, And Functions
The configuration symbols are `NET_VENDOR_TOSHIBA`, `GELIC_NET`, `GELIC_WIRELESS`, and `TC35815`.

`NET_VENDOR_TOSHIBA` is a bool menu gate labeled "Toshiba devices". It defaults to `y` and depends on `(PCI && MIPS) || PPC_PS3` according to Kconfig operator precedence.

`GELIC_NET` is a tristate "PS3 Gigabit Ethernet driver" depending on `PPC_PS3` and selecting `PS3_SYS_MANAGER`. `GELIC_WIRELESS` is a bool depending on `GELIC_NET && WLAN` and selecting `WIRELESS_EXT`. `TC35815` is a tristate depending on `PCI && MIPS` and selecting `PHYLIB`.

## Control Flow
Kconfig first evaluates whether the Toshiba vendor menu is visible. If `NET_VENDOR_TOSHIBA` is enabled, users can select `GELIC_NET` for PS3 Ethernet, optionally enable `GELIC_WIRELESS`, or select `TC35815` on MIPS PCI systems. The selected symbols then drive object inclusion in the sibling Makefile.

## State And Persistence Behavior
The persistent state is kernel configuration: built-in, module, or disabled choices for `GELIC_NET` and `TC35815`, plus boolean choices for `NET_VENDOR_TOSHIBA` and `GELIC_WIRELESS`. No runtime state is defined here.

## Dependencies And Integration Points
The file integrates directly with `drivers/net/ethernet/toshiba/Makefile`: `CONFIG_GELIC_NET` builds `ps3_gelic.o`, `CONFIG_GELIC_WIRELESS` contributes `ps3_gelic_wireless.o` to that composite object, and `CONFIG_TC35815` builds `tc35815.o`.

It depends on architecture/platform symbols `PPC_PS3`, `PCI`, and `MIPS`, networking symbol `WLAN`, and selects subsystem support `PS3_SYS_MANAGER`, `WIRELESS_EXT`, and `PHYLIB`.

## Risks And Edge Cases
The vendor gate dependency mixes `&&` and `||`; current Kconfig precedence makes it equivalent to `(PCI && MIPS) || PPC_PS3`. Changing parentheses could hide PS3 options or expose Toshiba PCI options on unintended platforms.

`GELIC_WIRELESS` is a bool rather than a tristate and depends on `GELIC_NET`; wireless code is compiled into the Gelic composite object when enabled. Disabling the vendor menu hides all child options without changing their source files.

## Test Signals
Configuration tests should check PS3 builds with `GELIC_NET=y/m`, PS3 wireless enabled with `WLAN`, MIPS PCI builds with `TC35815=y/m`, and non-PS3 non-MIPS visibility. Verify selected dependencies appear in generated `.config` and that the Makefile includes the expected objects for built-in and module builds.
