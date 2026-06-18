# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t93.c

Purpose: implements a compact SPI RTC driver for the ST M41T93, with BCD timekeeping, oscillator-failure handling, halt-update recovery, and battery-low warnings.

Important APIs and functions: `m41t93_set_reg()` writes a single register with the SPI write bit set. `m41t93_set_time()` and `m41t93_get_time()` are the RTC callbacks in `m41t93_rtc_ops`. Probe sets SPI mode parameters, probes the weekday register, and registers the RTC.

Control flow: setting time rejects pre-2000 dates, tries to clear the OF flag, kickstarts the oscillator if OF remains, encodes century bits in the hour register, and writes a burst of eight time registers. Reading time clears HT if set, treats OF as `-EINVAL` while still decoding registers, warns on battery low, bulk-reads registers, and reconstructs the century from hour bits.

State and persistence: all state is stored in the SPI RTC registers. There is no software persistence beyond the registered RTC device. Flags provide sticky hardware state for oscillator failure, battery low, and halted readout updates.

Dependencies and integration: uses SPI `spi_w8r8()`, `spi_write_then_read()`, BCD helpers, and the RTC class. It has no alarm, wakeup, or NVMEM integration.

Risks: the OF kickstart path uses a local buffer before final field population, so register semantics should be verified on hardware. Reads can return decoded time with `-EINVAL` when OF is set, which callers treat as invalid. Century encoding assumes supported years map cleanly into the two top hour bits.

Test signals: pre-2000 rejection, OF clear and kickstart paths, HT clear path, BL warning, probe-not-found detection from weekday upper bits, and century rollover reads/writes.
