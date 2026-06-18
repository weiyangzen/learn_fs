# subset-b-005595 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/scx200_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/scx200_wdt.c

## Purpose
`scx200_wdt.c` is a legacy NatSemi SCx200 watchdog driver exposing the chipset watchdog through the old misc `/dev/watchdog` interface. It programs the SCx200 configuration block watchdog registers directly with port I/O, supports magic close, configurable timeout, reboot notifier shutdown handling, and a single-open policy.

## Important APIs, types, and functions
The driver is built around module parameters `margin` and `nowayout`, global state `wdto_restart`, `expect_close`, `open_lock`, and `scx_lock`, and the miscdevice `scx200_wdt_miscdev`. Core hardware helpers are `scx200_wdt_ping()`, `scx200_wdt_update_margin()`, `scx200_wdt_enable()`, and `scx200_wdt_disable()`. User entry points are `scx200_wdt_open()`, `scx200_wdt_release()`, `scx200_wdt_write()`, and `scx200_wdt_ioctl()`, with `scx200_wdt_notify_sys()` disabling the timer on halt or poweroff when allowed.

## Control flow
Module init verifies `scx200_cb_present()`, reserves the SCx200 watchdog I/O slice, computes `wdto_restart = margin * W_SCALE`, disables the watchdog into a known state, registers a reboot notifier, then registers `/dev/watchdog`. Opening the device atomically claims `open_lock` and enables hardware by clearing WDTO/status, writing `W_ENABLE`, then pinging. Writes ping and scan for `V` to permit a later clean close. Ioctls report support/status, ping, and update timeout. Release disables only when magic close was seen and `nowayout` is false.

## State and persistence behavior
Persistent runtime state is in globals plus hardware registers under `scx200_cb_base`. No filesystem state exists. Hardware state persists across process close unless magic close is honored, and may persist across shutdown if `nowayout` is set. `open_lock` prevents concurrent users; `scx_lock` serializes port register sequences.

## Dependencies and integration points
The file depends on `<linux/scx200.h>` for configuration-block offsets and detection, direct `outb/outw` I/O, the misc watchdog minor, reboot notifiers, and watchdog ioctl constants. It predates the modern `watchdog_device` core and therefore implements the character-device behavior itself.

## Risks and test signals
Risks include unchecked large `margin` overflow into 16-bit `wdto_restart`, direct I/O to legacy registers, partial hardware changes before notifier or misc registration failures, and global `expect_close` semantics. Test signals are successful build on SCx200-enabled x86, correct rejection when the configuration block is absent or busy, single-open enforcement, `WDIOC_SETTIMEOUT` updating the reload value, magic-close behavior with and without `nowayout`, reboot-notifier disable on halt/poweroff, and observable WDTO reloads on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/scx200_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/shwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/shwdt.c

## Purpose
`shwdt.c` drives the integrated watchdog in SuperH processors. The hardware overflow period is extremely short, so the driver uses a kernel timer to keep clearing the hardware while userspace is considered alive, and intentionally stops that internal pinging after the configured userspace heartbeat expires.

## Important APIs, types, and functions
Important state is `clock_division_ratio`, `heartbeat`, `nowayout`, global `next_heartbeat`, and `struct sh_wdt` containing MMIO base, device, optional clock, spinlock, and timer. Watchdog operations are `sh_wdt_start()`, `sh_wdt_stop()`, `sh_wdt_keepalive()`, and `sh_wdt_set_heartbeat()`. `sh_wdt_ping()` is the internal timer callback that clears WOVF/IOVF and reloads the counter. Probe/remove/shutdown are `sh_wdt_probe()`, `sh_wdt_remove()`, and `sh_wdt_shutdown()`.

## Control flow
Module init validates the divisor then registers a platform driver named `sh-wdt`. Probe rejects per-CPU platform IDs, maps the resource, gets an optional clock, initializes the global `sh_wdt_dev`, validates heartbeat, registers the watchdog, sets up the timer, and enables runtime PM. Start resumes PM, enables the clock, schedules the internal timer, sets WTCSR mode/divisor bits, clears the counter and reset status, and enables counting. Userspace pings only extend `next_heartbeat`; the timer performs the real hardware keepalive until that deadline passes.

## State and persistence behavior
The active deadline is global rather than per-device, matching the single global hardware assumption. Timer state, PM usage count, and hardware WTCSR/RSTCSR/CNT registers persist until stop, shutdown, suspend, or reset. There is no durable software state.

## Dependencies and integration points
The driver depends on SuperH watchdog register helpers from `<asm/watchdog.h>`, platform resources, runtime PM, clocks, the watchdog core, and timer infrastructure. It uses a static `struct watchdog_device`, so it is intended for one global watchdog instance.

## Risks and test signals
The main risk is timing: low HZ, slow scheduling, or wrong divisor can allow hardware overflow even when userspace is healthy. Global `next_heartbeat` and static watchdog state would be unsafe for multiple devices, but probe forbids them. Test with valid and invalid divisors/heartbeats, start/stop/ping paths, timer expiry after missed userspace heartbeat, PM suspend/resume, shutdown stop, SH2 reset-status handling, and register traces around WTCSR/CNT writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/shwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/simatic-ipc-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/simatic-ipc-wdt.c

## Purpose
`simatic-ipc-wdt.c` supports watchdogs on Siemens SIMATIC IPC 227E and 427E systems. It controls fixed I/O ports for watchdog enable/trigger/timeout selection and, depending on platform mode, clears a secondary SAFE_EN_N reset gate through either a legacy I/O register or P2SB-discovered GPIO MMIO.

## Important APIs, types, and functions
Important constants are `WD_ENABLE_IOADR`, `WD_TRIGGER_IOADR`, timeout table `wd_timeout_table`, and SAFE_EN_N values. Watchdog operations are `wd_start()`, `wd_stop()`, `wd_ping()`, and `wd_set_timeout()`. Platform setup is split into `wd_secondary_enable()`, `wd_setup()`, and `simatic_ipc_wdt_probe()`. The global `wdd_data` is the registered `watchdog_device`.

## Control flow
Probe reads `struct simatic_ipc_platform` from platform data and accepts only 227E or 427E modes. It reserves the enable and trigger I/O ports; for 227E it temporarily reserves the GP status port, while for 427E it uses `p2sb_bar()` to locate GPIO community register space and maps PAD configuration. `wd_setup()` detects previous watchdog-triggered boot, resets the alarm bit, sets macro mode and default timeout index, and enables the secondary reset path. It then sets nowayout, asks the core to stop on reboot, and registers the watchdog.

## State and persistence behavior
The driver stores minimal state globally in `wdd_data` and `wd_reset_base_addr`. Hardware state persists in the I/O enable register, trigger side effects, timeout selection bits, and SAFE_EN_N gate. Bootstatus is captured from `WD_TRIGGERED` before the setup write clears alarm state.

## Dependencies and integration points
It integrates with the SIMATIC IPC base platform driver via `simatic_ipc_platform`, with x86 P2SB helpers for hidden bridge BAR discovery, fixed legacy I/O resource management, MMIO mapping, and the watchdog core.

## Risks and test signals
Risks are platform-data mismatch, fixed I/O port conflicts, incorrect timeout rounding via `find_closest()`, and failure to enable SAFE_EN_N, which would turn the watchdog into alarm-only behavior. Tests should cover both device modes, resource conflict failures, bootstatus when `WD_TRIGGERED` is set, timeout requests mapping to the supported table, trigger reads as pings, and reboot stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/simatic-ipc-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sl28cpld_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sl28cpld_wdt.c

## Purpose
`sl28cpld_wdt.c` is the watchdog client for Kontron SL28 CPLD watchdog blocks. It accesses a parent MFD regmap at an offset supplied by firmware, supports timeout programming, get-timeleft, optional WDT timeout pin assertion, nowayout lock behavior, and preservation of already-running hardware.

