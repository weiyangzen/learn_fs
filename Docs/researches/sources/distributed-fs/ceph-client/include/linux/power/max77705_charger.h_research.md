# sources/distributed-fs/ceph-client/include/linux/power/max77705_charger.h

Purpose: defines MAX77705 charger register bit fields, regmap field descriptors, current constants, and driver runtime data.

Important APIs and types: macros name interrupt/status bits, detail masks/shifts, configuration fields for charger/OTG/buck/boost/watchdog/protection/timing/current/voltage, AICL delay, and current step/min/max values. `enum max77705_field_idx` indexes regmap fields. `max77705_reg_field[]` maps field indices to charger configuration registers and bit ranges. `struct max77705_charger_data` stores device, regmap, regmap fields, parsed battery info, workqueue, charger input work, and charger power_supply.

Control flow: the charger driver allocates regmap fields from the static descriptors, uses field indices to unlock protection and program mode, charge current, input current, CV voltage, OTG current, watchdog, restart, and skip settings, schedules CHGIN/AICL work, and exposes a power_supply instance backed by `max77705_charger_data`.

State and persistence: runtime state includes regmap field handles, battery info pointer, workqueue/work item, and power_supply handle. Hardware register settings persist only according to chip power/reset behavior.

Dependencies and integration points: depends on regmap/regmap_field, MAX77705 charger register definitions from the broader MFD/regmap layer, power_supply battery info, workqueues, and charger IRQ/status handling.

Risks and test signals: risks include static `reg_field` definitions drifting from register map, off-by-one current scaling, failure to unlock protected fields, mode bit conflicts between OTG/UNO/boost, watchdog clearing mistakes, and workqueue teardown races. Test regmap field allocation, each configurable power_supply property, AICL work, IRQ/status decoding, OTG mode, charger enable/disable, and removal with pending work.
