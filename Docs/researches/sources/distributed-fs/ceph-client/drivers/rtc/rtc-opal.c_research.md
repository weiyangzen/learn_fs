# sources/distributed-fs/ceph-client/drivers/rtc/rtc-opal.c

Purpose: implements PowerNV IBM OPAL firmware RTC access, including firmware RTC read/write and timed power-on alarm support.

Important APIs/types/functions: `opal_to_tm()` and `tm_to_opal()` convert between OPAL BCD packed date/time values and `struct rtc_time`. `opal_get_rtc_time()` and `opal_set_rtc_time()` call `opal_rtc_read()`/`opal_rtc_write()` with retry handling for busy and transient hardware/internal errors. TPO alarm functions `opal_get_tpo_time()`, `opal_set_tpo_time()`, and `opal_tpo_alarm_irq_enable()` use OPAL async tokens, `opal_tpo_read()`/`write()`, and async completion messages.

Control flow: module init registers the platform driver only when `FW_FEATURE_OPAL` is present. Probe allocates the RTC, enables wake capability only when DT has `wakeup-source` or legacy `has-tpo`, clears alarm feature otherwise, sets range 0000-9999, clears update interrupt feature, and registers. Time reads/writes loop while firmware returns busy/busy-event and retry certain error statuses up to ten times. Alarm read/write allocate an async token, issue TPO command, wait for response, decode async return, and release the token.

State and persistence: all RTC and TPO state is owned by OPAL firmware/platform hardware. Driver state is only the RTC device. Alarm disable writes zero date/time through the TPO interface; no Linux-side cache or IRQ handler exists.

Dependencies and integration: depends on PowerPC OPAL firmware APIs, platform/OF compatible `ibm,opal-rtc`, platform ID `opal-rtc`, async token infrastructure, and firmware feature gating.

Risks and test signals: alarm support depends entirely on DT wakeup properties, not probing TPO availability. TPO only cares about hour and minute and passes `(h_m_s_ms >> 32) & 0xffff0000`, so seconds are ignored by design. OPAL read/write loops can wait indefinitely if firmware keeps returning BUSY. Test no-OPAL init, busy/busy-event polling, hardware/internal retry exhaustion, async token interruption, no-alarm feature clearing, TPO no-alarm `-ENOENT`, alarm disable, and full BCD century conversions.
