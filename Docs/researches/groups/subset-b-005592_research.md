# Research: subset-b-005592

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ie6xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/ie6xx_wdt.c`

Purpose: Intel Atom E6xx platform watchdog driver using an I/O-port resource supplied by a platform device. It exposes the watchdog through the watchdog core, programs preload registers derived from the 33 MHz PCI clock, and optionally exposes a debugfs register dump.

Important APIs, types, and functions: `ie6xx_wdt_dev` is a singleton `struct watchdog_device`; `ie6xx_wdt_ops` implements start, stop, ping, and set_timeout. Module parameters `timeout`, `nowayout`, and `resetmode` shape initial policy and hardware reset behavior. The register unlock sequence is centralized in `ie6xx_wdt_unlock_registers()` and protected by `ie6xx_wdt_data.unlock_sequence`; `ie6xx_wdt_set_timeout()` writes `WDTCR`, clears `PV1`, writes `PV2`, and reloads/clears timeout via `RR1`.

Control flow: `late_initcall()` registers the platform driver after validating the timeout range. Probe reserves the I/O region, records `sch_wdtba`, warns if `WDTLR` is locked, initializes debugfs, and registers the watchdog. Start programs the timeout then writes `WDT_ENABLE`; stop refuses a locked watchdog and clears `WDTLR`; ping performs the unlock sequence and writes `WDT_RELOAD`. Remove stops, unregisters, removes debugfs, and releases the I/O range.

State and persistence: live state is held in hardware registers plus singleton driver globals. A locked `WDTLR` persists until reboot and can prevent stop. `WDOG_HW_RUNNING` is not inferred on probe, so pre-enabled hardware is only surfaced through lock warnings/debugfs, not as core-running state.

Dependencies and integration points: depends on platform I/O resources, watchdog core, raw in/out port access, debugfs when enabled, and platform alias `ie6xx_wdt`. It integrates with user space through `/dev/watchdog*` via watchdog core and with debugfs as `/sys/kernel/debug/ie6xx_wdt`.

Risks and test signals: risks include register unlock sequence interruption, incorrect `resetmode`, preload rounding errors, and stop failures when locked. Test by validating module parameter bounds, start/ping/stop behavior, debugfs register visibility, locked-register handling, and reboot behavior for warm/cold reset settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ie6xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imgpdc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imgpdc_wdt.c`

Purpose: Imagination Technologies PowerDown Controller watchdog driver for `img,pdc-wdt` devices. It maps PDC registers, enables `sys` and `wdt` clocks, programs coarse power-of-two timeouts, reports reset cause, and supplies a restart hook.

Important APIs, types, and functions: `struct pdc_wdt_dev` embeds `watchdog_device` plus clock and MMIO pointers. `pdc_wdt_keepalive()` writes the two tickle magic values, `pdc_wdt_stop()` clears `PDC_WDT_CONFIG_ENABLE` and tickles to commit the stop, `__pdc_wdt_set_timeout()` computes `order_base_2(timeout * clk_rate) - 1`, and `pdc_wdt_restart()` asserts `PDC_WDT_SOFT_RESET`.

Control flow: probe allocates state, maps the MMIO resource, enables clocks, derives min/max timeout from the watchdog clock, initializes the watchdog core device, stops any active watchdog, reads tickle status for boot cause, sets nowayout and restart priority, installs stop-on-reboot/unregister, then registers with `devm_watchdog_register_device()`.

State and persistence: timeout precision is hardware-limited to powers of two clock cycles, so the actual timeout is at least the requested value. Bootstatus is latched in `PDC_WDT_TICKLE1` status bits and translated to `WDIOF_CARDRESET` for timeout or bad tickle resets. Clock rate is a runtime dependency for all timeout math.

Dependencies and integration points: requires devicetree compatible `img,pdc-wdt`, `sys` and `wdt` clocks, MMIO, watchdog core, and restart priority 128. User-visible timeout values may differ from real hardware intervals due to rounding.

Risks and test signals: risks include invalid zero/high clock rates, coarse timeout surprises, and stop not completing unless tickled. Test with devicetree clocks, timeout values near powers of two, bootstatus after timeout/reset/user reset, restart path, and stop-on-reboot/unregister behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imgpdc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx2_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imx2_wdt.c`

Purpose: watchdog driver for i.MX2 and later NXP/Freescale watchdog blocks. It supports many OF compatibles, internal or external reset routing, optional pretimeout IRQs, suspend/resume handling, and restart.

Important APIs, types, and functions: `struct imx2_wdt_device` holds the clock, regmap, watchdog core device, match data, and policy flags. `imx2_wdt_setup()` writes WCR once-only low-power/reset bits and enables the watchdog; `imx2_wdt_ping()` writes the `0x5555`/`0xAAAA` service sequence; `imx2_wdt_set_pretimeout()` programs WICR; `imx2_wdt_restart()` writes WCR three times for the i.MX6Q SRS erratum.

Control flow: probe maps registers through regmap, gets/enables the clock, requests an IRQ when present to enable pretimeout reporting, reads reset status, parses `fsl,ext-reset-output` and `fsl,suspend-in-wait`, initializes watchdog core values, marks already-running hardware, clears WMCR, and registers. Start either updates a running watchdog or performs full setup; shutdown stretches timeout to the 128 second hardware maximum and pings; PM paths stretch/restart the watchdog around sleep depending on SoC behavior.

State and persistence: watchdog enable can persist from boot firmware and is marked with `WDOG_HW_RUNNING`. The hardware cannot be stopped through watchdog core because no stop op is provided. User timeout may exceed hardware heartbeat; the driver clamps actual hardware timeout to `IMX2_WDT_MAX_TIME` while retaining the requested logical timeout for core supervision.

Dependencies and integration points: depends on OF match data for WDW support, a clock, regmap MMIO, optional interrupt, watchdog core ping-on-suspend helpers, and restart priority 128. Reset routing is controlled by devicetree properties.

Risks and test signals: risks include incorrect low-power behavior, mismatched external reset wiring, pretimeout count conversion, and firmware-left-running watchdogs. Test all compatible data paths, IRQ pretimeout notification, suspend/resume for i.MX7D versus other SoCs, shutdown timeout extension, and restart reset assertion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx2_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx7ulp_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imx7ulp_wdt.c`

Purpose: watchdog driver for i.MX7ULP, i.MX8ULP, and i.MX93 style watchdogs with unlock/update handshakes, LPO clock selection, variant-specific prescaling, and noirq PM.

Important APIs, types, and functions: `struct imx7ulp_wdt_device` stores MMIO, clock, reset mode, watchdog core device, and `struct imx_wdt_hw_feature`. `imx7ulp_wdt_wait_ulk()` and `imx7ulp_wdt_wait_rcs()` poll unlock and reconfiguration completion. `_imx7ulp_wdt_enable()` and `_imx7ulp_wdt_set_timeout()` disable local IRQs around the unlock-write window. `imx7ulp_wdt_init()` configures CS/TOVAL with retry verification.

