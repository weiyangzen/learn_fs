# Research Report: subset-b-005204

This grouped report covers the exact subset-b-005204 source list. Each section preserves the source path in its title and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6594.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6594.c

Purpose: Implements the RTC class driver for TI TPS6594 PMIC MFD children. It exposes calendar time, one-shot alarm, alarm wake, and RTC offset calibration through `struct rtc_class_ops` using the parent PMIC `regmap`.

Important APIs/types/functions: `struct tps6594_rtc` stores the allocated `rtc_device` and alarm IRQ. Time and alarm paths are `tps6594_rtc_read_time`, `tps6594_rtc_set_time`, `tps6594_rtc_read_alarm`, `tps6594_rtc_set_alarm`, and `tps6594_rtc_alarm_irq_enable`. Calibration is split between raw compensation helpers `tps6594_rtc_{get,set}_calibration` and RTC-core ppb APIs `read_offset`/`set_offset`. Probe uses `devm_rtc_allocate_device`, `devm_request_threaded_irq`, `device_init_wakeup`, and `devm_rtc_register_device`.

Control flow: Probe enables the crystal, verifies or starts RTC run state, intentionally stops the RTC until first `set_time` if it was uninitialized, installs a threaded alarm IRQ, marks the device wake-capable, sets the 2000-2099 range, and registers. Reads first check `TPS6594_BIT_RUN`, pulse `GET_TIME` to latch coherent shadow registers, bulk-read BCD fields, and translate into `rtc_time`. Time writes stop the counter, bulk-write the seven time registers, and restart it. Alarm writes disable the interrupt, bulk-write six BCD alarm fields, then re-enable if requested. The IRQ handler reads status only as a sanity check and reports `RTC_IRQF | RTC_AF`; resume separately notices latched startup RTC interrupts and clears/replays them.

State and persistence: Hardware state is in PMIC RTC, alarm, interrupt, status, and compensation registers. Driver state is minimal and devm-owned. Calibration persists in compensation registers and is exposed as signed ppb with an inverted sign convention. Wake state is configured via IRQ wake around system suspend.

Dependencies/integration: Depends on Linux RTC core, `linux/mfd/tps6594.h`, regmap, platform device IDs, and PM sleep helpers. It integrates with `/sys/class/rtc`, `wakealarm`, and `offset` through RTC core callbacks.

Risks: Stop/start bit naming is counterintuitive, so polarity regressions would break set-time. Offset conversion relies on bounded math and sign inversion. Alarm IRQ handling assumes parent interrupt/status clearing semantics. The driver rejects reads when the run bit is clear, which surfaces uninitialized or oscillator-failed hardware as `-EINVAL`.

Test signals: Exercise `hwclock -r/-w`, alarm wake from suspend, `/sys/class/rtc/rtcN/offset`, invalid oscillator/run-bit handling, and boundary years 2000/2099. Regmap fault injection should cover each bulk read/write and compensation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6594.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-twl.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-twl.c

Purpose: Provides RTC support for TI TWL4030/TWL5030/TWL6030/TPS659x0 PMIC families. It handles time/alarm BCD registers, PM wake behavior, interrupt routing, and small battery-backed NVMEM areas.

Important APIs/types/functions: `struct twl_rtc` stores the RTC device, register map, cached interrupt-enable bits, wake flag, PM suspend IRQ state, and TWL class. Register access goes through `twl_rtc_read_u8`, `twl_rtc_write_u8`, `twl_i2c_read`, and `twl_i2c_write`. RTC callbacks are `twl_rtc_read_time`, `twl_rtc_set_time`, `twl_rtc_read_alarm`, `twl_rtc_set_alarm`, and `twl_rtc_alarm_irq_enable`. NVMEM is implemented by `twl_nvram_read`/`twl_nvram_write`.

Control flow: Probe requires DT, an IRQ, and a supported TWL class. It selects the 4030 or 6030 register map, reads and clears power-up/alarm status, unmasks TWL6030 RTC interrupt lines, starts the RTC, disables inherited bootloader interrupts, caches interrupt state, registers an RTC device, requests the threaded IRQ, and registers secured/backup NVMEM windows. Time reads latch a coherent snapshot with `GET_TIME`; TWL6030 needs an extra clear/restore and `RTC_V_OPT` handling. Time writes clear STOP, bulk-write six BCD fields, then set STOP to run. Alarm writes disable alarm IRQ, write six fields, then optionally re-enable. IRQ handling reads status, reports alarm or periodic events, clears alarm status, and performs an extra TWL4030 power ISR read to clear legacy interrupt state.

