# sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-regmap.c

## Purpose
`tcan4x5x-regmap.c` implements the SPI regmap bus used by the TCAN4x5x wrapper. It translates regmap reads and writes into TCAN SPI command frames with big-endian register/value formatting.

## Important APIs, Types, And Functions
- `TCAN4X5X_SPI_INSTRUCTION_WRITE` and `TCAN4X5X_SPI_INSTRUCTION_READ` encode the TCAN SPI opcodes.
- `tcan4x5x_regmap_gather_write()` builds one write transfer containing command header plus payload.
- `tcan4x5x_regmap_write()` adapts flat regmap writes to gather writes.
- `tcan4x5x_regmap_read()` builds command and receive transfers, supporting both half-duplex and full-duplex SPI controllers.
- Read/write access tables restrict allowed TCAN, M_CAN, and MRAM register ranges.
- `tcan4x5x_regmap` and `tcan4x5x_bus` define regmap geometry, endianness, raw transfer limits, flags, and access policy.
- `tcan4x5x_regmap_init()` creates the devm regmap.

## Control Flow
The TCAN probe calls `tcan4x5x_regmap_init()` after SPI setup. All later TCAN core register access and common M_CAN register/FIFO access go through this regmap. Reads copy the command into the aligned TX buffer, set word length, then either issue command and RX payload as separate transfers for half-duplex controllers or one full-duplex transfer with a sanitized data area.

## State And Persistence
The regmap uses no cache (`REGCACHE_NONE`). Transfer state is transient in `map_buf_tx` and `map_buf_rx` embedded in `struct tcan4x5x_priv`. There is no persistent state.

## Dependencies And Integration Points
The file depends on SPI controller capabilities, regmap bus APIs, and TCAN private buffers from `tcan4x5x.h`. It is linked into the composite `tcan4x5x` module with `tcan4x5x-core.o`.

## Risks And Edge Cases
- `tcan4x5x_spi_cmd_set_len()` stores byte length divided by four; callers must provide 32-bit aligned transfer lengths.
- Raw reads/writes are capped at 256 bytes, matching the static buffer data length.
- Access tables must include every M_CAN register used by the common core; missing ranges would fail regmap operations.
- Full-duplex reads rely on copying from `buf_rx->data` after the combined transfer; sanitizing TX data avoids leaking stale buffer contents.

## Test Signals
Exercise regmap single register reads/writes, bulk MRAM reads/writes, half-duplex and full-duplex SPI controllers, access-table rejection of invalid registers, and max-size raw transfers.
