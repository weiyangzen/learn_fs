## sources/distributed-fs/ceph-client/include/linux/mfd/da9062/core.h

Purpose: This header defines the Dialog DA9061/DA9062 PMIC core type, compatible variants, logical IRQ numbers, and shared runtime structure.

Important APIs, types, and constants: `enum da9062_compatible_types` distinguishes DA9061 and DA9062 compatible handling. `enum da9061_irqs` maps DA9061 IRQs across banks A-C, while `enum da9062_irqs` adds alarm and tick and defines the DA9062 IRQ count. `struct da9062` stores parent device, regmap, regmap IRQ data, and selected chip type.

Control flow: Bus probe detects compatible type, initializes regmap from `registers.h`, registers the correct regmap IRQ chip using the matching enum layout, and creates MFD children.

State and persistence: Runtime state is the `struct da9062` object and regmap IRQ data. Hardware state is the DA9061/DA9062 PMIC register set defined in `registers.h`.

Dependencies and integration points: Includes interrupt support and the DA9062 register map. Integrates with regulator, RTC, watchdog, onkey, GPIO, and hwmon/power-management child drivers.

Risks: DA9061 and DA9062 have different IRQ counts and event availability; using the wrong enum/table will misroute interrupts. The struct is intentionally small, so child drivers depend on shared regmap and chip type rather than copied platform data.

Test signals: Probe both DA9061 and DA9062 compatibles, verify IRQ count/table selection, regmap IRQ delivery for onkey/watchdog/temp/GPI events, and child creation for variant-appropriate functions.
