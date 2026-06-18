# subset-b-005202 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c372.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c372.c

Purpose: implements an I2C RTC class driver for Ricoh R2025S/D, R2221TL, RS5C372A/B, RV5C386, and RV5C387A chips. It exposes time, alarm, voltage-low status, oscillator trim, offset adjustment, and optional proc/sysfs diagnostics.

Important APIs/types/functions: `struct rs5c372` stores the I2C client, RTC device, chip type, bus mode, cached 17-byte register buffer, and 12/24-hour flag. Key helpers are `rs5c_get_regs()`, `rs5c_reg2hr()`, `rs5c_hr2reg()`, `rs5c_oscillator_setup()`, `rs5c372_get_trim()`, `rs5c372_read_offset()`, and `rs5c372_set_offset()`. RTC ops include `read_time`, `set_time`, `read_alarm`, `set_alarm`, `alarm_irq_enable`, voltage `ioctl`, and offset callbacks.

Control flow: probe validates I2C/SMBus capabilities, identifies the chip from I2C or OF match data, reads all registers, detects the hour mode, performs oscillator setup after power loss, registers the RTC device, and creates trim/osc sysfs files when enabled. Time reads reject stopped oscillators using variant-specific status-bit polarity, then decode BCD fields into a 2000-2099 range. Time writes bulk-write time registers and clear warning bits. Alarm programming disables alarm A, writes minute/hour/day wildcard fields, and optionally re-enables alarm IRQs.

State and persistence: hardware persists time, alarm registers, control bits, oscillator stop/voltage flags, and trim register. Driver state caches the last register read and remembers bus style and hour mode. Offset programming writes the trim register and keeps RS5C372 XSL or R2221TL DEV semantics.

Dependencies and integration points: depends on I2C/SMBus block access, RTC core, BCD helpers, OF/I2C IDs, optional proc/sysfs RTC interfaces, and userspace `RTC_VL_READ`/`RTC_VL_CLR` ioctls.

Risks and test signals: `has_irq` is never set because IRQ registration is still a revisit item, so `alarm_irq_enable()` returns `-EINVAL` even though wake alarm registers can be programmed. Register cache values can be stale for offset reads unless refreshed by another operation. Variant-specific XSTP polarity is easy to regress. Test full I2C and SMBus-only adapters, all compatibles, oscillator-loss handling, voltage-clear ioctl, 12/24-hour conversion, alarm set/read with day wildcards, offset range limits, sysfs trim/osc output, and probe failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c372.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rtd119x.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rtd119x.c

Purpose: implements the built-in Realtek RTD1295/RTD119x RTC as a platform driver backed by MMIO registers and a clock.

Important APIs/types/functions: `struct rtd119x_rtc` stores the MMIO base, clock, RTC device, and fixed base year. `rtd119x_rtc_reset()`, `rtd119x_rtc_set_enabled()`, `rtd119x_rtc_read_time()`, and `rtd119x_rtc_set_time()` implement the hardware operations. RTC ops expose only `read_time` and `set_time`.

Control flow: probe maps the register resource, enables the input clock, powers the RTC if needed, resets and zeroes calendar registers on first power-up, enables the counter with the magic `0x5a` value, and registers the RTC. Reads sample seconds before and after reading all date fields, retrying up to three times if a rollover is detected. The hardware stores day-of-year count since `base_year` 2014; reads convert that day count to year/month/day, and writes convert `tm_yday` back to the 15-bit day counter.

State and persistence: hardware registers hold seconds, minutes, hours, day count, power state, reset control, and enable state. The driver has no alarm or NVRAM state and disables the RTC and clock on remove.

Dependencies and integration points: depends on platform resources, OF compatible `realtek,rtd1295-rtc`, `of_clk_get()`, MMIO accessors, RTC core, and leap-year/month helpers.

Risks and test signals: seconds are stored shifted left by one, limiting resolution interpretation to hardware format. Set-time correctness depends on a valid `tm_yday` supplied by the RTC core. Supported range is limited by a 15-bit day counter relative to 2014. Test first-boot RTCPWR initialization, clock enable failure cleanup, rollover retry behavior, dates before 2014, far-future day overflow, leap years, and remove-time disable/clock release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rtd119x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3028.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3028.c

Purpose: implements the Micro Crystal RV3028 I2C RTC with alarms, update interrupts, timestamp capture, EEPROM-backed configuration, NVRAM/EEPROM nvmem cells, backup switch control, trickle charger setup, offset calibration, and optional clock output.