State and persistence: The PMIC maintains BCD time/alarm registers, status, interrupt-enable bits, and battery-backed NVMEM. The driver caches `rtc_irq_bits` because enable state is modified under RTC ops locking and needs to survive PM suspend/resume. `wake_enabled` tracks whether IRQ wake was enabled by alarm operations.

Dependencies/integration: Integrates with TWL MFD helpers, RTC core, NVMEM via `devm_rtc_nvmem_register`, OF match `"ti,twl4030-rtc"`, platform IRQs, and PM sleep callbacks.

Risks: Cached interrupt bits can diverge if external code writes registers. TWL6030 shadow-register sequencing is easy to regress. The TWL4030 extra-clear workaround can theoretically clear unrelated power interrupt status. Alarm fields can be wildcard-like in hardware, but the driver reports normal decoded values.

Test signals: Boot on 4030 and 6030 variants, validate time set/read coherency across seconds rollover, alarm IRQ and wake toggling, NVMEM read/write windows, PM suspend/resume restoration of timer/alarm bits, and probe recovery from pending power-up/alarm status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-twl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-vt8500.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-vt8500.c

Purpose: Implements the VIA/WonderMedia VT8500 SoC RTC driver. It exposes MMIO-backed time, date, alarm, and alarm IRQ control to the Linux RTC core.

Important APIs/types/functions: `struct vt8500_rtc` holds the mapped register base, alarm IRQ, RTC device, and a spinlock used around interrupt status clear. The RTC operations are `vt8500_rtc_read_time`, `vt8500_rtc_set_time`, `vt8500_rtc_read_alarm`, `vt8500_rtc_set_alarm`, and `vt8500_alarm_irq_enable`. `vt8500_rtc_irq` handles the alarm interrupt.

Control flow: Probe allocates driver state, initializes the spinlock, gets the platform IRQ, maps the register resource, enables the RTC in 24-hour mode by writing `VT8500_RTC_CR_ENABLE`, allocates/registers the RTC, and requests the alarm IRQ. Time reads fetch packed BCD date/time registers and decode seconds, minutes, hours, day, month, weekday, and a 2000/2100 century bit. Time writes encode date and time into the set registers. Alarm reads decode the alarm-set register and status register, reporting enabled if any compare-enable bit is set and pending from interrupt status. Alarm writes pack day/hour/min/sec plus compare-enable bits when requested. IRQ handling reads and writes back interrupt status to clear it, then reports `RTC_AF | RTC_IRQF` when the alarm bit was set.

State and persistence: Hardware stores packed BCD date/time and alarm values. Driver state is devm-managed except the register values. The code sets `range_min` to 2000 and `range_max` to 2199, matching the century bit logic.

Dependencies/integration: Uses platform resources, OF compatible `"via,vt8500-rtc"`, `devm_platform_ioremap_resource`, `devm_request_irq`, RTC class ops, MMIO `readl/writel`, and BCD helpers.

Risks: The write-status and invalid-time bits are defined but not used, so the driver does not wait for write completion or reject invalid hardware state. IRQ status clearing is protected, but ordinary alarm writes are not locked against concurrent IRQ. `remove` writes zero to the interrupt status register despite the comment saying disable alarm matching, so hardware semantics should be checked before changing it.

Test signals: Validate rollover-safe read/write, alarm enable/disable bitmask behavior, pending alarm reporting, IRQ clear-on-write behavior, and boundary years 2000 and 2199 under a DT platform instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-vt8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-wilco-ec.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-wilco-ec.c

Purpose: Provides RTC read/write support for Google Wilco Embedded Controller systems. Unlike register-based RTC drivers, it sends legacy EC mailbox messages to read or update CMOS time-of-day.

Important APIs/types/functions: Protocol structs are `ec_rtc_read_request`, `ec_rtc_read_response`, and `ec_rtc_write_request`. The RTC callbacks are `wilco_ec_rtc_read` and `wilco_ec_rtc_write`, registered through `wilco_ec_rtc_ops`. `wilco_ec_rtc_probe` allocates and registers the RTC device with a fixed 2000-2099 range.

