# sources/distributed-fs/ceph-client/drivers/spi/spi-falcon.c

## Purpose
Implements the Lantiq Falcon serial flash controller as a half-duplex SPI controller. The hardware is serial-flash oriented, so the driver translates SPI messages into EBU serial flash command/address/dummy/data register operations and maintains chip select across multi-transfer flash sequences.

## Important APIs, Types, And Functions
`struct falcon_sflash` stores cached `sfcmd` state and the SPI host pointer. `falcon_sflash_xfer()` is the state machine for command preparation, write, read, CS disable, and end states. `falcon_sflash_setup()` programs EBU timing and serial-flash bus configuration. `falcon_sflash_xfer_one()` walks an entire SPI message, marks begin/end flags, serializes hardware access with `ebu_lock`, and finalizes the message. Probe registers a devm SPI controller with `SPI_CONTROLLER_HALF_DUPLEX`.

## Control Flow
Setup selects a 100 MHz or 50 MHz EBU clock and derives the serial clock period. Each message starts with `FALCON_SPI_XFER_BEGIN`; the first TX byte becomes the opcode and cached CS command. Up to three following bytes are treated as address, zero bytes as dummy cycles, and remaining TX data as write payload. Read and write data are chunked through 32-bit `SFDATA` accesses with command length fields. The last transfer gets `FALCON_SPI_XFER_END`, which clears keep-CS behavior either on the final data command or an explicit CS-disable command.

## State And Persistence
The only software state is cached `sfcmd` per message. Hardware state includes EBU clock/timing, serial-flash device-size setup, bus read/write configuration, command status, address, and data registers. No persistent storage is used.

## Dependencies And Integration Points
Depends on Lantiq SoC helpers (`ltq_ebu_*`, `ltq_sys1_*`) and the global `ebu_lock`. It integrates with SPI NOR/flash-style clients through standard SPI messages but supports only mode 3 and half-duplex behavior.

## Risks
The parser assumes flash-style message layout: opcode first, up to three address bytes, and zero-valued dummy bytes. Complex SPI devices or unusual flash commands may not map cleanly. Busy polling on `SFSTAT_CMD_PEND` lacks an explicit timeout. Warnings indicate unsupported per-transfer delay and `cs_change`.

## Test Signals
Read JEDEC ID, page program, erase/status commands, multi-byte reads with dummy cycles, 50/100 MHz setup, nonstandard command layouts, command-error handling, and concurrent EBU users are key test signals.
