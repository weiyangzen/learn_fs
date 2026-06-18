# sources/distributed-fs/ceph-client/drivers/regulator/max77693-regulator.c

Purpose: provides SAFEOUT and charger regulators for MAX77693 and MAX77843 MFD devices. It supports voltage-table SAFEOUT rails and a current regulator for charger input/fast-charge limits.

Important APIs/types/functions: `struct chg_reg_data` abstracts charger register differences. `max77693_chg_get_current_limit()` and `max77693_chg_set_current_limit()` translate linear selector fields to current limits using regulator constraints. `max77693_get_regmap()` chooses the system or charger regmap based on chip type and regulator ID.

Control flow: platform probe reads the platform device ID to select MAX77693 or MAX77843 descriptor arrays and charger data, then registers each descriptor with the appropriate regmap.

State and persistence: there is no private state allocation. The driver passes a static `chg_reg_data` pointer through `config.driver_data`; hardware registers retain enable/current/voltage state.

Dependencies and integration: depends on MAX77693/MAX77843 MFD private headers, parent regmaps, platform child IDs, and regulator core current/voltage APIs.

Risks and test signals: comments note MAX77693 charger handling manipulates maximum input current rather than fast charge current. `config.driver_data` points to charger data for all regulators, but only charger ops consume it. Test regmap routing, SAFEOUT voltage table selection, current constraint boundaries, selector saturation, and both platform IDs.
