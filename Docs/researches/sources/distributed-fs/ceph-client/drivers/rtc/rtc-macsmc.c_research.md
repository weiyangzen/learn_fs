# sources/distributed-fs/ceph-client/drivers/rtc/rtc-macsmc.c

Purpose: implements Apple SMC-backed RTC support for Apple Silicon systems, deriving wall time from a 48-bit SMC counter plus a persistent NVMEM offset.

Important APIs and types: `struct macsmc_rtc` stores the Apple SMC handle, RTC device, and `rtc_offset` NVMEM cell. RTC callbacks are `macsmc_rtc_get_time()` and `macsmc_rtc_set_time()`.

Control flow: probe only binds when a device-tree node is present, obtains the parent `apple_smc`, gets the `rtc_offset` NVMEM cell, allocates the RTC, sets a range based on a signed 48-bit 32768 Hz counter, and registers the RTC. Reads fetch six bytes of `CLKM`, read six offset bytes from NVMEM, add them, sign-extend from 48 bits, shift by 15 to seconds, and convert to `rtc_time`. Setting time reads `CLKM` and writes a new offset so the requested second starts at the current counter.

State and persistence: the SMC counter is hardware state; the time base is persistent through the NVMEM offset cell. The driver does not store alarms or volatile time state.

Dependencies and integration: Apple SMC MFD APIs, `nvmem_cell_read()`/`write()`, OF compatible `apple,smc-rtc`, RTC class, and sign-extension helpers.

Risks: NVMEM cell length shorter than six bytes is fatal. Endianness follows raw `memcpy()` into `u64`, so it relies on the SMC/NVMEM storage layout expected by the platform. There is no alarm support. Setting time truncates the offset write to six bytes.

Test signals: missing DT node, missing NVMEM cell, short cell, partial SMC read returning `-EIO`, negative offset sign extension, set/read round trip, and range limit behavior.
