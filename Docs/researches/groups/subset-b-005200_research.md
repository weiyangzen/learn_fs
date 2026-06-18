# subset-b-005200 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-moxart.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-moxart.c

Purpose: implements the MOXA ART RTC as a GPIO bit-banged serial device. It exposes only RTC read/set time operations and manually drives `rtc-data`, `rtc-sclk`, and `rtc-reset` GPIO lines to access BCD calendar registers.

Important APIs/types/functions: `struct moxart_rtc` stores the `rtc_device`, a spinlock, and three GPIO descriptors. `moxart_rtc_write_byte()` and `moxart_rtc_read_byte()` implement LSB-first serial transfer with microsecond delays. `moxart_rtc_read_register()` and `moxart_rtc_write_register()` wrap the reset pulse, data-line direction changes, command byte, and local IRQ masking. `moxart_rtc_read_time()` decodes BCD date/time fields; `moxart_rtc_set_time()` writes all calendar fields after disabling write protection.

Control flow: probe allocates private state, gets the three named GPIOs, initializes the spinlock, stores driver data, and registers the RTC class device. Runtime reads take `rtc_lock`, read seconds through year plus weekday, decode 12/24-hour mode and BCD digits, derive yday using a static month offset table, then release the lock. Runtime writes take the same lock, clear `GPIO_RTC_PROTECT_W`, write BCD year/month/day/hour/min/sec registers, then re-enable protection.

State and persistence: persistent state is entirely in the external RTC registers, especially BCD time/date fields and the write-protect bit. Driver state is limited to GPIO descriptors and locking; no alarm, wakeup, NVMEM, or remove-time restoration exists.

Dependencies and integration: depends on gpiolib descriptor APIs, platform/OF compatible `moxa,moxart-rtc`, the RTC class, and board-provided GPIO names. It does not use an IRQ and does not advertise alarm support.

Risks and test signals: register access disables local IRQs while bit-banging GPIOs and doing `udelay()`, so slow GPIO backends could hurt latency. `spin_lock_irq()` is combined with helper-level `local_irq_save()`, which is redundant but protects against concurrent RTC ops. The leap-year yday calculation is simplified and the `tm_year <= 69` branch is unreachable after adding 100. Test valid/invalid GPIO descriptors, read/write protection sequencing, 12-hour PM/noon/midnight decoding, BCD conversions, month/yday boundary cases including leap years, and that concurrent read/set operations do not interleave GPIO transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-moxart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpc5121.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpc5121.c

Purpose: supports Freescale MPC5121 and MPC5200 memory-mapped RTC blocks. MPC5121 exposes a read-only uptime counter plus writable offset, while MPC5200 uses direct calendar registers; both share minute-resolution alarm handling.

Important APIs/types/functions: `struct mpc5121_rtc_regs` maps the byte/word register layout, and `struct mpc5121_rtc_data` stores IRQs, register base, RTC device, and cached `rtc_wkalrm`. `mpc5121_rtc_update_smh()` updates second/minute/hour set registers using the hardware sequence required for alarms. Time callbacks split into `mpc5121_rtc_read_time()`/`set_time()` and `mpc5200_rtc_read_time()`/`set_time()`. Alarm and IRQ callbacks are shared: `mpc5121_rtc_read_alarm()`, `mpc5121_rtc_set_alarm()`, `mpc5121_rtc_alarm_irq_enable()`, `mpc5121_rtc_handler()`, and `mpc5121_rtc_handler_upd()`.

Control flow: probe maps registers, marks the platform device wake-capable, parses two OF IRQs, requests alarm and update handlers, allocates the RTC, selects MPC5200 ops by default, then switches to MPC5121 ops and U32 range when compatible is `fsl,mpc5121-rtc`. MPC5121 reads Linux time as `actual_time + target_time`; set-time writes the offset into `target_time`. MPC5200 reads/writes calendar date fields directly. Alarm setup only programs hour and minute, sets mday/month/year to `-1` in the cached alarm, writes `alm_enable`, and reports pending from `alm_status`.

State and persistence: MPC5121 persists the Linux-time offset in `target_time`, abusing a hibernation target register because `actual_time` is read-only. Alarm state partly persists in hardware hour/minute and enable/status bits and partly in the driver's cached `wkalarm`, which is lost across reprobe. Remove disables alarm and update interrupts and disposes OF IRQ mappings.

Dependencies and integration: depends on OF compatible strings `fsl,mpc5121-rtc` and `fsl,mpc5200-rtc`, `irq_of_parse_and_map()`, big-endian MMIO helpers for 16/32-bit fields, and RTC feature flags for minute alarm resolution and lack of update interrupt support.

Risks and test signals: probe does not explicitly reject zero IRQ mappings before requesting them. Cached alarm date fields can diverge from hardware and are not persistent. The MPC5121 offset model caps the usable range to U32 seconds despite the underlying hardware maximum. Test both compatibles, keep-alive battery/oscillator failure warning path, alarm IRQ ack/status clear, periodic/update IRQ handling, minute-resolution alarm semantics, remove cleanup, missing IRQs, 12-hour MPC5200 decoding, and wraparound near U32 limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpc5121.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpfs.c

Purpose: implements the Microchip PolarFire SoC RTC as a memory-mapped seconds counter with wake alarm support, prescaler setup, and wake IRQ integration.

Important APIs/types/functions: `struct mpfs_rtc_dev` holds the `rtc_device` and register base. `mpfs_rtc_start()` starts the counter, `mpfs_rtc_clear_irq()` disables/clears alarm state and flushes the posted write, `mpfs_rtc_readtime()`/`settime()` read and upload the 64-bit datetime split across lower/upper registers, and `mpfs_rtc_readalarm()`/`setalarm()` program alarm and compare registers. `mpfs_rtc_alarm_irq_enable()` toggles alarm-on/off control bits, and `mpfs_rtc_wakeup_irq_handler()` reports `RTC_AF`.

Control flow: probe allocates the RTC, gets/enables the `rtc` clock, maps MMIO, requests the wakeup IRQ, reads the `rtcref` clock rate to program the prescaler as rate minus one, initializes wakeup plus wake IRQ, and registers the device. Set-time writes the split datetime registers, sets `CONTROL_UPLOAD_BIT`, polls for upload completion with `read_poll_timeout()`, and restarts the RTC. Set-alarm disables the alarm, writes split alarm seconds, writes compare registers to all ones for alarm mode, then optionally sets wake mode and starts the counter.

