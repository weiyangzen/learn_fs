# subset-b-005596 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_dev.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_dev.c

## Purpose
`watchdog_dev.c` is the generic Linux watchdog character-device layer. It turns registered `struct watchdog_device` instances into `/dev/watchdogN`, preserves the legacy `/dev/watchdog` miscdevice for watchdog0, exposes optional sysfs attributes, drives standard watchdog ioctls, and supplies framework-managed keepalive/pretimeout timers for hardware with shorter heartbeat limits than the user-visible timeout.

## Important APIs, types, and functions
The main internal state is `struct watchdog_core_data`, attached through `wdd->wd_data`, with a device/cdev, mutex, status bits, hrtimer, kthread work, last keepalive timestamps, and open deadline. Public entry points are `watchdog_dev_register`, `watchdog_dev_unregister`, `watchdog_dev_init`, `watchdog_dev_exit`, `watchdog_set_last_hw_keepalive`, `watchdog_dev_suspend`, and `watchdog_dev_resume`. Key helpers include `watchdog_start`, `watchdog_stop`, `watchdog_ping`, `__watchdog_ping`, `watchdog_set_timeout`, `watchdog_set_pretimeout`, `watchdog_get_timeleft`, `watchdog_cdev_register`, and `watchdog_cdev_unregister`.

## Control flow
Module init creates the FIFO-priority `watchdogd` kthread worker, registers the watchdog class, and allocates major/minor space. Device registration allocates core data, initializes keepalive and pretimeout timers, adds a cdev/device, and for id 0 registers the legacy miscdevice. Opening the node single-opens the device, pins the owner module when needed, starts hardware, and disables the pre-userspace open deadline. Writes scan for magic close character `V` and ping. Ioctls first defer to a driver-specific ioctl, then implement common `WDIOC_*` operations. Release stops only on magic close or non-magicclose devices; otherwise it pings and leaves hardware running.

## State and persistence
State is runtime-only: device open bits, magic-close permission, `WDOG_ACTIVE`/`WDOG_HW_RUNNING`, module/device references, open deadline, last userspace and hardware keepalive times, and hrtimers. The keepalive worker persists while hardware is running before userspace takes over or while a virtual timeout exceeds hardware `max_hw_heartbeat_ms`. No on-disk persistence exists.

## Dependencies and integration points
It integrates the watchdog core, character-device layer, miscdevice compatibility, sysfs, module lifetime, hrtimers, kthread work, tracepoints, and pretimeout governors. Driver callbacks in `wdd->ops` provide hardware start/stop/ping/status/timeout behavior. `handle_boot_enabled` and `open_timeout` module parameters control early boot handling for already-running hardware watchdogs.

## Risks and test signals
Risks include lifetime races between unregister and open/release, incorrect module pinning when hardware remains running, timer scheduling around min/max heartbeat bounds, magic-close semantics, nowayout immutability, and pretimeout timer cancellation during stop/unregister/suspend. Test signals include concurrent open attempts, unregister while open, already-running hardware with finite open timeout, virtual timeout greater than hardware timeout, all standard watchdog ioctls, sysfs visibility with and without pretimeout support, suspend/resume pings, and nowayout release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_hrtimer_pretimeout.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_hrtimer_pretimeout.c

## Purpose
This file implements software pretimeout delivery for watchdog devices that do not expose hardware pretimeout support. It uses a per-watchdog hrtimer in `watchdog_core_data` to notify the selected pretimeout governor before the full watchdog timeout expires.

## Important APIs, types, and functions
The exported framework helpers are `watchdog_hrtimer_pretimeout_init`, `watchdog_hrtimer_pretimeout_start`, and `watchdog_hrtimer_pretimeout_stop`. The timer callback `watchdog_hrtimer_pretimeout` resolves the owning `watchdog_core_data` from `pretimeout_timer` and calls `watchdog_notify_pretimeout`.

## Control flow
Device registration initializes the hrtimer. Each successful hardware start or ping calls `watchdog_hrtimer_pretimeout_start`. If the device lacks hardware `WDIOF_PRETIMEOUT` but has a valid nonzero `wdd->pretimeout`, the timer is armed for `timeout - pretimeout` seconds. Otherwise it is cancelled. When the timer fires it invokes the governor and does not restart itself; the next watchdog ping/start rearms it.

## State and persistence
State is limited to the hrtimer embedded in watchdog core data and the current `wdd->timeout`/`wdd->pretimeout` values. Nothing persists across unregister or reboot.

## Dependencies and integration points
It depends on Linux hrtimers, `struct watchdog_device`, `watchdog_core.h`, and the pretimeout governor interface in `watchdog_pretimeout.h`. It is called only by the generic watchdog device layer.

## Risks and test signals
Risks are off-by-one timer scheduling, stale timer callbacks after unregister, double-notification when hardware already provides pretimeout, and invalid pretimeout values. Test signals include devices with software-only pretimeout, hardware pretimeout devices, timeout changes that invalidate pretimeout, repeated ping rearming, stop/unregister cancellation, and governor callback invocation timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_hrtimer_pretimeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.c

## Purpose
`watchdog_pretimeout.c` manages watchdog pretimeout governors. It tracks registered governors, assigns a default governor to watchdog devices that can emit pretimeout events, exposes sysfs-facing governor list/get/set helpers, and dispatches pretimeout notifications.

## Important APIs, types, and functions
Important state includes `default_gov`, `pretimeout_list`, `governor_list`, `pretimeout_lock`, and `governor_lock`. Internal wrappers are `struct watchdog_pretimeout` and `struct governor_priv`. Public functions are `watchdog_register_governor`, `watchdog_unregister_governor`, `watchdog_register_pretimeout`, `watchdog_unregister_pretimeout`, `watchdog_notify_pretimeout`, `watchdog_pretimeout_available_governors_get`, `watchdog_pretimeout_governor_get`, and `watchdog_pretimeout_governor_set`.

## Control flow
Governors register by name under `governor_lock`; duplicate names fail. If the registered name matches `WATCHDOG_PRETIMEOUT_DEFAULT_GOV`, it becomes `default_gov` and is assigned to pretimeout-capable devices without an explicit governor. Watchdog registration allocates a list entry when `watchdog_have_pretimeout(wdd)` is true and initializes `wdd->gov`. Sysfs set resolves a governor by `sysfs_streq` and updates `wdd->gov`. Pretimeout notification takes the spinlock and calls the selected governor callback if present.

