# sources/distributed-fs/ceph-client/drivers/power/supply/ab8500-chargalg.h

Purpose: this header defines the charger abstraction consumed by the AB8500 charging algorithm. It lets the algorithm operate over AC and USB charger power supplies through a common `ux500_charger` interface.

Important APIs, types, and functions: `psy_to_ux500_charger(x)` converts a mains or USB `power_supply` to its driver data. `struct ux500_charger_ops` contains callbacks for `enable`, `check_enable`, `kick_wd`, and `update_curr`. `struct ux500_charger` wraps a `power_supply`, callback table, maximum output voltage/current, watchdog refresh value, and enabled flag.

Control flow: the header has no executable code. At runtime, `ab8500_chargalg.c` discovers external power supplies, uses `psy_to_ux500_charger()` for mains/USB supplies, and calls these ops to enable/disable charging, verify hardware enable state, kick the charger watchdog, and adjust charge current during maximization.

State and persistence: charger state is per `struct ux500_charger`, owned by the concrete charger driver. The charging algorithm reads `max_out_*` constraints and updates hardware through ops; it does not persist this structure beyond pointers cached in its own device state.

Dependencies and integration points: the file depends on the power supply class. It is tightly integrated with AB8500 charger implementations that expose mains/USB supplies with `struct ux500_charger` as `drv_data`. The comment explicitly limits `psy_to_ux500_charger()` use to `POWER_SUPPLY_TYPE_MAINS` and `POWER_SUPPLY_TYPE_USB`.

Risks: the macro is a raw cast-like retrieval with no runtime type validation; using it on the wrong power supply type would corrupt assumptions. Callback pointers are optional, so callers must continue checking for null ops. Unit expectations for voltage/current are microvolts and microamps; mismatched units would directly affect charger hardware programming.

Test signals: compile users with concrete charger drivers, verify mains/USB power supplies set `drv_data` to `struct ux500_charger`, and exercise algorithm paths for enable, disable, watchdog, check-enable, and current update with missing-op cases.
