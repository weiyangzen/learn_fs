# subset-b-005201 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2127.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2127.c

Purpose: implements the NXP PCF2127/PCF2129/PCA2129/PCF2131 RTC family across both I2C and SPI transports. Beyond basic RTC time and alarm support, it exposes backup-voltage ioctls, backup-switch parameters, PCF2127 SRAM through nvmem, tamper timestamp sysfs attributes, and an optional watchdog when the device is declared as a reset source.

Important APIs/types/functions: `struct pcf21xx_config` captures variant register layout and capabilities; `struct pcf2127` stores the RTC, watchdog, regmap, variant config, IRQ state, and cached timestamp values. `pcf2127_rtc_read_time()` and `pcf2127_rtc_set_time()` convert seven BCD date/time registers and handle the PCF2131 STOP/CPR write sequence. `pcf2127_rtc_read_alarm()`, `pcf2127_rtc_set_alarm()`, and `pcf2127_rtc_alarm_irq_enable()` manage the day-resolution alarm. `pcf2127_rtc_irq()` fans out alarm, watchdog, minute/second, and timestamp flags. `pcf2127_watchdog_init()` registers the watchdog, `pcf2127_nvmem_read/write()` expose 512 bytes of PCF2127 SRAM, and `timestamp[0-3]_{show,store}` provide tamper timestamps. `pcf2127_i2c_probe()` and `pcf2127_spi_probe()` build variant-specific regmaps before entering common `pcf2127_probe()`.

Control flow: module init registers I2C first and SPI second, rolling back I2C if SPI registration fails. Probe allocates an RTC, sets the 2000-2099 range, requests an alarm IRQ when present, enables wakeup and alarm features as allowed, configures PCF2131 interrupt routing, registers PCF2127 nvmem, disables POR override, programs CLKOUT OTP refresh, sets watchdog clock/control bits, initializes the watchdog, clears battery timestamp interrupts, enables each supported timestamp input, adds timestamp sysfs attributes, then registers the RTC. Time reads avoid `CTRL2` because reading it resets the watchdog value; every path that must read `CTRL2` pings an active watchdog afterward.

State and persistence: RTC time, alarm, battery flags, backup-switch mode, watchdog countdown, and timestamp flags live in chip registers. PCF2127 SRAM is battery-backed and persistent. Driver state caches tamper timestamps only when an IRQ is available, so userspace must clear sysfs validity to accept new events. The watchdog is only active when configured by firmware with `reset-source`; the driver detects an already-running watchdog only on variants whose watchdog value register is readable.

Dependencies and integration: integrates with the RTC core, regmap, I2C, SPI, OF matching, optional watchdog core, nvmem registration through RTC, sysfs attributes, and wakeup IRQ handling. Device tree controls compatible matching, IRQ trigger handling, wakeup behavior, and reset-source watchdog registration.

Risks: reading `CTRL2` has a side effect that stops the watchdog, so any future status path must preserve the active-ping pattern. PCF2131 writes require STOP and CPR sequencing; failures can leave STOP set if later cleanup is not considered. Timestamp sysfs silently returns empty output for invalid timestamps and returns 0 for out-of-range timestamp IDs, which can hide configuration mismatch. The I2C probe mutates a static `regmap_config`, so simultaneous probe of different variants would rely on probe serialization. Test signals include I2C and SPI probe for each variant, OSF invalid-time handling, alarm IRQ and wakeup behavior, watchdog start/stop/timeout, nvmem read/write on PCF2127 only, tamper timestamp capture with and without IRQ, and `RTC_VL_READ/CLR` plus backup-switch `rtc_param` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85063.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85063.c

Purpose: supports the PCF85063/PCA85073A/PCF85063A/PCF85063TP and Micro Crystal RV8263/RV8063 RTC family over I2C or SPI. It provides timekeeping, optional alarms, oscillator offset correction, one-byte battery-backed RAM through nvmem, and optional clkout registration.

Important APIs/types/functions: `struct pcf85063_config` describes the regmap and alarm/capacitance quirks. `pcf85063_rtc_read_time()` bulk-reads the time registers and rejects oscillator-stop data; `pcf85063_rtc_set_time()` stops the divider, writes all time registers, and restarts it. `pcf85063_rtc_read_alarm()`, `pcf85063_rtc_set_alarm()`, `pcf85063_rtc_alarm_irq_enable()`, and `pcf85063_rtc_handle_irq()` implement alarm support for variants with alarm registers. `pcf85063_read_offset()` and `pcf85063_set_offset()` expose RTC offset calibration. `pcf85063_nvmem_read/write()` map the single RAM byte. `pcf85063_clkout_*()` implements common-clock operations when enabled.

Control flow: common probe verifies chip presence by reading seconds, allocates the RTC, performs a software reset after power-loss detection, programs quartz load capacitance from `quartz-load-femtofarads` or variant defaults, sets feature bits, requests an IRQ only for alarm-capable variants, registers the nvmem byte, optionally registers clkout, and registers the RTC. I2C and SPI front ends only select the proper config and initialize the regmap.

State and persistence: the chip stores BCD time, alarm, offset calibration, alarm flags, clkout state, and one RAM byte. The driver has no durable state beyond chip registers; clkout and wake configuration are runtime kernel registrations. A POR issue triggers software reset but the driver still reports invalid time until userspace sets a new value.

Dependencies and integration: depends on RTC core, regmap, I2C, SPI for RV8063, OF matching, PM wake IRQ, nvmem through RTC, and optionally common clock. Device tree can supply wakeup and clock-output names plus crystal load.