## Important APIs, types, and functions
`struct sl28cpld_wdt` embeds `struct watchdog_device`, a parent `regmap`, block offset, and `assert_wdt_timeout`. Watchdog ops are `sl28cpld_wdt_ping()`, `sl28cpld_wdt_start()`, `sl28cpld_wdt_stop()`, `sl28cpld_wdt_set_timeout()`, and `sl28cpld_wdt_get_timeleft()`. Probe reads properties `reg` and `kontron,assert-wdt-timeout-pin`.

## Control flow
Probe requires a parent device and regmap, allocates state, reads the register offset, initializes min/max timeout of 1..255 seconds, then reads `WDT_CTRL` and `WDT_TIMEOUT` before modifying hardware. A zero hardware timeout is replaced with `WDT_DEFAULT_TIMEOUT`; device-tree or module timeout can override through `watchdog_init_timeout()`. If the CPLD lock bit was set, nowayout is forced. If hardware was already enabled, start is called to normalize mode and `WDOG_HW_RUNNING` is set before managed registration.

## State and persistence behavior
State is split between per-device data and CPLD registers. The lock bit can make stop impossible after start when nowayout sets `WDT_CTRL_LOCK`. Existing enabled hardware is treated as running state and surfaced to the watchdog core.

## Dependencies and integration points
The file depends on platform-device probing under the SL28 CPLD MFD, firmware properties, regmap read/write/update_bits, and standard watchdog helpers including `watchdog_stop_on_reboot()`.

## Risks and test signals
Risks include global module parameter `nowayout` being updated when one device is locked, write failures leaving timeout/core state diverged, and enabling lock bits too early. Tests should exercise property errors, default timeout fallback for zero, lock-bit detection, already-running hardware, timeout writes, ping writes of `0x6b`, get-timeleft reads, and optional timeout-pin assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sl28cpld_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/smsc37b787_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/smsc37b787_wdt.c

## Purpose
`smsc37b787_wdt.c` is a legacy misc-device watchdog driver for the SMSC 37B787 Super I/O watchdog. It unlocks the chip configuration port, selects logical device 8, configures GPIO pins for watchdog output, programs timeout units and values, and implements `/dev/watchdog` ioctls directly.

## Important APIs, types, and functions
Low-level helpers are `open_io_config()`, `close_io_config()`, `select_io_device()`, `write_io_cr()`, and `read_io_cr()`. Medium-level helpers program GPIO and watchdog registers: `gpio_bit12()`, `gpio_bit13()`, `wdt_timer_units()`, `wdt_timeout_value()`, `wdt_timer_conf()`, and `wdt_timer_ctrl()`. High-level controls include `wb_smsc_wdt_initialize()`, `wb_smsc_wdt_shutdown()`, `wb_smsc_wdt_set_timeout()`, `wb_smsc_wdt_reset_timer()`, `wb_smsc_wdt_open()`, `wb_smsc_wdt_write()`, `wb_smsc_wdt_ioctl()`, and reboot notifier `wb_smsc_wdt_notify_sys()`.

## Control flow
Module init reserves ports `0x3f0..0x3f1`, clamps timeout, initializes pin and watchdog register state, registers the reboot notifier, and registers misc `/dev/watchdog`. Opening is single-user, optionally pins the module for nowayout, and enables the current timeout. Writes parse magic close when allowed and always reload. Ioctls expose support/status, enable/disable options, keepalive, and timeout conversion between seconds and optional minutes mode. Release disables only on expected close; unexpected close resets the timer.

## State and persistence behavior
Global state tracks units, timeout, open flag, close expectation, and nowayout. Hardware state is in Super I/O configuration registers and GPIO function bits and persists until explicitly reset or power-cycled. `io_lock` serializes multi-port unlock/select/write sequences.

## Dependencies and integration points
The driver uses direct x86-style port I/O, misc watchdog minor, reboot notifiers, and user access helpers. It is not integrated with the modern watchdog core.

## Risks and test signals
Risks include fixed I/O address assumptions, no chip ID probing, unit-minute support compiled out as unreliable, and potential board pin side effects. Test by reserving conflicts, open/write/magic-close semantics, `WDIOC_SETOPTIONS`, timeout range and unit conversion, reboot notifier shutdown, and register trace validation for GPIO selection and watchdog reset on real SMSC hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/smsc37b787_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/softdog.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/softdog.c

## Purpose
`softdog.c` implements a software-only watchdog using high-resolution timers. On expiry it can ignore reboot, panic, emergency restart, or run a configured reboot command before falling back to emergency restart. It also optionally supports pretimeout notification.

## Important APIs, types, and functions
Module parameters are `soft_margin`, `nowayout`, `soft_noboot`, `soft_panic`, `soft_reboot_cmd`, and `soft_active_on_boot`. Main timers are `softdog_ticktock` and optional `softdog_preticktock`. Important callbacks are `softdog_fire()`, `softdog_pretimeout()`, `softdog_ping()`, `softdog_stop()`, `reboot_work_fn()`, and `reboot_kthread_fn()`. `softdog_dev` is the registered watchdog.

## Control flow
Init validates/configures timeout via `watchdog_init_timeout()`, applies nowayout and stop-on-reboot, initializes timers, optionally starts immediately, then registers the watchdog. Starting and pinging are the same operation: the expiry hrtimer is armed for `w->timeout`, and the module refcount is acquired if the timer was previously inactive. Expiry releases that refcount and performs the configured action. If a reboot command is used, work launches a kernel thread and the timer is extended by the default margin to force emergency restart if orderly restart stalls.

## State and persistence behavior
State is entirely volatile: hrtimer active state, module reference count, and the static `soft_reboot_fired` guard. There is no hardware persistence, so it cannot recover from CPU lockups, interrupt-disabled stalls, or scheduler failures except where the expiry path still runs.

## Dependencies and integration points
The driver integrates with watchdog core, hrtimers, workqueues, kthreads, `kernel_restart()`, `emergency_restart()`, and optional `CONFIG_SOFT_WATCHDOG_PRETIMEOUT`.

## Risks and test signals
Risks include giving a false sense of hardware recovery, module refcount imbalance if timer paths change, pretimeout calculation when pretimeout exceeds timeout, and reboot-command path needing scheduler/workqueue progress. Tests should cover init parameter ranges, start/stop reference behavior, expiry modes, `soft_active_on_boot`, pretimeout notification, nowayout close behavior through the core, and emergency fallback after a reboot command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/softdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.h

## Purpose
`sp5100_tco.h` is the private register-definition header for the AMD SP5100/SB800/EFCH TCO watchdog driver. It centralizes MMIO register offsets, control bits, PM I/O ports, chipset-specific PM register indexes, hardcoded EFCH addresses, and revision threshold constants.

## Important APIs, types, and functions
The header defines no functions or types. Key macros include `SP5100_WDT_CONTROL(base)`, `SP5100_WDT_COUNT(base)`, `SP5100_WDT_START_STOP_BIT`, `SP5100_WDT_FIRED`, `SP5100_WDT_ACTION_RESET`, `SP5100_WDT_DISABLED`, and `SP5100_WDT_TRIGGER_BIT`. It also defines PM register names for SP5100, SB800, and EFCH layouts and `AMD_ZEN_SMBUS_PCI_REV`.

## Control flow
There is no executable control flow. `sp5100_tco.c` uses these constants to classify the chipset, read the PM watchdog base registers, enable decode and one-second resolution, map MMIO, and manipulate the common control/count watchdog registers.

## State and persistence behavior
The header stores no state. Its constants describe hardware state fields that persist in chipset PM and watchdog registers.

## Dependencies and integration points
It includes `<linux/bitops.h>` for `BIT()` and `GENMASK()` and is private to `sp5100_tco.c`. The macro values encode externally documented AMD/ATI register contracts.

## Risks and test signals
The main risk is incorrect magic values: a wrong address, mask, or revision threshold will make setup fail or program unrelated chipset state. Test by compiling the driver, checking macro use against datasheets for each layout, and validating detected MMIO/PM register traces on SP5100, SB800, EFCH, and Zen EFCH-MMIO systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sp805_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sp805_wdt.c

