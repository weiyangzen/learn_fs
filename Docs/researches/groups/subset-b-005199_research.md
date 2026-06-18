# Research: subset-b-005199

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-jz4740.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-jz4740.c

Purpose: implements the Ingenic JZ4740/JZ4760/JZ4770/JZ4780 SoC RTC as a platform MMIO RTC, including timekeeping, alarm IRQs, hibernate-based poweroff, wakeup timing parameters, and an optional exported 32 kHz clock.

Important APIs and functions: the `jz4740_rtc_ops` callbacks are `jz4740_rtc_read_time()`, `jz4740_rtc_set_time()`, `jz4740_rtc_read_alarm()`, `jz4740_rtc_set_alarm()`, and `jz4740_rtc_alarm_irq_enable()`. Register access is centralized in `jz4740_rtc_reg_read()`, `jz4740_rtc_reg_write()`, `jz4740_rtc_wait_write_ready()`, `jz4780_rtc_enable_write()`, and `jz4740_rtc_ctrl_set_bits()`. Probe wires resources, wake IRQ, optional `pm_power_off`, and optional `clk_hw` provider.

Control flow: probe maps registers, enables the `rtc` clock, marks the device wake-capable, registers the RTC, and requests the alarm/update IRQ. Reads reject uninitialized hardware by checking the scratchpad magic, then read the seconds register until two consecutive values match. Setting time writes seconds and then stores the scratchpad marker. Alarm setup writes `SEC_ALARM` and toggles alarm enable and interrupt bits. The IRQ handler translates 1 Hz and alarm flags into `rtc_update_irq()` events and clears hardware flags through the protected control update helper.

State and persistence: the hardware stores seconds, alarm seconds, regulator and wake timing registers, hibernate state, and a scratchpad initialization marker. Driver state is `struct jz4740_rtc`, including mapped base, SoC type, RTC device, optional clock hardware, and spinlock. `dev_for_power_off` is a static singleton for system-power-controller use. The RTC persists if the SoC backup domain remains powered.

Dependencies and integration: depends on platform resources, device tree compatibles, `devm_clk_get_enabled()`, PM wake IRQ helpers, RTC class APIs, optional OF clock provider, and the kernel global `pm_power_off` hook. The SoC type controls whether the JZ4780 write-enable sequence is required before writes.

Risks: all writes depend on `WRDY` polling and, on newer chips, the magic `WENR` sequence; timeout handling is critical. The wakeup/reset tick calculations mask values with the field mask and may deserve hardware validation. Alarm times are stored as lower 32-bit seconds, matching the advertised `U32_MAX` range. The global poweroff hook can only support one device.

Test signals: boot on each compatible, read before/after scratchpad initialization, write-ready timeout injection, JZ4780 write-enable failure, alarm enable/disable and IRQ clearing, wake-from-suspend, hibernate poweroff, and optional 32 kHz clock registration and enable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-jz4740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-loongson.c

Purpose: provides RTC support for Loongson SoCs and bridges, covering TOY counter timekeeping, alarm handling, PM-domain wakeup control, ACPI fixed RTC events, and chip-specific workarounds for broken control or alarm registers.

Important APIs and types: `struct loongson_rtc_config` carries PM offset and workaround flags; `struct loongson_rtc_priv` stores regmap, PM base, RTC device, spinlock, and the 64-year alarm compensation. RTC callbacks are `loongson_rtc_read_time()`, `loongson_rtc_set_time()`, `loongson_rtc_read_alarm()`, `loongson_rtc_set_alarm()`, and `loongson_rtc_alarm_irq_enable()`. Interrupt paths are `loongson_rtc_isr()` and ACPI `loongson_rtc_handler()`.

Control flow: probe maps MMIO into a regmap, selects OF/ACPI match data, allocates the RTC, configures alarms unless the chip flags disable them, clears UIE support, and registers a 2000-2099 RTC. Time reads check whether TOY counters and oscillator are enabled unless the LS1C workaround applies, then decode packed `TOY_READ0/1`. Setting time writes `TOY_WRITE0/1` and enables TOY/oscillator. Alarms write `TOY_MATCH0`, while PM enable bits drive wake and interrupt routing.

State and persistence: hardware TOY registers persist in the RTC domain. `fix_year` is derived from current time and compensates the 6-bit alarm year field; stale `fix_year` after a time jump can affect alarm reconstruction. PM status/enable registers are protected by `priv->lock`.

Dependencies and integration: uses MMIO regmap, ACPI fixed event handler registration, OF and ACPI match tables, platform IRQs, and Loongson PM1 status/enable registers. Some variants disable alarm feature bits at runtime.

Risks: LS1C control-register accesses can hang, so workaround flags must match hardware. Alarm year encoding is only six bits and relies on a previous time read to set `fix_year`. ACPI handler removes PM wake enable and clears status; mismatch between ACPI and non-ACPI paths can leave alarms armed. `pm_base` is derived by subtracting a per-chip offset from the RTC register base.

Test signals: verify LS1B/LS1C/LS2K/LS7A/ACPI variants, alarm feature clearing for workaround chips, 64-year alarm compensation around boundaries, ACPI fixed event install/remove, PM1 enable/status updates, and TOY disabled reads returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-lp8788.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-lp8788.c

Purpose: implements the TI LP8788 MFD RTC child, using parent LP8788 register helpers for time, two selectable alarms, wakeup, and optional alarm IRQ delivery.

Important APIs and functions: `struct lp8788_rtc` links the parent `struct lp8788`, RTC device, selected alarm, and mapped IRQ. Time conversion helpers are `_to_tm_wday()` and `_to_lp8788_wday()`. RTC callbacks are `lp8788_rtc_read_time()`, `lp8788_rtc_set_time()`, `lp8788_read_alarm()`, `lp8788_set_alarm()`, and `lp8788_alarm_irq_enable()`. `lp8788_alarm_irq_register()` maps the parent IRQ-domain alarm resource.

Control flow: probe obtains the parent LP8788, picks platform-data alarm selection or alarm 1, registers an RTC, and tries to map/request the alarm IRQ. Reads unlock/latch the RTC and bulk-read second through weekday registers. Setting time writes individual byte registers except weekday, which is read-only. Alarm operations use arrays to choose alarm 1 or alarm 2 base/enable/int masks.