Control flow: Probe creates a devm RTC device, assigns read/set callbacks, sets owner and supported range, and registers. Reads build a `WILCO_EC_MSG_LEGACY` mailbox request using static `read_rq`, receive binary fields from the EC, translate month/year into Linux `rtc_time`, validate with `rtc_valid_tm`, and return `-EIO` if the EC reports invalid data. Writes convert Linux `rtc_time` into EC protocol fields, including BCD century/year/month/day/hour/min/sec and weekday remapped from Linux 0=Sunday to EC 0=Saturday, then send the mailbox message with no response payload.

State and persistence: Persistent state lives entirely inside the EC/CMOS. The driver keeps no private per-device state and relies on parent device drvdata to obtain `struct wilco_ec_device`. Weekday persistence matters because the EC uses it for battery charging schedules.

Dependencies/integration: Depends on `linux/platform_data/wilco-ec.h`, the Wilco EC mailbox core, RTC core, platform driver binding `"rtc-wilco-ec"`, and `timekeeping.h` for RTC structures.

Risks: Read responses are binary while writes are BCD, so protocol confusion would silently corrupt time. Static `read_rq` is shared, but immutable after initialization. The driver has no alarm support, no wakealarm, and no offset support. It trusts the parent EC device and mailbox transport for serialization and command completion.

Test signals: Mock or hardware-test mailbox read/write payloads, invalid EC time validation, weekday conversion for all seven days, century boundaries 2000 and 2099, and parent probe ordering where `dev_get_drvdata(dev->parent)` must be valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-wilco-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm831x.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm831x.c

Purpose: Implements RTC support for Wolfson WM831x PMICs using a 32-bit seconds counter split across two 16-bit registers, plus a similarly split alarm counter and PM-aware alarm enable handling.

Important APIs/types/functions: `struct wm831x_rtc` stores the parent `wm831x`, RTC device, and cached alarm-enabled state. Key callbacks are `wm831x_rtc_readtime`, `wm831x_rtc_settime`, `wm831x_rtc_readalarm`, `wm831x_rtc_setalarm`, and `wm831x_rtc_alarm_irq_enable`. Alarm helpers `wm831x_rtc_start_alarm` and `wm831x_rtc_stop_alarm` manipulate `WM831X_RTC_ALM_ENA`. PM callbacks suspend/resume/freeze alarm state. `wm831x_rtc_add_randomness` feeds the write counter into kernel randomness.

Control flow: Probe reads RTC control, caches whether alarm is enabled, marks wakeup capable, allocates/registers RTC with `range_max = U32_MAX`, requests the alarm IRQ via `wm831x_irq`, and contributes the write counter to device randomness. Time reads first require `WM831X_RTC_VALID`, then bulk-read the two time registers twice until stable or retry exhaustion. Time writes split `rtc_tm_to_time64`, write high/low halves, poll the sync bit, then read back and require the update to be within one second. Alarm writes stop the alarm, write high/low alarm halves, and optionally restart. The alarm IRQ simply reports `RTC_IRQF | RTC_AF`.

State and persistence: The PMIC stores time, alarm, valid/sync/alarm-enable bits, and write counter. Driver state caches desired alarm enable so suspend can disable non-wakeup alarms and resume can restore them.

Dependencies/integration: Uses WM831x MFD register APIs, platform child device, RTC core, threaded IRQ, PM callbacks, and kernel randomness infrastructure.

Risks: The polling loop uses the hardware sync bit semantics; changes must preserve the intended wait condition. Readback verification can reject writes blocked by PMIC security policy. No explicit alarm pending state is reported. Probe logs IRQ request failure but still returns success, leaving a registered RTC without alarm interrupts if IRQ setup fails.

Test signals: Stable double-read under rollover, write acceptance/rejection paths, alarm set/enable/disable, PM suspend with and without wakeup, freeze/thaw alarm disabling, and IRQ request failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm831x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm8350.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm8350.c

Purpose: Provides RTC support for Wolfson WM8350 PMICs, including time read/write, wildcard-style alarms, update/alarm interrupts, and PM wake behavior.

Important APIs/types/functions: The driver uses WM8350 MFD register helpers directly through `struct wm8350`. RTC callbacks are `wm8350_rtc_readtime`, `wm8350_rtc_settime`, `wm8350_rtc_readalarm`, `wm8350_rtc_setalarm`, and `wm8350_rtc_alarm_irq_enable`. Alarm state transitions use `wm8350_rtc_stop_alarm` and `wm8350_rtc_start_alarm`. IRQ handlers are `wm8350_rtc_alarm_handler` and `wm8350_rtc_update_handler`.