## State and persistence
The lists are global runtime state. Device-to-governor binding lives in `wdd->gov` and changes with sysfs writes or governor unregister. There is no persistent storage; settings reset when devices or governors unregister.

## Dependencies and integration points
It depends on the watchdog core, sysfs formatting helpers, slab allocation, mutexes, spinlocks, and list APIs. It integrates with `watchdog_dev.c` sysfs attributes and with pretimeout governor modules such as noop or panic governors.

## Risks and test signals
Risks include callbacks invoked while holding `pretimeout_lock`, governor module unload races, default governor replacement semantics, allocation failure during watchdog registration, and sysfs writes racing notification. Test signals include duplicate governor registration, default governor late registration, unregistering the active governor, devices without pretimeout support, sysfs list/get/set paths, and notification while governors are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.h

## Purpose
This header defines the watchdog pretimeout governor interface and provides either real declarations or stubbed inline fallbacks depending on `CONFIG_WATCHDOG_PRETIMEOUT_GOV`.

## Important APIs, types, and functions
It defines `WATCHDOG_GOV_NAME_MAXLEN`, forward-declares `struct watchdog_device`, and defines `struct watchdog_governor` with a fixed-length `name` and `pretimeout` callback. Enabled builds declare governor registration, watchdog pretimeout registration, available-governor listing, and per-device governor get/set functions. Disabled builds return success for registration/unregistration no-ops and `-EINVAL` for sysfs governor operations.

## Control flow
Consumers include this header unconditionally. Compile-time conditionals decide whether calls link to `watchdog_pretimeout.c` or fold into harmless stubs. The default governor macro is selected from `CONFIG_WATCHDOG_PRETIMEOUT_DEFAULT_GOV_NOOP` or `CONFIG_WATCHDOG_PRETIMEOUT_DEFAULT_GOV_PANIC`.

## State and persistence
The header has no state of its own. It controls whether runtime governor state exists in the pretimeout subsystem.

## Dependencies and integration points
It is included by watchdog core code and governor implementations. Its stub design lets `watchdog_dev.c` compile without pretimeout governor support while keeping call sites simple.

## Risks and test signals
Risks are mismatches between Kconfig defaults and the macro, fixed name truncation, and call sites assuming sysfs operations work when governors are disabled. Test signals include builds with governor support disabled, noop default, panic default, and pretimeout-capable devices under each configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wd501p.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wd501p.h

## Purpose
`wd501p.h` centralizes I/O-port offsets and status-bit definitions for Industrial Computer Source WDT500/501 ISA and PCI watchdog cards.

## Important APIs, types, and functions
The header defines register offsets relative to the driver-global `io` base: counter ports `WDT_COUNT0..2`, control register `WDT_CR`, status/reset/temperature or buzzer ports, digital control `WDT_DC`, and PCI-only ports for clock, opto reset outputs, and programmable output. It also defines status bits such as `WDC_SR_WCCR`, `WDC_SR_TGOOD`, isolated input bits, fan good, power over/under, and IRQ.

## Control flow
There are no functions. ISA and PCI drivers include this file and use the macros directly in `inb`/`outb` sequences for start, stop, ping, status, temperature, and interrupt handling.

## State and persistence
The header has no state. It assumes including C files provide a valid `io` variable and know which board type and features are present.

## Dependencies and integration points
It is shared by `wdt.c` and `wdt_pci.c`, with `WDT_IS_PCI` controlling comments/usage rather than changing most definitions. It binds the drivers tightly to legacy I/O-port hardware.

## Risks and test signals
Risks include incorrect `io` base selection, using PCI-only ports on ISA hardware, inverted status bit interpretation, and lack of type safety around macro arithmetic. Test signals are hardware smoke tests for WDT500 and WDT501 variants, status-bit decoding under fault inputs, temperature readback, and PCI-only output toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wd501p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdat_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wdat_wdt.c

## Purpose
`wdat_wdt.c` implements the ACPI WDAT hardware watchdog driver. It parses the firmware WDAT table into action-specific instruction lists and exposes the watchdog through the modern watchdog core.

## Important APIs, types, and functions
Core types are `struct wdat_instruction`, wrapping an `acpi_wdat_entry` and mapped register pointer, and `struct wdat_wdt`, containing the platform device, `watchdog_device`, timer period, suspend flags, and action lists. Important functions are `wdat_wdt_run_action`, `wdat_wdt_read`, `wdat_wdt_write`, `wdat_wdt_enable_reboot`, `wdat_wdt_boot_status`, `wdat_wdt_set_running`, watchdog ops `start`, `stop`, `ping`, `set_timeout`, optional `get_timeleft`, `wdat_wdt_probe`, and noirq suspend/resume callbacks.

## Control flow
Probe obtains the ACPI WDAT table, validates period/count bounds, maps platform memory or I/O resources, converts each WDAT entry into an instruction tied to the matching resource, and links it under its action number. It reads boot status, detects already-running state, enables reboot-on-fire, sets a safer initial timeout, marks nowayout/stop policies, and registers with the watchdog core. Runtime ops execute firmware-defined action sequences for start, stop, reset, countdown, and timeleft.

## State and persistence
Runtime state is device-managed and firmware-derived. Hardware countdown/reboot configuration persists in platform registers until firmware or the driver changes it. The driver remembers whether it stopped the watchdog during suspend so resume can reprogram appropriately.

## Dependencies and integration points
It depends on ACPI WDAT definitions, generic address structures, platform resources, I/O mapping helpers, PM noirq hooks, and the watchdog core. It integrates with firmware-provided WDAT platform devices and ACPI sleep state handling.

## Risks and test signals
Risks include malformed WDAT tables, unsupported access widths or address spaces, register-resource mismatch, preserve-mask arithmetic, period/count overflow, firmware reinitialization across sleep, and optional actions returning `-EOPNOTSUPP`. Test signals include WDAT systems with memory and I/O GAS entries, missing optional actions, boot-status clear, running-at-boot detection, suspend-to-idle versus S3/S4 paths, timeout conversion boundaries, and ACPI table fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdat_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdrtas.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wdrtas.c

## Purpose
`wdrtas.c` is a legacy PowerPC RTAS watchdog driver. It exposes `/dev/watchdog` and optionally `/dev/temperature`, controlling firmware surveillance through RTAS calls rather than the modern watchdog core.

