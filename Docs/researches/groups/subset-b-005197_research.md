# subset-b-005197 grouped RTC research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq32k.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq32k.c

## Purpose
TI BQ32000 I2C RTC driver. It exposes basic RTC read/set operations, initializes oscillator and optional trickle charger settings from device tree, and adds a sysfs control for the trickle-charge FET bypass bit.

## Important APIs, types, and functions
- `struct bq32k_regs` mirrors the seven contiguous time registers from seconds through years.
- `bq32k_read()` and `bq32k_write()` implement offset-prefixed I2C transfers. Writes use a fixed `MAX_LEN + 1` stack buffer, so all callers must keep transfer length within the hardware register span.
- `bq32k_rtc_read_time()` reads the register block, rejects oscillator failure via `BQ32K_OF`, and decodes BCD fields plus the century bit.
- `bq32k_rtc_set_time()` encodes `struct rtc_time`, enables century tracking, sets the century bit when `tm_year >= 100`, and writes the full register block.
- `trickle_charger_of_init()` recognizes `trickle-resistor-ohms` and `trickle-diode-disable` combinations, then programs `BQ32K_CFG2` and `BQ32K_TCH2`.
- `bq32k_sysfs_show/store_tricklecharge_bypass()` exposes `trickle_charge_bypass` by reading/updating `BQ32K_TCFE`.
- `bq32k_probe()` checks I2C functionality, clears `BQ32K_STOP`, warns on `BQ32K_OF`, applies trickle charger DT setup, registers the RTC, and creates sysfs.

## Control flow
Probe performs hardware readiness checks before registration. Runtime RTC operations go directly through the `rtc_class_ops` table. Removal only removes the sysfs file because device-managed registration and allocations handle the rest.

## State and persistence behavior
Persistent state is entirely in battery-backed BQ32000 registers: time/date, century state, oscillator failure/stop flags, trickle charger configuration, and bypass bit. The driver holds no private runtime state beyond the registered `rtc_device` pointer in client data. `BQ32K_OF` is not cleared by reads; setting time rewrites minutes and effectively clears the flag.

## Dependencies and integration points
Depends on Linux I2C, RTC class, BCD helpers, sysfs device attributes, and OF properties. Integrates through `module_i2c_driver()`, `i2c_device_id` `"bq32000"`, and OF compatible `"ti,bq32000"`.

## Risks
- `bq32k_write()` does not locally validate `len <= MAX_LEN`; current callers are safe, but future writes must respect it.
- Sysfs writes parse arbitrary integers as truthy/falsy and do not serialize with concurrent RTC operations beyond I2C bus serialization.
- Trickle charger DT validation is strict and returns an error for unsupported resistor/diode combinations, which can fail probe if the property is wrong.
- Time validity depends on the oscillator failure flag and battery condition.

## Test signals
Useful signals are successful probe, warning logs for oscillator stop/failure, `hwclock` read/set behavior, sysfs `trickle_charge_bypass` read/write, DT trickle charger cases, and I2C error injection on the offset read/write helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq32k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq4802.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq4802.c

## Purpose
TI BQ4802 platform RTC driver supporting either I/O port or memory-mapped register access. It provides basic read/set time only.

## Important APIs, types, and functions
- `struct bq4802` stores mapped memory or I/O base, an RTC device, a spinlock, resource pointer, and polymorphic `read`/`write` callbacks.
- `bq4802_read_io/write_io()` and `bq4802_read_mem/write_mem()` abstract register access for IORESOURCE_IO and IORESOURCE_MEM.
- `bq4802_read_time()` locks, sets the update-transfer bit in register `0x0e`, reads time/date/century registers, restores control, unlocks, then converts BCD to `rtc_time`.
- `bq4802_set_time()` converts `rtc_time` to BCD, locks, enables update mode, writes seconds/minutes/hours/day/month/year/century, restores control, and unlocks.
- `bq4802_probe()` allocates state, selects resource mode, maps memory when needed, stores driver data, and registers the RTC using `devm_rtc_device_register()`.

## Control flow
Probe determines the register access path from the platform resource and installs the same `rtc_class_ops` regardless of transport. Runtime calls are short critical sections protected by `spin_lock_irqsave()`.

## State and persistence behavior
Time and century persist in BQ4802 hardware registers. The driver has no alarm or NVRAM interface and maintains no persistent software state. The spinlock protects multi-register snapshots and programming sequences.

## Dependencies and integration points
Depends on platform resources, I/O accessors, RTC class, BCD helpers, and optional memory mapping. It binds through platform alias `"rtc-bq4802"` and driver name `"rtc-bq4802"`.

## Risks
- No explicit range metadata, so century math relies on raw hardware values and RTC core defaults.
- Memory resources are mapped with `devm_ioremap()` rather than `devm_ioremap_resource()`, so resource ownership/conflict checking is minimal for MMIO.
- There is no oscillator validity check or alarm handling.

## Test signals
Probe with both I/O and MMIO resources, read/write round trips across century boundaries, concurrent read/set stress for lock coverage, and faulted resource configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq4802.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-brcmstb-waketimer.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-brcmstb-waketimer.c

## Purpose
Broadcom STB wake timer RTC driver. It wraps a seconds counter and alarm comparator as an RTC, supports wakeup from suspend/poweroff, and handles separate wake and runtime alarm IRQ lines when provided.

## Important APIs, types, and functions
- `struct brcmstb_waketmr` stores RTC, MMIO base, wake/alarm IRQs, reboot notifier, optional clock/rate, cached alarm time, and alarm state booleans.
- `brcmstb_waketmr_is_pending()`, `clear_alarm()`, and `set_alarm()` manage event flags, comparator programming, prescaler setup, and IRQ enable balance.
- `brcmstb_waketmr_irq()` handles wake-only interrupts; `brcmstb_alarm_irq()` handles runtime alarm events, disables IRQs during wake-enabled expiration, and calls `rtc_update_irq()`.
- `wktmr_read()` samples seconds plus prescaler until the prescaler value is stable, producing subsecond ordering support.
- RTC ops read/write the seconds counter, cache/read alarms, program comparator, and enable/disable alarms.
- PM callbacks enable IRQ wake, catch noirq alarm races via `alarm_expired`, clear alarms on resume, and a reboot notifier arms wake behavior for `SYS_POWER_OFF`.

## Control flow
Probe maps the timer, enables optional clock or uses 27 MHz default, requests the wake IRQ, clears stale alarm state, optionally requests a second alarm IRQ with `IRQF_NO_AUTOEN`, registers reboot notifier, sets `range_max = U32_MAX`, and registers the RTC. Alarm programming always clears the previous comparator, writes prescaler and alarm time, and adjusts if the requested second is already behind the counter.

## State and persistence behavior
Hardware state is the counter, prescaler, alarm comparator, and event flag. Software caches `rtc_alarm`, `alarm_en`, and `alarm_expired` because runtime IRQ enablement and wake IRQ behavior are not fully represented by the hardware registers. Counter range is 32-bit seconds.

