# sources/distributed-fs/ceph-client/drivers/rtc/rtc-fsl-ftm-alarm.c

Purpose: presents NXP/Freescale FlexTimer Module hardware as an RTC alarm device. It is not a battery-backed wall-clock RTC; it uses system time for `read_time()` and the FTM counter for short wake alarms.

Important APIs/types/functions: `struct ftm_rtc` stores RTC device, MMIO base, endian mode, and alarm frequency. `rtc_readl()`/`rtc_writel()` abstract endian access. `ftm_clean_alarm()`, `ftm_counter_enable()`, `ftm_irq_enable()`, and `ftm_irq_acknowledge()` manage FTM counter state. RTC methods are `ftm_rtc_read_time()`, `ftm_rtc_set_alarm()`, `ftm_rtc_read_alarm()`, and `ftm_rtc_alarm_irq_enable()`.

Control flow: probe maps registers, requests the IRQ, detects `big-endian`, computes the 250 Hz alarm frequency, initializes wake IRQ support, and registers the RTC. Setting an alarm clears any existing counter, computes cycles from requested alarm time minus `ktime_get_real_seconds()`, rejects values above 0xffff cycles, writes `MOD = cycle - 1`, enables the counter, and enables interrupts. The IRQ handler reports `RTC_AF`, acknowledges TOF with an erratum workaround, disables IRQs, and cleans the alarm.

State and persistence: there is no persistent RTC time. Alarm state lives in volatile FTM registers; runtime state stores register base and derived frequency.

Dependencies and integration: uses platform/OF/ACPI matching, MMIO, RTC core, wake IRQ helpers, and Freescale FTM register definitions.

Risks and test signals: negative or zero alarm deltas can underflow `cycle`, and max alarm range is only about 262 seconds. `read_alarm()` is a stub. Test endian modes, out-of-range and past alarms, TOF clear workaround, wake IRQ setup failure, and suspend wake behavior.