Important APIs/types/functions: `struct rv3028_data` carries the regmap, RTC device, chip type, and optional `clk_hw`. EEPROM helpers `rv3028_enter_eerd()`, `rv3028_exit_eerd()`, `rv3028_update_eeprom()`, and `rv3028_update_cfg()` serialize nonvolatile configuration changes. RTC ops cover time, alarm, alarm IRQ enable, offset, backup-switch `param_get/set`, and voltage ioctl. Nvmem callbacks expose two RAM bytes and 43 EEPROM bytes.

Control flow: probe creates an I2C regmap, warns on missed alarm status, allocates the RTC, optionally requests a threaded IRQ, selects day-of-month alarms with `WADA`, enables timestamp events, applies trickle charger properties, adds timestamp sysfs attributes, registers the RTC, registers nvmem providers, and optionally registers clkout. IRQ handling reads status, reports PF/AF/UF events, clears handled flags and disables matching interrupt enables, and notifies timestamp sysfs on external events.

State and persistence: time, alarms, event flags, clock output, backup mode, trickle charger, and offset are persisted in hardware registers, with selected settings committed through EEPROM update commands. Timestamp count/data and RAM survive backup power. Driver state is mostly the regmap and RTC feature bits.

Dependencies and integration points: depends on I2C regmap, RTC core, nvmem registration through RTC, sysfs attribute groups, optional Common Clock Framework provider, device properties `trickle-resistor-ohms` and `aux-voltage-chargeable`, and ACPI/OF IDs.

Risks and test signals: EEPROM paths must always restore EERD state after errors. Alarm enable depends on RTC core `uie_rtctimer` and `aie_timer` state. `devm_rtc_nvmem_register()` return values are ignored. Test PORF rejection/clear, alarm rounding to minute, IRQ flag clearing, timestamp count/reset, backup switch modes, offset clamp, EEPROM busy timeouts, trickle property validation, clkout rate/prepare/unprepare, and operation without IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3028.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3029c2.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3029c2.c

Purpose: implements Micro Crystal RV3029 and RV3049 RTC support over I2C and SPI, including time, alarm, battery-backed RAM, EEPROM-controlled trickle charging, and optional hwmon temperature reporting.

Important APIs/types/functions: `struct rv3029_data` stores device, RTC, regmap, and IRQ. EEPROM helpers `rv3029_eeprom_enter()`, `rv3029_eeprom_exit()`, `rv3029_eeprom_busywait()`, `rv3029_eeprom_read/write()`, and `rv3029_eeprom_update_bits()` guard nonvolatile access. `rv3029_probe()` is bus-neutral, while `rv3029_i2c_probe()` and `rv3049_probe()` provide regmaps. RTC ops cover time, alarm, alarm IRQ enable, and voltage ioctl.

Control flow: bus probe initializes the regmap with inaccessible holes, then common probe applies trickle charger configuration, registers hwmon when configured, allocates the RTC, requests an optional alarm IRQ, sets the 2000-2079 range, registers the RTC, and exposes 8 bytes of battery-backed RAM. Time reads reject VLOW2 or PON, then decode the watch section, including 12-hour mode. Set-time writes the watch section and clears PON/VLOW2. Alarm IRQ handling reads IRQ control/flags under `rtc_lock`, reports AF, disables AIE, and writes updated flags/control.

State and persistence: time, alarm, IRQ flags, trickle charger bits, temperature configuration, and RAM live in hardware. EEPROM refresh is disabled during direct EEPROM access and re-enabled afterward; low-voltage bits gate safe EEPROM access.

Dependencies and integration points: depends on I2C or SPI regmap, RTC core, optional `CONFIG_RTC_DRV_RV3029_HWMON`, OF trickle-resistor property, nvmem, BCD helpers, and both I2C and SPI module registration.

Risks and test signals: trickle configuration selects the first table resistance greater than or equal to the requested value and can dereference past the table if a too-large value is provided. EEPROM reads/writes must not proceed under VLOW2 or persistent VLOW1. Test both bus frontends, inaccessible regmap ranges, low-voltage paths, 12/24-hour decoding, full-date alarm programming, IRQ disable-after-alarm, nvmem, hwmon temperature/update interval, and SPI registration rollback if I2C/SPI init partially fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3029c2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3032.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3032.c

Purpose: implements the Micro Crystal RV3032 I2C RTC with minute-resolution alarms, offset calibration, EEPROM and NVRAM access, backup switching, trickle charger configuration, optional clock output, and hwmon temperature input.

Important APIs/types/functions: `struct rv3032_data` stores regmap, RTC, trickle state, and optional clkout hardware. `rv3032_enter_eerd()`, `rv3032_exit_eerd()`, and `rv3032_update_cfg()` manage EEPROM update mode. RTC ops include time, alarm, alarm IRQ enable, offset, voltage ioctl, and backup-switch params. Nvmem callbacks expose 16 RAM bytes and 32 user EEPROM bytes.