## Dependencies and integration points
Depends on platform MMIO resources, optional `clk`, interrupt framework, PM wakeup APIs, reboot notifier, and RTC class. It binds to OF compatible `"brcm,brcmstb-waketimer"`.

## Risks
- IRQ enable/disable balance is delicate, especially `alarm_expired` paths that re-enable a disabled IRQ to maintain nesting balance.
- `rtc_alarm` is cached in software and may not reflect externally modified hardware.
- Counter and alarm range are limited to `U32_MAX` seconds.
- Suspend/noirq race handling depends on `alarm_expired` being set only from the runtime alarm IRQ.

## Test signals
Alarm set/read/enable tests with one and two IRQ resources, suspend/resume wake tests, `SYS_POWER_OFF` notifier behavior, clock absent/zero-rate fallback, and alarms set at or before the current counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-brcmstb-waketimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cadence.c

## Purpose
Cadence RTC platform driver for `cdns,rtc-r109v3`. It provides timekeeping, calendar, alarm interrupts, wake support, and clock validation for a register-mapped RTC block.

## Important APIs, types, and functions
- `struct cdns_rtc` stores the RTC device, peripheral/reference clocks, MMIO base, and IRQ.
- `cdns_rtc_set_enabled()` and `cdns_rtc_get_enabled()` control the time/calendar counters via `CDNS_RTC_CTLR`.
- `cdns_rtc_time2reg()` and `cdns_rtc_reg2time()` translate BCD time fields using bitfield helpers.
- `cdns_rtc_read_time()` disables counting, samples time and calendar registers, decodes full date including century, then re-enables.
- `cdns_rtc_set_time()` writes time/calendar and retries until valid flags `VT|VC` appear in status.
- Alarm ops program time/date/month alarm registers, retry until `VTA|VCA`, and toggle alarm event/interrupt masks.
- `cdns_rtc_irq_handler()` reads the event flag register, which clears it, and reports `RTC_AF`.
- Probe maps registers, obtains `pclk` and `ref_clk`, requires ref clock of 1 or 100 Hz, requests IRQ, sets range 1900-2999, forces 24-hour mode, keeps RTC values, and enables wakeup.

## Control flow
The driver gates read/set sequences with the enable bit to avoid racing hardware updates. Probe enables clocks before touching hardware and unwinds them on failures. Suspend/resume only toggles IRQ wake when the device is wake-capable.

## State and persistence behavior
Hardware holds date/time, alarm date/time, enabled state, event flags, and keep-RTC configuration. Software state is limited to clock handles and MMIO pointers. Alarm enabled state is read from hardware only implicitly through register masks, not cached.

## Dependencies and integration points
Depends on platform devices, OF, MMIO, `clk`, `bitfield`, RTC class, interrupt handling, and PM wake IRQ support. Registers as a platform driver named `"cdns-rtc"`.

## Risks
- Reference clock acceptance is strict: only 1 Hz or 100 Hz is allowed.
- `cdns_rtc_read_time()` returns `-EINVAL` if the RTC is disabled, so boot firmware state matters.
- Alarm read returns only day/month and time, not year or enabled/pending fields.
- Set loops retry only three times before `-EIO`.

## Test signals
Probe with valid/invalid ref clocks, read/set across century boundaries, alarm set/read/IRQ delivery, wake from suspend, and injected invalid status flag failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cadence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cmos.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cmos.c

## Purpose
PC-style MC146818/CMOS RTC class driver for platform/ACPI/OF systems. It provides time read/set, alarm support from one day to one year depending on hardware/FADT registers, interrupt handling including HPET emulation and ACPI fixed events, NVRAM export, and suspend/poweroff wake behavior.

## Important APIs, types, and functions
- `struct cmos_rtc` stores the singleton RTC device, parent device, IRQ, claimed I/O or memory resource, alarm expiration, wake callbacks, suspend control state, enhanced alarm registers, century register, and a saved wake alarm.
- `cmos_read_time()` and `cmos_set_time()` delegate to MC146818 helpers and respect `pm_trace_rtc_valid()`.
- `cmos_read_alarm()` uses `mc146818_avoid_UIP()` and a callback to safely read alarm registers, then decodes BCD or binary mode and marks unsupported fields as `-1`.
- `cmos_validate_alarm()` enforces alarm offset limits based on day/month alarm register availability.
- `cmos_set_alarm()` converts alarm fields to BCD or binary, writes under `mc146818_avoid_UIP()`, updates HPET alarm glue if used, and caches `alarm_expires`.
- `cmos_irq_enable()` and `cmos_irq_disable()` update `RTC_CONTROL`, coordinate HPET bits, optional ACPI wake event callbacks, and status flushing.
- `cmos_interrupt()` reads and clears `RTC_INTR_FLAGS`, masks against enabled IRQ bits or suspended control state, implements one-shot AIE behavior, and reports `rtc_update_irq()`.
- ACPI helpers install/remove `ACPI_EVENT_RTC` handling, choose `use_acpi_alarm` based on FADT and DMI-era quirks, and populate enhanced alarm/century register numbers.
- `cmos_nvram_read/write()` expose CMOS NVRAM while skipping RTC alarm/century registers on writes.
- `cmos_do_probe()` enforces singleton registration, claims register resources, initializes board/ACPI alarm metadata, sets frequency defaults, requests real or HPET IRQ handlers, registers RTC and NVRAM, and installs ACPI event handling.
- Suspend/resume and shutdown paths save/restore alarm state, enable wake, handle ACPI wake status, and avoid buggy immediate reboot behavior around AIE poweroff.

## Control flow
Initialization uses `platform_driver_probe()` and a singleton global `cmos_rtc`. All direct CMOS accesses must occur with interrupts disabled under global `rtc_lock`, which coordinates with other architecture code and legacy CMOS users. Alarm reads/writes are wrapped with UIP avoidance because some Intel chipsets disconnect alarm registers during updates. Runtime IRQ flow clears flags first, masks to enabled IRQs, disables AIE for one-shot semantics, and then reports to the RTC core. PM flow disables non-wake IRQ sources during suspend, optionally enables wake IRQ or ACPI fixed events, saves current wake alarm, restores BIOS-modified alarms on resume, and re-enables prior interrupt bits.

## State and persistence behavior
Persistent state lives in CMOS RTC/NVRAM registers, including time, alarm, century, control/frequency registers, and firmware-used NVRAM. Software keeps singleton resource ownership, selected alarm register layout, cached expiration, saved alarm for PM restore, and suspend control bits. NVRAM writes intentionally avoid known RTC fields to prevent corrupting alarm/century state.

## Dependencies and integration points
Depends on `linux/mc146818rtc.h`, global `rtc_lock`, platform resources, optional ACPI fixed events, optional HPET RTC emulation, optional OF initialization properties, x86 DMI/legacy IRQ logic, PM, NVRAM, procfs, and RTC core. Binds via platform driver name `"rtc_cmos"`, ACPI IDs from `ACPI_CMOS_RTC_IDS`, and OF compatible `"motorola,mc146818"`.