Control flow: probe maps registers, enables the clock, reads `fsl,ext-reset-output`, initializes core timeout bounds, associates match data, configures the hardware while preserving already-enabled state, and registers. Start/stop call the enable wrapper with retry; set_timeout writes `TOVAL`; restart enables the watchdog, sets a one-second timeout, then spins until reset. Suspend_noirq stops an active watchdog and disables the clock; resume_noirq reenables the clock and restores/feeds active watchdogs.

State and persistence: active hardware at probe is marked `WDOG_HW_RUNNING` and kept enabled. The CS update bits and TOVAL are verified after each retry, reducing exposure to missed unlock windows. Variant data changes clock-rate conversion, prescaler usage, and post-RCS delay.

Dependencies and integration points: depends on OF compatibles `fsl,imx7ulp-wdt`, `fsl,imx8ulp-wdt`, `fsl,imx93-wdt`, a clock, MMIO, watchdog core, and noirq system sleep callbacks.

Risks and test signals: risks include timeout conversion mismatches for i.MX93 prescaler, failing unlock/RCS polling, local IRQ latency requirements, and restart spinning if reset does not occur. Test repeated start/stop/set_timeout under load, suspend/resume, external reset configuration, already-running boot state, and retry failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx7ulp_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx_sc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imx_sc_wdt.c`

Purpose: NXP i.MX system-controller watchdog driver that delegates watchdog operations to SC firmware through ARM SMCCC calls and uses SCU IRQ notifications for pretimeout.

Important APIs, types, and functions: `struct imx_sc_wdt_device` embeds `watchdog_device` and a notifier block. `imx_sc_wdt_start()`, stop, ping, timeout, and pretimeout functions send `IMX_SIP_TIMER` SMC subcommands. `imx_sc_wdt_is_running()` probes by attempting start and undoing it when Linux successfully started it. `imx_sc_wdt_notify()` maps SCU watchdog IRQ events to `watchdog_notify_pretimeout()`.

Control flow: probe initializes the watchdog, sets default timeout in firmware, detects running firmware state, enables stop-on-reboot/unregister, attempts to enable SCU watchdog IRQ group and register a notifier, conditionally advertises pretimeout, then registers the watchdog. Operations are thin firmware RPCs and convert nonzero firmware return values to `-EACCES`.

State and persistence: the authoritative watchdog state is in SC firmware, not Linux registers. Firmware may already have the watchdog running, represented with `WDOG_HW_RUNNING`. Pretimeout programming uses `timeout - pretimeout` because firmware interprets the value relative to current timestamp.

Dependencies and integration points: depends on ARM SMCCC, NXP SCU firmware/IRQ APIs, OF compatible `fsl,imx-sc-wdt`, watchdog core, and firmware support for the timer SIP service.

Risks and test signals: risks include firmware semantic changes, probing by start/stop causing side effects, inability to stop due to permission, and pretimeout conversion errors. Test SMC failure handling, already-running detection, notifier registration cleanup, pretimeout delivery, and stop-on-reboot/unregister with firmware traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx_sc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/indydog.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/indydog.c`

Purpose: legacy miscdevice watchdog for SGI IP22 Indy hardware using SGI memory-controller watchdog registers exposed through `sgimc`.

Important APIs, types, and functions: `indydog_start()` sets `SGIMC_CCTRL0_WDOG`, `indydog_stop()` clears it, and `indydog_ping()` writes `sgimc->watchdogt = 0`. The file operations implement open, write, ioctl, and release directly rather than using watchdog core.

Control flow: module init registers a reboot notifier and a misc watchdog device on `WATCHDOG_MINOR`. Open enforces single-open via `indydog_alive`, optionally pins the module for nowayout, starts and pings the hardware. Writes ping if non-empty. Ioctl supports support/status/options/keepalive/timeout. Release stops the hardware unless `nowayout` is set. Reboot notifier stops on `SYS_DOWN` or `SYS_HALT`.

State and persistence: state is a single open bit plus hardware enable in `cpuctrl0`; there is no magic-close character tracking. Timeout is fixed at 30 seconds and bootstatus is always reported as zero.

Dependencies and integration points: SGI IP22 architecture headers, miscdevice `/dev/watchdog`, reboot notifier, raw memory-controller access, and legacy watchdog ioctl ABI.

Risks and test signals: risks include lack of watchdog core supervision, no bootstatus, and stop-on-close behavior without magic close. Test single-open enforcement, WDIOC_SETOPTIONS, reboot notifier stop, nowayout module pinning, and repeated write keepalives on IP22 hardware or emulation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/indydog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel-mid_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/intel-mid_wdt.c`

Purpose: Intel MID SCU watchdog driver for Merrifield-like platforms where watchdog control is performed through Intel SCU IPC and a warning IRQ panics the kernel.

Important APIs, types, and functions: `struct mid_wdt` stores watchdog core state, device pointer, and SCU IPC device. `wdt_command()` wraps `intel_scu_ipc_dev_command_with_size()`. `wdt_start()` sends `SCU_WATCHDOG_START` with pretimeout and timeout dwords, `wdt_ping()` sends keepalive, and `wdt_stop()` sends stop. `mid_wdt_irq()` calls `panic("Kernel Watchdog")`.

Control flow: probe requires platform data, runs optional platform probe hook, initializes watchdog core bounds, forces nowayout, obtains the SCU IPC device, requests the warning IRQ with `IRQF_NO_SUSPEND`, starts the watchdog immediately to override firmware/U-Boot defaults, marks `WDOG_HW_RUNNING`, and registers the watchdog.

State and persistence: firmware may leave the watchdog running with unknown thresholds, so probe deliberately restarts it with deterministic values. There is no set_timeout op even though `WDIOF_SETTIMEOUT` is advertised; timeout range is fixed in the device structure. Nowayout is always forced.

Dependencies and integration points: depends on Intel MID platform data, SCU IPC platform APIs, watchdog core, panic path, and IRQ routing for warning/pretimeout.

Risks and test signals: risks include IPC command size quirks, panic-on-warning behavior, missing platform data, and inability to read hardware state. Test SCU IPC start/stop/ping returns, IRQ panic delivery, probe-defer for SCU IPC, deterministic restart after firmware, and watchdog daemon interaction under nowayout.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel-mid_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel_oc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/intel_oc_wdt.c`

Purpose: Intel OC watchdog driver for ACPI-described I/O-port watchdog registers, including support for one-time register locking and fixed heartbeat reporting.

Important APIs, types, and functions: `struct intel_oc_wdt` contains the watchdog core device, I/O resource, mutable `watchdog_info`, and `locked` flag. Ops perform direct `inl/outl` updates: start sets `EN`, stop clears it, ping sets `RLD`, set_timeout writes `TOV = timeout - 1`, and setup interprets status/lock bits.

Control flow: probe obtains and reserves the I/O resource, initializes timeout bounds, applies module heartbeat, calls `intel_oc_wdt_setup()`, sets drvdata and nowayout, installs stop-on-reboot/unregister, and registers. Setup maps status bits to `WDIOF_CARDRESET`, detects enabled/locked state, forces nowayout and removes `WDIOF_SETTIMEOUT` when a running watchdog is locked, or rejects a disabled locked watchdog.

