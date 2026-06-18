# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.c

## Purpose

`sym_nvram.c` discovers, reads, validates, and applies persistent adapter configuration for the Symbios/LSI driver. It supports Symbios 24C16 EEPROM format, Tekram 24C16/93C46 formats, and optional PA-RISC firmware initiator data. The result is translated into host identity, parity, scan ordering, bus reset policy, and per-target queueing/disconnect/sync/wide settings.

## Important APIs, Types, And Functions

The public functions are `sym_nvram_setup_host()`, `sym_nvram_setup_target()`, `sym_read_nvram()`, and `sym_nvram_type()`. Format-specific policy helpers are `sym_Symbios_setup_target()` and `sym_Tekram_setup_target()`. Debug-only dumpers are compiled behind `SYM_CONF_DEBUG_NVRAM`.

The 24C16 serial EEPROM path is implemented by `S24C16_set_bit()`, `S24C16_start()`, `S24C16_stop()`, `S24C16_do_bit()`, `S24C16_write_ack()`, `S24C16_read_ack()`, `S24C16_write_byte()`, and `S24C16_read_byte()`. `sym_read_S24C16_nvram()` reads arbitrary byte ranges. Optional write support is guarded by `SYM_CONF_NVRAM_WRITE_SUPPORT`.

The 93C46 Tekram path uses `T93C46_Clk()`, `T93C46_Read_Bit()`, `T93C46_Write_Bit()`, `T93C46_Stop()`, `T93C46_Send_Command()`, `T93C46_Read_Word()`, and `T93C46_Read_Data()`. Format validators are `sym_read_Symbios_nvram()` and `sym_read_Tekram_nvram()`.

## Control Flow And State

`sym_read_nvram()` probes in priority order. It first attempts Symbios format by reading from `SYMBIOS_NVRAM_ADDRESS`, checking type, trailer, byte count, and checksum. If that fails, it tries Tekram format, choosing 24C16 for specific NCR device IDs and falling back to 93C46 where appropriate, then validates the 0x1234 checksum. If both fail, it asks PA-RISC PDC firmware where compiled. `nvp->type` records the winning source or zero.

EEPROM access is bit-banged through chip GPIO registers. Each read saves `nc_gpreg` and `nc_gpcntl`, configures data/clock pins, performs start/address/read/ack/stop sequences, and restores original GPIO state. The deliberate `udelay()` calls and dummy mailbox reads pace the serial protocol.

Host setup applies validated NVRAM only after detection. Symbios NVRAM can disable parity bits in `rv_scntl0`, set `np->myaddr`, increase verbosity, request reverse scan ordering, and set `SYM_AVOID_BUS_RESET`. Tekram sets the host ID. PA-RISC can override initiator ID, sync factor, width, and bus mode.

Per-target setup mutates `struct sym_tcb`: Symbios can disable tags, disable disconnects, disable boot/LUN scanning, and set requested period/width. Tekram can set tag count from `max_tags_index`, enable disconnect, set period from `Tekram_sync[]`, and enable wide negotiation.

## Dependencies And Integration Points

This file includes `sym_glue.h` and `sym_nvram.h`, uses PCI device IDs to decide Tekram access method, and directly touches chip registers through `INB()`/`OUTB()` macros. Its outputs are consumed during HCB attach and target initialization, shaping later SCSI negotiation, queue depth, scan behavior, and reset policy.

## Risks And Test Signals

Hardware risks are concentrated in GPIO bit-banging. A missed restore of `gpcntl/gpreg`, wrong pin direction, or insufficient delay can leave EEPROM or adapter GPIO in a bad state. Validation failures intentionally fall through to other formats, so corrupted EEPROM should not be trusted. The optional write path contains an apparent `y` loop variable use not declared in the visible function, making write support suspect if enabled.

Useful tests are probe on cards with no NVRAM, Symbios NVRAM, Tekram 24C16, Tekram 93C46, and PA-RISC firmware; checksum/trailer corruption tests; confirmation that host ID/parity/scan order are applied; and per-target negotiation traces showing expected tags, disconnect, sync period, and width.