## Risks
- This driver is a singleton and shares registers with firmware, architecture code, userspace, NVRAM, and possibly HPET emulation; lock discipline is critical.
- Alarm capability varies widely: no IRQ, ACPI-only alarm, one-day basic alarm, enhanced day/month alarm, and HPET limitations all affect behavior.
- BIOS/firmware may alter alarms during suspend; resume restore logic is complex.
- CMOS NVRAM writes can affect firmware checksums; the driver deliberately leaves checksum ownership to userspace.
- Poweroff wake/AIE handling contains platform workarounds for buggy automatic reboot behavior.

## Test signals
Read/set time with BCD and binary modes, alarm validation for one-day/month/year limits, IRQ delivery via native IRQ and HPET emulation, ACPI fixed event wake, suspend/resume alarm restore, NVRAM bounds and skipped registers, platform resource conflicts, and no-IRQ systems exposing no alarm feature unless ACPI alarm is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cmos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-core.h -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-core.h

## Purpose
Internal RTC core header that declares or stubs optional RTC character-device, procfs, and sysfs integration hooks based on kernel configuration.

## Important APIs, types, and functions
- Under `CONFIG_RTC_INTF_DEV`, declares `rtc_dev_init()` and `rtc_dev_prepare(struct rtc_device *rtc)`; otherwise provides empty inline stubs.
- Under `CONFIG_RTC_INTF_PROC`, declares `rtc_proc_add_device()` and `rtc_proc_del_device()`; otherwise provides empty inline stubs.
- Under `CONFIG_RTC_INTF_SYSFS`, declares `rtc_get_dev_attribute_groups()` returning attribute group arrays; otherwise returns `NULL`.

## Control flow
There is no runtime logic beyond compile-time selection. RTC core users can call these helpers unconditionally and rely on no-op stubs when optional interfaces are disabled.

## State and persistence behavior
No state is stored here. It only controls symbol visibility and optional subsystem integration at compile time.

## Dependencies and integration points
Depends on `struct rtc_device` being visible to includers. Integrates RTC core internals with dev node setup, proc registration, and sysfs attribute grouping.

## Risks
The main risk is configuration skew: code that assumes dev/proc/sysfs side effects must tolerate no-op stubs when options are disabled.

## Test signals
Build coverage for `CONFIG_RTC_INTF_DEV`, `CONFIG_RTC_INTF_PROC`, and `CONFIG_RTC_INTF_SYSFS` enabled and disabled; runtime checks that optional interfaces appear only when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cpcap.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cpcap.c

## Purpose
Motorola CPCAP PMIC RTC platform driver. It exposes the PMIC day/time-of-day counters and alarm registers through the RTC class and requests both alarm and 1 Hz update interrupts, with the update IRQ deliberately disabled to avoid unnecessary wakeups.

## Important APIs, types, and functions
- `struct cpcap_time` represents PMIC split time as day plus two TOD register fragments.
- `struct cpcap_rtc` stores parent regmap, RTC device, vendor ID, alarm/update IRQs, and software IRQ-enable booleans.
- `cpcap2rtc_time()` and `rtc2cpcap_time()` convert between PMIC day/TOD fields and `rtc_time`.
- `cpcap_rtc_read_time()` samples `TOD2`, `DAY`, `TOD1`, `TOD2` and rereads day if rollover is detected.
- `cpcap_rtc_set_time()` disables active IRQs, writes time registers in vendor-specific order, then restores IRQs.
- Alarm ops read/write `DAYA/TODA2/TODA1` and control alarm IRQ state through `cpcap_rtc_alarm_irq_enable()`.
- IRQ handlers report `RTC_AF` and `RTC_UF`.
- Probe obtains parent regmap, vendor, IRQs, initializes wakeup, sets range from day mask, requests threaded IRQs, disables both initially, and registers the RTC.

## Control flow
The driver uses regmap for all PMIC access. Time setting is the highest-risk path because ST and non-ST vendors require different register write ordering to avoid inconsistent counters.

## State and persistence behavior
Time and alarm persist in CPCAP registers. Software tracks whether alarm/update IRQs are enabled because the IRQ framework state is not directly queried. The day field is 15-bit, so range is `(DAY_MASK + 1) * 86400 - 1`.

## Dependencies and integration points
Depends on parent Motorola CPCAP MFD regmap, CPCAP register definitions, platform IRQ resources, RTC class, and wakeup support. Binds to OF compatible `"motorola,cpcap-rtc"`.

## Risks
- `ret |= regmap_read/update_bits` combines errors; any nonzero result becomes generic `-EIO` in read paths and can obscure the first error.
- Alarm `set_alarm()` enables the IRQ on success regardless of `alrm->enabled`, which is worth testing against RTC core expectations.
- Time write ordering is vendor-sensitive and can break if vendor detection is wrong.
- Update IRQ is requested only to mask/own it; enabling it later depends on software state.

## Test signals
Vendor-specific set-time tests, rollover read around `TOD2`, alarm enable/disable and IRQ delivery, update IRQ staying disabled by default, wakeup initialization, and regmap error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cpcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cros-ec.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cros-ec.c

## Purpose
ChromeOS Embedded Controller RTC driver. It translates RTC class operations into EC host commands for current time and relative alarm management, and listens for EC host events to report RTC alarm interrupts.

## Important APIs, types, and functions
- `struct cros_ec_rtc` stores the EC pointer, RTC device, EC event notifier, and a saved absolute alarm value used across IRQ enable/disable.
- `cros_ec_rtc_get()` and `cros_ec_rtc_set()` wrap `cros_ec_cmd_xfer_status()` for `EC_CMD_RTC_*` commands.
- `cros_ec_rtc_read_time()` and `set_time()` map EC 32-bit seconds to/from `rtc_time`.
- Alarm read/set convert between RTC absolute alarm time and EC relative alarm offsets; disabled alarms send `EC_RTC_ALARM_CLEAR`.
- `cros_ec_rtc_alarm_irq_enable()` saves the current alarm when disabling and restores it if still in the future when enabling.
- `cros_ec_rtc_event()` checks `EC_HOST_EVENT_RTC` and calls `rtc_update_irq()`.
- Probe validates initial EC time read, initializes wakeup, registers RTC with `range_max = U32_MAX`, probes old EC 24-hour alarm limit, clears test alarm, registers RTC, and subscribes to EC notifier.

## Control flow
All hardware communication is synchronous host-command traffic to the parent EC. Alarm operations always read current EC time first because EC alarm commands are relative. The notifier path is asynchronous and translates EC host events into RTC alarm interrupts.

## State and persistence behavior
Time and active alarm live in EC firmware. Software stores `saved_alarm` only when RTC core disables alarm IRQs, so it can restore a future alarm later. Range is limited to 32-bit seconds.

