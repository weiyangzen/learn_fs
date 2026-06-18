# sources/distributed-fs/ceph-client/drivers/regulator/rtq2208-regulator.c

Purpose: supports the Richtek RTQ2208 PMIC by dynamically discovering which buck phases and LDO configurations are present, registering only the active regulators, and wiring IRQ notifications for buck UV/OV and hot-die events.

Important APIs/types/functions: `struct rtq2208_regulator_desc` extends descriptors with MTP, mode, and suspend fields. `rtq2208_regulator_check()` enters hidden pages, reads buck phase and LDO configuration, computes used regulators, fixed LDO voltages, and IRQ masks. `rtq2208_init_regulator_desc()` fills each descriptor according to regulator index and MTP selection. `rtq2208_irq_handler()` reads, clears, and reports fault records.

Control flow: probe allocates an `rtq2208_rdev_map`, initializes regmap, discovers active rails through hidden-page reads, parses the `richtek,mtp-sel-high` property, allocates descriptors for active rails, registers them, initializes IRQ masks, and requests a threaded IRQ. Buck ops support voltage, mode, ramp, active discharge, and suspend mode/enable. LDO ops are fixed or two-step adjustable depending on hidden configuration.

State and persistence: the rdev map persists regulator pointers for IRQ dispatch. Dynamic descriptors persist for the device lifetime. Hardware hidden configuration determines rail topology; operational state remains in PMIC registers.

Dependencies and integration: depends on I2C, regmap, OF regulator matching, machine constraints for fixed LDO voltage, IRQ, and bitfield helpers. There is no static full descriptor table because topology is hardware-configured.

Risks and test signals: hidden-page entry/exit must be correct or later register access could be affected. IRQ mask arrays are mutated according to active rails, so index mapping is critical. `cfg.regmap` is not explicitly assigned before registration, relying on regulator core lookup behavior may be risky. Tests should cover all buck phase encodings, fixed/adjustable LDO combinations, MTP high/low, ramp delay calculation, IRQ clear/unmask, and absent IRQ/hidden-page failures.
