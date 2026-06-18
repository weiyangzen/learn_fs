# sources/distributed-fs/ceph-client/drivers/rtc/rtc-moxart.c

Purpose: implements the MOXA ART RTC as a GPIO bit-banged serial device. It exposes only RTC read/set time operations and manually drives `rtc-data`, `rtc-sclk`, and `rtc-reset` GPIO lines to access BCD calendar registers.

Important APIs/types/functions: `struct moxart_rtc` stores the `rtc_device`, a spinlock, and three GPIO descriptors. `moxart_rtc_write_byte()` and `moxart_rtc_read_byte()` implement LSB-first serial transfer with microsecond delays. `moxart_rtc_read_register()` and `moxart_rtc_write_register()` wrap the reset pulse, data-line direction changes, command byte, and local IRQ masking. `moxart_rtc_read_time()` decodes BCD date/time fields; `moxart_rtc_set_time()` writes all calendar fields after disabling write protection.

Control flow: probe allocates private state, gets the three named GPIOs, initializes the spinlock, stores driver data, and registers the RTC class device. Runtime reads take `rtc_lock`, read seconds through year plus weekday, decode 12/24-hour mode and BCD digits, derive yday using a static month offset table, then release the lock. Runtime writes take the same lock, clear `GPIO_RTC_PROTECT_W`, write BCD year/month/day/hour/min/sec registers, then re-enable protection.

State and persistence: persistent state is entirely in the external RTC registers, especially BCD time/date fields and the write-protect bit. Driver state is limited to GPIO descriptors and locking; no alarm, wakeup, NVMEM, or remove-time restoration exists.

Dependencies and integration: depends on gpiolib descriptor APIs, platform/OF compatible `moxa,moxart-rtc`, the RTC class, and board-provided GPIO names. It does not use an IRQ and does not advertise alarm support.

Risks and test signals: register access disables local IRQs while bit-banging GPIOs and doing `udelay()`, so slow GPIO backends could hurt latency. `spin_lock_irq()` is combined with helper-level `local_irq_save()`, which is redundant but protects against concurrent RTC ops. The leap-year yday calculation is simplified and the `tm_year <= 69` branch is unreachable after adding 100. Test valid/invalid GPIO descriptors, read/write protection sequencing, 12-hour PM/noon/midnight decoding, BCD conversions, month/yday boundary cases including leap years, and that concurrent read/set operations do not interleave GPIO transactions.
