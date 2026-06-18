# subset-b-005591 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bd9576_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/bd9576_wdt.c

## Purpose
This platform watchdog driver supports ROHM BD9576MUF and BD9573MUF PMIC watchdog blocks exposed by the ROHM MFD parent. It configures the hardware watchdog timing window through the parent regmap and feeds/enables the watchdog through firmware-described GPIO lines.

## Important APIs, types, and functions
`struct bd9576_wdt_priv` holds the enable GPIO, ping GPIO, parent regmap, device pointer, and embedded `watchdog_device`. The watchdog ops are `bd9576_wdt_start`, `bd9576_wdt_stop`, and `bd9576_wdt_ping`; the setup helpers are `find_closest_fast`, `find_closest_slow_by_fast`, `find_closest_slow`, and `bd957x_set_wdt_mode`. Probe uses `dev_get_regmap`, `devm_fwnode_gpiod_get`, `device_property_read_u32_array`, `watchdog_init_timeout`, and `devm_watchdog_register_device`.

## Control Flow
Probe allocates private state, obtains the parent regmap and two parent fwnode GPIOs, reads optional `rohm,hw-timeout-ms`, programs slow or window mode, then registers the watchdog. Start asserts the enable GPIO and immediately pulses the ping GPIO. Ping is a high-low pulse. Stop deasserts the enable GPIO. The watchdog core handles software timeout feeding against the programmed `min_hw_heartbeat_ms`/`max_hw_heartbeat_ms`.

## State and Persistence
Persistent runtime state is limited to GPIO descriptors, regmap pointer, and the registered watchdog. Hardware configuration persists in PMIC registers until the parent device or PMIC reset changes it. The driver does not persist state across reboot and uses `watchdog_stop_on_reboot`.

## Dependencies and Integration Points
The driver depends on the ROHM BD957x MFD, regmap, firmware properties, GPIO descriptors, and the watchdog core. Device-tree or firmware must provide `rohm,watchdog-enable`, `rohm,watchdog-ping`, and optional `rohm,hw-timeout-ms` on the parent node.

## Risks and Test Signals
Risks include invalid timing arrays, window-mode feeds that are too early, missing parent GPIO properties, and rounded hardware margins differing from requested values. Test signals should cover one-value and two-value `rohm,hw-timeout-ms`, bad GPIO/regmap probe deferral, start/ping/stop GPIO sequencing, nowayout behavior, and reboot stop handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bd9576_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bd96801_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/bd96801_wdt.c

## Purpose
This driver manages the watchdog inside the ROHM BD96801 PMIC. It supports interface-feed mode, slow/window timing configuration, optional interrupt-only or reset assertion policy, and detection of watchdog state left running by firmware.

## Important APIs, types, and functions
`struct wdtbd96801` stores the device, regmap, and embedded `watchdog_device`. Core ops are `bd96801_wdt_start`, `bd96801_wdt_stop`, and `bd96801_wdt_ping`. Configuration is handled by `bd96801_set_wdt_mode`, `bd96801_set_heartbeat_from_hw`, and `init_wdg_hw`; `bd96801_irq_hnd` calls `emergency_restart` when the PMIC interrupt is wired. Timing fields use `FIELD_PREP`/`FIELD_GET` against `BD96801_REG_WD_TMO` and `BD96801_REG_WD_CONF`.

## Control Flow
Probe reads `BD96801_REG_WD_CONF`. If the watchdog is already enabled, it rejects unsupported Q&A mode, derives min/max heartbeat from hardware registers, and marks `WDOG_HW_RUNNING`. Otherwise it reads `rohm,hw-timeout-ms`, programs slow or window mode, and applies optional `rohm,wdg-action` values `prstb` or `intb-only`. Start sets interface-feed enable, ping writes the feed bit, and stop clears enable bits.

## State and Persistence
State is maintained in PMIC registers and the watchdog core fields for min/max hardware heartbeat. Running hardware can survive bootloader handoff; the driver preserves existing configuration instead of reinitializing it. The module parameter `nowayout` affects whether stop is permitted.

## Dependencies and Integration Points
The driver integrates with the BD96801 MFD regmap, firmware properties on the parent PMIC node, platform IRQ named `bd96801-wdg`, the Linux reboot path, and the watchdog framework.

## Risks and Test Signals
Key risks are incorrect timeout rounding, unsupported Q&A-mode handoff, interrupt handler returning `IRQ_NONE` after forcing restart, and mismatched action properties. Tests should cover running-at-probe hardware, both timeout property orderings, min/max bounds, IRQ registration, feed/start/stop regmap failures, and `WDOG_HW_RUNNING` keepalive handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bd96801_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/booke_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/booke_wdt.c

## Purpose
`booke_wdt.c` implements the PowerPC Book-E CPU watchdog using per-CPU timer control/status SPRs. It exposes a global watchdog device for Book-E systems and supports optional boot-time enable through module parameters.

## Important APIs, types, and functions
The central object is the static `booke_wdt_dev`. Operations are `booke_wdt_start`, `booke_wdt_stop`, `booke_wdt_ping`, and `booke_wdt_set_timeout`. Low-level helpers run on every CPU through `on_each_cpu`: `__booke_wdt_set`, `__booke_wdt_ping`, `__booke_wdt_enable`, and `__booke_wdt_disable`. On E500, `period_to_sec` and `sec_to_period` translate between watchdog period encodings and seconds.

## Control Flow
Module init sets firmware version from `cur_cpu_spec`, maps the configured period into seconds, applies nowayout, optionally starts the watchdog, and registers the device. Starting clears TSR status and writes TCR with watchdog interrupt/restart control and the encoded period on all CPUs. Ping clears TSR watchdog status on all CPUs. Stopping clears WIE and period fields where hardware permits effective disable.

## State and Persistence
State is held in CPU SPRs, so each CPU must be programmed consistently. There is no storage persistence. On some Book-E hardware, restart-control bits cannot be fully undone once set, so stop is implemented by clearing enable/period fields as far as the architecture permits.

## Dependencies and Integration Points
The driver depends on PowerPC Book-E SPR definitions, timebase frequency, SMP callbacks, and watchdog core registration. E500-specific timeout math uses `ppc_tb_freq` and 64-bit division.

## Risks and Test Signals
Risks include timeout conversion overflow, SMP CPU hotplug assumptions, partial disable semantics, and misconfigured `booke_wdt_period`. Tests should cover E500 and non-E500 builds, start-before-register parameter behavior, ping across CPUs, set_timeout range boundaries, and reboot/reset behavior under real hardware or architecture emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/booke_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cadence_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/cadence_wdt.c

## Purpose
This platform driver supports the Cadence/Xilinx watchdog used by Zynq-class SoCs. It programs the zero-mode, counter-control, restart, and status registers to provide reset-on-timeout or interrupt-on-timeout operation.

## Important APIs, types, and functions
`struct cdns_wdt` stores MMIO base, clock, prescaler selection, reset-vs-IRQ mode, spinlock, and embedded watchdog. Main ops are `cdns_wdt_start`, `cdns_wdt_stop`, `cdns_wdt_reload`, and `cdns_wdt_settimeout`. Probe handles `devm_platform_ioremap_resource`, optional IRQ registration, `devm_clk_get_enabled`, `watchdog_init_timeout`, and `devm_watchdog_register_device`. PM callbacks stop/restart the device around suspend.

