<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max14577-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max14577-regulator.c

Purpose: MFD child regulator driver for Maxim MAX14577 and MAX77836, covering SAFEOUT, charger current regulation, and MAX77836 LDO1/LDO2.

Important APIs/types/functions: charger callbacks implement multi-register enable status and current-limit get/set using shared Maxim charger-current tables. `max14577_get_regmap()` selects between charger/safeout regmap and MAX77836 PMIC regmap. Descriptor arrays differ by device type.

Control flow: init performs build-time descriptor-size and voltage-range checks, then registers the platform driver. Probe selects the supported descriptor array by `dev_type`, applies optional platform init/of nodes by matching array index, selects each regulator’s regmap, and registers it.

State and persistence: no private mutable state. Hardware registers store charger enable/current, safeout enable, and LDO voltage/enable state.

Dependencies and integration: MAX14577 MFD private APIs, platform data, OF regulator matching, regulator current and voltage types, and standard regmap helpers.

Risks and test signals: charger `is_enabled()` does not check `max14577_read_reg()` return values. Platform regulator arrays must align with descriptor indexes. Test both device types, regmap selection for MAX77836 LDOs, current-limit boundary calculations, charger status logic, and BUILD_BUG_ON invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max14577-regulator.c -->