State and persistence: time and alarm registers live inside the LP8788 PMIC. Driver state only tracks the chosen alarm and IRQ mapping. Weekday is bit-encoded in hardware; alarms store an alarm-enable bit in the weekday/en register slot.

Dependencies and integration: depends on `linux/mfd/lp8788.h`, the LP8788 IRQ domain, named platform IRQ resource `LP8788_ALM_IRQ`, parent register accessors, RTC class, and platform data for selecting alarm 1 versus alarm 2.

Risks: no alarm IRQ resource leaves timekeeping usable but `alarm_irq_enable()` returns `-EIO`. `_to_lp8788_wday()` assumes a valid nonzero `tm_wday`, while Linux weekdays are normally 0-6; zero would shift by -1. Year support is offset from 2000 and rejects pre-2000 dates only. The read path does not validate hardware fields.

Test signals: time set/read across 2000 boundary, weekday conversions, both alarm selections, missing IRQ resource, IRQ-domain mapping failures, interrupt enable register bit selection, and alarm IRQ delivery to `rtc_update_irq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-lp8788.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc24xx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc24xx.c

Purpose: supports the NXP LPC178x/18xx/408x/43xx RTC block with MMIO time registers, alarm registers, clocks, and a single interrupt line.

Important APIs and functions: `struct lpc24xx_rtc` stores the register base, RTC device, and `rtc`/`reg` clocks. `lpc24xx_rtc_ops` exposes read/set time and alarm plus alarm IRQ enable. `lpc24xx_rtc_interrupt()` handles interrupt status and alarm masking.

Control flow: probe maps registers, fetches/enables the RTC and register clocks, clears pending interrupts, enables counting, requests the IRQ, and registers the RTC. Setting time disables counting with calibration enabled, writes discrete fields, then re-enables. Reading time uses consolidated `CTIME0/1/2` registers. Alarm writes disable matching through `AMR`, program all alarm fields, then optionally clear `AMR` to match all fields.

State and persistence: time and alarm state are hardware-backed. The driver has no persistent software state beyond clock handles and base pointer. Hardware alarm enable state is inferred from `AMR == 0`.

Dependencies and integration: depends on platform MMIO and IRQ resources, named clocks `rtc` and `reg`, OF compatible `nxp,lpc1788-rtc`, RTC class APIs, and standard IRQ handling.

Risks: month/year values appear written/read in hardware encoding rather than normalized Linux conventions; this must match controller documentation. Any failure after enabling clocks must unwind both clocks, which probe and remove mostly handle. The interrupt handler reports `RTC_IRQF` even if no recognized cause is set.

Test signals: clock enable/unwind paths, time set/read normalization, alarm enable/disable through `AMR`, IRQ status clearing, removal masking, and alarm invalid-date validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc24xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc32xx.c

Purpose: implements RTC support for LPC32xx SoCs using an up/down counter pair, match0 alarm, backup-domain initialization key, and suspend/freezer wake management.

Important APIs and functions: `struct lpc32xx_rtc` holds base, IRQ, software `alarm_enabled`, RTC device, and spinlock. RTC callbacks are `lpc32xx_rtc_read_time()`, `lpc32xx_rtc_set_time()`, `lpc32xx_rtc_read_alarm()`, `lpc32xx_rtc_set_alarm()`, and `lpc32xx_rtc_alarm_irq_enable()`. PM hooks include suspend/resume plus freeze/thaw.

Control flow: probe maps the RTC, initializes the backup domain only if the key register does not contain the load value, disables match0 otherwise, registers the RTC, then requests the IRQ if present. Setting time disables the counter, writes `UCOUNT` and the complementary `DCOUNT`, and restores control. Alarms write match0 and enable control bit when requested. The IRQ disables the alarm, moves match0 to `0xffffffff`, clears status, and reports `RTC_AF`.

State and persistence: hardware counter state can survive chip power cycles. The key register prevents reinitializing persistent domain state on later boots. Software `alarm_enabled` is needed across freeze/thaw because the hardware alarm bit is deliberately cleared.

Dependencies and integration: platform MMIO, optional platform IRQ, OF compatible `nxp,lpc3220-rtc`, RTC class APIs, spinlocks, and PM sleep callbacks.

Risks: no IRQ resource leaves alarms configurable but not wake-capable. Counter updates rely on the disable bit and lock ordering. The driver intentionally sets match0 to a far future value after an interrupt to avoid repeated firing. Freeze always disables the alarm and thaw restores only if software state says it was enabled.

Test signals: first-boot key initialization versus retained-state path, set/read epoch seconds, alarm one-shot behavior, IRQ absence, suspend wake enable/disable, hibernate freeze/thaw, and `UCOUNT/DCOUNT` consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t80.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t80.c

Purpose: supports the ST M41T80-family and Micro Crystal RV4162 I2C RTCs, including time, alarm IRQs, oscillator-failure and battery-low reporting, optional square-wave clock output, and optional legacy watchdog miscdevice support.

Important APIs and types: `struct m41t80_data` stores feature flags, I2C client, RTC device, and optional common-clock state. Feature bits describe halt, battery-low, square-wave, extra watchdog resolution, and alternate square-wave register placement. RTC callbacks include `m41t80_rtc_read_time()`, `m41t80_rtc_set_time()`, `m41t80_read_alarm()`, `m41t80_set_alarm()`, `m41t80_alarm_irq_enable()`, and `m41t80_rtc_proc()`. Optional clock methods are `m41t80_sqw_*`; optional watchdog methods are `wdt_ping()`, `wdt_disable()`, `wdt_ioctl()`, `wdt_open()`, and `wdt_release()`.

Control flow: probe validates I2C functionality, selects feature flags, allocates the RTC, optionally requests a threaded alarm IRQ, configures wakeup, clears HT and ST bits, registers watchdog and square-wave clock where enabled, and registers the RTC. Time reads reject oscillator failure, then bulk-read BCD date/time. Setting time writes BCD registers, preserves square-wave bits in the weekday register on alternate chips, and if OF was set, restarts the oscillator with a 4-second stabilization delay before clearing OF. Alarm setup clears AFE and AF, writes alarm fields while preserving SQWE, then optionally re-enables AFE.

State and persistence: date/time, flags, alarm, square-wave, and watchdog registers live in battery-backed RTC hardware. Software state tracks feature selection and optional clock rate/enable cache. The watchdog code uses static global `save_client`, `wdt_margin`, `wdt_is_open`, and `boot_flag`.

Dependencies and integration: depends on SMBus byte and I2C-block transactions, OF/I2C ID match data, RTC class, optional common clock provider, optional watchdog miscdevice and reboot notifier, wakeup-source property, and threaded IRQs.

Risks: OF and HT handling is device-specific and can delay set-time by seconds. Alarm IRQ support depends on either a physical IRQ or wakeup-source property; otherwise alarm features are cleared. The watchdog implementation is legacy, global, and only one client can be saved. Square-wave and alarm share `ALARM_MON` bits, so preserving SQWE is required to avoid side effects.

Test signals: all supported IDs and feature combinations, OF restart/clear failure, HT logging and clear, battery-low proc output, alarm IRQ flag clearing, wakeup-source without IRQ, square-wave rate selection and alternate register placement, watchdog open/ioctl/reboot notifier behavior, and I2C transfer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t93.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t93.c

Purpose: implements a compact SPI RTC driver for the ST M41T93, with BCD timekeeping, oscillator-failure handling, halt-update recovery, and battery-low warnings.

Important APIs and functions: `m41t93_set_reg()` writes a single register with the SPI write bit set. `m41t93_set_time()` and `m41t93_get_time()` are the RTC callbacks in `m41t93_rtc_ops`. Probe sets SPI mode parameters, probes the weekday register, and registers the RTC.

Control flow: setting time rejects pre-2000 dates, tries to clear the OF flag, kickstarts the oscillator if OF remains, encodes century bits in the hour register, and writes a burst of eight time registers. Reading time clears HT if set, treats OF as `-EINVAL` while still decoding registers, warns on battery low, bulk-reads registers, and reconstructs the century from hour bits.

State and persistence: all state is stored in the SPI RTC registers. There is no software persistence beyond the registered RTC device. Flags provide sticky hardware state for oscillator failure, battery low, and halted readout updates.

Dependencies and integration: uses SPI `spi_w8r8()`, `spi_write_then_read()`, BCD helpers, and the RTC class. It has no alarm, wakeup, or NVMEM integration.

Risks: the OF kickstart path uses a local buffer before final field population, so register semantics should be verified on hardware. Reads can return decoded time with `-EINVAL` when OF is set, which callers treat as invalid. Century encoding assumes supported years map cleanly into the two top hour bits.

Test signals: pre-2000 rejection, OF clear and kickstart paths, HT clear path, BL warning, probe-not-found detection from weekday upper bits, and century rollover reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t94.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t94.c

Purpose: supports the ST M41T94 SPI RTC with basic BCD read and set time, including halt/stop-bit clearing and century-bit handling.

Important APIs and functions: `m41t94_read_time()` and `m41t94_set_time()` form `m41t94_rtc_ops`. Probe sets 8-bit SPI transfers, reads seconds as a presence check, registers the RTC, and stores the RTC pointer as driver data.

Control flow: read first clears the halt-update bit in register `0x0c`, then clears the stop bit in seconds, then reads each date/time register individually and adds 100 years when the century bit is set or century-enable is clear. Set time writes registers starting at seconds with the SPI write bit, always enables century handling in the hour register, and sets the century bit for years >= 2000.

State and persistence: the chip stores time in battery-backed BCD registers. No software state is persistent. The driver has no alarm or NVMEM exposure.

Dependencies and integration: uses SPI single-byte operations, BCD helpers, platform/SPI module plumbing, and RTC class registration.

Risks: read-time ignores negative return values from later `spi_w8r8()` calls after the initial halt/seconds checks. It always interprets years with 1900/2000 century behavior and lacks range limits in set-time. No `rtc_valid_tm()` call is made.

Test signals: SPI presence failure, halt and stop bit clearing, 1999/2000 century behavior, invalid SPI reads during individual field reads, and basic set/read round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t35.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t35.c

Purpose: implements the SGS-Thomson M48T35 Timekeeper RAM RTC for memory-mapped platforms, with BCD time read/write and SGI IP27 register-layout support.

Important APIs and types: `struct m48t35_rtc` maps the chip layout near the end of the Timekeeper RAM window, with an alternate member order for `CONFIG_SGI_IP27`. `struct m48t35_priv` holds mapped registers and a spinlock. RTC callbacks are `m48t35_read_time()` and `m48t35_set_time()`.

Control flow: probe requests and maps the memory resource, initializes the lock, and registers the RTC. Reads set the READ latch bit under lock, read date/time BCD fields, restore control, convert to `rtc_time`, and normalize 1970-2069/2070-style year handling. Writes validate 1970-2069, convert to BCD, set the SET bit under lock, write fields, and restore control.

State and persistence: battery-backed Timekeeper RAM contains the RTC registers and likely broader RAM content, although this driver exposes only time. Driver state is volatile mapping metadata and lock.

Dependencies and integration: platform memory resource, `readb()`/`writeb()`, BCD helpers, spinlocks, and RTC class registration.

Risks: supported date range is intentionally narrow and rejects dates after 2069. Day-of-week is ignored on read because hardware updates it only after a nonzero initial set. Register layout depends on build-time SGI configuration. No alarm or NVRAM provider is exposed despite the RAM-backed device.

Test signals: both register layouts, read latch/set latch behavior, 1969/1970/2069/2070 boundaries, BCD conversion, and memory-region request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t59.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t59.c

Purpose: supports ST M48T59/M48T02/M48T08 Timekeeper RTC/NVRAM devices across memory-mapped and platform-supplied I/O access modes, including optional alarm IRQs, battery status, and NVMEM exposure.

Important APIs and types: `struct m48t59_private` stores I/O base, IRQ, RTC device, and a spinlock. Platform data `struct m48t59_plat_data` supplies type, offset, and read/write callbacks. RTC callbacks cover time, alarm, proc battery output, and alarm IRQ enable. `m48t59_nvram_read()` and `m48t59_nvram_write()` back `devm_rtc_nvmem_register()`.

Control flow: probe chooses MEM or IO resource mode, fills default platform data and callbacks for memory resources, maps registers if needed, obtains optional IRQ, selects chip offset and alarm support by type, registers NVMEM for bytes before the RTC window, then registers the RTC. Reads/writes set READ/WRITE bits around BCD field access under the spinlock. Alarm writes support wildcard-ish invalid fields and are disabled on chips without alarm support or IRQ.

State and persistence: time, alarm, flags, and NVRAM are battery-backed hardware state. Software only serializes access. `pdata->offset` determines which address range is RTC registers versus NVRAM.

Dependencies and integration: depends on platform data for I/O-mapped chips, `linux/rtc/m48t59.h`, optional platform IRQ, NVMEM provider registration through RTC, and RTC class/proc hooks.

Risks: NVRAM read/write loops ignore the `offset` argument and use `cnt` directly, which is a correctness risk for nonzero-offset NVMEM accesses. Alarm methods return `-EIO` without IRQ. Century handling applies only M48T59 CEB/CB bits. Platform data defaults are mutable through `pdev->dev.platform_data`.

Test signals: each chip type offset and alarm feature behavior, memory versus I/O callback paths, NVMEM reads/writes with nonzero offsets, IRQ shared handling, battery flag proc output, century-bit rollover, and missing platform callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t59.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t86.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t86.c

Purpose: supports ST M48T86/Dallas DS12887-style indexed RTCs, including binary or BCD time mode, 12/24-hour handling, battery status reporting, chip-presence verification, and 114-byte NVRAM exposure.

Important APIs and functions: `m48t86_readb()` and `m48t86_writeb()` implement index/data register access. `m48t86_rtc_read_time()`, `m48t86_rtc_set_time()`, and `m48t86_rtc_proc()` are RTC callbacks. `m48t86_nvram_read()` and `m48t86_nvram_write()` expose NVRAM. `m48t86_verify_chip()` checks optional-board presence by writing the last two NVRAM bytes.

Control flow: probe maps separate index and data resources, stores driver data before verification, writes/readbacks NVRAM sentinels to prove the chip exists, registers RTC and NVMEM, and logs battery status. Reads decode based on data-mode bit and correct 12-hour PM. Writes set update/24-hour bits, write either binary or BCD fields, then clear update.

State and persistence: RTC registers and NVRAM are battery-backed. The verification path temporarily mutates two NVRAM bytes and restores them if the test succeeds.

Dependencies and integration: platform MMIO resources, optional OF compatible `st,m48t86`, RTC class, NVMEM provider via RTC, BCD helpers, and indexed CMOS-like hardware semantics.

Risks: failed chip verification can leave modified NVRAM bytes if the second-stage checks fail before restoration. No locking protects index/data access, so concurrent RTC and NVMEM operations could interleave. Years are always interpreted as 2000-2099. The driver lacks alarm support despite alarm registers existing.

Test signals: verify-chip success/failure with restoration, BCD and binary mode reads/writes, 12-hour PM correction, battery proc output, NVRAM nonzero offset accesses, and missing resource errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ma35d1.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ma35d1.c

Purpose: implements the Nuvoton MA35D1 RTC using MMIO BCD calendar/time registers, hardware initialization magic, alarm interrupts, and suspend wakeup support.

Important APIs and functions: `struct ma35_rtc` stores IRQ, MMIO base, and RTC device. `ma35d1_rtc_init()` writes the magic code until the active bit appears. `ma35d1_rtc_ops` provides read/set time, read/set alarm, and alarm IRQ enable. `ma35d1_rtc_interrupt()` reports alarm events.

Control flow: probe maps registers, obtains and enables the first DT clock, initializes RTC hardware if inactive, requests the IRQ with `IRQF_NO_SUSPEND`, enables wakeup, allocates/registers the RTC, and sets range 2000-2099. Reads loop until time and calendar are stable across a second read, then decode BCD fields. Setting time and alarm writes packed BCD calendar/time words. Alarm IRQ enable toggles `ALMIEN`.

State and persistence: hardware RTC registers retain time, alarm, weekday, init state, and interrupt flags in the RTC domain. Software state is minimal and volatile.

Dependencies and integration: OF compatible `nuvoton,ma35d1-rtc`, platform MMIO/IRQ, `of_clk_get()` and `clk_prepare_enable()`, RTC class, wake IRQ semantics through suspend/resume hooks, and raw MMIO accessors.

Risks: the enabled clock is not devm-managed or disabled on later probe failures. `platform_get_irq()` return is not checked before request. Read stability loop has no timeout if registers never stabilize. Interrupt handler calls `rtc_update_irq()` even when no event bits are set.

Test signals: inactive initialization timeout, clock lookup/enable failure cleanup, stable read loop under rollover, alarm IRQ enable/clear, invalid IRQ handling, suspend/resume wake toggling, and date range boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ma35d1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-macsmc.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-macsmc.c

Purpose: implements Apple SMC-backed RTC support for Apple Silicon systems, deriving wall time from a 48-bit SMC counter plus a persistent NVMEM offset.

Important APIs and types: `struct macsmc_rtc` stores the Apple SMC handle, RTC device, and `rtc_offset` NVMEM cell. RTC callbacks are `macsmc_rtc_get_time()` and `macsmc_rtc_set_time()`.

Control flow: probe only binds when a device-tree node is present, obtains the parent `apple_smc`, gets the `rtc_offset` NVMEM cell, allocates the RTC, sets a range based on a signed 48-bit 32768 Hz counter, and registers the RTC. Reads fetch six bytes of `CLKM`, read six offset bytes from NVMEM, add them, sign-extend from 48 bits, shift by 15 to seconds, and convert to `rtc_time`. Setting time reads `CLKM` and writes a new offset so the requested second starts at the current counter.

State and persistence: the SMC counter is hardware state; the time base is persistent through the NVMEM offset cell. The driver does not store alarms or volatile time state.

Dependencies and integration: Apple SMC MFD APIs, `nvmem_cell_read()`/`write()`, OF compatible `apple,smc-rtc`, RTC class, and sign-extension helpers.

Risks: NVMEM cell length shorter than six bytes is fatal. Endianness follows raw `memcpy()` into `u64`, so it relies on the SMC/NVMEM storage layout expected by the platform. There is no alarm support. Setting time truncates the offset write to six bytes.

Test signals: missing DT node, missing NVMEM cell, short cell, partial SMC read returning `-EIO`, negative offset sign extension, set/read round trip, and range limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-macsmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max31335.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max31335.c

Purpose: supports Analog Devices/Maxim MAX31331 and MAX31335 I2C RTCs with time, alarm, optional IRQs, SRAM NVMEM, configurable trickle charger, optional clock output, and MAX31335 temperature hwmon.

Important APIs and types: `struct chip_desc` abstracts register locations and capabilities per chip; `struct max31335_data` stores regmap, RTC, clock output, input clock, chip descriptor, and IRQ. RTC callbacks are `max31335_read_time()`, `max31335_set_time()`, `max31335_read_alarm()`, `max31335_set_alarm()`, and `max31335_alarm_irq_enable()`. Extra integration is handled by `max31335_clkout_register()`, `max31335_nvmem_reg_read/write()`, `max31335_read_temp()`, and `max31335_trickle_charger_setup()`.

Control flow: probe initializes an I2C regmap, selects chip data, allocates the RTC with range 2000-2199 and one-day alarm offset max, registers/disables clkout based on `#clock-cells`, requests threaded alarm IRQ if present, clears alarm feature if not, registers NVMEM, optionally registers hwmon for temperature, configures trickle charging from firmware properties, then registers the RTC. Time and alarm operations bulk-read/write BCD fields and manipulate the A1 interrupt/status bits. IRQ handling locks the RTC ops mutex, clears A1F, and emits `RTC_AF`.

