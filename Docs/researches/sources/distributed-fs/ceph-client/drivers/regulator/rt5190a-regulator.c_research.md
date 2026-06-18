# sources/distributed-fs/ceph-client/drivers/regulator/rt5190a-regulator.c

Purpose: registers five Richtek RT5190A rails: fixed buck1, adjustable buck2/buck3, fixed buck4, and fixed LDO, with interrupt reporting for voltage and thermal events.

Important APIs/types/functions: `struct rt5190a_priv` holds descriptors and registered regulator devices. `rt5190a_fillin_regulator_desc()` builds per-rail descriptors. `rt5190a_parse_regulator_dt_data()` matches the `regulators` node and validates fixed-rail constraints. `rt5190a_device_initialize()` applies a register patch and optional mute property. `rt5190a_irq_handler()` maps OV/UV/OT event bits to regulator notifier calls.

Control flow: probe initializes regmap, checks the manufacturer/device register, applies initialization patch, parses regulator DT data and protection mode, registers all five regulators, then optionally requests IRQ. Runtime fixed-buck mode changes update `RT5190A_REG_DCDCCNTL`; adjustable buck voltage selection uses regmap helpers.

State and persistence: descriptors are constructed at probe, including fixed voltages from DT constraints. Hardware stores enable, discharge, mode, protection, mute, fault, and voltage selector state. Interrupt latches are write-cleared by the handler.

Dependencies and integration: depends on I2C regmap, DT binding mode constants from `dt-bindings/regulator/richtek,rt5190a-regulator.h`, OF regulator matching, and optional IRQ.

Risks and test signals: `rt5190a_device_check()` expects a zero 16-bit manufacture value, a tight hardware assumption. Event handling uses `REGULATOR_ERROR_*` constants in notifier calls for some cases rather than `REGULATOR_EVENT_*`, which deserves review. Tests should cover fixed-rail min/max validation, latchup property polarity, register patch application, mute property, IRQ OV/UV/OT delivery, and absent IRQ behavior.
