# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ma35d1.c

Purpose: implements the Nuvoton MA35D1 RTC using MMIO BCD calendar/time registers, hardware initialization magic, alarm interrupts, and suspend wakeup support.

Important APIs and functions: `struct ma35_rtc` stores IRQ, MMIO base, and RTC device. `ma35d1_rtc_init()` writes the magic code until the active bit appears. `ma35d1_rtc_ops` provides read/set time, read/set alarm, and alarm IRQ enable. `ma35d1_rtc_interrupt()` reports alarm events.

Control flow: probe maps registers, obtains and enables the first DT clock, initializes RTC hardware if inactive, requests the IRQ with `IRQF_NO_SUSPEND`, enables wakeup, allocates/registers the RTC, and sets range 2000-2099. Reads loop until time and calendar are stable across a second read, then decode BCD fields. Setting time and alarm writes packed BCD calendar/time words. Alarm IRQ enable toggles `ALMIEN`.

State and persistence: hardware RTC registers retain time, alarm, weekday, init state, and interrupt flags in the RTC domain. Software state is minimal and volatile.

Dependencies and integration: OF compatible `nuvoton,ma35d1-rtc`, platform MMIO/IRQ, `of_clk_get()` and `clk_prepare_enable()`, RTC class, wake IRQ semantics through suspend/resume hooks, and raw MMIO accessors.

Risks: the enabled clock is not devm-managed or disabled on later probe failures. `platform_get_irq()` return is not checked before request. Read stability loop has no timeout if registers never stabilize. Interrupt handler calls `rtc_update_irq()` even when no event bits are set.

Test signals: inactive initialization timeout, clock lookup/enable failure cleanup, stable read loop under rollover, alarm IRQ enable/clear, invalid IRQ handling, suspend/resume wake toggling, and date range boundaries.