State and persistence: date/time, alarm, interrupt flags, SRAM, trickle-charger setting, clock-output register, and temperature data are chip registers. Software state only tracks descriptor and registrations.

Dependencies and integration: I2C, regmap with volatile register callback, RTC class, optional common clock provider, `devm_rtc_nvmem_register()`, optional hwmon, firmware properties `aux-voltage-chargeable`, `trickle-resistor-ohms`, `adi,tc-diode`, and OF/I2C match tables.

Risks: `MAX31335_YEAR` is defined with the same value as month, though code uses descriptor offsets for time. `max31335_alarm_irq_enable()` passes `enabled` directly as bit value instead of using `FIELD_PREP`, relying on bit zero semantics for A1IE. The global static NVMEM config is mutated per probe, which is fragile for multiple devices. Trickle setup silently ignores unsupported resistor values.

Test signals: MAX31331 versus MAX31335 descriptor paths, 2099/2100 century bit behavior, alarm IRQ clear and pending state, no-IRQ alarm feature clearing, NVMEM read/write offsets, clkout rates/enabling/no provider path, hwmon temperature conversion, and all trickle property combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max31335.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6900.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6900.c

Purpose: implements the Maxim MAX6900 I2C RTC with burst read/write for time registers, separate century handling, and write-protect management.

