# subset-b-005594 Research

Grouped research for Linux watchdog drivers under `sources/distributed-fs/ceph-client/drivers/watchdog`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rave-sp-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rave-sp-wdt.c

Purpose: watchdog-core driver for the Zodiac Inflight Innovations RAVE Supervisory Processor MCU. It exposes the SP firmware watchdog through Linux watchdog APIs and also uses it as a high-priority restart handler.

Important APIs, types, and functions: `struct rave_sp_wdt_variant` captures protocol differences between legacy and RDU command layouts. `struct rave_sp_wdt` owns the `watchdog_device`, parent `struct rave_sp`, variant, and reboot notifier. Key functions are `rave_sp_wdt_exec()`, variant `configure()` and `restart()` helpers, `rave_sp_wdt_start()`, `rave_sp_wdt_stop()`, `rave_sp_wdt_ping()`, `rave_sp_wdt_set_timeout()`, `rave_sp_wdt_reboot_notifier()`, and `rave_sp_wdt_probe()`.

Control flow: probe allocates state, selects OF match data, reads an optional NVMEM `wdt-timeout`, initializes watchdog limits from the variant, registers a reboot notifier, starts the hardware unconditionally because previous state is unknown, then registers the watchdog. Start and timeout changes send SP configuration commands. Ping sends `RAVE_SP_CMD_PET_WDT`. Restart is split: a reboot notifier sends the UART/SP reset command during `SYS_DOWN`/`SYS_HALT`, while watchdog `.restart` only waits for the firmware-delayed reset.

State and persistence behavior: persistent runtime state is the watchdog core status, selected timeout, variant pointer, and SP transport handle. The optional NVMEM cell supplies an initial timeout. `WDOG_HW_RUNNING` is set after successful start, and `max_hw_heartbeat_ms` lets watchdog core keep the firmware-fed watchdog alive.

Dependencies and integration points: depends on the RAVE SP MFD command transport, OF match data, NVMEM consumer API, reboot notifier infrastructure, and watchdog core restart priority.

Risks and edge cases: reset cannot be issued from atomic restart context because SP communication may use UART, so notifier ordering is critical. Probe starts the watchdog before registration; registration failure must stop it. Variant command byte layouts differ, and the RDU timeout is 16-bit while legacy is 8-bit.

Test signals: boot with both compatibles, NVMEM and DT timeout override tests, watchdog start/stop/ping/set-timeout, registration-failure unwind, clean reboot/halt restart behavior, and SP command error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rave-sp-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rc32434_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rc32434_wdt.c

Purpose: legacy miscdevice watchdog for the IDT RC32434 SoC watchdog registers. It provides `/dev/watchdog` operations directly instead of using `watchdog_device`.

Important APIs, types, and functions: global `rc32434_wdt_device` stores open state and an I/O spinlock, while `wdt_reg` maps `struct integ` watchdog registers. Key routines are `rc32434_wdt_set()`, `rc32434_wdt_start()`, `rc32434_wdt_stop()`, `rc32434_wdt_ping()`, file operations, ioctl handling, platform probe/remove/shutdown, and `SET_BITS()`.

Control flow: probe maps the named memory resource, initializes the lock, stops any running watchdog, validates the module timeout, then registers `/dev/watchdog`. Open enforces single user, optionally pins the module under nowayout, starts and pings the hardware. Write scans for magic close `V` and pings. Ioctl implements support/status, enable/disable, keepalive, and set/get timeout. Release stops only after magic close; otherwise it keeps the watchdog alive.

State and persistence behavior: state is global, not per-device: timeout, expected-close flag, open bit, and mapped register pointer. Hardware state is in `wtcompare`, `wtcount`, `errcs`, and `wtc`; shutdown stops the watchdog.

Dependencies and integration points: depends on RC32434 platform resources, board `idt_cpu_freq`, miscdevice `WATCHDOG_MINOR`, userspace watchdog ioctls, and raw MMIO helpers.

Risks and edge cases: `rc32434_wdt_start()` takes `io_lock` and calls `rc32434_wdt_set()`, which takes the same spinlock again, making lock recursion a notable review point. Timeout conversion depends on external CPU frequency and 32-bit compare range. Global state prevents multiple devices.

Test signals: open exclusivity, magic-close and unexpected-close paths, timeout bounds against `idt_cpu_freq`, start/stop register bits, shutdown disable, and lockdep coverage around start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rc32434_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rdc321x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rdc321x_wdt.c

Purpose: legacy RDC321x watchdog miscdevice backed by southbridge PCI configuration registers, with a kernel timer that keeps the short hardware watchdog enabled while userspace supplies a longer emulated heartbeat.

Important APIs, types, and functions: `rdc321x_wdt_device` stores completion, timer, queue/running flags, default ticks, lock, southbridge `pci_dev`, and base config register. Important functions are `rdc321x_wdt_trigger()`, `rdc321x_wdt_start()`, `rdc321x_wdt_stop()`, `rdc321x_wdt_reset()`, file operations, ioctl handling, probe, and remove.

Control flow: probe requires platform data containing the southbridge PCI device and a `wdt-reg` I/O resource, resets the watchdog register, initializes completion and timer, and registers `/dev/watchdog`. Enable starts the periodic timer and writes config bits that clear and enable the hardware watchdog. The timer decrements emulated `ticks`, rewrites the enable bit to feed hardware, and completes removal once queueing stops or ticks expire.

State and persistence behavior: runtime state is process-open bit, timer queue flag, `running` counter, `ticks`, and PCI register values. `rdc321x_wdt_stop()` deliberately returns `-EIO` after clearing running state, indicating hardware cannot really be disabled through the normal API.

Dependencies and integration points: uses platform data from `linux/mfd/rdc321x.h`, PCI config space read/write, Linux timers, completion, miscdevice watchdog ABI, and spinlock serialization.

Risks and edge cases: no nowayout/magic-close support is implemented despite being a watchdog miscdevice. `running` is incremented on each start and not a boolean under all paths. Remove waits for timer completion, so stale queue state can delay unload. PCI config register semantics are hardware-specific.