Risks: `pcf85063_rtc_set_alarm()` writes `AF` back set when enabling alarms, relying on chip semantics where writing zero clears flags; this deserves hardware regression coverage. Offset range/rounding has two calibration modes and should be tested at limits. The common clk provider is added without an explicit remove call beyond devm clock lifetime. Test signals include OS invalid time, POR reset path, alarm IRQ clearing, offset read/write round trips, nvmem byte persistence, clkout rates/enable state, and I2C/SPI variant max-register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85063.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8523.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8523.c

Purpose: implements an I2C RTC driver for NXP PCF8523 and Micro Crystal RV8523 devices, including timekeeping, minute-resolution alarms, backup-switch mode reporting/setting, voltage-low reporting, oscillator offset correction, crystal load selection, and wake IRQ support.

Important APIs/types/functions: `struct pcf8523` stores the `rtc_device` and regmap. `pcf8523_rtc_read_time()` reads control and date registers and rejects STOP or oscillator-stop state; `pcf8523_rtc_set_time()` stops the clock, overwrites the OS bit while writing BCD time, and restarts. `pcf8523_rtc_read_alarm()`, `pcf8523_rtc_set_alarm()`, and `pcf8523_irq_enable()` handle minute/day alarm registers. `pcf8523_param_get/set()` map RTC backup-switch modes to `CONTROL3.PM`. `pcf8523_rtc_ioctl()` reports backup-low and invalid-time flags. `pcf8523_rtc_read_offset/set_offset()` implement two-mode offset calibration.

Control flow: probe checks I2C capability, allocates regmap and RTC, loads crystal capacitance from firmware, handles standby mode after oscillator stop, sets RTC operations and feature flags, configures timer/clockout control if an IRQ exists, requests a shared threaded IRQ, enables wake IRQ, marks the device wake capable when IRQ or `wakeup-source` is present, and registers the RTC.

State and persistence: time, alarm, offset, oscillator-stop, battery-low/switch-over, and power-management mode persist in chip registers. The driver keeps only regmap/RTC pointers in memory. Setting time clears the oscillator-stop bit by rewriting seconds.

Dependencies and integration: uses I2C, regmap, RTC class ops, `rtc_param` backup-switch API, PM wake IRQ, OF properties, BCD helpers, and IRQ threading. The alarm feature has minute resolution and no update interrupt.

Risks: the alarm programming buffer is declared as five bytes but only four alarm registers are meaningful, making write length worth checking against device docs. `pcf8523_rtc_set_alarm()` writes `CONTROL2` as zero, clearing more than only AF on future variants. Offset write clamps instead of returning range errors, so callers may not know an exact correction was not representable. Test signals include STOP/OS invalid reads, standby exit on probe, backup-switch mode round trips, IRQ alarm pending/clear behavior, wake suspend/resume, offset extremes, and crystal load defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85363.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85363.c

Purpose: supports NXP PCF85263 and PCF85363 I2C RTCs with BCD timekeeping, alarm 1 on INTA, oscillator load configuration, and one or two RTC-backed nvmem regions depending on the variant.

Important APIs/types/functions: `struct pcf85363` holds the RTC and regmap; `struct pcf85x63_config` selects max register and nvmem count. `pcf85363_rtc_read_time()` and `pcf85363_rtc_set_time()` bulk-read/write date registers, using STOP and CPR reset for writes. `pcf85363_rtc_read_alarm()`, `_pcf85363_rtc_alarm_irq_enable()`, `pcf85363_rtc_set_alarm()`, and `pcf85363_rtc_handle_irq()` implement full date alarm 1. `pcf85363_nvram_read/write()` expose the 64-byte RAM window and `pcf85x63_nvram_read/write()` expose the one-byte RAM register.

Control flow: probe chooses OF variant data or defaults to PCF85363, initializes regmap, allocates the RTC, programs crystal load, sets time range and ops, configures INTA output and clears flags when IRQ or wakeup is desired, requests a threaded low-trigger IRQ if present, sets alarm feature and wakeup capability based on IRQ/wakeup-source, registers the RTC, then registers each available nvmem region.

State and persistence: the hardware keeps time, alarm registers, alarm enable flags, interrupt flags, pin mode, oscillator setting, and battery-backed RAM. Driver state is only pointers to regmap/RTC. Alarm feature availability is dynamic: wakeup-source without a physical IRQ marks RTC alarm supported even though no interrupt handler is installed.

Dependencies and integration: uses I2C, OF match data, regmap, RTC core, devm nvmem registration via RTC, and IRQ threading. Device tree controls compatible variant, wakeup-source, IRQ flags, and quartz load.

Risks: the driver does not check oscillator-stop or validity flags on time reads, so stale time can appear valid after power loss. NVMEM registrations happen after `devm_rtc_register_device()` and their return values are ignored. The IRQ handler uses `i2c_get_clientdata(dev_id)` because it receives the client pointer, so changing the IRQ cookie would break it. Test signals include PCF85263 one-byte nvmem only, PCF85363 RAM window access, INTA alarm IRQ clear, wakeup-source without IRQ behavior, invalid oscillator cases, and STOP/CPR write timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85363.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8563.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8563.c

Purpose: implements the Philips/NXP PCF8563, Epson RTC8564, Micro Crystal RV8564, and PCA8565 I2C RTC driver with time, minute-resolution alarms, voltage-low reporting, optional clkout, and wakeup support.

