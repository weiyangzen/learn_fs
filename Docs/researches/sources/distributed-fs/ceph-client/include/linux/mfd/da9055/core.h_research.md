## sources/distributed-fs/ceph-client/include/linux/mfd/da9055/core.h

Purpose: This header defines the DA9055 PMIC core runtime structure, logical IRQ IDs, regmap I/O wrappers, and lifecycle exports.

Important APIs, types, and constants: IRQ IDs cover alarm, tick, nonkey, regulator, and hwmon events. `struct da9055` stores regmap, regmap IRQ data, parent device, I2C client, IRQ base, and chip IRQ. Inline wrappers provide single register read/write, bulk read, raw bulk write, and update-bits helpers. Exported APIs are `da9055_device_init()`, `da9055_device_exit()`, and `da9055_regmap_config`.

Control flow: I2C probe initializes regmap and `struct da9055`, then calls device init to set up IRQs and MFD children. Child drivers use the inline wrappers for register access.

State and persistence: Runtime state is `struct da9055` plus regmap/regmap-irq data. Hardware state includes PMIC system, regulator, ADC, RTC, and event registers defined in `reg.h`.

Dependencies and integration points: Includes interrupt and regmap headers; references `i2c_client` and `device` types through including contexts. Integrates with regulators, RTC, hwmon/ADC, onkey, and IRQ child functions.

Risks: `da9055_reg_read()` returns either a negative error or a positive register value, so callers must not cast blindly to unsigned. Raw group writes depend on regmap configuration permitting raw writes. IRQ constants are sparse and must match regmap IRQ chip definitions.

Test signals: Probe/init/exit cleanup, regmap wrapper error propagation, bulk read/write behavior, IRQ registration and child IRQ delivery, and child driver access to the shared `da9055` state.
