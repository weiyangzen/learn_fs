# subset-b-005203 RTC driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.c

Purpose: RTC subsystem platform driver for StrongARM SA1100 and related PXA/MMP RTC blocks. It exposes a seconds counter, alarm compare register, 1 Hz/update interrupt, proc diagnostics, clock enable, wakeup, and two register layouts selected by architecture or DT compatible.

Important APIs/types/functions: `struct sa1100_rtc` comes from `rtc-sa1100.h`. `sa1100_rtc_interrupt()` handles both 1 Hz and alarm IRQs, clears RTSR status carefully, and reports `RTC_AF`/`RTC_UF`. `sa1100_rtc_read_time()` and `sa1100_rtc_set_time()` map the 32-bit `RCNR` seconds counter to `struct rtc_time`. `sa1100_rtc_read_alarm()`, `sa1100_rtc_set_alarm()`, and `sa1100_rtc_alarm_irq_enable()` operate on `RTAR` and `RTSR_ALE`. `sa1100_rtc_init()` is exported for reuse and performs clock setup, divider initialization, RTC registration, and initial interrupt-status clearing.

Control flow/state/persistence: probe obtains named IRQs, allocates the RTC, requests both IRQs, maps MMIO, assigns register offsets for SA1100 vs MMP/PXA layout, enables wakeup, then calls the shared init. The persistent hardware state is the counter, alarm, trim/divider, and status/enable bits. If `RTTR` is zero, the driver installs a default 32768 Hz divider and resets the counter to zero, explicitly treating old state as invalid.

Dependencies/integration: platform driver name `sa1100-rtc`, OF compatibles `mrvl,sa1100-rtc` and `mrvl,mmp-rtc`, clock framework, devm RTC registration, MMIO, named platform IRQs, and PM wake IRQ enable on alarm.