Control flow: probe creates the regmap, reads status, allocates the RTC, optionally requests IRQ, configures trickle charging from properties, sets backup switch and minute-alarm feature bits, registers the RTC/nvmem devices, optionally registers clkout, and registers hwmon. Time reads reject PORF or VLF, bulk-read BCD time, and decode to 2000-2099. Alarm operations program minute/hour/day, clear AF/UF, and combine AIE/UIE based on RTC core timers. IRQ handling reports PF/AF/UF, clears corresponding status flags, and disables matching interrupt enables.

State and persistence: persistent hardware state includes time, alarms, flags, PMU backup/trickle bits, offset, EEPROM user area, RAM, and clock-output configuration. Driver state prevents backup-switch mode changes after trickle charger setup because those PMU fields overlap.

Dependencies and integration points: depends on I2C regmap, RTC nvmem helpers, optional Common Clock Framework, hwmon, device properties `trickle-resistor-ohms` and `trickle-voltage-millivolt`, ACPI/OF IDs, and RTC backup-switch params.

Risks and test signals: EEPROM entry/exit must be restored across all error paths. `devm_rtc_nvmem_register()`, clkout registration, and hwmon registration errors are mostly ignored. `hwmon_info` advertises max/hyst fields that are not readable in the read callback. Test PORF/VLF rejection and clear, alarm IRQ paths with/without IRQ, offset clamping, backup-switch rejection when trickle is active, trickle property matrix, EEPROM busy timeouts, clkout low/high-frequency rates, and stable two-sample temperature reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3032.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv8803.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv8803.c

Purpose: implements Micro Crystal RV8803 and Epson RX8803/RX8804/RX8900 I2C RTCs with time, minute-resolution alarms, voltage status, one-byte NVRAM, wake IRQ support, and RX8900 backup/trickle options.

Important APIs/types/functions: `struct rv8803_data` stores client, RTC, `flags_lock`, cached control register, RX8900 backup options, alarm corruption flag, and chip type. Transfer wrappers `rv8803_read_reg()`, `rv8803_read_regs()`, `rv8803_write_reg()`, and `rv8803_write_regs()` retry around the chip's documented no-ACK window. `rv8803_regs_init()`, `rv8803_regs_reset()`, and `rv8803_regs_configure()` initialize variant-specific registers.

Control flow: probe checks SMBus functionality, reads and warns about voltage/alarm flags, allocates the RTC, requests optional threaded IRQ and wake IRQ, applies RX8900 DT properties, configures WADA and backup control, registers the RTC, and registers 1-byte nvmem. Reads reject alarm-corruption state and V2F, perform a second time read around second 59, and decode BCD. Set-time stops the clock, writes BCD fields, restarts, and clears voltage flags after possible register reset. Alarm set disables AIE/UIE, clears AF, writes minute/hour/day, and re-enables selected interrupts.

State and persistence: hardware keeps time, alarm, flags, control bits, RAM, oscillator offset, and RX8900 backup flags. Driver state caches `ctrl` to coordinate alarm/update interrupt enables and marks invalid alarm registers as data-risk state.

Dependencies and integration points: depends on I2C SMBus block/byte operations, RTC core, nvmem, PM wake IRQ helpers, OF/I2C IDs, and optional wakeup-source property.

Risks and test signals: cached control state must stay synchronized with hardware writes. Invalid BCD alarm values force future time reads to fail until reset through set-time. Test no-ACK retry behavior, V1F/V2F ioctls, alarm invalidation/reset, IRQ flag clearing under mutex, wakeup-source without IRQ, RX8900 `epson,vdet-disable` and `trickle-diode-disable`, suspend/resume wake enable, and nvmem byte access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv8803.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx4581.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx4581.c

Purpose: implements a simple SPI RTC class driver for the Epson RX4581, exposing time read/write only.

Important APIs/types/functions: `rx4581_set_reg()` and `rx4581_get_reg()` implement the SPI register protocol, where read uses the MSB and write uses the low nibble address. `rx4581_get_datetime()` reads a stable time snapshot, and `rx4581_set_datetime()` writes BCD time after stopping the clock. RTC ops expose `read_time` and `set_time`.

Control flow: probe verifies a basic register read, registers the RTC, and stores the RTC pointer as SPI driver data. Read-time checks and clears the update flag, bulk-reads seven time registers, repeats if UF becomes set during the read, warns on low-voltage flag, and decodes BCD fields with a 1970-2069 century heuristic. Set-time builds an 8-byte write buffer, sets STOP, writes time registers, clears VLF, and clears STOP.