Important APIs and functions: `max6900_i2c_read_regs()` performs burst plus century read, `max6900_i2c_write_regs()` writes century then burst with required delays, `max6900_i2c_clear_write_protect()` clears control write protect, and `max6900_rtc_read_time()`/`max6900_rtc_set_time()` are RTC callbacks.

Control flow: probe requires raw I2C transfers and registers the RTC. Reading sends burst-read and century-read messages, decodes BCD fields, and computes `tm_year` from century and year bytes. Setting clears write-protect, populates BCD fields including century, sets write-protect in the control byte, writes century first, delays, writes the burst block, and delays again.

State and persistence: hardware RTC registers contain time, control/write-protect, and century. There is no driver-owned persistent state.

Dependencies and integration: raw I2C transfer capability, SMBus byte write for control, BCD helpers, RTC class, and MAX6900-specific command opcodes.

Risks: I2C read/write expects exact message counts; partial transfers become `-EIO`. The driver has no alarm support. Weekday is not normalized by subtracting one. Required idle delay after writes is handled with `msleep(3)` but depends on datasheet timing.

Test signals: I2C capability failure, partial transfer failures, write-protect clear failure, century rollover, write delay timing, and set/read round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6902.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6902.c

Purpose: supports the Maxim MAX6902 SPI RTC with burst BCD time reads, individual field writes, separate century register, and write-protect control.