Important APIs/types/functions: `struct pcf8563` stores the RTC, century polarity heuristic, regmap, and optional clkout. `pcf8563_rtc_read_time()` bulk-reads status/time registers, rejects low-voltage data, and updates `c_polarity`; `pcf8563_rtc_set_time()` writes BCD date/time and century bit using that polarity. `pcf8563_set_alarm_mode()`, `pcf8563_get_alarm_mode()`, `pcf8563_rtc_read_alarm()`, `pcf8563_rtc_set_alarm()`, `pcf8563_irq_enable()`, and `pcf8563_irq()` manage alarm enable/pending flags. `pcf8563_clkout_*()` registers a four-rate common-clock output.

Control flow: probe checks I2C functionality, initializes regmap, sets wake capability, puts the timer into low-frequency mode, clears status/interrupt flags, allocates the RTC, configures minute-resolution alarm and time range, requests a shared threaded alarm IRQ when available, enables alarm feature if IRQ or wakeup-source is present, registers the RTC, then registers clkout when common clock is enabled.

State and persistence: the chip stores BCD time, low-voltage flag, alarm registers, interrupt enables, timer control, and clkout state. The driver's only mutable policy state is `c_polarity`, inferred from the month century bit during reads and used during future writes.

Dependencies and integration: integrates with I2C, regmap, RTC class ops/ioctl, common clock, OF matching, IRQ threading, and wakeup-source. It disables update interrupts because the hardware interface does not provide the RTC core update IRQ feature.

Risks: century bit polarity is heuristic and can be wrong on boards where firmware uses the bit differently. Probe clears ST2 and timer settings unconditionally, which can disturb firmware-programmed modes. The IRQ handler re-enables alarm mode after handling AF, which preserves AIE while clearing AF but needs hardware validation. Test signals include LV invalid-time path, century rollover writes, minute-resolution alarm IRQ, clkout rate/enable operations, wakeup-source with and without IRQ, and RTC8564/PCA8565 compatible matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8563.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8583.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8583.c

Purpose: provides a legacy I2C RTC driver for the PCF8583 RTC/RAM chip. It handles time read/write and uses the chip's RAM area to maintain full year and checksum data because the RTC hardware only stores a two-bit year field.

Important APIs/types/functions: `struct pcf8583` stores the RTC and cached control byte; `struct rtc_mem` describes small RAM transactions. `pcf8583_get_datetime()` reads six BCD time/date bytes with an I2C combined transaction. `pcf8583_set_datetime()` stops the clock through the control register, writes time and optional date bytes, then restores control. `pcf8583_read_mem()` and `pcf8583_write_mem()` access RAM from offset 8 upward. `pcf8583_rtc_read_time()` reconciles the two-bit hardware year with RAM year bytes; `pcf8583_rtc_set_time()` updates the RAM year and checksum.

Control flow: probe checks plain I2C support, allocates per-client state, and registers an RTC with read/set time only. Reads clear STOP/HOLD if set, read hardware time plus RAM year bytes, then derive `tm_year`. Writes program RTC time/date, read checksum and year bytes, adjust checksum for changed year bytes, and write both RAM locations.

State and persistence: the chip stores time in BCD registers, a two-bit year in the day register, and full year/checksum in battery-backed RAM locations `CMOS_YEAR` and `CMOS_CHECKSUM`. The driver's cached control byte is runtime-only and initialized as zero before first use.

Dependencies and integration: uses the I2C core directly rather than regmap, BCD helpers, RTC core, and devm allocation/registration. It has no OF table, IRQ, alarm, or nvmem integration despite using RAM internally.

Risks: cached control state may not reflect hardware after probe, so restoring control can overwrite existing mode bits. RAM checksum handling assumes a preexisting PCF8583 CMOS layout. The hardware year correction is subtle around four-year wraps and century bytes. Test signals include STOP/HOLD recovery, read/write around year modulo-four transitions, RAM checksum preservation, invalid RAM contents, and I2C short transfer error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8583.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pic32.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pic32.c

Purpose: implements the Microchip PIC32MZDA MMIO RTC driver with BCD time read/write, alarm interrupt support, wakeup capability, and clock gating around register access.

Important APIs/types/functions: `struct pic32_rtc_dev` holds the RTC, MMIO base, clock, alarm lock, IRQ, and alarm-clock reference state. `pic32_rtc_gettime()` and `pic32_rtc_settime()` read/write BCD byte registers. `pic32_rtc_getalarm()`, `pic32_rtc_setalarm()`, `pic32_rtc_setaie()`, and `pic32_rtc_alarmirq()` implement alarm controls. `pic32_rtc_setfreq()` configures alarm mask/chime mode, and `pic32_rtc_enable()` unlocks PIC32 syskey and enables/disables the RTC block.

Control flow: probe obtains the alarm IRQ, maps registers, gets/prepares the clock, enables the RTC block, marks wakeup capable, registers an RTC with a 2000-2099 range, configures periodic alarm frequency, requests the IRQ, and disables the clock after setup. Remove disables alarm IRQ and unprepares the clock.

State and persistence: time and alarm registers persist in RTC hardware while power is retained. Driver state tracks whether the clock must remain enabled for an armed alarm through `alarm_clk_enabled`. Alarm programming currently clears the time/date alarm registers rather than writing the requested alarm timestamp.

Dependencies and integration: depends on platform devices, OF compatible `microchip,pic32mzda-rtc`, MMIO accessors, PIC32 platform syskey helpers, common clock, RTC core, and IRQ handling.