## Important APIs, types, and functions
Global state includes RTAS tokens for `set-indicator`, `event-scan`, `get-sensor-state`, and `ibm,get-system-parameter`, `wdrtas_interval`, single-open atomic state, and magic-close state. Important functions are `wdrtas_set_interval`, `wdrtas_get_interval`, `wdrtas_timer_start`, `wdrtas_timer_stop`, `wdrtas_timer_keepalive`, `wdrtas_get_temperature`, `wdrtas_write`, `wdrtas_ioctl`, `wdrtas_open`, `wdrtas_close`, `wdrtas_reboot`, `wdrtas_get_tokens`, and device registration helpers.

## Control flow
Init resolves required RTAS tokens, registers the watchdog miscdevice, optionally registers the temperature miscdevice, installs a reboot notifier, and reads the initial interval. Opening starts surveillance and performs an event-scan keepalive. Writes scan for `V` if nowayout is false and keepalive by draining RTAS event-scan results. Ioctls implement support/status/bootstatus/temp/options/keepalive/timeout. Close stops only after magic close; otherwise it pings and leaves the watchdog active.

## State and persistence
The interval is held in seconds in the driver but programmed as RTAS minutes. Firmware surveillance state lives outside the kernel and may persist until changed by RTAS. The driver does not use watchdog-core device state.

## Dependencies and integration points
It depends on RTAS firmware services, miscdevice, reboot notifiers, uaccess, and watchdog ioctl ABI. Temperature support depends on the optional RTAS sensor token.

## Risks and test signals
Risks include missing RTAS tokens, minute/second rounding surprises, event-scan failures, legacy miscdevice collisions, temperature copied as one byte despite `int` storage, and `nowayout` not preventing close path logic from leaving state ambiguous. Test signals include systems with and without optional sensor/SP tokens, open exclusivity, magic close, timeout set/get, reboot notifier shutdown, and RTAS error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdrtas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wdt.c

## Purpose
`wdt.c` is the legacy ISA driver for Industrial Computer Source WDT500/501 watchdog cards. It controls counter chips and status registers through fixed I/O ports and exposes `/dev/watchdog` plus an optional temperature device for WDT501.

## Important APIs, types, and functions
Key globals are `io`, `irq`, `heartbeat`, `wd_heartbeat`, `type`, `tachometer`, `wdt_is_open`, `expect_close`, and `wdt_lock`. Important functions are `wdt_ctr_mode`, `wdt_ctr_load`, `wdt_start`, `wdt_stop`, `wdt_ping`, `wdt_set_heartbeat`, `wdt_get_status`, `wdt_get_temperature`, `wdt_interrupt`, file operations, `wdt_notify_sys`, `wdt_init`, and `wdt_exit`.

## Control flow
Init validates card type and heartbeat, requests the I/O region and IRQ, registers a reboot notifier, optionally registers `/dev/temperature`, then registers `/dev/watchdog`. Opening single-opens and programs counters: CTR0 as 100 Hz source, CTR1 as watchdog heartbeat, CTR2 as reset pulse. Writes scan for magic close and reload CTR1. Ioctls expose status, keepalive, and timeout. Interrupts read status and log external, thermal, fan, and power faults. Shutdown notifiers disable the card.

## State and persistence
State is global because only one ISA card is supported. Hardware counter and status state persists while the board is powered. The driver does not pin its module for nowayout and uses legacy open bits rather than watchdog core state.

## Dependencies and integration points
It depends on raw I/O port access, IRQs, miscdevice, reboot notifiers, and the shared `wd501p.h` register map. User integration is the legacy watchdog ioctl ABI.

## Risks and test signals
Risks include unprobeable hardware requiring correct module parameters, I/O/IRQ conflicts, inverted fault bits, interrupt handling under spinlock while printing, magic close not clearing open state on unexpected close, and no modern watchdog-core policies. Test signals include WDT500 and WDT501 hardware, heartbeat bounds, fault input interrupts, tachometer option, temperature read, shutdown/reboot notifier, and unexpected close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt285.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wdt285.c

## Purpose
`wdt285.c` implements the Intel/DEC 21285 Footbridge watchdog for older ARM platforms. It directly programs timer 4 and an irreversible SA110 watchdog enable bit.

## Important APIs, types, and functions
State includes `soft_margin`, computed `reload`, and single-open `timer_alive`. Main functions are `watchdog_ping`, `watchdog_open`, `watchdog_release`, `watchdog_write`, `watchdog_ioctl`, `footbridge_watchdog_init`, and `footbridge_watchdog_exit`. In `ONLY_TESTING` builds, `watchdog_fire` handles timer interrupts without rebooting.

## Control flow
Init skips NetWinder machines and registers `/dev/watchdog`. Open refuses if the hardware watchdog bit is already set or the device is open, computes reload from `mem_fclk_21285 / 256`, clears and loads timer 4, starts auto-reload, and in normal builds sets the irreversible watchdog-enable bit. Writes and keepalive ioctls reload the timer. Timeout ioctl accepts a narrow range and recomputes reload.

## State and persistence
Once enabled in normal builds, the hardware watchdog cannot be disabled until reset. The driver has no magic close and release does not stop real hardware. Runtime state is minimal and global.

## Dependencies and integration points
It depends on ARM Footbridge platform headers, machine detection, CSR timer registers, miscdevice, and legacy watchdog ioctls.

## Risks and test signals
Risks include irreversible enablement, platform clock assumptions, ambiguous zero timeout handling, no nowayout/module pinning option, and direct memory-mapped register access without locking. Test signals include Footbridge non-NetWinder hardware, timeout set/get, repeated keepalive, already-enabled detection, and `ONLY_TESTING` interrupt path if compiled for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt285.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt977.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wdt977.c

## Purpose
`wdt977.c` controls the Winbond W83977AF Super I/O watchdog, originally for NetWinder systems but usable with fixed index/data ports. It exposes the legacy `/dev/watchdog` interface.

## Important APIs, types, and functions
Important state includes `timeout` in seconds, `timeoutM` in hardware minutes, `timer_alive`, `testmode`, `expect_close`, `nowayout`, and a spinlock around Super I/O register access. Core functions are `wdt977_start`, `wdt977_stop`, `wdt977_keepalive`, `wdt977_set_timeout`, `wdt977_get_status`, file operations, `wdt977_notify_sys`, `wd977_init`, and `wd977_exit`.

## Control flow
Init validates the timeout, requests the fixed I/O port pair except on NetWinder, registers a reboot notifier and miscdevice. Start unlocks the Super I/O, selects logical device 8, programs F2/F3/F4 watchdog registers, configures Aux1 GP16 output unless in test mode, then locks the chip. Keepalive rewrites F2. Stop writes shutdown values. Open single-opens, optionally pins the module for nowayout, and starts hardware. Close stops only after magic close, otherwise pings.

