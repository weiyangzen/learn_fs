# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_i2c.c

## Purpose
`goodix_berlin_i2c.c` is the I2C transport wrapper for the Goodix Berlin core. It provides a 32-bit-register/8-bit-value regmap over I2C, supplies a BUS_I2C input ID, selects GT9916 IC metadata, and delegates functional behavior to `goodix_berlin_probe()`.

## Important APIs, types, and functions
- `goodix_berlin_i2c_regmap_conf` sets `reg_bits = 32`, `val_bits = 8`, and caps raw read/write transfers at 256 bytes.
- `goodix_berlin_i2c_input_id` sets the input bus type to `BUS_I2C`; vendor/product are intentionally unset.
- `goodix_berlin_i2c_probe()` gets IC data from match data, creates the regmap with `devm_regmap_init_i2c()`, and calls the core probe.
- `gt9916_data` uses revision D firmware-version and IC-info addresses.
- I2C and OF match tables bind `"gt9916"` and `"goodix,gt9916"` to that data.

## Control flow
When an I2C client matches, probe initializes regmap and immediately transfers ownership of device setup to the common Berlin core. The driver struct shares the core PM ops and raw-register dev_groups, so suspend/resume and sysfs behavior are implemented by the core.

## State and persistence
The transport wrapper stores no private state beyond regmap devm resources. All runtime state belongs to `goodix_berlin_core`.

## Dependencies and integration points
This file integrates the I2C subsystem, regmap-I2C, OF/I2C ID matching, input bus IDs, and the exported Berlin core symbols. It depends on a valid IRQ in `client->irq`.

## Risks
- The fixed 256-byte raw transfer cap must be sufficient for core reads such as IC-info chunks and event buffers; future larger reads need transport review.
- Only GT9916 is matched here; other Berlin I2C parts require correct IC-data addresses before adding compatibles.
- Regmap setup assumes the controller accepts 32-bit register addresses over I2C as provided by regmap.

## Test signals
- Build with `CONFIG_TOUCHSCREEN_GOODIX_BERLIN_I2C`.
- Probe a DT node with `goodix,gt9916`, required regulators, reset GPIO, and IRQ.
- Verify core sysfs register reads work through the I2C regmap and that event delivery survives suspend/resume.
