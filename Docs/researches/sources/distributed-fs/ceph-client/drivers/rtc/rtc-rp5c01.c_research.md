# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rp5c01.c

Purpose: implements the Ricoh RP5C01 MMIO RTC, including time read/write and a 13-byte nvmem view assembled from two 4-bit RAM banks.

Important APIs/types/functions: `struct rp5c01_priv` stores 32-bit-wide MMIO register pointer, RTC, and a spinlock shared by RTC and nvmem access. `rp5c01_read/write()` access low nibbles. `rp5c01_lock()` switches to time mode and `rp5c01_unlock()` returns to timer-enabled mode 01. `rp5c01_read_time()` and `rp5c01_set_time()` read/write decimal digit registers. `rp5c01_nvram_read/write()` switch RAM banks 10 and 11 to combine or split high/low nibbles.

Control flow: probe obtains the MMIO resource, maps it, initializes the lock, allocates the RTC, registers nvmem with size `RP5C01_MODE` bytes, then registers the RTC. There is no IRQ, alarm, suspend/resume, or OF match table.

State and persistence: time digits, mode register, timer/alarm enable bits, and RAM nibbles live in hardware. The driver maps years 00-69 to 2000-2069 and 70-99 to 1970-1999. NVMEM content is battery-backed if board hardware supplies backup power.

Dependencies and integration: uses platform devices, MMIO raw 32-bit access, RTC core, RTC nvmem helper, spinlocks, and devm resource management.

Risks: `rp5c01_set_time()` mutates `tm->tm_year` when it is >=100, altering caller state. There is no validity check for stopped oscillator or illegal digit values. RTC and nvmem modes share registers, making locking essential for all future access paths. Test signals include nvmem high/low nibble packing, concurrent nvmem/time access, year pivot behavior, register-width assumptions, and read/write digit boundaries.