State and persistence: `INTEL_OC_WDT_CTL_LCK` persists until reboot and freezes timeout/enable/lock fields. If firmware left the watchdog running, `WDOG_HW_RUNNING` is set. Reset-cause status bits are read from the same control register.

Dependencies and integration points: depends on ACPI IDs `INT3F0D` and `INTC1099`, I/O port reservation, watchdog core, and module parameters `heartbeat` and `nowayout`.

Risks and test signals: risks include incorrectly handling locked disabled hardware, mutating global nowayout based on one device, and no explicit status-bit clear. Test locked-running, locked-disabled, unlocked start/stop, heartbeat override, bootstatus after watchdog reset, and ACPI resource conflicts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel_oc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it8712f_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/it8712f_wdt.c`

Purpose: legacy IT8712F Smart Guardian watchdog driver using Super I/O configuration ports and a game-port "DogFood" address for pinging.

Important APIs, types, and functions: Super I/O helpers enter/exit configuration mode with `request_muxed_region(0x2e, 2)`. `it8712f_wdt_update_margin()` chooses seconds or minutes precision and writes WDT config/timeout bytes. `it8712f_wdt_enable()` selects GPIO LDN, programs control/config, exits, then pings via game-port read. `it8712f_wdt_disable()` clears config/control/timeout registers. Legacy file operations implement magic close and ioctls.

Control flow: init finds the chip ID, activates/reads the game-port base, adjusts max units for later revisions, reserves the ping I/O byte, disables any existing watchdog, registers a reboot notifier, and registers `/dev/watchdog`. Open enforces single-open and enables the watchdog. Writes ping and track `V` magic close. Release disables only with magic close and `!nowayout`. Ioctl supports get status, keepalive, timeout set/get.

State and persistence: driver state is in globals `wdt_open`, `expect_close`, `revision`, `address`, and module parameters. Hardware reset cause is read from `WDT_CONTROL` status bit for `GETSTATUS`, but `GETBOOTSTATUS` always returns zero. Later revisions support 16-bit timeout units.

Dependencies and integration points: depends on x86-style I/O ports, Super I/O IT8712F device ID, game-port LDN activation, misc watchdog ABI, reboot notifier, and legacy user-space magic-close semantics.

Risks and test signals: risks include sharing Super I/O ports, losing the magic-close state, wrong seconds/minutes conversion, and reliance on game-port side-effect pinging. Test chip detection, revision-specific 8/16-bit timeouts, busy I/O regions, WDIOC_SETTIMEOUT bounds, unexpected close, reboot notifier, and status-bit reset cause.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it8712f_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it87_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/it87_wdt.c`

Purpose: watchdog-core driver for many ITE IT87xx EC/LPC Super I/O chips, replacing older miscdevice patterns with watchdog core registration.

Important APIs, types, and functions: chip detection uses Super I/O `CHIPID`/`CHIPREV` and a large supported-ID switch. `_wdt_update_timeout()` writes GPIO watchdog config and timeout bytes, choosing seconds or minute units and optional test mode. `_wdt_running()` checks nonzero timeout registers. `wdt_start()` and `wdt_stop()` rewrite timeout to requested value or zero; `wdt_set_timeout()` rounds minute-mode timeouts.

Control flow: init reads chip ID/revision, applies DMI quirks, determines 8- or 16-bit timeout capacity, configures GPIO watchdog control, applies PWRGD routing quirks, detects firmware-running state, clamps/rounds the module timeout, sets max timeout, installs stop-on-reboot, and registers the watchdog. Exit unregisters it.

State and persistence: state is mostly hardware register state plus global `timeout`, `testmode`, `nowayout`, `max_units`, and `chip_type`. Firmware-left-running watchdogs are marked `WDOG_HW_RUNNING`. There is no explicit ping operation; watchdog core keepalive relies on start/set_timeout behavior and hardware semantics.

Dependencies and integration points: depends on Super I/O ports, DMI quirks, watchdog core, ITE GPIO/EC register layout, and module parameters for timeout/test/nowayout.

Risks and test signals: risks include unsupported/unknown chip IDs, DMI-specific output routing, minute rounding surprises, testmode disabling reset output, and lack of a conventional ping op. Test detection for each supported ID class, firmware-running handoff, timeout rounding, DMI Qotom PWRGD quirk, stop-on-reboot, and hardware reset output in normal versus test mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it87_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ixp4xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/ixp4xx_wdt.c`

Purpose: watchdog-core driver for Intel IXP4xx network processors, including a restart-only fallback for the broken Rev A0 IXP42x watchdog.

Important APIs, types, and functions: `struct ixp4xx_wdt` stores watchdog core state, timer base, and clock rate. `ixp4xx_wdt_start()` unlocks with `IXP4XX_WDT_KEY`, loads timeout ticks, enables count/reset, and relocks. Stop unlocks and clears enable. `ixp4xx_wdt_restart()` loads zero and enables reset. A dummy ops table supports only restart on affected CPUs.

Control flow: probe chooses full or restart-only ops based on CPU revision helpers, gets timer base from platform data, obtains parent clock or falls back to 66.666 MHz, computes max timeout, reads warm-reset bootstatus, registers the watchdog, and logs availability.

State and persistence: hardware status register exposes warm reset cause as `WDIOF_CARDRESET`. The driver does not mark pre-enabled hardware running; it configures on user start. Timeout updates restart the watchdog if active.

Dependencies and integration points: depends on platform data containing the base address, parent fixed clock when available, IXP4xx CPU helpers, watchdog core, and MMIO raw writes.

Risks and test signals: risks include wrong platform-data base, Rev A0 behavior, clock fallback mismatch, and warm-reset status interpretation. Test both CPU revision paths, max timeout calculation from clock, restart-only watchdog semantics, bootstatus after warm reset, and active timeout updates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ixp4xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/jz4740_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/jz4740_wdt.c`

Purpose: watchdog-core driver for Ingenic JZ4740/JZ4780 watchdogs hosted in the TCU syscon/regmap block.

Important APIs, types, and functions: `struct jz4740_wdt_drvdata` stores watchdog core device, parent TCU regmap, watchdog clock, and clock rate. Ping writes `TCU_REG_WDT_TCNT = 0`; set_timeout disables `TCER`, writes `TDR`, clears counter, then restores enable if it was set; start enables the clock and counter; stop clears counter enable and disables the clock; restart starts with timeout zero.

Control flow: probe gets the `wdt` clock, rounds and sets it to the smallest possible rate, computes timeout bounds from 16-bit hardware, obtains the parent regmap with `device_node_to_regmap()`, sets nowayout/drvdata, and registers.

State and persistence: active state is in TCU `TCER` and clock enable state. Timeout is limited by `0xffff / clk_rate`; the default heartbeat is clamped into supported bounds. There is no bootstatus handling.

Dependencies and integration points: depends on OF compatibles `ingenic,jz4740-watchdog`/`jz4780`, TCU MFD regmap in the parent node, and a controllable watchdog clock.

