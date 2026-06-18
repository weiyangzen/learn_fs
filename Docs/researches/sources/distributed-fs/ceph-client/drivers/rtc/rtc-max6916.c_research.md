# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max6916.c

Purpose: implements the MAX6916 SPI RTC for 2000-2099 BCD timekeeping, with oscillator/status initialization and burst read/write.

Important APIs and functions: `max6916_read_reg()` and `max6916_write_reg()` handle SPI register access. `max6916_read_time()` and `max6916_set_time()` are RTC callbacks. Probe configures SPI mode 3, clears write-protect, enables oscillator behavior, logs control/status registers, and registers the RTC.

Control flow: read sends clock-burst read and decodes BCD fields, subtracting one from weekday and adding 100 to year. Set validates `tm_year` in 100-199, builds a burst write buffer including control byte, and writes it. Probe reads seconds, modifies control bit 7, masks status bits, writes status, and registers the device.

State and persistence: time, control, and status are in RTC registers. Driver state is not persistent.

Dependencies and integration: SPI mode 3, RTC class, BCD helpers, and MAX6916 burst command protocol.

Risks: status initialization masks data with `0x1B`, which must match oscillator/flag semantics. The burst write includes a control byte set to BCD zero. No alarm support. License string is `GPL v2` rather than the common `GPL`.

Test signals: date range rejection, SPI read/write failure paths, oscillator/status post-probe state, weekday normalization, and set/read round trip.