Control flow: Probe rejects unsupported BCD and 12-hour modes, enables the RTC tick in `POWER_MGMT_5` if needed, starts the clock if it is stopped, initializes wakeup, registers the RTC, registers seconds and alarm IRQs, and masks seconds updates by default. Reads use two consecutive four-register block reads and accept the time only when they match, then decode binary fields and calculate yday. Set-time sets `RTC_SET`, waits for stop confirmation, writes four packed registers, and clears `RTC_SET` to run. Alarm read decodes wildcard masks as `-1` fields and reports enabled from `ALMSTS` polarity. Alarm write converts `-1` fields back to masks, stops alarm, writes three registers, and optionally starts it. Alarm IRQ reports AF and makes the alarm one-shot by setting `RTC_ALMSET`.

State and persistence: PMIC registers persist time, alarm masks, tick enable, status, and alarm state. Driver-owned `wm8350->rtc.alarm_enabled` is used on resume to restore alarms. Device/block lifetime is managed by the parent MFD platform data.

Dependencies/integration: Depends on WM8350 MFD core/RTC register definitions, RTC core, platform driver, PM sleep, and MFD IRQ registration/freeing.

Risks: Alarm enable polarity is subtle because `ALMSTS` indicates stopped/disabled state. The retry loops use small retry counts and can fail on slow hardware. Probe must unlock/lock protected registers around tick enable. Wildcard alarms have no direct one-shot date semantics, so handler disables after trigger.

Test signals: Non-BCD 24-hour probe only, time double-read stability, stop/start retry timeouts, wildcard alarm fields, one-shot alarm interrupt behavior, seconds update interrupt masking, and suspend/resume with wake alarms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-x1205.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-x1205.c

Purpose: Implements an I2C RTC driver for the Xicor/Intersil X1205. It supports current time, alarm 0, oscillator restart after clock failure, trim reporting through proc/sysfs, and probe-time register validation.

Important APIs/types/functions: Low-level helpers include `x1205_get_datetime`, `x1205_set_datetime`, `x1205_get_status`, `x1205_get_dtrim`, `x1205_get_atrim`, and `x1205_validate_client`. RTC callbacks are `x1205_rtc_read_time`, `x1205_rtc_set_time`, `x1205_rtc_read_alarm`, `x1205_rtc_set_alarm`, and `x1205_rtc_proc`. Sysfs helpers expose `atrim` and `dtrim`.

Control flow: Probe verifies I2C functionality, validates zero-bit and BCD range patterns across status/time/alarm registers, registers the RTC, checks clock-failure status, calls `x1205_fix_osc` if needed, and creates trim sysfs files. Date reads perform a two-message I2C transfer from either CCR or alarm base, mask alarm compare-enable bits, decode BCD fields, and compute full year from Y2K+YR. Writes build a 10-byte address+payload, set 24-hour mode, set alarm compare bits for alarm registers, execute required WEL then RWEL unlock writes, write the payload, optionally update AL0E after nonvolatile alarm writes with write-cycle delays, and finally disable writes.

State and persistence: Time/alarm/status/trim registers are nonvolatile device state. The Linux driver stores only the RTC device pointer in I2C client data. `RTCF` marks clock failure, and alarm pending/enabled are reported from status and INT registers.

Dependencies/integration: Uses raw I2C transfers/master sends, RTC core, BCD helpers, OF compatible `"xicor,x1205"`, legacy I2C IDs, sysfs `DEVICE_ATTR`, and the RTC proc hook.

Risks: The write-enable sequence is mandatory and easy to break. Alarm writes have two nonvolatile write delays and RWEL is cleared between them. The driver has no IRQ handler; alarm state can be read/set but not delivered as RTC interrupts. Validation can reject unusual but real register contents if hardware has unexpected values.

Test signals: I2C transfer failure injection, write-enable sequencing, CCR and alarm round trips, AL0E enable/disable, RTCF oscillator restart, trim sysfs/proc output, and probe validation against known-good register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-x1205.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-xgene.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-xgene.c

Purpose: Provides an MMIO RTC driver for AppliedMicro APM X-Gene SoCs. It exposes a 32-bit seconds counter, compare alarm, interrupt handling, clock control, and wake-aware suspend/resume.

Important APIs/types/functions: `struct xgene_rtc_dev` stores the RTC device, CSR mapping, clock, and PM IRQ state. RTC callbacks are `xgene_rtc_read_time`, `xgene_rtc_set_time`, `xgene_rtc_read_alarm`, `xgene_rtc_set_alarm`, and `xgene_rtc_alarm_irq_enable`. `xgene_rtc_interrupt` handles compare interrupts.