Risks and test signals: risks include clock-rate rounding failures, timeout truncation through `u16`, parent regmap absence, and restart behavior with zero timeout. Test clock setup, start/stop clock balancing, timeout bounds, active set_timeout preserving enable state, and watchdog reset through restart.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/jz4740_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/keembay_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/keembay_wdt.c`

Purpose: Intel Keem Bay non-secure watchdog driver with separate timeout and threshold interrupts, secure-monitor interrupt clearing, and pretimeout support.

Important APIs, types, and functions: `struct keembay_wdt` holds watchdog core state, clock/rate, IRQs, and MMIO base. Writes go through `keembay_wdt_writel()`, which first writes `WDT_UNLOCK` to `TIM_SAFE`. Timeout and pretimeout registers are programmed from seconds times clock rate. Timeout ISR clears via SMC and calls `emergency_restart()`; threshold ISR disables pretimeout, clears via SMC, and notifies watchdog core.

Control flow: probe maps MMIO, gets clock rate, requests named `threshold` and `timeout` IRQs, initializes defaults, applies module timeout, writes timeout/pretimeout registers, registers watchdog, and stores drvdata. PM suspend stops an active watchdog, resume starts it.

State and persistence: timeleft is read from `TIM_WATCHDOG / rate`. Pretimeout register stores `timeout - pretimeout`; a threshold interrupt clears pretimeout to avoid repeated notifications. Clock is assumed enabled by default and is only read for rate.

Dependencies and integration points: depends on OF compatible `intel,keembay-wdt`, named IRQs, ARM SMCCC secure service `0x8200ff18`, watchdog core, emergency restart, and MMIO unlock protocol.

Risks and test signals: risks include secure monitor interrupt clearing failures, missing IRQ names, clock-rate mistakes, and pretimeout greater than timeout. Test threshold/timeout IRQ paths, SMC clear arguments, timeleft, suspend/resume, nowayout stop attempts, and timeout register overflow for high clock rates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/keembay_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/kempld_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/kempld_wdt.c`

Purpose: Kontron PLD watchdog driver for a staged hardware watchdog where the hardware pretimeout stage runs before the final timeout stage, opposite to the kernel API view.

Important APIs, types, and functions: `struct kempld_wdt_data` stores PLD parent data, watchdog core device, stage descriptors, pretimeout, and PM status. Stage helpers set action, timeout, and read programmed timeout using PLD clock and prescaler. `kempld_wdt_probe_stages()` discovers writable stage byte masks and assigns timeout/pretimeout stages. `kempld_wdt_ioctl()` implements legacy pretimeout ioctls.

Control flow: probe reads PLD config and forces nowayout if enable/global lock bits are set, attaches watchdog core, discovers stages, programs module timeout/pretimeout, imports existing hardware settings if enabled, installs stop-on-reboot/unregister, and registers. Start programs timeout action then sets enable. Stop clears enable and verifies it. Ping writes `'K'` to kick register. Suspend stores config and stops if enabled; resume restores active/stopped state.

State and persistence: watchdog state persists in PLD registers, including lock bits that can make nowayout mandatory. Timeout and pretimeout are reconstructed from stage registers when firmware left the watchdog enabled. Hardware stages are described by masks discovered at runtime.

Dependencies and integration points: depends on the parent `kempld` MFD, PLD mutex/register APIs, PLD clock rate, optional NMI feature mask, watchdog core, platform PM hooks, and module parameters.

Risks and test signals: risks include stage assignment bugs, inverted pretimeout semantics, lock-bit handling, prescaler rounding, and ioctl/core pretimeout inconsistencies. Test stage probing on one- and two-stage PLDs, locked watchdogs, pretimeout NMI delivery, suspend/resume with BIOS-modified state, and timeout reconstruction from existing registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/kempld_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lantiq_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lantiq_wdt.c`

Purpose: Lantiq SoC watchdog driver for XRX/Falcon variants, using password-protected control register writes and syscon reset-cause reporting.

Important APIs, types, and functions: `struct ltq_wdt_priv` stores watchdog core state, MMIO base, and divided clock rate. Start/stop/ping use a two-password sequence (`PW1`, then `PW2`) through `ltq_wdt_mask()`. `ltq_wdt_get_timeleft()` reads the status counter. Variant callbacks read reset status from RCU syscon phandles.

Control flow: probe maps watchdog registers, computes watchdog clock from `clk_get_io() / LTQ_WDT_DIVIDER`, initializes timeout to max, reads variant bootstatus, applies nowayout and OF timeout, detects already-enabled watchdog, reprograms it with current settings, marks `WDOG_HW_RUNNING`, and registers.

State and persistence: enable and counter state live in watchdog control/status registers. Reset cause is variant-specific syscon state. If firmware left the watchdog enabled, Linux overwrites settings without a stop and takes ownership.

Dependencies and integration points: depends on Lantiq SoC clock helper, MMIO, syscon/regmap phandles `regmap` or `lantiq,rcu`, OF compatible match data, and watchdog core.

Risks and test signals: risks include broken password sequencing, clock divider too high yielding zero rate, bootstatus phandle differences, and max timeout derived from clock. Test XRX/Falcon reset cause, already-running handoff, get_timeleft, start/ping password writes, and nowayout/module parameter behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lantiq_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se10_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se10_wdt.c`

Purpose: Lenovo SE10 watchdog driver for specific DMI-matched systems using Super I/O BRAM and EC command ports.

Important APIs, types, and functions: `set_bram()` writes watchdog control/config bytes through the BRAM base discovered from Super I/O. `send_cmd()` waits on EC input/output buffer flags. Watchdog ops start by writing `CUS_WDT_SWI=0x80`, stop writes zero, set_timeout writes `CUS_WDT_CFG`, get_timeleft sends `CUS_WDT_CNT`, and ping sends `CUS_WDT_FEED`.

Control flow: module init uses DMI callbacks to create a platform device for supported Lenovo product names. Probe reserves Super I/O config ports, verifies chip ID `0x5632`, reads BRAM base from LDN 0x10, initializes watchdog defaults and nowayout, programs the default timeout, installs stop-on-reboot/unregister, and registers.

State and persistence: global `bram_base` stores the hardware access window. Timeout and enable state are stored in board controller BRAM/EC state. The driver does not read bootstatus. EC buffer waits are bounded by `MAX_WAIT` loops but `wait_for_buffer()` itself returns no status.

Dependencies and integration points: depends on DMI product IDs 12NH/12NJ/12NK/12NL/12NM, x86 I/O ports, Super I/O config mode, watchdog core, and EC command protocol.