State and persistence: hardware persists the seconds counter, prescaler, mode bits, control bits, alarm registers, and compare bypass values. Driver state is stateless beyond base address and RTC pointer. Alarm enabled state is derived from `MODE_WAKE_EN`; pending state is not returned by `read_alarm()`.

Dependencies and integration: depends on platform MMIO, two clocks named `rtc` and `rtcref`, `pm_wakeirq`, IRQ 0 as wakeup interrupt, and OF compatible `microchip,mpfs-rtc`.

Risks and test signals: `mpfs_rtc_readalarm()` reconstructs alarm time as lower register shifted by 32 plus masked upper register, which is the inverse of the set-time split and should be verified against the hardware register definition. Probe calls `devm_clk_get_enabled("rtc")` then separately `devm_clk_get("rtcref")`; missing or zero-rate `rtcref` needs coverage. Alarm mode writes `mode = MODE_WAKE_EN | MODE_WAKE_CONTINUE` only when enabling, leaving prior mode bits when disabling. Test upload timeout, posted interrupt clear, prescaler maximum, wake IRQ registration, alarm enable/disable, 42-bit range cap, and split lower/upper encoding for time and alarm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-msc313.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-msc313.c

Purpose: supports the MStar/SigmaStar MSC313 RTC, a 32-bit seconds counter with match-alarm registers and clock-rate programming.

Important APIs/types/functions: `struct msc313_rtc` stores the RTC device and MMIO base. Alarm callbacks use `REG_RTC_MATCH_VAL_L/H` and `INT_MASK_BIT`; time callbacks use load and count registers plus `LOAD_EN_BIT`, `READ_EN_BIT`, and `CNT_EN_BIT`. `msc313_rtc_interrupt()` checks `ALM_INT_BIT`, clears interrupt state through control bits, and reports `RTC_AF`.

Control flow: probe maps the register block, obtains IRQ 0, allocates the RTC, requests a shared IRQ, enables the input clock, writes the clock rate into frequency control registers, stores private data, and registers the RTC. Reads fail with `-EINVAL` if the counter is not enabled, then set `READ_EN_BIT` and busy-wait until the hardware latches count registers. Set-time writes split load value, sets `LOAD_EN_BIT`, busy-waits until it clears, then enables counting. Alarm setup writes split match value and masks/unmasks the interrupt.

State and persistence: persistent hardware state includes frequency control, count, load, match, enable, interrupt mask, and status bits. Driver state is only MMIO and RTC pointer. There is no explicit range beyond U32 seconds and no wakeup setup.

Dependencies and integration: depends on OF compatible `mstar,msc313-rtc`, platform MMIO, one clock, one shared IRQ, and RTC class alarm APIs.

Risks and test signals: the read and load latch waits are unbounded busy loops with only `udelay(1)`, so hardware stuck bits can hang the caller. Alarm enabled defaults to zero unless unmasked; `read_alarm()` does not report pending status. Test disabled-counter read failure, latch completion, stuck latch behavior, clock-rate split programming, shared IRQ returning `IRQ_NONE` for non-alarm status, alarm mask polarity, and U32 wrap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-msc313.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-msm6242.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-msm6242.c

Purpose: implements the Oki MSM6242 legacy RTC, used on m68k-era systems, using 4-bit digit registers mapped as 32-bit MMIO slots.

Important APIs/types/functions: `struct msm6242_priv` stores the MMIO register array and RTC device. `msm6242_read()`/`write()` use raw 32-bit access while masking to low nibbles. `msm6242_lock()` asserts HOLD and retries while BUSY is set, and `msm6242_unlock()` releases HOLD. `msm6242_read_time()` and `msm6242_set_time()` handle digit-by-digit BCD-like fields, weekday, month, year, and 12/24-hour conversion.

Control flow: probe gets the memory resource, maps it with `devm_ioremap()`, stores driver data, and registers a time-only RTC. Runtime reads hold the chip, read seconds/minutes/hours/day/week/month/year digit registers, map years 00-69 to 2000-2069 and 70-99 to 1970-1999, convert 12-hour PM/AM if needed, then unlock. Runtime writes hold the chip, write each digit register, preserve 12/24-hour mode semantics for the hour tens register, optionally write weekday, fold years >= 2000 to two digits, and unlock.

State and persistence: all time state lives in MSM6242 registers and persists according to board power. Driver state has no cache. No alarm or IRQ support is exposed despite control-register interrupt bits existing.

Dependencies and integration: platform-only driver named `rtc-msm6242`, no OF table, RTC class ops, raw MMIO, and legacy board resources.

Risks and test signals: `msm6242_lock()` warns but continues after BUSY timeout, so callers may read or write inconsistent values. `msm6242_set_time()` mutates `tm->tm_year` when folding to two digits. Raw 32-bit access assumes a specific bus layout where each 4-bit register occupies a word. Test HOLD/BUSY retry behavior, 12-hour midnight/noon/PM conversion, year windowing, weekday `-1` skip, resource size/alignment, and behavior when control register reads are unreliable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-msm6242.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt2712.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt2712.c

Purpose: implements the MediaTek MT2712 SoC RTC with protected write-trigger semantics, full date/time alarm matching, power-loss detection, and suspend wake support.

Important APIs/types/functions: `struct mt2712_rtc` tracks RTC device, base, IRQ, wake-enabled state, and `powerlost`. `mt2712_rtc_write_trigger()` writes `WRTGR` and waits for `BBPU_CBUSY` to clear. `mt2712_rtc_writeif_unlock()` performs the two-step protection unlock. Time functions are `__mt2712_rtc_read_time()`, `mt2712_rtc_read_time()`, and `mt2712_rtc_set_time()`. Alarm functions program `MT2712_AL_*`, `MT2712_AL_MASK`, and `MT2712_IRQ_EN`. `mt2712_rtc_hw_init()` programs BBPU, CII, power keys, CON registers, and detects lost backup state.

