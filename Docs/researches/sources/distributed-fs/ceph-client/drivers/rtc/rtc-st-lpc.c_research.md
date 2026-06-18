# sources/distributed-fs/ceph-client/drivers/rtc/rtc-st-lpc.c

Purpose: RTC mode driver for ST LPC low-power timer hardware. It uses a 64-bit free-running low-power timer as current time and a low-power alarm timer for wake alarm support.

Important APIs/types/functions: `struct st_rtc` holds RTC device, cached alarm, clock/rate, MMIO, IRQ state, lock, and IRQ. `st_rtc_read_time()` reads MSB/LSB consistently and divides ticks by clock rate. `st_rtc_set_time()` writes tick count and starts the timer. `st_rtc_set_hw_alarm()` programs the low-power alarm through WDT gating. Alarm ops cache `rtc_wkalrm`, compute relative delta from current time, and enable/disable an IRQ requested with `IRQF_NO_AUTOEN`. PM suspend/resume clears or restarts alarm hardware depending on wakeup.

Control flow/state/persistence: probe requires DT `st,lpc-mode == ST_LPC_MODE_RTC`, maps MMIO, maps IRQ, requests clock, sets wake capability, computes range from `U64_MAX / clkrate`, and registers. Current time persists as hardware counter ticks; alarm state is partly cached in RAM.

Dependencies/integration: compatible `st,stih407-lpc`, `dt-bindings/mfd/st-lpc.h`, platform MMIO, `irq_of_parse_and_map()`, clock framework, RTC core.

Risks/test signals: alarm programming subtracts current seconds without checking for alarms in the past, causing unsigned underflow. IRQ handler reports `RTC_AF` without `RTC_IRQF`. Cached alarm state is lost across driver reload and cleared on resume. Test mode rejection, clock-rate zero, relative alarm math, wake/non-wake suspend paths, IRQ enable state transitions, and range calculation.