Risks and test signals: risks include DMI over/under matching, silent EC wait timeout, BRAM base discovery errors, and no locking around global BRAM base beyond muxed regions. Test DMI creation/removal, chip ID mismatch, timeout 1-255 bounds, get_timeleft EC command, ping under load, and stop-on-reboot/unregister.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se10_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se30_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se30_wdt.c`

Purpose: Lenovo SE30 watchdog driver for DMI-matched systems using an NCT6692-based shared-memory host interface discovered through Super I/O.

Important APIs, types, and functions: Super I/O helpers enter/exit config mode and read chip/base registers. `shm_get_ready()` programs module/cmd/select fields, issues read control, and waits for ID change. `read_shm_win()` and `write_shm_win()` access the SHM data window. `lenovo_se30_wdt_enable()` writes reset config and watchdog count; ping disables, writes count, then re-enables because active refresh is unsupported.

Control flow: module init creates a platform device from DMI matches. Probe verifies chip ID mask, reads SHM base from LDN 0x0F, reserves and maps the SHM region, initializes watchdog register descriptors, sets bounds and nowayout, installs stop-on-reboot/unregister, and registers.

State and persistence: watchdog timeout is an 8-bit count in the board controller, with no bootstatus tracking. The active watchdog cannot be refreshed in-place; ping briefly disables and re-enables it. If SHM readiness times out, read returns zero timeleft or write returns error.

Dependencies and integration points: depends on Lenovo DMI product names 11NA/11NB/11NC/11NH/11NJ/11NK, Super I/O ports, MMIO SHM window, watchdog core, and NCT6692 host-interface semantics.

Risks and test signals: risks include ping disable/enable race, SHM ready timeout, invalid base address, DMI matching drift, and no `.set_timeout` op despite advertising `WDIOF_SETTIMEOUT`. Test DMI platform creation, SHM base validation, start/stop/ping sequences, timeleft reads, and behavior during reboot/unregister.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se30_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/loongson1_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/loongson1_wdt.c`

Purpose: Loongson1/LS2K0300 watchdog-core driver with variant-specific register offsets and enable bits.

Important APIs, types, and functions: `struct ls1x_wdt_pdata` supplies timer, set, and enable-bit layout. `ls1x_wdt_ping()` writes the set register, `ls1x_wdt_set_timeout()` writes clock-rate-scaled counts capped by max hardware heartbeat, start writes the enable bit, stop clears it, and restart enables with a count of one.

Control flow: probe obtains match data, maps MMIO, enables the clock, computes `max_hw_heartbeat_ms`, initializes watchdog defaults and module heartbeat, sets nowayout/drvdata, and registers. PM suspend stops active watchdogs; resume restarts them.

State and persistence: timeout count is stored in hardware timer register; logical timeout can exceed one hardware heartbeat because watchdog core may supervise via `max_hw_heartbeat_ms`. No bootstatus is reported.

Dependencies and integration points: depends on OF compatibles `loongson,ls1b-wdt`, `ls1c-wdt`, `ls2k0300-wdt`, a clock, MMIO, watchdog core, and simple PM ops.

Risks and test signals: risks include incorrect variant offset data, clock-rate overflow, not restoring timeout on resume beyond start, and no reboot stop hook. Test all compatible layouts, timeout counts, restart reset, suspend/resume active state, and heartbeat values above hardware max.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/loongson1_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lpc18xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lpc18xx_wdt.c`

Purpose: NXP LPC18xx watchdog driver for hardware that cannot be disabled after start, using an internal kernel timer to keep feeding after user-space stop.

Important APIs, types, and functions: `struct lpc18xx_wdt_dev` stores watchdog core device, register/watchdog clocks, MMIO, timer, and spinlock. `lpc18xx_wdt_feed()` writes the `0xaa`/`0x55` feed sequence under irqsave spinlock to avoid abort conditions. `lpc18xx_wdt_stop()` starts periodic internal feeding. Restart deliberately writes a bad feed sequence after enabling reset.

Control flow: probe maps MMIO, enables `reg` and `wdtclk`, computes timeout bounds from 24-bit counter and divide-by-4 prescaler, initializes timeout and hardware TC, sets up the feed timer, sets nowayout and restart priority, installs stop-on-reboot, and registers. Start cancels internal feeding, enables watchdog/reset bits, and performs a valid feed. Remove warns that hardware will likely reboot and deletes the timer.

State and persistence: hardware disable is impossible, so "stop" means kernel-owned periodic feeding at half the timeout. Timeleft is read from `TV` and converted by clock rate. Timer state distinguishes active userspace management from fallback kernel feeding.

Dependencies and integration points: depends on OF compatible `nxp,lpc1850-wwdt`, two clocks, MMIO, watchdog core, timer API, and restart priority.

Risks and test signals: risks include feed sequence interruption, timer fallback being mistaken for hardware stop, removal causing reset, and clock-derived timeout bounds. Test start-stop-start transitions, timer feed cadence, bad-feed restart, get_timeleft conversion, stop-on-reboot, and behavior when userspace closes the watchdog.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lpc18xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/m54xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/m54xx_wdt.c`

Purpose: legacy miscdevice watchdog for ColdFire MCF547x/MCF548x processors using GPT0 watchdog bits.

Important APIs, types, and functions: `wdt_enable()` preserves GPT GPIO settings, programs `GCIR0` from `heartbeat` and bus clock, and sets watchdog enable/count enable with the output compare password. `wdt_disable()` clears enable bits. `wdt_keepalive()` rewrites the password bit. File operations implement single-open, magic close, ioctls, and keepalive writes.

Control flow: init reserves the GPT counter register region and registers `/dev/watchdog`. Open sets in-use state, clears OK-to-close, and enables hardware. Writes scan for `V` when not nowayout and ping. Ioctl supports support/status/bootstatus/keepalive/set/get timeout with max 30 seconds. Release disables only when magic close was seen; otherwise it pings and leaves the watchdog running.

State and persistence: state is tracked with `wdt_status` bits `WDT_IN_USE` and `WDT_OK_TO_CLOSE`, plus global heartbeat/nowayout. Bootstatus is not available. Hardware GPT configuration may preserve pre-existing GPIO usage.

Dependencies and integration points: depends on ColdFire architecture headers/registers, misc watchdog ABI, raw MMIO access, and module parameters.

Risks and test signals: risks include bus-clock math, preserving GPIO mode incorrectly, heartbeat maximum mismatch, and legacy close semantics. Test region reservation, magic close versus unexpected close, set_timeout reprogramming, keepalive writes, nowayout module pinning behavior, and GPT register values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/m54xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/machzwd.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/machzwd.c`

Purpose: legacy MachZ ZF-Logic watchdog driver using fixed I/O ports and a kernel timer to bridge a short hardware watchdog interval to a user-space heartbeat window.

Important APIs, types, and functions: fixed port helpers access ZF registers through index/data ports. `zf_timer_on()` programs WD1/WD2, sets `next_heartbeat`, starts the kernel timer, and enables WD1 with selected action. `zf_ping()` feeds WD2 and toggles `RESET_WD1` while user heartbeat is fresh. File ops implement writes, keepalive ioctl, open/close, and magic close.

Control flow: init verifies ZF-Logic version, maps module `action` to RESET/SMI/NMI/SCI, reserves I/O ports, registers reboot notifier and misc device, then clears status/control. Open enforces single-open and starts internal/hardware timers. User writes extend `next_heartbeat`. The kernel timer pings every ~500 ms until the user heartbeat expires. Close disables only with magic close, otherwise it deletes the internal timer and leaves hardware to reset. Reboot notifier turns timers off.

State and persistence: software state includes `zf_is_open`, `zf_expect_close`, `next_heartbeat`, selected action, spinlock, and kernel timer. Hardware has two cascading watchdog timers; WD2 eventually resets unconditionally after WD1 expires.

Dependencies and integration points: fixed I/O base `0x218`, misc watchdog ABI, reboot notifier, timer API, spinlock-protected port access, and module action/nowayout parameters.

Risks and test signals: risks include action-bit mapping, kernel timer deletion causing intentional reset, no timeout ioctl, and short hardware interval sensitivity. Test hardware detection, all action modes, magic close, unexpected close reset path, reboot notifier, and timer keepalive cadence under scheduler stress.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/machzwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/marvell_gti_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/marvell_gti_wdt.c`