## State and persistence
Hardware timeout granularity is minutes; NetWinder doubles the programmed minute count due to a hardware bug. Super I/O state persists until reprogrammed or reset. Driver state is global and legacy.

## Dependencies and integration points
It depends on raw x86/ARM I/O ports, NetWinder machine detection, miscdevice, reboot notifier, and watchdog ioctl ABI.

## Risks and test signals
Risks include fixed port conflicts, unlock/lock sequence mistakes, seconds-to-minutes rounding, NetWinder special-case cleanup releasing an unrequested region, testmode changing reset semantics, and nowayout module pinning. Test signals include timeout boundaries, NetWinder and non-NetWinder builds, magic close, SETOPTIONS enable/disable, status bit F4 card-reset detection, and reboot notifier stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt977.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt_pci.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wdt_pci.c

## Purpose
`wdt_pci.c` is the PCI variant driver for ICS PCI-WDT500/501 cards. It uses the shared WDT register definitions but obtains I/O resources and IRQs through PCI probing.

## Important APIs, types, and functions
Global state includes `dev_count`, `open_lock`, `wdtpci_lock`, `expect_close`, `io`, `irq`, `heartbeat`, `wd_heartbeat`, `type`, and `tachometer`. Important functions mirror the ISA driver: `wdtpci_ctr_mode`, `wdtpci_ctr_load`, `wdtpci_start`, `wdtpci_stop`, `wdtpci_ping`, `wdtpci_set_heartbeat`, `wdtpci_get_status`, `wdtpci_get_temperature`, `wdtpci_interrupt`, file operations, reboot notifier, `wdtpci_init_one`, and `wdtpci_remove_one`.

## Control flow
PCI probe enforces one supported device, validates type, enables the PCI device, requests BAR 2, records I/O base and IRQ, registers a shared IRQ, validates heartbeat, registers reboot notifier, optional temperature miscdevice, and watchdog miscdevice. Start disables and pets the card, programs clock and counters, disables buzzer/opto outputs, then enables the watchdog. Writes and keepalive reload counter 1. Interrupts report board faults.

## State and persistence
The driver supports only one global device because `/dev/watchdog` is singular. Hardware counter/output state persists while powered. Nowayout pins the module but the legacy state model remains outside watchdog core.

## Dependencies and integration points
It depends on PCI IDs for AccessIO WDG-CSM, BAR 2 I/O port access, shared IRQs, miscdevice, reboot notifier, and `wd501p.h`. User integration is the standard legacy watchdog ioctl interface plus optional `/dev/temperature`.

## Risks and test signals
Risks include global state with PCI hotplug, `dev_count` leaks on early probe failures, BAR/IRQ mismatch, timing-sensitive `udelay(8)` programming, only-one-device limitation, and unexpected close keeping hardware running. Test signals include PCI probe/remove cycles, heartbeat bounds, WDT500/501 status and tachometer options, temperature read, shared IRQ behavior, reboot notifier stop, and failure-path cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wdt_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wm831x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wm831x_wdt.c

## Purpose
`wm831x_wdt.c` implements a watchdog-core platform driver for WM831x PMIC watchdog blocks, using the parent MFD register APIs and optional platform data.

## Important APIs, types, and functions
`struct wm831x_wdt_drvdata` holds a `watchdog_device`, parent `struct wm831x`, mutex, and unused `update_state`. Timeout table `wm831x_wdt_cfgs` maps supported second values to `WDOG_TO` register codes. Ops are `wm831x_wdt_start`, `wm831x_wdt_stop`, `wm831x_wdt_ping`, and `wm831x_wdt_set_timeout`; probe configures platform data and registers the device.

## Control flow
Probe reads the watchdog register, warns if paused in debug mode, allocates driver data, initializes watchdog core fields and nowayout, reads the current timeout code, applies optional primary/secondary/software reset action platform data under security unlock, and calls `devm_watchdog_register_device`. Start/stop unlock protected registers and set or clear `WM831X_WDOG_ENA`. Ping verifies software reset/update support through `WM831X_WDOG_RST_SRC`, sets `WM831X_WDOG_RESET`, and writes the watchdog register.

## State and persistence
Driver state is devm-managed. PMIC watchdog configuration persists in PMIC registers until changed. The mutex serializes protected register unlock/write/lock sequences.

## Dependencies and integration points
It depends on WM831x MFD core/pdata/watchdog headers, platform bus, watchdog core, and module parameter `nowayout`.

## Risks and test signals
Risks include unsupported hardware update mode, security unlock failures, timeout table rejecting valid-looking values, stale timeout if register read returns unknown code, and platform data bit-shift mistakes. Test signals include all supported timeouts, debug-paused hardware, software reset source disabled, start/stop/ping errors, platform-data action programming, and devm removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wm831x_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wm8350_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wm8350_wdt.c

## Purpose
`wm8350_wdt.c` is a watchdog-core platform driver for the WM8350 PMIC watchdog.

## Important APIs, types, and functions
It uses one static `watchdog_device` and a global `wdt_mutex`. Timeout table `wm8350_wdt_cfgs` maps 1, 2, and 4 seconds to register values. Ops are `wm8350_wdt_set_timeout`, `wm8350_wdt_start`, `wm8350_wdt_stop`, and `wm8350_wdt_ping`; probe binds parent MFD data, sets defaults, and registers with devm.

## Control flow
Probe retrieves `struct wm8350` from platform driver data, sets nowayout and driver data, assigns the parent device, programs a default 4 second timeout, and registers. Start/stop unlock system control register 2, update watchdog mode bits, write, and relock. Ping rewrites the current system control register value, which refreshes the watchdog.

## State and persistence
The watchdog device is static, so the driver effectively assumes one instance. PMIC register state persists across driver lifetime. The mutex serializes register access.

## Dependencies and integration points
It depends on WM8350 MFD core functions, platform bus, watchdog core, and the module parameter `nowayout`.

## Risks and test signals
Risks include static-device multi-instance unsafety, no read-error checks in several paths, narrow timeout support, protected register lock/unlock sequencing, and default timeout programming failures. Test signals include probe with missing platform data, 1/2/4 second timeouts and invalid values, start/stop/ping under injected MFD errors, and module reload on boards with the PMIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wm8350_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/xen_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/xen_wdt.c

## Purpose
`xen_wdt.c` exposes the Xen hypervisor scheduler watchdog as a Linux watchdog-core device when running inside a Xen domain.

