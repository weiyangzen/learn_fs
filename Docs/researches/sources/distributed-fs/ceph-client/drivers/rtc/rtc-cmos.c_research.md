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