Important APIs and functions: `max6902_set_reg()` and `max6902_get_reg()` wrap one-byte register access. `max6902_read_time()` and `max6902_set_time()` implement RTC class operations. Probe configures SPI mode 3 and tests the seconds register.

Control flow: reading performs burst read command `0xbf`, decodes seconds through year, reads the century register separately, and normalizes `tm_year`. Setting converts `tm_year` to absolute year, clears write-protect, writes each time register and century, then restores write-protect.

State and persistence: all state is in the SPI chip registers; software state is only the registered RTC pointer.

Dependencies and integration: SPI mode 3, 8-bit words, BCD helpers, RTC class, and SPI write/read command bit conventions.

Risks: `max6902_set_time()` mutates the caller's `rtc_time` by adding 1900 to `tm_year`, which is surprising and can leak back to caller state. Individual writes ignore return values, so failed writes can still return success. No alarm or validation.

Test signals: SPI setup/probe read failure, write failure injection on individual fields, caller `tm_year` mutation, century rollover, and write-protect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6902.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6916.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6916.c

Purpose: implements the MAX6916 SPI RTC for 2000-2099 BCD timekeeping, with oscillator/status initialization and burst read/write.

Important APIs and functions: `max6916_read_reg()` and `max6916_write_reg()` handle SPI register access. `max6916_read_time()` and `max6916_set_time()` are RTC callbacks. Probe configures SPI mode 3, clears write-protect, enables oscillator behavior, logs control/status registers, and registers the RTC.

Control flow: read sends clock-burst read and decodes BCD fields, subtracting one from weekday and adding 100 to year. Set validates `tm_year` in 100-199, builds a burst write buffer including control byte, and writes it. Probe reads seconds, modifies control bit 7, masks status bits, writes status, and registers the device.

State and persistence: time, control, and status are in RTC registers. Driver state is not persistent.

Dependencies and integration: SPI mode 3, RTC class, BCD helpers, and MAX6916 burst command protocol.

Risks: status initialization masks data with `0x1B`, which must match oscillator/flag semantics. The burst write includes a control byte set to BCD zero. No alarm support. License string is `GPL v2` rather than the common `GPL`.

Test signals: date range rejection, SPI read/write failure paths, oscillator/status post-probe state, weekday normalization, and set/read round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6916.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max77686.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max77686.c

Purpose: supports RTC blocks in Maxim/Samsung PMICs MAX77686, MAX77802, MAX77620, and MAX77714, handling model-specific register maps, ancillary I2C or shared regmap access, regmap IRQ chips, alarms, update handshakes, and suspend wake routing.