Control flow: Probe allocates state, maps CSR registers, allocates RTC, requests the platform IRQ, obtains and enables the RTC clock, turns on the RTC with `RTC_CCR_EN`, marks wake-capable, sets the RTC range to `U32_MAX`, and registers. Time read converts `RTC_CCVR` seconds to `rtc_time`; set writes `RTC_CLR` and reads it back as a barrier, with a comment that visible counter update occurs after one second. Alarm set writes `RTC_CMR` and applies interrupt enable/disable. IRQ enable manipulates `RTC_CCR_IE` and `RTC_CCR_MASK`. The interrupt handler checks `RTC_STAT_BIT`, reads `RTC_EOI` to clear, and reports alarm.

State and persistence: Hardware counter, compare register, control bits, and clock domain hold functional state. Driver PM state records whether IRQ wake was enabled and whether alarm IRQ was enabled before non-wakeup suspend.

Dependencies/integration: Uses platform MMIO, OF compatible `"apm,xgene-rtc"`, common clock framework, RTC core, IRQ wake APIs, and PM sleep ops.

Risks: `read_alarm` does not read `RTC_CMR`; it returns time zero with enabled state only, so users cannot inspect the programmed alarm time. Suspend disables the clock only when not wake-capable and restores alarm IRQ state on resume. Set-time truncates to 32 bits and depends on hardware’s one-second update latency.

Test signals: Read/set around one-second latency, alarm programming and IRQ/EOI clear, wake and non-wake suspend paths, clock enable/disable failure, range near `U32_MAX`, and the known read_alarm time-zero limitation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-xgene.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-zynqmp.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/rtc-zynqmp.c

Purpose: Implements RTC support for Xilinx Zynq UltraScale+ MPSoC. It handles seconds timekeeping, alarms, second/alarm interrupts, battery switch enable, and RTC offset calibration with fractional ticks.

Important APIs/types/functions: `struct xlnx_rtc_dev` stores RTC device, MMIO base, alarm/sec IRQs, optional clock, and calibration frequency. RTC callbacks are `xlnx_rtc_set_time`, `xlnx_rtc_read_time`, `xlnx_rtc_read_alarm`, `xlnx_rtc_set_alarm`, `xlnx_rtc_alarm_irq_enable`, `xlnx_rtc_read_offset`, and `xlnx_rtc_set_offset`. Probe and PM are `xlnx_rtc_probe`, `xlnx_rtc_suspend`, and `xlnx_rtc_resume`.

Control flow: Probe allocates RTC state, maps registers, clears stale alarm interrupt status, detects whether an alarm from previous boot is still in the future, requests named alarm and second IRQs, derives calibration frequency from optional clock or DT `calibration`, initializes calibration if empty, enables battery backup in `RTC_CTRL`, re-enables a valid retained alarm, marks wake-capable, and registers. Set-time writes time+1 to `RTC_SET_TM_WR` and clears the seconds status bit. Read-time checks whether a second tick has occurred; before it has, it reads `RTC_SET_TM_RD - 1`, otherwise `RTC_CUR_TM`. Alarm enabling clears stale alarm status in a bounded loop before enabling. Interrupt handling disables alarm interrupts after any asserted interrupt and reports AF for alarm status.

State and persistence: Hardware retains current time, set-time shadow, alarm, interrupt status/mask, calibration, and battery-enable state. Driver stores calibration frequency and IRQ IDs. Offset is represented as ppb by comparing programmed ticks to `freq` and optional fractional tick fields.

Dependencies/integration: Uses platform MMIO, named IRQ resources, OF compatible `"xlnx,zynqmp-rtc"`, common clock framework, RTC core offset API, PM wake APIs, and DT calibration fallback.

Risks: Resume unconditionally enables alarm IRQ for non-wakeup devices, even if no alarm was active before suspend. Fractional offset math truncates toward integer fractional ticks and must preserve negative offset adjustment. Alarm enable can time out clearing a sticky status bit.

Test signals: Immediate read after set_time, normal read after one tick, alarm IRQ one-shot behavior, stale pending alarm cleanup, retained alarm re-enable after boot, offset conversion positive/negative/fractional cases, invalid calibration >16-bit, and suspend/resume wake and non-wake modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/sysfs.c

