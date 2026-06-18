# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds2404.c

Purpose: implements a platform RTC driver for the DS2404 elapsed-time counter using three GPIO lines to bit-bang reset, clock, and data rather than a standard bus controller.

Important APIs/types/functions: `struct ds2404` stores device and GPIO descriptors. `ds2404_reset()`, `ds2404_write_byte()`, and `ds2404_read_byte()` implement the serial protocol. `ds2404_read_memory()` and `ds2404_write_memory()` execute DS2404 memory commands, scratchpad verification, and copy-scratchpad completion. RTC methods `ds2404_read_time()` and `ds2404_set_time()` read/write the 32-bit little-endian counter.

Control flow: probe allocates state and RTC device, obtains `rst`, `clk`, and `dq` GPIOs with expected initial directions, registers the RTC, then enables the oscillator by writing control memory. Reads reset the chip, issue read-memory at counter offset `0x203`, fetch four bytes, and convert seconds to `rtc_time`. Writes program the same offset via write-scratchpad, verify by reading scratchpad contents, then copy it to memory and wait for completion.

State and persistence: counter and oscillator control persist in DS2404 hardware. The driver stores only GPIO descriptors and the device pointer at runtime.

Dependencies and integration: depends on platform GPIO descriptors, busy-wait microsecond delays, RTC core, and a `platform:ds2404` binding. `range_max` is `U32_MAX`.

Risks and test signals: `ds2404_write_memory()` busy-waits on DQ without a timeout, so a broken bus can hang. Verification failures only log and return void, so `set_time()` can report success after failed writes. Test GPIO polarity, protocol timing, oscillator enable, write verification failure, stuck DQ behavior, and U32 boundary conversion.
