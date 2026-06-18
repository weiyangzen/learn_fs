# sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.c

## Purpose
`sp5100_tco.c` drives AMD/ATI/Hygon SP5100, SB800, Hudson/Bolton, and newer embedded FCH TCO watchdogs. It discovers the SMBus PCI function, determines register layout by vendor/device/revision, enables watchdog decode/resolution in PM registers, maps the watchdog MMIO window, initializes hardware, and registers a watchdog core device.

## Important APIs, types, and functions
`enum tco_reg_layout` selects `sp5100`, `sb800`, `efch`, or `efch_mmio`. `struct sp5100_tco` embeds `watchdog_device`, MMIO base, and layout. Watchdog ops are `tco_timer_start()`, `tco_timer_stop()`, `tco_timer_ping()`, `tco_timer_set_timeout()`, and `tco_timer_get_timeleft()`. Setup helpers include `tco_reg_layout()`, `sp5100_tco_read_pm_reg8/32()`, `sp5100_tco_update_pm_reg8()`, `tco_timer_enable()`, `sp5100_tco_prepare_base()`, `sp5100_tco_timer_init()`, `sp5100_tco_setupdevice()`, and `sp5100_tco_setupdevice_mmio()`.

## Control flow
Module init scans all PCI devices for a supported SMBus ID, stores the first match, registers a platform driver, and creates a synthetic platform device. Probe allocates state, initializes timeout limits, applies module heartbeat/nowayout, and calls setup. Setup either reserves PM I/O ports or the fixed EFCH ACPI MMIO PM region, reads primary and alternate watchdog MMIO addresses, reserves and maps one, enables decode and one-second resolution, checks disabled/fired bits, sets reset/poweroff action, writes a safe timeout, and stops the timer before registration.

## State and persistence behavior
Global PCI and platform-device pointers track the single system TCO device. Bootstatus is latched from `SP5100_WDT_FIRED` before the control register write clears it. Hardware control/count registers persist across driver removal until stopped by unregister policy or explicit stop.

## Dependencies and integration points
The driver depends on PCI IDs, legacy PM I/O ports `0xcd6/0xcd7`, fixed EFCH MMIO addresses, `sp5100_tco.h` register definitions, platform-device glue, devm MMIO reservation/mapping, and watchdog core stop-on-reboot/unregister handling.

## Risks and test signals
Risks include chipset revision classification mistakes, contention on shared PM I/O ports, alternate MMIO fallback conflicts, fixed EFCH address assumptions, and action bit semantics. Test signals include device detection for each layout, resource conflict errors, fired-bit bootstatus, disabled-hardware rejection, timeout/count readback, start/ping distinct trigger writes, stop-on-reboot/unregister, and no PCI driver binding conflict with SMBus drivers.
