# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_spi.c

## Purpose
Implements the SPI transport frontend for MCP23S08, MCP23S17, and MCP23S18 GPIO expanders. It supports up to eight addressed chips sharing one SPI chip select and instantiates the shared MCP23S08 core once per populated address.

## Important APIs, Types, and Functions
Key type is `struct mcp23s08_driver_data`, which stores per-address chip pointers and a flexible array of chip state. SPI regmap transport callbacks are `mcp23sxx_spi_write`, `mcp23sxx_spi_gather_write`, and `mcp23sxx_spi_read`, collected in `mcp23sxx_spi_regmap`. Probe helpers are `mcp23s08_spi_regmap_init` and `mcp23s08_probe`. Variant descriptors are `mcp23s08_spi`, `mcp23s17_spi`, and `mcp23s18_spi`.

## Control Flow and State
Probe reads `microchip,spi-present-mask` or deprecated `mcp,spi-present-mask`, validates it against eight possible addresses, allocates enough `struct mcp23s08` objects for populated chips, and iterates set bits. For each address it assigns the shared parent IRQ, creates a per-chip regmap config copy with a unique name, initializes SPI regmap with opcode/address handling, names the pinctrl descriptor, and calls `mcp23s08_probe_one` with hardware address `0x40 | (addr << 1)`. It accumulates total GPIO count in driver data.

## Dependencies and Integration Points
Depends on SPI core, custom regmap bus callbacks, firmware property parsing, shared MCP23S08 core, and match tables for SPI IDs and OF compatibles. Like the I2C frontend, it registers at `subsys_initcall` to make expander GPIOs available early.

## Risks and Test Signals
Risks include invalid present-mask handling, address/opcode mistakes in SPI reads and writes, shared parent IRQ behavior across multiple chips on one chip select, per-chip regmap name collisions, and sparse address population. Test signals include probing masks with one and multiple chips, SPI transfer traces for read/write/gather-write opcodes, GPIO and IRQ tests on each populated address, and validation for deprecated and current OF properties.
