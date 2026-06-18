# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mcp795.c

Purpose: supports Microchip MCP795 SPI RTCs with timekeeping, oscillator control, alarm0 IRQs, and workarounds for silicon date/month write issues.

Important APIs and functions: SPI RTCC helpers are `mcp795_rtcc_read()`, `mcp795_rtcc_write()`, and `mcp795_rtcc_set_bits()`. Oscillator helpers are `mcp795_stop_oscillator()` and `mcp795_start_oscillator()`. Alarm control is `mcp795_update_alarm()`. RTC callbacks are `mcp795_read_time()`, `mcp795_set_time()`, `mcp795_read_alarm()`, `mcp795_set_alarm()`, and `mcp795_alarm_irq_enable()`.

Control flow: probe configures SPI mode 0, starts the oscillator, clears 12-hour mode, registers the RTC, and if an IRQ exists clears pending alarm and requests a falling-edge threaded IRQ with wakeup enabled. Setting time stops the oscillator, saves EXTOSC, reads existing fields to preserve config bits, writes seconds through date, writes month/year separately for silicon issue avoidance, then restarts oscillator and restores EXTOSC. Alarm set rejects past alarms and alarms more than roughly one year out, disables alarm, writes match fields, and optionally enables it.

State and persistence: RTC registers hold time, oscillator/config bits, alarm fields, and flags. No software alarm state is retained. The IRQ handler disables the alarm in hardware and reports `RTC_AF`.

Dependencies and integration: SPI, OF/SPI IDs, BCD helpers, RTC class, optional IRQ/wakeup, and MCP795 command opcodes for RTCC access.

Risks: `mcp795_set_time()` mutates `tim->tm_year` when greater than 100. Stopping oscillator and EXTOSC toggling can fail or delay updates. Alarm range logic uses `is_leap_year(alm->time.tm_year)`, where `tm_year` is years since 1900 and may need absolute-year scrutiny. No explicit alarm feature clearing when no IRQ exists.

Test signals: oscillator stop timeout, EXTOSC preservation, date/month split write workaround, past and >1-year alarm rejection, IRQ disable-on-fire, 12-hour clear, SPI transfer failures, and set-time `tm_year` mutation.