State and persistence: hardware persists BCD time, flag register bits, control STOP/RESET bits, RAM, alarm, and timer registers, though this driver uses only time, flags, and STOP. Driver state is only the devm RTC device.

Dependencies and integration points: depends on SPI core, RTC core, BCD helpers, and SPI device ID `rx4581`. It has no OF table, alarm support, IRQ handling, voltage ioctl, or nvmem registration.

Risks and test signals: VLF is logged but read-time still returns success, so consumers may accept unreliable time. If the bulk write fails after STOP is set, the clock may remain stopped. The day-of-week decode uses `ilog2()` and assumes a valid one-hot register. Test SPI mode/speed expected by board data, UF retry loop, VLF read/set-time clear, STOP recovery after failures, year rollover around 2069/2070, and invalid weekday encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx4581.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx6110.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx6110.c

Purpose: implements the Epson RX-6110 SA RTC over either SPI or I2C using a shared regmap-backed core, exposing time read/write and basic initialization/status handling.

Important APIs/types/functions: `struct rx6110_data` stores the RTC and regmap. `rx6110_rtc_tm_to_data()` and `rx6110_data_to_rtc_tm()` convert between `rtc_time` and native BCD/one-hot weekday format. `rx6110_set_time()`, `rx6110_get_time()`, and `rx6110_init()` implement RTC operations and startup configuration. Separate SPI/I2C probe functions allocate regmaps and call common `rx6110_probe()`.

Control flow: module init registers SPI first and I2C second, unwinding SPI if I2C registration fails. Probe allocates bus-specific state, initializes regmap, registers the RTC, and applies defaults: disables timer enable, writes reserved/IRQ/alarm default registers, warns on VLF/AF/TF/UF, and clears non-VLF flags. Reads reject VLF, bulk-read seven time registers, decode BCD, and enforce year 2000-2099. Writes set STOP, bulk-write time, clear VLF, and clear STOP.

State and persistence: hardware stores time, alarm/timer registers, extension/control/flag bits, user bytes, and IRQ register. The driver persists no local state beyond the regmap and RTC pointer and does not expose alarm/timer/user RAM functions.

Dependencies and integration points: depends on regmap over SPI or I2C, RTC core, ACPI I2C ID `SECC6110`, OF SPI compatible `epson,rx6110`, I2C/SPI IDs, and board-provided SPI mode constraints.

Risks and test signals: `rx6110_data_to_rtc_tm()` sets `tm_wday = ffs(mask)` without subtracting one, unlike most RTC drivers. SPI mode mismatches only warn and continue. I2C regmap also sets `read_flag_mask = 0x80`, which should be validated against bus protocol. Test both buses, VLF rejection/clear, STOP bit failure recovery, weekday encoding, reserved register patching, alarm flag warning/clear, and init rollback between SPI/I2C registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx6110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8010.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8010.c

Purpose: implements the Epson RX-8010SJ I2C RTC with time, alarm, update/periodic/alarm interrupt reporting, voltage-low ioctl, and reserved-register initialization.

Important APIs/types/functions: `struct rx8010_data` stores the regmap, RTC, and cached control register. `rx8010_init()` initializes reserved registers, clears stale flags, and caches control state. `rx8010_irq_1_handler()` reports PF/AF/UF events. RTC ops cover time, alarm, alarm IRQ enable, and `RTC_VL_READ`.

Control flow: probe allocates state, initializes I2C regmap, runs hardware init, allocates RTC, requests optional IRQ, clears alarm feature when IRQ is absent, sets range 2000-2099, and registers. Time reads reject VLF and decode seven BCD registers. Set-time sets STOP, writes time, clears STOP, and clears VLF. Alarm programming disables AIE/UIE from the cached control byte, clears AF, writes minute/hour, configures day-of-month matching by clearing WADA, writes day or AE wildcard, and re-enables AIE/UIE based on RTC core timers.

State and persistence: time, alarm, flags, extension, control, timer, and reserved registers live in hardware. The cached `ctrlreg` mirrors control bits and is used to avoid read-modify-write drift during alarm operations.

Dependencies and integration points: depends on I2C regmap, RTC core, OF/I2C IDs, optional IRQ from firmware, and RTC UIE/AIE timer state.

Risks and test signals: no explicit I2C functionality check is done before regmap creation. `tm_wday` read uses `ffs()` without subtracting one. `set_alarm()` bulk-writes only two bytes initially, then writes the day register separately, so partial failures can leave mixed alarm state. Test reserved-register initialization, VLF read/set/clear, IRQ flag clearing, alarm with day wildcard, UIE/AIE combination, missing IRQ feature clearing, and weekday interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8025.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8025.c

Purpose: implements Epson RX8025 and RX8035 I2C RTCs with time, minute-resolution daily alarm, oscillator validity checks, digital offset calibration, IRQ reporting, and a deprecated sysfs clock-adjust alias.

