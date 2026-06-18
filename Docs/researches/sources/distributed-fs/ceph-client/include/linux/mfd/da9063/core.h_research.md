## sources/distributed-fs/ceph-client/include/linux/mfd/da9063/core.h

Purpose: This header defines the Dialog DA9063/DA9063L MFD core interface, child driver names, chip/variant IDs, IRQ numbering, shared runtime state, and core init APIs.

Important APIs, types, and constants: Driver-name macros identify core, regulators, LEDs, watchdog, hwmon, onkey, RTC, and vibration children. `PMIC_CHIP_ID_DA9063` is the expected chip ID. `enum da9063_type` distinguishes DA9063 and DA9063L. `enum da9063_variant_codes` lists AD, BB, CA, DA, and EA variant codes. `enum da9063_irqs` maps onkey, alarm, tick, ADC ready, sequencer, wake, temperature, comparator, LDO limit, regulator UV/OV, DVC ready, VDD monitor, warning, and GPI0-GPI15 interrupts. `struct da9063` stores device, type, variant code, flags, software-PM flag, regmap, chip IRQ, IRQ base, and regmap IRQ data. APIs are `da9063_device_init()` and `da9063_irq_init()`.

Control flow: Probe detects chip/variant, initializes `struct da9063`, configures regmap IRQs, then registers MFD children named by the macros. Child drivers use shared regmap and IRQ numbers.

State and persistence: Runtime state includes type, variant, flags, software power-management mode, and regmap IRQ data. Hardware state is in registers declared by the included DA9063 register map.

Dependencies and integration points: Includes interrupt support and `da9063/registers.h`. Integrates with regulator, LED, watchdog, hwmon, onkey, RTC, vibration, IRQ, and power-management paths.

Risks: DA9063L has a reduced feature set compared with DA9063; child registration must respect `type` and variant. `use_sw_pm` changes power-management behavior and must match platform expectations. IRQ enum ordering must match regmap IRQ tables.

Test signals: Chip/variant ID detection, DA9063 vs DA9063L child set selection, IRQ init and delivery for all event banks, software-PM mode behavior, and probe/remove cleanup of all named child devices.