Risks: `pic32_rtc_setalarm()` ignores `alrm->time` and writes zero to alarm time/date registers, so requested absolute alarms are not honored. It also calls `pic32_rtc_setaie()` while the clock is already enabled, causing nested enable/disable calls without prepare-count issues but with confusing lifetime. Reads only retry once when seconds equals zero, which may still race updates. Test signals include set/read time, alarm timestamp programming correctness, IRQ delivery and clock gating, probe failure cleanup, and wake from suspend on alarm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pic32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl030.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl030.c

Purpose: supports the ARM AMBA PrimeCell PL030 RTC, a simple 32-bit counter with match alarm and load register.

Important APIs/types/functions: `struct pl030_rtc` stores the MMIO base. `pl030_read_time()` and `pl030_set_time()` convert between seconds counter and `rtc_time`, adding one second on writes because the load register transfers on the next 1 Hz edge. `pl030_read_alarm()` and `pl030_set_alarm()` access the match register. `pl030_interrupt()` acknowledges interrupts through EOI.

Control flow: probe requests AMBA regions, allocates driver and RTC objects, maps registers, disables control and clears pending IRQ, requests the interrupt, registers the RTC, and releases resources manually on errors. Remove disables control, frees IRQ, unmaps registers, and releases AMBA regions.

State and persistence: the hardware counter, match register, and control register contain all persistent RTC state. The driver does not expose alarm IRQ enable in RTC ops and disables `RTC_CR` on probe/remove, so alarm interrupt behavior is minimal.

Dependencies and integration: uses AMBA bus matching by PrimeCell ID, MMIO, RTC core, and interrupt handling. Range maximum is `U32_MAX` seconds.

Risks: the interrupt handler only acknowledges and does not call `rtc_update_irq()`, so alarm events are not reported to userspace. The driver uses non-devm `ioremap()` and `request_irq()` with manual cleanup mixed with devm RTC allocation. Test signals include AMBA region conflicts, read/write counter accuracy with the one-second load adjustment, match register behavior, IRQ acknowledgment, and remove/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl031.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl031.c

Purpose: implements ARM AMBA PL031 RTC support, including original ARM and STMicroelectronics variants. It provides counter timekeeping, alarms, wake IRQ support, ST clockwatch enablement, an ST weekday reset fix, and ST v2 calendar/year-register conversion.

Important APIs/types/functions: `struct pl031_vendor_data` selects variant ops and range; `struct pl031_local` stores vendor data, RTC, and MMIO base. Generic paths are `pl031_read_time()`, `pl031_set_time()`, `pl031_read_alarm()`, `pl031_set_alarm()`, and `pl031_alarm_irq_enable()`. ST v2 paths use `pl031_stv2_tm_to_time()`, `pl031_stv2_time_to_tm()`, `pl031_stv2_read_time()`, and `pl031_stv2_set_alarm()`. `pl031_interrupt()` clears AI and notifies RTC core.

Control flow: probe requests AMBA regions, duplicates the variant ops, maps registers, enables either normal counter or ST clockwatch mode, applies the ST reset weekday correction if needed, initializes wakeup, allocates and registers the RTC, and requests the IRQ with variant flags. Remove frees IRQ and releases AMBA regions.

State and persistence: original variants store seconds in DR/LR/MR. ST v2 stores packed calendar fields in DR/MR plus BCD century/year registers. Interrupt mask/status registers preserve alarm enable/pending state until cleared.

Dependencies and integration: uses AMBA device IDs to select ARM, ST v1, or ST v2 behavior; integrates with RTC core, wake IRQ helpers, MMIO, BCD helpers, and IRQ handling. ST v2 supports year range 0000-9999 while original variants are limited by a 32-bit seconds counter.

Risks: ST v2 weekday must be valid or calculated, and bad weekday handling can reject otherwise valid times. Probe uses `request_irq()` after devm RTC registration, so failure cleanup depends on manual release paths. `pl031_remove()` does not unmap devm mappings, which is fine, but uses manual AMBA release. Test signals include all AMBA IDs, ST reset weekday fix, ST v2 conversion round trips, alarm IRQ enable/clear, wake IRQ behavior, shared IRQ flags, and 32-bit range boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl031.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pm8xxx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pm8xxx.c

Purpose: implements the Qualcomm PM8xxx/PMIC RTC block for several PMIC register layouts. It supports raw 32-bit seconds counters, alarms, wake IRQs, optional direct hardware time setting, and an offset model that persists wall-clock offset in NVMEM or a Qualcomm UEFI variable.

Important APIs/types/functions: `struct pm8xxx_rtc_regs` describes per-PMIC register addresses and alarm enable bits; `struct pm8xxx_rtc` stores regmap, offset storage, policy flags, and RTC state. `pm8xxx_rtc_read_raw()` reads the four-byte counter safely across LSB carry. `__pm8xxx_rtc_set_time()` performs the hardware write sequence when allowed. `pm8xxx_rtc_update_offset()` derives and persists offset when direct set-time is disabled. `pm8xxx_rtc_read_time()` adds offset to raw seconds; `pm8xxx_rtc_set_alarm()` subtracts it before programming hardware. `pm8xxx_alarm_trigger()` reports and clears alarm IRQs.

Control flow: probe matches OF compatible to register layout, obtains parent regmap, optionally gets the alarm IRQ unless `qcom,no-alarm`, reads offset storage when direct set-time is not allowed, enables the RTC, allocates/configures the RTC, requests alarm IRQ and wake IRQ if available, and registers the device. Shutdown flushes small dirty offset changes that were deferred to reduce flash wear.