Control flow: probe allocates private data, maps MMIO, calls hardware init before fetching the IRQ or allocating the RTC, requests a low-triggered threaded alarm IRQ, enables wake capability, sets the RTC range to 2000-2127, and registers. Reads reject access while `powerlost` is true and repeat field reads if seconds carried. Set-time writes all time fields, triggers the write, and clears `powerlost`. Set-alarm updates masked alarm fields, masks day-of-week matching, triggers, then enables/disables the alarm IRQ.

State and persistence: persistent state includes RTC time/alarm registers, power keys, BBPU, CON0/CON1, protection state, IRQ enable/status, and alarm mask. The driver caches only `powerlost` and suspend wake state. Alarm interrupt status is read in the threaded handler but not explicitly cleared there beyond framework/event handling via hardware semantics.

Dependencies and integration: depends on MMIO platform resource, IRQ 0, OF compatible `mediatek,mt2712-rtc`, PM sleep hooks, and MediaTek RTC write-trigger/protection conventions.

Risks and test signals: `mt2712_rtc_hw_init()` uses `mt2712_rtc->rtc` for debug messages before the RTC device is allocated, which is hazardous if those debug paths execute. `mt2712_rtc_write_trigger()` logs timeout but returns void, so callers cannot fail writes. Read consistency loop compares a second read against `tm_sec` and relies on wrap direction. Test power-key lost-power path, write-trigger timeout, protection unlock sequencing, alarm IRQ status handling, wake enable/disable failure paths, range endpoints, and probe ordering under dynamic debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt2712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt6397.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt6397.c

Purpose: provides RTC support for MediaTek MT6397-family PMICs over the parent MFD regmap, covering time, one-shot alarm, pending power-on alarm state, and wake IRQs.

Important APIs/types/functions: `struct mt6397_rtc` is defined in the MT6397 RTC header and used here for regmap, base address, match data, mutex, IRQ, and RTC device. `mtk_rtc_write_trigger()` writes the variant-specific WRTGR and polls `RTC_BBPU_CBUSY`. `mtk_rtc_irq_handler_thread()` reports alarm events and disables alarm IRQ. Bulk time/alarm callbacks use `RTC_OFFSET_*` indexes and masks from `linux/mfd/mt6397/rtc.h`.

Control flow: probe gets parent `mt6397_chip`, uses the memory resource start as `addr_base`, gets match data for WRTGR offset, requests the alarm IRQ, enables wakeup, sets a 1900-2027 range with start-time correction from 1968-01-02, and registers. Reads bulk-read time fields under a mutex and retry if seconds carry. Set-time increments month and weekday to hardware's one-based encoding, bulk-writes the fields, then triggers. Set-alarm reads current alarm registers, overlays masked fields, writes them only when enabling, sets the DOW mask and one-shot enable bit, then triggers.

State and persistence: hardware registers persist time, alarm, IRQ enable/status, PDN2 power-on alarm flag, and BBPU busy state. Driver state has a mutex and variant data but no alarm cache. The IRQ handler disables alarm enable after firing, making alarms one-shot.

Dependencies and integration: depends on MT6397 MFD parent data/regmap, OF compatibles `mediatek,mt6323-rtc`, `mt6357-rtc`, `mt6358-rtc`, and `mt6397-rtc`, variant WRTGR offsets, threaded high-triggered IRQ, and PM wake hooks.

Risks and test signals: `mtk_rtc_set_time()` and set-alarm mutate the caller-provided `rtc_time` month/weekday in place. The IRQ handler computes `irqen = irqsta & ~RTC_IRQ_EN_AL`, which uses status bits as the new enable value and deserves hardware-specific validation. Set-alarm with `enabled == false` does not rewrite alarm time fields, only clears one-shot. Test all compatibles, WRTGR poll timeout, regmap errors, month/weekday one-based conversions, power-on alarm pending flag, one-shot disable after IRQ, and suspend wake calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt6397.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt7622.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt7622.c

Purpose: implements the MediaTek MT7622/SOC RTC block, including protected initialization magic, 2001-2099 calendar range, alarm handling, clock control, and wake IRQ support.

Important APIs/types/functions: `struct mtk_rtc` holds RTC device, MMIO base, IRQ, and clock. Register helpers `mtk_w32()`, `mtk_r32()`, `mtk_rmw()`, `mtk_set()`, and `mtk_clr()` wrap relaxed MMIO. `mtk_rtc_hw_init()` writes power-check, key, and protection magic values and clears debounce/stop. `mtk_rtc_get_alarm_or_time()` and `mtk_rtc_set_alarm_or_time()` abstract time/alarm register banks. `mtk_rtc_alarmirq()` handles alarm status and disables alarm control.

Control flow: probe maps MMIO, gets and enables the `rtc` clock, requests IRQ 0, initializes hardware, marks wake-capable, and registers the RTC through `devm_rtc_device_register()`. Reads repeatedly sample the seconds register before and after the other fields until stable. Set-time validates the tm_year against 2001-2099, stops the counter, writes all fields rebased by 100, and restarts. Set-alarm validates the year, clears alarm enable, synchronizes with any running IRQ handler, writes alarm fields, then writes `RTC_AL_ALL` to enable all alarm matching and interrupt bits.

State and persistence: hardware persists magic/protection registers, debounce, control stop bit, time/alarm calendar registers, alarm control, and interrupt status. Driver state owns the clock and IRQ only. Remove disables the clock.

Dependencies and integration: depends on OF compatibles `mediatek,mt7622-rtc` and `mediatek,soc-rtc`, a named `rtc` clock, MMIO, IRQ, and PM sleep wake calls.

Risks and test signals: the valid range intentionally excludes year 2000 because hardware mishandles leap-year behavior for relative year zero. Set-alarm ignores `wkalrm->enabled` and always restarts the alarm after programming. No explicit `alarm_irq_enable` callback is provided, so alarm enable control is via set-alarm only. Test year 2000 rejection, 2001/2099 endpoints, stable-read loop around second rollover, alarm pending ack, `synchronize_irq()` path, clock cleanup on probe errors/remove, and wake IRQ enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt7622.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mv.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mv.c

Purpose: implements the Marvell Orion RTC, using packed BCD MMIO registers for time/date and optional alarm interrupt support.