Important APIs and types: `struct max77686_rtc_driver_data` describes per-model delay, masks, register map, alarm-enable style, I2C address, IRQ origin, pending status register, IRQ chip, and regmap config. `struct max77686_rtc_info` holds parent and RTC regmaps, IRQ chip data, virtual alarm IRQ, mutex, and RTC device. Core helpers are `max77686_rtc_data_to_tm()`, `max77686_rtc_tm_to_data()`, `max77686_rtc_update()`, `max77686_rtc_stop_alarm()`, `max77686_rtc_start_alarm()`, and `max77686_init_rtc_regmap()`.

Control flow: probe selects platform-device driver data, initializes the RTC regmap either through an ancillary I2C client or the parent regmap, registers a regmap IRQ chip, initializes binary/24-hour mode, enables wakeup, registers the RTC, maps RTCA1 virtual IRQ, and requests the threaded alarm IRQ. Reads trigger read-update, bulk-read fields, then decode. Writes bulk-write and trigger write-update. Alarm handling differs between MAX77802's dedicated enable register and other chips' per-field enable bits.

State and persistence: time, alarm, enable bits, update bits, and interrupt status are PMIC RTC registers. Software state tracks the regmap IRQ chip and mutex-protected operations. Wake state is managed through device wakeup and PM callbacks.

Dependencies and integration: MFD parent regmaps, I2C ancillary devices, regmap IRQ framework, platform IDs, RTC class, PM sleep hooks, and PMIC-private register definitions.

Risks: model data must exactly match hardware; incorrect map or mask corrupts time/alarm fields. The driver initializes control registers at probe, which can alter mode. MAX77714 has unsupported alarm pending status. Suspend disables the parent IRQ for shared-IRQ models to avoid I2C access while suspended, which must coordinate with other MFD users.

Test signals: each platform ID, ancillary versus parent-regmap path, regmap IRQ add/delete cleanup, binary/24-hour initialization, read/write update delay timing, MAX77802 dedicated alarm enable, no-pending-status model, suspend/resume wake behavior, and failed virtual IRQ mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max77686.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8907.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8907.c

Purpose: implements the MAX8907 PMIC RTC child with regmap time/alarm access and a regmap-IRQ alarm0 interrupt.

Important APIs and functions: `struct max8907_rtc` references the parent MFD, RTC regmap, RTC device, and IRQ. `regs_to_tm()` and `tm_to_regs()` convert BCD register arrays. `max8907_rtc_read_time()`, `max8907_rtc_set_time()`, `max8907_rtc_read_alarm()`, and `max8907_rtc_set_alarm()` are RTC callbacks. `max8907_irq_handler()` clears alarm0 control and emits `RTC_AF`.

Control flow: probe obtains the parent `struct max8907`, registers the RTC, obtains alarm0 virtual IRQ from the parent's RTC irqchip, and requests a threaded IRQ. Time operations bulk-read/write eight registers. Alarm set disables alarm0, writes target registers, and writes control `0x77` when enabled.

State and persistence: time and alarm state live in MAX8907 RTC registers. The driver does not keep software alarm state; enable is read from alarm control bits.

Dependencies and integration: MAX8907 MFD, parent `regmap_rtc`, regmap IRQ virtual IRQ lookup, RTC class, BCD helpers, and platform child binding.

Risks: the driver lacks `.alarm_irq_enable`, so alarm enable is only through `set_alarm()`. Month conversion in `tm_to_regs()` uses `tm_mon + 1`, but other fields depend on normalized input. IRQ handler disables alarm control unconditionally after firing.

Test signals: time conversion including 12-hour mode reads, alarm set/read/IRQ, virtual IRQ lookup failure, missing parent regmap, and alarm control clearing after IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8907.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8925.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8925.c

Purpose: provides RTC support for the MAX8925 PMIC, including time, alarm0, IRQ wake flags, and custom BCD-like digit conversion.

Important APIs and types: `struct max8925_rtc_info` holds RTC device, parent chip, RTC I2C client, device, and IRQ. `tm_calc()` decodes register digits into `rtc_time`; `data_calc()` encodes them. RTC callbacks include read/set time and alarm. `rtc_update_handler()` handles alarm IRQ and disables alarm0 match bits.

Control flow: probe obtains parent chip and RTC client, requests platform IRQ, enables wakeup, and registers the RTC. Time and alarm paths bulk-read/write eight registers via MAX8925 helpers. Alarm read combines IRQ mask, alarm control, and RTC status to populate enabled and pending. Suspend/resume set or clear the parent's wakeup flag bit.

State and persistence: PMIC RTC registers store time, alarm, masks, status, and control. Software state is volatile; wakeup intent is reflected in parent `wakeup_flag` during suspend.

Dependencies and integration: MAX8925 MFD helpers, platform IRQ, RTC class, PM sleep hooks, and parent wakeup flag contract.

Risks: conversion helpers encode `tm_mon` directly rather than `tm_mon + 1`, which should be checked against hardware conventions and other drivers. Probe uses `platform_get_irq()` without checking before request. Alarm IRQ enable is not exposed separately in `rtc_class_ops`; alarm enable comes through `set_alarm()`.

Test signals: digit conversion around month/year boundaries, IRQ mask/status pending behavior, alarm0 control `0x77`, platform IRQ failure, suspend/resume wakeup flag, and invalid buffer length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8925.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8997.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8997.c

Purpose: supports the MAX8997 PMIC RTC with binary-mode timekeeping, alarm1, IRQ-domain alarm delivery, and WTSR/SMPL reset features controlled by module parameters.

Important APIs and functions: `struct max8997_rtc_info` tracks parent PMIC, RTC I2C client, RTC device, mutex, virtual IRQ, and 24-hour mode. Conversion helpers are `max8997_rtc_data_to_tm()` and `max8997_rtc_tm_to_data()`. Alarm helpers include `max8997_rtc_stop_alarm()` and `max8997_rtc_start_alarm()`. Reset-feature helpers are `max8997_rtc_enable_wtsr()` and `max8997_rtc_enable_smpl()`.

Control flow: probe initializes binary/24-hour control, enables WTSR/SMPL if module parameters allow, marks wakeup, registers the RTC, maps the RTCA1 IRQ from the parent IRQ domain, and requests a threaded IRQ. Writes require `max8997_rtc_set_update_reg()` followed by a 20 ms delay. Alarm enabling sets enable bits on second/minute/hour and valid date/month/year fields while clearing weekday enable.

State and persistence: RTC registers hold time, alarm, update, WTSR, and SMPL settings. Software mutex serializes updates. WTSR/SMPL are disabled in shutdown.