## Control Flow
Probe maps registers, reads `reset-on-timeout`, optionally registers an IRQ handler when reset is not used, enables the input clock, chooses a prescaler from the clock rate, and registers the watchdog. Start disables the timer, computes and clamps the counter value, writes the protected CCR and ZMR registers with access keys, selects reset or IRQ output, and kicks the counter. Set-timeout updates `wdd->timeout` and restarts hardware.

## State and Persistence
Runtime state includes selected prescaler, clock handle, MMIO registers, and watchdog core timeout. Hardware registers are volatile and are reprogrammed on resume if the watchdog was active. `watchdog_stop_on_unregister` and reboot stop are requested.

## Dependencies and Integration Points
The driver uses the platform bus, OF compatible `cdns,wdt-r1p2`, Linux clock framework, IRQ subsystem, MMIO accessors, and the watchdog core.

## Risks and Test Signals
Risks include clock-rate based timeout rounding, use of interrupt mode without a valid IRQ, lock coverage around protected register writes, and suspend/resume clock sequencing. Tests should cover reset and interrupt DT modes, 75 MHz threshold selection, max timeout clamping, reload while active, timeout changes, and system suspend with active/inactive watchdog states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cadence_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cgbc_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/cgbc_wdt.c

## Purpose
`cgbc_wdt.c` exposes the Congatec Board Controller watchdog through the Linux watchdog core. It sends packed command frames to the parent CGBC MFD command interface and supports optional pretimeout behavior.

## Important APIs, types, and functions
`struct cgbc_wdt_data` links the parent `cgbc_device_data` with a `watchdog_device`. `struct cgbc_wdt_cmd_cfg` is the packed 15-byte command payload validated by `static_assert`. Watchdog ops are `cgbc_wdt_start`, `cgbc_wdt_stop`, `cgbc_wdt_keepalive`, `cgbc_wdt_set_timeout`, and `cgbc_wdt_set_pretimeout`.

## Control Flow
Probe obtains parent MFD data, initializes timeout limits, applies module parameters, and registers the device. Start computes timeout1 as `timeout - pretimeout` in milliseconds and timeout2 as pretimeout in milliseconds, encodes action bytes for reset-only or SMI-plus-reset, and sends `CGBC_WDT_CMD_INIT`. Ping sends `CGBC_WDT_CMD_TRIGGER`; stop sends an init command with disable mode. Timeout/pretimeout changes restart hardware when active.

## State and Persistence
The driver keeps only current watchdog core timeout/pretimeout and a parent pointer. Hardware state lives in the board controller and is updated by command messages. No persistent storage is used.

## Dependencies and Integration Points
It depends on `linux/mfd/cgbc.h`, the parent CGBC command transport, the platform bus, module parameters, and watchdog core pretimeout support.

## Risks and Test Signals
Risks include millisecond overflow/truncation into three-byte fields, pretimeout greater than timeout, command transport failure, and action encoding mismatches with firmware expectations. Tests should cover disabled, reset-only, and SMI pretimeout modes; module parameter parsing; active timeout changes; command payload byte order; and parent command error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cgbc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cpwd.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/cpwd.c

## Purpose
`cpwd.c` drives the three hardware watchdog timers on Sun CP1400/CP1500 boards. It provides Solaris-compatible miscdevice interfaces for RIC, XIR, and POR watchdogs and handles a known CP1400 PLD interrupt-mask defect.

## Important APIs, types, and functions
`struct cpwd` holds the shared MMIO base, IRQ, options-derived policy, broken-PLD flag, and three subdevice descriptors. Important helpers include `cpwd_toggleintr`, `cpwd_starttimer`, `cpwd_stoptimer`, `cpwd_pingtimer`, `cpwd_getstatus`, `cpwd_brokentimer`, and `cpwd_interrupt`. User APIs are the `cpwd_fops` file operations and ioctls including Linux `WDIOC_*` and SPARC watchdog `WIOC*` commands.

## Control Flow
Probe maps the Open Firmware watchdog node, reads `/options` properties, detects the defective board model, registers three misc devices, and optionally initializes a timer workaround. The first open registers the shared IRQ. Writes and keepalive ioctls reload a selected timer by reading its downcounter. Start writes the limit register and enables interrupts; stop masks interrupt delivery or enters broken-stop maintenance.

## State and Persistence
Global `cpwd_device`, per-subdevice runstatus bits, default timeouts, IRQ registration state, and a workaround timer form runtime state. Firmware option properties influence default behavior but are not modified. The PLD counters and interrupt masks persist until reprogrammed or reset.

## Dependencies and Integration Points
The driver depends on SPARC/Open Firmware resources, `asm/watchdog.h` Solaris ioctl definitions, miscdevice registration, shared IRQ handling, timers, and endian-aware MMIO access.

## Risks and Test Signals
Risks include incorrect minor-to-index mapping in writes, global singleton lifetime, IRQ registration on first open, broken PLD rescheduling, and legacy ioctl compatibility. Tests should cover all three minors, CP1400 broken model behavior, `/options` combinations, interrupt service marking, compat ioctls, and unload with running/stopped timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cpwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cros_ec_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/cros_ec_wdt.c

## Purpose
This driver exposes the ChromeOS Embedded Controller hang-detect watchdog as a Linux watchdog. All hardware control is done by EC host commands rather than local registers.

## Important APIs, types, and functions
`union cros_ec_wdt_data` overlays EC request and response payloads. `cros_ec_wdt_send_cmd` builds `EC_CMD_HANG_DETECT` messages and calls `cros_ec_cmd_xfer_status`. Watchdog ops are `cros_ec_wdt_ping`, `cros_ec_wdt_start`, `cros_ec_wdt_stop`, and `cros_ec_wdt_set_timeout`. Probe uses parent `cros_ec_dev` data and EC status commands.

## Control Flow
Probe sends `GET_STATUS`, maps EC watchdog reset status to `WDIOF_CARDRESET`, clears EC status, initializes min/max from EC constants, and registers the watchdog. Start sends `SET_TIMEOUT` with the current reboot timeout, ping sends `RELOAD`, stop sends `CANCEL`, and set-timeout rolls back the cached timeout if the EC command fails. Suspend stops an active watchdog and resume starts it again.

## State and Persistence
The Linux side stores only the watchdog core object and parent EC pointer. The EC owns actual watchdog timing and reset status, which can persist across AP resets until explicitly cleared during probe.

## Dependencies and Integration Points
The driver depends on the cros_ec platform data/protocol headers, platform device binding name `cros-ec-wdt`, EC command transport, PM callbacks, and watchdog core.

## Risks and Test Signals
Risks include EC command version/payload mismatch, bootstatus clear failure, suspend/resume leaving EC watchdog canceled, and timeout rollback correctness. Tests should cover successful and failing EC commands, AP boot caused by EC watchdog, min/max timeout validation through watchdog core, active suspend/resume, and unregister/reboot stop semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/cros_ec_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9052_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/da9052_wdt.c

## Purpose
`da9052_wdt.c` controls the watchdog inside Dialog DA9052 PMICs. It maps supported PMIC watchdog scales to user-visible seconds, reports PMIC fault-log boot causes, and observes a minimum feed window.

