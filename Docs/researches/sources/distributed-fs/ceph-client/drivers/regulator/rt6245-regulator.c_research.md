# sources/distributed-fs/ceph-client/drivers/regulator/rt6245-regulator.c

Purpose: implements the Richtek RT6245 single buck regulator, whose configuration is written through virtual regmap registers encoded as one-byte SMBus command codes with parity checksum.

Important APIs/types/functions: `struct rt6245_priv` tracks optional enable GPIO and software enable state. `rt6245_reg_write()` maps virtual register plus value to a command byte using `func_base[]` and bit-count checksum. `rt6245_init_device_properties()` applies optional properties for current limit, thermal level, power-good delay, and switching frequency. Regulator ops support voltage selection, ramp delay, and GPIO enable.

Control flow: probe initializes software state as enabled, obtains optional enable GPIO, waits for soft-start, creates a regmap with custom write-only encoding and defaults, applies DT properties, and registers the regulator. Disable enters cache-only mode and powers the chip down via GPIO; enable powers it up, exits cache-only, syncs cached virtual registers, and marks enabled.

State and persistence: enable state is software-only. Regmap cache holds virtual register values while hardware is off. Hardware stores only the encoded settings accepted over SMBus.

Dependencies and integration: depends on I2C SMBus byte write, optional GPIO, regmap custom `reg_write`, regulator OF init data, and Richtek DT properties.

Risks and test signals: no readable registers are modeled, so cache correctness is vital. If no enable GPIO exists, disable returns `-EINVAL`. Virtual register index bounds rely on regmap `max_register`; `func_base` includes a final zero for VOUT. Tests should cover checksum generation, property application, regcache sync after disable/enable, ramp table, voltage selector bounds, and GPIO absent behavior.
