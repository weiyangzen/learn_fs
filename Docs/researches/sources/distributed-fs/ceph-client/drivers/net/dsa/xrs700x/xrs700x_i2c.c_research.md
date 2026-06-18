# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_i2c.c

Purpose: this file is the I2C transport frontend for the XRS700x DSA core. It implements the switch's 32-bit register, 16-bit value I2C protocol as a custom regmap bus and delegates switch behavior to `xrs700x.c`.

Important APIs, types, and functions: `struct xrs700x_i2c_cmd` is the packed wire command containing a big-endian 32-bit register and big-endian 16-bit value. `xrs700x_i2c_reg_read()` writes `reg | 1` then receives a 16-bit value. `xrs700x_i2c_reg_write()` sends register and value together. `xrs700x_i2c_regmap_config` defines 32-bit registers, 16-bit values, stride 2, no cache, custom read/write, and big-endian formatting. Probe/remove/shutdown call `xrs700x_switch_alloc()`, `xrs700x_switch_register()`, `xrs700x_switch_remove()`, and `xrs700x_switch_shutdown()`.

Control flow: probe allocates the common switch object, initializes a devm regmap using the custom I2C operations, stores client data, and registers the switch. Remove and shutdown fetch client data and delegate to the common core, with shutdown clearing client data.

State and persistence: transport state is the `i2c_client` pointer passed as core private data and the devm regmap stored in `priv->regmap`. No register cache is used, so all accesses hit the bus.

Dependencies and integration points: it depends on Linux I2C, regmap, OF match data for `arrow,xrs7003e`, `arrow,xrs7003f`, `arrow,xrs7004e`, and `arrow,xrs7004f`, and the common XRS700x core. The match `.data` provides the expected chip info consumed by core detection.

Risks: I2C read/write helpers only treat negative transfer returns as errors; short positive transfers are not rejected. `max_register = 0` with custom callbacks relies on regmap not enforcing a range that would block real addresses. Protocol correctness depends on the `reg | 1` read marker and big-endian conversion. There is no explicit bus lock here beyond I2C core serialization.

Test signals: I2C probe on all compatibles, regmap read/write of known registers, detection ID match/mismatch, short-transfer fault injection, DSA registration through I2C, remove/shutdown delegation, and no-cache behavior for changing hardware counters.