## Important APIs, types, and functions
`struct da9052_wdt_data` stores the embedded watchdog, parent `struct da9052`, and `jpast` timestamp. Core ops are `da9052_wdt_start`, `da9052_wdt_stop`, `da9052_wdt_ping`, and `da9052_wdt_set_timeout`. Register access goes through `da9052_reg_update` and `da9052_reg_read`, with timeout selection in `DA9052_CONTROL_D_REG`.

## Control Flow
Set-timeout first disables the watchdog scale bits, waits at least 150 microseconds when enabling, maps requested seconds to a scale value, programs the PMIC, and updates the watchdog timeout. Start calls set-timeout with the cached timeout; stop passes zero. Ping waits for the watchdog minimum window, toggles the watchdog bit high then low, and returns register errors.

## State and Persistence
The driver caches `jpast` to avoid early feeds and maps `da9052->fault_log` into `bootstatus`. PMIC control registers can be left enabled by firmware; probe detects this, reinitializes the watchdog, and sets `WDOG_HW_RUNNING`.

## Dependencies and Integration Points
It integrates with the DA9052 MFD core, PMIC register definitions, fault log fields, Linux jiffies timing, module timeout/nowayout parameters, and watchdog core.

## Risks and Test Signals
Risks include the `mdelay(msec)` logic when `msec < DA9052_TWDMIN`, exact timeout mapping failures, boot-enabled handoff, and failure while toggling the feed bit. Tests should cover every supported timeout map value, invalid timeout, fault-log bootstatus bits, early ping timing, start/stop register failures, and running-at-probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9052_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9055_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/da9055_wdt.c

## Purpose
This driver manages the Dialog DA9055 PMIC watchdog through DA9055 MFD register helpers. It exposes discrete PMIC timeout scale values and a simple keepalive operation to the watchdog core.

## Important APIs, types, and functions
`struct da9055_wdt_data` contains the watchdog and parent `struct da9055`. Important functions are `da9055_wdt_set_timeout`, `da9055_wdt_ping`, `da9055_wdt_start`, `da9055_wdt_stop`, and `da9055_wdt_probe`. Timeout scales are defined by `da9055_wdt_maps` and programmed through `DA9055_REG_CONTROL_B`; pings write `DA9055_REG_CONTROL_E`.

## Control Flow
Probe allocates state, sets default timeout, configures nowayout, stops the watchdog to leave a known idle state, and registers the watchdog. Start programs the current timeout; stop maps timeout zero; ping waits `DA9055_TWDMIN` milliseconds then sets the watchdog reset bit. Set-timeout validates the requested seconds against the map before updating the PMIC and watchdog core.

## State and Persistence
The driver maintains no separate persistent cache beyond watchdog core timeout and parent pointer. PMIC registers hold enabled/timeout state until changed. Unlike DA9052, this driver does not expose PMIC fault-log bootstatus.

## Dependencies and Integration Points
It depends on the DA9055 MFD core/register helpers, platform device binding `da9055-watchdog`, module nowayout, delay helpers, and watchdog core.

## Risks and Test Signals
Risks include mandatory 256 ms delay in ping paths, unsupported timeout values, register update failures during probe stop, and lack of running-at-probe handoff. Tests should cover all mapped timeouts including 0, 32/33 and 65/66 aliases, invalid timeout rejection, start/stop sequencing, ping timing, and regmap/MFD error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9055_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9062_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/da9062_wdt.c

## Purpose
`da9062_wdt.c` supports DA9062 and DA9061 PMIC watchdogs. It provides watchdog start/stop/ping, discrete timeout scaling, optional software suspend policy, bootloader handoff, and a high-priority restart handler.

## Important APIs, types, and functions
`struct da9062_watchdog` stores the parent `struct da9062`, watchdog device, and `use_sw_pm` flag. Key helpers are `da9062_wdt_read_timeout`, `da9062_wdt_timeout_to_sel`, `da9062_reset_watchdog_timer`, `da9062_wdt_update_timeout_register`, and `da9062_wdt_restart`. Watchdog ops include start, stop, ping, set_timeout, and restart.

## Control Flow
Probe reads optional `dlg,use-sw-pm`, initializes watchdog limits, reads any active PMIC timeout, applies DT timeout overrides, and marks `WDOG_HW_RUNNING` if firmware left the watchdog enabled. Updating timeout disables the scale bits, waits 150-300 us, then writes the new selector. Ping writes the control-F watchdog bit unless the system is already leaving `SYSTEM_RUNNING`. Restart bypasses regmap with unlocked SMBus transfer to write PMIC shutdown.

## State and Persistence
Runtime state includes selected timeout in watchdog core, PMIC register state, `WDOG_HW_RUNNING`, and the suspend policy flag. PMIC watchdog state can persist across bootloader handoff.

## Dependencies and Integration Points
The driver depends on DA9062 MFD/regmap definitions, I2C client access for restart, firmware property `dlg,use-sw-pm`, OF compatible `dlg,da9062-watchdog`, PM callbacks, and watchdog restart priority.

## Risks and Test Signals
Risks include disabling the watchdog during timeout changes, restart in atomic/shutdown context, ping suppression during reboot, and timeout rounding to supported selectors. Tests should cover boot-enabled handoff, each timeout selector, software PM suspend/resume, restart path failure, active set_timeout, and regmap update errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9062_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9063_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/da9063_wdt.c

## Purpose
This driver controls the Dialog DA9063 PMIC watchdog. It supports discrete PMIC timeout selectors, boot-enabled watchdog handoff, optional software power management, and watchdog-based system restart.

## Important APIs, types, and functions
The parent `struct da9063` is used as watchdog driver data. Important helpers are `da9063_wdt_timeout_to_sel`, `da9063_wdt_read_timeout`, `da9063_wdt_disable_timer`, `da9063_wdt_update_timeout`, and `da9063_wdt_restart`. Watchdog ops implement start, stop, ping, set_timeout, and restart.

## Control Flow
Probe obtains the parent MFD object, sets `use_sw_pm` from `dlg,use-sw-pm`, initializes limits and restart priority, reads existing PMIC timeout, applies firmware timeout override, and marks `WDOG_HW_RUNNING` when the hardware was already active. Start/update disables the watchdog, waits 150-300 us, and writes the selector because the timeout field also starts the watchdog. Set-timeout only touches hardware when active. Ping writes `DA9063_WATCHDOG` unless shutdown is in progress. Restart writes `DA9063_SHUTDOWN` via unlocked SMBus and waits.

## State and Persistence
PMIC registers hold actual watchdog state. The driver buffers timeout in `watchdog_device` when inactive because the hardware cannot store a nonzero timeout without starting. Bootloader-enabled state is preserved and reprogrammed.

## Dependencies and Integration Points
It depends on DA9063 MFD/regmap/I2C definitions, platform binding `DA9063_DRVNAME_WATCHDOG`, watchdog restart handling, and optional PM callbacks.

## Risks and Test Signals
Risks include forced disable during active timeout changes, restart path dependence on I2C availability, timeout selector rounding, and inconsistent software PM with always-on watchdog policy. Tests should cover inactive set_timeout buffering, active reprogramming, running-at-probe, restart, suspend/resume with and without `dlg,use-sw-pm`, and regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/da9063_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/davinci_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/davinci_wdt.c