Important APIs/types/functions: `struct rx8025_data` stores the RTC, model, cached `ctrl1`, and 24-hour mode. SMBus helpers read/write single or block registers using the chip's shifted register address format. `rx8025_check_validity()`, `rx8025_reset_validity()`, `rx8025_init_client()`, `rx8025_read_offset()`, and `rx8025_set_offset()` handle status and calibration. RTC ops cover time, alarm, alarm IRQ enable, and offset.

Control flow: probe checks SMBus capabilities, identifies model, initializes control/status, allocates RTC, requests optional IRQ, sets minute-alarm feature and clears update-interrupt feature, adds sysfs `clock_adjust_ppb`, and registers. Reads reject PON or stopped oscillator, with opposite XST polarity for RX8025 versus RX8035, then decode BCD. Set-time writes BCD fields and clears validity flags. Alarm operations program minute/hour only and toggle `DALE` in cached control state.

State and persistence: hardware stores time, alarms, control/status flags, digital offset, and alarm enable bits. Driver state caches `ctrl1` and hour mode derived from control or RX8035 hour register.

Dependencies and integration points: depends on I2C SMBus byte/block access, RTC core, sysfs attribute group, BCD helpers, and I2C IDs. It has no OF match table in this file.

Risks and test signals: IRQ handler appears to clear `DAFG` by assigning `status &= RX8025_BIT_CTRL2_DAFG`, which can leave only the alarm bit rather than clearing it. Year range is set to 1900-2099 while set-time subtracts 100. Test RX8025/RX8035 XST polarity, 12/24-hour conversion, alarm IRQ flag clearing, offset saturation and deprecated sysfs sign inversion, PON/VDET reset, missing IRQ behavior, and writes of read-only bits noted in comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8025.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8111.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8111.c

Purpose: implements a minimal Epson RX8111 I2C RTC driver exposing time read/write and voltage-low reporting, while defining register fields for broader chip functionality.

Important APIs/types/functions: `struct rx8111_data` stores regmap, an array of allocated `regmap_field` objects, device, and RTC pointer. `rx8111_regfields[]` maps extension, flag, control, power-switch, and status bits. `rx8111_read_time()`, `rx8111_set_time()`, `rx8111_ioctl()`, and `rx8111_read_vl_flag()` implement the current RTC surface.

Control flow: probe allocates state, initializes I2C regmap, allocates all regmap fields, allocates an RTC, sets 2000-2099 range, clears alarm feature, and registers. Read-time checks XST, VLF, and STOP before bulk-reading seven BCD time registers. Set-time clears XST/VLF, sets STOP, bulk-writes the time, then clears STOP. Voltage ioctl reports `RTC_VL_DATA_INVALID` from VLF and `RTC_VL_BACKUP_LOW` from the VLOW status monitor.

State and persistence: hardware keeps time, alarms, timer, timestamp, power-switch, flag, and status registers. The driver currently persists no local runtime state beyond regmap/regfields and does not expose alarms, IRQs, timestamps, power-switch configuration, or nvmem.

Dependencies and integration points: depends on I2C regmap, regmap fields, RTC core, OF compatible `epson,rx8111`, BCD helpers, and userspace `RTC_VL_READ`.

Risks and test signals: probe uses `devm_kmalloc()` rather than zeroed allocation, leaving unused members such as `data->rtc` uninitialized. If set-time fails after STOP is set, the driver intentionally leaves the clock stopped and future reads fail until a successful set-time. `FIELD_GET()` is used with single-bit masks on a raw flag value; current definitions work but are unusual. Test XST/VLF/STOP rejection, VLOW ioctl composition, set-time failure recovery, invalid weekday masks, all regmap_field allocations, and alarm feature absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8581.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8581.c

Purpose: implements Epson RX8571/RX8581 I2C RTC support with time read/write and battery-backed nvmem exposure.

Important APIs/types/functions: `struct rx85x1_config` selects regmap range and number of nvmem regions for RX8581 or RX8571. `rx8581_rtc_read_time()` and `rx8581_rtc_set_time()` implement RTC ops. Nvmem callbacks expose one RAM byte for RX8581-like chips and an additional 16-byte user RAM region for RX8571.

Control flow: probe selects OF match data when present, initializes I2C regmap, stores it as client data, allocates an RTC, sets ops/range/start-time behavior, registers the RTC, and registers configured nvmem regions. Read-time checks VLF, clears and waits out UF by repeating time reads until the update flag stays clear, then decodes BCD fields. Set-time builds BCD time data, sets STOP, writes time registers, clears VLF, and clears STOP.