Risks/test signals: most risk is register-status semantics. The interrupt path has special handling for spurious `RTSR_HZ`/`RTSR_AL` states seen on SA11xx and clears disabled pending sources to avoid interrupt storms. Test with alarm firing, 1 Hz updates, suspend wake, both register layouts, zeroed trim register initialization, and removal disabling `RTSR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.h -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.h

Purpose: private header for the SA1100/PXA RTC implementation. It defines the per-device state passed between the platform-specific probe path and the exported common initializer.

Important APIs/types/functions: `struct sa1100_rtc` contains the spinlock, MMIO pointers for counter/alarm/status/trim registers, 1 Hz and alarm IRQ numbers, `struct rtc_device *`, and `struct clk *`. The single function declaration is `sa1100_rtc_init(struct platform_device *pdev, struct sa1100_rtc *info)`.

Control flow/state/persistence: the header has no executable flow, but its struct defines all mutable state used by `rtc-sa1100.c`. Register pointer fields are initialized after MMIO mapping and before shared initialization; `lock` protects RTSR writes; the clock pointer is prepared/enabled by init and disabled by remove.

Dependencies/integration: includes `linux/kernel.h` for kernel types, forward-declares `struct clk` and `struct platform_device`, and is included by the local driver. It is not a user ABI.

Risks/test signals: changes to this header affect both the standalone driver and any user of the exported init symbol. Validate struct field initialization ordering, lock use around RTSR paths, and compile coverage when `sa1100_rtc_init()` is referenced externally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sc27xx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sc27xx.c

Purpose: RTC driver for Spreadtrum/Unisoc SC27xx PMIC RTC blocks. It supports current time, normal alarm, auxiliary alarm, power-down validity detection, and power-off alarm persistence through PMIC regmap registers.

Important APIs/types/functions: `struct sprd_rtc` stores the RTC device, parent regmap, register base, IRQ, and validity flag. `sprd_rtc_get_secs()` and `sprd_rtc_set_secs()` convert split sec/min/hour/day registers to seconds for time, normal alarm, and auxiliary alarm register groups. `sprd_rtc_lock_alarm()` updates SPG alarm lock bits and power-off alarm flag. `sprd_rtc_set_alarm()` chooses normal alarm for the RTC core AIE timer and auxiliary alarm for wake-only alarms. `sprd_rtc_check_power_down()` sets `valid`, and `sprd_rtc_check_alarm_int()` restores alarm enable when SPG indicates a previous power-off alarm.

Control flow/state/persistence: probe gets the parent regmap, DT `reg` base, IRQ, allocates RTC, restores alarm interrupt state, checks power-status validity, requests a threaded IRQ, enables wakeup, sets range 0..5662310399 seconds, and registers. Hardware stores time and normal/SPG registers in always-on VDDRTC regions, while `INT_EN` does not persist across full power down; the driver uses SPG flags to bridge that.

Dependencies/integration: platform driver `sprd-rtc`, compatible `sprd,sc2731-rtc`, parent MFD regmap, RTC core, threaded IRQ with `IRQF_ONESHOT | IRQF_EARLY_RESUME`, DT base offset, and wakeup integration.

Risks/test signals: register writes require polling up to 200 ms because always-on register updates are slow. Alarm mode selection depends on comparing requested alarm with `rtc->aie_timer.node.expires`; regressions can break power-on alarm vs deep-sleep wake behavior. Test invalid power status, set-time validity transition, normal and auxiliary alarms, alarm lock/unlock, power-cycle persistence, and timeout/error propagation from regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sc27xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd2405al.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd2405al.c

Purpose: I2C/regmap RTC driver for the DFRobot SD2405AL chip. It implements time read/write only, using BCD-encoded hardware registers and a protected write-enable sequence.

Important APIs/types/functions: `struct sd2405al` stores `dev` and `regmap`. `sd2405al_enable_reg_write()` and `sd2405al_disable_reg_write()` perform the ordered `WRTC1/WRTC2/WRTC3` control-bit sequence. `sd2405al_read_time()` bulk reads time registers and handles both 24-hour and 12-hour PM formats. `sd2405al_set_time()` writes BCD data in 24-hour mode, clears the time-trim flag register, then disables writes. `sd2405al_probe()` checks I2C functionality, creates an 8-bit regmap, allocates and registers the RTC with a 2000..2099 range.

Control flow/state/persistence: probe is simple and does not initialize the chip time. Runtime state is in battery-backed chip registers and control write-enable bits. `set_time` temporarily opens write access and should normally leave writes disabled.

Dependencies/integration: I2C core, regmap I2C, RTC core, BCD helpers, compatible `dfrobot,sd2405al`, I2C ID `sd2405al`, address documented as 0x32.

Risks/test signals: the error path in `sd2405al_set_time()` can return before disabling register writes if the bulk write or flag clear fails. Tests should cover 12-hour PM conversion, month/year offsets, write-enable ordering, failed-regmap cleanup behavior, and range boundaries 2000/2099.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd2405al.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd3078.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd3078.c

Purpose: I2C RTC driver for the SD3078. It provides read/set time using BCD time registers and optional write-protection support compiled out by default.

Important APIs/types/functions: `sd3078_enable_reg_write()` writes key bits in the documented order. `sd3078_disable_reg_write()` is present under `WRITE_PROTECT_EN`. `sd3078_rtc_read_time()` bulk reads seven time registers and converts 12-hour/24-hour modes into Linux `rtc_time`. `sd3078_rtc_set_time()` bulk writes BCD time in 24-hour mode. `sd3078_probe()` initializes the 8-bit regmap, allocates RTC, sets range 2000..2099, registers it, then enables register writes.

Control flow/state/persistence: after probe, the driver leaves register writes enabled because `WRITE_PROTECT_EN` is `0` and `sd3078_enable_reg_write()` is called after registration. Time state persists in chip registers; there is no alarm, nvmem, or oscillator-validity handling.

Dependencies/integration: I2C core, regmap, BCD helpers, RTC core, OF compatible `whwave,sd3078`, I2C ID `sd3078`.

Risks/test signals: all write-key operations ignore regmap return values, so bus failures in protection setup can be silent. Time conversion mutates no caller-owned fields except in normal RTC ops. Test 12-hour PM/AM reads, 24-hour writes, write protection build option, month/year rebasing, and I2C/regmap failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd3078.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sh.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sh.c

Purpose: SuperH and Renesas RZ/A on-chip RTC platform driver. It handles BCD calendar registers, carry-safe reads, optional 4-digit year support, alarm match registers, clock enable, wakeup, and OF/non-OF resource variants.

Important APIs/types/functions: `struct sh_rtc` holds MMIO, alarm IRQ, clock, `rtc_device`, lock, and capability flags. `sh_rtc_read_time()` clears/uses the carry flag and 128 Hz counter to read a stable time. `sh_rtc_set_time()` stops/resets the prescaler, writes BCD fields, then restarts RTC. Alarm helpers encode ignored fields as disabled alarm register bytes using `AR_ENB`. `sh_rtc_alarm()` clears `RCR1_AF` and disables AIE before calling `rtc_update_irq()`. Probe maps IO/MEM resources, gets clock names (`rtcN` or `fck`), loads platform capability flags, disables interrupts, sets date range, and registers.

Control flow/state/persistence: hardware stores BCD calendar and alarm registers. Reads loop until no carry and no inverted-bit rollover. Remove disables alarms and clock. PM toggles IRQ wake if wakeup is allowed.

Dependencies/integration: platform driver `sh-rtc`, compatible `renesas,sh-rtc`, optional `CONFIG_SUPERH` platform data, clock framework, IO or MEM resources, RTC core, IRQ wake.

Risks/test signals: year handling differs between 2-digit and 4-digit hardware, with fallback century logic for old parts. The RYRAR/RCR3 year-alarm support is intentionally absent. Test carry/rollover read stability, alarm ignored fields, 4-digit vs 2-digit ranges, clock absence tolerance, OF and legacy IRQ numbering, and suspend wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-snvs.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-snvs.c

Purpose: Freescale/NXP SNVS low-power secure RTC driver. It provides a seconds counter, one-shot low-power timer alarm, wake IRQ support, and syscon or legacy MMIO regmap access.

Important APIs/types/functions: `struct snvs_rtc_data` stores RTC device, regmap, LP offset, IRQ, and optional clock. `rtc_read_lpsrt()` reads the 64-bit counter registers; `rtc_read_lp_counter()` and `_lsb()` retry until counter deltas are plausible. `rtc_write_sync_lp()` waits for several 32 kHz cycles after writes. `snvs_rtc_enable()` toggles `SRTC_ENV`. RTC ops read/set time by converting the 47-bit counter shifted by 15 fractional bits, manage `SNVS_LPTAR`, and enable alarm/wakeup bits. The IRQ handler clears alarm status, disables the one-shot alarm, and reports `RTC_AF`.

Control flow/state/persistence: probe allocates RTC, obtains regmap from DT `regmap` phandle or legacy MMIO, initializes glitch detect, clears status, enables the RTC, sets wake IRQ, requests a shared IRQ, and registers. Time persists in SNVS LP domain when powered.

Dependencies/integration: OF compatible `fsl,sec-v4.0-mon-rtc-lp`, syscon/regmap, optional `snvs-rtc` clock, PM wakeirq helpers, MMIO fallback, RTC core.

Risks/test signals: several error paths after `clk_enable()` in set-time/set-alarm can return without disabling the clock. Counter-read validity is heuristic and timeout based. Test syscon and legacy bindings, stable counter reads around rollover, alarm one-shot behavior, wake IRQ setup, suspend noirq clock gating, and error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-snvs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-spacemit-p1.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-spacemit-p1.c

Purpose: RTC driver for the SpacemiT P1 PMIC. It exposes time read/write only over the parent PMIC regmap and explicitly disables alarm/update interrupt RTC features.

Important APIs/types/functions: `struct p1_rtc` stores regmap and RTC device. `p1_rtc_read_time()` checks `RTC_EN`, then reads the six-byte time block until two successive second values match, working around unstable hardware latching. `p1_rtc_set_time()` disables the RTC, writes six raw fields, and re-enables it. Probe gets the parent regmap, allocates/registers RTC, sets range 2000..2063, and clears alarm/update features.

Control flow/state/persistence: time registers store seconds, minutes, hours, zero-based day-of-month, zero-based month, and year since 2000. Set-time leaves RTC disabled if the bulk write fails, matching the comment that partially updated time should not run.

Dependencies/integration: platform MFD child named `spacemit-p1-rtc`, parent regmap, RTC core, module alias `platform:spacemit-p1-rtc`.

Risks/test signals: comments say hours are documented as 0-59 but the driver masks them with 5 bits, so hardware documentation and runtime validation should be checked. Read stability relies only on identical seconds, not whole-buffer equality. Test disabled RTC reads, unstable second rollover loops, day/month conversions, 2063 boundary, failed writes leaving RTC disabled, and feature bits exposed to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-spacemit-p1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-spear.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-spear.c

Purpose: ST SPEAr platform RTC driver with BCD date/time registers, full alarm date/time registers, interrupt control, clock management, and suspend wake support.

Important APIs/types/functions: `struct spear_rtc_config` holds RTC device, clock, spinlock, MMIO, and IRQ wake state. Helpers clear/enable/disable alarm interrupt, poll busy bits, and check lost write status. `spear_rtc_read_time()` waits not busy, reads time/date and converts BCD. `spear_rtc_set_time()` writes packed BCD time/date and checks write completion. Alarm ops mirror this for alarm registers. `spear_rtc_irq()` clears status and reports `RTC_AF`.

Control flow/state/persistence: probe requests the alarm IRQ, maps MMIO, enables the clock, initializes lock and RTC range 0..9999, registers, and enables wake capability. Suspend either enables IRQ wake or disables interrupt/clock; resume reverses that. Shutdown disables interrupt and clock.

Dependencies/integration: platform driver `rtc-spear`, compatible `st,spear600-rtc`, clock framework, MMIO, RTC core, IRQ wake.

Risks/test signals: `spear_rtc_read_time()` loops while the first time read equals a second time read, which is unusual and can be sensitive to hardware behavior. `tm2bcd()` mutates the caller-provided `rtc_time`, so callers must not reuse fields after set ops. Test busy/lost-write handling, BCD packing for years, alarm enable/disable, suspend non-wakeup clock restore, and interrupt status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-spear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ssd202d.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ssd202d.c

Purpose: MMIO RTC driver for MStar/SigmaStar SSD202D SoCs. It reads and writes a base seconds value plus running counter through an isolation-control handshake.

Important APIs/types/functions: `struct ssd202d_rtc` stores RTC device and base MMIO. `ssd202d_rtc_isoctrl()` writes a fixed sequence to `REG_ISO_CTRL` and polls acknowledgement plus `iso_en`. `ssd202d_rtc_read_reg()` and `_write_reg()` transfer values through read/write data registers while gating isolation. `ssd202d_rtc_read_counter()` latches the running counter. RTC ops check SW enable, combine base and counter for read, and write base/reset counter/enable SW0 for set-time.

Control flow/state/persistence: probe maps MMIO, allocates/registers RTC, and sets a 32-bit range. The driver does not initialize time; `set_time` updates the base, resets counter, and marks SW0 enabled.

Dependencies/integration: compatible `mstar,ssd202d-rtc`, platform MMIO, polling helpers, RTC core. No clock or IRQ integration.

Risks/test signals: `ssd202d_rtc_isoctrl()` returns 0 even if the final `iso_en` poll fails after logging, and most callers ignore errors because read/write helpers are `void`. Test iso handshake timeouts, SW0 disabled reads, base+counter rollover, reset sequencing, and failure injection for delayed/absent acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ssd202d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-st-lpc.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-st-lpc.c

Purpose: RTC mode driver for ST LPC low-power timer hardware. It uses a 64-bit free-running low-power timer as current time and a low-power alarm timer for wake alarm support.

Important APIs/types/functions: `struct st_rtc` holds RTC device, cached alarm, clock/rate, MMIO, IRQ state, lock, and IRQ. `st_rtc_read_time()` reads MSB/LSB consistently and divides ticks by clock rate. `st_rtc_set_time()` writes tick count and starts the timer. `st_rtc_set_hw_alarm()` programs the low-power alarm through WDT gating. Alarm ops cache `rtc_wkalrm`, compute relative delta from current time, and enable/disable an IRQ requested with `IRQF_NO_AUTOEN`. PM suspend/resume clears or restarts alarm hardware depending on wakeup.

Control flow/state/persistence: probe requires DT `st,lpc-mode == ST_LPC_MODE_RTC`, maps MMIO, maps IRQ, requests clock, sets wake capability, computes range from `U64_MAX / clkrate`, and registers. Current time persists as hardware counter ticks; alarm state is partly cached in RAM.

Dependencies/integration: compatible `st,stih407-lpc`, `dt-bindings/mfd/st-lpc.h`, platform MMIO, `irq_of_parse_and_map()`, clock framework, RTC core.

Risks/test signals: alarm programming subtracts current seconds without checking for alarms in the past, causing unsigned underflow. IRQ handler reports `RTC_AF` without `RTC_IRQF`. Cached alarm state is lost across driver reload and cleared on resume. Test mode rejection, clock-rate zero, relative alarm math, wake/non-wake suspend paths, IRQ enable state transitions, and range calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-st-lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-starfire.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-starfire.c

Purpose: built-in Starfire platform RTC reader for SPARC systems using OpenBoot PROM calls. It exposes read-time only.

Important APIs/types/functions: `starfire_get_time()` builds an OBP Forth command string pointing at a static `unix_tod`, calls `prom_feval()`, and returns the resulting Unix seconds. `starfire_read_time()` converts seconds to `rtc_time`. `starfire_rtc_probe()` allocates/registers an RTC with `range_max = U32_MAX`.

Control flow/state/persistence: the driver is registered by `builtin_platform_driver_probe()`, so it probes once and cannot be unbound like a normal module. State is owned by firmware; the Linux driver has no set-time, alarm, or persistent software state.

Dependencies/integration: SPARC `asm/oplib.h`, platform device name `rtc-starfire`, RTC core. It is firmware-dependent and has no OF table in this file.

Risks/test signals: static command/time buffers are not synchronized, though normal RTC core access is serialized enough for typical use. Firmware failures are not reported; zero time would be returned. Test on Starfire firmware, confirm year-2038/2106 behavior from U32 range, and ensure absence of set/alarm features is accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-starfire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-stk17ta8.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-stk17ta8.c

Purpose: platform RTC and NVRAM driver for Simtek STK17TA8 battery-backed SRAM/RTC. It supports BCD time, alarm interrupts, voltage-low warning, oscillator start, and nvmem access to the SRAM window before the RTC register block.

Important APIs/types/functions: `struct rtc_plat_data` stores RTC, MMIO, last read jiffies, IRQ, alarm masks, cached alarm fields, and lock. Time ops use `RTC_READ`/`RTC_WRITE` flags around register access and include a century register. `stk17ta8_rtc_update_alarm()` writes alarm fields, using `0x80` as wildcard or update interrupt encoding. The IRQ handler distinguishes alarm vs update events by checking `RTC_SECONDS_ALARM`. NVMEM callbacks read/write byte ranges directly.

Control flow/state/persistence: probe maps the whole device, starts the RTC if `RTC_STOP` is set, warns on power-fail, requests shared IRQ if available, allocates RTC, registers battery-backed nvmem, and registers RTC. Alarm settings are cached in RAM but programmed into hardware on updates.

Dependencies/integration: platform name `stk17ta8`, MMIO, shared IRQ, BCD helpers, RTC core, `devm_rtc_nvmem_register()`.

Risks/test signals: if no IRQ is available alarm ops return `-EINVAL`. Read path sleeps 1 ms when called in the same jiffy to avoid continuous-read update issues. Test oscillator-stop recovery, voltage-low reporting, century conversion, wildcard alarm fields, update-vs-alarm interrupt reporting, nvmem boundaries, and IRQ absent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-stk17ta8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-stm32.c

Purpose: full STM32 RTC platform driver covering multiple STM32, STM32H7, STM32MP1, and STM32MP25 register layouts. It provides calendar time, Alarm A, prescaler programming, backup-domain unlock, optional resource isolation checks, LSCO/alarm output pinmux, wake IRQ, and PM clock handling.

Important APIs/types/functions: `struct stm32_rtc_data` describes register offsets, event bits, clear-event method, clock/DBP/RIF/pin capabilities. `struct stm32_rtc` stores mapped registers, syscfg DBP regmap, clocks, IRQ, and optional LSCO gate. `stm32_rtc_enter_init_mode()`, `stm32_rtc_exit_init_mode()`, and `stm32_rtc_wait_sync()` guard calendar writes and synchronization. Time and alarm ops convert BCD fields, with `stm32_rtc_valid_alrm()` limiting alarms to the current day-of-month through the same day next month. Pinmux actions program Alarm A output or register an LSCO clock. `stm32_rtc_init()` computes asynchronous/synchronous prescalers from `rtc_ck` and forces 24-hour mode.

Control flow/state/persistence: probe maps MMIO, loads match data, optionally obtains backup-domain protection syscfg fields, enables pclk/rtc_ck, unlocks backup domain, checks RIF on MP25, initializes prescalers, sets wake IRQ, registers RTC, requests threaded alarm IRQ, cleans output configuration, registers/enables pinctrl, warns if calendar not initialized, and logs version. Remove disables alarm IRQ, clocks, LSCO, and DBP as needed.

Dependencies/integration: OF compatibles `st,stm32-rtc`, `st,stm32h7-rtc`, `st,stm32mp1-rtc`, `st,stm32mp25-rtc`; syscon regmap for backup-domain protection; clock, pinctrl/pinmux, PM wakeirq, MMIO, RTC core, and RIF security registers.

Risks/test signals: the driver mutates `rtc_time` during BCD conversion, depends on exact prescaler math, and has variant-specific event clearing (`ISR` write-0 vs `SCR` write-1). Alarm hardware lacks month/year matching. Test every compatible layout, DBP enable/disable, RIF denied access, non-32768 LSCO rejection, alarm range rejection, pending flag clearing, suspend/resume sync, prescaler warning path, and pinmux conflicts between calibration, tamp/alarm, and LSCO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-stmp3xxx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-stmp3xxx.c

Purpose: Freescale/Sigmatel STMP37xx/STMP378x/i.MX28 RTC driver. It provides seconds counter, alarm, persistent oscillator configuration, optional child watchdog registration, and suspend/resume reset handling.

Important APIs/types/functions: `struct stmp3xxx_rtc_data` stores RTC device, MMIO, and alarm IRQ. `stmp3xxx_wait_time()` polls stale bits before reading/writing seconds. `stmp3xxx_rtc_gettime()` and `_settime()` access `STMP3XXX_RTC_SECONDS`. Alarm ops use `STMP3XXX_RTC_ALARM` plus persistent alarm wake/enable bits. Optional `stmp3xxx_wdt_set_timeout()` exposes watchdog control through child platform data.

Control flow/state/persistence: probe maps MMIO, verifies RTC presence, avoids block reset if watchdog is running, detects or reads DT override for 32 kHz crystal frequency, configures persistent oscillator and alarm bits, disables IRQs, allocates/registers RTC, requests alarm IRQ, then registers the watchdog child if enabled. Persistent registers survive low-power states and control wake and clock source.

Dependencies/integration: compatible `fsl,stmp3xxx-rtc`, STMP register set/clear offsets, optional `CONFIG_STMP3XXX_RTC_WATCHDOG`, DT `stmp,crystal-freq`, RTC core, platform IRQ.

Risks/test signals: resetting the block can stop a running watchdog, so the skip path is critical. Crystal fuse values can be unreliable, hence DT override. Test stale-bit timeout, 32000/32768/no-crystal modes, alarm wake bits, watchdog-enabled probe, resume reset clearing alarm wake, and invalid crystal warning path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-stmp3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun4v.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun4v.c

Purpose: SUN4V hypervisor-backed RTC driver for SPARC logical domains. It implements read and set time through hypervisor TOD calls.

Important APIs/types/functions: `hypervisor_get_time()` calls `sun4v_tod_get()` with retry handling for `HV_EWOULDBLOCK`. `hypervisor_set_time()` calls `sun4v_tod_set()` with the same retry policy and returns Linux errors for timeout or unsupported calls. RTC ops convert between `rtc_time` and seconds. Probe allocates/registers an RTC with `range_max = U64_MAX`.

Control flow/state/persistence: the driver is built in with `builtin_platform_driver_probe()`. No MMIO or software persistent state is maintained; the hypervisor owns the time source.

Dependencies/integration: SPARC `asm/hypervisor.h`, platform name `rtc-sun4v`, RTC core, microsecond delays for hypervisor busy retry.

Risks/test signals: read failures return zero time after warning rather than an error. Set can return `-EAGAIN` or `-EOPNOTSUPP`. Test hypervisor busy retry paths, unsupported TOD services, permission behavior for setting time, and U64 range handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun4v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun6i.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun6i.c

Purpose: Allwinner A31/A23 and later RTC driver with integrated low-speed oscillator clock provider, RTC calendar, counter or absolute alarms, battery-backed GP data nvmem, and wakeup support.

Important APIs/types/functions: `struct sun6i_rtc_clk_data` captures SoC oscillator capabilities; `struct sun6i_rtc_dev` stores RTC, clock-provider state, MMIO, alarm, flags, and lock. `sun6i_rtc_clk_init()` maps RTC early and registers internal oscillator, muxed LOSC, and external gate clocks. RTC ops read stable date/time snapshots, encode either YMD fields or `RTC_LINEAR_DAY`, set alarms as relative seconds or absolute day/HMS, poll access bits with `sun6i_rtc_wait()`, and expose GP data through nvmem callbacks.

Control flow/state/persistence: early `CLK_OF_DECLARE_DRIVER` setup may allocate the singleton `sun6i_rtc` before platform probe. Probe optionally enables a bus clock, maps MMIO if early init did not, requests IRQ, clears and disables alarm sources, enables LOSC, allocates RTC, sets range based on linear-day flag, registers RTC, then registers nvmem. Alarm time is cached in `chip->alarm`.

Dependencies/integration: compatibles for A31/A23/H3/R40/V3/H5/H6/H616/R329, clk provider framework, optional CCU probe, platform MMIO/IRQ, wakeup, RTC core, nvmem.

Risks/test signals: singleton early clock state couples clock provider and platform probe lifetime. Non-linear date range is limited to 2033; newer linear-day chips use 65536 days. Alarm enable only disables in `.alarm_irq_enable`; normal enabling is done in `.set_alarm`. Test early clock registration, internal/external LOSC parent changes, access-bit timeouts, linear and non-linear time encoding, nvmem word alignment, alarm wake, and suspend IRQ wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun6i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunplus.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunplus.c

Purpose: RTC driver for Sunplus SP7021. It exposes a 32-bit seconds counter, absolute alarm register, alarm IRQ, reset/clock management, wakeup, and optional trickle charger configuration from DT.

Important APIs/types/functions: `struct sunplus_rtc` stores RTC, resource pointer, clock, reset, MMIO, and IRQ. `sp_get_seconds()`/`sp_set_seconds()` access timer registers. RTC ops convert seconds to/from `rtc_time`, read/write alarm seconds, and control alarm bits in `RTC_CTRL`. `sp_rtc_set_trickle_charger()` parses `trickle-resistor-ohms` and `aux-voltage-chargeable` to program battery charger resistance/diode/enable bits.

Control flow/state/persistence: probe maps named `rtc` resource, requests rising-edge IRQ, enables clock, deasserts reset, marks wakeup, allocates/registers RTC with U32 range, configures trickle charger if DT properties exist, and sets `DIS_SYS_RST_RTC` to preserve RTC through system reset. Remove disables wakeup, asserts reset, and disables clock.

Dependencies/integration: compatible `sunplus,sp7021-rtc`, platform named resource, clock/reset frameworks, DT properties for charger, RTC core, IRQ wake PM.

Risks/test signals: `struct resource *res` is logged but never assigned. Alarm read treats `RTC_ALARM_SET == 0` as disabled, so a legitimate epoch alarm cannot be represented. Test clock/reset error unwinds, trickle charger valid/invalid values, alarm enable bitmask writes, wake IRQ suspend/resume, and U32 rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunxi.c

Purpose: older Allwinner A10/A20 RTC driver. It handles YMD/HMS calendar registers, relative counter alarm, limited year ranges, and alarm IRQs.

Important APIs/types/functions: `struct sunxi_rtc_data_year` defines min/max year, year bitmask, and leap-year bit shift per compatible. `struct sunxi_rtc_dev` stores RTC, device, data-year pointer, MMIO, and IRQ. `sunxi_rtc_gettime()` reads stable YMD/HMS values and rebases year to Linux. `sunxi_rtc_settime()` validates year, writes time/date, and polls access bits. `sunxi_rtc_setalarm()` computes a relative day/hour/min/sec gap from current time, bounds it to 255 days, writes `SUNXI_ALRM_DHMS`, and enables alarm IRQ. IRQ handler clears pending status and reports `RTC_AF`.

Control flow/state/persistence: probe allocates, maps MMIO, requests IRQ, loads match data for A10 or A20 year format, clears/disables alarm registers, assigns RTC ops, and registers.

Dependencies/integration: compatibles `allwinner,sun4i-a10-rtc` and `allwinner,sun7i-a20-rtc`, platform MMIO/IRQ, RTC core, delay/poll helpers.

Risks/test signals: `.alarm_irq_enable()` only disables; enabling is done through `.set_alarm`. `sunxi_rtc_wait()` considers success when masked bits equal mask, unlike sun6i's wait-for-clear, so hardware semantics must be preserved. Test both year parameter sets, leap bit placement, past/far alarms, access polling, relative alarm encoding, and read stability around rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-tegra.c

Purpose: NVIDIA Tegra internal RTC driver for Tegra 200 series and ACPI-exposed variants. It supports seconds time, alarm0, interrupt masking/status, proc info, clock setup for DT systems, wakeup, and PM alarm wake.

Important APIs/types/functions: `struct tegra_rtc_info` holds platform device, RTC, MMIO, optional clock, IRQ, and lock. `tegra_rtc_wait_while_busy()` waits for the hardware copy/update window so writes have a safe period. `tegra_rtc_read_time()` reads milliseconds first to latch shadow seconds. Alarm ops use `SECONDS_ALARM0` and mask bit `SEC_ALARM0`. IRQ handler clears all masks/status on any IRQ and reports alarm or periodic events.

Control flow/state/persistence: probe maps MMIO, gets IRQ, allocates RTC, enables optional DT clock, clears alarm/status/mask registers, enables wakeup, requests high-trigger IRQ, registers RTC, and logs. Suspend clears status, enables only alarm0 mask for wake, and calls `enable_irq_wake()` when appropriate; shutdown disables alarm IRQ.

Dependencies/integration: OF compatible `nvidia,tegra20-rtc`, ACPI ID `NVDA0280`, platform MMIO/IRQ, optional clock, RTC core, seq proc callback, PM wake.

Risks/test signals: `tegra_rtc_wait_while_busy()` comments say wait for busy then not busy, but implementation only waits while currently busy; timing assumptions need hardware validation. Set-alarm ignores wait return values. Test shadow read correctness, write windows, alarm disable-on-IRQ, suspend wake mask, ACPI and OF probe paths, and U32 time range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-test.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-test.c

Purpose: software-only RTC test driver that creates three platform RTC devices for exercising RTC core behavior without hardware.

Important APIs/types/functions: `struct rtc_test_data` stores RTC, time offset, kernel timer alarm, and alarm enable flag. Time ops map RTC time to `ktime_get_real_seconds() + offset`; set-time updates offset. Alarm ops compute timer expiration from requested wall time minus offset, clamp jiffies expiration to `U32_MAX`, and use a `timer_list` callback to report `RTC_AF`. Device id 0 uses ops without read/set alarm; ids 1 and 2 include alarm ops and wakeup capability.

Control flow/state/persistence: module init registers the platform driver, allocates three platform devices, and adds them. Probe allocates private state, allocates RTC, selects ops based on id, initializes timer, and registers. Exit unregisters devices and driver. State is in RAM only and disappears on module unload.

Dependencies/integration: platform device/driver core, RTC core, kernel timers, jiffies, module init/exit.

Risks/test signals: alarm enable can add a timer even if no valid expiration has been programmed, and negative timeouts convert through unsigned arithmetic. This is a test fixture, so expected behavior should be documented in tests. Test three-device creation, no-alarm feature exposure on id 0, offset math, timer callback IRQ delivery, module unload cleanup, and alarm times in the past/far future.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ti-k3.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ti-k3.c

Purpose: Texas Instruments K3/AM62 RTC driver. It supports 48-bit seconds, alarm, offset calibration, scratch-register nvmem, unlock/synchronization fences across clock domains, erratum i2327 handling, wakeup, and low-power resume reconfiguration.

Important APIs/types/functions: `struct ti_k3_rtc` stores IRQ, sync timeout, 32 kHz rate, RTC device, regmap, and regmap fields. `k3rtc_field_read/write()`, `k3rtc_fence()`, and `k3rtc_unlock_rtc()` abstract register field access and 32 kHz domain synchronization. `k3rtc_configure()` enforces erratum requirements, enables oscillator-dependent sync, sets counter freeze mode, clears/disables IRQs, and fences. RTC ops read/write 48-bit time, alarm compare, alarm IRQ enable, and ppb offset through compensation register math. `ti_k3_rtc_interrupt()` handles delayed status clear/reload sequencing for 32 kHz-domain IRQ deassertion. NVMEM callbacks expose scratch registers.

Control flow/state/persistence: probe maps MMIO regmap, allocates fields, enables `osc32k` and `vbus` clocks, gets IRQ, allocates RTC with 48-bit range, requests threaded IRQ, configures hardware, marks wakeup capable/source, registers RTC, then registers nvmem. Resume reconfigures if RTC is locked, indicating low-power context loss.

Dependencies/integration: compatible `ti,am62-rtc`, regmap MMIO/fields, `sys_soc` erratum match, clocks `osc32k` and `vbus`, threaded IRQ, RTC core offset API, nvmem, PM wake.

Risks/test signals: AM62X SR1.0 requires bootloader unlock; Linux refuses operation if locked. Field operations cannot be used for some writes due to freeze/race behavior. Test erratum matched/unmatched paths, non-32768 clock warning and timeout calculation, fence timeouts, IRQ status clear/reload sequence, offset min/max conversion, scratch nvmem alignment, and resume after context loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ti-k3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6586x.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6586x.c

Purpose: RTC driver for TI TPS6586x PMICs. It exposes a 1 kHz tick counter as seconds, one alarm with a 14-bit seconds-ahead range, wake IRQ support, and PMIC register configuration through the parent MFD API.

Important APIs/types/functions: `struct tps6586x_rtc` stores device, RTC, IRQ, and software IRQ enable state. Time ops read a dummy-prefixed multi-byte counter and shift ticks by 10 to seconds; set-time disables RTC, writes shifted ticks, and re-enables it. Alarm ops enable/disable the IRQ line manually, read current counter, clamp alarms beyond `ALM1_VALID_RANGE_IN_SEC` by programming a past time, and write three alarm bytes. Probe starts the counter in 1 kHz mode, configures start time metadata, requests a no-auto-enable threaded IRQ, and registers.

Control flow/state/persistence: probe enables the PMIC counter and wakeup, then RTC core state maps hardware seconds to a configured start date of 2009-01-01. Remove disables RTC control bits. Suspend/resume toggles IRQ wake if enabled.

Dependencies/integration: TPS6586x MFD functions (`tps6586x_reads/writes/update/set_bits/clr_bits`), platform driver `tps6586x-rtc`, RTC core, IRQ core, PM wake.

Risks/test signals: `platform_get_irq()` result is not checked before `irq_set_status_flags()`. Out-of-range future alarms are silently converted to a past alarm rather than returning an error. Failed time write can leave RTC disabled. Test IRQ absence, counter read byte order, alarm range clamping, manual IRQ enable state, start-time mapping, and remove/error cleanup disabling the counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6586x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps65910.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps65910.c

Purpose: RTC driver for TI TPS65910 PMICs. It supports BCD time/alarm registers, alarm IRQ, RTC digital power enable, 2000..2099 range, and crystal compensation exposed through the RTC offset API.

Important APIs/types/functions: `struct tps65910_rtc` stores RTC and IRQ. `tps65910_rtc_read_time()` latches counting registers with `GET_TIME` then bulk reads BCD fields. `tps65910_rtc_set_time()` stops RTC, writes BCD registers, and restarts. Alarm ops bulk read/write alarm BCD registers and control `TPS65910_RTC_INTERRUPTS_IT_ALARM`. Calibration helpers write/read two compensation bytes and convert to/from ppb with sign inversion. The IRQ handler reads status, detects alarm, writes status back to clear, and reports `RTC_AF`.

Control flow/state/persistence: probe clears pending status, powers the RTC domain, writes control to start/enable RTC, requests threaded low-trigger IRQ if possible, marks wakeup or clears alarm feature if IRQ unavailable, sets range, and registers. PM toggles IRQ wake.

Dependencies/integration: TPS65910 MFD/regmap, platform driver `tps65910-rtc`, property `wakeup-source` on parent, RTC core, BCD/math64 helpers, IRQ core.

Risks/test signals: if IRQ request fails, probe continues without alarms but still leaves alarm ops in `rtc_class_ops` while clearing the alarm feature. IRQ handler calls `rtc_update_irq()` even when `events` is zero after a non-alarm status. Test BCD month/year conversion, stop/start sequencing failure, compensation min/max and rounding, IRQ unavailable feature behavior, wakeup-source handling, and status-clear semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps65910.c -->