State and persistence: raw RTC seconds are stored in PMIC registers. The Linux-visible time is raw seconds plus `offset` unless `allow-set-time` programs raw hardware directly. Offset can persist in an NVMEM cell or in EFI variable `RTCInfo`, converted between GPS and Unix offsets. Alarm registers store raw-time alarm seconds.

Dependencies and integration: depends on platform/OF matching, parent PMIC regmap, RTC core, nvmem consumer API, optional EFI variable support, PM wake IRQ, and unaligned little-endian helpers. Compatible data covers PM8921, PM8058, PM8941, and PMK8350 layouts.

Risks: offset arithmetic uses 32-bit seconds and can wrap for far future dates. Dirty offsets under 30 seconds are only persisted at shutdown, so sudden power loss can lose drift correction. EFI variable availability may defer probe, and the write path depends on runtime EFI services. Alarm pending is not surfaced in `read_alarm()`. Test signals include raw carry re-read, direct and offset set-time modes, NVMEM and UEFI offset read/write, dirty-offset shutdown flush, alarm IRQ clear, `qcom,no-alarm`, wake IRQ, and each compatible register map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pm8xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ps3.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ps3.c

Purpose: provides a minimal PlayStation 3 platform RTC backed by the hypervisor RTC value plus an OS-area offset.

Important APIs/types/functions: `read_rtc()` calls `lv1_get_rtc()` and returns the hypervisor RTC value. `ps3_get_time()` reports `read_rtc() + ps3_os_area_get_rtc_diff()`. `ps3_set_time()` stores the requested wall-clock delta through `ps3_os_area_set_rtc_diff()`. `ps3_rtc_probe()` allocates and registers the RTC device.

Control flow: platform probe allocates an RTC, installs read/set ops, sets the maximum range to `U64_MAX`, stores the RTC as platform data, and registers it. There is no interrupt, alarm, suspend/resume, or cleanup-specific logic beyond devm.

State and persistence: the raw RTC is owned by PS3 firmware/hypervisor. Linux persists wall-clock changes as an OS-area difference rather than writing the hypervisor clock itself.

Dependencies and integration: depends on PS3 architecture headers, LV1 hypervisor calls, PS3 OS area helpers, platform device binding, and RTC core.

Risks: `read_rtc()` uses `BUG_ON(result)`, so an unexpected hypervisor failure panics the kernel. No alarm or validity reporting is present. Test signals include successful platform probe, read/set offset round trip, OS-area persistence across reboot, and behavior under hypervisor call failure in architecture-specific tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ps3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pxa.c

Purpose: implements PXA27x/PXA3xx RTC support for the newer calendar registers while also initializing the SA1100-compatible sub-device block. It supports time, alarm 1, proc diagnostics, update/periodic interrupt reporting, and wakeup on alarm.

Important APIs/types/functions: `struct pxa_rtc` embeds `struct sa1100_rtc` and stores MMIO base, RTC, resource, and spinlock. `ryxr_calc()`, `rdxr_calc()`, and `tm_calc()` convert between split year/date and day/time registers. `rtsr_clear_bits()` and `rtsr_set_bits()` preserve trigger bits while updating enables. `pxa_rtc_irq()` reports alarm/update/periodic events. `pxa_rtc_read_time/set_time()` and `pxa_rtc_read_alarm/set_alarm()` implement RTC ops.

Control flow: probe allocates state, reads memory and IRQ resources, maps registers, requests the 1 Hz and alarm IRQs immediately through `pxa_rtc_open()`, wires SA1100 register pointers and calls `sa1100_rtc_init()`, clears interrupt enables, registers a separate `pxa-rtc` device, and marks wakeup capable. Remove frees both IRQs. Suspend/resume toggles wake on the alarm IRQ.

State and persistence: PXA hardware stores calendar time in `RYCR/RDCR`, alarm in `RYAR1/RDAR1`, and interrupt state/enables in `RTSR`. Driver state only protects register updates and keeps SA1100 integration data.

Dependencies and integration: depends on platform resources, OF compatible `marvell,pxa-rtc`, MMIO, RTC core, interrupt handling, proc output, PM sleep, and the local `rtc-sa1100.h` helper.

Risks: `pxa_rtc_open()` return value is ignored in probe, so IRQ request failure may not stop registration. The interrupt handler calls `rtc_update_irq()` even when `events` is zero. Both SA1100 and PXA RTC devices may expose overlapping hardware behavior. Test signals include IRQ request failure, SA1100 init failure, alarm/update/periodic interrupts, proc output, suspend wake, calendar conversion including weekday/month boundaries, and cleanup on probe errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-r7301.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-r7301.c

Purpose: supports Epson Toyocom RTC-7301SF/DG parallel RTCs using MMIO plus regmap. It provides timekeeping and optional alarm IRQ support, with bank switching for normal time, alarm, and timer control banks.

Important APIs/types/functions: `struct rtc7301_priv` stores regmap, IRQ, spinlock, and selected bank. `rtc7301_read/write/update_bits()` abstract 8-bit vs 32-bit register spacing. `rtc7301_select_bank()` changes bank and caches it. `rtc7301_wait_while_busy()`, `rtc7301_stop()`, and `rtc7301_start()` handle update timing. `rtc7301_get_time()` and `rtc7301_write_time()` convert digit registers. `rtc7301_read_time/set_time()`, `rtc7301_read_alarm/set_alarm()`, and `rtc7301_alarm_irq_enable()` implement RTC ops.

Control flow: probe maps MMIO, selects regmap config based on `reg-io-width`, initializes the timer-control bank, registers the RTC, and optionally requests a shared alarm IRQ and marks wake capable. Suspend/resume enable or disable IRQ wake when the device may wake.

