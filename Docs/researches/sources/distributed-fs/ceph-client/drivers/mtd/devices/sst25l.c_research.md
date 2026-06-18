# sources/distributed-fs/ceph-client/drivers/mtd/devices/sst25l.c

Purpose: SPI MTD NOR driver for SST25L flash chips using SST-specific status, erase, ID, and Auto Address Increment program commands.

Important APIs/types/functions: `struct sst25l_flash` stores SPI device, mutex, and embedded MTD. `struct flash_info` describes known device IDs and geometry. Helpers are `sst25l_status()`, `sst25l_write_enable()`, `sst25l_wait_till_ready()`, `sst25l_erase_sector()`, and `sst25l_match_device()`. MTD callbacks are `sst25l_erase()`, `sst25l_read()`, and `sst25l_write()`.

Control flow: probe reads ID with command `0x90`, matches two supported chips, allocates state, fills MTD NOR geometry, and registers optional platform partitions. Erase validates erase-size alignment, waits ready, then loops sectors with write-enable and sector-erase commands. Read sends opcode/address then receives data. Write requires `to` aligned to `writesize`, enables writes, uses `AAI_PROGRAM` with full address for the first byte of each page and 2-byte continuation writes for remaining bytes, then disables writes.

State and persistence: persistent state is NOR contents and protection bits. Runtime state is a per-device mutex and MTD geometry. `sst25l_write_enable()` also writes status register protection bits to enable or disable writes.

Dependencies/integration: SPI core, MTD partitions via `flash_platform_data`, jiffies timeout/`cond_resched`, and devm allocation.

Risks: `sst25l_read()` ignores the return value of `spi_sync()` after waiting ready and returns 0 even if transfer failed. `sst25l_write()` overwrites an earlier error with the return from write-disable in `out`, potentially masking failures. Supported chip table is very small.

Test signals: unknown ID rejection, write-enable status verification, 3-second busy timeout, erase alignment checks, AAI writes across page boundaries, transfer error injection for read/write, and remove unregister warning path.
