# sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91sam9.c

## Purpose

`rtc-at91sam9.c` implements an RTC using the AT91SAM9 real-time timer (RTT) plus a general-purpose backup register (GPBR). The RTT counter cannot be set directly, so wall-clock time is represented as GPBR base offset plus the RTT's seconds counter.

## Important APIs, types, and functions

`struct sam9_rtc` stores RTT MMIO, RTC device, interrupt mask, GPBR regmap and offset, IRQ, slow clock, suspend/cached-event state, and a spinlock. RTC callbacks are `at91_rtc_readtime()`, `at91_rtc_settime()`, `at91_rtc_readalarm()`, `at91_rtc_setalarm()`, `at91_rtc_alarm_irq_enable()`, plus `at91_rtc_proc()` for `/proc/driver/rtc`. Event helpers `at91_rtc_cache_events()` and `at91_rtc_flush_events()` manage IRQ delivery.

## Control flow

Probe gets the IRQ, maps RTT registers, resolves `atmel,rtt-rtc-time-reg` to a syscon GPBR and offset, enables the slow clock, checks the prescaler against the slow-clock rate, resets RTT and clears GPBR if needed, disables interrupts, allocates/registers the RTC with `range_max = U32_MAX`, and requests a shared conditional-suspend IRQ. Read time rejects unset GPBR (`0`) with `-EILSEQ`, reads the RTT counter twice to cross clock domains safely, adds the offset, and converts to `rtc_time`. Set time writes a new base, resets the RTT, and adjusts any pending alarm relative to the new base.

## State and persistence behavior

The GPBR base and RTT counter live in the backup power domain and are intended to survive low-power states. Alarm state is the RTT alarm register relative to the base, with `ALARM_DISABLED` as sentinel. Software caches interrupt events while suspended and flushes them on resume.

## Dependencies and integration points

The driver depends on platform MMIO/IRQ, syscon regmap, OF phandle arguments, slow clock API, RTC class APIs, `/proc` RTC hook, and PM wake handling. It matches `"atmel,at91sam9260-rtt"`.

## Risks and edge cases

If GPBR is zero, time is considered unset. Setting time adds one second before writing the base and resets RTT, a behavior that must match expected hardware latency. Changing time adjusts or disables existing alarms depending on whether the time jumps over them. Reading RTT status clears it, so only the IRQ handler may read `SR`. During suspend, increment interrupts are masked to avoid unwanted wakeups.

## Test signals

Test unset GPBR behavior, prescaler reinitialization, set/read time after RTT reset, alarm adjustment across forward and backward time changes, shared IRQ filtering, `/proc` update IRQ output, suspend wake by alarm but not by RTT increment, and persistence across backup-domain retention.
