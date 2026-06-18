# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t94.c

Purpose: supports the ST M41T94 SPI RTC with basic BCD read and set time, including halt/stop-bit clearing and century-bit handling.

Important APIs and functions: `m41t94_read_time()` and `m41t94_set_time()` form `m41t94_rtc_ops`. Probe sets 8-bit SPI transfers, reads seconds as a presence check, registers the RTC, and stores the RTC pointer as driver data.

Control flow: read first clears the halt-update bit in register `0x0c`, then clears the stop bit in seconds, then reads each date/time register individually and adds 100 years when the century bit is set or century-enable is clear. Set time writes registers starting at seconds with the SPI write bit, always enables century handling in the hour register, and sets the century bit for years >= 2000.

State and persistence: the chip stores time in battery-backed BCD registers. No software state is persistent. The driver has no alarm or NVMEM exposure.

Dependencies and integration: uses SPI single-byte operations, BCD helpers, platform/SPI module plumbing, and RTC class registration.

Risks: read-time ignores negative return values from later `spi_w8r8()` calls after the initial halt/seconds checks. It always interprets years with 1900/2000 century behavior and lacks range limits in set-time. No `rtc_valid_tm()` call is made.

Test signals: SPI presence failure, halt and stop bit clearing, 1999/2000 century behavior, invalid SPI reads during individual field reads, and basic set/read round trip.