## Important APIs, types, and functions
Global state includes the synthetic platform device, `struct sched_watchdog wdt`, and `wdt_expires`. Watchdog ops are `xen_wdt_start`, `xen_wdt_stop`, `xen_wdt_kick`, and `xen_wdt_get_timeleft`. Probe verifies hypervisor support with `SCHEDOP_watchdog`, initializes timeout and nowayout, and registers. Suspend/resume preserve the Xen watchdog id around stop/restart.

## Control flow
Module init exits outside Xen, registers a platform driver, then creates a simple platform device. Probe sends a sentinel watchdog request expecting `-EINVAL` to indicate support, configures watchdog core policies, and registers. Start sets the requested timeout and asks Xen to allocate a watchdog id. Ping updates the existing id. Stop sends timeout zero and clears the id. Resume re-creates the watchdog if it was active before suspend.

## State and persistence
The Xen watchdog id is hypervisor state. `wdt_expires` is a kernel-side approximation used for `GETTIMELEFT`. State is global, so the driver supports one watchdog instance.

## Dependencies and integration points
It depends on Xen domain detection, `HYPERVISOR_sched_op`, Xen `sched_watchdog` ABI, platform bus, and watchdog core.

## Risks and test signals
Risks include unexpected hypervisor return codes, `BUG_ON(!err)` in start if the hypervisor returns zero without assigning an id, stale `wdt_expires`, suspend/resume id preservation, and unsigned underflow in timeleft after expiry. Test signals include Xen with and without watchdog op support, start/stop/ping, timeout module parameter, suspend/resume with active and inactive watchdogs, and hypercall failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/xen_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/xilinx_wwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/xilinx_wwdt.c

## Purpose
`xilinx_wwdt.c` implements the Xilinx Versal window watchdog driver. It programs closed and open watchdog windows from the input clock and exposes the device through the watchdog core.

## Important APIs, types, and functions
`struct xwwdt_device` stores MMIO base, spinlock, `watchdog_device`, clock frequency, close-window percentage, and computed closed/open tick counts. Ops are `xilinx_wwdt_start` and `xilinx_wwdt_keepalive`. Probe maps registers, enables the clock, computes timeout limits, initializes watchdog core fields, and registers. Module parameters are `wwdt_timeout` and `closed_window_percent`.

## Control flow
Probe validates a >=1 MHz source clock, computes `max_hw_heartbeat_ms` from the combined 32-bit windows, validates/chooses the closed-window percentage, initializes timeout, converts milliseconds to ticks, and adjusts closed/open windows for hardware maximums. Start enables master write, clears enable, writes first and second window registers, then enables the watchdog. Ping enables master write and sets the software restart bit in ESR.

## State and persistence
Runtime state is per-platform device. Hardware window registers persist until reset or reprogramming. `nowayout` is forced on through `watchdog_set_nowayout(..., 1)`.

## Dependencies and integration points
It depends on platform MMIO resources, clocks, OF compatible `xlnx,versal-wwdt`, math64 helpers, spinlocks, and watchdog core min/max heartbeat handling.

## Risks and test signals
Risks include clock-rate assumptions, tick multiplication overflow before 64-bit division boundaries, closed-window percentages that violate hardware limits, forced nowayout surprise, no stop op, and pinging during the closed window. Test signals include multiple clock rates, timeout above and below hardware maximum, invalid close percentages, watchdog core min heartbeat enforcement, OF probe, and register write/read smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/xilinx_wwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ziirave_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ziirave_wdt.c

## Purpose
`ziirave_wdt.c` is an I2C watchdog-core driver for the Zodiac/ZII RAVE switch watchdog processor. It also exposes sysfs attributes for firmware/bootloader versions, reset reason, reset duration configuration, and firmware update.

## Important APIs, types, and functions
`struct ziirave_wdt_data` holds a sysfs mutex, watchdog device, firmware and bootloader revisions, and reset reason. Watchdog ops are `ziirave_wdt_start`, `ziirave_wdt_stop`, `ziirave_wdt_ping`, `ziirave_wdt_set_timeout`, and `ziirave_wdt_get_timeleft`. Firmware helpers include `ziirave_firm_read_ack`, `ziirave_firm_set_read_addr`, `ziirave_firm_write_pkt`, `ziirave_firm_verify`, and `ziirave_firm_upload`. Sysfs handlers expose firmware, bootloader, reset reason, and trigger update from `ziirave_wdt.fw`.

## Control flow
Probe checks SMBus byte, byte-data, and block-write support, allocates state, initializes watchdog limits and groups, obtains timeout from module/OF or device register, writes it back, sets nowayout, handles initial unconfigured state by stopping the watchdog, programs optional reset duration, reads revisions and reset reason, validates the reason string, then registers. Firmware update jumps to bootloader, starts download, writes ihex records in 16-byte packets split at 128-byte pages, sends an empty packet, verifies by reading back bytes, ends download, resets the processor, rereads firmware version, and restores timeout.

## State and persistence
Device timeout, state, reset duration, revisions, and firmware live in the external watchdog processor. Kernel state caches version and reset reason for sysfs and serializes firmware updates with `sysfs_mutex`.

## Dependencies and integration points
It depends on I2C SMBus APIs, Intel HEX firmware loader, OF property `reset-duration-ms`, watchdog core, device sysfs groups, and `linux/unaligned.h` for packet formatting.

## Risks and test signals
Risks include destructive firmware update failures, read-only flash range filtering, checksum/page split bugs, stale cached revisions, reset reason array validation, missing `devm` unregister because manual `watchdog_register_device` is used, and I2C adapters lacking required SMBus operations. Test signals include valid and invalid timeouts, reset-duration property bounds, firmware update success/failure/verify mismatch, reset reason values, initial state handling, I2C error injection, and remove path unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ziirave_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/xen/Kconfig

## Purpose
This Kconfig file defines the Xen driver support menu. It controls memory ballooning, xenfs, event-channel device support, grant devices, backend/frontend drivers, ACPI/EFI helpers, SWIOTLB, virtio grant integration, and platform-specific Xen support options.

## Important APIs, types, and functions
It is declarative Kconfig. Important symbols include `XEN_BALLOON`, `XEN_BALLOON_MEMORY_HOTPLUG`, `XEN_DEV_EVTCHN`, `XEN_BACKEND`, `XENFS`, `XEN_GNTDEV`, `XEN_GRANT_DEV_ALLOC`, `SWIOTLB_XEN`, `XEN_PCIDEV_BACKEND`, `XEN_PRIVCMD`, `XEN_ACPI_PROCESSOR`, `XEN_MCE_LOG`, `XEN_EFI`, `XEN_AUTO_XLATE`, `XEN_ACPI`, `XEN_UNPOPULATED_ALLOC`, `XEN_VIRTIO`, and `XEN_VIRTIO_FORCE_GRANT`.