## Purpose
`sp805_wdt.c` drives ARM PrimeCell SP805 watchdog blocks on AMBA. It supports timeout/load conversion from clock rate, time-left reporting, restart handling, suspend/resume, optional ACPI-style `clock-frequency`, and preserving boot-enabled hardware.

## Important APIs, types, and functions
`struct sp805_wdt` embeds the watchdog, spinlock, MMIO base, optional clock, clock rate, AMBA device, and current load value. Key helpers are `wdt_is_running()`, `wdt_setload()`, `wdt_timeleft()`, `wdt_restart()`, `wdt_config()`, `wdt_ping()`, `wdt_enable()`, and `wdt_disable()`. Probe/remove and PM handlers are `sp805_wdt_probe()`, `sp805_wdt_remove()`, `sp805_wdt_suspend()`, and `sp805_wdt_resume()`.

## Control flow
Probe maps the AMBA resource, obtains rate from clock or property, deasserts optional reset, initializes watchdog metadata, computes default load, and if hardware is already running, reprograms it and marks `WDOG_HW_RUNNING`. Start enables the clock and calls `wdt_config(false)`, which unlocks registers, writes load, clears interrupt, enables interrupt/reset, relocks, and flushes posted writes. Ping rewrites load and clears interrupt without re-enabling the clock. Stop disables control and the clock. Restart writes a minimal load and enables reset for rapid reboot.

## State and persistence behavior
`load_val` and `timeout` cache the programmed period; hardware load/control/interrupt/lock registers persist until changed. Active watchdogs are stopped during suspend and restored on resume. Clock enable state follows start/stop.

## Dependencies and integration points
The file integrates with AMBA IDs, PrimeCell resources, optional clocks and resets, device properties, watchdog core restart priority, and PM ops.

## Risks and test signals
Risks include wrong clock-rate source, load overflow/rounding, disabling clocks while hardware is active, and time-left interpretation around the two-stage interrupt/reset cycle. Tests should cover clock property fallback, load clamping, running-hardware takeover, start/ping/stop register traces, restart path, suspend/resume only when active, and AMBA ID matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sp805_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sprd_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sprd_wdt.c

## Purpose
`sprd_wdt.c` drives Spreadtrum watchdog controllers with separate enable and RTC clocks, lock/unlock-protected registers, reset and interrupt/pretimeout support, and suspend/resume integration.

## Important APIs, types, and functions
`struct sprd_wdt` holds MMIO base, watchdog device, two clocks, and IRQ. Helpers include `sprd_wdt_lock()`, `sprd_wdt_unlock()`, `sprd_wdt_get_cnt_value()`, `sprd_wdt_load_value()`, `sprd_wdt_enable()`, and managed cleanup `sprd_wdt_disable()`. Watchdog ops are `sprd_wdt_start()`, `sprd_wdt_stop()`, `sprd_wdt_set_timeout()`, `sprd_wdt_set_pretimeout()`, and `sprd_wdt_get_timeleft()`. `sprd_wdt_isr()` clears interrupt and notifies pretimeout.

## Control flow
Probe maps registers, gets clocks, requests the IRQ with `IRQF_NO_SUSPEND`, initializes 3..60 second limits, enables both clocks and the new-version bit, registers cleanup, sets nowayout from Kconfig, initializes timeout, and registers. Starting waits for the load-busy bit to clear, writes timeout and pretimeout counters split into high/low registers, enables count/interrupt/reset bits, and sets `WDOG_HW_RUNNING`. Stop clears those enable bits. Suspend stops an active watchdog and fully disables clocks; resume re-enables clocks and restarts if active.

## State and persistence behavior
The watchdog timeout/pretimeout values are in core fields and load registers. The controller has explicit lock state and busy state; clock state is owned by enable/disable helpers. No durable software state exists.

## Dependencies and integration points
It integrates with platform resources, device tree compatible `sprd,sp9860-wdt`, two named clocks, IRQ pretimeout notification, PM sleep ops, and watchdog core.

## Risks and test signals
Risks include busy-bit timeout causing failed pings, pretimeout validation allowing values greater than timeout if core does not reject them, clock imbalance on error paths, and interrupt clear races. Tests should cover clock failure unwind, IRQ pretimeout delivery, busy polling timeout, start/stop bit updates, timeout/pretimeout reloads, time-left conversion, and suspend/resume restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sprd_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/st_lpc_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/st_lpc_wdt.c

## Purpose
`st_lpc_wdt.c` uses the ST LPC block in watchdog mode. It loads the low-power alarm timer, controls LPC watchdog enable, and configures reset masking/type through a syscon regmap.

## Important APIs, types, and functions
`struct st_wdog_syscfg` describes syscon registers/masks; `struct st_wdog` stores MMIO base, device, regmap, syscfg, clock, clock rate, and warm-reset flag. Key functions are `st_wdog_setup()`, `st_wdog_load_timer()`, `st_wdog_start()`, `st_wdog_stop()`, `st_wdog_set_timeout()`, `st_wdog_keepalive()`, `st_wdog_probe()`, `st_wdog_remove()`, `st_wdog_suspend()`, and `st_wdog_resume()`.

## Control flow
Probe requires device-tree property `st,lpc-mode` equal to `ST_LPC_MODE_WDT`, maps registers, obtains `st,syscfg`, enables the clock, computes `max_timeout`, initializes the global watchdog device, reads `timeout-sec`, registers, then unmasks watchdog reset via `st_wdog_setup(true)`. Start writes `LPC_WDT_OFF`; timeout/ping load `timeout * clkrate` into the LPA register and start it. Suspend stops an active watchdog, masks reset, and disables the clock; resume reverses that and reloads/restarts if active.

## State and persistence behavior
The driver uses a static global `st_wdog_dev`, so only one instance is represented. Hardware state persists in LPC timer registers and syscon reset gate/type bits. Clock rate determines all timeout encoding.

## Dependencies and integration points
Dependencies include ST LPC DT bindings, syscon/regmap, clock framework, device tree, and watchdog core. `stih407_syscfg` supplies enable mask data for compatible `st,stih407-lpc`.

## Risks and test signals
Risks include static singleton behavior, timeout overflow if clock rates are unexpectedly high, reset gate misconfiguration, and resume unregistering on clock-enable failure. Tests should validate mode rejection, syscfg phandle failures, max-timeout calculation, cold/warm reset bit programming, timeout/ping register writes, and suspend/resume transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/st_lpc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/starfive-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/starfive-wdt.c

## Purpose
`starfive-wdt.c` drives StarFive JH7100 and JH7110 watchdogs. It abstracts variant register layouts, handles locked registers, runtime PM, resets, two-clock enablement, optional early start, get-timeleft, and two-stage timeout behavior on JH7110.

## Important APIs, types, and functions
`struct starfive_wdt_variant` describes register offsets, unlock key, bit shifts, interrupt-clear polling, and `double_timeout`. `struct starfive_wdt` stores watchdog, spinlock, MMIO, clocks, variant, frequency, count, and suspend reload value. Important functions include clock/reset helpers, `starfive_wdt_unlock()/lock()`, `starfive_wdt_int_clr()`, `starfive_wdt_set_reload_count()`, `starfive_wdt_max_timeout()`, `starfive_wdt_get_timeleft()`, `starfive_wdt_keepalive()`, `starfive_wdt_start()`, `starfive_wdt_stop()`, PM wrappers, timeout setter, probe/remove/shutdown, and runtime/system PM callbacks.

## Control flow
Probe maps MMIO, gets clocks, enables runtime PM or clocks, deasserts resets, selects variant from DT, computes max timeout, initializes timeout, programs count, applies nowayout and reboot/unregister stop policy, then either starts early and marks hardware running or stops the block before registration. Start unlocks, disables for safety, enables reset, clears pending interrupt, loads count, enables, and relocks. Timeout changes recompute count, halving it for double-timeout variants, then reload while enabled.

