<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel_oc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/intel_oc_wdt.c`

Purpose: Intel OC watchdog driver for ACPI-described I/O-port watchdog registers, including support for one-time register locking and fixed heartbeat reporting.

Important APIs, types, and functions: `struct intel_oc_wdt` contains the watchdog core device, I/O resource, mutable `watchdog_info`, and `locked` flag. Ops perform direct `inl/outl` updates: start sets `EN`, stop clears it, ping sets `RLD`, set_timeout writes `TOV = timeout - 1`, and setup interprets status/lock bits.

Control flow: probe obtains and reserves the I/O resource, initializes timeout bounds, applies module heartbeat, calls `intel_oc_wdt_setup()`, sets drvdata and nowayout, installs stop-on-reboot/unregister, and registers. Setup maps status bits to `WDIOF_CARDRESET`, detects enabled/locked state, forces nowayout and removes `WDIOF_SETTIMEOUT` when a running watchdog is locked, or rejects a disabled locked watchdog.

State and persistence: `INTEL_OC_WDT_CTL_LCK` persists until reboot and freezes timeout/enable/lock fields. If firmware left the watchdog running, `WDOG_HW_RUNNING` is set. Reset-cause status bits are read from the same control register.

Dependencies and integration points: depends on ACPI IDs `INT3F0D` and `INTC1099`, I/O port reservation, watchdog core, and module parameters `heartbeat` and `nowayout`.

Risks and test signals: risks include incorrectly handling locked disabled hardware, mutating global nowayout based on one device, and no explicit status-bit clear. Test locked-running, locked-disabled, unlocked start/stop, heartbeat override, bootstatus after watchdog reset, and ACPI resource conflicts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel_oc_wdt.c -->
