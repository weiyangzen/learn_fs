# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08.c

## Purpose
Provides the bus-independent core for Microchip MCP23x08/MCP23x17/MCP23x18 GPIO expanders. It implements GPIO operations, pull-up pinconf, optional nested IRQ controller support, regmap configuration, and shared probe setup used by I2C and SPI frontends.

## Important APIs, Types, and Functions
Exports `mcp23x08_regmap`, `mcp23x17_regmap`, and `mcp23s08_probe_one`. Internal helpers wrap regmap access through shifted addresses: `mcp_read`, `mcp_write`, `mcp_update_bits`, and `mcp_set_bit`. GPIO operations include `mcp23s08_direction_input`, `mcp23s08_direction_output`, `mcp23s08_get`, `mcp23s08_get_multiple`, `mcp23s08_set`, and `mcp23s08_set_multiple`. IRQ paths are handled by `mcp23s08_irq`, mask/unmask/type callbacks, bus lock/sync callbacks, and `mcp23s08_irq_setup`.

## Control Flow and State
`mcp23s08_probe_one` initializes the mutex, GPIO chip, optional reset GPIO, verifies and normalizes `IOCON`, applies IRQ polarity/mirror/open-drain properties, disables interrupts before registering nested IRQs, registers the GPIO chip, registers a small pinctrl device, then requests the parent threaded IRQ when present. GPIO direction and output state are persisted in `IODIR` and `OLAT`; pull-ups live in `GPPU`. The IRQ handler reads `INTF`, `INTCON`, `GPINTEN`, `DEFVAL`, `INTCAP`, and `GPIO`, updates `cached_gpio`, masks level interrupts while handling, and synthesizes nested child IRQs using cached previous GPIO state plus captured/current input values.

## Dependencies and Integration Points
Depends on regmap with cache disabled locking because `mcp->lock` serializes access, gpiolib, pinctrl pinconf, threaded IRQs, firmware properties `interrupt-controller`, `microchip,irq-active-high`, `microchip,irq-mirror`, and `drive-open-drain`, and the I2C/SPI frontends that allocate `struct mcp23s08` and initialize regmap.

## Risks and Test Signals
Risks include IRQ-clearing side effects when reading `GPIO`, cache-only IRQ bus locking mistakes, incorrect 8-bit versus 16-bit register shifting, level IRQ reactivation if GPINTEN is not restored, and `cached_gpio` drift after failed reads. Test signals include GPIO direction/value/multiple operations on 8- and 16-bit parts, pull-up pinconf set/get, IRQ tests for rising/falling/both/level modes, active-high/mirror/open-drain property combinations, regcache sync error injection, and both I2C and SPI probe paths.