## Dependencies and integration points
Depends on ChromeOS EC protocol/data structures, platform child device model, blocking notifier chain, PM wake IRQ via parent EC IRQ, and RTC class. Binds to platform ID `"cros-ec-rtc"`.

## Risks
- EC alarms are relative; races between reading current time and setting an offset can shift the alarm by command latency.
- Old EC firmware may reject offsets beyond 24 hours; probe detects this by attempting a two-day alarm.
- `saved_alarm` logic must handle wrap and past alarms correctly.
- Alarm read does not set `enabled` or `pending`, only computes the time.

## Test signals
Host-command mocks for get/set/read alarm, old firmware 24-hour alarm detection, EC host event delivery, suspend/resume wake via parent EC IRQ, alarm disable/restore behavior, and U32 range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cros-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cv1800.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cv1800.c

## Purpose
Sophgo CV1800 RTC platform driver. It exposes a syscon/regmap-backed seconds counter and alarm register as a 32-bit-range RTC.

## Important APIs, types, and functions
- `struct cv1800_rtc_priv` stores RTC device, parent regmap, enabled clock, and alarm IRQ.
- `cv1800_rtc_enabled()` checks `SEL_SEC_PULSE` in `SEC_PULSE_GEN`; `cv1800_rtc_enable()` selects internally generated second pulses.
- `cv1800_rtc_read_time()` reads `SEC_CNTR_VAL` and returns `-EINVAL` if not enabled.
- `cv1800_rtc_set_time()` writes `SET_SEC_CNTR_VAL`, triggers `SET_SEC_CNTR_TRIG`, mirrors seconds into `MACRO_RG_SET_T`, and enables the RTC.
- Alarm ops read/write `ALARM_TIME` and `ALARM_ENABLE`.
- `cv1800_rtc_irq_handler()` reports `RTC_AF` and disables the alarm.
- Probe gets parent syscon regmap and parent `"rtc"` clock, enables wakeup, requests a high-trigger alarm IRQ, sets `range_max = U32_MAX`, and registers the RTC.

## Control flow
The driver relies on the parent node regmap rather than mapping its own resource. Setting time also initializes persistent backup-domain macro state and enables internal second pulses.

## State and persistence behavior
Time, alarm, enable, and macro retention fields live in the parent RTC register block. Software state is minimal. Alarm IRQ is one-shot in practice because the handler writes `ALARM_ENABLE = 0`.

## Dependencies and integration points
Depends on parent MFD/syscon regmap, parent `"rtc"` clock, platform IRQ, RTC class, and wakeup support. Binds by platform device ID `"cv1800b-rtc"` with driver name `"sophgo-cv1800-rtc"`.

## Risks
- Regmap read/write return values are mostly ignored after probe, so bus/register failures may be silent.
- `alarm_irq_enable()` writes the raw `enabled` value rather than masking to bit 0.
- Range is 32-bit seconds, and alarm time is truncated to `u32` on read.
- Driver has no PM callbacks despite calling `device_init_wakeup()`.

## Test signals
Parent regmap/clock probe failures, read before enable returning `-EINVAL`, set/read time round trip, alarm IRQ one-shot behavior, and wakealarm exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-cv1800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9052.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9052.c

## Purpose
Dialog DA9052 PMIC RTC driver. It exposes PMIC count/alarm registers through RTC class operations and wires the PMIC alarm IRQ to `rtc_update_irq()`.

## Important APIs, types, and functions
- `struct da9052_rtc` stores RTC device and parent DA9052 MFD pointer.
- `da9052_rtc_enable_alarm()` toggles alarm-on and tick-on bits in `DA9052_ALARM_Y_REG`.
- `da9052_read_alarm()` and `da9052_rtc_read_time()` use repeated group reads until two consecutive register snapshots match, avoiding rollover races.
- `da9052_set_alarm()` rounds any nonzero seconds up to the next minute, then writes minute/hour/day/month/year alarm fields.
- `da9052_rtc_set_time()` validates the 2000-2063 year range and writes six count registers.
- Probe configures battery charging, disables tick alarm, initializes wakeup, allocates/registers RTC with range 2000-2063, and requests the DA9052 ALARM IRQ.

## Control flow
Read operations use double-read retry loops with 20 ms sleeps and five retries. Setting an alarm always disables the alarm, writes fields, and re-enables it. The IRQ handler only reports `RTC_AF`.

## State and persistence behavior
Time and alarm state persist in PMIC registers. Software does not cache alarm enabled state. Alarm resolution is effectively one minute for the AD register layout because seconds are forced to zero.

## Dependencies and integration points
Depends on DA9052 MFD register helpers, platform device child, RTC class, PM wake capability, and DA9052 IRQ registration.

## Risks
- `BUG_ON(rtc_tm->tm_sec)` after rounding is harsh for a driver path and assumes conversion cannot fail.
- Double-read loops can return `-EIO` under register rollover or bus instability.
- Battery charging setup writes a fixed `0xFE` without policy visible in this file.
- No remove/free for `da9052_request_irq()` is visible here, so ownership depends on the parent helper.

## Test signals
Repeated-read stabilization around rollovers, alarm second rounding, 2063 boundary validation, PMIC IRQ delivery, battery-charge register setup, and failed group read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9052.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9055.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9055.c

## Purpose
Dialog DA9055 PMIC RTC driver. It initializes PMIC RTC power/crystal modes, exposes time and alarm operations, handles alarm IRQs, and preserves alarm state across PM transitions.

## Important APIs, types, and functions
- `struct da9055_rtc` stores RTC device, parent PMIC pointer, and software `alarm_enable`.
- `da9055_rtc_enable_alarm()` updates `DA9055_RTC_ALM_EN` and mirrors the enabled state in software.
- Time/alarm helpers read/write PMIC register groups and decode masked year/month/day/hour/min/sec fields.
- `da9055_rtc_read_time()` first checks `DA9055_RTC_READ`; if not asserted it returns `-EBUSY`.
- `da9055_rtc_device_init()` enables RTC, 32 kHz crystal, power-down RTC mode, optional reset-mode behavior from platform data, and disables tick wake bits.
- Probe initializes hardware, detects preexisting alarm enable state, enables wakeup, registers RTC, and requests threaded `"ALM"` IRQ.
- PM callbacks disable alarm when it is not a wake source, re-enable it on resume/thaw/restore if previously active, and freeze disables it unconditionally.

## Control flow
Alarm IRQ disables the alarm before reporting `RTC_AF`. Setting an alarm disables first, writes fields, then re-enables. PM policy separates wake-capable alarms from ordinary alarms to avoid unwanted wakeups.

## State and persistence behavior
PMIC registers persist time/alarm and mode bits. Software `alarm_enable` mirrors desired alarm state across PM callbacks. Time range is constrained by PMIC year field but not explicitly assigned to `rtc->range_*` in this driver.

## Dependencies and integration points
Depends on DA9055 MFD core/register/platform-data headers, platform IRQ named `"ALM"`, RTC class, and PM callbacks.