## Purpose
`davinci_wdt.c` supports TI DaVinci/Keystone watchdog timers implemented as a 64-bit timer block with watchdog key sequencing. It is a nowayout watchdog with a restart callback.

## Important APIs, types, and functions
`struct davinci_wdt_device` stores the MMIO base, clock, and embedded watchdog. Core functions are `davinci_wdt_start`, `davinci_wdt_ping`, `davinci_wdt_get_timeleft`, and `davinci_wdt_restart`. Probe uses `devm_clk_get_enabled`, `devm_platform_ioremap_resource`, `watchdog_set_restart_priority`, and `devm_watchdog_register_device`.

## Control Flow
Start disables the timer, configures 64-bit watchdog mode, clears counters, writes PRD12/PRD34 from timeout and clock rate, enables periodic mode, then writes the WDKEY sequence to move pre-active to active. Ping repeats the service key sequence. Get-timeleft checks the timeout flag and subtracts elapsed counter seconds. Restart programs zero period, activates watchdog, then writes an invalid key value to trigger reset.

## State and Persistence
Runtime state is the clock, MMIO registers, timeout in watchdog core, and nowayout status hard-set to true. Once active, the watchdog registers become mostly write-protected except WDKEY fields.

## Dependencies and Integration Points
The driver depends on platform resources, OF compatible `ti,davinci-wdt`, the clock framework, MMIO accessors, watchdog core, and restart priority integration.

## Risks and Test Signals
Risks include 64-bit timeout multiplication, clock-rate changes, inability to stop once active, timeleft underflow if the counter exceeds timeout, and restart key sequencing. Tests should cover heartbeat module parameter validation, clock probe deferral, timeleft before/after timeout flag, ping sequence, restart assertion, and register programming under different clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/davinci_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/db8500_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/db8500_wdt.c

## Purpose
This driver exposes the ST-Ericsson DB8500 A9 watchdog controlled through PRCMU firmware calls. It uses a single static watchdog device for all CPU watchdog operations.

## Important APIs, types, and functions
Operations are `db8500_wdt_start`, `db8500_wdt_stop`, `db8500_wdt_keepalive`, and `db8500_wdt_set_timeout`, each wrapping `prcmu_*_a9wdog` functions. The static `db8500_wdt` stores watchdog info, ops, and min/max limits. PM callbacks are `db8500_wdt_suspend` and `db8500_wdt_resume`.

## Control Flow
Probe sets the parent, nowayout, disables auto-off on sleep for CPU1, loads a default 10-minute timeout into all watchdogs, and registers the device. Start/stop/kick call PRCMU for `PRCMU_WDOG_ALL`. Set-timeout stops, loads a millisecond timeout, and restarts. Suspend/resume reconfigure auto-off policy and reload/restart the watchdog when active.

## State and Persistence
State is primarily in PRCMU-managed watchdog hardware plus the static watchdog object and module timeout parameter. There is no per-device allocation or persistent storage.

## Dependencies and Integration Points
The driver depends on DBx500 PRCMU MFD APIs, platform bus name `db8500_wdt`, watchdog core, and legacy platform suspend/resume callbacks.

## Risks and Test Signals
Risks include static singleton assumptions, timeout module parameter being overwritten to 600 during probe, ignored PRCMU return values in set_timeout, min_timeout allowing zero, and sleep auto-off behavior. Tests should cover PRCMU failure injection, active suspend/resume, timeout bounds, stop/start sequencing, and platform probe/register errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/db8500_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/diag288_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/diag288_wdt.c

## Purpose
`diag288_wdt.c` implements the IBM s390 diag 288 watchdog for z/VM and LPAR. On expiration it requests a CP command under z/VM or a system restart under LPAR.

## Important APIs, types, and functions
The static `wdt_dev` is registered only on CPUs with `S390_CPU_FEATURE_D288`. Operations are `wdt_start`, `wdt_stop`, `wdt_ping`, and `wdt_set_timeout`. `diag288` wraps `__diag288` with diagnostic accounting, while `diag288_str` copies the z/VM command, converts it to EBCDIC uppercase, and passes its physical address.

## Control Flow
Init applies nowayout, allocates `cmd_buf` only when running under z/VM, and registers the watchdog. Start chooses `WDT_FUNC_INIT` with optional conceal on z/VM or `LPARWDT_RESTART` on LPAR. Ping repeats init on z/VM and uses `WDT_FUNC_CHANGE` on LPAR. Stop cancels diag 288. Set-timeout updates the core timeout then pings.

## State and Persistence
Runtime state includes command buffer, command string module parameter, conceal flag, nowayout, and the hypervisor's watchdog configuration. The watchdog action persists in firmware/hypervisor until changed or canceled.

## Dependencies and Integration Points
The driver integrates with s390 machine detection, diag 288 assembly helpers, EBCDIC conversion utilities, diagnostic statistics, and the watchdog core.

## Risks and Test Signals
Risks include z/VM command truncation/conversion, physical address validity of the command buffer, different retrigger semantics between z/VM and LPAR, and nowayout preventing cancel. Tests should cover z/VM and LPAR paths, conceal option, invalid long command handling, timeout min/max, feature-gated module loading, and diag error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/diag288_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/digicolor_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/digicolor_wdt.c

## Purpose
This platform driver controls the Conexant Digicolor watchdog implemented by Timer A. It provides standard watchdog operation plus a restart handler that forces a short timeout.

## Important APIs, types, and functions
`struct dc_wdt` stores MMIO base, clock, and spinlock. Core helpers are `dc_wdt_set`, `dc_wdt_start`, `dc_wdt_stop`, `dc_wdt_set_timeout`, `dc_wdt_get_timeleft`, and `dc_wdt_restart`. The static `dc_wdt_wdd` carries ops, identity, and timeout limits.

## Control Flow
Probe maps the timer registers, obtains a clock, computes `max_timeout` from `U32_MAX / clk_rate`, initializes timeout from module/DT, sets restart priority, and registers the watchdog. Start and set-timeout program count as seconds times clock rate and enable both counter and watchdog bits. Stop clears the control register. Restart programs a count of one and waits for reset.

## State and Persistence
Runtime state is a static watchdog object plus per-device `dc_wdt` private data. Hardware count/control registers contain volatile state. No clock enable call is made beyond obtaining the clock handle, so integration depends on platform clock state.

## Dependencies and Integration Points
The driver depends on OF compatible `cnxt,cx92755-wdt`, platform MMIO resources, the clock framework, watchdog restart priority, and spinlocked MMIO writes.

## Risks and Test Signals
Risks include static watchdog reuse, timeout multiplication overflow if clock rate changes, get_timeleft division by zero if an invalid clock is supplied, and stop not using the spinlock. Tests should cover timeout boundary calculation, start/stop/restart register values, timeleft conversion, missing resource/clock errors, and reboot stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/digicolor_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/dw_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/dw_wdt.c

## Purpose
`dw_wdt.c` is the Synopsys DesignWare watchdog driver. It supports fixed or device-tree-provided TOP values, reset and pretimeout interrupt modes, optional reset control for stopping, debugfs register exposure, suspend/resume save-restore, and restart handling.

