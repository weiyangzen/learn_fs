# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-mcp23s08_i2c.c

## Purpose
Implements the I2C transport frontend for MCP23008, MCP23017, and MCP23018 GPIO expanders, wiring I2C match data and regmap initialization into the shared MCP23S08 core.

## Important APIs, Types, and Functions
The main function is `mcp230xx_probe`. Variant descriptors are `mcp23008_i2c`, `mcp23017_i2c`, and `mcp23018_i2c`. Device matching is provided by `mcp230xx_id` and `mcp23s08_i2c_of_match`, including deprecated `mcp,*` compatibles. Driver lifecycle uses `mcp23s08_i2c_init` with `subsys_initcall` and `mcp23s08_i2c_exit`.

## Control Flow and State
Probe allocates one `struct mcp23s08`, retrieves I2C match data, copies variant GPIO count, label, and register-shift metadata into the chip, creates an I2C regmap, stores `client->irq`, names the pinctrl descriptor, and calls `mcp23s08_probe_one` with dynamic GPIO base `-1`. After successful common probe, it stores client data.

## Dependencies and Integration Points
Depends on I2C core matching, OF matching, `devm_regmap_init_i2c`, the shared header/core, and optional client IRQ wiring from board firmware. The `subsys_initcall` timing registers the driver before many consumers that may request expander GPIOs.

## Risks and Test Signals
Risks include missing/incorrect match data, wrong variant regmap config, deprecated compatible handling, and devices needing GPIOs before this subsys initcall runs. Test signals include I2C probe for all three variants, GPIO count and label validation, interrupt-controller operation via `client->irq`, and OF/module alias autoloading.