Purpose: Marvell GTI central watchdog driver for CN9670/CN10K-style timers, using a selected GTI timer in interrupt/pretimeout/reset mode.

Important APIs, types, and functions: `struct gti_wdt_priv` stores watchdog core state, GTI base, clock, selected timer index, and match data. `gti_wdt_settimeout()` makes pretimeout one third of timeout and programs CNT/LEN fields in 1024-cycle units. `gti_wdt_start()` clears pending interrupt, enables interrupt, and sets mode 3. `gti_wdt_interrupt()` clears pending status and calls `watchdog_notify_pretimeout()`.

Control flow: probe maps GTI MMIO, enables/reads clock, selects the last timer unless `marvell,wdt-timer-index` overrides it, computes maximum pretimeout/timeout from counter fields, programs initial timeout, installs stop-on-reboot/unregister, registers watchdog, then requests the IRQ.

State and persistence: selected GTI timer registers hold mode, reload, and interrupt enable state. Hardware mode uses first timeout as kernel pretimeout, second SCP event effectively ignored by configuration, and third timeout as reset. Start sets `WDOG_HW_RUNNING`.

Dependencies and integration points: depends on OF compatibles `marvell,cn9670-wdt` and `marvell,cn10624-wdt`, GTI clock, MMIO, platform IRQ, optional timer-index property, and watchdog core pretimeout semantics.

Risks and test signals: risks include requesting IRQ after watchdog registration, timer index conflicts, 1/3 pretimeout policy surprises, and counter rounding/saturation. Test timer-index bounds, IRQ pretimeout, max timeout math by clock, stop disabling interrupts/mode, and full reset after missed pings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/marvell_gti_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max63xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/max63xx_wdt.c`

Purpose: watchdog-core driver for Maxim MAX6369-6374 external watchdog chips connected through memory-mapped WDI/WDSET pins.

Important APIs, types, and functions: timeout tables describe WDSET pin encodings, initial delay, and watchdog timeout. `max63xx_select_timeout()` chooses a table entry honoring the `nodelay` parameter for MAX6373/74. `max63xx_mmap_ping()` toggles WDI, and `max63xx_mmap_set()` writes WDSET bits under a spinlock. Start programs WDSET and pings edge-triggered no-delay modes; stop selects disabled WDSET value.

Control flow: probe selects a timeout table from OF match data or platform ID, validates/clamps heartbeat, chooses a hardware setting, maps the one-byte resource, initializes watchdog core timeout/info/ops, sets nowayout, registers, and logs selected timeout and initial delay.

State and persistence: hardware timeout is quantized to chip table entries and may be much longer than nominal according to datasheet variation. Driver state stores the selected table entry and MMIO access callbacks. No bootstatus or set_timeout op is provided.

Dependencies and integration points: depends on platform or OF IDs for specific Maxim variants, a memory-mapped byte resource, watchdog core, spinlock-protected raw byte access, and module parameters `heartbeat`, `nowayout`, `nodelay`.

Risks and test signals: risks include board-specific wiring assumptions, timeout tolerance much larger than selected value, nodelay selection failure, and disabling via WDSET not supported on all wiring. Test each variant table, heartbeat requests around available values, MMIO bit preservation, edge-triggered startup ping, and stop/nowayout behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max63xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max77620_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/max77620_wdt.c`

Purpose: Maxim MAX77620/MAX77714 PMIC watchdog driver using the parent MFD regmap and variant-specific register layouts.

Important APIs, types, and functions: `struct max77620_variant` describes ONOFF/CNFG registers, WDT clear mask, reset-wake bit, and auto-clear bits. Start/stop toggle `MAX77620_WDTEN`; ping writes the WDTC bit; set_timeout maps requested seconds to fixed 2/16/64/128 second hardware choices and clears the watchdog before changing TWD.

Control flow: probe obtains variant data from platform ID and parent regmap, enables watchdog-reset wake, sets auto-clear bits for sleep/off modes where supported, reads existing config to infer current timeout and running state, marks `WDOG_HW_RUNNING` if enabled, sets nowayout/drvdata, installs stop-on-unregister, and registers.

State and persistence: PMIC registers hold timeout, enable, and reset behavior across Linux driver lifetime and possibly across warm boot depending on PMIC state. Timeout values are rounded upward to one of four hardware settings. There is no bootstatus reporting.

Dependencies and integration points: depends on parent MAX77620/MAX77714 MFD regmap, platform device IDs, watchdog core, and PMIC register definitions.

Risks and test signals: risks include variant register mismatch, timeout rounding surprises, write ordering around WDTC/TWD, and stop-on-unregister interacting with nowayout expectations. Test both variants, existing enabled watchdog handoff, timeout bucket selection, ping writes, sleep/off auto-clear behavior, and register error propagation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max77620_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mei_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mei_wdt.c`

Purpose: Intel MEI iAMT watchdog driver that exposes a firmware-managed AMT watchdog through the watchdog core and dynamically registers/unregisters depending on firmware "watchdog required" state.

Important APIs, types, and functions: `struct mei_wdt` stores watchdog core object, MEI client, internal state, response completion, unregister work, registration lock, timeout, and optional debugfs. Packed MEI Management Control request/response structs encode start/ping and stop commands. `mei_wdt_ops_start()` transitions to START; ping sends start/ping and optionally waits for a response; stop sends stop only from RUNNING. RX callback validates firmware responses and reacts to `MEI_WDT_WDSTATE_NOT_REQUIRED`.

Control flow: probe allocates state, enables the MEI client, registers RX and notification callbacks, records firmware version, and either pings firmware for a response-required probe or registers immediately for legacy firmware. RX during PROBE stops firmware watchdog and registers if required, or marks NOT_REQUIRED. RX during RUNNING may schedule unregister work to avoid watchdog-core deadlock. Remove completes any waiter, cancels work, unregisters, disables MEI, removes debugfs, and frees state.

State and persistence: the authoritative watchdog is in Intel ME/AMT firmware. Driver state machine values are PROBE, IDLE, START, RUNNING, STOPPING, and NOT_REQUIRED. Registration state is guarded by `reg_lock`, and drvdata being non-NULL means registered. Firmware version controls whether ping responses are required.

Dependencies and integration points: depends on MEI client bus UUID `05B79A6F-4628-4D7F-899D-A91514CB32AB`, watchdog core, MEI send/recv/notif APIs, completions/workqueue, and optional debugfs files `state` and `activation`.

Risks and test signals: risks include response wait interruption, dynamic unregister during pings, firmware declaring watchdog not required, deadlock if unregister happens in RX context, and global `wd_info.firmware_version` mutation. Test legacy and response-required firmware, NOT_REQUIRED transitions and notification reactivation, stop while not running, debugfs state, MEI reset/remove with outstanding completion, and min timeout enforcement at 120 seconds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mei_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mena21_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mena21_wdt.c`

