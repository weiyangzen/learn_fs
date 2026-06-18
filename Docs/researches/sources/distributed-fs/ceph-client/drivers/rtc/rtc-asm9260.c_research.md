# sources/distributed-fs/ceph-client/drivers/rtc/rtc-asm9260.c

## Purpose

`rtc-asm9260.c` drives the Alphascale ASM9260 SoC RTC. It exposes consolidated time registers, direct time-counter writes, full-field alarm registers, and alarm IRQ masking through the RTC class.

## Important APIs, types, and functions

`struct asm9260_rtc_priv` stores the device, MMIO base, RTC device, and AHB clock. RTC callbacks are `asm9260_rtc_read_time()`, `asm9260_rtc_set_time()`, `asm9260_rtc_read_alarm()`, `asm9260_rtc_set_alarm()`, and `asm9260_alarm_irq_enable()`. `asm9260_rtc_irq()` handles alarm/increment interrupt state and calls `rtc_update_irq()`.

## Control flow

Probe gets the alarm IRQ, maps MMIO, enables the AHB clock, resets/enables the RTC clock control if needed, clears counter increment interrupt state, masks alarms, registers the RTC, and requests a threaded IRQ. Read time reads consolidated registers CTIME0-2 and rereads if CTIME1 changes across the sample. Set time writes second as zero first to prevent cascading while updating year/month/day/wday/yday/hour/minute, then writes the actual second. Alarm set writes all alarm fields and sets `HW_AMR` to either all matches enabled or all masked.

## State and persistence behavior

Hardware persists current calendar counters, alarm registers, mask register, clock control, calibration, and general-purpose registers. Software only tracks MMIO/clock/RTC pointers. Remove masks alarms and disables the AHB clock.

## Dependencies and integration points

It depends on platform MMIO/IRQ resources, common clock API, RTC class APIs, and OF compatible `"alphascale,asm9260-rtc"`.

## Risks and edge cases

The IRQ handler reads and clears `HW_CIIR`, which is documented as the counter increment interrupt register, not the interrupt location register; this should be verified against hardware because alarm status may actually live in `HW_ILR`. `read_time()` returns `tm_mon` directly from hardware without subtracting one and `tm_year` directly without subtracting 1900, unlike normal RTC ABI expectations; set paths mirror that raw format. `read_alarm()` validates the raw alarm time and can fail if partial fields are used.

## Test signals

Test ABI-correct month/year values against real hardware, alarm IRQ status source and clear behavior, set/read time coherence across a second rollover, alarm mask enable/disable, clock disable on remove, and invalid alarm field handling.