Important APIs/types/functions: `struct rtc_plat_data` stores RTC device, MMIO base, optional IRQ, and optional clock. `mv_rtc_read_time()`/`set_time()` decode and encode packed time/date registers. `mv_rtc_read_alarm()`/`set_alarm()` handle alarm registers with per-field `RTC_ALARM_VALID` bits. `mv_rtc_alarm_irq_enable()` toggles the alarm mask, and `mv_rtc_interrupt()` clears and reports alarm cause.

Control flow: probe maps MMIO, optionally enables a clock, rejects unsupported 12-hour mode, checks that the RTC is ticking by detecting the stuck reset value over one second, gets an optional IRQ, allocates the RTC, requests the IRQ if available, and clears the alarm feature when no IRQ exists. Time reads/writes access two packed registers. Alarm writes accept `-1` fields as don't-care by omitting valid bits and enable or mask the interrupt.

State and persistence: time, date, alarm, interrupt mask, and interrupt cause live in hardware. Driver state owns optional clock and IRQ. Remove disables wake capability and the clock but leaves RTC time running.

Dependencies and integration: depends on OF compatible `marvell,orion-rtc`, MMIO, optional clock, optional shared IRQ, BCD helpers, and `module_platform_driver_probe()` because remove is in exit text.

Risks and test signals: optional clock enable return is ignored if present; if `clk_prepare_enable()` fails, probe continues. Alarm enabled is reported as true for any nonzero interrupt mask. Probe's ticking check sleeps one second and assumes `0x01000000` means nonfunctional. Test 12-hour rejection, stuck-clock detection, optional/no IRQ behavior with RTC alarm feature cleared, don't-care alarm fields, alarm cause clear, clock failure handling, and BCD range endpoints 2000-2099.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc.c

Purpose: supports older Freescale/NXP i.MX1 and i.MX21 RTC blocks with day/hour/minute/second counters, alarms, periodic interrupt bits, and clock-rate selection.

Important APIs/types/functions: `struct rtc_plat_data` stores RTC device, MMIO, IRQ, `ipg` and `ref` clocks, cached alarm time, and device type. `get_alarm_or_time()` and `set_alarm_or_time()` convert between split day/hour/min/sec registers and seconds. `rtc_update_alarm()` writes alarm registers and clears interrupt status. `mxc_rtc_irq_enable()` protects interrupt-enable updates with `rtc->irq_lock`. `mxc_rtc_interrupt()` handles alarm and periodic status.

Control flow: probe identifies i.MX1 versus i.MX21, maps MMIO, allocates RTC, sets range based on 9-bit or 16-bit days, enables `ipg` and `ref` clocks, validates the reference clock rate against supported values, enables the module, optionally requests a shared IRQ and wake IRQ, then registers. Reads repeat `get_alarm_or_time()` until two samples match. Set-time writes the split registers until a readback matches. Set-alarm clears status, writes alarm time, caches it, and enables/disables the alarm bit.

State and persistence: hardware persists split time/alarm counters, control, status, and interrupt enable bits. Driver state caches `g_rtc_alarm` but read-alarm gets hardware registers and pending status. For i.MX1, `start_secs` is initialized to the start of the current year unless DT overrides it.

Dependencies and integration: depends on OF compatibles `fsl,imx1-rtc` and `fsl,imx21-rtc`, named clocks `ipg` and `ref`, supported ref rates of 32768/32000/38400 Hz, optional shared IRQ, wake IRQ integration, and RTC class feature/range handling.

Risks and test signals: `mxc_rtc_interrupt()` takes `rtc->irq_lock` and calls `mxc_rtc_irq_enable()`, which takes the same spinlock again in the alarm path, a potential self-deadlock if the alarm bit is set. Read/write consistency loops have no timeout. IRQ absence still leaves alarm ops registered but no explicit feature clear. Test alarm IRQ path under lockdep, reference clock validation, no-IRQ platforms, i.MX1 start-time behavior, range limits, periodic status events, read/write rollover loops, and wake IRQ setup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc_v2.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc_v2.c

Purpose: implements the i.MX53 secure RTC low-power block, using the LP secure counter and alarm registers with CKIL-domain synchronization and wake IRQ support.

Important APIs/types/functions: `struct mxc_rtc_data` tracks RTC device, MMIO, clock, spinlock, and IRQ. `mxc_rtc_sync_lp_locked()` waits for three CKIL cycles by watching `SRTC_LPSCLR`. `mxc_rtc_lock()`/`unlock()` combine the spinlock with clock enable/disable. `mxc_rtc_read_time()`/`set_time()` access `SRTC_LPSCMR`; alarm callbacks access `SRTC_LPSAR`, `SRTC_LPCR`, and `SRTC_LPSR`. `mxc_rtc_wait_for_flag()` handles init/non-valid state transitions.

Control flow: probe maps MMIO, gets the clock and IRQ, initializes wake IRQ, prepares/enables the clock, initializes glitch detect, clears status, exits init state, exits non-valid state with LP enabled, allocates/registers the RTC, disables the clock but leaves it prepared, then requests the IRQ. Runtime register writes take the driver lock, enable the clock, perform the write, synchronize across CKIL cycles, and disable the clock. The IRQ handler enables the clock under lock, checks/clears alarm status, disables further alarm wake bits, synchronizes, and reports `RTC_AF`.

State and persistence: hardware persists the LP secure counter, alarm register, LP control/status bits, non-valid/init state, glitch detector setting, and wake enable. Driver state persists lock, clock preparation, and IRQ.

Dependencies and integration: depends on OF compatible `fsl,imx53-rtc`, platform MMIO, a single RTC clock, one IRQ, `dev_pm_set_wake_irq()`, and the RTC class.

Risks and test signals: `mxc_rtc_read_time()` reads only `SRTC_LPSCMR`, so it treats the counter as a 32-bit seconds value and ignores `SRTC_LPSCLR` fractional/low bits. Synchronization loops have bounded timeouts and log once on stuck counters. Probe must balance prepared/enabled/disabled clock states across multiple error paths. Test init and non-valid state timeout paths, alarm interrupt disable behavior, CKIL sync timeout, clock-enable failure in IRQ and callbacks, wake IRQ setup, and U32 range wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct3018y.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct3018y.c

