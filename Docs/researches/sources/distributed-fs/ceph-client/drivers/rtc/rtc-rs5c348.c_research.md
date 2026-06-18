# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c348.c

Purpose: implements a SPI RTC driver for the Ricoh RS5C348. It supports time read/write, oscillator/voltage warnings, 12-hour or 24-hour mode handling, and Y2K century bit interpretation.

Important APIs/types/functions: `struct rs5c348_plat_data` stores the RTC pointer and detected 24-hour mode. `rs5c348_rtc_read_time()` checks CTL2 voltage/oscillator flags, performs a delayed burst read for consistent time registers, converts BCD, and handles 12-hour PM conversion. `rs5c348_rtc_set_time()` clears XSTP if present, performs a delayed burst write of all time registers, and sets month Y2K bit for years >=2000. `rs5c348_probe()` validates the seconds register, detects 24-hour mode from CTL1, allocates the RTC, and registers it.

Control flow: probe sets driver-owned platform data, performs a basic presence check using the seconds register's high bit, logs SPI clock, detects 12/24-hour mode, and registers read/set RTC ops. Runtime transfers prepend dummy CTL2 reads before burst time access to satisfy carry timing and then delay for Tcsr.

State and persistence: the chip stores BCD time, CTL1 24-hour mode, CTL2 oscillator/voltage flags, and the month Y2K bit. Driver state only records whether 24-hour mode is active.

Dependencies and integration: depends on SPI core, RTC core, BCD helpers, delays, platform data storage on the SPI device, and correct board SPI mode/chip-select wiring.

Risks: probe overwrites `spi->dev.platform_data`, so board-provided metadata would be lost. Presence detection is weak. There is no alarm, IRQ, or voltage ioctl despite warning on VDET. The 12-hour PM conversion is non-obvious and should be covered around midnight/noon. Test signals include SPI mode 1/high-active CS board setup, XSTP invalid read, VDET warning, burst transfer timing, 12-hour and 24-hour conversions, Y2K bit handling, and seconds-register presence failure.