## State and persistence behavior
Per-device state tracks the encoded count and saved suspend reload count. Hardware lock state is bracketed by the spinlock. Runtime PM owns clock enable state; system suspend saves current count, stops the watchdog, force-suspends, and resume restores the saved count and restarts active devices.

## Dependencies and integration points
It depends on DT compatibles `starfive,jh7100-wdt` and `starfive,jh7110-wdt`, clock names `apb` and `core`, reset arrays, PM runtime, watchdog core, and register polling.

## Risks and test signals
Risks include overflow in `timeout * freq`, double-timeout off-by-one behavior, failure to release runtime PM after early probe errors, and lock/unlock imbalance. Tests should cover both variants, interrupt-clear polling timeout, max-timeout math, early_enable, runtime PM start/stop, suspend/resume active and inactive cases, get-timeleft before/after IRQ status, and restart/shutdown policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/starfive-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/stm32_iwdg.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/stm32_iwdg.c

## Purpose
`stm32_iwdg.c` drives STM32 independent watchdog hardware. It computes prescaler/reload values from the LSI clock, optionally uses a peripheral clock and early wakeup interrupt on STM32MP1, supports pretimeout notification, and can take over boot-enabled watchdogs.

## Important APIs, types, and functions
`struct stm32_iwdg_data` describes variant features; `struct stm32_iwdg` stores watchdog, variant data, registers, clocks, and LSI rate. Register helpers are `reg_read()` and `reg_write()`. Watchdog ops are `stm32_iwdg_start()`, `stm32_iwdg_ping()`, `stm32_iwdg_set_timeout()`, and `stm32_iwdg_set_pretimeout()`. Setup helpers include `stm32_iwdg_clk_init()`, `stm32_iwdg_irq_init()`, `stm32_iwdg_isr()`, and `stm32_iwdg_probe()`.

## Control flow
Probe selects variant from DT, maps registers, enables clocks, initializes min timeout and `max_hw_heartbeat_ms`, requests optional early-wakeup IRQ and wakeup-source handling, applies nowayout, reads timeout from DT, and if boot-enabled handling is configured, starts hardware with deterministic values and sets `WDOG_HW_RUNNING`. Start enables write access, chooses a power-of-two prescaler, writes prescaler/reload/early-wakeup values, enables the peripheral, waits for PVU/RVU bits to clear, then reloads.

## State and persistence behavior
There is no stop operation because independent watchdogs generally cannot be stopped after start. Timeout and pretimeout live in core fields; hardware registers retain the last prescaler/reload/window/early-wakeup settings until reset.

## Dependencies and integration points
The driver depends on DT compatibles `st,stm32-iwdg` and `st,stm32mp1-iwdg`, clocks `lsi` and optional `pclk`, optional IRQ and wakeup integration, polling helpers, and watchdog core.

## Risks and test signals
Risks include prescaler/reload rounding errors, no ability to stop after bad configuration, pretimeout defaulting to three quarters of timeout, and rate-dependent min/max constraints. Tests should cover both variants, missing clocks, optional IRQ absent/present, wakeup-source setup, timeout and pretimeout changes while active, boot-enabled takeover, status polling timeout, and reload writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/stm32_iwdg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/stmp3xxx_rtc_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/stmp3xxx_rtc_wdt.c

## Purpose
`stmp3xxx_rtc_wdt.c` is a small watchdog frontend for STMP3xxx/i.MX23/i.MX28 RTC-based watchdog hardware. It delegates actual register programming to platform data supplied by the RTC parent.

## Important APIs, types, and functions
The driver uses module parameter `heartbeat`, static `stmp3xxx_wdd`, and platform data `struct stmp3xxx_wdt_pdata` with `wdt_set_timeout`. Watchdog ops are `wdt_start()`, `wdt_stop()`, and `wdt_set_timeout()`. Reboot behavior is handled by `wdt_notify_sys()`.

## Control flow
Probe stores the child device as watchdog drvdata, clamps heartbeat, sets parent, registers the watchdog, and registers a reboot notifier. Start calls the parent callback with timeout converted from seconds to 1 kHz ticks. Stop passes zero. Reboot notification deliberately keeps the watchdog enabled for `SYS_DOWN`, but stops it for halt and poweroff. Suspend stops if active; resume restarts if active.

## State and persistence behavior
The watchdog device is static and singleton. Hardware state is managed by the RTC parent and persists according to the parent callback. The status includes `WATCHDOG_NOWAYOUT_INIT_STATUS`, reflecting build-time nowayout policy.

## Dependencies and integration points
It depends on `<linux/stmp3xxx_rtc_wdt.h>`, platform data from an RTC MFD/parent, reboot notifiers, and watchdog core managed registration.

## Risks and test signals
Risks are null or invalid platform data, tick conversion overflow near `UINT_MAX / 1000`, static singleton limitations, and notifier behavior that intentionally leaves watchdog active during restart. Tests should validate parent callback calls, heartbeat clamping, halt/poweroff stop, restart keep-enabled behavior, and suspend/resume active-state preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/stmp3xxx_rtc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/stpmic1_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/stpmic1_wdt.c

## Purpose
`stpmic1_wdt.c` is the watchdog driver for the STPMIC1 PMIC. It controls watchdog start, stop, ping, and timeout through PMIC regmap registers exposed by the parent MFD.

## Important APIs, types, and functions
`struct stpmic1_wdt` stores a parent `struct stpmic1 *` and embedded `watchdog_device`. Watchdog ops are `pmic_wdt_start()`, `pmic_wdt_stop()`, `pmic_wdt_ping()`, and `pmic_wdt_set_timeout()`. Probe is `pmic_wdt_probe()`.

## Control flow
Probe requires a parent device and parent driver data, allocates state, fills watchdog metadata with 1..256 second bounds and default 30 seconds, reads optional timeout, applies nowayout, stores drvdata, and registers. Start/stop update `WCHDG_CR` start bit, ping sets the ping bit, and timeout writes `timeout - 1` to `WCHDG_TIMER_CR`.

## State and persistence behavior
Software state is per-device. Hardware state persists in PMIC watchdog control and timer registers and may survive across SoC resets depending on PMIC power behavior.

## Dependencies and integration points
The file integrates with the STPMIC1 MFD, regmap, OF compatible `st,stpmic1-wdt`, platform devices, and the watchdog core.

## Risks and test signals
Risks include parent-data absence, regmap write failures, timeout off-by-one encoding, and PMIC reset behavior differing from SoC-local watchdogs. Tests should cover parent validation, min/max/default timeout, timeout register values for 1 and 256 seconds, start/stop/ping bit updates, nowayout behavior, and devm unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/stpmic1_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sun4v_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sun4v_wdt.c

## Purpose
`sun4v_wdt.c` implements a watchdog using SPARC sun4v hypervisor support. Instead of direct registers, it programs the machine watchdog through hypervisor calls and validates optional platform machine-description properties.

## Important APIs, types, and functions
Global `wdd` is the watchdog device. Watchdog ops are `sun4v_wdt_ping()` for start/ping, `sun4v_wdt_stop()`, and `sun4v_wdt_set_timeout()`. Initialization uses `mdesc_grab()`, `mdesc_node_by_name()`, `mdesc_get_property()`, `sun4v_hvapi_register()`, and watchdog registration.

## Control flow
Init obtains the machine description, finds the `platform` node, registers the core hypervisor API, validates `watchdog-resolution` and `watchdog-max-timeout`, adjusts `max_timeout` if needed, initializes timeout from module parameter, applies nowayout, and registers. Ping/start calls `sun4v_mach_set_watchdog(timeout * 1000, NULL)` and maps `HV_EINVAL` to `-EINVAL`. Stop programs zero. Exit unregisters hypervisor API and the watchdog.

## State and persistence behavior
State is mostly hypervisor-owned. The Linux driver stores configured timeout and max range, but countdown state persists in the hypervisor until reset, stop, or new timeout.

## Dependencies and integration points
It depends on SPARC hypervisor APIs, machine description access, module parameters, and watchdog core. It is platform-specific and returns `-ENODEV` or `-EINVAL` for missing/invalid hypervisor metadata.