Purpose: implements the Nuvoton NCT3018Y I2C RTC with BCD time registers, hour/min/sec alarm, voltage-low reporting, optional IRQ alarm support, and optional common-clock `clkout` provider.

Important APIs/types/functions: `struct nct3018y` stores the RTC, I2C client, part number, and optional `clk_hw`. `nct3018y_set_alarm_mode()` toggles alarm interrupt enable and clears alarm flag. `nct3018y_get_alarm_mode()` reads enable and pending bits. RTC callbacks cover time, alarm, alarm IRQ enable, and `RTC_VL_READ`. Clock-output callbacks implement recalc, determine, set rate, prepare, unprepare, and is_prepared over `NCT3018Y_REG_CLKO`.

Control flow: probe checks I2C/SMBus functionality, reads control and part ID, applies NCT3018Y-specific 24-hour mode setup, clears status, allocates the RTC, configures 2000-2099 range, requests a falling-edge threaded IRQ if `client->irq` is present, optionally registers clkout, and registers the RTC. Read-time first reads status and returns `-EINVAL` if the voltage/battery mask reports invalid data, then reads a 10-byte block and decodes sparse time offsets. Set-time may temporarily set the TWO bit on NCT3018Y parts, writes seconds/minutes/hours individually and day/month/year as a block, then restores TWO. Alarm ops write/read only sec/min/hour alarm registers and use control/status bits for enabled/pending.

State and persistence: persistent hardware state includes time, alarm, status flags, control bits, part-specific TWO/HF bits, and clkout rate/enable. Driver state tracks part number and optional clkout registration. Alarm feature is cleared when no IRQ is supplied.

Dependencies and integration: depends on I2C with raw I2C, SMBus byte, and block-data support; OF compatible `nuvoton,nct3018y`; optional IRQ; optional common clock framework; and RTC voltage-low ioctl support.

Risks and test signals: `nct3018y_rtc_read_time()` treats status byte zero as invalid, but `probe()` clears the status register to zero, so the first read-time behavior depends on hardware repopulating battery bits. Several block reads request contiguous bytes while only every other alarm/time register is used for sec/min/hour. `nct3018y_clkout_register_clk()` ignores `of_clk_add_provider()` cleanup/error. Test part ID variants, TWO-bit restore on all write errors, voltage-low ioctl, no-IRQ feature clearing, alarm flag clear, clkout rates and enable, status-after-probe behavior, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct3018y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct6694.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct6694.c

Purpose: implements the Nuvoton NCT6694 RTC subdevice over the parent USB-MFD command protocol, providing BCD time, hour/min/sec alarm, IRQ-domain alarm events, and wake capability.

Important APIs/types/functions: packed protocol structs `nct6694_rtc_time`, `nct6694_rtc_alarm`, and `nct6694_rtc_status` are wrapped by `union nct6694_rtc_msg`. `struct nct6694_rtc_data` stores parent device, RTC, shared message buffer, and mapped IRQ. RTC callbacks build static `nct6694_cmd_header` instances for time, alarm, and status commands and call `nct6694_read_msg()`/`write_msg()`. `nct6694_irq()` clears pending status and reports `RTC_AF`.

Control flow: probe allocates state and the message union, maps `NCT6694_IRQ_RTC` from the parent IRQ domain, registers a devm cleanup action to dispose the mapping, initializes wakeup, allocates RTC, sets 2000-2099 range, stores driver data, requests a threaded IRQ, and registers the RTC. Time reads/writes transfer the full seven-byte BCD structure. Alarm reads/writes transfer three BCD fields plus enable/pending bytes. Alarm IRQ enable writes status command fields with interrupt/GPO enable bits.

State and persistence: hardware/firmware persists BCD time, alarm, alarm enable/pending, and status. The driver reuses one shared message union for all callbacks and IRQ handler, relying on RTC core locking only where explicitly used in the IRQ path.

Dependencies and integration: depends on the parent `nct6694` MFD, USB command helpers, IRQ domain, platform subdevice name `nct6694-rtc`, and RTC class.

Risks and test signals: `nct6694_rtc_alarm_irq_enable()` modifies `sts->irq_en` without first reading current status, so stale union contents can affect enable state. The shared union has no explicit lock in normal read/set callbacks, while the IRQ path uses `rtc_lock()`. Alarm date is not supported, only sec/min/hour. Test concurrent RTC ops and IRQ, IRQ mapping cleanup, status enable from cold zeroed buffer, BCD conversion, parent command failures, wakeup init failure, and no-domain/no-IRQ cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct6694.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ntxec.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ntxec.c

Purpose: implements RTC date/time access for the Netronix embedded controller MFD used in e-book readers.

Important APIs/types/functions: `struct ntxec_rtc` stores the platform device and parent `struct ntxec`. `ntxec_read_time()` reads packed year/month, day/hour, and minute/second registers through the parent regmap, with a retry if minute/second changed. `ntxec_set_time()` writes a `reg_sequence` using `regmap_multi_reg_write()` and `ntxec_reg8()` encoding.

Control flow: probe inherits the OF node from the parent, allocates private data, gets the parent EC driver data, allocates an RTC, sets ops and 2000-2255 range, and registers. Read-time reads minute/second first, then day/hour and year/month, then re-reads minute/second; if either changed, it restarts from the beginning to avoid cross-field rollover. Set-time writes seconds as zero first, then year/month/day/hour/minute, then final seconds, preventing rollover while multi-register writes are in progress.

State and persistence: all RTC state lives in the embedded controller registers. Driver state has only the EC pointer. No alarm, IRQ, wakeup, or local cache exists.

Dependencies and integration: depends on the Netronix EC MFD, parent regmap, platform subdevice `ntxec-rtc`, and RTC class. The driver reuses the parent OF node for binding/metadata.

Risks and test signals: read retry can loop indefinitely if the EC returns unstable minute/second values. The register interface uses binary bytes rather than BCD. No validity flag is checked for backup-battery or EC time initialization. Test consistent retry around minute rollover, multi-write ordering, parent regmap errors, 2255 upper range, and absence of alarm/update features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ntxec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nvidia-vrs10.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nvidia-vrs10.c

Purpose: implements RTC support for NVIDIA VRS10 power sequencer devices over I2C with PEC enabled, including 32-bit seconds time, alarm wake bits, interrupt clearing, and suspend wake integration.

