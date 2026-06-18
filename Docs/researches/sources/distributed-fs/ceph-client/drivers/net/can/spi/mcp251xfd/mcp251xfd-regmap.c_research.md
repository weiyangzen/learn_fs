# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-regmap.c

Purpose: Implements custom Linux regmap buses for MCP251xFD SPI access, with and without controller CRC framing, including errata-specific write splitting and read retry behavior.

Important APIs, types, and functions: `mcp251xfd_regmap_init()` selects and initializes `map_reg` and `map_rx`. Nocrc paths implement gather/write/read/update-bits. CRC paths implement CRC gather/write/read, `mcp251xfd_regmap_crc_read_check_crc()`, and retrying reads. Static regmap configs define endian handling, register ranges, widths, and raw transfer sizes.

Control flow: Initialization creates devm regmaps and DMA-safe buffers only for required modes. Register access builds SPI command buffers, supports half-duplex with two transfers, and copies data between regmap buffers and caller memory. CRC reads retry, apply TBC and OSC wake exceptions, and return `-EBADMSG` on persistent mismatch.

State and persistence behavior: Persistent driver state is selected regmap pointers and reusable RX/TX transfer buffers in `mcp251xfd_priv`. No regcache is used; all accesses hit hardware.

Dependencies and integration points: Depends on SPI, regmap, unaligned endian helpers, CRC helper, quirk flags, and register constants. Core, RX/TEF, ring setup, and dump code use this hardware access layer.

Risks: Sensitive to SPI framing, endian, DMA-safe buffer lifetime, and silicon errata. IOCON write splitting protects LAT bits. Wrong update-bits read/skip decisions can clear write-one or FIFO control bits.

Test signals: CRC/nocrc reads and writes, full/half duplex controllers, raw RAM reads, IOCON updates crossing excluded byte, CRC mismatch retries, OSC wake reads, and `-EBADMSG` fault injection.