Purpose: Implements the generic RTC subsystem sysfs attributes and helper APIs for adding extra RTC attribute groups. It is shared by RTC devices rather than tied to one hardware driver.

Important APIs/types/functions: Attribute show/store methods cover `name`, `date`, `time`, `since_epoch`, `max_user_freq`, `hctosys`, `wakealarm`, `offset`, and `range`. Visibility is controlled by `rtc_attr_is_visible` and `rtc_does_wakealarm`. Public helpers are `rtc_get_dev_attribute_groups`, `rtc_add_groups`, and `rtc_add_group`.

Control flow: Read-only date/time attributes call `rtc_read_time`, format with `%ptR*`, or convert via `rtc_tm_to_time64`. `max_user_freq_store` parses an unsigned long and accepts values 1..4095. `hctosys_show` reports whether this RTC matched `CONFIG_RTC_HCTOSYS_DEVICE` and successfully set system time. `wakealarm_show` returns an epoch only for enabled alarms. `wakealarm_store` reads current RTC time, parses absolute, relative `+N`, or push `+=N` values, rejects clobbering an active alarm unless pushing, disables alarms by programming a valid future dummy time when the requested epoch is not in the future, and calls `rtc_set_alarm`. Offset store delegates to RTC class offset callbacks. Visibility hides `wakealarm` if parent cannot wake or alarm feature is absent, hides `offset` without `set_offset`, and hides `range` when min/max are equal.

State and persistence: Most state is in the underlying RTC driver and hardware. `max_user_freq` is mutable in `struct rtc_device`. `rtc_add_groups` replaces `rtc->dev.groups` with a devm-allocated merged array and frees prior non-default group arrays.

Dependencies/integration: Uses RTC core APIs, sysfs attribute groups, kstrto parsing, wakeup capability, `RTC_FEATURE_ALARM`, and exported symbols for drivers that attach extra sysfs groups.

Risks: `wakealarm_store` has only minimal locking and documents that it cannot fully prevent concurrent alarm clobbering through other interfaces. It assumes RTC times are in the RTC’s timezone. `rtc_add_groups` must preserve the default group pointer ownership distinction.

Test signals: Attribute visibility matrix, wakealarm absolute/relative/push/disable cases, EBUSY on active alarm overwrite, max_user_freq bounds, offset show/store on capable and incapable RTCs, range hiding, and multiple group additions without leaking or dropping default groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/test_rtc_lib.c -->
## sources/distributed-fs/ceph-client/drivers/rtc/test_rtc_lib.c

Purpose: Provides KUnit coverage for RTC library date conversion, specifically `rtc_time64_to_tm`, across long Gregorian-calendar intervals.

Important APIs/types/functions: `advance_date` is a local reference model for incrementing date, day-of-year, and weekday by one day. `rtc_time64_to_tm_test_date_range` drives the conversion under test for a caller-specified number of years. Test entry points are `rtc_time64_to_tm_test_date_range_1000` and slow `rtc_time64_to_tm_test_date_range_160000`, registered in `rtc_lib_test_cases` and `rtc_lib_test_suite`.

Control flow: The test computes total seconds for whole 400-year cycles because the Gregorian calendar repeats every 146097 days. It starts from 1900-01-01 Monday, adds a fixed `01:02:03` time offset, and iterates one day at a time. For each day it calls `rtc_time64_to_tm`, asserts year/month/day/yday/hour/min/sec/wday against the reference state, then advances the reference date. The 1000-year case is normal; the 160000-year case is marked `KUNIT_CASE_SLOW`.

State and persistence: No persistent state exists. State is local loop variables and KUnit result recording. The test intentionally exercises very large positive `time64_t` values.

Dependencies/integration: Depends on KUnit and `linux/rtc.h`, built as part of RTC library tests when enabled. It validates shared RTC core logic used by many drivers in this subset.

Risks: The reference model depends on `rtc_month_days`, so it is not fully independent of RTC date helpers. The computed total seconds truncates to whole 400-year groups for non-multiple inputs, which is intentional for test ranges used here. Runtime can be high for the slow case.

Test signals: Passing KUnit output for both normal and slow cases, especially leap-year boundaries, yday reset at Jan 1, weekday modulo behavior, and large `time64_t` conversion stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/test_rtc_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/Makefile -->
## sources/distributed-fs/ceph-client/drivers/s390/Makefile

Purpose: Defines the top-level build aggregation for S/390-specific drivers.