Dependencies and integration: MAX8997 MFD private helpers, IRQ domain mapping, module parameters `wtsr_en` and `smpl_en`, RTC class, mutexes, and parent PMIC status registers.

Risks: reset features can affect system behavior beyond RTC timekeeping and are enabled by default. Driver uses info-level logging in set_alarm and IRQ paths, which can be noisy. No PM sleep hooks are present despite wakeup initialization. The driver only supports years >= 2000.

Test signals: WTSR/SMPL enable/disable and shutdown cleanup, update-register delay, alarm bit selection and IRQ handling, parent status pending read, year rejection, IRQ-domain mapping failure, and module parameter-disabled reset features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8997.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8998.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8998.c

Purpose: implements MAX8998 and LP3974 PMIC RTC support with BCD time, alarm0, optional IRQ-domain alarm delivery, and an LP3974 delay workaround.

Important APIs and types: `struct max8998_rtc_info` stores parent PMIC, RTC client, RTC device, IRQ, and `lp3974_bug_workaround`. Conversion helpers are `max8998_data_to_tm()` and `max8998_tm_to_data()`. Alarm helpers are `max8998_rtc_stop_alarm()`, `max8998_rtc_start_alarm()`, and `max8998_rtc_alarm_irq_enable()`.

Control flow: probe registers the RTC first, maps alarm0 IRQ if the parent IRQ domain exists, requests a threaded IRQ, logs chip name, and enables LP3974 workaround based on platform data. Time operations bulk-read/write eight BCD registers. Alarm setup disables alarm0, writes eight alarm registers, optionally waits for the workaround, then writes an alarm config mask (`0x77` or `0x57`) if enabled.

State and persistence: time, alarm, configuration, and status are PMIC RTC registers. Software only tracks workaround and IRQ mapping. LP3974 workaround adds 2-second sleeps after writes.

Dependencies and integration: MAX8998 MFD helpers, parent platform data, IRQ domain, RTC class, BCD helpers, and platform IDs for MAX8998/LP3974.

Risks: `max8998_tm_to_data()` writes `tm_mon` directly rather than `tm_mon + 1`, which should be validated against chip conventions. If IRQ mapping/request fails, alarm feature bits are not cleared. The LP3974 workaround makes writes extremely slow. There is no PM wake handling despite alarm IRQ support.

Test signals: MAX8998 versus LP3974 platform IDs, month/year conversion round trips, no IRQ-domain behavior, IRQ request failure, alarm config mask difference, status pending read, and write delays under workaround mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc13xxx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc13xxx.c

Purpose: supports Freescale/NXP MC13xxx PMIC RTCs, using separate day and time-of-day registers plus PMIC IRQs for alarm and RTC reset detection.

Important APIs and types: `struct mc13xxx_rtc` stores the RTC device, parent `mc13xxx`, and validity flag. RTC callbacks include `mc13xxx_rtc_read_time()`, `mc13xxx_rtc_set_time()`, `mc13xxx_rtc_read_alarm()`, `mc13xxx_rtc_set_alarm()`, and `mc13xxx_rtc_alarm_irq_enable()`. IRQ handlers are `mc13xxx_rtc_alarm_handler()` and `mc13xxx_rtc_reset_handler()`.

Control flow: probe allocates RTC state, requests reset and time-of-day alarm IRQs under the parent lock, sets range to 15-bit days, and registers the RTC. Reads sample day, seconds, day until day is stable. Setting time invalidates an active alarm seconds register, writes seconds zero, writes days, writes seconds, restores alarm seconds, unmasks reset IRQ if this makes the RTC valid, and updates `valid`. Alarm set disables the alarm by writing an invalid seconds value, masks/unmasks the alarm IRQ, then writes alarm day and seconds.

State and persistence: PMIC registers store days, seconds, alarm day/seconds, and IRQ status. Software `valid` is cleared by RTC reset IRQ and restored after a successful set-time.

Dependencies and integration: MC13xxx MFD register and IRQ APIs, parent lock discipline, platform IDs for MC13783/MC13892/MC34708, RTC class, and PMIC IRQ status APIs.

Risks: all public operations return `-ENODATA` while invalid until time is set. Day/seconds split requires careful ordering to avoid false alarms; the driver explicitly invalidates alarm seconds during updates. Alarm read uses current day plus alarm seconds and may not represent the programmed alarm day register. Probe error cleanup frees both IRQs even if only one request succeeded.

Test signals: reset IRQ invalidation, set-time restoring validity, day rollover during read, alarm false-trigger prevention, invalid alarm seconds behavior, IRQ mask/unmask status, and 15-bit day range limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc13xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc146818-lib.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc146818-lib.c

Purpose: provides shared MC146818/CMOS RTC helper routines for safe UIP-aware time reads, RTC presence checks, and CMOS time writes across architecture-specific RTC drivers.

Important APIs and functions: exported functions are `mc146818_avoid_UIP()`, `mc146818_does_rtc_work()`, `mc146818_get_time()`, and `mc146818_set_time()`. `mc146818_get_time_callback()` performs locked CMOS reads. `apply_amd_register_a_behavior()` handles AMD/Hygon register-A bank-select behavior.

Control flow: `mc146818_avoid_UIP()` repeatedly locks `rtc_lock`, reads seconds before checking UIP, waits if UIP is active, optionally invokes a callback, then rechecks UIP and seconds for NMI/virtualization races. `mc146818_get_time()` uses that helper, converts BCD when required, applies DECstation and ACPI century handling, then normalizes month/year. `mc146818_set_time()` validates year range, optionally splits ACPI century, converts to BCD if needed, sets RTC_SET, adjusts frequency-select/divider behavior, writes fields, and restores control/frequency registers.

State and persistence: hardware CMOS RTC registers are persistent. No software state is kept beyond stack callback parameters. Global `rtc_lock` serializes CMOS access.

Dependencies and integration: CMOS_READ/WRITE macros, `rtc_lock`, ACPI FADT century field, architecture config such as DECstation, x86 vendor data for AMD/Hygon behavior, BCD helpers, and exported symbols for other RTC code.

Risks: callbacks may run more than once, so callers must be idempotent. Timeout is in milliseconds but polling granularity is 100 usec. Incorrect century or binary/BCD mode handling changes dates by 100 years. Register-A behavior differs on AMD/Hygon and must preserve bank select semantics.