## Risks
- Set-time lacks explicit year validation despite a limited PMIC year field.
- `alarm_enable` can diverge if register updates fail after partial state changes.
- `set_alarm()` always re-enables the alarm, ignoring `alrm->enabled`.
- Probe uses older `devm_rtc_device_register()` style and returns IRQ request errors only if request itself fails.

## Test signals
RTC_READ busy path, PM suspend/resume with and without wakeup, alarm IRQ one-shot behavior, platform reset mode, year boundary writes, and disabled-alarm `set_alarm()` semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9055.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9063.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9063.c

## Purpose
Dialog DA9063/DA9062 compatible PMIC RTC driver. It abstracts register differences across variants, exposes time/alarm operations, enables the RTC and crystal, and uses an optional ALARM IRQ as a wake IRQ.

## Important APIs, types, and functions
- `struct da9063_compatible_rtc_regmap` maps register addresses, masks, and alarm layout for DA9063 AD, DA9063 BB, and DA9062 AA.
- `struct da9063_compatible_rtc` stores RTC device, cached alarm time, parent regmap, selected config, and `rtc_sync` flag.
- `da9063_data_to_tm()` and `da9063_tm_to_data()` convert masked raw register arrays to/from `rtc_time`.
- `da9063_rtc_read_time()` bulk-reads count registers, requires the ready-to-read bit, and contains a synchronization workaround that can return cached alarm time when an alarm fired one second ahead.
- `da9063_rtc_set_time()` bulk-writes count registers.
- Alarm ops read/write variant-specific alarm layouts and toggle the alarm-on bit.
- `da9063_alarm_event()` disables alarm, marks `rtc_sync`, and reports `RTC_AF`.
- Probe selects config from OF/variant, enables RTC and 32 kHz oscillator, clears alarm/tick state, initializes cached alarm, sets minute-resolution feature for AD layout, requests optional threaded ALARM IRQ, configures wake IRQ, and registers RTC with range 2000-2063.

## Control flow
All register access goes through parent regmap and selected config. Alarm setup disables first, writes raw fields starting at the variant-specific offset, caches the programmed alarm time, then optionally enables. IRQ handling is one-shot.

## State and persistence behavior
PMIC registers persist time, alarm, enable, crystal, and event bits. Software caches the most recently programmed alarm and `rtc_sync` to compensate for hardware synchronization delay after an alarm event.

## Dependencies and integration points
Depends on DA9062/DA9063 MFD register definitions, OF match data, parent regmap, platform IRQ by name `"ALARM"`, `dev_pm_set_wake_irq()`, and RTC class.

## Risks
- Many masks/register layouts are variant-specific; wrong match data corrupts time/alarm fields.
- `regmap_update_bits()` in probe uses `DA9063_ALARM_STATUS_ALARM` directly in one place instead of the config status mask, so variant assumptions need testing.
- Optional IRQ absence clears the alarm feature; non-ENXIO errors abort probe.
- Synchronization workaround changes read-time behavior immediately after alarms.

## Test signals
Probe each variant, ready-to-read false path, range validation, minute-resolution feature on AD config, optional IRQ/no-IRQ feature flags, wake IRQ setup, alarm IRQ read-time synchronization, and regmap failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9063.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-digicolor.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-digicolor.c

## Purpose
Conexant Digicolor RTC platform driver. It exposes a command-driven MMIO RTC that stores a reference value plus a running time counter and alarm offset.

## Important APIs, types, and functions
- `struct dc_rtc` stores RTC device and MMIO base.
- `dc_rtc_cmds()` writes command codes with `GO_BUSY` and polls until hardware clears busy.
- `dc_rtc_read()` issues read/nop commands, reads reference and stable time counter by repeated sampling, and returns `reference + time`.
- `dc_rtc_write()` writes a reference value and sends write/nop/reset/nop commands.
- RTC ops convert between seconds and `rtc_time`, read/write alarm offset relative to reference, and toggle interrupt enable.
- `dc_rtc_irq()` clears the interrupt flag and reports `RTC_AF`.
- Probe maps MMIO, allocates RTC, requests IRQ, sets `range_max = U32_MAX`, and registers the RTC.

## Control flow
All time reads and writes pass through explicit hardware command sequences. Alarm programming is simpler: it directly writes `ALARM` as target time minus current reference and enables/disables the interrupt byte.

## State and persistence behavior
Hardware stores reference seconds, elapsed counter, alarm offset, interrupt enable, and interrupt flag. Software stores only MMIO and RTC pointers.

## Dependencies and integration points
Depends on platform MMIO, `readb_relaxed_poll_timeout()`, RTC class, IRQ framework, and OF compatible `"cnxt,cx92755-rtc"`.

## Risks
- Command polling timeout is large (`500 * 10 ms`), so hung hardware can stall operations for seconds.
- Alarm pending calculation uses `alarm_reg + reference > now`, which describes future scheduled alarms rather than a latched interrupt flag.
- Alarm set with a target before reference underflows into a large `u32` offset.
- No PM/wakeup support is implemented.

## Test signals
Command timeout injection, stable double-read behavior, time set/read round trip, past alarm programming, IRQ clear/report, and interrupt enable toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-digicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1216.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1216.c

## Purpose
Dallas DS1216 RTC platform driver. It accesses a serial bit-stream clock embedded behind a memory-mapped register, using a magic sequence to switch the device into clock mode.

## Important APIs, types, and functions
- `struct ds1216_regs` maps the eight clock bytes including fractional seconds.
- `struct ds1216_priv` stores RTC device and MMIO base.
- `magic[]` is the 64-bit sequence used by `ds1216_switch_ds_to_clock()`.
- `ds1216_read()` and `ds1216_write()` shift 64 bits through the least significant bit of the mapped register.
- `ds1216_rtc_read_time()` switches to clock mode, reads registers, decodes BCD and 12/24-hour mode, and maps years below 70 to 2000+.
- `ds1216_rtc_set_time()` preserves the 12/24-hour mode bit, clears fractional seconds, writes BCD fields, and switches/writes back.
- Probe maps resource, registers RTC, and performs a dummy read to put the clock into a known state.

## Control flow
Every read/write begins by resetting the DS1216 pointer and writing the magic sequence. Set-time reads the existing register block first to preserve mode bits before writing the updated block.

## State and persistence behavior
All clock state persists in DS1216 hardware. Software stores only MMIO and RTC pointers. Fractional seconds are cleared on set-time.

## Dependencies and integration points
Depends on platform MMIO, BCD helpers, and RTC class. Binds through platform alias `"rtc-ds1216"`.

## Risks
- Month handling appears one-based on read and write without the usual `tm_mon - 1/+1` adjustment, so month indexing deserves targeted verification.
- Weekday write uses raw `tm_wday` while read subtracts one from hardware field.
- Bit-banged MMIO has no locking; concurrent RTC core calls rely on framework serialization.
- No validity or oscillator failure checks.

## Test signals
Read/write round trips for month and weekday, 12-hour and 24-hour modes, year 1969/1970/2000 boundaries, dummy-read probe behavior, and MMIO read/write ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1216.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1286.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1286.c

