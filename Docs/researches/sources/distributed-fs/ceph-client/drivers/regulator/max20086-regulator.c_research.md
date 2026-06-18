# sources/distributed-fs/ceph-client/drivers/regulator/max20086-regulator.c

Purpose: implements the MAX20086/MAX20087/MAX20088/MAX20089 camera power protector regulator driver. It exposes two or four switch-style voltage outputs as regulator framework devices and uses one optional global enable GPIO for chip power/shutdown.

Important APIs/types/functions: `struct max20086_chip_info` selects device ID and output count; `struct max20086` owns the regmap, enable GPIO, chip match data, and per-output regulator metadata. `max20086_parse_regulators_dt()` matches child regulators under `regulators`; `max20086_detect()` verifies `MAX20086_REG_ID`; `max20086_regulators_register()` calls `devm_regulator_register()` for each output. Regulator ops are generic regmap enable/disable/is_enabled against `MAX20086_REG_CONFIG`.

Control flow: I2C probe allocates state, initializes an 8-bit regmap, parses DT, verifies the chip ID, masks all interrupts because IRQ support is absent, requests the optional `enable` GPIO high if any output is boot-on/always-on, then registers each output descriptor.

State and persistence: runtime state is devm-managed and non-persistent. Regulator enable state lives in the chip config register; the global enable GPIO state is chosen from DT constraints to avoid dropping boot-critical rails.

Dependencies and integration: depends on I2C, regmap, GPIO descriptors, OF regulator matching, and regulator core. Compatible strings and I2C IDs map to fixed `chip_info` records.

Risks and test signals: no IRQ handling means faults are masked and invisible to Linux. DT must provide a `regulators` subnode with valid output names. Test signals include chip-ID mismatch, 2-output versus 4-output variants, boot-on GPIO preservation, interrupt mask write failure, and all output enable bits toggling only their own mask.
