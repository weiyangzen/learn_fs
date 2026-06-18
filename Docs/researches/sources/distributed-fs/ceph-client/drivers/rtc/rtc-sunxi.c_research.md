# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunxi.c

Purpose: older Allwinner A10/A20 RTC driver. It handles YMD/HMS calendar registers, relative counter alarm, limited year ranges, and alarm IRQs.

Important APIs/types/functions: `struct sunxi_rtc_data_year` defines min/max year, year bitmask, and leap-year bit shift per compatible. `struct sunxi_rtc_dev` stores RTC, device, data-year pointer, MMIO, and IRQ. `sunxi_rtc_gettime()` reads stable YMD/HMS values and rebases year to Linux. `sunxi_rtc_settime()` validates year, writes time/date, and polls access bits. `sunxi_rtc_setalarm()` computes a relative day/hour/min/sec gap from current time, bounds it to 255 days, writes `SUNXI_ALRM_DHMS`, and enables alarm IRQ. IRQ handler clears pending status and reports `RTC_AF`.

Control flow/state/persistence: probe allocates, maps MMIO, requests IRQ, loads match data for A10 or A20 year format, clears/disables alarm registers, assigns RTC ops, and registers.

Dependencies/integration: compatibles `allwinner,sun4i-a10-rtc` and `allwinner,sun7i-a20-rtc`, platform MMIO/IRQ, RTC core, delay/poll helpers.

Risks/test signals: `.alarm_irq_enable()` only disables; enabling is done through `.set_alarm`. `sunxi_rtc_wait()` considers success when masked bits equal mask, unlike sun6i's wait-for-clear, so hardware semantics must be preserved. Test both year parameter sets, leap bit placement, past/far alarms, access polling, relative alarm encoding, and read stability around rollover.