State and persistence: time and alarm digits persist in RTC registers. Driver state caches current bank and serializes access with a spinlock because time, alarm, and timer registers share addresses across banks. Alarm support is disabled by returning `-EINVAL` when no IRQ is available.

Dependencies and integration: uses platform/OF matching, MMIO regmap, property API, RTC core, IRQ handling, spinlocks, and PM wake. The `reg-io-width` property controls byte vs 32-bit spacing.

Risks: low-level regmap reads ignore errors and return masked data, so bus faults can become bogus time. Probe calls `platform_get_irq()` and stores negative values without returning, intentionally allowing no-alarm operation but requiring callers to handle `-EINVAL`. Alarm only matches second/minute/hour/day, with weekday/month/year marked don't-care. Test signals include both register widths, bank-switch serialization, busy timeout, alarm IRQ clear, no-IRQ alarm errors, suspend wake, and digit conversion for full four-digit years.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-r7301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-r9701.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-r9701.c

Purpose: implements a simple SPI RTC driver for the Epson RTC-9701JE, supporting only time read/write over single-register SPI transactions.

Important APIs/types/functions: `write_reg()` sends a write command/address plus one byte; `read_regs()` loops over requested register IDs and reads one byte each with SPI write-then-read. `r9701_get_datetime()` reads seconds, minutes, hours, day, month, and year BCD registers. `r9701_set_datetime()` writes the same fields. `r9701_probe()` verifies the century register before registering the RTC.

Control flow: probe reads `R100CNT` and expects `0x20` as a presence check, allocates an RTC, installs ops, sets range 2000-2099, and registers it. Runtime reads/writes perform independent SPI transactions for each register.

State and persistence: the RTC chip stores BCD calendar values. There is no driver-private persistent state, alarm support, IRQ support, or voltage reporting.

Dependencies and integration: depends on SPI core, RTC core, BCD helpers, and module SPI aliasing.

Risks: multi-register reads/writes are not atomic, so reads can cross a tick and writes can transiently expose partial time. Probe validation is minimal and depends on the century register value. Test signals include SPI mode/clock board data, R100CNT presence failure, read/write round trips, tick-boundary consistency, and year range boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-r9701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t583.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t583.c

Purpose: implements RTC support for the Ricoh RC5T583 PMIC MFD. It provides BCD time read/write, year-alarm support, alarm IRQ notification, wake capability, and suspend/resume preservation of interrupt enables.

Important APIs/types/functions: `struct rc5t583_rtc` stores the RTC and saved interrupt-enable register. `rc5t583_rtc_read_time()` and `rc5t583_rtc_set_time()` bulk-transfer time registers through the parent regmap. `rc5t583_rtc_read_alarm()` and `rc5t583_rtc_set_alarm()` manage the year-alarm register range. `rc5t583_rtc_alarm_irq_enable()` updates the Y-alarm enable bit. `rc5t583_rtc_interrupt()` reads and clears Y-alarm status and calls `rtc_update_irq()`.

Control flow: probe clears pending RTC interrupts and adjust register, derives the IRQ from platform data `irq_base + RC5T583_IRQ_YALE`, requests a threaded low-trigger IRQ, marks wakeup capable, and registers the RTC. Remove disables the alarm. Suspend caches `RTC_CTL1`; resume restores it.

State and persistence: time and alarm live in PMIC RTC registers. The driver assumes years are 2000-2099. `irqen` is runtime state used only across system sleep.

Dependencies and integration: depends on the `rc5t583` MFD parent, its regmap, platform data IRQ base, RTC core, and threaded IRQs.

Risks: probe dereferences platform data without a null check, so DT-only or malformed MFD setup can fault. The interrupt handler calls `rtc_update_irq()` even if no Y-alarm status was present, with events zero. Alarm seconds are not supported and read back as zero. Test signals include platform-data IRQ derivation, alarm enable/status clear, suspend/resume register restore, missing IRQ handling, BCD conversion, and years outside 2000-2099.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t583.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t619.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t619.c

Purpose: supports the Ricoh RC5T619/RN5T618-family PMIC RTC. It provides time read/write with 12-hour and 24-hour handling, full date alarms, alarm IRQ/wake support when the MFD IRQ domain is available, and one-time power-on cleanup.

Important APIs/types/functions: `struct rc5t619_rtc` stores IRQ, RTC, and parent MFD pointer. `rtc5t619_12hour_bcd2bin()` and `rtc5t619_12hour_bin2bcd()` convert 12-hour encoded values. `rc5t619_rtc_periodic_disable()` and `rc5t619_rtc_pon_setup()` clear periodic/PON state. `rc5t619_rtc_read_time()` rejects PON invalid state; `rc5t619_rtc_set_time()` runs setup if PON is set. `rc5t619_rtc_read_alarm()`, `rc5t619_rtc_set_alarm()`, and `rc5t619_rtc_alarm_enable()` handle alarms. `rc5t619_rtc_irq()` clears alarm flags and reports events.

Control flow: probe gets the parent `rn5t618`, resolves the virtual RTC IRQ if an IRQ domain exists, reads CTRL2, disables periodic functions, clears alarm flags after PON, allocates RTC, sets 1900-2099 range, requests a threaded IRQ if available and enables IRQ wake, otherwise disables alarm interrupt and warns, then registers the RTC.

State and persistence: PMIC registers store time, month century flag, alarm, PON/voltage flags, 12/24-hour mode, periodic settings, and alarm enable/status. Driver state only remembers IRQ availability and parent pointers.