Important APIs/types/functions: This is a kbuild Makefile rather than C code. Its only build rule appends `cio/`, `block/`, `char/`, `crypto/`, `net/`, `scsi/`, and `virtio/` subdirectories to `obj-y`.

Control flow: During kernel build descent into `drivers/s390`, kbuild always visits the listed subdirectories because they are under `obj-y`; configuration inside each child directory decides which objects are built.

State and persistence: No runtime state. Build state is the set of subdirectory make invocations.

Dependencies/integration: Integrates with Linux kbuild and the architecture-specific driver tree. It is the parent entry point for `drivers/s390/block/Makefile`, including DASD and SCM block drivers.

Risks: Removing a subdirectory here silently excludes its internal Kconfig-selected objects from the build. Adding optionality here would be redundant with child Kconfig/Makefile logic and could break expected S/390 driver discovery.

Test signals: `make drivers/s390/` or a full S390 build should descend into all listed directories. Kbuild warnings about missing directories or unvisited configured objects would indicate issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/s390/block/Kconfig

Purpose: Declares S/390 block-device configuration options for DCSSBLK, DASD core/disciplines, DASD profiling/EER, and SCM block devices.

Important APIs/types/functions: Kconfig symbols are `DCSSBLK`, `DASD`, `DASD_PROFILE`, `DASD_ECKD`, `DASD_FBA`, `DASD_DIAG`, `DASD_EER`, and `SCM_BLOCK`. Dependencies tie them to `S390`, `BLOCK`, `CCW`, `ZONE_DEVICE`, `EADM_SCH`, and `SCM_BUS`; `DCSSBLK` selects `FS_DAX`.

Control flow: Menu visibility starts with the comment depending on `S390 && BLOCK`. DASD defaults to built-in when `CCW && BLOCK` are available. ECKD/FBA/DIAG default to built-in or tristate according to their declarations and depend on DASD. DASD profiling and EER are boolean defaults when DASD is enabled. SCM block builds as a module by default when its S390 bus prerequisites are available.

State and persistence: Kconfig selections persist in `.config` and drive conditional compilation in the block Makefile and C sources. For example, `CONFIG_DASD_PROFILE` includes profiling/debugfs code in `dasd.c`, and `CONFIG_DASD_EER` adds `dasd_eer.o`.

Dependencies/integration: Integrates with s390 CCW channel subsystem, block layer, DAX/zone-device support, EADM subchannels, and SCM bus.

Risks: Defaults make DASD and common disciplines available automatically on S/390, so broken dependencies can affect boot-critical storage. Boolean `DASD_EER` and `DASD_PROFILE` increase compiled surface whenever DASD is on. Help text should remain clear because selecting DIAG only makes sense under VM.

Test signals: `olddefconfig` on S390 should select expected defaults; all combinations of `DASD` with ECKD/FBA/DIAG modular or built-in should link through `drivers/s390/block/Makefile`; `CONFIG_DASD_PROFILE=n` should compile out profiling sections cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/Makefile -->
## sources/distributed-fs/ceph-client/drivers/s390/block/Makefile

Purpose: Defines object aggregation for S/390 block drivers, especially the DASD core and its ECKD/FBA/DIAG disciplines.

Important APIs/types/functions: Kbuild composite objects are `dasd_mod-objs`, `dasd_eckd_mod-objs`, `dasd_fba_mod-objs`, `dasd_diag_mod-objs`, and `scm_block-objs`. Conditional object entries use `obj-$(CONFIG_...)`.

Control flow: `dasd_mod` is built from core files `dasd.o`, `dasd_ioctl.o`, `dasd_proc.o`, `dasd_devmap.o`, `dasd_genhd.o`, and `dasd_erp.o`; `dasd_eer.o` is added only when `CONFIG_DASD_EER` is set. ECKD combines `dasd_eckd.o`, `dasd_3990_erp.o`, and `dasd_alias.o`; FBA and DIAG each wrap one discipline file. `DCSSBLK` and `SCM_BLOCK` add their respective modules.

State and persistence: No runtime state. Build composition determines which exported symbols from `dasd.c` are linked into the core module and available to discipline modules.

Dependencies/integration: Receives Kconfig decisions from `drivers/s390/block/Kconfig` and emits modules consumed by the s390 CCW driver model and block layer.

Risks: Object ordering matters for module initialization and symbol availability. Forgetting to add a file to the composite object can create unresolved symbols only for certain configs. `dasd_eer.o` is conditionally part of the core, so call sites in `dasd.c` must have stubs when disabled.

