## sources/distributed-fs/ceph-client/drivers/rtc/rtc-xgene.c

Purpose: Provides an MMIO RTC driver for AppliedMicro APM X-Gene SoCs. It exposes a 32-bit seconds counter, compare alarm, interrupt handling, clock control, and wake-aware suspend/resume.

Important APIs/types/functions: `struct xgene_rtc_dev` stores the RTC device, CSR mapping, clock, and PM IRQ state. RTC callbacks are `xgene_rtc_read_time`, `xgene_rtc_set_time`, `xgene_rtc_read_alarm`, `xgene_rtc_set_alarm`, and `xgene_rtc_alarm_irq_enable`. `xgene_rtc_interrupt` handles compare interrupts.

Control flow: Probe allocates state, maps CSR registers, allocates RTC, requests the platform IRQ, obtains and enables the RTC clock, turns on the RTC with `RTC_CCR_EN`, marks wake-capable, sets the RTC range to `U32_MAX`, and registers. Time read converts `RTC_CCVR` seconds to `rtc_time`; set writes `RTC_CLR` and reads it back as a barrier, with a comment that visible counter update occurs after one second. Alarm set writes `RTC_CMR` and applies interrupt enable/disable. IRQ enable manipulates `RTC_CCR_IE` and `RTC_CCR_MASK`. The interrupt handler checks `RTC_STAT_BIT`, reads `RTC_EOI` to clear, and reports alarm.

State and persistence: Hardware counter, compare register, control bits, and clock domain hold functional state. Driver PM state records whether IRQ wake was enabled and whether alarm IRQ was enabled before non-wakeup suspend.

Dependencies/integration: Uses platform MMIO, OF compatible `"apm,xgene-rtc"`, common clock framework, RTC core, IRQ wake APIs, and PM sleep ops.

Risks: `read_alarm` does not read `RTC_CMR`; it returns time zero with enabled state only, so users cannot inspect the programmed alarm time. Suspend disables the clock only when not wake-capable and restores alarm IRQ state on resume. Set-time truncates to 32 bits and depends on hardware’s one-second update latency.

Test signals: Read/set around one-second latency, alarm programming and IRQ/EOI clear, wake and non-wake suspend paths, clock enable/disable failure, range near `U32_MAX`, and the known read_alarm time-zero limitation.