State and persistence: hardware stores BCD time, flag/control bits, one RAM byte, and for RX8571 a larger user RAM window. Driver state is the selected immutable config and regmap.

Dependencies and integration points: depends on I2C regmap, RTC core, OF compatibles `epson,rx8571` and `epson,rx8581`, I2C ID `rx8581`, nvmem registration, and BCD/ilog2 helpers.

Risks and test signals: `devm_rtc_nvmem_register()` results are ignored. If set-time fails after STOP, the clock can remain stopped. `ilog2()` assumes a valid nonzero one-hot weekday. The loop clearing UF can spin if hardware keeps setting UF. Test RX8571 versus RX8581 nvmem sizes, VLF rejection and clear, UF retry behavior, STOP failure recovery, RTC start-time initialization, invalid weekday encodings, and OF match data fallback to RX8581 config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8581.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rzn1.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rzn1.c

Purpose: implements the Renesas RZ/N1 MMIO RTC with calendar time, week-based alarms, optional one-second alarm refinement, runtime PM, and oscillator offset support when using the standard 32.768 kHz mode.

Important APIs/types/functions: `struct rzn1_rtc` stores the RTC device, MMIO base, spinlock for CTL1 interrupt bits, and cached alarm time. `rzn1_rtc_get_time_snapshot()`, `rzn1_rtc_read_time()`, `rzn1_rtc_set_time()`, `rzn1_rtc_alarm_irq_enable()`, `rzn1_rtc_read_alarm()`, `rzn1_rtc_set_alarm()`, `rzn1_rtc_read_offset()`, and `rzn1_rtc_set_offset()` implement behavior. Ops are split between SUBU offset-capable mode and SCMP external-rate mode.

Control flow: probe maps registers, gets alarm IRQ, enables runtime PM, optionally reads an `xtal` clock, disables the controller, selects SCMP mode if the xtal is valid but not 32768 Hz, programs SCMP or SUBU mode, enables the controller, disables interrupts, requests alarm IRQ, optionally requests PPS IRQ, then registers the RTC. Time reads reject stopped counters and re-snapshot on second mismatch. Set-time waits for stop acknowledgement, writes BCD packed time/calendar registers, and restarts. Alarm enable chooses minute alarm or one-second interrupt depending on how close the target second is.

State and persistence: hardware persists time/calendar, control mode, alarm minute/hour/weekday, second compare, and offset/subtraction registers. The exact requested alarm timestamp is cached in RAM for second-level handling.

Dependencies and integration points: depends on platform MMIO, named IRQs `alarm` and optional `pps`, optional clock `xtal`, runtime PM, RTC core, BCD helpers, and OF compatible `renesas,rzn1-rtc`.

Risks and test signals: alarms cannot be set more than one week ahead and `days_ahead = tm_mday - now_mday` is fragile across month boundaries. Second-precision alarms degrade to minute precision without PPS IRQ. Offset writes with zero steps return without clearing previous offset. Test SCMP/SUBU selection, non-32768 xtal rates, stopped-counter reads, month-boundary alarms, PPS-present and PPS-absent behavior, CTL1 spinlock protection, runtime PM remove path, and offset range/update-busy timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rzn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s32g.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s32g.c

Purpose: implements the NXP S32G2/S32G3 RTC alarm/wakeup block as an RTC class device. It does not maintain calendar time in hardware; it derives read_time from system real time plus accumulated sleep seconds and uses the hardware API counter for alarms.

Important APIs/types/functions: `struct rtc_priv` stores RTC device, MMIO base, IPG and selected source clocks, SoC data, computed RTC frequency, accumulated `sleep_sec`, IRQ, and selected clock source index. `rtc_soc_data` defines clock divisor and reserved clock sources. Core functions are `rtc_clk_dts_setup()`, `rtc_clk_src_setup()`, `s32g_rtc_set_alarm()`, `s32g_rtc_read_time()`, suspend/resume hooks, and `s32g_rtc_handler()`.

Control flow: probe maps registers, enables wakeup, gets `ipg` and the first usable source clock, allocates RTC, configures source/dividers with counter disabled, computes effective RTC Hz, requests the alarm IRQ, and registers. Alarm set converts requested wall time to a positive offset from current real time minus accumulated sleep, bounds it by 32-bit APIVAL cycles, waits for API synchronization, and writes APIVAL. IRQ clears APIVAL/status and reports AF. Suspend adds remaining APIVAL-derived seconds to `sleep_sec`; resume reconfigures registers because suspend-to-RAM may reset them.

State and persistence: APIVAL, RTCC, RTCS, clock source/divider, and accumulated software `sleep_sec` drive behavior. No set_time op exists, and calendar state is not persisted in the RTC block.