Purpose: MEN A21 VME CPU board watchdog driver controlled entirely by six GPIO lines for enable, fast mode, trigger, and reset-cause inputs.

Important APIs, types, and functions: `struct a21_wdt_drv` stores watchdog core state and six GPIO descriptors. Start/stop set the enable GPIO, ping toggles trigger low then high with a 10 ns delay, set_timeout accepts only 1 or 30 seconds and controls the fast GPIO, and `a21_wdt_get_bootstatus()` reads three reset-status GPIOs.

Control flow: probe verifies exactly six GPIOs, acquires them by index, keeps initial values for output GPIOs, initializes static watchdog defaults, sets nowayout/drvdata/parent, maps reset bit patterns to bootstatus flags, stores driver data, and registers. Shutdown deasserts enable.

State and persistence: state is external board GPIO latch state; timeout mode is represented by the fast GPIO. Transition from 1-second fast mode back to 30-second slow mode is explicitly rejected. Bootstatus is decoded from reset GPIO combinations.

Dependencies and integration points: depends on OF compatible `men,a021-wdt`, GPIO descriptor ordering in devicetree, watchdog core, and board-specific reset-code wiring.

Risks and test signals: risks include GPIO ordering mistakes, static global watchdog object shared assumptions, fast-to-slow transition limitation, and no stop-on-reboot helper beyond shutdown. Test DT GPIO count/order, reset-code mappings, only accepted timeout values, trigger pulse visibility, shutdown disable, and nowayout behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mena21_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menf21bmc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/menf21bmc_wdt.c`

Purpose: MEN 14F021P00 BMC watchdog driver using SMBus commands to a parent I2C BMC device.

Important APIs, types, and functions: `struct menf21bmc_wdt` stores watchdog core state and the parent `i2c_client`. Start sends `BMC_CMD_WD_ON`, stop writes `BMC_CMD_WD_OFF` with magic value `0x69`, ping sends `BMC_CMD_WD_TRIG`, set_timeout writes `BMC_CMD_WD_TIME` in 100 ms units, and bootstatus reads `BMC_CMD_RST_RSN`.

Control flow: probe obtains the parent I2C client, allocates state, initializes watchdog bounds, reads the current BMC timeout because BMC persists it across restarts, initializes the watchdog timeout from that value, sets nowayout/drvdata, maps reset reason to bootstatus, registers, and logs enabled state. Shutdown writes the watchdog-off command.

State and persistence: timeout value is stored in the BMC and survives system restart, so probe imports it. Bootstatus is BMC reset-reason state. Stop requires the magic off value.

Dependencies and integration points: depends on platform device under an I2C BMC, SMBus byte/word operations, watchdog core, and platform shutdown.

Risks and test signals: risks include SMBus endianness/word units, persistent BMC timeout surprises, shutdown command using word write for an off command otherwise written as byte-data, and no stop-on-reboot helper. Test BMC timeout import, reset-reason mappings, start/stop/ping SMBus transactions, nowayout, and shutdown on poweroff/reboot.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menf21bmc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menz69_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/menz69_wdt.c`

Purpose: watchdog-core driver for MEN z069 IP-core devices on the MCB bus.

Important APIs, types, and functions: `struct men_z069_drv` stores watchdog core device, MMIO base, and claimed MCB memory resource. `men_z069_wdt_start()` sets `WDEN`, stop clears it, ping toggles the watchdog trigger value by XORing `WVR` with `0xffff`, and set_timeout writes seconds converted at 500 Hz into `WTR` while preserving enable.

Control flow: MCB probe requests the `z069-wdt` memory resource, maps it, initializes timeout bounds from the 15-bit counter, applies watchdog_init_timeout, sets nowayout/drvdata/parent, stores MCB drvdata, and registers with watchdog core. Remove unregisters and releases MCB memory.

State and persistence: hardware state is in `WTR` and `WVR`; timeout counter max is `0x7fff / 500`. No bootstatus is reported. The driver preserves enable state while changing timeout.

Dependencies and integration points: depends on MCB bus device ID `0x45`, MCB memory APIs, MMIO, watchdog core, and namespace import `MCB`.

Risks and test signals: risks include resource release on partial probe, timeout multiplication overflow beyond 15 bits, trigger toggle assumptions, and unregister ordering. Test MCB resource mapping, timeout bounds, start/stop bit preservation, ping toggling, and remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menz69_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_gxbb_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/meson_gxbb_wdt.c`

Purpose: watchdog driver for newer Amlogic Meson GXBB/T7 watchdog hardware with 1 ms timebase setup, optional running-state handoff, and timeleft support.

Important APIs, types, and functions: `struct meson_gxbb_wdt` stores MMIO, watchdog core device, and clock. Match `wdt_params` supplies reset bit position. Start/stop toggle `GXBB_WDT_CTRL_EN`; ping writes reset register; set_timeout writes `TCNT` setup value in milliseconds; get_timeleft subtracts current count from setup count.

Control flow: probe maps registers, enables clock, reads match data, initializes watchdog core bounds and module timeout, detects an already-enabled watchdog and temporarily stretches timeout while preserving running state, programs control register with divider/reset/clock bits, sets final timeout, and registers. PM suspend stops active watchdog; resume restarts it.

State and persistence: watchdog enable may persist from boot and is marked `WDOG_HW_RUNNING`. Timeout register is limited to 16-bit milliseconds, so max hardware heartbeat is about 65 seconds. Control register holds clock divider and reset routing.

Dependencies and integration points: depends on OF compatibles `amlogic,meson-gxbb-wdt` and `amlogic,t7-wdt`, clock rate, MMIO, watchdog core, and system sleep PM ops.

Risks and test signals: risks include divider truncation, max timeout clamping while recording requested timeout, preserving enabled state during setup, and T7 reset-bit differences. Test already-running firmware handoff, get_timeleft, suspend/resume, timeout near 65 seconds, and reset-line behavior per compatible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_gxbb_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/meson_wdt.c`

Purpose: watchdog driver for older Amlogic Meson6/Meson8 watchdog blocks with variant-specific enable bits, counter masks, and count units.

Important APIs, types, and functions: `struct meson_wdt_data` describes enable bit, terminal-count mask, and counts-per-second. `meson_wdt_change_timeout()` updates terminal count bits, ping writes the reset register, start programs timeout/pings/enables, stop clears enable, and restart loops writing a reset-enabled terminal count until hardware resets.

Control flow: probe maps MMIO, selects match data, computes max timeout from mask/count unit, initializes watchdog defaults and restart priority, applies module timeout and nowayout, stops the watchdog initially, installs stop-on-reboot, registers, and logs settings.