Test signals: UIP stuck timeout, UIP race during read, long read warning path, binary versus BCD mode, ACPI century presence/absence, DECstation special year handling, AMD/Hygon register-A path, year > 2069 rejection, and exported caller integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc146818-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mcp795.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mcp795.c

Purpose: supports Microchip MCP795 SPI RTCs with timekeeping, oscillator control, alarm0 IRQs, and workarounds for silicon date/month write issues.

Important APIs and functions: SPI RTCC helpers are `mcp795_rtcc_read()`, `mcp795_rtcc_write()`, and `mcp795_rtcc_set_bits()`. Oscillator helpers are `mcp795_stop_oscillator()` and `mcp795_start_oscillator()`. Alarm control is `mcp795_update_alarm()`. RTC callbacks are `mcp795_read_time()`, `mcp795_set_time()`, `mcp795_read_alarm()`, `mcp795_set_alarm()`, and `mcp795_alarm_irq_enable()`.

Control flow: probe configures SPI mode 0, starts the oscillator, clears 12-hour mode, registers the RTC, and if an IRQ exists clears pending alarm and requests a falling-edge threaded IRQ with wakeup enabled. Setting time stops the oscillator, saves EXTOSC, reads existing fields to preserve config bits, writes seconds through date, writes month/year separately for silicon issue avoidance, then restarts oscillator and restores EXTOSC. Alarm set rejects past alarms and alarms more than roughly one year out, disables alarm, writes match fields, and optionally enables it.

State and persistence: RTC registers hold time, oscillator/config bits, alarm fields, and flags. No software alarm state is retained. The IRQ handler disables the alarm in hardware and reports `RTC_AF`.

Dependencies and integration: SPI, OF/SPI IDs, BCD helpers, RTC class, optional IRQ/wakeup, and MCP795 command opcodes for RTCC access.

Risks: `mcp795_set_time()` mutates `tim->tm_year` when greater than 100. Stopping oscillator and EXTOSC toggling can fail or delay updates. Alarm range logic uses `is_leap_year(alm->time.tm_year)`, where `tm_year` is years since 1900 and may need absolute-year scrutiny. No explicit alarm feature clearing when no IRQ exists.

Test signals: oscillator stop timeout, EXTOSC preservation, date/month split write workaround, past and >1-year alarm rejection, IRQ disable-on-fire, 12-hour clear, SPI transfer failures, and set-time `tm_year` mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-mcp795.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson-vrtc.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson-vrtc.c

Purpose: implements Amlogic virtual wakeup RTC timer support, exposing current system wall time as RTC time and programming a relative wakeup alarm register during suspend.

Important APIs and types: `struct meson_vrtc_data` stores the alarm MMIO pointer, absolute alarm time, and enabled flag. RTC callbacks are `meson_vrtc_read_time()`, `meson_vrtc_set_alarm()`, and `meson_vrtc_alarm_irq_enable()`. PM callbacks are `meson_vrtc_suspend()` and `meson_vrtc_resume()`.

Control flow: probe maps the alarm register, marks wakeup-capable, allocates and registers an RTC. Reads return `ktime_get_real_ts64()`. Setting an alarm stores the absolute alarm epoch seconds if enabled, or zero otherwise. On suspend the driver subtracts current real time from stored alarm time and writes the positive relative seconds to the wakeup register. Resume clears stored alarm time and hardware wakeup value.

State and persistence: no real RTC hardware time is stored; time comes from kernel wall clock. The only hardware state is a wakeup countdown/seconds register. Alarm state is volatile software state.

Dependencies and integration: platform MMIO, OF compatible `amlogic,meson-vrtc`, RTC class, device wakeup, and PM sleep hooks.

Risks: `alarm_irq_enable()` stores `enabled` but suspend only checks `alarm_time`, so disabled alarms with stale nonzero time would be a risk if `set_alarm()` did not clear it. There is no read_alarm callback and no interrupt reporting. If alarm time has already passed, suspend logs an error and leaves the wakeup register unchanged.

Test signals: current-time read, set alarm then suspend relative conversion, disabled alarm clearing, passed-alarm suspend path, resume clearing, and wakeup register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson-vrtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson.c

Purpose: supports the internal RTC block in Amlogic Meson6/Meson8/Meson8b/Meson8m2 SoCs, managing both the AHB front-end and a custom serial bus to RTC registers, plus battery-backed register memory exposed as NVMEM.

Important APIs and types: `struct meson_rtc` stores device, reset, regulator, peripheral regmap, and serial regmap. Low-level serial helpers include `meson_rtc_sclk_pulse()`, `meson_rtc_send_bit()`, `meson_rtc_get_bus()`, `meson_rtc_serial_bus_reg_read()`, and `meson_rtc_serial_bus_reg_write()`. RTC callbacks are `meson_rtc_gettime()` and `meson_rtc_settime()`. NVMEM callbacks are `meson_rtc_regmem_read()` and `meson_rtc_regmem_write()`.

Control flow: probe allocates RTC state and device, maps the AHB registers into a regmap, obtains reset and `vdd` regulator, enables the regulator, writes static analog values, initializes a custom regmap bus for serial registers, verifies the counter can be read, registers NVMEM over four 32-bit regmem registers, and registers the RTC. Serial reads acquire bus readiness, send address bits, switch direction, and shift in 32 data bits. Writes acquire the bus, send data and address bits, then set write direction.

State and persistence: the RTC counter and four regmem words are hardware-backed and may be battery-backed through the RTC supply. Software state only tracks resource handles. The regulator remains enabled after successful probe.

Dependencies and integration: platform MMIO, regmap MMIO and custom bus APIs, reset controller, regulator framework, RTC class, NVMEM provider, OF compatibles for Meson generations, and polling helpers.

Risks: remove path does not disable the regulator on driver unbind. `meson_rtc_write_static()` polls `RTC_REG4` but masks a bit defined for `RTC_ADDR0`, which should be checked against hardware behavior. NVMEM callbacks divide byte counts by four and ignore remainder, so unaligned/non-multiple accesses may be mishandled. Bus acquisition resets hardware up to three times on readiness timeout.

Test signals: regulator enable/failure cleanup, reset-on-bus-timeout, serial read/write bit order, counter read functional check, set/read epoch seconds, NVMEM offset/size alignment, static value programming, and probe failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson.c -->
