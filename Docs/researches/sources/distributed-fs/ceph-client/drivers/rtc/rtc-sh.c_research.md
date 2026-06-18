# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sh.c

Purpose: SuperH and Renesas RZ/A on-chip RTC platform driver. It handles BCD calendar registers, carry-safe reads, optional 4-digit year support, alarm match registers, clock enable, wakeup, and OF/non-OF resource variants.

Important APIs/types/functions: `struct sh_rtc` holds MMIO, alarm IRQ, clock, `rtc_device`, lock, and capability flags. `sh_rtc_read_time()` clears/uses the carry flag and 128 Hz counter to read a stable time. `sh_rtc_set_time()` stops/resets the prescaler, writes BCD fields, then restarts RTC. Alarm helpers encode ignored fields as disabled alarm register bytes using `AR_ENB`. `sh_rtc_alarm()` clears `RCR1_AF` and disables AIE before calling `rtc_update_irq()`. Probe maps IO/MEM resources, gets clock names (`rtcN` or `fck`), loads platform capability flags, disables interrupts, sets date range, and registers.

Control flow/state/persistence: hardware stores BCD calendar and alarm registers. Reads loop until no carry and no inverted-bit rollover. Remove disables alarms and clock. PM toggles IRQ wake if wakeup is allowed.

Dependencies/integration: platform driver `sh-rtc`, compatible `renesas,sh-rtc`, optional `CONFIG_SUPERH` platform data, clock framework, IO or MEM resources, RTC core, IRQ wake.

Risks/test signals: year handling differs between 2-digit and 4-digit hardware, with fallback century logic for old parts. The RYRAR/RCR3 year-alarm support is intentionally absent. Test carry/rollover read stability, alarm ignored fields, 4-digit vs 2-digit ranges, clock absence tolerance, OF and legacy IRQ numbering, and suspend wake.
