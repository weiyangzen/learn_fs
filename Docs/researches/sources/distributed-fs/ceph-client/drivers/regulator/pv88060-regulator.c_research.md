# sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.c

Purpose: implements the Powerventure/Dialog PV88060 I2C regulator driver. It registers one buck, seven LDOs, and six fixed-voltage switches, and reports global VDD fault and over-temperature events to all registered regulators.

Important APIs/types/functions: `struct pv88060_regulator` wraps `regulator_desc` with a buck configuration register. `struct pv88060` stores device, regmap, and registered regulator devices. `pv88060_buck_get_mode()` and `pv88060_buck_set_mode()` map chip buck mode bits to regulator FAST/NORMAL/STANDBY modes. Descriptor macros define regulator descriptors and register/mask fields. `pv88060_irq_handler()` handles event register bits.

Control flow: probe allocates state, initializes an 8-bit regmap, optionally masks interrupt banks A/B/C, requests a low-triggered threaded IRQ, unmasks VDD fault and over-temperature events, then registers all regulators. IRQ handling reads `EVENT_A`, broadcasts notifier events to every registered regulator, and clears handled event bits.

State and persistence: there is no voltage or mode cache. Optional platform data can provide per-regulator init data. PMIC register state persists according to hardware; driver state is devm-managed.

Dependencies and integration: depends on I2C, regmap, interrupt handling, regulator core, and optional OF matching (`pvs,pv88060`). Register constants come from `pv88060-regulator.h`.

Risks and test signals: no chip identity register is checked, so compatible/I2C binding correctness is critical. Global fault events are broadcast to all regulators. Test regulator registration, buck current-limit table, buck mode transitions, LDO voltage ranges, switch enable bits, IRQ mask/unmask/clear behavior, and no-IRQ operation.