## Risks and test signals
Risks include milliseconds/seconds conversion boundaries, hypervisor rounding to resolution, property validation rejecting systems, and leaving the hypervisor API registered on partial failures. Tests should cover absent platform node, invalid resolution/max-timeout properties, module timeout validation, HV_EINVAL mapping, stop programming zero, and exit unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sun4v_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sunplus_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sunplus_wdt.c

## Purpose
`sunplus_wdt.c` drives the Sunplus SP7021 watchdog/timer block. It handles magic command words for stop/resume/unlock/lock, max hardware heartbeat constraints, get-timeleft, and restart using a minimal count.

## Important APIs, types, and functions
`struct sp_wdt_priv` stores watchdog, MMIO base, clock, and reset control. Watchdog ops are `sp_wdt_start()`, `sp_wdt_stop()`, `sp_wdt_ping()`, `sp_wdt_get_timeleft()`, and `sp_wdt_restart()`. Probe is `sp_wdt_probe()` and reset cleanup is `sp_reset_control_assert()`.

## Control flow
Probe enables the clock, gets/deasserts shared reset, maps MMIO, initializes timeout defaults and `max_hw_heartbeat_ms`, applies nowayout and stop-on-reboot, sets restart priority, and registers. Ping writes either `WDT_CONMAX` for too-large core timeout under max-hw-heartbeat management or unlocks, writes a count derived from `timeout * 90000 >> 4`, and locks. Start writes resume; stop writes stop. Restart stops, unlocks, writes count 1, locks, resumes, and lets hardware reset.

## State and persistence behavior
Hardware state is in WDT control/count registers and shared reset. Software state is per-device. Because the hardware maximum is about 11 seconds, the watchdog core may need to ping periodically for larger user timeouts via `max_hw_heartbeat_ms`.

## Dependencies and integration points
It depends on DT compatible `sunplus,sp7021-wdt`, clock and reset frameworks, MMIO, and watchdog restart priority.

## Risks and test signals
Risks include `get_timeleft()` returning raw ticks rather than seconds, shared reset side effects, count truncation, and core reliance for long timeouts. Tests should validate magic command order, max-hw heartbeat behavior, restart reset, timeout count calculations, stop-on-reboot, and clock/reset cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sunplus_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sunxi_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sunxi_wdt.c

## Purpose
`sunxi_wdt.c` drives Allwinner sunxi watchdog variants. It abstracts variant-specific register offsets, reset bits, timeout shift, and key values while exposing standard watchdog start/stop/ping/set-timeout and restart operations.

## Important APIs, types, and functions
`struct sunxi_wdt_reg` describes register layout and keying; `struct sunxi_wdt_dev` stores watchdog, MMIO base, and selected layout. Core functions are `sunxi_wdt_restart()`, `sunxi_wdt_ping()`, `sunxi_wdt_set_timeout()`, `sunxi_wdt_stop()`, and `sunxi_wdt_start()`. Variant tables cover sun4i, sun6i, sun20i, and sun55i compatibles.

## Control flow
Probe allocates state, selects variant data from DT, maps registers, initializes 1..16 second bounds, reads optional timeout, applies nowayout and restart priority, stores drvdata, stops the watchdog into a known state, sets stop-on-reboot, and registers. Start programs reset behavior, writes the timeout selector from `wdt_timeout_map`, reloads, and enables. Restart forces reset mode, enables with the lowest timeout, reloads, then loops re-enabling until reset occurs.

## State and persistence behavior
Timeout is stored in the watchdog device and encoded into mode register selector bits. Variant key values are ORed into protected register writes where required. Hardware state persists in mode/config/control registers.

## Dependencies and integration points
The driver depends on OF match data, platform MMIO resources, watchdog core, restart handlers, and Allwinner-specific register layouts.

## Risks and test signals
Risks include timeout rounding by incrementing unsupported values only once, write-key omissions for variants, infinite loop in restart by design, and differences between reset mask/value meanings. Tests should cover all compatible variants, unsupported timeout requests, stop clearing enable, ping reload, restart reset path, boot probe stop, and timeout map boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sunxi_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/tegra_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/tegra_wdt.c

## Purpose
`tegra_wdt.c` drives the Tegra watchdog by pairing watchdog ID 0 with timer 5 in the Tegra timer block. It programs a fixed 1 MHz periodic timer and configures the watchdog to reset after multiple expirations.

## Important APIs, types, and functions
`struct tegra_wdt` stores watchdog plus watchdog and timer register bases. Watchdog ops are `tegra_wdt_start()`, `tegra_wdt_stop()`, `tegra_wdt_ping()`, `tegra_wdt_set_timeout()`, and `tegra_wdt_get_timeleft()`. Probe and PM handlers are `tegra_wdt_probe()`, `tegra_wdt_suspend()`, and `tegra_wdt_resume()`.

## Control flow
Probe maps the timer block, allocates state, derives watchdog and timer base offsets, initializes 1..255 second timeout bounds, applies nowayout, sets stop-on-unregister, registers, and saves drvdata. Start programs timer 5 for a quarter-second-equivalent cadence, writes watchdog config with timeout and reset enable, and starts the counter. Stop unlocks watchdog, disables it, and stops the timer. Timeout changes restart the active watchdog.

## State and persistence behavior
The device state is per-platform-device. Hardware state persists in watchdog config/status/cmd and timer PTV registers. Suspend stops active hardware; resume restarts it if the core still marks it active.

## Dependencies and integration points
It depends on DT compatible `nvidia,tegra30-timer`, platform MMIO, watchdog core, and PM sleep ops. It assumes timer 5 is unused by clocksource code.

## Risks and test signals
Risks include conflicts if timer 5 is repurposed, time-left arithmetic around expiration count, no boot-running takeover, and direct fixed-clock assumption. Tests should cover register offsets, start/stop/ping writes, timeout restart while active, suspend/resume, time-left decoding, and interaction with Tegra clocksource allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/tegra_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/tqmx86_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/tqmx86_wdt.c

## Purpose
`tqmx86_wdt.c` drives the TQMx86 PLD watchdog. The hardware supports power-of-two timeouts from 1 to 4096 seconds and cannot be stopped once started.

## Important APIs, types, and functions
`struct tqmx86_wdt` embeds the watchdog and I/O base. Watchdog ops are `tqmx86_wdt_start()` and `tqmx86_wdt_set_timeout()`. Probe maps an I/O resource, initializes timeout bounds, forces nowayout, programs the initial timeout, and registers.

## Control flow
Probe obtains an `IORESOURCE_IO`, maps it with `devm_ioport_map()`, fills `watchdog_device`, reads optional module/firmware timeout, sets nowayout to Kconfig value, and calls `tqmx86_wdt_set_timeout()` before registration. Timeout requests are rounded up to a power of two; the encoded value is `ilog2(t) | 0x90` plus an offset for sub-second hardware encodings. Start writes `0x81` to the config/status register.

## State and persistence behavior
The driver stores only the rounded timeout and I/O base. Hardware cannot be stopped through this driver, so started state persists until reset or power cycle.

## Dependencies and integration points
It depends on a platform device named `tqmx86-wdt`, I/O port resources, log2 helpers, and watchdog core.

## Risks and test signals
Risks include rounding timeout upward without reporting an error, no stop operation, and encoding assumptions for PLD revisions. Tests should validate I/O resource absence, timeout rounding for edge values, register writes to `WDCFG` and `WDCS`, nowayout behavior, and core acceptance of start-only hardware with `max_hw_heartbeat_ms`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/tqmx86_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ts4800_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ts4800_wdt.c

## Purpose
`ts4800_wdt.c` drives the Technologic Systems TS-4800 watchdog through a syscon regmap register. Hardware supports only a few feed values, so the driver maps requested timeouts to the closest supported 2 or 10 second feed.