## Control flow
The menu is visible only under `XEN`. Per-feature dependencies constrain options by architecture, Dom0/backend role, PCI, ACPI, memory hotplug, target core, eventfd, virtio, DMA ops, and EFI. `select` clauses pull in required helpers such as `SWIOTLB`, `MMU_NOTIFIER`, `DMA_SHARED_BUFFER`, grant DMA ops, and IOMMU support.

## State and persistence
State is build-time `.config` state. Selected symbols drive kbuild object inclusion and preprocessor conditionals in Xen drivers.

## Dependencies and integration points
It integrates Xen guest/Dom0 subsystems with memory management, block/network/storage backends, userspace hypercall interfaces, ACPI/EFI platform services, DMA mapping, and virtio grant support.

## Risks and test signals
Risks include under-specified dependencies causing randconfig build failures, defaults enabling too much in non-Dom0 guests, hidden selects changing DMA behavior, and architecture-specific symbols being visible in impossible configurations. Test signals include `allmodconfig`, `randconfig`, x86/ARM/ARM64 Xen guest and Dom0 builds, EFI-enabled builds, and combinations of virtio grant options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/Makefile -->
# sources/distributed-fs/ceph-client/drivers/xen/Makefile

## Purpose
This Makefile maps Xen Kconfig symbols and architecture conditions to built objects and subdirectories.

## Important APIs, types, and functions
It uses kbuild variables such as `obj-y`, `obj-$(CONFIG_...)`, composite object lists, and architecture-conditioned `dom0-*` lists. Always-built Xen core objects include grant table, features, balloon, manage, time, mem reservation, events, and xenbus. Conditional objects cover CPU hotplug, Dom0 platform helpers, block bio merge, event-channel device, grant devices, xenfs, sys-hypervisor, platform PCI, SWIOTLB, mcelog, pciback, privcmd, ACPI processor, EFI, scsiback, pv calls, xlate MMU, front shared buffers, unpopulated alloc, and grant DMA.

## Control flow
Kbuild evaluates configuration variables and descends into `events/`, `xenbus/`, `xenfs/`, and `xen-pciback/` as appropriate. Composite variables map module names such as `xen-evtchn`, `xen-gntdev`, `xen-gntalloc`, and `xen-privcmd` to their constituent objects.

## State and persistence
The Makefile has no runtime state; it creates build graph state from `.config`.

## Dependencies and integration points
It links the Kconfig menu to the actual Xen driver implementation files and architecture-specific Dom0 helpers.

## Risks and test signals
Risks include stale object names, architecture conditional mismatches, unconditional core objects lacking dependencies, and module composition drift. Test signals include Xen disabled/enabled builds, Dom0 ARM64 and x86 builds, `CONFIG_BLOCK=n`, modular grant/privcmd/xenfs options, and `make W=1` for orphaned objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/xen/acpi.c

## Purpose
`acpi.c` contains Xen Dom0 ACPI integration helpers for sleep notification and interrupt routing information.

## Important APIs, types, and functions
Key functions are `xen_acpi_notify_hypervisor_sleep`, `xen_acpi_notify_hypervisor_extended_sleep`, internal `xen_acpi_notify_hypervisor_state`, `xen_acpi_get_gsi_info`, `xen_acpi_register_get_gsi_func`, and `xen_acpi_get_gsi_from_sbdf`. It defines a local ACPI PRT entry shape matching the fields used from ACPI PCI IRQ lookup.

## Control flow
Sleep helpers package PM control values into `XENPF_enter_acpi_sleep` platform ops, validating 16-bit or 8-bit fields depending on extended mode, then notify Xen. GSI lookup reads a PCI device interrupt pin, uses ACPI PCI IRQ lookup, allocates link interrupts when needed, defaults polarity based on ACPI IRQ model, and returns GSI/trigger/polarity. SBDF lookup is an externally registered callback protected by an rwlock.

## State and persistence
Only the registered SBDF-to-GSI callback pointer is persistent runtime state. ACPI and Xen platform state are external.

## Dependencies and integration points
It depends on PCI, ACPI PCI IRQ routing, Xen platform hypercalls, and exported Xen ACPI helper symbols used by other Xen PCI/ACPI code.

## Risks and test signals
Risks include truncating sleep control values, ignoring hypercall return from sleep notification, ACPI PRT assumptions, callback unregister absence, and rwlock use around arbitrary callback execution. Test signals include S-state transitions, extended sleep values, PCI devices with direct and link-based PRT entries, GIC and non-GIC polarity defaults, invalid inputs, and SBDF callback registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/arm-device.c -->
# sources/distributed-fs/ceph-client/drivers/xen/arm-device.c

## Purpose
`arm-device.c` maps and unmaps device MMIO regions into Xen initial-domain physical space for ACPI-enumerated platform and AMBA devices on ARM/ARM64 Dom0.

## Important APIs, types, and functions
Important helpers are `xen_map_device_mmio`, `xen_unmap_device_mmio`, `xen_platform_notifier`, optional `xen_amba_notifier`, and their `arch_initcall` registration functions. It uses Xen `XENMEM_add_to_physmap_range` and `XENMEM_remove_from_physmap`.

## Control flow
At arch init, if running in the Xen initial domain with ACPI enabled, the file registers bus notifiers. On `BUS_NOTIFY_ADD_DEVICE`, each memory resource is split into Xen pages, guest PFNs and device indexes are allocated and filled 1:1 from resource addresses, and Xen maps them as `XENMAPSPACE_dev_mmio`. On delete, the resources are removed from physmap page by page. Mapping failures trigger cleanup of already mapped resources.

## State and persistence
The file keeps no long-lived per-device state; Xen physmap mappings persist until corresponding bus delete or domain teardown.

## Dependencies and integration points
It depends on platform bus, optional AMBA bus, ACPI state, Xen memory hypercalls, Xen page macros, and initial-domain detection.

