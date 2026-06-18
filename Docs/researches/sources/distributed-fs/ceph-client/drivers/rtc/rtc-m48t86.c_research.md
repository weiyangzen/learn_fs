# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m48t86.c

Purpose: supports ST M48T86/Dallas DS12887-style indexed RTCs, including binary or BCD time mode, 12/24-hour handling, battery status reporting, chip-presence verification, and 114-byte NVRAM exposure.

Important APIs and functions: `m48t86_readb()` and `m48t86_writeb()` implement index/data register access. `m48t86_rtc_read_time()`, `m48t86_rtc_set_time()`, and `m48t86_rtc_proc()` are RTC callbacks. `m48t86_nvram_read()` and `m48t86_nvram_write()` expose NVRAM. `m48t86_verify_chip()` checks optional-board presence by writing the last two NVRAM bytes.

Control flow: probe maps separate index and data resources, stores driver data before verification, writes/readbacks NVRAM sentinels to prove the chip exists, registers RTC and NVMEM, and logs battery status. Reads decode based on data-mode bit and correct 12-hour PM. Writes set update/24-hour bits, write either binary or BCD fields, then clear update.

State and persistence: RTC registers and NVRAM are battery-backed. The verification path temporarily mutates two NVRAM bytes and restores them if the test succeeds.

Dependencies and integration: platform MMIO resources, optional OF compatible `st,m48t86`, RTC class, NVMEM provider via RTC, BCD helpers, and indexed CMOS-like hardware semantics.

Risks: failed chip verification can leave modified NVRAM bytes if the second-stage checks fail before restoration. No locking protects index/data access, so concurrent RTC and NVMEM operations could interleave. Years are always interpreted as 2000-2099. The driver lacks alarm support despite alarm registers existing.

Test signals: verify-chip success/failure with restoration, BCD and binary mode reads/writes, 12-hour PM correction, battery proc output, NVRAM nonzero offset accesses, and missing resource errors.