State and persistence: the driver intentionally stops the watchdog during probe rather than handing off a running firmware watchdog. Timeout is stored in terminal-count bits and constrained by variant mask. No bootstatus or timeleft support is provided.

Dependencies and integration points: depends on OF compatibles `amlogic,meson6-wdt`, `meson8-wdt`, `meson8b-wdt`, `meson8m2-wdt`, watchdog core, MMIO, and restart priority.

Risks and test signals: risks include stopping a bootloader-enabled watchdog unexpectedly, count-unit differences, infinite restart loop if reset fails, and max timeout calculation. Test each compatible data set, start/stop/ping, reboot restart, module timeout bounds, and stop-on-reboot behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mixcomwd.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mixcomwd.c`

Purpose: legacy ISA-style MixCOM/FlashCOM watchdog miscdevice driver that probes fixed I/O ports and uses an internal timer because the hardware cannot be shut down normally.

Important APIs, types, and functions: `mixcomwd_io_info[]` lists candidate ports and card IDs. `checkcard()` reserves a port and validates ID. `mixcomwd_ping()` writes magic value 55. `mixcomwd_timerfun()` pings every five seconds. File ops implement single-open, magic close, status ioctl, and keepalive.

Control flow: init scans the fixed port list until a card responds, registers `/dev/watchdog`, and leaves the port reserved. Open pings and, if not nowayout, cancels any internal keepalive timer from a prior close. Writes optionally scan for `V` and ping. Release with magic close starts the internal ping timer instead of disabling hardware; unexpected release logs that the watchdog will not stop. Exit warns and deletes internal timer, deregisters misc device, and releases the port.

State and persistence: driver state includes `mixcomwd_opened`, `watchdog_port`, `mixcomwd_timer_alive`, `expect_close`, and a kernel timer. Hardware keeps running once activated; "close" transfers responsibility to kernel timer.

Dependencies and integration points: depends on fixed legacy I/O port probing, misc watchdog ABI, timer API, module nowayout, and port reservation.

Risks and test signals: risks include false-positive fixed-port probing, timer cleanup causing reset, no timeout setting, and confusing close semantics. Test card detection on all supported ports, status bit reporting, magic close timer behavior, unexpected close, module exit warning, and nowayout module pinning.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mixcomwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mlx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mlx_wdt.c`

Purpose: Mellanox/NVIDIA watchdog driver for platform-data-described regmap watchdog blocks, supporting main reset watchdogs and auxiliary alarm-only watchdogs across three hardware types.

Important APIs, types, and functions: `struct mlxreg_wdt` stores watchdog core state, parent platform data, regmap, register indices, value size, and type. `mlxreg_wdt_config()` discovers action/timeout/timeleft/ping/reset registers by label. Timeout setting differs by type: type1 uses power-of-two milliseconds, type2 writes seconds, type3 writes 16-bit seconds across one or two regmap bytes. `mlxreg_wdt_check_card_reset()` reads reset-cause register for main watchdogs.

Control flow: probe obtains platform data/regmap, validates regmap value size, configures info/ops/bounds from platform identity and version, applies NOWAYOUT/start-at-boot feature flags, initializes timeout from platform health counter, optionally starts and marks `WDOG_HW_RUNNING`, checks bootstatus, and registers with stop-on-reboot/unregister.

State and persistence: state lives in parent CPLD/regmap registers. Platform data labels determine all register semantics. Type1 rounds timeout down to the actual closest power-of-two interval. Start-at-boot feature means Linux immediately enables and owns the watchdog.

Dependencies and integration points: depends on `mlxreg_core_platform_data`, regmap, platform features, watchdog core, and board-specific label conventions.

Risks and test signals: risks include missing/mislabeled platform data, timeout rounding for type1, 16-bit byte-order handling for type3, reset-cause mask semantics, and restart on active timeout change. Test all three types, main versus aux info flags, feature flags, timeleft reads, timeout restart behavior, and bootstatus detection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mlx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/moxart_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/moxart_wdt.c`

Purpose: MOXA ART SoC watchdog driver using simple MMIO count/mode/enable registers and watchdog core restart support.

Important APIs, types, and functions: `struct moxart_wdt_dev` stores watchdog core device, MMIO base, and clock frequency. Start writes `clock_frequency * timeout` to count, magic mode `0x5ab9`, and enable `0x03`; stop writes zero to enable; set_timeout only updates the core timeout; restart programs count one and enables reset.

Control flow: probe maps MMIO, gets the clock and validates frequency, computes max timeout from `UINT_MAX / clock_frequency`, initializes watchdog core defaults with optional module heartbeat, sets nowayout and restart priority, installs stop-on-unregister, registers, and logs debug state.

State and persistence: timeout count is only written on start or restart; changing timeout while running updates software state but does not immediately reprogram hardware because set_timeout does not restart or write registers. No bootstatus/timeleft is provided.

Dependencies and integration points: depends on OF compatible `moxa,moxart-watchdog`, a clock, MMIO, watchdog core, and restart priority 128.

Risks and test signals: risks include set_timeout while active not affecting hardware until restart/start, clock frequency overflow, and no stop-on-reboot. Test active timeout changes, start/restart register sequence, stop-on-unregister, heartbeat module parameter, and reset behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/moxart_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mpc8xxx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mpc8xxx_wdt.c`

Purpose: watchdog driver for Freescale/NXP MPC8xx/MPC83xx/MPC86xx watchdogs with one-time enable/disable hardware behavior and Open Firmware matching.

Important APIs, types, and functions: `struct mpc8xxx_wdt_ddata` stores MMIO base, watchdog core device, spinlock, and computed SWTC count. `mpc8xxx_wdt_keepalive()` writes the required `0x556c`/`0xaa39` service sequence under spinlock. `mpc8xxx_wdt_start()` programs SWCRR with enable, prescaler, count, and reset/interrupt mode, verifies enable, marks `WDOG_HW_RUNNING`, and pings.

Control flow: `arch_initcall()` registers the platform driver early. Probe gets match data, system frequency, maps registers, rejects hardware-enabled-only variants if firmware has not enabled them, optionally maps reset status resource to set/clear bootstatus, initializes watchdog core timeout and nowayout, computes SWTC/max hardware heartbeat, starts if already enabled, registers, and stores drvdata.

State and persistence: hardware may only allow enable or disable once after power-on reset. For variants marked `hw_enabled`, software cannot enable if firmware did not. Reset-cause bits are read and cleared from an optional second memory resource. Logical timeout is adjusted to at least hardware minimum heartbeat.

Dependencies and integration points: depends on OF compatibles `mpc83xx_wdt`, `fsl,mpc8610-wdt`, `fsl,mpc823-wdt`, `fsl_get_sys_freq()`, big-endian MMIO access, watchdog core, and early platform-driver registration.

Risks and test signals: risks include one-time enable semantics, reset versus interrupt mode module parameter, system-frequency conversion, and bootstatus clear side effects. Test firmware-enabled and software-enabled variants, keepalive sequence, reset-status resource handling, timeout/SWTC calculation, nowayout, and mode selection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mpc8xxx_wdt.c -->