## Purpose
Dallas DS1286 RTC platform driver. It exposes time, limited alarm, proc diagnostics, watchdog interrupt ioctl toggles, and alarm IRQ enable through raw memory-mapped registers.

## Important APIs, types, and functions
- `struct ds1286_priv` stores RTC device, raw register base, and spinlock.
- `ds1286_rtc_read/write()` access 8-bit values through 32-bit raw register slots.
- `ds1286_read_time()` waits briefly if transfer-enable/update is active, locks, sets `RTC_TE`, reads fields, restores command, decodes BCD, and applies DS1286-specific year mapping.
- `ds1286_set_time()` validates years from 1970 through hardware range, encodes year as offset from 1940 modulo 100, writes fields under lock, and clears hundredths.
- `ds1286_read_alarm()` reads minute/hour/weekday alarm fields; `set_alarm()` supports minute/hour matching and rejects nonzero seconds.
- `ds1286_alarm_irq_enable()` toggles `RTC_TDM`; ioctl toggles watchdog alarm mask `RTC_WAM` when RTC device interface is enabled.
- `ds1286_proc()` reports oscillator, square wave, alarm mode, watchdog/alarm flags, interrupt mode, and pin polarity.
- Probe maps registers, initializes spinlock, and registers RTC.

## Control flow
Register updates are guarded by a driver spinlock. Read and set time temporarily set transfer-enable state to freeze or access registers consistently, then restore the command register.

## State and persistence behavior
Hardware stores time, command bits, alarm fields, watchdog/alarm flags, oscillator settings, and interrupt modes. Software stores only register mapping and lock.

## Dependencies and integration points
Depends on platform MMIO, `linux/rtc/ds1286.h`, BCD helpers, optional RTC dev ioctl, optional procfs, and RTC class.

## Risks
- Alarm support is partial: only minute/hour/weekday fields, no full date, and seconds must be zero.
- Busy-wait around update uses jiffies/barrier instead of sleep.
- Year conversion is unusual and hardware-specific, needing boundary tests.
- Raw MMIO width/layout assumptions must match platform wiring.

## Test signals
Year boundary set/read, alarm wildcard behavior for invalid hour/minute, ioctl mask toggles, proc output fields, spinlock coverage under concurrent ops, and memory resource probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1286.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1302.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1302.c

## Purpose
Dallas/Maxim DS1302 SPI RTC driver. It provides basic clock burst read/write operations and validates enough control-register behavior during probe to detect the chip.

## Important APIs, types, and functions
- Register constants encode DS1302 shifted address plus read/write command bits.
- `ds1302_rtc_set_time()` first writes the control register to enable writes, then sends an eight-byte clock burst ending with write-disable.
- `ds1302_rtc_get_time()` reads a clock burst and decodes BCD fields into a 2000-based year.
- `ds1302_probe()` validates SPI word length, speed, and mode, reads the control register, retries suspicious values, writes write-disable if needed, verifies detection, stores the SPI device as driver data, and registers the RTC.

## Control flow
All time operations use stack buffers and `spi_write_then_read()` to avoid nonportable DMA from arbitrary stack segments. Probe rejects incompatible SPI configuration before any RTC registration.

## State and persistence behavior
Time and write-protect state persist in DS1302 registers. The driver stores the `spi_device` as its own driver data; no private struct is needed.

## Dependencies and integration points
Depends on SPI, RTC class, BCD helpers, optional OF compatible `"maxim,ds1302"`, and SPI device ID `"ds1302"`.

## Risks
- No alarm, RAM, or trickle charger support despite constants for RAM/TCR.
- The driver assumes 2000+ years and does not expose range metadata.
- SPI mode requirements are validated only for CPHA and speed; board polarity assumptions rely on board setup.
- No oscillator halt/validity checks.

## Test signals
Probe rejection for bad bits-per-word, excessive speed, and CPHA; control-register detection path; clock burst read/write round trip; and write-protect behavior after set-time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1302.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1305.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1305.c

## Purpose
DS1305/DS1306 SPI RTC driver. It supports basic time, one-day alarm using ALM0, optional interrupt handling through a workqueue, proc trickle-charge reporting, and 96 bytes of NVRAM through RTC nvmem.

## Important APIs, types, and functions
- `struct ds1305` stores SPI device, RTC device, work item, exit flag, 12-hour mode flag, and cached control/status/trickle registers.
- `bcd2hour()` and `hour2bcd()` support both 24-hour and 12-hour AM/PM hardware modes.
- `ds1305_get_time()` and `set_time()` perform burst SPI transfers for seven BCD time registers, using year range 2000-2099.
- `ds1305_get_alarm()` refreshes control/status cache, reports ALM0 enabled/pending, reads ALM0 registers, and rejects disabled match fields for second/minute/hour.
- `ds1305_set_alarm()` reads current time, enforces future alarm within `rtc->alarm_offset_max`, disables ALM0, writes second/minute/hour with weekday disabled, and optionally re-enables.
- `ds1305_alarm_irq_enable()` updates cached control and writes `DS1305_AEI0`.
- `ds1305_irq()` disables IRQ and schedules `ds1305_work()`, which clears alarm enables/status under `rtc_lock`, re-enables IRQ unless exiting, and reports `RTC_AF`.
- `ds1305_nvram_read/write()` build two-transfer SPI messages for NVRAM.
- Probe validates SPI mode/speed/platform data, reads control registers, configures oscillator/write-protect/trickle settings, registers RTC/NVRAM, sets alarm offset to under one day, and requests IRQ if present.

## Control flow
The driver caches control registers because alarm enable and status are interdependent. IRQ work is deferred to process context so it can use RTC locking and SPI I/O safely. Alarm programming is serialized by the RTC core ops lock as documented in comments.

## State and persistence behavior
Hardware stores time, alarms, control/status, trickle charger, and NVRAM. Software caches control/status/trickle bytes and 12-hour mode, and uses `FLAG_EXITING` during removal to avoid re-enabling IRQ after shutdown.

## Dependencies and integration points
Depends on SPI, `linux/spi/ds1305.h` platform data, RTC class, workqueues, nvmem, optional procfs, and IRQ framework.

## Risks
- Alarm range is intentionally limited to less than one day because weekday matching is disabled.
- Cached control registers can become stale if external masters modify the chip.
- IRQ clear behavior assumes ALM0/ALM1 status relationships described in comments.
- Probe setup must preserve board-specific trickle settings and write-protect behavior.

## Test signals
12/24-hour round trips, alarm range errors, IRQ workqueue clear/report, NVRAM read/write bounds, trickle proc output, SPI setup validation, and removal while IRQ work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1307.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1307.c