## Important APIs, types, and functions
`struct dw_wdt` holds registers, clocks, reset control, response mode, sorted timeout table, watchdog object, saved PM registers, and optional debugfs directory. Key functions include `dw_wdt_init_timeouts`, `dw_wdt_handle_tops`, `dw_wdt_set_timeout`, `dw_wdt_set_pretimeout`, `dw_wdt_start`, `dw_wdt_stop`, `dw_wdt_restart`, `dw_wdt_get_timeleft`, `dw_wdt_irq`, and `dw_wdt_drv_probe`.

## Control Flow
Probe maps MMIO, enables timer/APB clocks, obtains optional reset, sets reset mode, optionally registers a rising-edge IRQ for pretimeout, deasserts reset, builds timeout ranges, initializes the watchdog, and either adopts already-running hardware or programs a default timeout. Start selects a TOP, kicks the counter, and enables the watchdog. Pretimeout switches response mode to two-stage IRQ mode. Stop resets the block if reset control exists; otherwise it marks hardware running so the core keeps feeding.

## State and Persistence
The watchdog cannot always be stopped once started. Runtime state includes current response mode, sorted hardware timeout table, saved PM register values, and optional `WDOG_HW_RUNNING`. Hardware registers persist through software close unless reset is available.

## Dependencies and Integration Points
It depends on platform/OF binding `snps,dw-wdt`, timer and optional APB clocks, optional reset controller, optional IRQ, debugfs, PM callbacks, and watchdog pretimeout/restart framework.

## Risks and Test Signals
Risks include malformed `snps,watchdog-tops`, timeout sorting/rounding errors, two-stage timeleft accounting, IRQ status not cleared until ping, stop semantics without reset control, and clock/reset ordering. Tests should cover fixed/custom TOPs, running-at-probe adoption, pretimeout IRQ notification, restart, suspend/resume, debugfs registration, and no-reset nowayout-like behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/dw_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ebc-c384_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ebc-c384_wdt.c

## Purpose
This ISA watchdog driver supports the WinSystems EBC-C384 SBC. It programs fixed I/O ports to select second or minute timeout resolution and pet/stop the hardware.

## Important APIs, types, and functions
The watchdog core callbacks are `ebc_c384_wdt_start`, `ebc_c384_wdt_stop`, and `ebc_c384_wdt_set_timeout`. Probe is through an `isa_driver` and allocates a `watchdog_device`. Module init gates registration on DMI board name `EBC-C384 SBC`.

## Control Flow
Init checks DMI, registers one ISA device, and probe reserves I/O range `0x564-0x568`. Set-timeout chooses seconds mode for values up to 255 and minute mode for larger values, rounding up to minute granularity. Start writes the encoded timeout to the pet port; stop writes zero. The watchdog core provides keepalive through `.start` because no explicit `.ping` is supplied.

## State and Persistence
State is held in the hardware I/O ports and the allocated watchdog object. The driver has no persistent storage and no explicit shutdown callback; `devm_watchdog_register_device` owns registration lifetime.

## Dependencies and Integration Points
It depends on DMI matching, ISA driver infrastructure, x86 I/O port access, `devm_request_region`, module timeout/nowayout parameters, and watchdog core.

## Risks and Test Signals
Risks include DMI false positives/negatives, second-to-minute rounding surprises, absence of explicit ping op, and fixed I/O port conflicts. Tests should cover DMI gating, port reservation failure, timeout boundaries at 255/256/15300 seconds, start/stop port writes, nowayout/magic close, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ebc-c384_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ep93xx_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ep93xx_wdt.c

## Purpose
`ep93xx_wdt.c` supports the Cirrus Logic EP93xx watchdog, whose hardware timeout is about 250 ms. The driver relies on the watchdog core to provide a longer software timeout via frequent hardware heartbeats.

## Important APIs, types, and functions
`struct ep93xx_wdt_priv` stores MMIO base and embedded watchdog. Operations are `ep93xx_wdt_start`, `ep93xx_wdt_stop`, and `ep93xx_wdt_ping`, which write magic values to `EP93XX_WATCHDOG`. Probe reads status, initializes `max_hw_heartbeat_ms = 200`, and registers through `devm_watchdog_register_device`.

## Control Flow
Probe maps MMIO, reads the watchdog register for bootstatus and nCS1-disable status, initializes timeout limits, applies module timeout/nowayout, and registers the device. Start writes `0xaaaa`, stop writes `0xaa55`, and ping writes `0x5555`. The core keeps pinging within the short hardware heartbeat window while honoring the user timeout.

## State and Persistence
Runtime state is private MMIO pointer and watchdog core settings. Bootstatus is derived from a hardware bit read at probe. Hardware state is otherwise volatile.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, EP93xx platform device naming, watchdog core software heartbeat support, and module parameters.

## Risks and Test Signals
Risks include missing `.set_timeout` despite advertising `WDIOF_SETTIMEOUT`, very short hardware heartbeat pressure, bootstatus interpretation, and stop behavior under nowayout. Tests should cover software timeout feeding, start/stop/ping magic writes, bootstatus bit, module timeout initialization, and registration failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ep93xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/eurotechwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/eurotechwdt.c

## Purpose
`eurotechwdt.c` is a legacy miscdevice watchdog for Eurotech CPU-1220/1410/1420 boards using an SMSC Super-I/O watchdog. It can signal timeout by interrupt or reboot output.

## Important APIs, types, and functions
Global state tracks open status, timeout, magic-close flag, I/O base, IRQ, event mode, and spinlock. Helpers include `eurwdt_unlock_chip`, `eurwdt_lock_chip`, `eurwdt_write_reg`, `eurwdt_activate_timer`, `eurwdt_disable_timer`, and `eurwdt_ping`. File operations implement write, ioctl, open, and release, and a reboot notifier disables the timer on shutdown.

## Control Flow
Module init requests the IRQ and I/O range, registers a reboot notifier and `/dev/watchdog`, then unlocks/selects the Super-I/O logical device. Open initializes the default timeout and activates the timer. Writes scan for magic `V` when nowayout is false and ping the timer. Ioctls support status, set options, keepalive, and timeout get/set. Release disables only after magic close; otherwise it pings and leaves the watchdog running.

## State and Persistence
State is global and single-open. Hardware configuration is programmed in Super-I/O registers and may continue after unexpected close or module unload. The driver does not use watchdog core state.

## Dependencies and Integration Points
It depends on fixed/parameterized I/O ports, IRQ handling, miscdevice `/dev/watchdog`, reboot notifier, and legacy watchdog ioctls.

## Risks and Test Signals
Risks include no reliable board probing, IRQ zero handling versus unconditional free, global lock coverage, magic-close semantics, and continuing hardware after unload. Tests should cover both `ev=int` and reboot modes, invalid IRQ handling, timeout bounds, unexpected close, reboot notifier, and I/O region/IRQ conflict paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/eurotechwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/exar_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/exar_wdt.c

## Purpose
This driver supports watchdog blocks in Exar/MaxLinear XR28V38x UART/Super-I/O devices. It scans Super-I/O configuration ports, creates platform devices for detected watchdogs, and exposes each through the watchdog core.

