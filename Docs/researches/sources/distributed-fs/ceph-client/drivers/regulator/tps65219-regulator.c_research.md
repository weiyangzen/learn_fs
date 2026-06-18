# sources/distributed-fs/ceph-client/drivers/regulator/tps65219-regulator.c

Purpose: Platform child regulator driver for TPS65214/TPS65215/TPS65219 PMIC families, covering common buck rails, variant LDO rails, bypass-capable LDOs, standby mode, and regulator fault IRQ notifications.

Important APIs/types/functions: `struct tps65219_chip_data` selects common and variant regulator descriptors plus common and variant IRQ type tables. `TPS65219_REGULATOR` builds descriptors with voltage/current fields, enable masks, linear ranges, ramp delays, and bypass masks. Ops use generic regmap helpers plus custom standby-mode set/get. `tps65219_regulator_irq_handler` maps named platform IRQs to regulator notifier events.

Control flow: probe chooses chip data from platform ID, registers common bucks, registers variant LDOs, then requests every named common and variant IRQ. Runtime mode writes `STBY_1_CONFIG` bits; voltage and bypass use regmap helpers. IRQ handler reports timeout globally or calls `regulator_notifier_call_chain` for rail-specific overcurrent, undervoltage, residual-voltage, short-circuit, and thermal events.

State and persistence: state is in parent regmap. IRQ data is devm-allocated per IRQ and stores the event type, but the current code does not populate `irq_data->rdev`, so notifier delivery has a null regulator device for rail-specific events.

Dependencies and integration points: TPS65219 MFD, platform IRQ resources by name, regulator core/notifier API, regmap, OF regulator nodes, and platform device IDs for chip variants.

Risks: all listed IRQ names are mandatory; missing one aborts probe. `tps65219_get_mode` appears to return STANDBY when the bit is set despite `set_mode(NORMAL)` setting the bit, suggesting inverted semantics. Null `rdev` in IRQ data is a likely notifier bug.

Test signals: all three chip IDs, regulator count/ranges per variant, standby mode round trips, bypass for LDO1/2, complete IRQ resource tables, and notifier behavior with real rdev association.
