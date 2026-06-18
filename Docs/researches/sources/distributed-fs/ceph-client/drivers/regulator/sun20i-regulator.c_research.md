<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sun20i-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sun20i-regulator.c

Purpose: exposes the Allwinner D1/T113 internal system LDOA and LDOB regulators in the system-control block.

Important APIs/types/functions: `sun20i_d1_system_ldo_list_voltage()` implements custom rounded voltage calculation for a repeating 13.333 mV step. `sun20i_d1_system_ldo_ops` uses this custom listing, ascending map, and regmap selector get/set. `sun20i_d1_system_ldo_descs[]` describes LDOA and LDOB selector masks in `SUN20I_SYS_LDO_CTRL_REG`. `sun20i_regulator_get_regmap()` tries syscon lookup first and falls back to the parent platform regmap for DT backward compatibility.

Control flow: probe obtains match data, gets the parent regmap through syscon or fallback, builds regulator config, and registers each descriptor. Runtime voltage operations only read/write selector fields; there are no enable/disable callbacks.

State and persistence: the driver stores no private state. Selector state is in the system-control register. These LDOs are assumed controlled by voltage selection rather than explicit enable bits.

Dependencies and integration: depends on the parent system-control device, OF compatible `allwinner,sun20i-d1-system-ldos`, regmap/syscon, and regulator child nodes `ldoa` and `ldob` with `ldo-in` supply.

Risks and test signals: custom voltage rounding must match hardware's fractional step encoding. The fallback regmap path is intentionally compatibility-driven and should be kept while old DTs exist. Test selector-to-voltage values around 1.606667 V threshold, map_voltage behavior, both regmap acquisition paths, missing match data, and real DTS consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sun20i-regulator.c -->