## Purpose
Large compatibility I2C RTC driver for DS1307-family and similar chips, including DS1307/1308/1337/1338/1339/1340/1341/1388/3231, M41T variants, MCP794xx, RX8025, RX8130, PT7C4338, and ISL12057 mappings. It handles core timekeeping, variant alarms, oscillator/status quirks, trickle charger setup, NVRAM, M41T offset/frequency test, DS3231 hwmon and common-clock outputs, and DS1388 watchdog support.

## Important APIs, types, and functions
- `enum ds_type` identifies supported chip families.
- `struct ds1307` stores variant type, device, regmap, name, RTC device, and optional common-clock hardware.
- `struct chip_desc` records per-variant alarm support, NVRAM offset/size, register offset, century handling, backup square-wave bits, IRQ handler, RTC ops table, trickle charger register/setup callback, and charger policy flags.
- `ds1307_get_time()` bulk-reads seven time registers at variant offset, validates oscillator/status bits per chip, decodes BCD date/time, handles RX8130 weekday bit-position format, and optional century support.
- `ds1307_set_time()` validates range, encodes BCD fields, sets century bits where available, clears oscillator-failure bits for several variants, starts MCP794xx oscillator/VBAT, writes the register block, and clears RX8130 voltage-loss flag.
- DS1337-style alarm ops read/write ALARM1/ALARM2/status/control registers and use A1IE/A1I.
- RX8130 alarm ops use minute/hour/day alarm registers, extension/flag/control registers, minute precision, and `rx8130_irq()`.
- MCP794xx alarm ops use alarm 0 registers, compute weekday from current RTC time, clear interrupt flag, and toggle `MCP794XX_BIT_ALM0_EN`.
- `m41txx_rtc_read_offset()` and `set_offset()` expose calibration offset in ppb using positive/negative step sizes.
- DS1388 watchdog ops start/stop/ping/set timeout through watchdog registers and register a watchdog device when enabled.
- `chips[]`, `ds1307_id[]`, and `ds1307_of_match[]` map device IDs/OF compatibles to variant descriptors.
- `ds1307_irq()` handles generic DS1337-like alarm IRQs by clearing status and disabling A1IE.
- `frequency_test` sysfs group is added for M41T variants.
- `ds1307_nvram_read/write()` expose variant NVRAM ranges via RTC nvmem.
- `ds1307_trickle_init()` interprets `trickle-resistor-ohms`, `aux-voltage-chargeable`, and deprecated `trickle-diode-disable`.
- DS3231 hwmon reads temperature registers in 0.25 C units.
- DS3231 common-clock support registers square-wave and 32 kHz clocks, avoiding SQW registration when the alarm feature uses the shared pin.
- `ds1307_probe()` creates regmap, selects variant, configures trickle charging, initializes oscillator/control/status quirks, converts 12-hour to 24-hour mode where needed, sets alarm/wakeup feature flags, requests IRQ, registers RTC, NVRAM, hwmon, clocks, and watchdog.

## Control flow
Probe is variant-driven: identify chip, apply optional charger setup, handle variant-specific oscillator/control/status cleanup, read base time registers, normalize hour mode, allocate/register RTC, request IRQ if alarm-capable, then attach optional subsystems. Runtime calls are selected by `chip_desc.rtc_ops` or the generic DS13xx ops. Alarm IRQ paths clear status and disable the alarm to preserve one-shot RTC semantics.

## State and persistence behavior
Persistent state lives in chip registers: time, status/oscillator flags, alarms, control bits, trickle charger, NVRAM/SRAM, calibration, temperature registers, clock-output enable bits, and watchdog registers. Software stores variant metadata, regmap, RTC device, and common-clock handles. Several paths update persistent status bits during probe or set-time, such as clearing oscillator failure flags and enabling battery-backed oscillator bits.

## Dependencies and integration points
Depends on I2C, regmap, RTC class, device properties/OF, nvmem, optional hwmon, optional common clock provider, optional watchdog core, and BCD helpers. Integration is broad: I2C ID table, OF compatible table, optional wakeup-source property, IRQs, RTC features, sysfs attributes, nvmem registration, hwmon registration, clock provider, and watchdog registration.

## Risks
- Very broad variant surface creates high regression risk from shared code changes.
- Oscillator-failure handling differs by chip; some reads return `-EINVAL`, some only warn/clear during probe/set-time.
- Century support depends on build option and chip bits; range is 2000-2099 unless century support and hardware allow beyond.
- Alarm semantics vary by variant: DS1337 full second/min/hour/day, RX8130 minute precision, MCP794xx computed weekday, shared SQW/alarm pin conflicts.
- Trickle charger DT settings can alter battery/supercap charging policy and must match hardware.
- Optional subsystems may silently not register on configuration or hardware constraints.
- The source shown contains duplicated-looking declarations in `ds1307_probe()` in this tree snapshot; compilation should confirm whether this is an artifact or actual issue.

## Test signals
Variant matrix probe tests, oscillator failure flags, set/read time across 1999/2099/2100 boundaries with/without century config, each alarm implementation and IRQ path, wakeup-source without IRQ, NVRAM read/write offsets, M41T offset and frequency_test sysfs, DS3231 temperature and clocks, DS1388 watchdog lifecycle, trickle charger DT permutations, and regmap error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1307.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1343.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1343.c

## Purpose
Dallas/Maxim DS1343/DS1344 SPI RTC driver. It provides time, alarm, sysfs glitch-filter/trickle charger visibility, NVRAM, IRQ wake support, and PM wake handling.

## Important APIs, types, and functions
- `struct ds1343_priv` stores RTC device, regmap, and IRQ.
- Sysfs attributes `glitch_filter` and `trickle_charger` read/update `DS1343_CONTROL_REG` and report trickle charger configuration.
- `ds1343_nvram_read/write()` expose 96 bytes starting at `DS1343_NVRAM`.
- Time ops bulk read/write seven BCD registers, using range 2000-2099.
- Alarm ops require an IRQ, read pending/enabled from status/control, read/write ALM0 second/min/hour/day, and toggle A0IE.
- `ds1343_thread()` handles alarm IRQ in threaded context, clears `IRQF0`, reports `RTC_AF`, and disables A0IE under `rtc_lock()`.
- Probe configures SPI mode 3 and inverted CS-high handling, initializes regmap, enables INTCN, disables oscillator stop and alarms, clears status flags, registers sysfs group/RTC/NVRAM, requests threaded IRQ, and enables wake IRQ.
- PM callbacks enable/disable IRQ wake when the device may wake.

## Control flow
Probe normalizes control/status registers before RTC registration. Alarm IRQs are one-shot: status is cleared and A0IE is disabled. Sysfs and RTC ops share the same regmap.

## State and persistence behavior
Hardware stores BCD time, alarm, control/status, trickle charger, glitch filter, and NVRAM. Software stores IRQ availability. Wake ability is attached only when IRQ request succeeds.

## Dependencies and integration points
Depends on SPI, regmap, RTC, nvmem, PM wake IRQ helpers, sysfs attribute groups, and SPI IDs `"ds1343"`/`"ds1344"`.