Test signals: platform-data absence, PCI register read/write tracing, enable/disable ioctl behavior, timer expiry path, remove while queued, and userspace keepalive extending `ticks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rdc321x_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/realtek_otto_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/realtek_otto_wdt.c

Purpose: watchdog-core driver for Realtek Otto MIPS SoCs, supporting two watchdog phases, pretimeout notification, configurable reset mode, and restart.

Important APIs, types, and functions: `struct otto_wdt_ctrl` owns the watchdog, device, MMIO base, clock rate, and phase1 IRQ. Key functions are `otto_wdt_start()`, `otto_wdt_stop()`, `otto_wdt_ping()`, `otto_wdt_determine_timeouts()`, timeout/pretimeout setters, `otto_wdt_restart()`, `otto_wdt_phase1_isr()`, and probe helpers for clock and reset mode.

Control flow: probe maps registers, clears stale interrupts, resets control defaults, gets the clock, requests the named `phase1` IRQ, parses optional `realtek,reset-mode`, sets watchdog bounds, programs an initial timeout/pretimeout pair, and registers with watchdog core. Timeout programming searches prescaler values until both phase fields fit. Phase1 IRQ clears the interrupt and calls `watchdog_notify_pretimeout()`. Restart disables phase1 IRQ, picks reset mode from reboot action, programs the shortest enabled timeout, and waits.

State and persistence behavior: state is MMIO control, phase counters, selected reset mode, watchdog timeout/pretimeout, clock rate, and IRQ binding. Pretimeout cannot be fully disabled, so the driver always keeps phase split state.

Dependencies and integration points: depends on clocks, platform IRQ resources, fwnode properties, bitfield helpers, reboot action constants, watchdog core, and OF compatibles for RTL8380/8390/9300/9310.

Risks and edge cases: timeout rounding can change requested values; pretimeout must be less than timeout. Restart disables the IRQ but does not restore it because reset is expected. Bad clock rate makes all time calculations invalid. Hardware cannot be stopped after phase1 according to comments.

Test signals: reset-mode property variants, timeout/pretimeout rounding, phase1 interrupt notification, start/stop/ping MMIO writes, restart actions for soft/warm/default reboot, and invalid clock/property failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/realtek_otto_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wdt.c

Purpose: watchdog-core driver for Renesas R-Car WDT blocks, including runtime PM, bootstatus detection, restart, and suspend/resume.

Important APIs, types, and functions: `struct rwdt_priv` stores MMIO base, watchdog, clock rate, selected clock divider, and clock. Key routines are `rwdt_write()`, `rwdt_init_timeout()`, `rwdt_wait_cycles()`, `rwdt_start()`, `rwdt_stop()`, `rwdt_get_timeleft()`, `rwdt_restart()`, quirk blacklist helpers, probe, remove, suspend, and resume.

Control flow: probe rejects blacklisted early R-Car Gen2 cases, maps registers, gets the clock, enables runtime PM long enough to read overflow/running status, selects a divider that fits the 16-bit counter, initializes watchdog bounds, honors DT timeout, restarts firmware-enabled hardware if needed, then registers. Start stops the timer, waits required cycles, writes counter/divider/reset registers, waits for write-ready, and enables. Stop clears TME and runtime-suspends. Restart uses atomic-safe clock enable and polling to force a near-immediate overflow.

State and persistence behavior: state persists in `wdev.status`, `bootstatus`, selected `cks`, timeout, runtime PM usage, and WDT registers. Suspend stops active watchdog and resume restarts it.

Dependencies and integration points: uses clk, PM runtime, OF match, SoC revision matching, SMP boot CPU count quirks, watchdog core restart priority, relaxed MMIO, and polling helpers.

Risks and edge cases: register writes require magic keys and cycle delays; skipping delays can lose writes. Blacklist logic depends on SoC IDs and SMP setup. Restart is atomic and cannot sleep. Runtime PM balance must match active state.

Test signals: divider selection at clock extremes, firmware-running detection, bootstatus overflow, runtime PM counts, suspend/resume active and inactive cases, restart latency, and blacklisted SoC handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wwdt.c

Purpose: watchdog-core driver for Renesas R-Car Window Watchdog Timer, where firmware is expected to configure the one-shot WWDT setup and Linux adapts to it.

Important APIs, types, and functions: `struct wwdt_priv` contains MMIO base and watchdog. Important routines are `wwdt_start()`, `wwdt_error_irq()`, `wwdt_pretimeout_irq()`, and `wwdt_probe()`.

Control flow: probe maps registers, gets the `cnt` clock, reads run and mode registers, derives interval and closed-window size, sets min/max hardware heartbeat and timeout from firmware configuration, forces nowayout, conditionally requests an error IRQ when ECM reset mode is not selected, conditionally requests a pretimeout IRQ when WIE is set, and registers the watchdog. Start writes the run key to `WDTA0WDTE`.

State and persistence behavior: Linux does not program the full WWDT mode because hardware can be set up only once after boot. State is firmware-defined register configuration, watchdog running bit, calculated heartbeat windows, and optional IRQ subscriptions.

Dependencies and integration points: depends on OF compatibles, a `cnt` clock, named `error` and `pretimeout` IRQ resources, watchdog pretimeout notification, and R-Car ECM behavior.

Risks and edge cases: if firmware did not configure WWDT correctly, Linux has limited ability to repair it. Window size is a closed-window fraction, so early pings can violate hardware timing. `devm_watchdog_register_device()` return is ignored in probe, which is a notable error-handling weakness.

Test signals: firmware-running and stopped cases, all WDTA0OVF/WDTA0WS derived timing values, error and pretimeout IRQ delivery, nowayout behavior, and registration failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/retu_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/retu_wdt.c

Purpose: watchdog-core driver for the Nokia Retu MFD watchdog. The hardware cannot be disabled, so the driver either hands feeding to userspace or self-feeds while stopped.

Important APIs, types, and functions: `struct retu_wdt_dev` stores parent `retu_dev`, device pointer, and delayed ping work. Key functions are `retu_wdt_ping_enable()`, `retu_wdt_ping_disable()`, `retu_wdt_ping_work()`, watchdog start/stop/ping/set-timeout operations, and probe.

Control flow: probe allocates watchdog and private state, sets bounds of 0..63 seconds, binds drvdata, creates auto-cancel delayed work, registers the watchdog, then either pings once for nowayout or schedules periodic self-feeding. Start cancels self-feeding and writes the userspace timeout to the Retu register. Stop re-enables self-feeding. Ping and set-timeout write the timeout directly.

State and persistence behavior: state is the delayed work schedule, selected timeout, nowayout flag, and Retu watchdog register. There is no persistent storage; stopped state is emulated by periodically programming the maximum timer.

Dependencies and integration points: depends on the Retu MFD driver, `retu_write()`, devm delayed-work autocancel, watchdog core, and platform device parent data.

Risks and edge cases: because hardware cannot stop, any failure in delayed work scheduling or Retu writes can reset the system unexpectedly. `min_timeout` is zero, which is unusual and should match hardware semantics. In nowayout mode self-feeding is skipped.

Test signals: start/stop transition between userspace and kernel feeding, delayed work cancellation on removal, Retu write failures, timeout bounds, nowayout behavior, and long idle stopped-state survival.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/retu_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/riowd.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/riowd.c

Purpose: legacy miscdevice watchdog for Sun RIO systems using a NatSemi Super I/O power-management logical device.

Important APIs, types, and functions: `struct riowd` stores two-byte indexed register window and a spinlock. Key functions are `riowd_writereg()`, miscdevice open/release/write/ioctl handlers, probe, remove, and OF match.

Control flow: probe allows only one device, maps two bytes from the OF resource, publishes global `riowd_device`, and registers `/dev/watchdog`. Keepalive writes the timeout in minutes to index `WDTO_INDEX`; disable writes zero. `WDIOC_SETTIMEOUT` accepts seconds, validates 60..15300, rounds up to minutes, writes hardware, and returns seconds.

State and persistence behavior: state is global pointer, spinlock, and module parameter `riowd_timeout` in minutes. Hardware timeout state persists in Super I/O register index 0x05 until changed.

Dependencies and integration points: depends on OF platform resource mapping with `of_ioremap()`, miscdevice watchdog ABI, indexed Super I/O register access, and the Sun BBC reset wiring described in comments.

Risks and edge cases: no open-exclusion bit is used, so multiple opens can race. The driver has no magic close or nowayout handling. Timeout granularity is minutes, and SETTIMEOUT rounds up. If misc registration fails, the global pointer is cleared, but remove does not clear it.

Test signals: OF resource map/unmap, timeout rounding, enable/disable ioctl, concurrent opens/writes, status ioctls, and reset-line behavior on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/riowd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rn5t618_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rn5t618_wdt.c

Purpose: watchdog-core driver for the Ricoh RN5T618 PMIC watchdog using the parent regmap.

Important APIs, types, and functions: `struct rn5t618_wdt` holds the watchdog and parent PMIC pointer. Important routines are `rn5t618_wdt_set_timeout()`, `rn5t618_wdt_start()`, `rn5t618_wdt_stop()`, `rn5t618_wdt_ping()`, and probe.

Control flow: probe gets the parent PMIC, initializes watchdog bounds from a four-entry hardware timeout map, reads `RN5T618_POFFHIS` to set bootstatus, applies module/DT timeout, and registers. Set-timeout selects the smallest hardware map entry whose timeout plus the one-second interrupt grace period covers the requested value. Start programs timeout, enables repower-on, enables watchdog, and enables watchdog interrupt. Ping reads and rewrites the watchdog register to restart the counter, then clears the pending interrupt.

State and persistence behavior: persistent hardware state is in PMIC registers: watchdog enable/time, repower-on, interrupt enable, IRQ pending, and power-off history. Driver state is selected timeout and nowayout.

Dependencies and integration points: depends on RN5T618 MFD definitions, regmap, platform parent data, watchdog core, and PMIC power-off history semantics.

Risks and edge cases: timeout selection intentionally rounds up and reports the hardware-supported value, not the user value. Multi-step start can leave partial enablement if later regmap updates fail. Ping depends on read/write side effects documented by the PMIC.

Test signals: all timeout map selections, bootstatus for VINDET and WDG, regmap error injection during start/ping, interrupt clearing, stop disable, and nowayout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rn5t618_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rt2880_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rt2880_wdt.c

Purpose: watchdog-core driver for Ralink/MediaTek RT288x/RT3xxx/MT76xx timer1 watchdog hardware.

Important APIs, types, and functions: `struct rt2880_wdt_data` stores MMIO base, divided clock frequency, clock/reset handles, and watchdog. Key routines are `rt288x_wdt_ping()`, `rt288x_wdt_start()`, `rt288x_wdt_stop()`, `rt288x_wdt_set_timeout()`, `rt288x_wdt_bootcause()`, and probe.

Control flow: probe maps timer registers, gets clock, optionally deasserts reset, computes the prescaled frequency, fills watchdog limits, reads boot cause from the SoC reset-status register, initializes timeout, sets nowayout, and registers. Start configures timer1 as watchdog mode with 65536 prescale, loads timeout counts, and enables. Stop reloads and clears enable. Set-timeout updates software timeout and reloads hardware.

State and persistence behavior: state is hardware timer control/load registers, SoC reset-status bit, selected timeout, clock-derived frequency, and optional reset controller state.

Dependencies and integration points: depends on Ralink architecture `rt_sysc_r32()`, clocks, reset controller, platform MMIO, OF compatible, and watchdog core stop-on-reboot.

Risks and edge cases: `wdt->max_timeout = 0xffff / freq` can become zero if the prescaled clock is too high. Probe returns 0 even if `devm_watchdog_register_device()` fails, losing error propagation. Optional reset deassert errors are ignored when the reset is absent but also ignored if deassert fails.

Test signals: clock-rate extremes, reset status bootcause, start/stop register programming, timeout reload, failed registration behavior, and reset-controller failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rt2880_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rtd119x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rtd119x_wdt.c

Purpose: built-in watchdog-core driver for Realtek RTD129x/RTD119x style watchdog registers.

Important APIs, types, and functions: `struct rtd119x_watchdog_device` stores watchdog, MMIO base, and clock. Important functions are `rtd119x_wdt_start()`, `rtd119x_wdt_stop()`, `rtd119x_wdt_ping()`, `rtd119x_wdt_set_timeout()`, and probe.

Control flow: probe maps registers, enables the clock, initializes watchdog bounds from the clock rate, stops on reboot, clears the watchdog, programs the default timeout, stops hardware, and registers. Start and stop replace the low enable byte in `TCWCR` with magic enable/disable values. Ping writes the clear bit then calls start. Timeout writes seconds multiplied by clock rate into overflow register.

State and persistence behavior: state is entirely MMIO plus selected timeout; the driver is built in with `builtin_platform_driver()`. No bootstatus or nowayout handling is present.

Dependencies and integration points: depends on platform MMIO, enabled clock, OF compatible `realtek,rtd1295-watchdog`, and watchdog core.

Risks and edge cases: multiplication of timeout by clock rate is written as 32-bit and relies on max-timeout calculation to avoid overflow. `watchdog_info.options` is zero even though operations support timeout and ping. No `watchdog_init_timeout()` means DT timeout property is ignored.

Test signals: default timeout programming, max timeout from clock, start/stop magic values, ping re-enabling behavior, stop-on-reboot, and DT timeout ignored/regression awareness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rtd119x_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rti_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rti_wdt.c

Purpose: watchdog-core driver for Texas Instruments K3 RTI windowed watchdog modules, including always-nowayout behavior and optional reserved-memory bootstatus handoff.

Important APIs, types, and functions: `struct rti_wdt_device` holds MMIO base, source frequency, and watchdog. Key routines are `rti_wdt_start()`, `rti_wdt_ping()`, `rti_wdt_setup_hw_hb()`, `rti_wdt_get_timeleft_ms()`, `rti_wdt_get_timeleft()`, probe, and remove.

Control flow: probe gets the clock rate, enables runtime PM, maps registers, initializes watchdog bounds and nowayout, detects already-enabled hardware, derives heartbeat/window settings from hardware, optionally reads a reserved memory magic sequence to set `WDIOF_CARDRESET`, initializes timeout, registers, records last hardware keepalive when applicable, and runtime-suspends if not running. Start resumes PM, programs preload, NMI reaction, 50 percent open window, min hardware heartbeat, and enable key. Ping writes the two-key service sequence.

State and persistence behavior: state includes runtime PM state, watchdog enabled bit, preload/window registers, min heartbeat, last-ping estimate, timeout, and reserved-memory reset-cause words that are cleared after read.

Dependencies and integration points: uses clocks, PM runtime, reserved-memory OF mapping, `memremap()`, watchdog core last keepalive, and K3 RTI register protocol.

Risks and edge cases: windowed watchdog pings too early can be fatal; min heartbeat must match hardware window. Reserved memory must be at least 12 bytes and trusted. If already running, heartbeat configuration is ignored. Nowayout is forced.

Test signals: already-running detection, last-ping calculation, reserved-memory magic and clearing, window size cases, early/late ping behavior, runtime PM balance, and get-timeleft at timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rti_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rza_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rza_wdt.c

Purpose: watchdog-core driver for Renesas RZ/A watchdog variants with 3-bit and 4-bit clock selectors and restart support.

Important APIs, types, and functions: `struct rza_wdt` owns watchdog, MMIO base, clock, reload count, and clock selector. Main routines are `rza_wdt_calc_timeout()`, `rza_wdt_start()`, `rza_wdt_stop()`, `rza_wdt_ping()`, `rza_set_timeout()`, `rza_wdt_restart()`, and probe.

Control flow: probe maps registers, gets clock, validates minimum rate, chooses variant data from OF, computes max timeout or max hardware heartbeat, initializes timeout, and registers. Start stops the timer, clears overflow after required dummy read, calculates reload, enables reset, writes counter and control. Ping reloads the saved count. Set-timeout restarts with the new timeout. Restart programs fastest clock and one tick before overflow, then waits.

State and persistence behavior: state is selected `cks`, computed `count`, watchdog timeout, and hardware counter/control/reset registers. No PM or bootstatus state is tracked.

Dependencies and integration points: depends on OF match data, clocks, watchdog core, magic-keyed 16-bit MMIO writes, and restart callback.

Risks and edge cases: 3-bit variants cannot represent even one-second hardware timeouts, so watchdog core must use `max_hw_heartbeat_ms`. Timeout changes restart the timer, which can perturb active timing. Clock rate assumptions drive both max timeout and reload count.

Test signals: both compatibles, clock-rate validation, max timeout/heartbeat calculations, ping reload value, timeout restart while active, and restart reset latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rza_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzg2l_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rzg2l_wdt.c

Purpose: watchdog-core driver for Renesas RZ/G2L and RZ/V2M watchdogs, using reset controls, runtime PM, and two different restart mechanisms.

Important APIs, types, and functions: `struct rzg2l_wdt_priv` stores MMIO base, watchdog, reset controller, oscillator/PCLK rates, register delay, clocks, and device type. Important functions are `rzg2l_wdt_write()`, `rzg2l_wdt_init_timeout()`, start/stop/set-timeout/restart/ping, PM disable action, probe, and suspend/resume callbacks.

Control flow: probe maps registers, gets `oscclk` and `pclk`, computes synchronization delay, gets reset control, enables IRQ-safe runtime PM, sets watchdog bounds, nowayout, stop-on-unregister, timeout, and registers. Start resumes PM, deasserts reset, clears interrupt/lapsed time, programs timeout for two overflow cycles, clears counter, and enables. Stop asserts reset and runtime-suspends. Timeout changes stop/start active hardware. Restart powers hardware, then either forces parity error on RZ/G2L or resets/programs zero timeout on RZ/V2M.

State and persistence behavior: state is reset assertion, PM usage, programmed WDTSET/WDTTIM/WDTCNT/WDTINT registers, selected timeout, and device-type-specific restart path.

Dependencies and integration points: depends on clocks, reset controller, PM runtime/genpd IRQ-safe behavior, OF match data, Linux units helpers, and watchdog core restart.

Risks and edge cases: register writes require calculated synchronization delays. Restart intentionally leaves PM usage elevated for reboot. Active timeout changes reset the block, creating a short watchdog blind spot. `WDTSET` is only 12 bits.

Test signals: RZ/G2L versus RZ/V2M restart, PM/reset error injection, active timeout update, suspend/resume active and inactive states, max timeout calculation, and register delay correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzg2l_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzn1_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rzn1_wdt.c

Purpose: watchdog-core driver for the Renesas RZ/N1 short-period watchdog, relying on watchdog core heartbeats because hardware cannot provide long timeouts.

Important APIs, types, and functions: `struct rzn1_watchdog` stores watchdog, MMIO base, and clock rate in kHz. Key routines are `max_heart_beat_ms()`, `compute_reload_value()`, `rzn1_wdt_ping()`, `rzn1_wdt_start()`, IRQ handler, and probe.

Control flow: probe maps registers, requests the watchdog IRQ, enables the clock, computes max hardware heartbeat, caps it at one second, initializes a default 60-second logical timeout, and registers. Start writes the one-shot retrigger register with interrupt mode, enable, prescale, and reload value. Ping writes any value to retrigger. IRQ logs a critical timeout and calls `emergency_restart()`.

State and persistence behavior: hardware state is a write-once retrigger/configuration register after start; software state is max hardware heartbeat and logical watchdog timeout. `WATCHDOG_NOWAYOUT_INIT_STATUS` is set.

Dependencies and integration points: depends on platform IRQ, OF node name for IRQ registration, clocks, watchdog core auto-ping for max hardware heartbeat, and reboot emergency restart path.

Risks and edge cases: the hardware register can be written only once, so timeout cannot change after start. Clock changes after start alter real timeout. The maximum period may be below two seconds, making watchdog core scheduling essential.

Test signals: max-heartbeat computation, one-time start behavior, watchdog core auto-ping, IRQ-triggered emergency restart, clock-rate zero handling, and timeout DT initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzn1_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzv2h_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rzv2h_wdt.c

Purpose: watchdog-core driver for Renesas RZ/V2H(P), RZ/T2H, and RZ/N2H watchdogs, with optional debug-control register support and restart.

Important APIs, types, and functions: `struct rzv2h_of_data` describes clock source/dividers/TOPS/debug-control support. `struct rzv2h_wdt_priv` stores MMIO windows, clocks, reset control, watchdog, and OF data. Key routines are `rzv2h_wdt_ping()`, debug count start/stop helpers, `rzv2h_wdt_setup()`, start/stop/restart, `rzt2h_wdt_wdtdcr_init()`, and probe.

Control flow: probe selects OF data, maps base, gets prepared clocks, optional reset, chooses count clock, computes max hardware heartbeat, enables runtime PM, optionally initializes WDTDCR count-stop state, sets watchdog fields, nowayout, stop-on-unregister, timeout, and registers. Start resumes PM, deasserts reset, delays, writes WDTCR/WDTRCR/WDTSR, starts optional debug count, and refreshes via 0x00/0xff. Stop asserts reset, stops optional debug count, and runtime-suspends. Restart handles inactive clocks manually or resets active hardware, programs shortest window, refreshes, and waits.

State and persistence behavior: state spans reset/clock/PM state, optional WDTDCR counter-stop bit, watchdog control/status/reset registers, and selected OF data. No bootstatus is read.

Dependencies and integration points: uses prepared clocks, optional reset controls, PM runtime, OF match data, watchdog core, and SoC-specific window semantics.

Risks and edge cases: WDTCR and WDTRCR are writable only once between reset release and first refresh, so restart must reset active hardware. Optional `oscclk` must be present for LOCO-source SoCs. Manual `clk_enable()` in restart assumes clocks are already prepared.

Test signals: both OF data variants, optional WDTDCR path, start-stop PM/reset balance, inactive and active restart, refresh sequence ordering, and max hardware heartbeat calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzv2h_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/s32g_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/s32g_wdt.c

Purpose: watchdog-core driver for NXP S32G SWT watchdog hardware, including optional early enable and time-left reporting.

Important APIs, types, and functions: `struct s32g_wdt_device` stores counter clock rate, MMIO base, and watchdog. Key functions are `s32g_wdt_ping()`, `s32g_wdt_start()`, `s32g_wdt_stop()`, `s32g_wdt_set_timeout()`, `s32g_wdt_get_timeleft()`, `s32g_wdt_init()`, and probe.

Control flow: probe maps the SWT registers, gets the `counter` clock, initializes watchdog limits from a 32-bit timeout register and clock rate, applies module/DT timeout, nowayout, stop-on-unregister, initializes control register policy, optionally starts hardware under `early_enable`, registers, and logs configuration. Ping writes the fixed service sequence. Set-timeout writes timeout counts then pings. Get-timeleft temporarily stops running hardware because the counter-output register is readable only while disabled.

State and persistence behavior: state is the SWT control register, timeout register, counter output, selected timeout, clock rate, and `WDOG_HW_RUNNING` when early enabled.

Dependencies and integration points: depends on platform MMIO, `counter` clock, module parameters, watchdog core, and debug/suspend mode semantics in the SWT control register.

Risks and edge cases: get-timeleft briefly disables the watchdog, which is observable hardware state. Minimum timeout is zero because hardware clamps small counter values. Clock-rate changes after probe invalidate conversions. `watchdog_info.options` includes ioctl command constants, not only option flags.

Test signals: service sequence writes, early_enable, timeout count conversion, get-timeleft while active, nowayout stop rejection through core, and clock-rate boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/s32g_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/s3c2410_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/s3c2410_wdt.c

Purpose: watchdog-core driver for Samsung S3C2410-family, Exynos, Exynos Auto, and Google GS watchdog blocks, including extensive PMU syscon integration and SoC quirks.

Important APIs, types, and functions: `struct s3c2410_wdt_variant` describes PMU offsets, reset bits, counter-enable bits, and quirks. `struct s3c2410_wdt` stores device, bus/source clocks, MMIO, count, lock, suspend saves, watchdog, cpufreq notifier placeholder, variant, PMU regmap, and counter width. Key functions include PMU helpers, `s3c2410wdt_start()`, `s3c2410wdt_stop()`, `s3c2410wdt_keepalive()`, `s3c2410wdt_set_heartbeat()`, `s3c2410wdt_restart()`, IRQ handler, bootstatus reader, variant selection, probe, shutdown, suspend, and resume.

Control flow: probe selects variant and cluster-specific data, looks up PMU regmap if needed, maps registers, enables clocks, computes max timeout from clock/prescaler/counter width, sets heartbeat, requests IRQ, sets nowayout/restart priority/bootstatus, applies debug-mask quirk, either starts at boot or stops bootloader hardware, registers the watchdog, then enables PMU reset/counter routing. Start programs WTDAT/WTCNT/WTCON under lock and chooses interrupt-only mode when `soft_noboot` is set. Suspend saves WTCON/WTDAT, disables PMU routing, and stops; resume restores registers and routing.

State and persistence behavior: state is split across watchdog registers, PMU reset mask/disable/counter-enable registers, boot reset status, saved suspend registers, clock rates, module parameters, and watchdog core status.

Dependencies and integration points: depends on platform/OF matching, syscon regmap phandle, bus/source clocks, IRQ, PM sleep, watchdog core, and Samsung PMU register layouts.

Risks and edge cases: wrong cluster index or PMU quirk data can mask the wrong reset line. Heartbeat math depends on clock rates and 16-bit versus 32-bit counters. PMU enable happens after watchdog registration, so probe unwind uses devm action. `soft_noboot` converts reset into IRQ keepalive behavior.

Test signals: each compatible/cluster variant, PMU mask/reset/counter bits, bootstatus, 16/32-bit max timeout, `tmr_atboot`, `soft_noboot` IRQ path, suspend/resume restoration, restart, and missing syscon/clock/IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/s3c2410_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sa1100_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sa1100_wdt.c

Purpose: legacy miscdevice watchdog for SA11x0/PXA2xx OS timer channel 3 watchdog functionality.

Important APIs, types, and functions: global state stores OS timer frequency, open bit, `pre_margin`, boot status, MMIO base, module margin, and clock. Key routines are `sa1100dog_open()`, release/write/ioctl handlers, probe, and remove.

Control flow: probe maps OS timer registers, gets and enables `OSTIMER0`, derives `oscr_freq`, sets bootstatus from platform data, computes default margin, and registers `/dev/watchdog`. Open enforces single user, sets match register 3 to current counter plus margin, clears status, enables watchdog match and interrupt. Writes and keepalive update the match register. Timeout ioctl validates the counter product fits 32 bits and updates `pre_margin`.

State and persistence behavior: watchdog cannot be disabled once activated according to comments; release only logs and clears open state. Hardware state is OSMR3, OSSR, OWER, and OIER. Software state is precomputed margin and bootstatus.

Dependencies and integration points: depends on platform MMIO resource, legacy clock name lookup, platform data boot flag, miscdevice ABI, and SA/PXA OS timer hardware.

Risks and edge cases: no nowayout parameter or magic close is implemented because stop is unavailable. Timeout arithmetic can overflow without the explicit check. Clock lookup uses `clk_get(NULL, "OSTIMER0")`, which is global and platform-specific.

Test signals: single-open behavior, match register refresh, timeout bounds around 32-bit counter wrap, platform bootstatus, clock enable/disable, and release while active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sa1100_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sama5d4_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sama5d4_wdt.c

Purpose: watchdog-core driver for Atmel/Microchip SAMA5D4, SAM9X60, and SAMA7G5 watchdog timers, supporting hardware reset or software-reset interrupt modes.

Important APIs, types, and functions: `struct sama5d4_wdt` stores watchdog, MMIO base, mode and interrupt registers, last ping timestamp, IRQ need flag, and SAM9X60 capability flag. Key functions are timed `wdt_write()` helpers, start/stop/ping/set-timeout, IRQ handler, DT init, hardware init, probe, and suspend/resume.

Control flow: probe allocates state, detects SAM9X60-style hardware, maps registers, parses DT options (`atmel,watchdog-type`, idle/dbg halt), optionally requests IRQ for software reset, initializes timeout, detects already-running hardware, programs mode/load registers, sets nowayout and stop-on-unregister, registers, and stores drvdata. Writes respect a three-slow-clock delay after refresh. IRQ mode calls `emergency_restart()` on watchdog status. Suspend stops active watchdog; resume reinitializes registers and restarts if active.

State and persistence behavior: state includes cached mode/interrupt registers, last-ping jiffies, timeout, running bit from hardware, and suspend-time reinitialization. Hardware watchdog configuration may survive boot or suspend, and init tries to normalize it.

Dependencies and integration points: depends on AT91 watchdog register definitions, OF properties, IRQ mapping, watchdog core, jiffies delays, and emergency restart.

Risks and edge cases: writes too soon after ping violate hardware timing. Resume notes a FIXME because reinitialization also pings the watchdog. SAM9X60 and older WDT disable bits differ. Software-reset mode depends on IRQ availability.

Test signals: SAMA5D4 and SAM9X60 compatibles, software versus hardware reset mode, idle/dbg halt properties, write-delay compliance, already-running detection, suspend/resume, IRQ emergency restart, and timeout update while disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sama5d4_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sb_wdog.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sb_wdog.c

Purpose: legacy miscdevice driver for SiByte SB1 SoC watchdog timer 1, with interrupt warning and reboot notifier support.

Important APIs, types, and functions: global state includes `sbwd_lock`, kernel/user watchdog MMIO pointers, timeout in microseconds, open gate, and expected close. Key functions are `sbwdog_set()`, `sbwdog_pet()`, file operations, reboot notifier, shared IRQ handler, module init, and exit.

Control flow: module init registers reboot notifier, requests IRQ 1 for the user watchdog, and registers `/dev/watchdog`. Open enforces single user, pins module, writes initial count, and starts hardware. Write scans for magic `V`, pets the watchdog, and release disables only after magic close. IRQ handler logs impending reset for user watchdog or reloads the kernel watchdog. Reboot notifier disables both watchdogs on halt/down.

State and persistence behavior: state is global MMIO registers, user timeout, open bit, and expected-close flag. Hardware has two-stage behavior: first expiry interrupts, second resets.

Dependencies and integration points: depends on SiByte architecture I/O base/register definitions, IRQ 1 sharing, miscdevice watchdog ABI, reboot notifier, and raw MMIO accesses.

Risks and edge cases: raw pointer arithmetic assumes fixed SoC register layout. Timeout is limited to 23 bits. `WDIOC_GETTIMEOUT` returns remaining count rather than configured timeout. Module reference is always taken on open and only put on magic close.

Test signals: IRQ warning path, magic close and unexpected close, timeout upper bound, reboot notifier disabling both dogs, shared IRQ behavior, and user versus kernel watchdog register selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sb_wdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc60xxwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc60xxwdt.c

Purpose: legacy I/O-port watchdog driver for 60xx single-board computers. It emulates a longer userspace heartbeat by pinging short hardware from a kernel timer.

Important APIs, types, and functions: global state includes start/stop port parameters, timer, next heartbeat, open bit, expected close, timeout, and nowayout. Key functions are `wdt_timer_ping()`, `wdt_startup()`, `wdt_turnoff()`, `wdt_keepalive()`, file operations, reboot notifier, init, and unload.

Control flow: init validates timeout, reserves configured I/O ports, registers reboot notifier, and registers `/dev/watchdog`. Open enforces single user, optionally pins the module, starts the kernel timer. The timer reads from the start port every quarter second while userspace heartbeat is fresh. Writes update `next_heartbeat` and scan for `V`. Close disables only with magic close; otherwise it stops the kernel timer and leaves hardware to expire.

State and persistence behavior: software state is timer and heartbeat deadline; hardware state is controlled by reads from start/stop I/O ports. Timeout is an emulated userspace supervision interval, not hardware timeout.

Dependencies and integration points: depends on x86-style port I/O, miscdevice watchdog ABI, kernel timers, reboot notifier, and manually configured module ports.

Risks and edge cases: hardware parameters cannot be probed, so wrong ports can affect unrelated hardware. Unexpected close deletes the ping timer, intentionally allowing reset. Stop port 0x45 may be unreserved because the kernel already owns it.

Test signals: port reservation paths, timer ping cadence, heartbeat expiry, magic close, nowayout module pinning, reboot notifier, and timeout bounds 1..3600.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc60xxwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc7240_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc7240_wdt.c

Purpose: legacy I/O-port watchdog driver for IEI NANO7240 SBC watchdog hardware.

Important APIs, types, and functions: global `wdt_status` bitfield tracks open, enabled, and expected-close states. Key routines are `wdt_enable()`, `wdt_disable()`, `wdt_set_timeout()`, `wdt_keepalive()`, file operations, reboot notifier, init, and unload.

Control flow: module init reserves enable port 0x443, validates and writes timeout, disables hardware, registers reboot notifier, then registers `/dev/watchdog`. Open enforces single user and enables hardware. Write scans for `V` when nowayout is false and keeps alive by reading enable port. Close disables when expected close is set or nowayout is false; otherwise it keeps hardware alive and logs. Ioctl supports enable/disable, keepalive, and timeout.

State and persistence behavior: state is timeout in seconds, status bits, and hardware state toggled by I/O port reads/writes. The disable port 0x043 is not reserved because it overlaps system timer resources.

Dependencies and integration points: depends on I/O port access, miscdevice watchdog ABI, reboot notifier, module parameters, and SBC-specific port semantics.

Risks and edge cases: the `nowayout` description says "Disable watchdog when closing" but the logic treats nowayout as cannot-stop. Hardware disable uses an unreserved port. Close logic disables on any close when nowayout is false, even without magic close.

Test signals: timeout range 1..255, enable/disable port I/O, nowayout false and true close behavior, magic close, reboot notifier, and port conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc7240_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc8360.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc8360.c

Purpose: legacy I/O-port watchdog driver for SBC8360 boards using a table of vendor timeout encodings.

Important APIs, types, and functions: global state includes open bit, expected close, 64-entry `wd_times` table, selected timeout index, margin, multiplier, and nowayout. Key functions are `sbc8360_activate()`, `sbc8360_ping()`, `sbc8360_stop()`, write/open/close handlers, reboot notifier, init, and exit.

Control flow: init validates timeout index, reserves enable and base-time ports, registers reboot notifier and miscdevice, then derives margin/multiplier from the table and logs milliseconds. Open enforces single user, pins module if nowayout, performs the enable phase sequence with sleeps, and pings once. Writes scan for magic close and ping. Close stops only after magic close; otherwise it leaves hardware running.

State and persistence behavior: state is module-global and only one device is supported. Hardware state is configured through ports 0x120 and 0x121; actual timeout is encoded by the margin/multiplier table.

Dependencies and integration points: depends on legacy port I/O, miscdevice watchdog ABI, reboot notifier, and module parameters.

Risks and edge cases: no ioctl implementation is provided, so timeout cannot be changed at runtime through watchdog ioctls. Error path after second `request_region()` failure releases only the first region, but if first request fails no resources exist. Activation uses interruptible sleeps without checking interruption.

Test signals: all timeout index classes, open/write/close magic semantics, reboot notifier stop, port reservation cleanup, nowayout module pin, and absence of ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc8360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_epx_c3.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc_epx_c3.c

Purpose: simple legacy watchdog miscdevice for Winsystems EPX-C3 boards using fixed control and pet I/O ports.

Important APIs, types, and functions: global `epx_c3_alive` tracks open state. Important functions are `epx_c3_start()`, `epx_c3_stop()`, `epx_c3_pet()`, file operations, ioctl handler, reboot notifier, init, and exit.

Control flow: init reserves two I/O ports, registers reboot notifier, and registers `/dev/watchdog`. Open rejects concurrent users, pins the module when nowayout, enables hardware, pets it, and marks alive. Write pets. Ioctl supports support/status, enable/disable, keepalive, and fixed get-timeout. Release disables only when nowayout is false. Reboot notifier disables on halt/down.

State and persistence behavior: state is only `epx_c3_alive`, nowayout, and hardware port values. Timeout is fixed at one second and not programmable.

Dependencies and integration points: depends on port I/O, miscdevice watchdog ABI, reboot notifier, and board-specific non-probeable hardware.

Risks and edge cases: open-state flag is not atomic and can race. There is no magic close despite normal watchdog expectations. The driver warns in module description that it cannot probe hardware, so loading on wrong systems can write unrelated ports.

Test signals: correct board-only loading policy, I/O port reservation, concurrent open race testing, fixed timeout ioctl, nowayout release behavior, and reboot notifier disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_epx_c3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_fitpc2_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc_fitpc2_wdt.c

Purpose: legacy miscdevice watchdog for Compulab SBC-FITPC2 boards, detected by DMI board name and controlled through command/data I/O ports.

Important APIs, types, and functions: global state includes nowayout, margin, status bits, and `wdt_lock`. Key routines are `wdt_send_data()`, `wdt_enable()`, `wdt_disable()`, file operations, ioctl handler, init, and exit.

Control flow: init checks DMI board name for `SBC-FITPC2`, reserves command and data ports, validates margin 31..255 seconds, and registers `/dev/watchdog`. Open enforces single user and enables. Enable sends interface-on and reboot-timeout commands with sleeps. Write scans for `V` only when nowayout is false, then enables again as keepalive. Close disables only when OK-to-close was set; otherwise it re-enables and logs.

State and persistence behavior: state is status bits, configured margin, and hardware controller state through command/data ports. No bootstatus is tracked.

Dependencies and integration points: depends on DMI, port I/O, mutex serialization, miscdevice watchdog ABI, and board firmware command timing.

Risks and edge cases: when nowayout is true, write returns zero after still refreshing hardware, which may surprise userspace expecting byte count. Command protocol uses fixed sleeps and can be slow. No reboot notifier disables the watchdog on shutdown.

Test signals: DMI match/non-match, margin bounds, command ordering with delays, magic close, nowayout write return, concurrent ioctl/write locking, and port conflict cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_fitpc2_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbsa_gwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbsa_gwdt.c

Purpose: watchdog-core driver for ARM SBSA Generic Watchdog with single-stage reset mode or two-stage WS0 panic mode.

Important APIs, types, and functions: `struct sbsa_gwdt` stores watchdog, system counter frequency, architecture version, MediaTek WS0 race workaround flag, and refresh/control frame bases. Key routines are versioned WOR read/write, `sbsa_gwdt_set_timeout()`, `sbsa_gwdt_get_timeleft()`, `sbsa_gwdt_keepalive()`, `sbsa_gwdt_get_version()`, start/stop, WS0 interrupt handler, probe, suspend, and resume.

Control flow: probe maps control and refresh frames, reads generic timer frequency, initializes watchdog, reads IIDR version/implementer, computes max heartbeat for 32-bit or 48-bit WOR, detects WS1 boot reset and already-enabled state, optionally requests WS0 IRQ for panic action, doubles max timeout in single-stage mode, initializes timeout, writes WOR, stops on reboot, and registers. Start sets WCS enable; ping writes WRR; get-timeleft combines WCV and system counter, adding an extra WOR stage in single-stage mode.

State and persistence behavior: state is hardware WCS flags, WOR offset, WCV compare, bootstatus, action module parameter, timeout, and min heartbeat workaround. Suspend stops active hardware and resume restarts when watchdog core says hardware was running.

Dependencies and integration points: depends on ARM arch timer counter/frequency, MMIO 64-bit lo/hi helpers, platform resources, optional IRQ, watchdog core, and panic path.

Risks and edge cases: `action` is a global module parameter and can be downgraded if IRQ request fails. MediaTek workaround changes min heartbeat to avoid refresh-at-WS0 race. Timeleft math assumes counter monotonicity and valid WCV.

Test signals: v0/v1 WOR width, action 0 and 1, IRQ failure fallback, WS1 bootstatus, already-running detection, MediaTek IIDR workaround, suspend/resume, and timeleft before/after WS0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbsa_gwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc1200wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sc1200wdt.c

Purpose: legacy miscdevice watchdog for National Semiconductor PC87307/PC97307 Super I/O watchdogs, with optional ISA PnP discovery.

Important APIs, types, and functions: global state includes timeout in minutes, I/O base/length, open flag, expected close, spinlock, optional PnP device, and nowayout. Key functions are indexed register read/write helpers, `sc1200wdt_start()`, `sc1200wdt_stop()`, `sc1200wdt_status()`, file operations, reboot notifier, ISA/PnP probe/remove, module init, and exit.

Control flow: init optionally registers a PnP driver to discover the I/O base; otherwise it requires `io=`. It reserves ports, probes by checking PMC3 default bits, registers reboot notifier, and registers `/dev/watchdog`. Open enforces single user, clamps timeout, starts hardware by configuring WDCF and WDTO. Write scans magic close and reloads WDTO. Ioctl supports status, enable/disable, keepalive, and timeout seconds converted to minutes.

State and persistence behavior: state is Super I/O PM index/data registers, timeout minutes, bootstatus fixed zero, and open/expected-close bits. Hardware status reads WDO inactive-high state.

Dependencies and integration points: depends on port I/O, optional PNP, miscdevice watchdog ABI, reboot notifier, and Super I/O register semantics.

Risks and edge cases: timeout seconds are divided by 60, so values below 60 become zero and can disable hardware. PnP and manual I/O paths share globals. Probe heuristic can fail if firmware disabled related devices.

Test signals: PnP discovery and manual `io=`, PMC3 probe success/failure, timeout conversion edge cases, magic close, status reporting, reboot notifier stop, and port cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc1200wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc520_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sc520_wdt.c

Purpose: legacy miscdevice watchdog for AMD Elan SC520 MMCR watchdog. It uses a kernel timer to service a short hardware timeout while userspace supplies a longer heartbeat.

Important APIs, types, and functions: global state includes mapped `wdtmrctl`, kernel timer, next heartbeat, open bit, expected close, timeout, nowayout, and spinlock. Key functions are `wdt_timer_ping()`, `wdt_config()`, `wdt_startup()`, `wdt_turnoff()`, `wdt_keepalive()`, `wdt_set_heartbeat()`, file operations, reboot notifier, init, and unload.

Control flow: init validates timeout, maps MMCR watchdog control register at a fixed physical address, registers reboot notifier, and registers `/dev/watchdog`. Open enforces single user, pins module if nowayout, starts kernel timer and configures hardware for reset with a 2-second-ish hardware expiry. Timer writes the service sequence while userspace heartbeat is fresh. Close stops only on magic close; otherwise it leaves hardware active.

State and persistence behavior: software state is the emulated heartbeat deadline; hardware state is MMCR watchdog control and service/config unlock sequences. Unload disables only when nowayout is false.

Dependencies and integration points: depends on fixed SC520 MMCR mapping, raw MMIO service sequences, miscdevice watchdog ABI, reboot notifier, and Linux timers.

Risks and edge cases: fixed physical address can be wrong on unsupported hardware. Timer deletion on unexpected close stops kernel feeding, deliberately causing reset. Configuration unlock sequence must be exact. No explicit request_mem_region is used.

Test signals: ioremap failure, service/config write sequence, heartbeat expiry, magic close and nowayout, reboot notifier, timeout bounds, and timer cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc520_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sch311x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sch311x_wdt.c

Purpose: legacy Super I/O watchdog driver for SMSC SCH3112/SCH3114/SCH3116 chips, using platform-device wrapping after manual Super I/O detection.

Important APIs, types, and functions: global `sch311x_wdt_data` stores runtime base, boot status, and I/O lock. Key routines are Super I/O enter/exit/read/write helpers, `sch311x_detect()`, `sch311x_wdt_set_timeout()`, start/stop/keepalive/status helpers, file operations, platform probe/remove/shutdown, module init, and exit.

Control flow: module init scans common Super I/O config ports, validates device ID or `force_id`, selects logical device 0x0a, reads runtime base, registers a platform driver and synthetic platform device. Probe reserves runtime register regions, stops hardware, disables keyboard/mouse interaction in WDT config, validates timeout, captures boot status, and registers `/dev/watchdog`. Open starts hardware by setting timeout and routing GP60 to WDT function. Keepalive rewrites timeout. Close stops only after magic `V`.

State and persistence behavior: state is runtime register base, boot status from WDT control bit, timeout rounded to seconds or minutes, open/expected-close flags, and Super I/O register configuration.

Dependencies and integration points: depends on port I/O, Super I/O configuration protocol, platform driver/device framework, miscdevice watchdog ABI, and shutdown callback.

Risks and edge cases: detection writes to Super I/O config ports and can be affected by `force_id`. Timeouts above 255 seconds round up to minutes. Remove stops only when nowayout is false, but shutdown always stops. No reboot notifier is used outside platform shutdown.

Test signals: detection on all config ports, forced ID, runtime base zero handling, timeout rounding up to minutes, bootstatus status bit, open/magic close, shutdown stop, and region cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sch311x_wdt.c -->
