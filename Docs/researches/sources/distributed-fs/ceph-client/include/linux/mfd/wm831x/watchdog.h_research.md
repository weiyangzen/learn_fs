<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/watchdog.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/watchdog.h

## Purpose
`watchdog.h` defines the WM831x watchdog register fields. It supports enabling the watchdog, debug and sleep behavior, reset triggering, primary and secondary timeout actions, and timeout selection.

## Important APIs, types, and functions
There are no functions or structs. Macros describe register `0x4004`: `WM831X_WDOG_ENA`, `WM831X_WDOG_DEBUG`, `WM831X_WDOG_RST_SRC`, `WM831X_WDOG_SLPENA`, `WM831X_WDOG_RESET`, `WM831X_WDOG_SECACT_MASK`, `WM831X_WDOG_PRIMACT_MASK`, and `WM831X_WDOG_TO_MASK`, each with mask/shift/width companions.

## Control flow
The watchdog driver programs timeout and action fields from platform data, enables or disables the watchdog through `WM831X_WDOG_ENA`, and kicks or forces reset through the reset bit according to the chip protocol.

## State and persistence behavior
Watchdog configuration is hardware state. Once enabled, it can survive normal software control paths until explicitly disabled or until reset; sleep-enable and reset-source fields affect behavior across low-power and reboot paths.

## Dependencies and integration points
The header pairs with `wm831x_watchdog_pdata` and `enum wm831x_watchdog_action` in `pdata.h`, the watchdog subsystem, WM831x IRQ `WM831X_IRQ_WDOG_TO`, and core register access.

## Risks and test signals
Risks include choosing reset actions unexpectedly, failing to account for sleep behavior, writing timeout selectors outside hardware range, and mishandling debug mode. Test signals include watchdog start/stop/ping tests, timeout IRQ versus reset policy tests, suspend behavior, and reset-source readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/watchdog.h -->