## Important APIs, types, and functions
`struct ts4800_wdt` stores watchdog, regmap, feed offset, and selected feed value. Important functions are `ts4800_write_feed()`, `ts4800_wdt_start()`, `ts4800_wdt_stop()`, `ts4800_wdt_set_timeout()`, and `ts4800_wdt_probe()`. `ts4800_wdt_map` defines timeout-to-register mappings.

## Control flow
Probe parses the `syscon` phandle and offset, obtains the parent regmap, initializes min/max timeout from the mapping table, applies nowayout and optional timeout, defaults to maximum if unset, calls set-timeout to choose feed value, disables the write-only watchdog into a known state, then registers. Start writes the selected feed value; stop writes the disable value.

## State and persistence behavior
Because the feed register is write-only, probe cannot discover prior state and always disables it. Selected timeout and feed value are cached in software; hardware state persists in syscon logic.

## Dependencies and integration points
It depends on OF syscon phandle format, regmap, platform devices, and watchdog core.

## Risks and test signals
Risks include unsupported timeout rounding logic, write-only state loss at probe, and syscon phandle reference leaks if paths change. Tests should cover missing phandle/offset/regmap, timeout mapping below/between/above supported values, start/stop writes, nowayout close behavior, and initialization disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ts4800_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ts72xx_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ts72xx_wdt.c

## Purpose
`ts72xx_wdt.c` drives external CPLD watchdog logic on Technologic Systems TS-72xx boards. It controls separate feed and control MMIO resources and supports coarse timeout choices up to 8 seconds hardware heartbeat.

## Important APIs, types, and functions
`struct ts72xx_wdt_priv` stores control/feed registers, watchdog, and encoded control value. Watchdog ops are `ts72xx_wdt_start()`, `ts72xx_wdt_stop()`, `ts72xx_wdt_ping()`, and `ts72xx_wdt_settimeout()`. Probe maps two resources and registers the watchdog.

## Control flow
Probe maps control and feed registers, initializes watchdog metadata with min timeout 1 and max hardware heartbeat 8000 ms, applies nowayout and optional timeout, stores drvdata, and registers. Timeout setter maps requested seconds to 1, 2, 4, or 8 second control encodings, updates the reported timeout, and if active restarts hardware. Start feeds first, then writes control; stop feeds then writes disable.

## State and persistence behavior
Software caches the current `regval`; hardware state persists in CPLD control and feed side effects. Core may extend user-visible timeouts using `max_hw_heartbeat_ms`.

## Dependencies and integration points
It depends on platform MMIO resources, OF compatible `technologic,ts7200-wdt`, and watchdog core.

## Risks and test signals
Risks include a default timeout larger than hardware heartbeat relying on core keepalives, no explicit stop-on-reboot, and coarse rounding behavior. Tests should cover two-resource mapping, timeout encoding, active restart on timeout change, feed/control write order, nowayout, and core-managed heartbeat for long default timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ts72xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/twl4030_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/twl4030_wdt.c

## Purpose
`twl4030_wdt.c` drives the TWL4030 PM receiver watchdog over the TWL I2C API. It exposes start/stop/set-timeout operations for a 1..30 second PMIC watchdog.

## Important APIs, types, and functions
The hardware access wrapper is `twl4030_wdt_write()`. Watchdog ops are `twl4030_wdt_start()`, `twl4030_wdt_stop()`, and `twl4030_wdt_set_timeout()`. Probe allocates a `watchdog_device`, stops hardware, and registers. Platform PM callbacks stop/resume active hardware.

## Control flow
Probe allocates and fills a watchdog with default 30 seconds, min 1, max 30, applies nowayout, saves drvdata, stops hardware by writing zero, and registers. Start writes `timeout + 1` to the watchdog config register; stop writes zero. Timeout setter only updates software; the new value takes effect on next start or resume.

## State and persistence behavior
Software state is the allocated watchdog. Hardware state resides in the TWL PM receiver register. Suspend stops active watchdogs and resume starts them again if the core still marks them active.

## Dependencies and integration points
It depends on the TWL MFD API `twl_i2c_write_u8()`, platform devices, OF compatible `ti,twl4030-wdt`, and watchdog core.

## Risks and test signals
Risks include off-by-one timeout encoding, no ping operation despite advertising keepalive through start semantics, and stop-on-probe changing bootloader state. Tests should cover I2C write errors, timeout boundaries, suspend/resume active behavior, start/stop register values, and nowayout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/twl4030_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/txx9wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/txx9wdt.c

## Purpose
`txx9wdt.c` drives TXx9 SoC timer hardware in watchdog mode. It programs timer compare, divider, mode, and watchdog-control registers using the IM bus clock.

## Important APIs, types, and functions
Global state includes mapped `txx9wdt_reg`, clock `txx9_imclk`, and spinlock `txx9_lock`. Watchdog ops are `txx9wdt_ping()`, `txx9wdt_start()`, `txx9wdt_stop()`, and `txx9wdt_set_timeout()`. Probe/remove/shutdown manage the clock, MMIO mapping, timeout bounds, and registration.

## Control flow
Probe gets and enables `imbus_clk`, maps timer registers, validates timeout against `WD_MAX_TIMEOUT`, initializes the static watchdog, applies nowayout, and registers. Start writes compare as `WD_TIMER_CLK * timeout`, sets clock divider and watchdog timer mode, clears pending interrupt, enables counting, and pings. Ping writes watchdog interrupt enable/clear. Stop writes watchdog disable and clears timer enable. Timeout changes stop and restart.

## State and persistence behavior
The driver uses singleton globals and a static watchdog. Hardware timer state persists in TXx9 timer registers until stop/reset. Clock state is enabled for the lifetime of the registered driver.

## Dependencies and integration points
It depends on `<asm/txx9tmr.h>` register layout/macros, platform MMIO, clock framework, raw MMIO access, and watchdog core.

## Risks and test signals
Risks include division by zero if clock rate is bad, singleton assumptions, timeout max computed from runtime clock, and raw register access ordering. Tests should cover clock failures, timeout clamp to default, start/stop/ping register writes, set-timeout restart, remove clock cleanup, shutdown stop, and max-timeout math for board clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/txx9wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/uniphier_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/uniphier_wdt.c

## Purpose
`uniphier_wdt.c` drives the Socionext UniPhier watchdog through a parent syscon regmap. It supports power-of-two timeouts, reset-selection setup, polling around counter clear status, and standard start/stop/ping operations.

## Important APIs, types, and functions
`struct uniphier_wdt_dev` embeds watchdog and regmap. Important helpers are `uniphier_watchdog_ping()`, `__uniphier_watchdog_start()`, `__uniphier_watchdog_stop()`, `__uniphier_watchdog_restart()`, `uniphier_watchdog_start()`, `uniphier_watchdog_stop()`, and `uniphier_watchdog_set_timeout()`. Probe is `uniphier_wdt_probe()`.

## Control flow
Probe gets the parent syscon regmap, initializes timeout defaults and bounds, applies optional module/DT timeout and nowayout, stores drvdata, stops the watchdog, programs reset selection to reset both targets, and registers. Start rounds the timeout to a power of two, waits until status is clear, writes period, enables and clears, then polls until status is set. Ping writes the clear bit and waits for status set.

## State and persistence behavior
Timeout is rounded and stored in the watchdog device. Hardware state persists in syscon registers `WDTTIMSET`, `WDTRSTSEL`, and `WDTCTRL`. No durable software state exists.

## Dependencies and integration points
It depends on DT compatible `socionext,uniphier-wdt`, parent syscon regmap, polling helpers, and watchdog core stop-on-reboot.

## Risks and test signals
Risks include power-of-two rounding not reflected until set/start, polling timeouts, parent syscon assumptions, and `WDIOF_OVERHEAT` option being a semantic mismatch for a watchdog reset source. Tests should cover parent lookup, reset-selection write, ping/start poll timeouts, rounded timeout requests, stop clearing enable, and nowayout/stop-on-reboot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/uniphier_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/via_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/via_wdt.c