## Important APIs, types, and functions
`struct wdt_priv` contains I/O resource, config-port identity, runtime unit/timeout, spinlock, and watchdog device. Super-I/O helpers include `exar_sio_enter`, `exar_sio_read16`, `exar_sio_select_wdt`, and `exar_detect`. Watchdog operations are `exar_wdt_start`, `exar_wdt_stop`, `exar_wdt_keepalive`, and `exar_wdt_set_timeout`.

## Control Flow
Module init scans config ports `0x2e`/`0x4e` with multiple enter keys, validates vendor/device IDs, reads active runtime base, registers platform devices, then probes them. Probe initializes watchdog limits, configures the WDT control register, sets timeout, stops hardware, and registers. Start disarms, writes units, and arms by writing the timeout twice. Ping reads `WDT_VAL`; stop writes a safe disarm sequence.

## State and Persistence
State is per detected watchdog but platform-device nodes are tracked in a global list. Hardware state is in Super-I/O and runtime I/O registers. No persistent storage exists; detected platform devices are unregistered at module exit.

## Dependencies and Integration Points
The driver depends on raw I/O port access, muxed Super-I/O config regions, platform-device registration, list management, module timeout/nowayout, and watchdog core.

## Risks and Test Signals
Risks include false Super-I/O detection, I/O region conflicts, minute/second rounding above 255 seconds, multiple detected devices, and arm/disarm write sequencing. Tests should cover all enter keys, unsupported IDs, active flag false, multiple watchdog registration, timeout boundary at 255 seconds, and start/stop/ping I/O traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/exar_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/f71808e_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/f71808e_wdt.c

## Purpose
`f71808e_wdt.c` supports watchdogs in a family of Fintek Super-I/O chips. It performs chip detection, configures reset-output pin multiplexing, supports second/minute timeouts, pulse/level reset outputs, bootstatus detection, and optional start-on-load.

## Important APIs, types, and functions
`struct fintek_wdt` stores the watchdog, Super-I/O address, chip type, identity, encoded timer value, unit mode, and pulse configuration. Detection uses `fintek_wdt_find`; platform probe uses `fintek_wdt_probe`. Watchdog ops are `fintek_wdt_start`, `fintek_wdt_stop`, `fintek_wdt_keepalive`, and `fintek_wdt_set_timeout`; pulse setup is `fintek_wdt_set_pulse_width`.

## Control Flow
Module init validates parameters, searches Super-I/O ports, registers a platform driver/device with chip type, and probe configures the watchdog object. Probe clears stale timeout status, detects running hardware, sets timeout and pulse width, optionally starts the watchdog, and registers. Start first writes the time value, configures chip-specific pin mux, enables the logical device and watchdog output, and sets pulse/level mode. Keepalive rewrites unit and time registers.

## State and Persistence
Runtime state includes encoded timeout/pulse settings and watchdog status bits. Hardware configuration persists in Super-I/O registers until changed. Boot timeout status is cleared during probe after being captured.

## Dependencies and Integration Points
The driver depends on Fintek Super-I/O IDs, raw I/O ports, muxed region locking, platform-device glue, watchdog core, and module parameters `force_id`, `pulse_width`, `start_withtimeout`, and `f71862fg_pin`.

## Risks and Test Signals
Risks include chip-specific pin mux mistakes, force-id misuse, race with other Super-I/O drivers, bootstatus clearing, start-on-load nowayout behavior, and pulse-width rounding. Tests should cover each supported chip ID, f71862 pin options, second/minute timeouts, pulse widths, running-at-probe, invalid parameters, and I/O conflict paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/f71808e_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ftwdt010_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ftwdt010_wdt.c

## Purpose
This driver supports the Faraday FTWDT010 watchdog and compatible Cortina Gemini watchdog. It programs a fixed 5 MHz watchdog clock, optional pretimeout interrupt, and restart behavior.

## Important APIs, types, and functions
`struct ftwdt010_wdt` embeds the watchdog and stores device, MMIO base, and IRQ presence. `ftwdt010_enable` centralizes register programming. Watchdog ops are `ftwdt010_wdt_start`, `ftwdt010_wdt_stop`, `ftwdt010_wdt_ping`, `ftwdt010_wdt_set_timeout`, and `ftwdt010_wdt_restart`. `ftwdt010_wdt_interrupt` notifies watchdog pretimeout.

## Control Flow
Probe maps MMIO, initializes timeout limits and default 13 seconds, disables bootloader-enabled hardware, optionally requests an IRQ and marks pretimeout capability internally, and registers the watchdog. Start writes load value, restart magic, clock/reset mode, optional interrupt enable, and enable bit. Ping writes restart magic. Restart enables the watchdog with timeout zero. Suspend clears enable; resume re-enables only if watchdog core state is active.

## State and Persistence
Runtime state includes `has_irq`, watchdog timeout, and MMIO registers. Bootloader-enabled hardware is deliberately disabled at probe. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, optional IRQ, OF compatibles `faraday,ftwdt010` and `cortina,gemini-watchdog`, PM ops, and watchdog restart/pretimeout framework.

## Risks and Test Signals
Risks include hard-coded 5 MHz clock assumptions, disabling a bootloader watchdog without handoff, pretimeout notification without advertising `WDIOF_PRETIMEOUT`, and suspend disabling hardware. Tests should cover IRQ/no-IRQ modes, boot-enabled disable, timeout max calculation, restart path, suspend/resume active state, and register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ftwdt010_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/gef_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/gef_wdt.c

## Purpose
`gef_wdt.c` is a legacy miscdevice watchdog for GE Intelligent Platforms FPGA watchdog hardware. It provides `/dev/watchdog` access to one watchdog even though the hardware can support more.

## Important APIs, types, and functions
Global state includes MMIO base, timeout/count, bus clock, status, open flag, magic-close flag, and spinlock. Hardware helpers are `gef_wdt_toggle_wdc`, `gef_wdt_service`, `gef_wdt_handler_enable`, `gef_wdt_handler_disable`, and `gef_wdt_set_timeout`. File operations implement write, ioctl, open, and release.

## Control Flow
Probe maps the FPGA watchdog registers from device tree, gets system bus frequency through `fsl_get_sys_freq`, computes the initial counter, disables any running watchdog, and registers `/dev/watchdog`. Open enforces single-open, optionally pins the module for nowayout, and enables hardware. Writes scan for magic close and service the watchdog. Ioctls support status, set options, keepalive, and timeout get/set. Release disables only after magic close.

## State and Persistence
State is global and singleton. The hardware register combines enabled state, service/enable toggle fields, and low 24 bits of count. Status bits are software-only and partially cleared on read.

## Dependencies and Integration Points
The driver depends on OF compatible `gef,fpga-wdt`, big-endian MMIO access, Freescale system frequency helper, miscdevice watchdog ABI, and module nowayout.

## Risks and Test Signals
Risks include global singleton limitations, count scaling from bus clock, upper-24-bit truncation, lack of watchdog core integration, and no interrupt-threshold support. Tests should cover timeout clamping, big-endian register toggle sequences, unexpected close, ioctl compatibility, OF map failure, and bus frequency fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/gef_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/geodewdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/geodewdt.c

