# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-crc16.c

Purpose: Implements the MCP251xFD-specific CRC-16 used by CRC-enabled SPI register and RAM commands. The generic kernel CRC16 helper is not used because the controller expects a left-shift/table variant.

Important APIs, types, and functions: `mcp251xfd_crc16_compute()` computes a CRC over one contiguous buffer with initial value `0xffff`; `mcp251xfd_crc16_compute2()` computes a command+data CRC by continuing the first calculation over a second buffer. Internal helpers are `mcp251xfd_crc16_byte()` and `mcp251xfd_crc16()`, backed by `mcp251xfd_crc16_table`.

Control flow: Callers build the SPI command and payload, pass command or command+payload bytes to these helpers, then append the returned big-endian CRC to the transfer buffer. Reads use the same algorithm in `mcp251xfd-regmap.c` to verify controller-returned CRCs.

State and persistence behavior: Stateless except for the constant lookup table. No allocation, locking, hardware access, or persistent configuration.

Dependencies and integration points: Included through `mcp251xfd.h` prototypes and consumed by CRC regmap operations, TX object loading, and prebuilt ring write commands.

Risks: Any table or shift-direction error corrupts every CRC-protected SPI access. `compute2()` depends on callers passing exactly the bytes included in chip-side CRC calculation.

Test signals: Known-good MCP251xFD SPI command vectors, hardware CRC read/write smoke tests, and negative tests that flip payload or CRC bytes and confirm `-EBADMSG` paths.