## Purpose
`via_wdt.c` drives watchdog hardware in VIA chipsets. It allocates/configures a small MMIO window through PCI config space, registers a watchdog, and uses an internal timer to ping the hardware at 500 ms intervals while userspace heartbeat has not expired.

## Important APIs, types, and functions
Global state includes `wdt_dev`, allocated `wdt_res`, mapped `wdt_mem`, `mmio`, timer `timer`, and `next_heartbeat`. Watchdog ops are `wdt_start()`, `wdt_stop()`, `wdt_ping()`, and `wdt_set_timeout()`. Hardware helpers include `wdt_reset()` and timer callback `wdt_timer_tick()`. PCI entry points are `wdt_probe()` and `wdt_remove()`.

## Control flow
Probe enables the PCI device, allocates an MMIO address, writes it to PCI config, enables watchdog/MMIO decode, reserves and maps the region, initializes timeout and bootstatus, registers the watchdog, then starts the internal ping timer in case BIOS had already enabled hardware. Start writes timeout count, sets running and trigger bits, updates `next_heartbeat`, and arms the timer. The timer keeps resetting hardware while userspace deadline has not passed or the watchdog is inactive; otherwise it stops pinging and logs impending reboot.

## State and persistence behavior
Software heartbeat deadline is separate from the hardware one-second heartbeat. Hardware fired/running/count/control bits persist in the chipset. Removing the driver unregisters, deletes the timer, unmaps, releases resources, and disables PCI device.

## Dependencies and integration points
It depends on VIA PCI IDs, PCI config access, global I/O memory resource allocation, timers/jiffies, MMIO, and watchdog core.

## Risks and test signals
Risks include BIOS/PnP MMIO setup failure, global singleton state, timer continuing around removal if not synchronized, and heartbeat policy split between userspace and internal timer. Tests should cover MMIO allocation/config verification, bootstatus fired bit, internal timer behavior before/after user heartbeat expiry, timeout count writes, stop clearing running bit, and resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/via_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/visconti_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/visconti_wdt.c

## Purpose
`visconti_wdt.c` drives Toshiba Visconti watchdog hardware. It uses a clock-derived divider to run the watchdog at 2 MHz, programs min/max/count/control registers, and supports time-left reporting.

## Important APIs, types, and functions
`struct visconti_wdt_priv` embeds watchdog, MMIO base, and divider. Watchdog ops are `visconti_wdt_start()`, `visconti_wdt_stop()`, `visconti_wdt_ping()`, `visconti_wdt_get_timeleft()`, and `visconti_wdt_set_timeout()`. Probe maps registers, enables clock, computes divider, and registers.

## Control flow
Probe maps MMIO, gets/enables the clock, derives `div = clk_freq / 2MHz`, initializes timeout bounds from the 32-bit max counter, applies nowayout and stop-on-unregister, initializes optional timeout, and registers. Start writes divider, min zero, max as `timeout * 2MHz`, clears control, and writes the start/stop command. Stop writes control stop state and command. Ping writes clear command. Timeout changes clear the counter before updating max to avoid immediate expiry.

## State and persistence behavior
Software stores divider and timeout; hardware counter/control/max state persists until changed. The clock is devm-enabled for device lifetime.

## Dependencies and integration points
It depends on DT compatible `toshiba,visconti-wdt`, platform MMIO, clock framework, watchdog core, and devm resources.

## Risks and test signals
Risks include divider truncation when clock is not an integer multiple of 2 MHz, timeout multiplication overflow if bounds are wrong, no stop-on-reboot, and author string typo being harmless metadata. Tests should cover zero clock rejection, divider calculation, start/stop/ping command writes, timeout update while active, get-timeleft conversion, and max-timeout boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/visconti_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/w83627hf_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/w83627hf_wdt.c

## Purpose
`w83627hf_wdt.c` drives many Winbond/Nuvoton Super I/O watchdog variants through extended-function configuration ports. It detects supported chip IDs, selects watchdog logical device 8, configures watchdog output pins/control/status registers, and registers a modern watchdog device.

## Important APIs, types, and functions
Chip variants are enumerated in `enum chips`; register globals `cr_wdt_timeout`, `cr_wdt_control`, and `cr_wdt_csr` are selected by chip ID. Super I/O helpers are `superio_enter()`, `superio_exit()`, `superio_select()`, `superio_outb()`, and `superio_inb()`. Core routines are `wdt_find()`, `w83627hf_init()`, `wdt_set_time()`, `wdt_start()`, `wdt_stop()`, `wdt_set_timeout()`, and `wdt_get_time()`. `wdt_use_alt_key()` is a DMI quirk for alternate unlock keys.

## Control flow
Init applies DMI quirks, probes ports `0x2e` then `0x4e`, logs chip name, initializes timeout and nowayout, sets stop-on-reboot, configures the chip, and registers. Chip init activates the watchdog logical device, applies chip-specific output pin routing or KBRST pulse enablement, optionally disables an already-running watchdog if `early_disable` is set or reloads it otherwise, sets seconds mode, disables keyboard/mouse watchdog cancellation, captures and clears card-reset status, and exits configuration mode.

## State and persistence behavior
Global state records selected port, register addresses, unlock/lock keys, and static watchdog data. Hardware configuration persists in Super I/O logical-device registers; bootstatus is captured from the CSR and then cleared.

## Dependencies and integration points
The driver depends on x86 port I/O, muxed region reservation, DMI quirks, watchdog core, and chip-specific Super I/O register contracts.

## Risks and test signals
Risks include broad chip matrix with subtle register differences, touching pin muxes on boards where BIOS configured alternate WDTO pins, singleton global state, and timeout setter not programming hardware until start. Tests should cover both probe addresses, each known ID mapping, DMI alternate key path, early_disable, bootstatus capture/clear, seconds mode programming, start/stop/get_time, and reboot stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/w83627hf_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/w83877f_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/w83877f_wdt.c

## Purpose
`w83877f_wdt.c` is a legacy misc-device driver for the Winbond W83877F watchdog. Because the hardware timeout is very short, the driver runs an internal timer that pings hardware frequently while userspace is within its longer heartbeat deadline.

## Important APIs, types, and functions
Global state includes `timeout`, `nowayout`, timer `timer`, `next_heartbeat`, `wdt_is_open`, `wdt_expect_close`, and `wdt_spinlock`. Hardware helpers are `wdt_timer_ping()`, `wdt_change()`, `wdt_startup()`, `wdt_turnoff()`, and `wdt_keepalive()`. File operations are `fop_open()`, `fop_write()`, `fop_close()`, and `fop_ioctl()`. Reboot notifier is `wdt_notify_sys()`.

## Control flow
Init validates timeout, reserves configuration and ping ports, registers reboot notifier, and registers misc `/dev/watchdog`. Opening single-claims the device and calls startup, which sets the userspace deadline, arms the internal timer, and enables hardware. The timer reads `WDT_PING` every quarter second while before `next_heartbeat`; if the deadline is missed, it stops pinging. Writes parse magic close when allowed and extend the deadline. Close disables only after magic close; unexpected close deletes the timer but leaves hardware running.

## State and persistence behavior
Hardware enable state is in W83877F configuration register 0x14 and ping side effects on port 0x443. Software deadline and open flags are volatile globals. `nowayout` prevents magic-close detection but does not call `__module_get()`.

## Dependencies and integration points
It uses fixed x86 I/O ports, misc watchdog minor, reboot notifiers, timers/jiffies, spinlocks, and user copy helpers rather than the watchdog core.

## Risks and test signals
Risks include fixed-port conflicts, stale internal timer state after unexpected close, no bootstatus detection, and reliance on frequent kernel timer scheduling. Tests should cover resource conflicts, single-open, internal timer ping cadence, missed heartbeat behavior, ioctl enable/disable/timeout, reboot notifier turnoff, and magic close with nowayout false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/w83877f_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/w83977f_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/w83977f_wdt.c

## Purpose
`w83977f_wdt.c` is a legacy misc-device driver for the Winbond W83977F Super I/O watchdog. It programs Aux2 watchdog registers and Aux1 GPIO pin functions through fixed Super I/O index/data ports.