Dependencies and integration points: depends on platform MMIO, OF match `nxp,s32g2-rtc`, named clocks `ipg` and `source0..source3`, RTC core, system time via `ktime_get_real_seconds()`, and PM sleep callbacks.

Risks and test signals: `rtc_clk_dts_setup()` returns `-EOPNOTSUPP` immediately when it sees a reserved source index, which prevents trying later valid sources. `alarm_irq_enable()` ignores its `enabled` argument and always enables API interrupt bits. Test clock-source selection, reserved source handling, divider math, APIVAL overflow/range, synchronization timeout, suspend/resume accumulation, system-time jumps, IRQ clear/report, and wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s32g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s35390a.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s35390a.c

Purpose: implements the Seiko Instruments S-35390A I2C RTC with time, minute-resolution alarm through INT2, voltage/reset status ioctl, and one-byte battery-backed nvmem.

Important APIs/types/functions: `struct s35390a` holds eight I2C client addresses and 12/24-hour mode. `s35390a_set_reg()` and `s35390a_get_reg()` access command-specific dummy I2C addresses. `s35390a_init()`, `s35390a_read_status()`, `s35390a_disable_test_mode()`, `s35390a_hr2reg()`, and `s35390a_reg2hr()` handle startup/status/encoding. RTC ops cover time, alarm, voltage ioctl, and nvmem callbacks access the free register.

Control flow: probe checks raw I2C capability, creates dummy clients for addresses `addr+1` through `addr+7`, allocates RTC, reads status, determines 24-hour mode, disables alarm or test mode, marks wake capability, sets feature bits, registers nvmem, and registers the RTC. Read-status returns reset-needed when POC or BLD is seen; POC also sleeps 500 ms. Time read rejects reset-needed state, reads TIME1, bit-reverses each byte, and decodes BCD. Time set reinitializes if needed, encodes BCD, bit-reverses bytes, and writes TIME1.

State and persistence: hardware persists time, status bits, test/alarm mode, INT2 alarm registers, and one free register. POC/BLD status is destructive-on-read, so probe/init may clear the only evidence of invalid time.

Dependencies and integration points: depends on I2C adapters supporting raw transfers and dummy devices, RTC core, bit-reversal helpers, nvmem, OF/I2C IDs, and wakeup-capable device integration.

Risks and test signals: no IRQ is requested despite INT2 alarm setup; pending alarm at probe is reported with `rtc_update_irq()` only if status says INT2. Alarm register access is unavailable when alarm mode is disabled. The code adds an extra PM bit in `s35390a_rtc_set_alarm()` even though `s35390a_hr2reg()` already handles PM. Test multi-address reservation, POC/BLD reset retries, bit-reversed time/alarm encoding, 12/24-hour alarm conversion, voltage ioctl semantics, nvmem free byte, test-mode clear, and alarm enable/read when INT2 mode is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s35390a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.c

Purpose: implements the Samsung S3C6410/Exynos3250 internal MMIO RTC with time, alarm, wakeup, SoC-specific enable/disable hooks, and clock-gated register access.

Important APIs/types/functions: `struct s3c_rtc` stores device/RTC pointers, MMIO base, RTC and source clocks, alarm state, SoC data, alarm IRQ, spinlock, and wake flag. `struct s3c_rtc_data` supplies per-compatible clock needs and callbacks. Core functions include `s3c_rtc_enable_clk()`, `s3c_rtc_disable_clk()`, `s3c_rtc_setaie()`, `s3c_rtc_read_time()`, `s3c_rtc_write_time()`, `s3c_rtc_getalarm()`, `s3c_rtc_setalarm()`, `s3c6410_rtc_enable()`, `s3c6410_rtc_disable()`, and PM callbacks.

Control flow: probe reads match data, gets alarm IRQ and MMIO resource, prepares/enables required clocks, disables bootloader RTC bits, re-enables/normalizes RTCCON, initializes wakeup, allocates/registers RTC, requests alarm IRQ, then gates clocks off. Time reads enable clocks, read BCD fields, retry once if seconds are zero to avoid mid-update reads, convert to 2000-2099, and disable clocks. Alarm set writes only valid fields, builds enable bits, and calls `s3c_rtc_setaie()`. Suspend disables RTC hardware and optionally enables IRQ wake; resume re-enables hardware and disables wake.

State and persistence: hardware persists BCD time, alarm registers, RTCCON, RTCALM, and interrupt-pending bits. Driver state tracks whether alarm IRQ enable is holding an extra clock reference so alarms can fire while normal access is gated.

Dependencies and integration points: depends on platform MMIO, Samsung register definitions from `rtc-s3c.h`, clocks `rtc` and `rtc_src`, RTC core, IRQ wake support, OF compatibles `samsung,s3c6410-rtc` and `samsung,exynos3250-rtc`.