Test signals: Build `CONFIG_DASD=y/m`, each discipline as `y/m`, `CONFIG_DASD_EER=y/n`, and `CONFIG_SCM_BLOCK=m`; check `modinfo` and link outputs for `dasd_mod`, `dasd_eckd_mod`, `dasd_fba_mod`, and `dasd_diag_mod`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd.c -->
## sources/distributed-fs/ceph-client/drivers/s390/block/dasd.c

Purpose: Implements the common S/390 DASD core driver. It provides device/block allocation, the DASD state machine, CCW request allocation and execution, interrupt completion, error recovery plumbing, blk-mq integration, open/release operations, path event handling, autoquiesce/EER integration, debugfs profiling, and module initialization. Discipline-specific code such as ECKD/FBA/DIAG plugs into this core through `struct dasd_discipline` callbacks.

Important APIs/types/functions: Exported entry points include `dasd_alloc_block`, `dasd_free_block`, `dasd_smalloc_request`, `dasd_fmalloc_request`, `dasd_sfree_request`, `dasd_ffree_request`, `dasd_start_IO`, `dasd_term_IO`, `dasd_int_handler`, `dasd_schedule_device_bh`, `dasd_schedule_block_bh`, synchronous helpers `dasd_sleep_on*`, generic CCW driver hooks `dasd_generic_probe/remove/set_online/set_offline/notify/path_event/shutdown`, and utility APIs such as `dasd_generic_read_dev_chars` and `dasd_get_sense`. Core state objects are `struct dasd_device`, `struct dasd_block`, `struct dasd_ccw_req`, profiling structures, CCW queues, timers, tasklets, and wait queues.

Control flow: Initialization creates wait queues, debug areas, debugfs statistics, devmap/gendisk/proc/EER infrastructure, and parses DASD parameters. Online processing creates or finds a DASD device, selects base or DIAG discipline, pins modules, calls discipline `check_device`, and drives the target state to ONLINE. The state machine walks NEW -> KNOWN -> BASIC -> READY -> ONLINE, allocating gendisks/debugfs, running discipline analysis, applying queue limits/capacity/discard settings, scanning partitions, and scheduling block work; reverse transitions flush queues, destroy partitions, free gendisks, and unregister debug resources. Block I/O enters through `do_dasd_request`, where a discipline builds a channel program, the request is placed on the block queue, a block tasklet moves filled CQRs to the device queue, and a device tasklet starts the head via discipline `start_IO`. Interrupts update CQR status, handle clear-pending completions, ESE format/read special cases, HPF/path errors, sense logging, autoquiesce triggers, and fast-start of the next queued request. Final requests are moved back through device and block final queues where ERP, cleanup, blk-mq completion, requeue, or failure mapping occurs.

State and persistence: Runtime state is mostly in `dasd_device` flags, `state/target`, stop bits, path masks, timers, queues, request status, retry counters, and discipline private data. Persistent user-visible effects include gendisk registration, partitions, debugfs statistics, EER records, and configured devmap/features. Request memory is carved from device chunk pools for normal CCWs, ERP, and ESE format operations.

Dependencies/integration: Deeply integrated with s390 CCW (`ccw_device_start`, `tm_start`, `clear`, IRB/SCSW sense), blk-mq, gendisk helpers, DASD devmap/genhd/ioctl/proc/EER/ERP modules, debugfs, async online, module autoloading for DIAG, VM `diag210`, path management helpers, and discipline callbacks.

Risks: Concurrency is complex: CCW-device locks, block queue locks, tasklet scheduling guards, timers, wait queues, workqueues, and module/device references must align. Error paths can requeue, start ERP chains, autoquiesce, format ESE tracks, or fail block requests; small status mistakes can leak requests or complete twice. Safe offline must avoid racing normal offline/openers. Path-loss and HPF/IFCC handling must avoid permanent stop states. Profiling/debugfs code must tolerate dynamic enable/disable. Several paths call `BUG()` on unexpected channel errors, so defensive validation is limited.

Test signals: S390 DASD boot with ECKD/FBA/DIAG, online/offline/safe-offline under I/O, blk-mq timeouts, request cancellation, path gone/operational events, ESE no-record-found formatting/read completion, HPF fallback, autoquiesce reasons, readonly detection under z/VM, debugfs profiling on/off/reset, EER enabled/disabled, DIAG module autoload, and build coverage with `CONFIG_DASD_PROFILE`/`CONFIG_DASD_EER` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd.c -->