## Important APIs, types, and functions
Global state includes `timeout`, converted `timeoutW`, `timer_alive`, `testmode`, `expect_close`, and a spinlock. Hardware functions are `wdt_start()`, `wdt_stop()`, `wdt_keepalive()`, `wdt_set_timeout()`, and `wdt_get_status()`. User operations are `wdt_open()`, `wdt_release()`, `wdt_write()`, and `wdt_ioctl()`, with reboot notifier `wdt_notify_sys()`.

## Control flow
Init converts the requested timeout to hardware counter units, reserves ports `0x3f0/0x3f1`, registers notifier and miscdevice. Opening claims the device, pins the module if nowayout, and starts hardware. Start unlocks Super I/O, selects Aux2 to set timeout/LED/status, activates Aux2, selects Aux1 to route GP16/GP13 unless testmode, activates Aux1, then locks. Writes parse magic close and reload by rewriting the timeout. Ioctls expose support, status, bootstatus, options, keepalive, and timeout.

## State and persistence behavior
Timeout is stored in seconds and hardware counter units, with conversion `(units * 30) - 15`. Hardware Super I/O pin routing and watchdog timer registers persist until stop or power cycle. Unexpected close keeps the watchdog running and reloads it.

## Dependencies and integration points
It depends on fixed x86 I/O ports, misc watchdog minor, reboot notifier, spinlocks, and direct user-copy ioctl handling.

## Risks and test signals
Risks include no chip probing, board-specific timeout unit assumptions, fixed port conflicts, and pin mux changes unless testmode is used. Tests should cover timeout conversion boundaries 15..7635 seconds, start/stop register sequences, testmode path, status bit readback, magic close/nowayout, ioctl options, and reboot notifier shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/w83977f_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wafer5823wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/wafer5823wdt.c

## Purpose
`wafer5823wdt.c` is a legacy misc-device watchdog driver for ICP Wafer 5823 single-board computers. It uses two configurable I/O ports: one to start/restart with a timeout value and one to stop/pat the watchdog.

## Important APIs, types, and functions
Global state includes configurable `wdt_stop`, `wdt_start`, `timeout`, `nowayout`, `wafwdt_is_open`, `expect_close`, and `wafwdt_lock`. Hardware helpers are `wafwdt_start()`, `wafwdt_stop()`, and `wafwdt_ping()`. User operations are `wafwdt_open()`, `wafwdt_close()`, `wafwdt_write()`, and `wafwdt_ioctl()`. Reboot notifier is `wafwdt_notify_sys()`.

## Control flow
Init validates timeout, reserves start/stop ports, registers reboot notifier, and registers misc `/dev/watchdog`. Open claims the device and starts hardware by writing timeout to start port then reading it. Writes scan for magic close when allowed and ping by reading stop then start under lock. Ioctl supports support/status/bootstatus, enable/disable options, keepalive, and timeout changes that stop then restart. Close stops only with magic close; unexpected close pings and leaves it running.

## State and persistence behavior
Software state is global and volatile. Hardware state persists through I/O port side effects until stopped or reset. There is no probing; users must know the correct ports.

## Dependencies and integration points
It uses fixed/configurable x86 I/O ports, misc watchdog minor, reboot notifiers, spinlocks, and watchdog ioctl constants.

## Risks and test signals
Risks include wrong port parameters touching unrelated hardware, no module pinning for nowayout, no bootstatus, and legacy misc implementation. Tests should cover port reservation for same/different start-stop ports, timeout range 1..255, open/write/close semantics, ioctl options, reboot notifier stop, and correct read/write port ordering on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/wafer5823wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.c

## Purpose
`watchdog_core.c` is the generic Linux watchdog registration core. It validates `struct watchdog_device` instances, assigns watchdog IDs, registers the character-device side through `watchdog_dev_register()`, supports deferred registration before misc/char infrastructure is ready, manages reboot/restart/PM notifiers, and provides managed registration helpers.

## Important APIs, types, and functions
Exported APIs are `watchdog_init_timeout()`, `watchdog_set_restart_priority()`, `watchdog_register_device()`, `watchdog_unregister_device()`, and `devm_watchdog_register_device()`. Internal functions include deferred-list helpers, `watchdog_check_min_max_timeout()`, `watchdog_reboot_notifier()`, `watchdog_restart_notifier()`, `watchdog_pm_notifier()`, `___watchdog_register_device()`, `__watchdog_register_device()`, `__watchdog_unregister_device()`, and init/exit routines.

## Control flow
`watchdog_init_timeout()` first validates a driver/module timeout, then `timeout-sec` firmware property, otherwise keeps the existing default and warns on invalid inputs. Registration is deferred until `watchdog_init()` has called `watchdog_dev_init()` and drained the deferred list. Real registration validates mandatory ops, allocates an ID from DT alias or an IDA, registers the char device, handles legacy watchdog0 conflicts by retrying a nonzero ID, applies global `stop_on_reboot`, registers reboot notifier, optional restart handler, and optional PM notifier. Unregister removes those hooks and frees the ID.

## State and persistence behavior
Core state includes `watchdog_ida`, deferred registration list and mutex, `wtd_deferred_reg_done`, and module parameter `stop_on_reboot`. Per-watchdog state is stored in each `watchdog_device` notifier blocks, status bits, ID, timeout, and core private data allocated by `watchdog_dev_register()`.

## Dependencies and integration points
The file depends on IDA allocation, device properties, OF aliases, reboot/restart/PM notifier APIs, tracepoints, `watchdog_dev_*` lower char-device helpers, and public watchdog status/ops contracts.

## Risks and test signals
Risks include ID leaks on complex failure paths, notifier registration inconsistencies, deferred unregister races, invalid driver ops accepted too early, and global `stop_on_reboot` overriding driver policy. Tests should cover timeout precedence and invalid fallback, deferred register/unregister before subsystem init, ID alias allocation and legacy watchdog0 retry, restart handler priority, reboot stop behavior with/without stop op, PM notifier paths, devm cleanup, and tracepoint coverage for stop failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.h

## Purpose
`watchdog_core.h` is the private header shared by the watchdog core and watchdog character-device implementation. It defines the core-private device wrapper, maximum watchdog count, internal status bits, and internal function prototypes.

## Important APIs, types, and functions
`MAX_DOGS` limits registered watchdog devices to 32. `struct watchdog_core_data` contains the internal `struct device`, `struct cdev`, back-pointer to `struct watchdog_device`, mutex, keepalive timestamps, open deadline, hrtimer, kthread work, optional pretimeout hrtimer, and internal status bits `_WDOG_DEV_OPEN`, `_WDOG_ALLOW_RELEASE`, and `_WDOG_KEEPALIVE`. It declares `watchdog_dev_register()`, `watchdog_dev_unregister()`, `watchdog_dev_init()`, and `watchdog_dev_exit()`. It also defines `watchdog_have_pretimeout()` and hrtimer-pretimeout helper prototypes or no-op stubs.

## Control flow
The header has no standalone runtime flow, but its declarations define how `watchdog_core.c` delegates character-device registration to `watchdog_dev.c`, and how optional hrtimer pretimeout code is compiled in or compiled out.

## State and persistence behavior
The header defines volatile in-kernel state only. `watchdog_core_data` tracks open/keepalive timing and character device state while a watchdog is registered; it is not durable and is cleaned up on unregister.

## Dependencies and integration points
It depends on Linux cdev, device, hrtimer, kthread, mutex, init, and public watchdog types. It is private to the watchdog subsystem, not a driver-facing public API.

## Risks and test signals
Risks include ABI drift between `watchdog_core.c` and the character-device implementation, max-device assumptions from `MAX_DOGS`, and configuration-dependent pretimeout behavior. Test by building with and without `CONFIG_WATCHDOG_HRTIMER_PRETIMEOUT`, registering more than one watchdog, exercising open/magic-close/keepalive state transitions through `watchdog_dev.c`, and verifying internal status bits are not exposed as public ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_core.h -->
