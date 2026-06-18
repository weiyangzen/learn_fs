# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun6i.c

Purpose: Allwinner A31/A23 and later RTC driver with integrated low-speed oscillator clock provider, RTC calendar, counter or absolute alarms, battery-backed GP data nvmem, and wakeup support.

Important APIs/types/functions: `struct sun6i_rtc_clk_data` captures SoC oscillator capabilities; `struct sun6i_rtc_dev` stores RTC, clock-provider state, MMIO, alarm, flags, and lock. `sun6i_rtc_clk_init()` maps RTC early and registers internal oscillator, muxed LOSC, and external gate clocks. RTC ops read stable date/time snapshots, encode either YMD fields or `RTC_LINEAR_DAY`, set alarms as relative seconds or absolute day/HMS, poll access bits with `sun6i_rtc_wait()`, and expose GP data through nvmem callbacks.

Control flow/state/persistence: early `CLK_OF_DECLARE_DRIVER` setup may allocate the singleton `sun6i_rtc` before platform probe. Probe optionally enables a bus clock, maps MMIO if early init did not, requests IRQ, clears and disables alarm sources, enables LOSC, allocates RTC, sets range based on linear-day flag, registers RTC, then registers nvmem. Alarm time is cached in `chip->alarm`.

Dependencies/integration: compatibles for A31/A23/H3/R40/V3/H5/H6/H616/R329, clk provider framework, optional CCU probe, platform MMIO/IRQ, wakeup, RTC core, nvmem.

Risks/test signals: singleton early clock state couples clock provider and platform probe lifetime. Non-linear date range is limited to 2033; newer linear-day chips use 65536 days. Alarm enable only disables in `.alarm_irq_enable`; normal enabling is done in `.set_alarm`. Test early clock registration, internal/external LOSC parent changes, access-bit timeouts, linear and non-linear time encoding, nvmem word alignment, alarm wake, and suspend IRQ wake.
