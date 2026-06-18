# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl030.c

Purpose: supports the ARM AMBA PrimeCell PL030 RTC, a simple 32-bit counter with match alarm and load register.

Important APIs/types/functions: `struct pl030_rtc` stores the MMIO base. `pl030_read_time()` and `pl030_set_time()` convert between seconds counter and `rtc_time`, adding one second on writes because the load register transfers on the next 1 Hz edge. `pl030_read_alarm()` and `pl030_set_alarm()` access the match register. `pl030_interrupt()` acknowledges interrupts through EOI.

Control flow: probe requests AMBA regions, allocates driver and RTC objects, maps registers, disables control and clears pending IRQ, requests the interrupt, registers the RTC, and releases resources manually on errors. Remove disables control, frees IRQ, unmaps registers, and releases AMBA regions.

State and persistence: the hardware counter, match register, and control register contain all persistent RTC state. The driver does not expose alarm IRQ enable in RTC ops and disables `RTC_CR` on probe/remove, so alarm interrupt behavior is minimal.

Dependencies and integration: uses AMBA bus matching by PrimeCell ID, MMIO, RTC core, and interrupt handling. Range maximum is `U32_MAX` seconds.

Risks: the interrupt handler only acknowledges and does not call `rtc_update_irq()`, so alarm events are not reported to userspace. The driver uses non-devm `ioremap()` and `request_irq()` with manual cleanup mixed with devm RTC allocation. Test signals include AMBA region conflicts, read/write counter accuracy with the one-second load adjustment, match register behavior, IRQ acknowledgment, and remove/error cleanup.