Dependencies and integration: depends on the `rn5t618` MFD, regmap, regmap IRQ domain, platform bus, RTC core, and IRQ wake handling.

Risks: `rc5t619_rtc_set_alarm()` increments `alrm->time.tm_mon` in place, mutating the caller's alarm structure. Probe calls `enable_irq_wake()` directly and does not pair it with PM helpers or disable on remove. If PON is set, reads fail until a set-time path initializes the chip. Test signals include PON invalid/read recovery, 12/24-hour conversions for midnight/noon, alarm month mutation, no-IRQ mode, IRQ flag clearing, wake behavior, and century flag around 1999/2000.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t619.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-renesas-rtca3.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-renesas-rtca3.c

Purpose: implements the Renesas RZ/G3S RTCA-3 on-chip RTC. It supports BCD calendar time, alarms, automatic time error adjustment through RTC offset APIs, wake alarm handling, runtime PM/reset sequencing, and a hardware-required periodic-interrupt handshake for alarm setup.

Important APIs/types/functions: `struct rtca3_priv` stores MMIO base, RTC, reset control, alarm setup completion, atomic setup state, spinlock, ppb calibration values, and wake IRQ. `rtca3_read_time()` handles carry-retry reads; `rtca3_set_time()` stops, writes counters, performs dummy reads, and restarts. `rtca3_set_alarm()` writes alarm registers, enables periodic 1/64-second interrupts, waits for two periodic ticks via `rtca3_periodic_handler()`, then enables AIE. `rtca3_read_offset()` and `rtca3_set_offset()` map RTC offset PPB to RADJ/RCR2 adjustment modes. `rtca3_initial_setup()` configures 24-hour calendar mode, reset, adjustment, start, and periodic source.

Control flow: probe maps registers, enables runtime PM, deasserts reset, registers a reset/runtime cleanup action, enables the always-on counter clock, initializes locks/completions, performs initial hardware setup, requests named alarm/period/carry IRQs, enables wakeup, allocates/configures the RTC range, and registers it. Remove disables alarm and periodic interrupts. Suspend rejects sleep while alarm setup is in progress and enables wake IRQ; resume disables wake, waits for readable counters, and synthesizes an alarm event if a deep-sleep wake lost AF state.

State and persistence: RTC counter, alarm, adjustment, interrupt flags, start/reset mode, and wake state live in the RTCA-3 register block. Driver-private state coordinates alarm setup and stores computed PPB per adjustment cycle from the counter clock rate.

Dependencies and integration: uses platform/OF compatible `renesas,rz-rtca3`, MMIO, reset controller, always-on clock, runtime PM, RTC core, completions, atomic state, spinlocks with cleanup guards, named IRQs, and PM sleep ops.

Risks: alarm setup depends on receiving two periodic interrupts within 500 ms; IRQ loss or disabled period IRQ causes `set_alarm()` failure and cleanup paths must prevent storms. The century calculation treats BCD `0x99` specially and otherwise assumes 20xx, limiting range despite two-digit hardware years. `rtca3_request_irqs()` requires a carry IRQ resource but does not request a handler, so missing carry IRQ blocks probe even though carry support is not implemented. Test signals include initial reset/start timing, carry-retry reads, alarm setup timeout and success, periodic IRQ handshake, offset range and mode switching, wake suspend/resume with expired alarm, runtime PM cleanup, and named IRQ resource validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-renesas-rtca3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rk808.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rk808.c

Purpose: implements RTC support for Rockchip RK808-series PMICs, including RK809/RK817 register variants. It provides BCD time, alarm IRQs, wakeup support, and calendar translation for the PMIC's non-Gregorian November behavior.

Important APIs/types/functions: `struct rk_rtc_compat_reg` maps register offsets per PMIC generation; `struct rk808_rtc` stores regmap, RTC, compat regs, and IRQ. `rockchip_to_gregorian()` and `gregorian_to_rockchip()` translate between the hardware calendar, where November has 31 days, and normal Gregorian time using a 2016 anchor. `rk808_rtc_readtime()` snapshots shadow registers with GET_TIME, reads time, converts BCD, and translates. `rk808_rtc_set_time()` stops the RTC, writes converted hardware date, and restarts. `rk808_rtc_setalarm()` and `rk808_alarm_irq()` program and clear alarm IRQs.

Control flow: probe chooses RK817-style registers for RK809/RK817, obtains the parent regmap, starts the RTC and selects shadowed reads, clears status bits, marks wakeup capable, allocates the RTC, obtains/request the platform IRQ, then registers the RTC. Suspend/resume only toggles IRQ wake when device wakeup is enabled.

State and persistence: time, alarm, status, interrupt enable, and control bits live in the PMIC. The driver does not store persistent state; calendar conversion is deterministic and must match firmware or other software accessing the same RTC.

Dependencies and integration: depends on the RK808 MFD parent, regmap, RTC core, platform IRQ, BCD helpers, and PM sleep wake handling.

Risks: `rk808_rtc_set_time()` mutates the caller-provided `rtc_time` by converting it in place. If bulk write fails after STOP is set, the function returns without restarting the RTC. Firmware that does not implement the same November-31 conversion will disagree with Linux. Test signals include RK808 and RK817 register maps, shadow read timing, failed write after STOP, alarm IRQ/status clear, suspend wake, conversion around November/December, and interoperability with firmware dates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rk808.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rp5c01.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rp5c01.c

