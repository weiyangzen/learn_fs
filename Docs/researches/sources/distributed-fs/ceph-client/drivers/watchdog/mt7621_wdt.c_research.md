# sources/distributed-fs/ceph-client/drivers/watchdog/mt7621_wdt.c

## Purpose
`mt7621_wdt.c` drives the Ralink/MediaTek MT7621/MT7628 timer-1 watchdog. It exposes timer load/control registers through the watchdog core and reports watchdog reset cause from the SoC syscon reset-status register.

## Important APIs, types, and functions
`struct mt7621_wdt_data` stores timer MMIO, optional reset control, syscon regmap, and `watchdog_device`. Main operations are `mt7621_wdt_start`, `mt7621_wdt_stop`, `mt7621_wdt_ping`, `mt7621_wdt_set_timeout`, `mt7621_wdt_bootcause`, and `mt7621_wdt_is_running`.

## Control flow
Probe resolves the syscon from `mediatek,sysctl` or the legacy compatible, maps timer registers, deasserts an optional reset, initializes watchdog limits, reads boot cause, applies `nowayout`, and registers the device. If hardware is already enabled, it is stopped then restarted with this driver's 1 ms prescaler and core timeout before `WDOG_HW_RUNNING` is set. Start programs the prescaler, writes the load in milliseconds, pings, and sets enable. Stop pings first, then clears the enable bit. Shutdown always stops the watchdog.

## State and persistence
Persistent hardware state consists of timer control/load bits and syscon reset-cause bits across reboot. Runtime state is in the embedded watchdog device and drvdata; no software state is persisted.

## Dependencies and integration points
The driver depends on OF compatible `mediatek,mt7621-wdt`, regmap/syscon, reset control, platform MMIO, module parameter `nowayout`, and watchdog core bootstatus/status handling.

## Risks and test signals
Risks include changing the prescaler while a bootloader-started watchdog is active, missing syscon phandle fallback, `max_timeout` limited by 16-bit millisecond load, and unconditional stop on shutdown despite nowayout. Test signals include both syscon lookup paths, running-at-boot normalization, timeout load math, reset-control absence, and reboot/shutdown behavior.