Important APIs/types/functions: `struct nvvrs_rtc_info` stores device, I2C client, RTC, and IRQ. `nvvrs_update_bits()` provides read-modify-write for control registers. `nvvrs_rtc_write_alarm()`, `nvvrs_rtc_enable_alarm()`, and `nvvrs_rtc_disable_alarm()` manage alarm registers and RTC_WAKE/RTC_PU bits. Time and alarm callbacks read/write four one-byte registers MSB-first or MSB-to-LSB. `nvvrs_pseq_irq_clear()` clears all interrupt source registers by read/writeback. `nvvrs_pseq_vendor_info()` validates model revision.

Control flow: probe requires a client IRQ, enables I2C PEC, validates vendor/model revision, clears pending interrupts, allocates the RTC, requests a threaded IRQ, initializes wakeup, sets 2000-2099 range, and registers. Reads assemble 32-bit seconds from T3..T0; writes split seconds into T3..T0. Set-alarm disables if requested disabled, but then always enables wake bits and writes the alarm time. IRQ handler checks `INT_SRC1_RTC`, reports `RTC_AF` under `rtc_lock()`, then clears all interrupt sources.

State and persistence: hardware persists seconds counter, alarm seconds, RTC_WAKE/RTC_PU control bits, interrupt source flags, model revision, and PEC behavior. Driver state has no cache. Disabled alarm is represented by writing `0xffffffff`.

Dependencies and integration: depends on I2C/SMBus byte operations with PEC, OF compatible `nvidia,vrs-10`, a valid IRQ, PM sleep wake callbacks, and RTC class.

Risks and test signals: `nvvrs_rtc_set_alarm()` disables when `enabled == false` but then immediately enables alarm wake bits and writes the requested alarm time, so disabled alarms may be re-enabled. `alarm_irq_enable()` is a no-op because hardware cannot separate IRQ enable from alarm programming. Multi-byte register coherency relies on MSB-first reads with no retry. Test model revision rejection, PEC transactions, disabled-alarm semantics, reset-value read alarm, interrupt-source clear failures, suspend/resume wake bit writes, 2038+ values within 2000-2099 range, and missing IRQ probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nvidia-vrs10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nxp-bbnsm.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nxp-bbnsm.c

Purpose: implements the NXP i.MX93 BBNSM RTC via a parent syscon regmap, using a 47-bit counter shifted to seconds plus a time-alarm register.

Important APIs/types/functions: `struct bbnsm_rtc` stores RTC device, syscon regmap, IRQ, and an unused clock pointer. `bbnsm_read_counter()` repeatedly reads MS and LS counter registers and converts `(msb << 17) | (lsb >> 15)` to seconds. RTC callbacks read/write time, read/write alarm, and toggle alarm IRQ/event enable. `bbnsm_rtc_irq_handler()` checks event bits, disables alarm, clears the event, and reports `RTC_AF`.

Control flow: probe allocates the RTC, resolves the parent's syscon regmap, gets IRQ 0, clears pending events, initializes wakeup and wake IRQ, requests a shared IRQ, sets range to U32 seconds, and registers. Read-time first verifies `RTC_EN` in `BBNSM_CTRL`, then reads the stable counter. Set-time disables RTC, writes seconds into the 47-bit counter split with 15 fractional bits, then re-enables. Set-alarm writes `BBNSM_TA` and delegates enable control to `bbnsm_rtc_alarm_irq_enable()`.

State and persistence: hardware persists control bits, interrupt enables, events, split RTC counter, and alarm time. Driver state has no cache. Alarm pending is read from `BBNSM_EVENTS`; enabled state is not reported by `read_alarm()`.

Dependencies and integration: depends on OF compatible `nxp,imx93-bbnsm-rtc`, parent syscon node, regmap, shared IRQ, wake IRQ helpers, and RTC class.

Risks and test signals: `bbnsm_read_counter()` initializes `time` from `tmp` and returns `time`, which can return the previous sample after timeout and ignores regmap read errors. `bbnsm_rtc_set_alarm()` comments "disable the alarm" but calls `regmap_update_bits(..., TA_EN, TA_EN)`, which appears to set the enable value with a narrow mask instead of using `TA_EN_MSK`. Most regmap operations ignore return values. Test counter stable-read timeout, disabled RTC read, set-time split encoding, alarm enable/disable bit masks, event clear write, regmap failure propagation gaps, wake IRQ setup, and U32 rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-nxp-bbnsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-omap.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-omap.c

Purpose: implements TI OMAP/AM33xx/DA8xx RTC support, including BCD calendar time, alarm interrupts, wake enable, scratch-register NVMEM, ext_wakeup pinconf, optional external clock selection, and AM3352 PMIC power-off sequencing.

Important APIs/types/functions: `struct omap_rtc_device_type` captures variant capabilities and lock/unlock operations; `struct omap_rtc` stores RTC device, MMIO, clock, two IRQs, cached interrupt register, power-controller state, external-clock state, and pinctrl device. Core callbacks are `omap_rtc_read_time()`, `omap_rtc_set_time()`, `omap_rtc_read_alarm()`, `omap_rtc_set_alarm()`, and `omap_rtc_alarm_irq_enable()`. `rtc_irq()` handles alarm and 1-second events. `omap_rtc_power_off_program()` and `omap_rtc_power_off()` program ALARM2 and PMIC power enable. Pinconf callbacks control `OMAP_RTC_PMIC_EXT_WKUP_*`, and NVMEM callbacks expose scratch registers.

Control flow: probe selects variant data from OF or platform ID, gets timer and alarm IRQs, chooses `ext-clk` or `int-clk`, maps MMIO, enables runtime PM, unlocks protected registers, disables interrupts, enables 32 kHz clock where supported, clears old status, forces 24-hour/stop/auto-comp state, optionally selects external 32 kHz clock, then locks. It allocates the RTC, sets 2000-2099 range, requests timer/alarm IRQs, registers pinctrl and RTC, registers scratch NVMEM, and if configured as system-power-controller installs `pm_power_off`. Time/alarm operations wait for BUSY clear with local IRQs disabled before touching BCD registers. Suspend saves/restores interrupt enables or enables IRQ wake; runtime suspend rejects full suspend without external clock.