Purpose: implements the Ricoh RP5C01 MMIO RTC, including time read/write and a 13-byte nvmem view assembled from two 4-bit RAM banks.

Important APIs/types/functions: `struct rp5c01_priv` stores 32-bit-wide MMIO register pointer, RTC, and a spinlock shared by RTC and nvmem access. `rp5c01_read/write()` access low nibbles. `rp5c01_lock()` switches to time mode and `rp5c01_unlock()` returns to timer-enabled mode 01. `rp5c01_read_time()` and `rp5c01_set_time()` read/write decimal digit registers. `rp5c01_nvram_read/write()` switch RAM banks 10 and 11 to combine or split high/low nibbles.

Control flow: probe obtains the MMIO resource, maps it, initializes the lock, allocates the RTC, registers nvmem with size `RP5C01_MODE` bytes, then registers the RTC. There is no IRQ, alarm, suspend/resume, or OF match table.

State and persistence: time digits, mode register, timer/alarm enable bits, and RAM nibbles live in hardware. The driver maps years 00-69 to 2000-2069 and 70-99 to 1970-1999. NVMEM content is battery-backed if board hardware supplies backup power.

Dependencies and integration: uses platform devices, MMIO raw 32-bit access, RTC core, RTC nvmem helper, spinlocks, and devm resource management.

Risks: `rp5c01_set_time()` mutates `tm->tm_year` when it is >=100, altering caller state. There is no validity check for stopped oscillator or illegal digit values. RTC and nvmem modes share registers, making locking essential for all future access paths. Test signals include nvmem high/low nibble packing, concurrent nvmem/time access, year pivot behavior, register-width assumptions, and read/write digit boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rp5c01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c313.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c313.c

Purpose: supports the Ricoh RS5C313 RTC on SH LANDISK-style hardware through board-specific bit-banged serial GPIO/control lines. It provides basic time read/write and resets invalid oscillator-stop state to 1 Jan 2000.

Important APIs/types/functions: the `CONFIG_SH_LANDISK` block defines serial port and CE line operations. `rs5c313_init_port()` configures SCL/SDA GPIO-like pins. `rs5c313_write_data()` and `rs5c313_read_data()` bit-bang 8-bit command/data cycles. `rs5c313_read_reg()` and `rs5c313_write_reg()` send RTC address/data commands. `rs5c313_rtc_read_time()` and `rs5c313_rtc_set_time()` read/write decimal digit registers while checking `ADJ_BSY`. `rs5c313_check_xstp_bit()` clears oscillator-stop state and seeds a default date.

Control flow: platform probe initializes board ports, checks and repairs XSTP, then registers an RTC with read/set time only. Runtime reads and writes assert CE, force 24-hour control mode, wait for adjustment not busy, transfer digit nibbles, then deassert CE.

State and persistence: the hardware stores BCD digit nibbles and control/test flags. There is no driver-private state except global `scsptr1_data` for SH LANDISK port shadowing. Invalid oscillator state is cleared by writing a default date.

Dependencies and integration: depends on platform driver registration, RTC core, SH LANDISK memory-mapped port definitions when enabled, BCD helpers, delays, and raw I/O. The machine-independent portion assumes the board-specific bit-bang helpers/macros exist.

Risks: the file is only meaningful for `CONFIG_SH_LANDISK`; otherwise helper macros/functions are absent. `rs5c313_check_xstp_bit()` calls `rs5c313_rtc_set_time(NULL, &tm)`, which is currently safe because the function only uses `dev` for errors, but fragile. There is no spinlock around global bit-bang state. Test signals include LANDISK build coverage, ADJ_BSY timeout, XSTP reset path, CE timing, 1970/2069 year pivot, and concurrent RTC access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c313.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c348.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c348.c

Purpose: implements a SPI RTC driver for the Ricoh RS5C348. It supports time read/write, oscillator/voltage warnings, 12-hour or 24-hour mode handling, and Y2K century bit interpretation.

Important APIs/types/functions: `struct rs5c348_plat_data` stores the RTC pointer and detected 24-hour mode. `rs5c348_rtc_read_time()` checks CTL2 voltage/oscillator flags, performs a delayed burst read for consistent time registers, converts BCD, and handles 12-hour PM conversion. `rs5c348_rtc_set_time()` clears XSTP if present, performs a delayed burst write of all time registers, and sets month Y2K bit for years >=2000. `rs5c348_probe()` validates the seconds register, detects 24-hour mode from CTL1, allocates the RTC, and registers it.

Control flow: probe sets driver-owned platform data, performs a basic presence check using the seconds register's high bit, logs SPI clock, detects 12/24-hour mode, and registers read/set RTC ops. Runtime transfers prepend dummy CTL2 reads before burst time access to satisfy carry timing and then delay for Tcsr.

State and persistence: the chip stores BCD time, CTL1 24-hour mode, CTL2 oscillator/voltage flags, and the month Y2K bit. Driver state only records whether 24-hour mode is active.

Dependencies and integration: depends on SPI core, RTC core, BCD helpers, delays, platform data storage on the SPI device, and correct board SPI mode/chip-select wiring.

Risks: probe overwrites `spi->dev.platform_data`, so board-provided metadata would be lost. Presence detection is weak. There is no alarm, IRQ, or voltage ioctl despite warning on VDET. The 12-hour PM conversion is non-obvious and should be covered around midnight/noon. Test signals include SPI mode 1/high-active CS board setup, XSTP invalid read, VDET warning, burst transfer timing, 12-hour and 24-hour conversions, Y2K bit handling, and seconds-register presence failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c348.c -->