## Purpose
This legacy watchdog driver supports AMD Geode GX/LX systems using the CS5535/CS5536 MFGPT timer reset event. It exposes a miscdevice `/dev/watchdog` interface.

## Important APIs, types, and functions
Global state includes platform device pointer, open/orphan flags, `cs5535_mfgpt_timer`, timeout, and safe-close flag. Hardware helpers are `geodewdt_ping`, `geodewdt_disable`, and `geodewdt_set_heartbeat`. File operations implement write, ioctl, open, and release. Platform callbacks include probe, remove, and shutdown.

## Control Flow
Module init creates a platform device and probes the driver. Probe allocates an MFGPT timer, configures scale and reset-on-CMP2 event, sets the initial compare value, and registers `/dev/watchdog`. Open enforces single-open, handles orphaned nowayout state, and pings. Writes scan for magic close and ping. Ioctls support options, keepalive, and timeout get/set. Unexpected close marks the device orphaned and leaves the timer running.

## State and Persistence
Runtime state is entirely global. MFGPT hardware retains compare/setup state until disabled or reset. Orphan flag tracks an unexpected close while keeping module references consistent.

## Dependencies and Integration Points
The driver depends on CS5535 MFGPT APIs, platform-device self-registration, miscdevice watchdog ABI, reboot/shutdown callback, and module timeout/nowayout parameters.

## Risks and Test Signals
Risks include timer allocation failure, module reference/orphan handling, timeout range limits, reset-event configuration, and lack of watchdog core supervision. Tests should cover safe and unsafe close, reopen after orphan, timeout boundaries, shutdown disable, ioctl options, and MFGPT API failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/geodewdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/gpio_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/gpio_wdt.c

## Purpose
`gpio_wdt.c` implements a generic external watchdog controlled by a GPIO line. It supports toggle-style and pulse/level-style hardware algorithms and can model always-running hardware.

## Important APIs, types, and functions
`struct gpio_wdt_priv` stores the GPIO descriptor, current toggle state, always-running flag, algorithm selector, and embedded watchdog. Operations are `gpio_wdt_start`, `gpio_wdt_stop`, and `gpio_wdt_ping`; `gpio_wdt_disable` holds or tristates the line depending on algorithm.

## Control Flow
Probe reads required `hw_algo` and `hw_margin_ms` properties, obtains the GPIO with suitable direction, reads optional `always-running`, initializes watchdog limits, and registers. Toggle mode starts as output low and flips the state on each ping. Level mode pulses high for one microsecond then low. Stop disables the GPIO only when hardware is not always running; otherwise it sets `WDOG_HW_RUNNING` so the core continues feeding.

## State and Persistence
Runtime state includes GPIO direction/value, last toggle state, and watchdog core status. External hardware may remain running independently of driver lifetime, especially with `always-running`.

## Dependencies and Integration Points
The driver depends on firmware properties, GPIO descriptor APIs, optional arch initcall registration, OF compatible `linux,wdt-gpio`, and watchdog core software heartbeat via `max_hw_heartbeat_ms`.

## Risks and Test Signals
Risks include wrong algorithm property, invalid heartbeat margin, GPIO polarity assumptions, stop semantics for always-running devices, and one-microsecond pulse timing. Tests should cover toggle and level modes, missing/invalid properties, always-running start/stop, GPIO probe deferral, max heartbeat feeding, and reboot stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/gpio_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/gxp-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/gxp-wdt.c

## Purpose
This driver supports the HPE GXP watchdog timer. It is created as a child of the timer driver and receives a shared register base through platform data because the timer/watchdog register area is interleaved.

## Important APIs, types, and functions
`struct gxp_wdt` stores the base pointer and watchdog object. Core functions are `gxp_wdt_start`, `gxp_wdt_stop`, `gxp_wdt_ping`, `gxp_wdt_set_timeout`, `gxp_wdt_get_timeleft`, and `gxp_restart`. `gxp_wdt_enable_reload` sets enable and reload bits in the control register.

## Control Flow
Probe allocates private data, takes `dev->platform_data` as MMIO base, initializes a 30-second watchdog with 655.35-second hardware heartbeat, detects already-enabled hardware, sets restart priority, and registers. Start writes count as seconds times 100 ticks and enables reload. Set-timeout updates core timeout and writes a count clamped to hardware heartbeat. Ping just enables reload. Restart writes a count of one, reloads, and waits briefly.

## State and Persistence
State is in the shared timer/watchdog registers and the watchdog core object. If enable is set at probe, `WDOG_HW_RUNNING` is recorded for handoff. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on platform data supplied by the GXP timer driver, raw MMIO byte/word access, watchdog core, restart priority, and reboot stop handling.

## Risks and Test Signals
Risks include trusting platform_data without validation, shared register ownership with the timer driver, tick/second truncation, and nowayout always using `WATCHDOG_NOWAYOUT`. Tests should cover parent-created device, already-running detection, timeout clamping, get_timeleft conversion, restart assertion, and missing/invalid platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/gxp-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/hpwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/hpwdt.c

## Purpose
`hpwdt.c` is the HPE iLO2+ hardware watchdog driver for supported ProLiant/iLO PCI devices. It supports watchdog core operation, optional NMI pretimeout decoding, crash-kernel timeout policy, suspend/resume, and hardware-running handoff.

## Important APIs, types, and functions
Global MMIO pointers identify NMI status, timer reload, and timer control registers. Watchdog ops are `hpwdt_start`, `hpwdt_stop_core`, `hpwdt_ping`, `hpwdt_settimeout`, `hpwdt_gettimeleft`, and optionally `hpwdt_set_pretimeout`. PCI lifecycle is handled by `hpwdt_init_one` and `hpwdt_exit`. NMI support uses `hpwdt_pretimeout`, `hpwdt_my_nmi`, and register/unregister NMI handlers.

## Control Flow
Probe validates subsystem vendor, rejects blacklisted auxiliary devices, enables PCI, maps BAR1, detects running hardware, registers NMI decoding when configured, applies nowayout/timeout/pretimeout/kdump settings, and registers the watchdog. Start writes reload ticks and control bits including pretimeout enable. Ping rewrites reload ticks. NMI pretimeout may stop or extend the timer, pack the NMI reason into a panic message, and call `nmi_panic`.

## State and Persistence
The driver uses global singleton state for one active PCI device. Hardware timer state may be active before probe and is adopted through `WDOG_HW_RUNNING`. `kdumptimeout` changes behavior in crash kernels.

## Dependencies and Integration Points
It depends on PCI IDs, BAR mapping, watchdog core, optional x86 NMI handlers, crash dump detection, suspend/resume PM ops, and HPE iLO hardware semantics.

## Risks and Test Signals
Risks include global state with multiple devices, NMI ownership conflicts, pretimeout/timeout interactions, kdump behavior, blacklist coverage, and MMIO lifetime. Tests should cover supported/blacklisted PCI IDs, running-at-probe, NMI registration failures, pretimeout toggling, kdump kernel path, suspend/resume, and max tick conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/hpwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/i6300esb.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/i6300esb.c

## Purpose
This PCI watchdog driver supports Intel 6300ESB chipset watchdog timers. It uses memory-mapped watchdog registers and PCI configuration bits to enable, lock, reload, stop, and configure dual-stage timers.