State and persistence: hardware persists BCD time/date, alarm1, alarm2, interrupt enables/status, control, oscillator, PMIC control, scratch registers, and KICK lock state. Driver state caches interrupt enable across suspend, power-off singleton pointer, PMIC-controller status, and external clock selection. Remove leaves RTC running but disables IRQs and restores internal clock when applicable.

Dependencies and integration: depends on OF compatibles `ti,am3352-rtc` and `ti,da830-rtc`, platform IDs, clocks, runtime PM, pinctrl/pinconf, RTC NVMEM registration, optional system-power-controller property, PM wake, and variant-specific KICK unlock registers.

Risks and test signals: the static `omap_rtc_nvmem_config.priv` and `rtc_pinctrl_desc.name` are mutated at probe, which is unsafe for multiple instances. `rtc_wait_not_busy()` has no error return if BUSY remains set. Several paths call clock disable on `rtc->clk` even when both `ext-clk` and `int-clk` lookups failed, relying on `IS_ERR()` checks only in some paths. PMIC power-off relies on a one-second ALARM2 race-retry loop and global `pm_power_off`. Test all variants, KICK lock/unlock, BUSY stuck behavior, alarm and 1-second IRQ events, IRQ wake register handling, scratch NVMEM read/write, ext_wakeup pinconf polarity, external clock suspend behavior, system power-off alarm2 sequence, and multi-instance assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-opal.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-opal.c

Purpose: implements PowerNV IBM OPAL firmware RTC access, including firmware RTC read/write and timed power-on alarm support.

Important APIs/types/functions: `opal_to_tm()` and `tm_to_opal()` convert between OPAL BCD packed date/time values and `struct rtc_time`. `opal_get_rtc_time()` and `opal_set_rtc_time()` call `opal_rtc_read()`/`opal_rtc_write()` with retry handling for busy and transient hardware/internal errors. TPO alarm functions `opal_get_tpo_time()`, `opal_set_tpo_time()`, and `opal_tpo_alarm_irq_enable()` use OPAL async tokens, `opal_tpo_read()`/`write()`, and async completion messages.

Control flow: module init registers the platform driver only when `FW_FEATURE_OPAL` is present. Probe allocates the RTC, enables wake capability only when DT has `wakeup-source` or legacy `has-tpo`, clears alarm feature otherwise, sets range 0000-9999, clears update interrupt feature, and registers. Time reads/writes loop while firmware returns busy/busy-event and retry certain error statuses up to ten times. Alarm read/write allocate an async token, issue TPO command, wait for response, decode async return, and release the token.

State and persistence: all RTC and TPO state is owned by OPAL firmware/platform hardware. Driver state is only the RTC device. Alarm disable writes zero date/time through the TPO interface; no Linux-side cache or IRQ handler exists.

Dependencies and integration: depends on PowerPC OPAL firmware APIs, platform/OF compatible `ibm,opal-rtc`, platform ID `opal-rtc`, async token infrastructure, and firmware feature gating.

Risks and test signals: alarm support depends entirely on DT wakeup properties, not probing TPO availability. TPO only cares about hour and minute and passes `(h_m_s_ms >> 32) & 0xffff0000`, so seconds are ignored by design. OPAL read/write loops can wait indefinitely if firmware keeps returning BUSY. Test no-OPAL init, busy/busy-event polling, hardware/internal retry exhaustion, async token interruption, no-alarm feature clearing, TPO no-alarm `-ENOENT`, alarm disable, and full BCD century conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-optee.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-optee.c

Purpose: implements an RTC backed by an OP-TEE pseudo trusted application. It maps RTC class operations to TEE invoke commands for time, offset correction, alarm, alarm wait events, wake-alarm status, and feature/range discovery.

Important APIs/types/functions: protocol structs `optee_rtc_time`, `optee_rtc_alarm`, and `optee_rtc_info` define shared-memory payloads. `struct optee_rtc` stores TEE context, primary and alarm-wait sessions, shared memory, feature flags, alarm kthread, and RTC device. RTC callbacks call PTA commands `GET_TIME`, `SET_TIME`, `GET/SET_OFFSET`, `READ/SET/ENABLE_ALARM`. `optee_rtc_wait_alarm()` blocks in a second session, `optee_rtc_cancel_wait_alarm()` cancels it, and `optee_rtc_handle_alarm_event()` reports RTC alarm IRQs from a kthread. `optee_rtc_read_info()` validates info version and programs RTC range/features.

Control flow: probe opens an OP-TEE context, opens the primary PTA session, allocates shared memory large enough for info/time/alarm payloads, reads info/features, and if alarm is supported creates a kthread, opens a second session for blocking waits, and enables wakeup if the PTA reports wake alarm support. It registers the RTC, clears unsupported feature bits after registration, then starts the alarm thread. Remove cancels wait, stops the thread, disables wakeup, closes sessions, frees shared memory, and closes context. Suspend sends wakeup status to OP-TEE based on `device_may_wakeup()`.

State and persistence: RTC time, offset, alarm, pending state, feature bits, and wake behavior are persisted and enforced by the secure PTA. Driver state includes session IDs, shared memory, features, and the lifetime of the alarm wait thread. No hardware registers are directly accessed.

Dependencies and integration: depends on the TEE client bus, OP-TEE implementation match, the RTC PTA UUID, kernel shared memory allocation, kthreads, RTC class feature bits, and PM sleep hooks.

Risks and test signals: shared memory is reused across operations without an explicit per-callback mutex, so concurrent RTC operations could overwrite payloads. Probe creates `alarm_task` before opening the second session; error unwind stops it only under alarm feature handling. `rtc_year_days()` is called with secure-world month values that appear already in `struct rtc_time` zero-based form only if the PTA follows Linux semantics. Test feature combinations, info version mismatch, range conversion, unsupported correction/alarm paths, concurrent set/read operations, alarm thread cancellation during remove, second-session open failure, wakeup suspend command failure, and TEE ret versus transport ret mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-optee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-palmas.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-palmas.c

Purpose: implements RTC support for TI Palmas/TPS65913/TPS65914 PMIC-family devices through the parent Palmas MFD register helpers, with BCD time, alarm IRQ, wake support, and backup-battery charging configuration.

