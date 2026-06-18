# sources/distributed-fs/ceph-client/drivers/regulator/as3722-regulator.c

Purpose: regulator driver for AMS AS3722 PMIC, supporting seven SD converters and eleven LDOs with current limits, external enable control, bypass, fast/normal mode, and optional LDO3 tracking.

Important APIs/types/functions: `as3722_reg_lookup[]` maps each regulator ID to register addresses, masks, supply names, and sleep-control fields. `struct as3722_regulators` owns generated descriptors and parsed config. Key functions include `as3722_get_regulator_dt_data()`, `as3722_sd_get_mode()`, `as3722_sd_set_mode()`, `as3722_extreg_init()`, `as3722_ldo3_set_tracking_mode()`, and `as3722_sd0_is_low_voltage()`.

Control flow: probe allocates state, parses the parent `regulators` node, then builds one descriptor per ID by combining lookup metadata with regulator-type-specific ops and voltage/current tables. It registers each regulator and, when `ams,ext-control` is present, enables the regulator and programs external control routing.

State and persistence: parsed per-rail config stores init data, tracking flag, and external control selection. Descriptors are runtime-generated but devm-owned. Persistent behavior is PMIC register state, including fuse-dependent SD0 low-voltage range and sleep-control routing.

Dependencies and integration: depends on AS3722 MFD helper APIs (`as3722_read/update_bits`), parent regmap, OF regulator parsing, and regulator core current-limit/bypass helpers.

Risks and test signals: invalid `ams,ext-control` values are only warned and ignored; external control forces an enable during probe. LDO6 bypass uses the same value for on and off, requiring hardware-specific validation. Tests should cover SD0 fuse variants, LDO3 tracking, ext-control routing 1..3, current-limit selectors, bypass, unsupported SD mode registers, malformed DT, and partial registration failures.