## Risks and test signals
Risks include resource-size rounding over partial pages, large allocation sizes for big MMIO windows, absence of per-page `errs` checking after range hypercalls, notifier ordering around driver probe, and cleanup only up to the failed resource index. Test signals include ACPI platform devices with multiple MMIO resources, AMBA devices, add/delete notifier paths, hypercall error injection, non-initial-domain no-op behavior, and partial mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/arm-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/balloon.c -->
# sources/distributed-fs/ceph-client/drivers/xen/balloon.c

## Purpose
`balloon.c` implements Xen memory ballooning: returning pages to Xen, reclaiming pages from Xen, optionally hotplugging unpopulated memory ranges, and providing ballooned pages for grant/foreign mappings.

## Important APIs, types, and functions
Global state includes `balloon_stats`, `balloon_state`, `balloon_mutex`, `balloon_thread_wq`, `ballooned_pages`, `balloon_wq`, and `frame_list`. Important functions are `balloon_append`, `balloon_retrieve`, `update_schedule`, `reserve_additional_memory`, `xen_online_page`, `increase_reservation`, `decrease_reservation`, `balloon_thread`, `balloon_set_new_target`, `xen_alloc_ballooned_pages`, `xen_free_ballooned_pages`, `balloon_add_regions`, `balloon_init`, and `balloon_wait_finish`.

## Control flow
Init runs in Xen domains, computes current reservation, initializes stats, installs memory hotplug callbacks/sysctl when enabled, adds extra memory regions to the balloon list, starts the `xen-balloon` kthread, and initializes the sysfs/control side through `xen_balloon_init`. The thread waits for target/current credit changes. Positive credit retrieves ballooned pages or hotplugs additional memory; negative credit allocates pages, scrubs them, resets VA mappings, adds them to the balloon list, flushes TLBs, and decreases the Xen reservation.

## State and persistence
Ballooned pages are tracked on a global list using page `lru`, with offline page flags and `NR_BALLOON_PAGES` accounting. `balloon_stats` tracks current, target, total, low/high ballooned pages, retry delay, and unpopulated target. Xen reservation and p2m mappings are persistent hypervisor/kernel state until reversed.

## Dependencies and integration points
It depends on Xen memory reservation helpers, p2m mapping helpers, Linux memory hotplug, sysctl, kthreads, freezer, page allocator, highmem kmap flushing, TLB flushes, and exported `xen_alloc_ballooned_pages`/`xen_free_ballooned_pages` users such as grant mappings.

## Risks and test signals
Risks include accounting underflow, OOM pressure during balloon-out, deadlocks with memory hotplug locks, P2M invalidation mistakes, highmem kmap stale mappings, retry cancellation during boot ballooning, and `target_unpopulated` imbalance on allocation failure. Test signals include PV and HVM/PVH guests, Dom0 current-reservation path, balloon up/down under memory pressure, hotplug unpopulated sysctl, grant-page allocation/free, extra memory regions, initial balloon wait timeout, and fault injection in reservation hypercalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/balloon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/biomerge.c -->
# sources/distributed-fs/ceph-client/drivers/xen/biomerge.c

## Purpose
`biomerge.c` provides a Xen-aware block-layer helper that decides whether a `bio_vec` and a following page are physically mergeable in Xen bus-frame space.

## Important APIs, types, and functions
The exported function is `xen_biovec_phys_mergeable(const struct bio_vec *vec1, const struct page *page)`.

## Control flow
When Xen and Linux page sizes match, it converts both pages to Xen bus frame numbers and checks whether `vec1` ending offset lands exactly at the next page's frame. When page sizes differ, it returns false because the merge logic is not implemented.

## State and persistence
The file has no state and no persistence.

## Dependencies and integration points
It depends on block `bio_vec`, Xen page/bfn helpers, and is built under `CONFIG_BLOCK` for Xen block I/O paths that must avoid merging segments that are not contiguous to the backend.

## Risks and test signals
Risks include wrong merge decisions when offsets cross Xen page boundaries, disabled merging on nonmatching page sizes reducing performance, and assumptions about `pfn_to_bfn` continuity. Test signals include block I/O merging tests under Xen, page-offset boundary cases, non-contiguous grant/bfn mappings, and builds with different Xen/Linux page-size configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/biomerge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/cpu_hotplug.c -->
# sources/distributed-fs/ceph-client/drivers/xen/cpu_hotplug.c

## Purpose
`cpu_hotplug.c` watches Xenstore CPU availability and mirrors Xen vCPU online/offline state into Linux CPU present/hotplug state.

## Important APIs, types, and functions
Important functions are `enable_hotplug_cpu`, `disable_hotplug_cpu`, `vcpu_online`, `vcpu_hotplug`, `handle_vcpu_hotplug_event`, `setup_cpu_watcher`, and `setup_vcpu_hotplug_event`.

## Control flow
A late initcall registers a Xenstore notifier for PV/PVH-capable Xen domains. When Xenstore is available, it registers a watch on `cpu`, then scans possible CPUs. For each `cpu/N/availability`, `"online"` registers/presents the CPU if needed, while `"offline"` offlines the device under the hotplug lock, unregisters Xen arch CPU state, and clears present. Watch callbacks parse the CPU number from the changed path and reapply the state.

## State and persistence
State is Linux CPU present/online state plus Xen arch CPU registration. The watch object is static. Xenstore availability is external persistent configuration for the domain.

## Dependencies and integration points
It depends on Xenstore watches/notifiers, CPU hotplug/device APIs, `xen_arch_register_cpu`, `xen_arch_unregister_cpu`, and Xen domain type checks.

## Risks and test signals
Risks include parsing unexpected Xenstore paths, ignored registration errors, races with normal CPU hotplug, initial-domain read failures, and policy differences between x86 PV/PVH and other Xen domains. Test signals include Xenstore CPU online/offline changes, CPUs outside `nr_cpu_ids`, non-hotpluggable CPUs, device_offline failures, Xenstore unavailable at init, and domain-type matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/cpu_hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/dbgp.c -->
# sources/distributed-fs/ceph-client/drivers/xen/dbgp.c

## Purpose
`dbgp.c` provides Xen Dom0 hooks around USB EHCI debug port reset/startup so the hypervisor can coordinate debug-port ownership during controller reset.

## Important APIs, types, and functions
The internal helper is `xen_dbgp_op`. Exported functions are `xen_dbgp_reset_prep` and `xen_dbgp_external_startup`, except when early DBGP printk owns the symbols.

## Control flow
Callers pass a USB HCD. Outside the Xen initial domain the helpers return success without hypercalls. In Dom0, the helper fills `physdev_dbgp_op` with operation code and, for PCI controllers, segment/bus/devfn and PCI bus type. It then calls `HYPERVISOR_physdev_op(PHYSDEVOP_dbgp_op, ...)`.