Important APIs/types/functions: `struct palmas_rtc` stores RTC device, device pointer, and IRQ. `palmas_rtc_read_time()` latches time with `GET_TIME` then bulk-reads seconds through years. `palmas_rtc_set_time()` stops the RTC, bulk-writes BCD time, and restarts it. Alarm callbacks use `PALMAS_ALARM_SECONDS_REG` through year plus `PALMAS_RTC_INTERRUPTS_REG`. `palmas_clear_interrupts()` read/write-clears `PALMAS_RTC_STATUS_REG`, and `palmas_rtc_interrupt()` reports `RTC_AF`.

Control flow: probe reads DT backup-battery charge properties, allocates state, clears pending interrupts, optionally configures backup battery charge current and enable bits, starts the RTC, gets IRQ 0, marks wake-capable, registers the RTC, and requests a low-triggered threaded IRQ. Set-alarm disables alarm interrupts before programming alarm registers and re-enables when requested. Remove disables alarm IRQ; suspend/resume toggle IRQ wake if wake-capable.

State and persistence: PMIC registers persist BCD time, alarm, RTC stop/control, interrupt enable/status, and backup-battery charging configuration. Driver state is minimal and contains no cache.

Dependencies and integration: depends on Palmas MFD parent data and register helper APIs, OF compatible `ti,palmas-rtc`, platform IRQ, PM wake hooks, and RTC class.

Risks and test signals: `platform_get_irq()` return is stored but not checked before wake setup and IRQ request, so negative IRQ handling relies on later APIs. Stop/start polarity is non-obvious: setting `STOP_RTC` starts in this driver's usage and clearing it stops. Backup-battery configuration is persistent and should be intentional from DT. Test parent regmap errors, pending status clear, backup charge low/high current properties, alarm disable-before-write, IRQ request failure with missing IRQ, suspend wake, and 2000-2099 BCD range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-palmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcap.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcap.c

Purpose: implements the Motorola EZX PCAP RTC subdevice, exposing day and time-of-day counters plus day/time alarm registers from the PCAP MFD.

Important APIs/types/functions: `struct pcap_rtc` stores parent PCAP chip and RTC device. `pcap_rtc_read_time()`/`set_time()` convert between seconds since epoch and PCAP day plus time-of-day registers. Alarm callbacks use the corresponding `DAYA` and `TODA` registers. `pcap_rtc_irq()` maps PCAP 1 Hz and alarm IRQs to RTC update and alarm events. `pcap_rtc_irq_enable()` enables/disables parent IRQ lines.

Control flow: probe gets the parent PCAP pointer, allocates and configures an RTC with a 14-bit day range, maps PCAP 1 Hz and alarm IRQs, requests both IRQs, and registers the RTC. Runtime time/alarm operations read or write the day and seconds-within-day registers. `alarm_irq_enable()` only enables/disables the PCAP alarm IRQ; set-alarm does not use the `enabled` field directly.

State and persistence: PCAP hardware persists day, time-of-day, alarm day, and alarm time-of-day counters. Driver state holds no cache. IRQ enable state is managed by Linux IRQ masking rather than a device register in this driver.

Dependencies and integration: depends on the EZX PCAP MFD, `pcap_to_irq()`, PCAP register access helpers, platform subdevice `pcap-rtc`, and RTC class.

Risks and test signals: `ezx_pcap_read()` and write return values are ignored, so bus failures are invisible to RTC callers. Alarm enabled state is not returned in `read_alarm()` and not programmed in `set_alarm()`. Disabling IRQs directly can interact poorly with shared users if parent IRQ mapping changes. Test PCAP read/write failures, 14-bit day range limit, 1 Hz update IRQ, alarm IRQ enable/disable, alarm set with disabled flag, and parent IRQ mapping correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2123.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2123.c

Purpose: implements the NXP/Philips PCF2123 and compatible RV2123 SPI RTC using regmap, with BCD time, minute-resolution alarm, offset calibration, optional IRQ, and reset/probe validation.

Important APIs/types/functions: `struct pcf2123_data` stores RTC device and SPI regmap. `pcf2123_regmap_config` sets 8-bit registers, read/write flag masks, and max register. `pcf2123_read_offset()`/`set_offset()` convert the signed 7-bit plus coarse-bit offset register to/from ppb using 2170 ppb steps. Time callbacks bulk-read/write seconds through year and use `OSC_HAS_STOPPED` validity. Alarm callbacks use minute/hour/day/month-day registers and `CTRL2_AIE/AF`. `pcf2123_rtc_irq()` checks/clears `CTRL2_AF`. `pcf2123_reset()` sends software reset, verifies STOP, and restarts.

Control flow: probe allocates state, initializes SPI regmap, tries to read current time, resets and presence-checks the chip if read-time fails, logs SPI speed, allocates RTC, optionally requests a threaded IRQ and enables wakeup, marks alarm resolution as minute, clears update interrupt feature, sets range 2000-2099 and start-time behavior, then registers. Set-time stops the counter, bulk-writes BCD time, then clears control to restart. Set-alarm disables AIE, clears AF, writes minute/hour/day and disables weekday matching, then re-enables if requested.

State and persistence: hardware persists time, alarm, control flags, oscillator-stopped flag, offset calibration, countdown timer/clockout state, and alarm flag. Driver state only stores regmap and RTC pointer. Reset clears/reinitializes control state but not Linux-side cache.

Dependencies and integration: depends on SPI, regmap, optional IRQ, OF compatibles `nxp,pcf2123`, `microcrystal,rv2123`, deprecated `nxp,rtc-pcf2123`, and SPI IDs. The device requires active-high chip select at board level.

Risks and test signals: probe resets the chip whenever read-time fails, including failures caused by an oscillator-stopped validity bit, which may clear useful diagnostic state. Offset conversion prefers coarse mode for overlapping values and clamps out-of-range requests. `pcf2123_rtc_irq()` ignores regmap read/update errors and can return `IRQ_NONE` on bus failure. Test SPI mode/CS polarity, oscillator-stopped read failure, reset presence check, offset clamp/coarse/fine mapping, alarm minute-resolution behavior, optional IRQ/fwnode trigger flags, AF clear, and 2000-2099 range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2123.c -->