## Risks
- SPI chip-select polarity adjustment is unusual (`mode ^= SPI_CS_HIGH`) and board-definition sensitive.
- Alarm operations return `-EINVAL` without IRQ, so feature exposure depends on IRQ presence.
- `rtc_add_group()` failure is logged but not fatal.
- Sysfs string parsing for glitch filter accepts only exact prefixes.

## Test signals
SPI mode/CS setup, alarm IRQ threaded one-shot behavior, sysfs glitch_filter read/write, trickle charger display cases, NVRAM access, PM wake enable/disable, and no-IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1343.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1347.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1347.c

## Purpose
Dallas DS1347 low-current SPI RTC driver. It exposes basic time read/set through regmap and disables write protection during probe.

## Important APIs, types, and functions
- Regmap access table limits writable/register access to the DS1347 time/control/status range.
- `ds1347_read_time()` checks oscillator-stop flag, reads a clock burst plus century register, rereads seconds until the burst is consistent, and decodes year as `century * 100 + year - 1900`.
- `ds1347_set_time()` sets `NEOSC`, writes a clock burst and century register, then clears `NEOSC` and `OSF`.
- Probe configures SPI mode 3 and 8 bits, initializes SPI regmap with read flag `0x80`, disables write protect, allocates RTC, sets range 0000-9999, and registers it.

## Control flow
Reads use a consistency loop around the burst register and seconds register to avoid rollover. Set-time temporarily sets oscillator control, writes all time fields, writes century separately, and clears oscillator failure.

## State and persistence behavior
Hardware stores time, century, control, and status flags. Software state is just the regmap in driver data. No alarms are exposed.

## Dependencies and integration points
Depends on SPI, regmap, RTC class, BCD helpers, and SPI driver name `"ds1347"`.

## Risks
- The read consistency loop has no retry bound; pathological hardware could loop indefinitely.
- Probe calls `spi_setup()` without checking its return value.
- No alarm, NVRAM, or trickle charger functionality is exposed.
- Century math must be tested across 1900/2000/9999 boundaries.

## Test signals
OSF read failure, set-time clearing OSF/NEOSC, century round trips, inconsistent seconds rollover loop, SPI setup failure handling, and write-protect disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1347.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1374.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1374.c

## Purpose
Maxim/Dallas DS1374 I2C RTC driver. It exposes a 32-bit seconds counter as an RTC, supports decrementer-based alarms when watchdog mode is not configured, and can alternatively register the alarm/decrementer as a watchdog device.

## Important APIs, types, and functions
- `struct ds1374` stores I2C client, RTC device, work item, mutex, exit flag, and optional watchdog device.
- `ds1374_read_rtc()` and `ds1374_write_rtc()` read/write little-endian multi-byte counter/decrementer registers using SMBus block operations.
- `ds1374_check_rtc_status()` warns on oscillator stop, clears OSF/AF, and disables alarm/decrementer control before IRQ setup.
- `ds1374_read_time()`/`set_time()` map `TOD0..3` 32-bit seconds to/from `rtc_time`.
- Alarm ops, compiled out when watchdog mode is enabled, translate absolute alarm time to a relative decrementer value, clamp past alarms to fire soon, write `WDALM0..2`, and toggle `WACE/AIE/WDALM`.
- `ds1374_irq()` disables IRQ and schedules `ds1374_work()`, which clears AF, disables alarm bits, re-enables IRQ unless exiting, and reports `RTC_AF`.
- Optional watchdog ops program the decrementer as watchdog timeout, start/stop through control bits, and register with watchdog core.
- Probe allocates RTC, initializes work/mutex, checks status, requests IRQ, sets wake capability, registers RTC, and optionally registers watchdog.
- Remove sets `exiting`, frees IRQ, and cancels work. PM callbacks toggle IRQ wake.

## Control flow
The same DS1374 decrementer is used either for alarms or watchdog depending on `CONFIG_RTC_DRV_DS1374_WDT`. Alarm programming is mutex-protected and always disables existing countdown before writing a new one. IRQ handling is deferred to workqueue because it performs SMBus I/O.

## State and persistence behavior
Hardware stores TOD counter, watchdog/alarm decrementer, control, status, and trickle charge. Software tracks workqueue exit state and mutex-protected alarm operations. In watchdog mode, watchdog timeout state is mirrored in `watchdog_device`.

## Dependencies and integration points
Depends on I2C SMBus block operations, RTC class, workqueues, PM wake, optional watchdog core, and OF/I2C ID tables (`"dallas,ds1374"`, `"ds1374"`).

## Risks
- Alarm and watchdog are mutually exclusive compile-time uses of the same hardware resource.
- Decrementer alarm must be recalculated if time changes; comments call this out.
- Past alarms are silently adjusted to fire soon rather than rejected.
- IRQ/work removal requires correct `exiting` handling to avoid enabling a freed IRQ.

## Test signals
TOD read/write endian correctness, OSF/AF clearing, alarm relative decrementer math, IRQ work one-shot disable, time-change alarm behavior, watchdog start/stop/timeout, remove while IRQ pending, and suspend/resume wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1374.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1390.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1390.c

## Purpose
Dallas/Maxim DS1390/1393/1394 SPI RTC driver. It supports basic RTC read/write and optional device-tree trickle charger setup, while explicitly leaving alarms and other extra chip-family features unsupported.

## Important APIs, types, and functions
- `struct ds1390` stores RTC device and a shared 9-byte command/data buffer.
- `ds1390_set_reg()` writes a single register by ORing the address with write bit `0x80`.
- `ds1390_get_reg()` reads a single register using `spi_write_then_read()` and the shared buffer.
- `ds1390_trickle_of_init()` reads `trickle-resistor-ohms` and `trickle-diode-disable`, builds a trickle register value for 250/2000/4000 ohm settings, and writes `DS1390_REG_TRICKLE`.
- `ds1390_read_time()` reads seven time registers starting at seconds and decodes BCD fields, including century bit in month.
- `ds1390_set_time()` writes a burst starting at seconds with the write bit set and stores century in the month high bit.
- Probe forces SPI mode 3 and 8-bit words, allocates state, verifies device readability, applies optional trickle setup, and registers the RTC.

## Control flow
All runtime operations are synchronous SPI transfers. Probe validates a basic seconds-register read before any optional charger setup or RTC registration.

## State and persistence behavior
Time and trickle charger configuration persist in hardware registers. Software state is the RTC pointer and reusable SPI buffer. No alarm state is exposed.

## Dependencies and integration points
Depends on SPI, OF properties, RTC class, and BCD helpers. Binds with OF compatible `"dallas,ds1390"` and SPI ID `"ds1390"`.

## Risks
- Alarm and status features are intentionally unavailable despite register definitions.
- SPI setup return is not checked.
- Shared transfer buffer relies on RTC core serialization for concurrent calls.
- Unsupported trickle resistor values only warn and skip charger setup.

## Test signals
Probe read failure, time read/write with century bit, DT trickle charger permutations, unsupported resistor warning, and SPI mode/bits setup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1390.c -->