## State and persistence
No driver state is stored. The effects are transient hypervisor coordination around debug-port reset phases.

## Dependencies and integration points
It depends on USB HCD/EHCI headers, optional PCI identification, Xen physdev hypercalls, and Xen initial-domain detection. It integrates with USB debug-port reset paths.

## Risks and test signals
Risks include unknown bus fallback for non-PCI controllers, hypercall failures disrupting USB reset, symbol availability under `CONFIG_EARLY_PRINTK_DBGP`, and Dom0-only behavior hiding issues in guests. Test signals include PCI EHCI debug-port reset in Dom0, non-PCI controller calls, non-Xen no-op paths, and hypervisor error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/dbgp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/efi.c -->
# sources/distributed-fs/ceph-client/drivers/xen/efi.c

## Purpose
`efi.c` implements Xen paravirtual EFI runtime services. It installs EFI function pointers that proxy runtime calls through Xen platform hypercalls and provides Xen-aware EFI memory descriptor lookup/config-table validation.

## Important APIs, types, and functions
Runtime wrappers include `xen_efi_get_time`, `set_time`, `get_wakeup_time`, `set_wakeup_time`, `get_variable`, `get_next_variable`, `set_variable`, `query_variable_info`, `get_next_high_mono_count`, `update_capsule`, `query_capsule_caps`, and `xen_efi_reset_system`. Public setup and helpers are `xen_efi_runtime_setup`, `efi_mem_desc_lookup`, and `xen_efi_config_table_is_usable`.

## Control flow
Each wrapper builds a `XENPF_efi_runtime_call` platform op, copies scalar structures or sets guest handles for buffers, invokes `HYPERVISOR_platform_op`, and returns either `EFI_UNSUPPORTED` or Xen-reported EFI status. Setup assigns these wrappers into global `efi` ops. Reset maps EFI cold/warm/shutdown to Xen reboot or poweroff. Memory descriptor lookup falls back to native lookup when not paravirt or when a native EFI memmap exists; otherwise it asks Xen firmware info for the descriptor covering the physical address.

## State and persistence
The file mutates global EFI runtime function pointers during early init. Variable/time/capsule state persists in firmware or Xen-mediated firmware storage, not in this driver.

## Dependencies and integration points
It depends on Linux EFI core types, Xen platform/firmware hypercalls, Xen guest handles, Xen reboot operations, and EFI paravirt feature flags.

## Risks and test signals
Risks include structure layout mismatches guarded by `BUILD_BUG_ON`, missing hypercall error propagation in memory descriptor lookup, guest-handle validity for user buffers, runtime-version gating for EFI 2.0 calls, reset default `BUG()`, and accepting unsafe config table memory types. Test signals include EFI time/variable operations under Xen, capsule capability queries, native versus paravirt memmap lookup, invalid hypercall returns, config table validation by memory type, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/Makefile -->
# sources/distributed-fs/ceph-client/drivers/xen/events/Makefile

## Purpose
This Makefile builds the Xen event-channel core object from base, two-level ABI, and FIFO ABI implementations.

## Important APIs, types, and functions
It declares `obj-y += events.o` and composes `events-y` from `events_base.o`, `events_2l.o`, and `events_fifo.o`.

## Control flow
Kbuild always links the three event-channel implementation objects into the `events.o` composite when the parent Xen events directory is built.

## State and persistence
No runtime state exists in the Makefile; it defines build graph state only.

## Dependencies and integration points
It is reached from `drivers/xen/Makefile` via `obj-y += events/` and provides the event-channel implementation used by the rest of Xen interrupt handling.

## Risks and test signals
Risks include missing an ABI implementation from the composite, stale object names, or unconditional inclusion of objects that no longer build on an architecture. Test signals include Xen builds across x86/ARM/ARM64, FIFO and two-level event-channel runtime selection, and kbuild dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_2l.c -->
# sources/distributed-fs/ceph-client/drivers/xen/events/events_2l.c

## Purpose
`events_2l.c` implements Xen's classic two-level event-channel ABI for Linux IRQ delivery. It supplies the `evtchn_ops` backend that manages pending/mask bits, CPU binding masks, event scanning, unmask semantics, resume cleanup, and debug dumps.

## Important APIs, types, and functions
Important state includes per-CPU `cpu_evtchn_mask`, `current_word_idx`, and `current_bit_idx`. Operations are `evtchn_2l_max_channels`, `evtchn_2l_remove`, `evtchn_2l_bind_to_cpu`, `evtchn_2l_clear_pending`, `evtchn_2l_set_pending`, `evtchn_2l_is_pending`, `evtchn_2l_mask`, `evtchn_2l_unmask`, `evtchn_2l_handle_events`, `evtchn_2l_resume`, `evtchn_2l_percpu_deinit`, and initializer `xen_evtchn_2l_init`. `xen_debug_interrupt` dumps shared-info and per-CPU event-channel state.

## Control flow
Initialization assigns `evtchn_ops` to the two-level implementation. Binding sets the port bit in exactly one CPU mask. Mask/pending operations manipulate Xen shared-info bitmaps with sync bitops. Unmask either clears the local mask and locally resends a pending event by setting `evtchn_pending_sel`/`evtchn_upcall_pending`, or calls Xen `EVTCHNOP_unmask` when the port is non-local or HVM pending delivery requires hypervisor help. Event handling prioritizes the timer VIRQ, exchanges and clears the vCPU selector word, scans pending words/bits fairly from saved cursors, and dispatches each active port through `handle_irq_for_port`.

## State and persistence
State is per-CPU event mask and scan cursor state plus Xen shared-info pending/mask/select fields. Resume and CPU deinit clear local masks; shared hypervisor state is rebuilt by higher-level event code.

## Dependencies and integration points
It depends on Xen shared info, vCPU info, event-channel hypercalls, sync bitops, IRQ core `generic_handle_irq`, and internal event helpers from `events_internal.h`.

## Risks and test signals
Risks include bit-width mismatches between `xen_ulong_t` and `unsigned long`, lost event edges during unmask, fairness cursor arithmetic using word count constants, timer VIRQ priority interactions, HVM/PV delivery differences, CPU hotplug mask cleanup, and verbose debug interrupt locking. Test signals include high event-channel counts, CPU rebinding, pending-while-masked delivery, HVM and PV guests, timer VIRQ latency, suspend/resume, CPU offline/online, and debug interrupt output consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_2l.c -->