Risks and test signals: `s3c_rtc_setaie()` manipulates clock references in nested ways and must balance normal access with alarm-held clocks. The driver explicitly does not support pre-2000 dates. Alarm year is read but never set in `s3c_rtc_setalarm()`. Test clock prepare/enable unwind, alarm enable/disable clock balance, seconds-zero retry, partial alarm masks, suspend/resume wake, RTCCON cleanup, IRQ pending clear, and invalid date range behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.h -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.h

Purpose: defines the Samsung S3C2410-family RTC register offsets and bit masks consumed by `rtc-s3c.c`.

Important APIs/types/functions: the header provides the `S3C2410_RTCREG(x)` identity macro, interrupt pending register `S3C2410_INTP`, RTCCON bits (`RTCEN`, `CNTSEL`, `CLKRST`, `TICSEL`, `TICEN`), alarm control bits in `S3C2410_RTCALM`, alarm field offsets, and time field offsets. It has no functions or types.

Control flow: there is no runtime control flow in the header. Its constants define how the driver reads/writes MMIO registers for time, alarm, interrupt acknowledgement, and RTC controller normalization.

State and persistence: the definitions map to persistent SoC RTC hardware registers. `S3C2410_RTCALM_*EN` masks indicate which alarm fields participate in matching, and `S3C2410_INTP_ALM`/`TIC` bits identify interrupt sources to clear.

Dependencies and integration points: included directly by `rtc-s3c.c`; protected by `__ASM_ARCH_REGS_RTC_H`. The values are part of the driver ABI with Samsung S3C-compatible RTC register layouts.

Risks and test signals: incorrect offsets or masks would corrupt calendar or alarm programming across every supported S3C-compatible SoC. Because `S3C2410_RTCREG(x)` is an identity macro, all offset interpretation relies on the MMIO resource already being mapped at the RTC register base. Validate against SoC reference manuals, alarm IRQ clear behavior, RTCCON enable/disable bits, and all time/alarm register offsets used by the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s5m.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s5m.c

Purpose: implements Samsung S5M8767, S2MPG10, S2MPS13, S2MPS14, and S2MPS15 PMIC RTC subdrivers, including time, alarm, alarm IRQ wake, UDR synchronization, and an S2MPG10 restart handler.

Important APIs/types/functions: `struct s5m_rtc_reg_config` abstracts per-chip register layout and UDR masks. `struct s5m_rtc_info` stores parent PMIC, regmap, RTC, IRQ, device type, 24-hour mode, and selected config. Conversion helpers `s5m8767_data_to_tm()` and `s5m8767_tm_to_data()` handle binary-format RTC data. Update helpers `s5m8767_wait_for_udr_update()`, `s5m8767_rtc_set_time_reg()`, and `s5m8767_rtc_set_alarm_reg()` synchronize hardware transfers. RTC ops cover time, alarm, and alarm IRQ enable.

Control flow: probe gets the PMIC RTC regmap or creates a dummy I2C client/regmap for older PMICs, selects the register config, obtains optional alarm IRQ, initializes PMIC RTC control to binary 24-hour mode, allocates the RTC, requests threaded alarm IRQ and wakeup if present, optionally registers an S2MPG10 sys-off restart handler, and registers the RTC. Reads optionally trigger RUDR, bulk-read time, and convert fields. Writes raw time/alarm data, set WUDR/AUDR/RUDR masks as required per chip, and wait for auto-clear. Alarm enable sets or clears `ALARM_ENABLE_MASK` bits across active alarm fields.

State and persistence: PMIC RTC registers persist time, alarm fields, enable bits, UDR transfer state, status bits, and watchdog/restart controls. Driver state records chip-specific UDR behavior, because some bits auto-clear and S2MPS13 AUDR must be manually cleared.

Dependencies and integration points: depends on Samsung MFD core/regmap, platform device IDs, parent PMIC status regmap for pending alarms, optional named IRQ `alarm`, RTC core, PM sleep wake IRQs, and sys-off restart registration for S2MPG10 power-controller systems.

Risks and test signals: UDR masks differ subtly across devices; a wrong config can make time/alarm writes silently not transfer. `s5m8767_wait_for_udr_update()` returns the last regmap status even when retries expire, only logging an error. Weekday uses `ffs()` without subtracting one. Test every device type, dummy RTC I2C creation, regmap-from-parent path, WUDR/RUDR/AUDR sequencing, S2MPS13 manual AUDR clear, pending-alarm status source, IRQ absent feature clearing, suspend/resume wake, and S2MPG10 restart watchdog arming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s5m.c -->
