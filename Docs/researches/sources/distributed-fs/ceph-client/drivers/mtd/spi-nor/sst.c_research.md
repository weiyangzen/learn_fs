# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sst.c

## Purpose
Provides SST/Microchip SPI NOR manufacturer support. It contains the SST flash table, special global-unlock behavior for SST26VF devices, and the SST Auto Address Increment word-programming path used by older byte-programming parts.

## Important APIs, Types, and Functions
The exported manufacturer is `spi_nor_sst`. `sst_nor_parts[]` describes SST25/SST26 devices and flags such as `SPI_NOR_HAS_LOCK`, `SPI_NOR_SWP_IS_VOLATILE`, `SPI_NOR_4BIT_BP`, and `SST_WRITE`. SST26 lock integration uses `sst26vf_nor_locking_ops`, where only full-chip unlock is supported through `sst26vf_nor_unlock()` and `spi_nor_global_block_unlock()`. Legacy write handling is implemented by `sst_nor_write_data()` and `sst_nor_write()`, installed by `sst_nor_late_init()` when the table marks `SST_WRITE`.

## Control Flow
After manufacturer matching, late init either installs SST26VF locking ops through per-part fixups or replaces `mtd->_write` for SST_WRITE parts. The write path prepares and locks the NOR, enables writes, handles an odd leading byte with byte program, writes the aligned body in two-byte AAI chunks, disables writes to terminate AAI, waits for ready, and optionally writes a trailing byte. `retlen` accumulates bytes actually written before unlock/unprepare.

## State and Persistence
Runtime state is mostly transient in `nor->program_opcode` and `nor->sst_write_second`, which drive the core write command sequence. Locking state lives in device status/configuration registers; `sst26vf_nor_unlock()` refuses partial unlock and refuses unlock if `SST26VF_CR_BPNV` indicates any block is permanently locked.

## Dependencies and Integration Points
The file depends on SPI NOR core helpers for register reads, write enable/disable, wait-ready, global unlock, and generic write data. It integrates with MTD by overriding `_write` only for the affected SST devices.

## Risks
The AAI write sequence is sensitive to odd addresses, trailing bytes, and write-disable timing. Partial unlock is intentionally unsupported for SST26VF, so callers expecting range locking get `-EINVAL` or `-EOPNOTSUPP`. If retlen accounting or ready polling is wrong, callers may see partial writes or later commands may run while AAI is active.

## Test Signals
Probe SST25/SST26 devices, run MTD write/read verification on odd and even offsets, validate full-chip unlock on SST26VF parts, and confirm unsupported lock/is_locked operations return expected errors.
