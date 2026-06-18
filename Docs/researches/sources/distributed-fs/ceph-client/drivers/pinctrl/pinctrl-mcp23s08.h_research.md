# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.h

## Purpose
Defines the shared interface and state structures for the MCP23S08/MCP230xx GPIO expander driver family, used by the common core and I2C/SPI transport frontends.

## Important APIs, Types, and Functions
Defines device type constants `MCP_TYPE_S08`, `MCP_TYPE_S17`, `MCP_TYPE_008`, `MCP_TYPE_017`, `MCP_TYPE_S18`, and `MCP_TYPE_018`. `struct mcp23s08_info` describes a variant's regmap config, label, type, GPIO count, and register shift. `struct mcp23s08` carries per-chip runtime state including address, IRQ polarity, rise/fall masks, parent IRQ, cached GPIO value, mutex, `gpio_chip`, regmap, pinctrl descriptor/device, and optional reset GPIO. It declares exported regmap configs and `mcp23s08_probe_one`.

## Control Flow and State
The header has no runtime control flow. It defines the state shared across transports and the core: bus frontends fill variant fields and regmap, while the core fills GPIO/pinctrl/IRQ callbacks and maintains cached state.

## Dependencies and Integration Points
Includes GPIO, IRQ, mutex, pinctrl, and type headers. It is included by `pinctrl-mcp23s08.c`, `pinctrl-mcp23s08_i2c.c`, and `pinctrl-mcp23s08_spi.c`, making it the contract between transport-specific probe code and common GPIO/pinctrl/IRQ behavior.

## Risks and Test Signals
Risks are interface drift between core and transports, wrong `reg_shift` or `ngpio` metadata per variant, and missing state initialization before `mcp23s08_probe_one`. Test signals are compile coverage for both transports, probing every listed variant, and runtime confirmation that 8-bit parts expose 8 pins while 16-bit parts expose 16 pins with correct register addressing.