## Important APIs, types, and functions
`struct esb_dev` embeds a watchdog device with BAR mapping and PCI device pointer. Low-level helpers include `esb_unlock_registers`, `esb_timer_start`, `esb_timer_stop`, `esb_timer_keepalive`, `esb_timer_set_heartbeat`, `esb_getdevice`, and `esb_initdevice`. PCI probe/remove manage resource lifetime.

## Control Flow
Probe allocates `esb_dev`, enables PCI, requests and maps BAR0, initializes watchdog core limits, applies module heartbeat/nowayout, configures chipset registers, checks prior timeout status, resets the timeout flag, and registers. The hardware requires writing unlock bytes before each protected register write. Start reloads and sets enable plus optional lock. Stop reloads then clears the lock register and verifies disable. Set-timeout writes timer1 and timer2 values then reloads.

## State and Persistence
State is per PCI device. Hardware lock/enable bits can survive and may prevent disabling when nowayout or firmware lock is active. Bootstatus is captured from `ESB_WDT_TIMEOUT`.

## Dependencies and Integration Points
The driver depends on PCI ID `PCI_DEVICE_ID_INTEL_ESB_9`, BAR0 MMIO, PCI config access, watchdog core, and module parameters.

## Risks and Test Signals
Risks include protected register unlock ordering, stop failure when locked, heartbeat shift/range math, multi-device handling, and bootstatus clearing. Tests should cover PCI resource failures, timeout boundaries, nowayout lock bit, prior timeout flag, start/stop/ping MMIO sequences, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/i6300esb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/iTCO_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/iTCO_wdt.c

## Purpose
`iTCO_wdt.c` is the Intel TCO watchdog driver for many ICH/PCH generations. It handles version-specific timeout encodings, NO_REBOOT control, optional SMI watchdog clearing disablement, running-at-probe handoff, and suspend-to-idle handling.

## Important APIs, types, and functions
`struct iTCO_wdt_private` stores watchdog device, TCO version, I/O resources, optional GCS/PMC mapping, PCI parent, suspend state, and a function pointer for NO_REBOOT updates. Core operations are `iTCO_wdt_start`, `iTCO_wdt_stop`, `iTCO_wdt_ping`, `iTCO_wdt_set_timeout`, and `iTCO_wdt_get_timeleft`. NO_REBOOT strategies include PCI config, memory-mapped GCS/PMC, TCO1_CNT, and Intel PMC GCR updates.

## Control Flow
Probe consumes `itco_wdt_platform_data`, validates I/O resources, selects NO_REBOOT update method, maps GCS/PMC when needed, clears NO_REBOOT to prove reset is possible, optionally disables SMI watchdog clearing, reserves TCO I/O, clears status bits, initializes the watchdog, detects whether hardware is already running, sets timeout, and registers. Start clears NO_REBOOT, reloads, and clears the halt bit. Stop sets halt and then sets NO_REBOOT.

## State and Persistence
Hardware TCO state may be running before probe. NO_REBOOT policy is persisted in chipset registers until changed. The driver caches whether it stopped the watchdog during suspend so it can restart on resume.

## Dependencies and Integration Points
It depends on platform data from Intel LPC/PMC infrastructure, I/O port resources, optional MMIO/PMC register APIs, ACPI sleep-state detection, watchdog core, and platform PM noirq callbacks.

## Risks and Test Signals
Risks include generation-specific NO_REBOOT bit errors, timeout tick conversion, SMI clearing resource absence, status clearing differences, and suspend-to-idle stop/restart. Tests should cover versions 1-6, PMC-backed NO_REBOOT, invalid heartbeat fallback, running-at-probe, timeleft math, SMI resource missing, and S0ix suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/iTCO_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ib700wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ib700wdt.c

## Purpose
`ib700wdt.c` is a legacy miscdevice watchdog for IB700 single-board computers. It controls the watchdog with fixed I/O ports for start/ping and stop and exposes the classic `/dev/watchdog` ABI.

## Important APIs, types, and functions
Global state includes platform device pointer, open bit, spinlock, timeout, nowayout, and magic-close marker. Hardware helpers are `ibwdt_ping`, `ibwdt_disable`, and `ibwdt_set_heartbeat`. File operations are `ibwdt_write`, `ibwdt_ioctl`, `ibwdt_open`, and `ibwdt_close`; platform lifecycle uses self-registered platform device and probe/remove/shutdown callbacks.

## Control Flow
Module init creates a platform device and probes the driver. Probe reserves `WDT_STOP` and `WDT_START` I/O ports, validates timeout, and registers `/dev/watchdog`. Open enforces single-open, pins module when nowayout, and activates the watchdog. Ping encodes timeout into the board's 0-F level value and writes `WDT_START`. Stop writes `WDT_STOP`. Release disables only after magic close; otherwise it pings and leaves hardware running.

## State and Persistence
State is global and not watchdog-core based. Hardware state persists in the board watchdog until stopped or reset. Shutdown disables the watchdog for soft shutdown.

## Dependencies and Integration Points
The driver depends on raw I/O ports `0x441` and `0x443`, platform-device self-registration, miscdevice watchdog ABI, compat ioctl handling, and module parameters.

## Risks and Test Signals
Risks include lack of hardware discovery, timeout tolerance/encoding, single-open global state, magic-close handling, and I/O port conflicts. Tests should cover timeout range 0-30, start/stop port writes, unexpected close, nowayout module ref, shutdown disable, and request_region failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ib700wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ibmasr.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ibmasr.c

## Purpose
`ibmasr.c` implements the IBM Automatic Server Restart watchdog for several IBM xSeries machine families. It is a legacy `/dev/watchdog` miscdevice with fixed hardware timeout and model-specific I/O register layouts.

## Important APIs, types, and functions
Model selection uses `ibmasr_id_table` and DMI device descriptions. Global hardware parameters include ASR type, base/length, read/write addresses, toggle mask, and disable mask. Important helpers are `asr_get_base_address`, `asr_enable`, `asr_disable`, `asr_toggle`, and `__asr_toggle`. File operations implement write, ioctl, open, and release.

## Control Flow
Module init scans DMI for supported ASR descriptions, computes model-specific I/O addresses, reserves the region, and registers `/dev/watchdog`. Open toggles and enables the timer. Writes scan for magic close and toggle the hardware line. Ioctls support keepalive, enable/disable, support info, and fixed `GETTIMEOUT` of 256 seconds. Release disables only after magic close; otherwise it toggles and leaves the watchdog active.

## State and Persistence
All driver state is global. Hardware has a fixed timeout and persists until disabled. Module exit disables only when nowayout is false, then deregisters and releases I/O resources.

## Dependencies and Integration Points
The driver depends on DMI, raw I/O port access, legacy PCI config access for Jasper base discovery, miscdevice watchdog ABI, and module nowayout.

## Risks and Test Signals
Risks include DMI string fragility, unsafe Jasper PCI config probing, model-specific mask/address mistakes, fixed timeout expectations, and nowayout unload behavior. Tests should cover each ASR type, I/O region conflicts, magic close, unexpected close, enable/disable ioctl, fixed timeout return, and DMI no-match path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ibmasr.c -->
